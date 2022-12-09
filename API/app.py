import json
import time
from datetime import datetime,timedelta
import pandas as pd
from sqlalchemy.orm import sessionmaker
import psql_database as db
from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS
from settings.connection_settings import mqtt_settings as settings

application = Flask(__name__)
CORS(application)
engine = db.engine
Session = sessionmaker(engine)
session = Session()

##### EVAPOTRANSPIRACION A AGUA #####
def compute_irrigation_value(computed_eto):
    id_plant = session.query(db.Plant.id_plant).filter(db.Plant.name == 'peppermint')[0][0]
    kc_ini = session.query(db.Plant.kc_ini).filter(db.Plant.id_plant == id_plant)[0][0]
    kc_med = session.query(db.Plant.kc_med).filter(db.Plant.id_plant == id_plant)[0][0]
    a = session.query(db.Crop.a).filter(db.Crop.id_plant == id_plant)[0][0]
    pc = session.query(db.Crop.pc).filter(db.Crop.id_plant == id_plant)[0][0]
    er = session.query(db.Crop.er).filter(db.Crop.id_plant == id_plant)[0][0]
    water_demand = ((computed_eto*((kc_ini+kc_med)/2)*a*(pc/100))/er)*1000
    return water_demand



# -------------------------------------------------------------------------------------------------------------------- #
@application.route('/irrigate')
def irrigate():
    import paho.mqtt.client as mqtt
    sessionMQTT = mqtt.Client()
    sessionMQTT.connect(settings['ip'],settings['port'])
    sessionMQTT.publish('relay/Signal',0)
    print(0)
    return '0'



@application.route('/chart-data')
def chart_data():
    def get_data():
        try:
            while True:
            
                Temperature = session.query(db.Sensor.temperature).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
                Humidity = session.query(db.Sensor.humidity).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
                SoilMoisture1 = session.query(db.Sensor.soilMoisture1).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
                SoilMoisture2 = session.query(db.Sensor.soilMoisture2).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
                SoilMoisture3 = session.query(db.Sensor.soilMoisture3).order_by(db.Sensor.datetime.desc()).limit(1)[0][0]
                json_data = json.dumps(
                    {'time': datetime.now().strftime('%H:%M:%S'), 'temp': float(Temperature), 'humidity': int(Humidity), 'soil1': int(SoilMoisture1),'soil2': int(SoilMoisture2),'soil3': int(SoilMoisture3)})
                yield f"data:{json_data}\n\n"
                time.sleep(4.95)
        except:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%H:%M:%S'), 'temp': None, 'humidity': None, 'soil1': None,'soil2': None,'soil3': None})
            yield f"data:{json_data}\n\n"

            pass

    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@application.route('/forecast-data')
def forecast_data():
    def get_data():
        try:
            array_forecast = []
            array_date = []
            array_water = []
            forecast_eto = session.query(db.predictedEto.date,db.predictedEto.predicted_eto,db.predictedEto.forecast_horizon).order_by(db.predictedEto.date.desc(),db.predictedEto.forecast_horizon.asc()).limit(7)
            for row in forecast_eto:
                array_date.append( (row[0] + timedelta(days=row[2])).strftime('%d-%m-%Y'))
                array_forecast.append(round(row[1],2))
                array_water.append(round(compute_irrigation_value(row[1]),2))
            df = pd.DataFrame({"Date": array_date,"Forecast": array_forecast, "Water": array_water})
            json_data = df.to_json()
            yield f"{json_data}\n\n"
        except:
            df = pd.DataFrame({"Date": datetime.now().strftime('%d-%m-%Y'),"Forecast": [None], "Water": [None]})
            json_data = df.to_json()
            yield f"{json_data}\n\n"


    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@application.route('/historical-data')
def historical_data():
    def get_data():
        try:
            horas = int(request.args.get('hours'))
            if horas == 1: horas = 168
            today = datetime.now() - timedelta(hours=horas)
            array_date = []
            array_temperature = []
            array_humidity = []
            array_soil1 = []
            array_soil2 = []
            array_soil3 = []
            fecha = today.strftime('%Y-%m-%d %H:%M:%S') 
            data = session.query(db.Sensor.datetime,db.Sensor.temperature,db.Sensor.humidity,db.Sensor.soilMoisture1,db.Sensor.soilMoisture2,db.Sensor.soilMoisture3).filter(db.Sensor.datetime >= fecha).order_by(db.Sensor.datetime.desc())
            for row in data:
                array_date.append(row[0].strftime('%Y-%m-%d %H:%M:%S'))
                array_temperature.append(row[1])
                array_humidity.append(row[2])
                array_soil1.append(row[3])
                array_soil2.append(row[4])
                array_soil3.append(row[5])
            df = pd.DataFrame({"Date": array_date,"Temperature":array_temperature,"Humidity":array_humidity,"Soil1":array_soil1,"Soil2":array_soil2,"Soil3":array_soil3})
            df.Date = pd.to_datetime(pd.to_datetime(df.Date,format='%Y-%m-%d').dt.strftime('%Y-%m-%d %H'),format='%Y-%m-%d')
            df_avg = df[["Temperature","Humidity","Soil1","Soil2","Soil3"]].groupby(df["Date"].sort_values()).mean().round(1)
            df_avg = df_avg.interpolate()
            df_avg.index = df_avg.index.strftime('%d-%m-%Y %H:%M')
            num = []
            for i in range(len(df_avg)):
                num.append(i)
            df_avg_j = pd.DataFrame({"index": num,"Date": df_avg.index,"Temperature": df_avg['Temperature'],"Humidity": df_avg['Humidity'],"Soil1": df_avg['Soil1'],"Soil2": df_avg['Soil2'],"Soil3": df_avg['Soil3']}).set_index('index')
            json_data = df_avg_j.to_json()
            yield f"{json_data}\n\n"
        except:
            df_avg_j = pd.DataFrame({"index": [0],"Date":[datetime.now().strftime('%d-%m-%Y %H:%M')],"Temperature":[None],"Humidity":[None],"Soil1":[None],"Soil2":[None],"Soil3":[None]}).set_index('index')
            json_data = df_avg_j.to_json()
            yield f"{json_data}\n\n"
    
    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

@application.route('/historical-water')
def historical_water():
    def get_data():
        try:
            dias = int(request.args.get('days'))
            if dias == 1: dias = 30
            today = datetime.now() - timedelta(days=dias)
            array_date = []
            array_water = []
            array_water_et = []
            fecha = today.strftime('%d-%m-%Y')
            water_data = session.query(db.waterAmount.date,db.waterAmount.water_amount).filter(db.waterAmount.date >= fecha).order_by(db.waterAmount.date.desc())
            water_data_et = session.query(db.computedEto.date,db.computedEto.computed_eto).filter(db.computedEto.date >= fecha).order_by(db.computedEto.date.desc())
            for row in water_data:
                array_date.append(row[0].strftime('%d-%m-%Y'))
                array_water.append(round(row[1],1))
            for row in water_data_et:
                array_water_et.append(round(compute_irrigation_value(row[1]),1))
            df = pd.DataFrame({"Date": array_date,"Water":array_water,"Water_et":array_water_et})
            json_data = df.to_json()
            yield f"{json_data}\n\n"
        except:
            df = pd.DataFrame({"Date": datetime.now().strftime('%d-%m-%Y'),"Water":[None],"Water_et":[None]})
            json_data = df.to_json()
            yield f"{json_data}\n\n"
    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    application.run(debug=True, threaded=True,port=4000)