postgresql = {
    'pguser': 'postgres',   # Nombre de usuario en PSQL
    'pgpasswd': '1234',     # Contraseña
    'pghost': 'localhost',  # IP de la base de datos
    'pgport': 5432,         # Puerto
    'pgdb': 'sensors'       # Nombre de la base de datos
}

mqtt_settings = {
    'ip': '192.168.1.111',  # Dirección IP de la Raspberry pi
    'port': 1883            # Puerto del servidor Mosquitto
}

openWeatherMap_settings = {
    'api_key': '6a9e9a96c0af5dbb6029a432d5e4ef99',
    'lat': -33.494286,
    'lon': -70.647473,
    'exclude': 'hourly,daily,minutely',
    'units': 'metric'
}