import psql_database as db
from sqlalchemy.orm import sessionmaker

engine = db.engine
Session = sessionmaker(engine)
session = Session()

eto = float(input('Ingrese ETo: '))

def compute_irrigation_value(computed_eto):
    id_plant = session.query(db.Plant.id_plant).filter(db.Plant.name == 'peppermint')[0][0]
    kc_ini = session.query(db.Plant.kc_ini).filter(db.Plant.id_plant == id_plant)[0][0]
    kc_med = session.query(db.Plant.kc_med).filter(db.Plant.id_plant == id_plant)[0][0]
    a = session.query(db.Crop.a).filter(db.Crop.id_plant == id_plant)[0][0]
    pc = session.query(db.Crop.pc).filter(db.Crop.id_plant == id_plant)[0][0]
    er = session.query(db.Crop.er).filter(db.Crop.id_plant == id_plant)[0][0]
    water_demand = ((computed_eto*((kc_ini+kc_med)/2)*a*(pc/100))/er)*1000
    return water_demand


print(compute_irrigation_value(eto))