#include <LiquidCrystal.h>
#include <Wire.h>
#include <IRremote.hpp>
#include "DHT.h"

#define DHTTYPE DHT11   // DHT 11
#define DHTPIN 5    // Digital pin connected to the DHT sensor
//use pins 3, 4, 5, 12, 13 or 14 --

// inizializza la libreria con i numeri dei pin utilizzati
LiquidCrystal lcd(2, 3, 4, 12, 9, 11);
DHT dht(DHTPIN, DHTTYPE);
const int PIRPin = 6;
const int buzzer = 10;
float RH=0, temperature=0;
const int RECV_PIN = 13;

float movementDetect=0;

int errorDetected=0;
String lati="",longi="",dateGPS="",timeGPS="";
int  firstLoop=1;
decode_results results;
unsigned long key_value = 0;
String InBytes;







void setup() {
  // imposta il numero di colonne e righe del display utilizzato:

  pinMode(PIRPin, INPUT);
  pinMode(buzzer, OUTPUT);
  lcd.begin(16, 2);
  dht.begin();


  IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK); // Start the receiver

  lcd.clear();
  lcd.print("Station N.");
  lcd.setCursor(0, 1);
  lcd.print(5);
  Wire.begin(9); 
  // Attach a function to trigger when something is received.
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);
}

uint32_t timer = millis();

void loop() {

      if(firstLoop == 1){
          firstLoop = 0;
          RH= dht.readHumidity();
          temperature= dht.readTemperature();
        }


  if (IrReceiver.decode()){

        key_value=IrReceiver.decodedIRData.decodedRawData;
        


        if(key_value == 0xF30CFF00){

            lcd.clear();
            if(dateGPS.length()==0){
              lcd.print("Station N.");
              lcd.setCursor(0, 1);
              lcd.print(5);
              }
            else{

              lcd.print("Station N. 5");
              lcd.setCursor(0, 1);
              lcd.print(dateGPS+" "+timeGPS);
              }


              }



        else if(key_value == 0xE718FF00){
            lcd.clear();
            lcd.print("Temp :"+ String(temperature)+" "+(char)223+"C");
            lcd.setCursor(0, 1);
            lcd.print("Hum  :"+ String(RH)+" %RH");


          }
       else if(key_value == 0xA15EFF00){

        if(lati==0 and longi==0){
            lcd.clear();
            lcd.print("NOT FIX POS");
            lcd.setCursor(0, 1);
            lcd.print("NOT AVAILABLE");

          }
        else{
            lcd.clear();
            lcd.print("LAT:"+lati);
            lcd.setCursor(0, 1);
            lcd.print("LONG:"+longi);

          }
          }
        IrReceiver.resume();

  }

    int val = digitalRead(PIRPin);
        if (val == HIGH) {
          movementDetect=1;

        }
        if(Serial.available()>0){
          InBytes = Serial.readStringUntil('\n');
          if ( InBytes =="on"){
            errorDetected=1;
            InBytes="";
            
            }
          
          
          }
        
        if(movementDetect && errorDetected ){
          tone(buzzer, 1000); // Send 1KHz sound signal...
          delay(1000); // wait for a second
          noTone(buzzer);     // Stop sound...
          delay(100); // wait for a second
          IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK); // Start the receiver
          
          }



        if(millis() - timer > 10000){
          timer = millis(); // reset the timer
          String techData="";
          RH= dht.readHumidity();
          temperature= dht.readTemperature();
          String RH_string=String(RH);
          String temp_string=String(temperature);
          String movement_string=String(movementDetect);
          techData+=RH_string;
          techData+=',';
          techData+=temp_string;
          techData+=',';
          techData+=movement_string;
          Serial.println(techData);
          movementDetect=0;

          errorDetected=0;

          }
}


 
void receiveEvent(int howMany)
{

  
  String  wire_in="";
  while(Wire.available() > 0) // loop through all but the last
  {
    char c = Wire.read(); // receive byte as a character
    wire_in.concat(c);
    delay(10);

  }
  Serial.println(wire_in);
  int ind1 = wire_in.indexOf(',');  //finds location of first ,
  timeGPS = wire_in.substring(0, ind1);   //captures first data String
  int   ind2 = wire_in.indexOf(',', ind1+1 );   //finds location of second ,
  dateGPS = wire_in.substring(ind1+1, ind2);   //captures second data String
  int    ind3 = wire_in.indexOf(',', ind2+1 );
  lati = wire_in.substring(ind2+1, ind3);
  int    ind4 = wire_in.indexOf(',', ind3+1);
  longi = wire_in.substring(ind3+1);

}
   




  
