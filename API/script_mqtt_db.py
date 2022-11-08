from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
import paho.mqtt.client as mqtt

import json
import requests
from datetime import datetime, timedelta
import math
import os
import time

import psql_database as db
from settings.connection_settings import mqtt_settings as settings
from settings.connection_settings import openWeatherMap_settings as api_settings
from settings.crop_settings import water
from settings.crop_settings import scheduled_irrigation_time as watertime

engine = db.engine
Session = sessionmaker(engine)
session = Session()
path = os.path.dirname(os.path.realpath(__file__))
path = path.replace('\\',"/")

def saveData(data):
    # Api de OpenWeatherMap para obtener la duración relativa del sol
    # Llamadas cada 2 minutos, para no sobrepasar el límite gratuito de 1000 diarias
    now = datetime.now()
    if now.minute%10 == 0 and now.second <= settings['interval']:   
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={api_settings["lat"]}&lon={api_settings["lon"]}&units={api_settings["units"]}&appid={api_settings["api_key"]}'
        req = requests.get(url)
        api_data = req.json()
        try:
            ssh = 1 - (api_data['clouds']['all']*0.01)
        except:
            ssh = None
    else:
        ssh = None
    
    # Guardado de datos en la base de datos
    values = db.Sensor( datetime = now,
                        temperature = data['Temperature'],
                        humidity = data['Humidity'],
                        sunshine = ssh,
                        soilMoisture1 = data['SM1'],
                        soilMoisture2 = data['SM2'],
                        soilMoisture3 = data['SM3'],
                        id_crop = 1)
    session.add(values)
    session.commit()

def read_initial_irrigation():
    f = open (path + '/settings/initial_irrigation.txt','r')
    content = f.read()
    f.close()
    if content == 'False\n':
        return False
    return True

def write_inital_irrigation():
    f = open(path + '/settings/initial_irrigation.txt','w')
    f.write('True')
    f.close()

def read_irrigation():
    f = open(path + '/settings/irrigation.txt','r')
    content = float(f.read())
    f.close()
    return content

def write_irrigation(water_amount):
    f = open(path + '/settings/irrigation.txt','w')
    f.write(str(water_amount))
    f.close()
    
def write_irr(info):
    f = open(path + '/logs/irr.txt','w')
    f.write(str(info))
    f.close()

def read_day():
    f = open(path + '/settings/day.txt','r')
    content = int(f.read())
    f.close()
    return content

def write_day(day):
    f = open(path + '/settings/day.txt','w')
    f.write(str(day))
    f.close()

def soilPercent_toWater(soilPercent, soilToday):
    soil_to_water = 0.198*(math.e**(0.055*(soilToday+soilPercent))) - 0.198*(math.e**(0.055*soilToday))
    return soil_to_water

def getSoilPercent(now):
    yesterday = now - timedelta(days=1)
    yesterday_water = session.query(db.waterAmount.water_amount).filter(
        func.to_char(db.waterAmount.date, 'DD-MM-YYYY') == yesterday.strftime("%d-%m-%Y"))[0][0]
    drip_delay = yesterday_water * (water['dripseconds'] / water['dripwater']) # Caudal del riego por goteo
    post_irrigation = (yesterday + timedelta(seconds = drip_delay+3600)).strftime("%d-%m-%Y %H:%M")
    soil_yesterday = session.query(func.min(db.Sensor.soilMoisture3)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY HH24:MI') == post_irrigation)[0][0]
    if soil_yesterday == None:
        soil_yesterday = session.query(func.max(db.Sensor.soilMoisture3)).filter(
            func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == yesterday.strftime("%d-%m-%Y"))[0][0]
    soil_today = session.query(db.Sensor.soilMoisture3).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
    if soil_today <= soil_yesterday:
        soil_diff = soil_yesterday - soil_today
    else:
        soil_diff = 0
    return soil_diff, soil_today

def compute_irrigation_value(computed_eto):
    id_plant = session.query(db.Plant.id_plant).filter(db.Plant.name == 'peppermint')[0][0]
    kc_ini = session.query(db.Plant.kc_ini).filter(db.Plant.id_plant == id_plant)[0][0]
    kc_med = session.query(db.Plant.kc_med).filter(db.Plant.id_plant == id_plant)[0][0]
    a = session.query(db.Crop.a).filter(db.Crop.id_plant == id_plant)[0][0]
    pc = session.query(db.Crop.pc).filter(db.Crop.id_plant == id_plant)[0][0]
    er = session.query(db.Crop.er).filter(db.Crop.id_plant == id_plant)[0][0]
    water_demand = ((computed_eto*((kc_ini+kc_med)/2)*a*(pc/100))/er)*1000
    return water_demand
    


def irrigationSignal(now):
    """ Señal para regar, enciende el relay una cantidad determinada de segundos
        siempre y cuando se haya ejecutado el script programado"""
    eto_calculated = session.query(func.count(db.computedEto.computed_eto)).filter(
                func.to_char(db.computedEto.date, 'DD-MM-YYYY') == now.strftime("%d-%m-%Y"))[0][0]
    try:
        irrigated = session.query(func.count(db.waterAmount.water_amount)).filter(
                    func.to_char(db.waterAmount.date, 'DD-MM-YYYY') == now.strftime("%d-%m-%Y"))[0][0]
    except:
        irrigated = 0

    if eto_calculated != 0 and irrigated == 0:
        if read_initial_irrigation():
            soil_diff, soil_today = getSoilPercent(now)
            water_value = soilPercent_toWater(float(soil_diff),float(soil_today))
        else:
            try:
                eto = session.query(db.computedEto.computed_eto).filter(
                func.to_char(db.computedEto.date, 'DD-MM-YYYY') == now.strftime("%d-%m-%Y"))[0][0]
                water_value = compute_irrigation_value(eto)
                write_inital_irrigation()                
            except:
                water_value = 0
                print("No hay datos para calcular el riego")
        caudal = water['water']/water['seconds']
        irrigation_value = water_value/caudal
        if read_irrigation() >= 0 and read_day() == 1:
            value = float(irrigation_value) + read_irrigation() + 0.08
            sessionMQTT.publish('relay/Signal',value)
            write_irr(now.strftime("%d-%m-%Y")+' '+str(value))
            write_irrigation(0)
            write_day(0)
            print('enviando señal riego', value)
        elif read_irrigation() == 0 and read_day() == 0:
            write_irrigation(irrigation_value)
            write_day(1)
        values = db.waterAmount(date = now.strftime("%d-%m-%Y"),
                                water_amount = water_value,
                                id_crop = 1)
        session.add(values)
        session.commit()


def ConnectMQTT(client,userdata,flags,rc):
    print("Conectado "+str(rc))
    sessionMQTT.subscribe('data/Sensor')

def MQTTtoDB(client,userdata,msg):
    """ Recibir mensajes desde el Arduino vía MQTT
        y guardar en la base de datos"""
    data = json.loads(str(msg.payload)[2:-1])
    saveData(data)
    actual_time = datetime.now()
    irrigationSignal(actual_time)

sessionMQTT = mqtt.Client()
sessionMQTT.on_connect = ConnectMQTT
sessionMQTT.on_message = MQTTtoDB
sessionMQTT.connect(settings['ip'],settings['port'])
sessionMQTT.loop_forever()
