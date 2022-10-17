import json
from time import time
from time import sleep
from flask import Flask, render_template, make_response
from sqlalchemy.orm import sessionmaker
import psql_database as db
from datetime import datetime

app = Flask(__name__)
today = datetime.now()
engine = db.engine
Session = sessionmaker(engine)
session = Session()

@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index_graphs.html')


@app.route('/data', methods=["GET", "POST"])
def data():
    Temperature = session.query(db.Sensor.temperature).order_by(db.Sensor.value_date.desc()).limit(1)[0][0]
    Humidity = session.query(db.Sensor.humidity).order_by(db.Sensor.value_date.desc()).limit(1)[0][0]
    Date = session.query(db.Sensor.value_date).order_by(db.Sensor.value_date.desc()).limit(1)[0][0]
    sleep(5)
    data = [time()*1000, Temperature, Humidity]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

if __name__ == "__main__":
    app.run(host='192.168.1.81',debug=True)