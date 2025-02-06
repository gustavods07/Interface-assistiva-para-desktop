#include <Mouse.h>
void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:

}

void loop() {
  int c =digitalRead(A0);
  int b =digitalRead(A1);
  int d =digitalRead(A2);
  int e =digitalRead(A3);
  int cd =digitalRead(A6);
  int ce =digitalRead(A8);

        // say what you got:
      if (c ==HIGH){Mouse.move(0,-1,0);}
      //cima
      if (e ==HIGH){Mouse.move(-1,0,0);}
      //esquerda
      if (b ==HIGH){Mouse.move(0,1,0);}
      //baixo
      if (d ==HIGH){Mouse.move(1,0,0);}
      //direita
      if (ce ==HIGH){Mouse.press(MOUSE_LEFT);Mouse.release(MOUSE_LEFT);}
      //clique esquerdo
      if (cd ==HIGH){Mouse.press(MOUSE_RIGHT);Mouse.release(MOUSE_RIGHT);}
      //clique direito
  // put your main code here, to run repeatedly:

}
