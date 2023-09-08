int dado; // variável que recebe valor inteiro originário do conversor ADC (0 a 1023).
float v;  // variável que recebe valor float/real originário da relação linear da tensão com a amostra do ADC.

void setup() {
  //define porta serial com taxa de 9600 bits/s.
  Serial.begin(9600);  

}

void loop() {
  // leitura do conversor analógico-digital, entrada A0
  dado = analogRead(A0);

  // regra de 3 para converter de valor_adc (0 a 1023) para valor de tensão (0 a 5)
  // 
  //         dado ---- 1023
  //            v ---- 5.0
  //
  // Obs: a tensão é valor real, definido aqui como float
  
  v = (dado * 5.0) / 1023;

  //espera 100ms
  delay(100);
  // e mostra na serial 
  Serial.println(v);
}
