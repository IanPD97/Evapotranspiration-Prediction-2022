import time
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import func
from pyet.combination import pm_fao56
from pyet.rad_utils import calc_rad_sol_in
from pyet.meteo_utils import daylight_hours
import psql_database as db
from DL.CNN import tcn_prediction as tcnn
import time

# VARIABLES
config = {
    'DEG_TO_RAD_CONSTANT' : 0.01745329251,          # Constante para transformar la latitud a radianes
    'lat' : -33.3971255,                            # Latitud del lugar donde se realiza el experimento
    'lat_rad' : float(-33.3971255) * 0.01745329251, # Transformación a radianes
    'num' : 6,                                      # Número de modelos en el ensemble de TCN
    'savename' : 'DL/tcn-models/model_0-',          # Ruta de los modelos entrenados
    'forecast_horizon' : 7                          # Horizonte de predicciones
}


# FUNCIONES
def tensorflow_ignore():
    """
    Make Tensorflow less verbose
    """
    import os
    try:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        # noinspection PyPackageRequirements
        import tensorflow as tf
        from tensorflow.python.util import deprecation
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        # Monkey patching deprecation utils to shut it up! Maybe good idea to disable this once after upgrade
        # noinspection PyUnusedLocal
        def deprecated(date, instructions, warn_once=True):  # pylint: disable=unused-argument
            def deprecated_wrapper(func):
                return func
            return deprecated_wrapper
        deprecation.deprecated = deprecated
    except ImportError:
        pass

def get_climatic_data(session):
    """ Obtener la información climática del día necesaria para realizar
        el cálculo de la Evapotranspiración, desde la base de datos"""

    today = datetime.now().strftime("%d-%m-%Y")
    tmax = session.query(func.max(db.Sensor.temperature)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    tmin = session.query(func.min(db.Sensor.temperature)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    tmean = session.query(func.avg(db.Sensor.temperature)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    rh = session.query(func.avg(db.Sensor.humidity)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    rhmin = session.query(func.min(db.Sensor.humidity)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    rhmax = session.query(func.max(db.Sensor.humidity)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    ssh = session.query(func.avg(db.Sensor.sunshine)).filter(
        func.to_char(db.Sensor.datetime, 'DD-MM-YYYY') == today)[0][0]
    return tmax, tmin, tmean, rh, rhmin, rhmax, ssh

def compute_eto(session,today):
    try:    
        computed_eto_exists = session.query(func.count(db.computedEto.date)).filter(
        func.to_char(db.computedEto.date, 'DD-MM-YYYY') == today)[0][0]
        if computed_eto_exists == 0:
            tmax,tmin,tmean,rh,rhmin,rhmax,ssh = get_climatic_data(session)
            df = pd.DataFrame(
                data = {'date':[today],
                        'tmean':[tmean],
                        'tmin':[tmin],
                        'tmax':[tmax],
                        'rh':[rh],
                        'rhmin':[rhmin],
                        'rhmax':[rhmax],
                        'wind':[0.05], 
                        'ssh':[ssh]}).set_index('date')
            df.index = pd.to_datetime(df.index,format='%d-%m-%Y')
            df['rs'] = calc_rad_sol_in(tindex = df.index,
                                    lat = config['lat_rad'],
                                    n = df.ssh*daylight_hours(df.index,config['lat_rad'])[0])
            computed_eto = pm_fao56(tmean = df.tmean,
                                    tmin = df.tmin,
                                    tmax = df.tmax,
                                    rh = df.rh,
                                    rhmin = df.rhmin,
                                    rhmax = df.rhmax,
                                    wind = df.wind,
                                    rs = df.rs,
                                    lat = config['lat_rad'],
                                    elevation = 20.0).values[0]
            eto = db.computedEto(date = today,computed_eto = computed_eto, id_crop = 1)
            session.add(eto)
            session.commit()
            print("Evapotranspiración calculada y guardada exitosamente")
            return True
        else:
            print("Ya se registró la evapotranspiración correspondiente al día de hoy")
            return True
    except:
        print("La base de datos no contiene valores válidos")
        return False

def predict_eto(session,today):
    try:
        predicted_eto_exists = session.query(func.count(db.predictedEto.date)).filter(
        func.to_char(db.predictedEto.date, 'DD-MM-YYYY') == today)[0][0]
        if predicted_eto_exists == 0:
            eto_back = session.query(db.computedEto.computed_eto).order_by(db.computedEto.date.desc()).limit(84)
            test = []
            t = []
            for eto in eto_back:
                t.append(eto[0])
            for i in range(len(t)):
                test.append(t[len(t)-i-1])
            test = pd.Series(test)
            models = tcnn.loadModels(savename = config['savename'], num = config['num'])
            for i in range(config['forecast_horizon']):
                predicted_values = tcnn.probabilisticForecast(test=test,models=models)
                predicted_value = predicted_values[0][0].sample(1000).mean()
                test = pd.Series(np.insert(np.array(test),len(test),predicted_value))
                values = db.predictedEto(date = datetime.now().strftime("%d-%m-%Y"),
                                        forecast_horizon = i+1,
                                        predicted_eto = predicted_value,
                                        id_crop = 1)
                session.add(values)
                session.commit()
                print(f'Predicción a {i+1} dias de horizonte guardada exitosamente')
                time.sleep(1)
        else:
            print("Ya se realizaron las predicciones correspondientes a este día")
            
    except Exception:
        import traceback
        traceback.print_exc()
        