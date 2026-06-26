#include <Servo.h>
Servo Base, Garra, Profundidade, Altura;  

// Servomotores
#define Sbase  3      
#define Sgarra 5
#define Sprof  11    
#define Salt   6

// Potenciômetros
#define Pbase  A2    
#define Pgarra A3
#define Pprof  A4
#define Palt   A5

// Botões
#define BD     12
#define BE     10
                 // Faixa dos servomotores com a função writeMicroseconds():700 a 2300
int B = 1510;    // Amplitude da base: 1056 (direita) a 1966 (esquerda), média = 1510
int G = 1200;    // Amplitude da garra: 900 (abre) a 1500 (fecha), média = 1200
int P = 1200;    // Amplitude da profundidade: 800 (trás) a 1600 (frente), média = 1200
int A = 1693;    // Amplitude da altura: 1350 (baixo) a 2036 (alto), média = 1693
int leitura;    
int Buzzer = 8;
int Sensor = 2;  
boolean estado = false;  // Inicia com a programação manual

void setup( ){
  pinMode(BD, INPUT_PULLUP);
  pinMode(BE, INPUT_PULLUP);
  pinMode(Buzzer, OUTPUT);
  pinMode(Sensor, INPUT); 
  
  Base.attach(Sbase);
  Garra.attach(Sgarra);
  Profundidade.attach(Sprof);
  Altura.attach(Salt);
  reset( );
}
 
void loop( ) {

  /*
  if(digitalRead(BE) == LOW){     // botão da esquerda para fazer o movimento automático
    reset();
    automatico();
  }
  
  if(digitalRead(BD) == LOW){         // botão da direita para trocar a programação
    estado = !estado;                 // inverte o estado entre false e true
    if(estado == false) buzmanual( );   // Som da programação manual
    else buzauto( );                  // Som da programação automática
    reset();
  }

  if(estado == true){                // Modo de funcionamento automático
    if(digitalRead(Sensor) == LOW){  // Indentificação do objeto pelo sensor de obstáculo
      buzsensor( );
      delay(300);
      automatico( );
    }
  }
  else joystick( );                   // Modo de funcionamento manual
    
} */

/*void joystick( ){                    // Controle do modo manual
  leitura = analogRead(Pbase);       // Faixa de leitura dos potenciômetros: 0 a 1023 
  if(leitura < 492)  B--;
  if(leitura < 200)  B--;
  if(leitura > 532)  B++;
  if(leitura > 823)  B++;
  B = constrain(B, 1056, 1966);   // Restringe B para o intervalo de 1056 a 1966
  Base.writeMicroseconds(B);

  leitura = analogRead(Pgarra);
  if(leitura < 492)  G--;
  if(leitura < 200)  G--;
  if(leitura > 532)  G++;
  if(leitura > 823)  G++;
  G = constrain(G, 900, 1500);
  Garra.writeMicroseconds(G);

  leitura = analogRead(Pprof);
  if(leitura > 532) P--;
  if(leitura > 823) P--;
  if(leitura < 492) P++;
  if(leitura < 200) P++;
  P = constrain(P, 800, 1600);
  Profundidade.writeMicroseconds(P);

  leitura = analogRead(Palt);
  if(leitura > 532)  A--;
  if(leitura > 823)  A--;
  if(leitura < 492)  A++;
  if(leitura < 200)  A++;
  A = constrain(A, 1350, 2036);
  Altura.writeMicroseconds(A);
  
  delay(3);
}*/

//void automatico( ){             // Programação automática do braço

    for(;B > 1420; B--){        // vira até a posição
      Base.writeMicroseconds(B);
      delay(2);
    }
    for(;P < 1520; P++){        // vai para frente
      Profundidade.writeMicroseconds(P);
      delay(2);
    }
    for(;G < 1500; G++){         // fecha a garra
      Garra.writeMicroseconds(G);
      delay(1);
    }
    for(;P > 1190; P--){         // vai para tras
      Profundidade.writeMicroseconds(P);
      delay(2);
    }
    for(;B < 1860; B++){        // gira para a esquerda
      Base.writeMicroseconds(B);
      delay(2);
    }
    for(;A > 1210; A--){         // abaixa a altura
      Altura.writeMicroseconds(A);
      delay(2);
    }
    for(;G > 1050; G--){         // abre a garra
      Garra.writeMicroseconds(G);
      delay(1);
    }   
    for(;P > 850; P--){        // vai para trás
      Profundidade.writeMicroseconds(P);
      delay(2);
    }
    reset( );
}
//}
void reset( ){                 // O braço volta para o início
    for(;B < 1600; B++){
      Base.writeMicroseconds(B);
      delay(2);
    }
    for(;B > 1600; B--){
      Base.writeMicroseconds(B);
      delay(2);
    }
    for(;P < 900; P++){
      Profundidade.writeMicroseconds(P);
      delay(2);
    }
    for(;P > 900; P--){
      Profundidade.writeMicroseconds(P);
      delay(2);
    }
    for(;A < 1360; A++){
      Altura.writeMicroseconds(A);
      delay(2);
    }
    for(;A > 1360; A--){
      Altura.writeMicroseconds(A);
      delay(2);
    }
    for(;G < 900; G++){
      Garra.writeMicroseconds(G);
      delay(1);
    }
    for(;G > 900; G--){
      Garra.writeMicroseconds(G);
      delay(1);
    }
}
/*
void buzsensor( ) {           // Som do sensor de obstáculo indentificando objeto
    tone(Buzzer,1109,500);
    delay(1000);
}


void buzauto( ) {             // Som para o modo automático
    tone(Buzzer,880,150);
    delay(300);
    tone(Buzzer,1109,150);
    delay(300);
    tone(Buzzer,1175,150);
}

void buzmanual( ){           // Som para o modo manual
    tone(Buzzer,1175,150);
    delay(300);
    tone(Buzzer,1109,150);
    delay(300);
    tone(Buzzer,880,150);
} */



