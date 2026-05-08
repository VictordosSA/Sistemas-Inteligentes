#include <Servo.h>

// Definir pinos dos servos
#define SERVO1_PIN 9
#define SERVO2_PIN 10

// Criar objetos servo
Servo servo1;
Servo servo2;

// Variáveis para armazenar posições atuais
int pos1 = 90;  // Posição inicial servo 1
int pos2 = 90;  // Posição inicial servo 2

void setup() {
  // Inicializar comunicação serial
  Serial.begin(9600);
  Serial.println("Sistema de Controle de Servos Iniciado");

  // Anexar servos aos pinos
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Mover servos para posição inicial
  servo1.write(pos1);
  servo2.write(pos2);

  Serial.println("Servos inicializados na posicao 90 graus");
}

void loop() {
  // Verificar se há dados na porta serial
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Remover espaços em branco

    Serial.print("Comando recebido: ");
    Serial.println(comando);

    // Processar comando
    if (comando.startsWith("SERVO1:")) {
      // Comando para servo 1: "SERVO1:90"
      int pos = comando.substring(7).toInt();
      if (pos >= 0 && pos <= 180) {
        pos1 = pos;
        servo1.write(pos1);
        Serial.print("Servo 1 movido para: ");
        Serial.println(pos1);
      } else {
        Serial.println("Erro: Posicao invalida para servo 1 (0-180)");
      }
    }
    else if (comando.startsWith("SERVO2:")) {
      // Comando para servo 2: "SERVO2:45"
      int pos = comando.substring(7).toInt();
      if (pos >= 0 && pos <= 180) {
        pos2 = pos;
        servo2.write(pos2);
        Serial.print("Servo 2 movido para: ");
        Serial.println(pos2);
      } else {
        Serial.println("Erro: Posicao invalida para servo 2 (0-180)");
      }
    }
    else if (comando.indexOf(",") > 0) {
      // Comando combinado: "SERVO1:90,SERVO2:45"
      int virgulaIndex = comando.indexOf(",");
      String cmd1 = comando.substring(0, virgulaIndex);
      String cmd2 = comando.substring(virgulaIndex + 1);

      // Processar primeiro servo
      if (cmd1.startsWith("SERVO1:")) {
        int pos = cmd1.substring(7).toInt();
        if (pos >= 0 && pos <= 180) {
          pos1 = pos;
          servo1.write(pos1);
          Serial.print("Servo 1 movido para: ");
          Serial.println(pos1);
        }
      }

      // Processar segundo servo
      if (cmd2.startsWith("SERVO2:")) {
        int pos = cmd2.substring(7).toInt();
        if (pos >= 0 && pos <= 180) {
          pos2 = pos;
          servo2.write(pos2);
          Serial.print("Servo 2 movido para: ");
          Serial.println(pos2);
        }
      }
    }
    else {
      Serial.println("Comando invalido. Use: SERVO1:angulo ou SERVO2:angulo ou SERVO1:angulo,SERVO2:angulo");
    }
  }

  // Pequeno delay para estabilidade
  delay(50);
}