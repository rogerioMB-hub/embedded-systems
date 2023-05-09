
#include <SoftwareSerial.h>

SoftwareSerial MasterBoard(10, 11); // RX, TX
char recebido;
void setup() 
{
  Serial.begin(9600);
  pinMode(13,OUTPUT);
}

void loop() { // run over and over
  int statusSerial = MasterBoard.available();

  Serial.print("BufferSize:");
  Serial.println(statusSerial);
  
  if (statusSerial>0) 
  {
    recebido = MasterBoard.read();
    Serial.write(recebido);
    if (recebido=='0')
    {
      digitalWrite(13, LOW);
    }
    if (recebido=='1')
    {
      digitalWrite(13, HIGH);
    }
  }
  
}
