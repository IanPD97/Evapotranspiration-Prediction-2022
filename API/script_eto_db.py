from sqlalchemy.orm import sessionmaker
from datetime import datetime
import psql_database as db
import eto_db_functions as etodb
import warnings

warnings.filterwarnings("ignore")
etodb.tensorflow_ignore()


engine = db.engine
Session = sessionmaker(engine)
session = Session()
today = datetime.now().strftime("%d-%m-%Y")

if (etodb.compute_eto(session,today)):
    etodb.predict_eto(session,today)
