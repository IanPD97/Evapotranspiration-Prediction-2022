/* CREDENCIALES */
// Datos WiFi
#define SECRET_SSID "movistar2,4GHZ_E210AA"
#define SECRET_PASS "Cincuenta50"
// Datos del servidor de MQTT
#define IP "192.168.1.111"
#define P 1883 //Puerto


/* CONFIGURACION DE LOS SENSORES*/
// Valores registrados en los sensores de humedad del suelo
//SECO
#define airValue1 697
#define airValue2 707
#define airValue3 713
//AGUA
#define waterValue1 251
#define waterValue2 284
#define waterValue3 265

// Pines de conexion
#define RELAYPIN 2 //Pin digital en el que esta conectado el relay
#define PINSM_1 A1 //Pines analogicos de los sensores de humedad del suelo
#define PINSM_2 A2 //--
#define PINSM_3 A3 //--
#define DHTPIN 3   //Pin digital al que se conecta el sensor de temperatura y humedad DHT11
