postgresql = {
    'pguser': 'postgres',   # Nombre de usuario en PSQL
    'pgpasswd': '1234',     # Contraseña
    'pghost': '192.168.1.111',  # IP de la base de datos
    'pgport': 5432,         # Puerto
    'pgdb': 'sensors'       # Nombre de la base de datos
}

mqtt_settings = {
    'ip': '192.168.1.111',  # Dirección IP de la Raspberry pi
    'port': 1883,           # Puerto del servidor Mosquitto
    'interval': 5,          # Intervalo de envío de los datos (Debe ser el mismo que el arduino)
}

openWeatherMap_settings = {
    'api_key': '6e63f4b358ab989e0f85bbbd853a9144',
    'lat': -33.494286,
    'lon': -70.647473,
    'units': 'metric'
}