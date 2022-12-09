//Editar según necesidad
#define ESTADO "AGUA" //"SECO" para calibrar los sensores al aire, "AGUA" para calibrar los sensores en agua
int myPins[] = {1,2,3}; //Número de cada pin analógico asociado a los sensores de humedad del suelo


int maxValues[sizeof(myPins)];
int minValues[sizeof(myPins)];
void setup() {
  Serial.begin(9600);
  if (ESTADO == "SECO"){
    airValues();
  }
  else if (ESTADO == "AGUA"){
    waterValues();
  }
  else{
    Serial.println("ESTADO INVALIDO");
  }
}

void loop() {
  delay(500);
}

void airValues(){
  delay(5000);
  Serial.println("Calibración de los sensores AIR(SECO)");
  Serial.println("Esperar 5 minutos para obtener los valores");
  delay(2000);
  for (byte i = 0; i < (sizeof(myPins) / sizeof(myPins[0])); i++) {
    int max_ = -10;
    for (int j=0; j<200; j++){
      int SM_actual = analogRead(myPins[i]);
      if (SM_actual >= max_){
        max_ = SM_actual;
      }
      Serial.print("SM"+String(myPins[i])+" ");
      Serial.println(SM_actual);
      delay(500);
    }
    maxValues[i]=max_;
  }
  Serial.println();
  Serial.println();
  Serial.println("---Valores a escribir en config.h---"); 
  Serial.println();
  for (byte i = 0; i < (sizeof(myPins) / sizeof(myPins[0])); i++) {
    Serial.print("airValue"+String(myPins[i])+" ");
    Serial.println(maxValues[i]);
  }
}



void waterValues(){
  delay(5000);
  Serial.println("Calibración de los sensores WATER(AGUA)");
  Serial.println("Esperar 5 minutos para obtener los valores");
  delay(2000);
  for (byte i = 0; i < (sizeof(myPins) / sizeof(myPins[0])); i++) {
    int min_ = 99999;
    for (int j=0; j<20; j++){
      int SM_actual = analogRead(myPins[i]);
      if (SM_actual <= min_){
        min_ = SM_actual;
      }
      Serial.print("SM"+String(myPins[i])+" ");
      Serial.println(SM_actual);
      delay(500);
    }
    minValues[i] = min_;
  }
  Serial.println();
  Serial.println();
  Serial.println("---Valores a escribir en config.h---"); 
  Serial.println();
  for (byte i = 0; i < (sizeof(myPins) / sizeof(myPins[0])); i++) {
    Serial.print("waterValue"+String(myPins[i])+" ");
    Serial.println(minValues[i]);
  }

}
