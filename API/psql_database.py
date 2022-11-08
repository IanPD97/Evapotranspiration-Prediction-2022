""" Creación de la base de datos. Ejecutar sólo la primera vez"""

from sqlalchemy import Column, Integer, DateTime, Float, Date, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psql_connection as connection
from datetime import datetime
from settings.crop_settings import mint
import pandas as pd
import time
import os

engine = connection.get_engine_from_settings()
Base = declarative_base()
path = os.path.dirname(os.path.realpath(__file__))
path = path.replace('\\',"/")

class Plant(Base):
    __tablename__ = 'plant'
    id_plant = Column(Integer(),primary_key = True, autoincrement = True)
    name = Column(String(20))
    kc_ini = Column(Float())
    kc_med = Column(Float())
    kc_fin = Column(Float())
    created_at = Column(DateTime())

class Crop(Base):
    __tablename__ = 'crop'
    id_crop = Column(Integer(),primary_key = True, autoincrement = True)
    id_plant = Column(Integer(),ForeignKey('plant.id_plant'))
    er = Column(Float())
    a = Column(Float())
    pc = Column(Float())
    created_at = Column(DateTime())

class Sensor(Base):
    """ Tabla para almacenar los datos de los sensores"""
    __tablename__ = 'sensor_data'
    datetime = Column(DateTime(),primary_key = True)
    id_crop = Column(Integer(),ForeignKey('crop.id_crop'))
    temperature = Column(Float())
    humidity = Column(Float())
    sunshine = Column(Float())
    soilMoisture1 = Column(Integer())
    soilMoisture2 = Column(Integer())
    soilMoisture3 = Column(Integer())

class computedEto(Base):
    """ Tabla que almacena datos historicos de ETo real"""
    __tablename__ = 'computed_eto'
    date = Column(Date(),primary_key = True)
    computed_eto = Column(Float(), nullable = False)
    id_crop = Column(Integer(),ForeignKey('crop.id_crop'))

class predictedEto(Base):
    """ Tabla que almacena datos historicos de ETo predicha"""
    __tablename__ = 'predicted_eto'
    id = Column(Integer(),primary_key = True, autoincrement = True)
    date = Column(Date(), nullable = False) # Fecha del registro
    forecast_horizon = Column(Integer(), nullable = False) # Horizonte de predicción respecto a la fecha del registro
    predicted_eto = Column(Float(), nullable = False)  # Valor predicho
    id_crop = Column(Integer(),ForeignKey('crop.id_crop'))

class waterAmount(Base):
    __tablename__ = 'water_amount'
    date = Column(Date(), primary_key = True)
    water_amount = Column(Float(), nullable = False)
    id_crop = Column(Integer(),ForeignKey('crop.id_crop'))

Session = sessionmaker(engine)
session = Session()

if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    plant = Plant(name = mint['plant'], kc_ini = mint['kc_ini'] , kc_med = mint['kc_med'] , kc_fin = mint['kc_med'] , created_at = datetime.now())
    session.add(plant)
    session.commit()
    id_plant = session.query(Plant.id_plant).filter(Plant.name == 'peppermint')[0][0]
    crop = Crop(id_plant = id_plant, er = mint['Er'],a = mint['A'], pc = mint['PC'], created_at = datetime.now())
    session.add(crop)
    session.commit()


    data = pd.read_csv(path +'/data/data.csv')
    df = data[['Data','Eto']].set_index('Data')
    id_crop = session.query(Crop.id_crop).filter(Crop.id_plant == id_plant)[0][0]
    for i in range(len(df)):
        date = df.index[i:i+1][0]
        date = datetime.strptime(date, '%d-%m-%Y').strftime("%d-%m-%Y")
        eto = df.Eto[i:i+1][0]
        Eto = computedEto(date = date, computed_eto = eto, id_crop = id_crop)
        session.add(Eto)
        session.commit()
        time.sleep(0.02)
    print('Finalizado! ')
