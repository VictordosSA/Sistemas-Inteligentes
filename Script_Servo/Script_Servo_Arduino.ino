#include <Servo.h>

// Definir pinos dos servos
#define SERVO1_PIN 2
#define SERVO2_PIN 10

//Parte do Codigo da Garra
// --- Definição dos Pinos ---
#define S1_PIN 5   // Garra
#define S2_PIN 11  // Braço 2 (Profundidade)
#define S3_PIN 6   // Braço 1 (Altura)
#define S4_PIN 3   // Base

//Parte do Codigo da Garra
// --- Instanciando os Servos ---
Servo s1, s2, s3, s4;

// Criar objetos servo
Servo servo1;
Servo servo2;

// Variáveis para armazenar posições atuais
int poss1 = 180;  // Posição neutra/stop servo 1
int poss2 = 180;  // Posição neutra/stop servo 2


//Parte do Codigo da Garra
// --- Posição atual dos servos ---
int pos1 = 90; 
int pos2 = 70;
int pos3 = 90;
int pos4 = 89;

// --- Limites de segurança ---
int limiteMin = 20;
int limiteMax = 180;

// --- Configurações de movimento ---
//Para deixar ainda mais leve, mexa nestes dois valores:
//            Se quiser mais lento e suave:
//int velocidade = 25;
//int fatorSuavidade = 4;
//              Se ficar lento demais, use:
//int velocidade = 15;
//int fatorSuavidade = 2;
int velocidade = 20;       // Maior = mais lento
int fatorSuavidade = 2;    // Maior = movimento mais leve
//////////////////////////////////////////////////////////////////////////////////
int tempoPausa = 200;     // Pausa entre as etapas




// Tempo padrão (ms) que um comando sem duração fará o servo se mover antes de retornar a neutro
const unsigned long DEFAULT_MOVE_MS = 500;

void setup() {
  // Inicializar comunicação serial
  Serial.begin(9600);
  Serial.println("Sistema de Controle de Servos Iniciado");

  // Anexar servos aos pinos
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Mover servos para posição neutra inicial
  poss1 = 90;
  poss2 = 90;
  servo1.write(poss1);
  servo2.write(poss2);

  Serial.println("Servos inicializados na posicao neutra (90 graus)");

 s1.attach(S1_PIN);
  s2.attach(S2_PIN);
  s3.attach(S3_PIN);
  s4.attach(S4_PIN);

  // Escreve a posição inicial para evitar movimentos bruscos
  escreverServos(pos1, pos2, pos3, pos4);
 

  Serial.println("Inicializando braço suavemente...");
  executarMovimento(95, 70, 90, 97);

}

void loop() {
  // Verificar se há dados na porta serial
  if (Serial.available() > 0) {

    FuncionaGarra();
    
  }

  // Pequeno delay para estabilidade
  delay(10);
}

// --- NÃO colocar outras definições de função dentro de loop() ---
// Função que executa sequência completa da garra (fora do loop)
void FuncionaGarra() {
  Serial.println("Iniciando sequência automática...");
  p1(); delay(tempoPausa);
  p2(); delay(tempoPausa);
  p3(); delay(tempoPausa);
  p4(); delay(tempoPausa);
  p5(); delay(tempoPausa);
  p6(); delay(tempoPausa);
  p7(); delay(tempoPausa);
  Serial.println("Sequência finalizada.");
}

// --- Função para escrever nos servos ---
void escreverServos(int a, int b, int c, int d) {
  s1.write(a);
  s2.write(b);
  s3.write(c);
  s4.write(d);
}

// --- Função para ajustar servos às posições atuais (definida para evitar erro de compilação) ---
void servosPos() {
  // garante servos na posição atual/neutral
  servo1.write(poss1);
  servo2.write(poss2);
  s1.write(pos1);
  s2.write(pos2);
  s3.write(pos3);
  s4.write(pos4);
}

// --- Função para calcular o maior movimento entre os servos ---
int maiorDistancia(int a, int b, int c, int d) {
  int maior = a;
  if (b > maior) maior = b;
  if (c > maior) maior = c;
  if (d > maior) maior = d;
  return maior;
}

// --- Movimento suave com aceleração e desaceleração ---
void executarMovimento(int d1, int d2, int d3, int d4) {
  // Trava de segurança
  d1 = constrain(d1, limiteMin, limiteMax);
  d2 = constrain(d2, limiteMin, limiteMax);
  d3 = constrain(d3, limiteMin, limiteMax);
  d4 = constrain(d4, limiteMin, limiteMax);

  int inicio1 = pos1;
  int inicio2 = pos2;
  int inicio3 = pos3;
  int inicio4 = pos4;

  int dist1 = abs(d1 - inicio1);
  int dist2 = abs(d2 - inicio2);
  int dist3 = abs(d3 - inicio3);
  int dist4 = abs(d4 - inicio4);

  int maior = maiorDistancia(dist1, dist2, dist3, dist4);
  if (maior == 0) {
    servosPos();
    return;
  }

  int totalPassos = maior * fatorSuavidade;

  for (int i = 0; i <= totalPassos; i++) {
    float t = (float)i / totalPassos;
    float suave = t * t * (3 - 2 * t); // curva suave
    pos1 = inicio1 + (d1 - inicio1) * suave;
    pos2 = inicio2 + (d2 - inicio2) * suave;
    pos3 = inicio3 + (d3 - inicio3) * suave;
    pos4 = inicio4 + (d4 - inicio4) * suave;
    escreverServos(pos1, pos2, pos3, pos4);
    delay(velocidade);
  }

  // garante destino exato
  pos1 = d1; pos2 = d2; pos3 = d3; pos4 = d4;
  escreverServos(pos1, pos2, pos3, pos4);
  servosPos();
}

// --- Funções de posição ---
//ara calibrar a garra, continue mexendo principalmente no primeiro número:

// --- Calibração da garra ---
int GARRA_FECHADA = 100;     // garra fechada
int GARRA_SEGURANDO = 95;    // garra segurando o objeto
int GARRA_ABERTA = 89;       // garra abre menos

// --- Funções de posição ---
void p1() { 
  Serial.println("P1: Garra fechada");
  executarMovimento(GARRA_ABERTA, 40, 90, 97);
}

void p2() { 
  Serial.println("P2: Garra aberta");
  executarMovimento(GARRA_ABERTA, 30, 90, 97);
}

void p3() {
  Serial.println("P3: Posicionando para pegar");
  executarMovimento(GARRA_FECHADA, 20, 70, 97);
}

void p4() {
  Serial.println("P4: Fechando garra no objeto");
  executarMovimento(GARRA_FECHADA, 20, 90, 97);
}

void p5() {
  Serial.println("P5: Levantando e girando base suavemente");

  executarMovimento(GARRA_SEGURANDO, 90, 130, 97);
  delay(100);

  executarMovimento(GARRA_SEGURANDO, 90, 130, 180);
}

void p6() {
  Serial.println("P6: Posicionando no destino");
  executarMovimento(GARRA_SEGURANDO, 90, 130, 180);
}

void p7() {
  Serial.println("P7: Soltando objeto suavemente");
  executarMovimento(GARRA_ABERTA, 90, 90, 180);

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
        delay(2000);
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


