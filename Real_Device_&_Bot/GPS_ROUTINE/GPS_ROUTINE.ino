// Test code for Adafruit GPS modules using MTK3329/MTK3339 driver
//
// This code shows how to listen to the GPS module in an interrupt
// which allows the program to have more 'freedom' - just parse
// when a new NMEA sentence is available! Then access data when
// desired.
//
// Tested and works great with the Adafruit Ultimate GPS module
// using MTK33x9 chipset
//    ------> http://www.adafruit.com/products/746
// Pick one up today at the Adafruit electronics shop
// and help support open source hardware & software! -ada

#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <Wire.h>

// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// Connect the GPS TX (transmit) pin to Digital 8
// Connect the GPS RX (receive) pin to Digital 7

// you can change the pin numbers to match your wiring:
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);
char* charArr;
int actualcharposistion = 0;
String hour = "";
String minute = "";
String day = "";
String month = "";

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO  false

void setup()
{

  // connect at 115200 so we can read the GPS fast enough and echo without dropping chars
  // also spit it out
  Serial.begin(115200);
  delay(5000);
  Serial.println("Adafruit GPS library basic parsing test!");

  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);

  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // For parsing data, we don't suggest using anything but either RMC only or RMC+GGA since
  // the parser doesn't care about other sentences at this time

  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  // For the parsing code to work nicely and have time to sort thru the data, and
  // print it out we don't suggest using anything higher than 1 Hz

  // Request updates on antenna status, comment out to keep quiet
  GPS.sendCommand(PGCMD_ANTENNA);

  delay(1000);


  Wire.begin(); 
}

uint32_t timer1 = millis();
uint32_t timer2 = millis();
void loop()                     // run over and over again
{
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!


  // if a sentence is received, we can check the checksum, parse it...
  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false

    if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

  // approximately every 2 seconds or so, print out the current stats
  if (millis() - timer1 > 2000) {
    timer1 = millis(); // reset the timer
    if (GPS.fix) {

      String hour = "";
      String minute = "";
      String day = "";
      String month = "";
      String year = "";

      if (GPS.hour < 10) {hour +='0'; }
      hour = String(hour+(GPS.hour+1));
      
      if (GPS.minute < 10) {minute+='0'; }
      minute = String(minute+GPS.minute);
      
      if (GPS.day < 10) {day += '0'; }
      day = String(day+GPS.day);
      
      if (GPS.month < 10) {month+='0';}
      month = String(month+GPS.month);
      year+="20";
      year+=GPS.year;
      String lati=String(GPS.latitudeDegrees);
      String longi=String(GPS.longitudeDegrees);
     // String toSend=String(day+'/'+month+'/'+year+','+ hour+':'+minute+','+lati+','+longi);
      String toSend="";
      toSend+=hour;
      toSend+=':';
      toSend+=minute;
      toSend+=',';
      toSend+=day;
      toSend+='/';
      toSend+=month;
      toSend+='/';
      toSend+=year;
      toSend+=',';
      toSend+=lati;
      toSend+=',';
      toSend+=longi;
      Serial.println(toSend);
 
      if (millis() - timer2 > 30000) {
        timer2 = millis();
        Wire.beginTransmission(9); // transmit to device #9
        Wire.print(toSend);       // sends charArr
        Wire.endTransmission();    // stop transmitting
      }

    }



  
    }
  }
