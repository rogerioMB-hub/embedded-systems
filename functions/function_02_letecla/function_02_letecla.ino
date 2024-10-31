#define out1 13
#define out2 12
#define in1   2
#define in2   3

bool x=LOW;
bool valor;


void pisca(bool, int, int);
void le_tecla(int, int);


void setup() 
{
  // configurando pinos de saida
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
}

void loop() 
{
  x=!x;
  pisca(x, out1, 100);
  le_tecla(in1, out2);
  le_tecla(in2, out3);
  
}


void pisca(bool y, int pino, int tms)
{
  digitalWrite(pino,y);
  delay(tms);
}


void le_tecla(int ptecla, int pled)
{
  valor = digitalRead(ptecla);
  digitalWrite(pled, valor);
}