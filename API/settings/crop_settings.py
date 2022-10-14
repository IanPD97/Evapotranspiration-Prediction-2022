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