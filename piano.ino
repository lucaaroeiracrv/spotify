// Definição dos pinos
const int buzzer = 8;
const int botaoDo = 2;
const int botaoRe = 3;
const int botaoMi = 4;
const int botaoFa = 5;

// Frequências das notas (Hz)
#define DO 262
#define RE 294
#define MI 330
#define FA 349

void setup() {
  pinMode(buzzer, OUTPUT);

  pinMode(botaoDo, INPUT_PULLUP);
  pinMode(botaoRe, INPUT_PULLUP);
  pinMode(botaoMi, INPUT_PULLUP);
  pinMode(botaoFa, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(botaoDo) == LOW) {
    tone(buzzer, DO);
  } 
  else if (digitalRead(botaoRe) == LOW) {
    tone(buzzer, RE);
  } 
  else if (digitalRead(botaoMi) == LOW) {
    tone(buzzer, MI);
  } 
  else if (digitalRead(botaoFa) == LOW) {
    tone(buzzer, FA);
  } 
  else {
    noTone(buzzer);
  }
}