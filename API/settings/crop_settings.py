mint = {
    'plant': 'peppermint',
    'kc_ini': 0.60,         # Valores coeficiente de cultivo, según manual FAO
    'kc_med': 1.15,
    'kc_fin': 1.10,
    'Er': 0.9,              # Riego por goteo 90% de eficiencia, según INIA
    'A': 1,                 # Marco de plantación, en m2
    'PC': 1,                # Porcentaje de cobertura - porcentaje de área sombreada a las 12:00 respecto al marco de plantación
    'FC': 0.92*1+18.7       # 0.92*PC + 18.7 -> en caso de macetero, considerar las medidas del macetero respecto al marco de plantación
    # DB = (Eto*kc * A * FC/100)/Er -> Cantidad a regar en Litros
}

water = {
    'seconds': 1,      # En 'seconds' segundos se liberan
    'water': 10,       # 'water' ml de agua
    # Caudal = water/seconds

    'soilmoisture': 20, # Para aumentar un 'soilmoisture'% la humedad del suelo, se necesitan
    'soilwater': 30,    # 'soilwater' ml de agua
    # Relacion = soilwater/soilmoisture

    'dripseconds': 100, # El riego por goteo tarda 'dripseconds' segundos en regar
    'dripwater': 10     # 'dripwater' ml de agua
    # DripCaudal = dripwater/dripseconds
}

scheduled_irrigation_time = {
    'hour': 21,         # Hora diaria de riego
    'minute': 30
}