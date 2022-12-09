#include "DHT.h"               //Librería del sensor DHT11
#include "config.h"            //Configuración de conexiones (WiFi - MQTT - Sensores(pines))

#include <SPI.h>               //v
#include <WiFi101.h>           //Librería de conexión WiFi
#include <ArduinoMqttClient.h> //Librería de MQTT

#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE); //Inicialización de la librería

#define OFF HIGH // Cambiar en caso de no funcionar el relay
#define ON LOW

//Datos de conexión a WiFi
const char ssid[]= SECRET_SSID;
const char pass[]= SECRET_PASS;
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

//Servidor de MQTT Mosquitto alojado en la Raspberry Pi
const char broker[] = IP; //IP de la Raspberry Pi
int port = P;             //Puerto de MQTT (por defecto es 1883)

//Tópico de publicación (envío de datos)
const char sensor[] = "data/Sensor";

//Tópico de suscripción (para recibir órdenes)
const char relay[] = "relay/Signal";

const long interval = 5000; //intervalo de envío de los datos
unsigned long previousMillis = 0;
int count = 0;



void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(RELAYPIN, OUTPUT);    //Inicialización del Relé
  digitalWrite(RELAYPIN, OFF); //Estado inicial Apagado
  // En caso de no funcionar, cambiar las definiciones de ENCENDIDO y APAGADO al inicio del código
  
  connectMQTT(mqttClient);
  reconnectIfError();
  mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(relay);
  Serial.print("Topic: ");
  Serial.println(relay);
}



void loop() {
  mqttClient.poll();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval){
    //Guardar el estado previo
    previousMillis = currentMillis;

    //DHT11
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    String temp = String(t);
    String hum = String(h);
    if (isnan(t)){
      temp = "null";
    }
    if (isnan(h)){
      hum = "null";
    }
    
    //SOIL MOISTURE
    int sm1_percent = getPercent(map(analogRead(PINSM_1), airValue1, waterValue1, 0, 100));
    int sm2_percent = getPercent(map(analogRead(PINSM_2), airValue2, waterValue2, 0, 100));
    int sm3_percent = getPercent(map(analogRead(PINSM_3), airValue3, waterValue3, 0, 100));

    String sensor_data = "{Temperature: "+ String(t)+ ", Humidity: "+ String(h)+", SM1: "+String(sm1_percent)+", SM2: "+String(sm2_percent)+", SM3: "+String(sm3_percent)+"}";

    String test ="{\"Temperature\": "+ temp +", "+"\"Humidity\": "+ hum +", "+"\"SM1\": "+String(sm1_percent)+", "+"\"SM2\": "+String(sm2_percent)+", "+"\"SM3\": "+String(sm3_percent)+"}";

    Serial.print("Sending message to topic: ");
    Serial.println(sensor);
    Serial.println(test);

    // ENVÍO DE LOS DATOS POR MQTT
    mqttClient.beginMessage(sensor);
    mqttClient.print(test);
    mqttClient.endMessage();
    
  }
  reconnectIfError();
}


/*--------------------FUNCIONES--------------------*/

//Reconectar en caso de desconexión repentina
void reconnectIfError(){
  while (!mqttClient.connected()){
  mqttClient.connect(broker,port);
  if (!mqttClient.connected()){
    Serial.println("Reconnecting to MQTT...");
    delay(2000);
  }
  else{
    Serial.println("Connected to MQTT!");
  }
  
    if (WiFi.status()!= WL_CONNECTED){
      while (WiFi.begin(ssid, pass) != WL_CONNECTED){
        //failed, retry
        Serial.println("Reconnecting to WiFi...");
        delay(2000);
      }
      Serial.println("Connected to WiFi!");
    }
  }
  mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(relay);
}


//Recepción de mensajes desde la Raspberry Pi
void onMqttMessage(int messageSize) {
  String sign = "";
  Serial.println("Received a message with topic '");
  Serial.println(mqttClient.messageTopic());
  while (mqttClient.available()) {
    sign = sign + (char)mqttClient.read();
  }
  Serial.println(sign);
  float irrigation_time = sign.toFloat();
  turnOnRelay(irrigation_time);
}


//Conexión de WiFi y servidor MQTT
void connectMQTT(MqttClient mqttClient){
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED){
    //failed, retry
    Serial.print(".");
    delay(5000);
  }
  Serial.println("You're connected to the network");
  Serial.println();
  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);
  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while(1);
  }
  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}


//Encender el relay x segundos
void turnOnRelay(float irrigation_time){
  digitalWrite(RELAYPIN,ON);
  delay(100);
  digitalWrite(RELAYPIN,OFF);
  Serial.print("Relay on for ");
  Serial.print(irrigation_time);
  Serial.println(" seconds...");
  delay((irrigation_time*1000));
  digitalWrite(RELAYPIN,ON);
  delay(100);
  digitalWrite(RELAYPIN,OFF);
}


//Regular valores anormales de los sensores
int getPercent(int SMPercent){
  if (SMPercent >= 100){
    SMPercent = 100;
  }
  else if (SMPercent <= 0){
    SMPercent = 0;
  }
  return SMPercent;
}
