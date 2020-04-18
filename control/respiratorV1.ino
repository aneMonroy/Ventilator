//---- ARDUINO LIBS ----------------//
//#include <SoftwareSerial.h>

//-----------------------------------------------------
//SoftwareSerial raspCom(3,4); //Serial Raspberry
#include "defaults.h"

uint8_t _rpm;
int _tidalVol;
bool initControl;
uint8_t _ieRatio;

void readIncomingMsg(void)
{
  char msg[100];
  Serial.readStringUntil('\n').toCharArray(msg,100);
  if (String(msg).substring(0,3)=="BPM")
  {
    int rc = sscanf(msg,"BPM %d", &_rpm);
    if(rc==1)
    {
      if(_rpm > MAX_RPM)
        _rpm = MAX_RPM;
      if(_rpm < MIN_RPM)
        _rpm = MIN_RPM;
      Serial.print("Set BPM: ");
      Serial.println(_rpm);
    }
  }
   else if(String(msg).substring(0,3)=="VOL")
   {
    int rc = sscanf(msg,"VOL %d", &_tidalVol);
    if(rc==1)
    {
      if(_tidalVol > MAX_VOL)
        _tidalVol = MAX_VOL;
      if(_tidalVol < MIN_VOL)
        _tidalVol = MIN_VOL;
      Serial.print("Set Volume: ");
      Serial.println(_tidalVol);
    }
   }
   else if(String(msg).substring(0,3)=="IRE")
   {
    int rc = sscanf(msg,"I:E %d", &_ieRatio);
    if(rc==1)
    {
      if (_ieRatio > 4 or _ieRatio <1)
        _ieRatio = 1I_2E;
      Serial.print("Set I:E: ");
      Serial.println(_ieRatio);
    }
   }
   else
   {
     initControl = true;
     Serial.println("Started/Updated");    
   }
}


void setup()
{
    // Puertos serie
    Serial.begin(115200);
    Serial.println("ArduinoRDY");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available())
  {
    readIncomingMsg();
  }

}

