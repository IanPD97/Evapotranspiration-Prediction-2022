from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
import paho.mqtt.client as mqtt

import json
import requests
from datetime import datetime, timedelta

import psql_database as db
from settings.connection_settings import mqtt_settings as settings
from settings.connection_settings import openWeatherMap_settings as api_settings
from settings.crop_settings import water
from settings.crop_settings import scheduled_irrigation_time as watertime

engine = db.engine
Session = sessionmaker(engine)
session = Session()


def saveData(data):
    # Api de OpenWeatherMap para obtener la duración relativa del sol
    # Llamadas cada 2 minutos, para no sobrepasar el límite gratuito de 1000 diarias
    now = datetime.now()
    if now.minute%2 == 0 and now.second <= settings['interval']:   
        url = f'https://api.openweathermap.org/data/3.0/onecall?lat={api_settings["lat"]}&lon={api_settings["lon"]}&units={api_settings["units"]}&exclude={api_settings["exclude"]}&appid={api_settings["api_key"]}'
        req = requests.get(url)
        api_data = req.json()
        try:
            ssh = 1 - (api_data['current']['clouds']*0.01)
        except:
            ssh = None
    else:
        ssh = None
    
    # Guardado de datos en la base de datos
    values = db.Sensor( value_date = now,
                        temperature = data['Temperature'],
                        humidity = data['Humidity'],
                        sunshine = ssh,
                        soilMoisture1 = data['SM1'],
                        soilMoisture2 = data['SM2'],
                        soilMoisture3 = data['SM3'])
    session.add(values)
    session.commit()

def read_initial_irrigation():
    f = open ('API/settings/initial_irrigation.txt','r')
    content = f.read()
    f.close()
    if content == 'False':
        return False
    return True

def write_inital_irrigation():
    f = open('API/settings/initial_irrigation.txt','w')
    f.write('True')
    f.close()

def soilPercent_toWater(soilPercent):
    factor = water['soilmoisture']/water['soilwater']
    water_value = factor * soilPercent
    return water_value

def getSoilPercent(now):
    yesterday = now - timedelta(days=1)
    yesterday_water = session.query(db.waterAmount.water_amount).filter(
        func.to_char(db.waterAmount.value_date, 'DD-MM-YYYY') == yesterday.strftime("%d-%m-%Y"))[0][0]
    drip_delay = yesterday_water * (water['dripseconds'] / water['dripwater']) # Caudal del riego por goteo
    post_irrigation = (yesterday + timedelta(seconds = drip_delay)).strftime("%d-%m-%Y %H:%M")
    soil_yesterday = session.query(func.avg(db.Sensor.soilMoisture3)).filter(
        func.to_char(db.Sensor.value_date, 'DD-MM-YYYY H24:MI') == post_irrigation)[0][0]
    if soil_yesterday == None:
        soil_yesterday = session.query(func.max(db.Sensor.soilMoisture3)).filter(
            func.to_char(db.Sensor.value_date, 'DD-MM-YYYY') == yesterday.strftime("%d-%m-%Y"))[0][0]
    soil_today = session.query(db.Sensor.soilMoisture3).order_by(db.Sensor.value_date.desc()).limit(1)[0][0]
    soil_diff = soil_yesterday - soil_today
    return soil_diff


def irrigationSignal(now,scheduled_hour,scheduled_minute,interval):
    """ Señal para regar, enciende el relay una cantidad determinada de segundos
        según la hora programada"""
    if now.hour == scheduled_hour and now.minute == scheduled_minute and now.second <= interval:
        if read_initial_irrigation():
            water_value = soilPercent_toWater(getSoilPercent(now))
        else:
            try:
                water_value = session.query(db.computedEto.irrigation_value).filter(
                func.to_char(db.computedEto.value_date, 'DD-MM-YYYY') == now.strftime("%d-%m-%Y"))[0][0]
                write_inital_irrigation()
            except:
                water_value = 0
                print("No hay datos para calcular el riego")
        caudal = water['water']/water['seconds']
        irrigation_value = water_value/caudal
        sessionMQTT.publish('relay/Signal',float(irrigation_value))
        values = db.waterAmount(value_date = now.strftime("%d-%m-%Y"),
                                water_amount = water_value)
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
    print(data)
    actual_time = datetime.now()
    irrigationSignal(actual_time,watertime['hour'],watertime['minute'],settings['interval'])


sessionMQTT = mqtt.Client()
sessionMQTT.on_connect = ConnectMQTT
sessionMQTT.on_message = MQTTtoDB
sessionMQTT.connect(settings['ip'],settings['port'])
sessionMQTT.loop_forever()