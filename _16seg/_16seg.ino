/*
  Drive the 16 segment led displays
 */

#define OE      8
#define STROBE  9
#define CLOCK   10
#define DATA    11

#include <SPI.h>
#include <avr/pgmspace.h>

/*

with the outputs at the top, fron left to right:

pin    output bit (zero indexed!)
1          3
2          2
3          1
4          0
5          7
6          6
7          5
8          4
9          11
10         10
11         9
12         8
13         15
14         14
15         13
16         12

*/

void shift(void);

// init the shift registers to all 0's
void shift_clear(void) {
  int i;
  digitalWrite(CLOCK, LOW);  

  digitalWrite(DATA, LOW);
  
  for (i = 0 ; i < 16 ; i++) {
    digitalWrite(CLOCK, HIGH);
//    delayMicroseconds(1);
    digitalWrite(CLOCK, LOW);
  }
}

void shift_bit(byte b) {
  digitalWrite(DATA, b & 1);
  shift();
}

void shift(void) {
  digitalWrite(CLOCK, HIGH);
//  delayMicroseconds(1);
  digitalWrite(CLOCK, LOW);  
}

void send_16(const uint16_t data) {
  int i;
  for (i = 0 ; i < 16 ; i++) {
    shift_bit((data & (1 << i)) >> i);
  }
}

void setup() {                
  int i, j;

  pinMode(OE, OUTPUT); // output enable
  digitalWrite(OE, LOW);  // no output to start with

  // make sure we're not a slave
//  digitalWrite(SS, HIGH);
//  SPI.begin();
//  SPI.setClockDivider(SPI_CLOCK_DIV4); // 16Mhz / 2 = 8Mhz

  // pins for controlling the mic5891 high side driver thats driving the rows
  pinMode(DATA, OUTPUT);

  pinMode(CLOCK, OUTPUT);
  digitalWrite(CLOCK, LOW);   // start clock on low

  pinMode(STROBE, OUTPUT);
  digitalWrite(STROBE, LOW); // don't propergate the register contents

  Serial.begin(9600);
  Serial.println("Hello World!");

//  uint16_t shift_thing = 0b1010101010101010;

//  Serial.println(shift_thing, HEX);
  Serial.println(">");
  
  shift_clear();  
  
  send_16(0xffff);
  
  digitalWrite(STROBE, HIGH); // put the data in the register
  
  digitalWrite(OE, LOW);
  digitalWrite(OE, HIGH); // and now we have an output
  
}


int cycle_counter = 0;

uint16_t state = 0;

void loop() {
  int i;
  int pin = 16;

//  for (i = 0 ; i < 5 ; i++)
//  {
//      SPI.transfer(buffer[i + (5 * row)]);
//  }
//  digitalWrite(OUTPUT, LOW); // switch off output

  pin = Serial.parseInt();

  if (pin == 0) {
     return;
  }

  pin--;

  if (pin > 16) {
      Serial.println("1-16 please");
  } else {
      Serial.print("pin ");
      Serial.println(pin);
      state = state ^ (1 << pin);
      Serial.println(state, HEX);
  }

  delay(250);
  digitalWrite(STROBE, LOW); // no data out (yet)
  send_16(state);
//  send_16(1 << cycle_counter);
//  send_16(0xffff);
  cycle_counter++;
  
  if (cycle_counter == 16) {
      cycle_counter = 0;
  }
  digitalWrite(STROBE, HIGH); // data out
//  delay(250);
//  digitalWrite(STROBE, LOW); // no data out (yet)
//  send_16(0xffff);
//  digitalWrite(STROBE, HIGH); // data out

  
//  digitalWrite(OUTPUT, HIGH); // output off  
}

