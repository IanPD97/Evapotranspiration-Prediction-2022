from sqlalchemy.orm import sessionmaker
from datetime import datetime
import psql_database as db
import eto_db_functions as etodb
import warnings
import time

warnings.filterwarnings("ignore")
etodb.tensorflow_ignore()


engine = db.engine
Session = sessionmaker(engine)
session = Session()

while(True):
    time_ = datetime.now()
    if time_.hour == 22 and time_.minute == 35 and time_.second<=10:
        today = datetime.now().strftime("%d-%m-%Y")
        etodb.compute_eto(session,today)
        etodb.predict_eto(session,today)
    time.sleep(10)
