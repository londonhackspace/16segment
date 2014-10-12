/*
  Drive the 16 segment led displays
 */

#define OE      8   // active high
#define STROBE  9   // active high
#define CLOCK   10
#define DATA    11

#include <SPI.h>
#include <avr/pgmspace.h>
#include <stdlib.h>

/*

with the outputs at the top, fron left to right:

pin    output bit (zero indexed!)
1          3  15
2          2  14
3          1  13
4          0  12
5          7  11
6          6  10
7          5   9
8          4   8
9          11  7
10         10  6
11         9   5 
12         8   4
13         15  3
14         14  2
15         13  1
16         12  0

last nibble -> first
first -> last
middle 2 swap

c387 -> 783c

*/

void shift(void);

// init the shift registers to all 0's
void shift_clear(void) {
  int i;

  digitalWrite(CLOCK, LOW);  
  delayMicroseconds(1);

  digitalWrite(DATA, LOW);
  delayMicroseconds(1);
  
  for (i = 0 ; i < 16 ; i++) {
    digitalWrite(CLOCK, HIGH);
    delayMicroseconds(1);
    digitalWrite(CLOCK, LOW);
    delayMicroseconds(1);
  }
}

void shift_bit(byte b) {
  digitalWrite(DATA, b & 1);
  shift();
}

void shift(void) {
  digitalWrite(CLOCK, HIGH);
  delayMicroseconds(1);
  digitalWrite(CLOCK, LOW);  
}

void send_16(const uint16_t data) {
  int i;
  for (i = 0 ; i < 16 ; i++) {
    shift_bit((data & (1 << i)) >> i);
  }
}

void blank(void) {
  int i;

  digitalWrite(OE, LOW); // outputs off
  
  digitalWrite(STROBE, LOW); // no data out (yet)
  delayMicroseconds(1);

  for (i = 0; i < 10 ; i++) {
//    shift_clear();
    send_16(0);
    delayMicroseconds(1);
  }
  delayMicroseconds(1);

  digitalWrite(STROBE, HIGH); // data out (yet)
  digitalWrite(OE, HIGH);
  delayMicroseconds(1);  
//  digitalWrite(OE, LOW);

}

void setup() {                

  pinMode(OE, OUTPUT); // output enable
  digitalWrite(OE, LOW);  // no output to start with

  pinMode(DATA, OUTPUT);

  pinMode(CLOCK, OUTPUT);
  digitalWrite(CLOCK, LOW);   // start clock on low

  pinMode(STROBE, OUTPUT);
  digitalWrite(STROBE, LOW); // don't propergate the register contents

  Serial.begin(9600);
  Serial.println("Hello World!");
  blank();

  Serial.println(">");
    
  digitalWrite(STROBE, HIGH); // put the data in the register
  
  digitalWrite(OE, LOW);
  digitalWrite(OE, HIGH); // and now we have an output
  blank();
}

#define LOOKING 0
#define RESET 1
#define WRITE 2

int state = LOOKING;
uint16_t writeval;
int writepos;
char writestr[5];

void loop() {
  int i;
  char c;

  if (Serial.available() > 0) {
    c = Serial.read();
    Serial.write(c);
    if (state == LOOKING) {
      switch (c) {
        case 'r':
          blank();
//          digitalWrite(OE, LOW);
          break;
        case 'w':
          state = WRITE;
          writepos = 0;
          writestr[4] = '\0';
          break;
        default:
          Serial.println("usage: 'r' to reset, 'wxxxx' with x = 4 hex digits");
          break;
      }
    } else if (state == WRITE) {
      writestr[writepos] = c;
/*      Serial.print("got: ");
      Serial.write(c);
      Serial.print(" ");
      Serial.println(writepos);*/
//      writeval += hex << (writepos * 4)
      writepos++;
      if (writepos > 3) {
        writeval = strtoul(writestr, NULL, 16);
//        Serial.print("Sending: ");
//        Serial.println(writeval, HEX);
        digitalWrite(STROBE, LOW); // no data out (yet)
        send_16(writeval);
        digitalWrite(STROBE, HIGH); // data out
        digitalWrite(OE, HIGH); // outputs on
        
        writepos = 0;
        state = LOOKING;
      }
    }
  }
}

