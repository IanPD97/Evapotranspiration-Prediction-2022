""" Creación de la base de datos. Ejecutar sólo la primera vez"""

from sqlalchemy import Column, Integer, DateTime, Float, Date
from sqlalchemy.ext.declarative import declarative_base
import psql_connection as connection


engine = connection.get_engine_from_settings()
Base = declarative_base()


class Sensor(Base):
    """ Tabla para almacenar los datos de los sensores"""
    __tablename__ = 'sensor_data'
    value_date = Column(DateTime(),primary_key = True)
    temperature = Column(Float())
    humidity = Column(Float())
    sunshine = Column(Float())
    soilMoisture1 = Column(Integer())
    soilMoisture2 = Column(Integer())
    soilMoisture3 = Column(Integer())

class computedEto(Base):
    """ Tabla que almacena datos historicos de ETo real"""
    __tablename__ = 'computed_eto'
    value_date = Column(Date(),primary_key = True)
    computed_eto = Column(Float(), nullable = False)
    irrigation_value = Column(Float(), nullable = False)

class predictedEto(Base):
    """ Tabla que almacena datos historicos de ETo predicha"""
    __tablename__ = 'predicted_eto'
    id = Column(Integer(),primary_key = True, autoincrement = True)
    value_date = Column(Date(), nullable = False) # Fecha del registro
    prediction_date = Column(Date(), nullable = False) # Fecha de la predicción
    predicted_eto = Column(Float(), nullable = False)  # Valor predicho
    predicted_irrigation_value = Column(Float(), nullable = False)

class waterAmount(Base):
    __tablename__ = 'water_amount'
    value_date = Column(Date(), primary_key = True)
    water_amount = Column(Float(), nullable = False)

if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)