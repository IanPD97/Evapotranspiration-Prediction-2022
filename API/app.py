import json
import time
from datetime import datetime,timedelta
import pandas as pd
from sqlalchemy.orm import sessionmaker
import psql_database as db
from flask import Flask, Response, render_template, stream_with_context
from flask_cors import CORS

application = Flask(__name__)
CORS(application)
engine = db.engine
Session = sessionmaker(engine)
session = Session()


@application.route('/chart-data')
def chart_data():
    def get_data():
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
    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response



@application.route('/historical-data')
def historical_data():
    def get_data():
        horas = 24
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
        df_avg = df[["Temperature","Humidity","Soil1","Soil2","Soil3"]].groupby(df["Date"].sort_values()).mean()
        df_avg = df_avg.interpolate()
        df_avg.index = df_avg.index.strftime('%d-%m-%Y %H:%M')
        num = []
        for i in range(len(df_avg)):
            num.append(i)
        df_avg_j = pd.DataFrame({"index": num,"Date": df_avg.index,"Temperature": df_avg['Temperature'],"Humidity": df_avg['Humidity'],"Soil1": df_avg['Soil1'],"Soil2": df_avg['Soil2'],"Soil3": df_avg['Soil3']}).set_index('index')
        df_avg_j.Temperature = round(df_avg_j.Temperature,1)
        df_avg_j.Humidity = round(df_avg_j.Humidity,1)
        df_avg_j.Soil1 = round(df_avg_j.Soil1,1)
        df_avg_j.Soil2 = round(df_avg_j.Soil2,1)
        df_avg_j.Soil3 = round(df_avg_j.Soil3,1)
        json_data = df_avg_j.to_json()
        yield f"{json_data}\n\n"
    response = Response(stream_with_context(get_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    application.run(debug=True, threaded=True,port=4000)