from sqlalchemy.orm import sessionmaker
import paho.mqtt.client as mqtt

import json
import requests
from datetime import datetime

import psql_database as db
from settings.connection_settings import mqtt_settings as settings
from settings.connection_settings import openWeatherMap_settings as api_settings


engine = db.engine
Session = sessionmaker(engine)
session = Session()


def saveData(data):
    # Api de OpenWeatherMap para obtener la duración relativa del sol
    # Llamadas cada 2 minutos, para no sobrepasar el límite gratuito de 1000 diarias
    now = datetime.now()
    if now.minute%2 == 0 and now.second <= 30:   
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


def ConnectMQTT(client,userdata,flags,rc):
    print("Conectado "+str(rc))
    MiMQTT.subscribe('data/Sensor')

def MQTTtoDB(client,userdata,msg):
    """ Funcion que recibe mensajes desde el Arduino vía MQTT
        y los guarda en la base de datos"""
    data = json.loads(str(msg.payload)[2:-1])
    saveData(data)
    print(data)
    

MiMQTT = mqtt.Client()
MiMQTT.on_connect = ConnectMQTT
MiMQTT.on_message = MQTTtoDB
MiMQTT.connect(settings['ip'],settings['port'])
MiMQTT.loop_forever()