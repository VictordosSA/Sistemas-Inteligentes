#include <Servo.h>

// Definir pinos dos servos
#define SERVO1_PIN 2
#define SERVO2_PIN 10

// Criar objetos servo
Servo servo1;
Servo servo2;

// Variáveis para armazenar posições atuais
int pos1 = 90;  // Posição neutra/stop servo 1
int pos2 = 90;  // Posição neutra/stop servo 2

// Tempo padrão (ms) que um comando sem duração fará o servo se mover antes de retornar a neutro
const unsigned long DEFAULT_MOVE_MS = 200;

void setup() {
  // Inicializar comunicação serial
  Serial.begin(9600);
  Serial.println("Sistema de Controle de Servos Iniciado");

  // Anexar servos aos pinos
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Mover servos para posição neutra inicial
  pos1 = 90;
  pos2 = 90;
  servo1.write(pos1);
  servo2.write(pos2);

  Serial.println("Servos inicializados na posicao neutra (90 graus)");
}

void loop() {
  // Verificar se há dados na porta serial
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Remover espaços em branco

    Serial.print("Comando recebido: ");
    Serial.println(comando);

    // função auxiliar para processar subcomando e garantir retorno ao neutro
    auto process_and_return = [&](String sub) {
      sub.trim();
      int moveDur = 0;
      if (sub.startsWith("SERVO1:")) {
        String rest = sub.substring(7);
        int colon = rest.indexOf(':');
        int ang = (colon > 0) ? rest.substring(0, colon).toInt() : rest.toInt();
        moveDur = (colon > 0) ? rest.substring(colon + 1).toInt() : 0;
        if (ang >= 0 && ang <= 180) {
          servo1.write(ang);
          Serial.print("Servo 1 movido para: ");
          Serial.println(ang);
          if (moveDur <= 0) moveDur = DEFAULT_MOVE_MS;
          delay(moveDur);
          servo1.write(90); // garante parada/neutra
          Serial.println("Servo 1 retornou a neutro (90)");
        } else {
          Serial.println("Erro: Posicao invalida para servo 1 (0-180)");
        }
      } else if (sub.startsWith("SERVO2:")) {
        String rest = sub.substring(7);
        int colon = rest.indexOf(':');
        int ang = (colon > 0) ? rest.substring(0, colon).toInt() : rest.toInt();
        moveDur = (colon > 0) ? rest.substring(colon + 1).toInt() : 0;
        if (ang >= 0 && ang <= 180) {
          servo2.write(ang);
          Serial.print("Servo 2 movido para: ");
          Serial.println(ang);
          if (moveDur <= 0) moveDur = DEFAULT_MOVE_MS;
          delay(moveDur);
          servo2.write(90); // garante parada/neutra
          Serial.println("Servo 2 retornou a neutro (90)");
        } else {
          Serial.println("Erro: Posicao invalida para servo 2 (0-180)");
        }
      } else {
        Serial.println("Subcomando invalido: " + sub);
      }
    };

    // se houver vírgula, trata comandos combinados
    if (comando.indexOf(",") > 0) {
      int virgulaIndex = comando.indexOf(",");
      String cmd1 = comando.substring(0, virgulaIndex);
      String cmd2 = comando.substring(virgulaIndex + 1);
      process_and_return(cmd1);
      process_and_return(cmd2);
    } else {
      // comando simples
      process_and_return(comando);
    }
  }

  // Pequeno delay para estabilidade
  delay(10);
}