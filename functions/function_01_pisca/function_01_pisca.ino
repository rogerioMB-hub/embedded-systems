#define out1 13

bool x=LOW;


void pisca(bool, int, int);

void setup() 
{
  // configurando pinos de saida
  pinMode(out1, OUTPUT);
}

void loop() 
{
  x=!x;
  pisca(x, out1, 100);
}


void pisca(bool y, int pino, int tms)
{
  digitalWrite(pino,y);
  delay(tms);
}
