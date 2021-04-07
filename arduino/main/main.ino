#include <pt.h>   // include protothread library
#include "Shahe_DialRead.h"
#include "Step_motor.h"

// UART speed
#define UARTBaudRate 9600

#define LEDPin 13

String inputString = "";
bool stringComplete = false;
bool is_record = false;
bool is_open_motor = false;

static struct pt pt1, pt2; // each protothread needs one of these


static int protothread1(struct pt *pt, int interval) {
  static unsigned long timestamp = 0;
  PT_BEGIN(pt);
  while(1) { // never stop 
    /* each time the function is called the second boolean
    *  argument "millis() - timestamp > interval" is re-evaluated
    *  and if false the function exits after that. */
    PT_WAIT_UNTIL(pt, millis() - timestamp > interval );
    timestamp = millis(); // take a new timestamp
    
    bool is_inch;
    prettyPrintValue(getValue(is_inch), is_inch);
    Serial.println();
  }
  PT_END(pt);
}

void setup() {
  // set ADC prescale to 16 (set ADC clock to 1MHz)
  // this gives as a sampling rate of ~77kSps
  sbi(ADCSRA, ADPS2);
  cbi(ADCSRA, ADPS1);
  cbi(ADCSRA, ADPS0);
  
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
//  pinMode(LEDPin, OUTPUT);
  PT_INIT(&pt1);  // initialise the two
  PT_INIT(&pt2);  // protothread variables

  Serial.begin(UARTBaudRate);
  inputString.reserve(20);
  digitalWrite(LEDPin, LOW);
}

void loop() {
  if (stringComplete) {
    if (inputString == "start\n"){
//      digitalWrite(LEDPin, HIGH);
      is_open_motor = true;
    } else if (inputString == "stop\n"){
//      digitalWrite(LEDPin, LOW);
      is_record = false;
      is_open_motor = false;
    }
    inputString="";
    stringComplete = false;
  }
  if (is_record){
    protothread1(&pt1, 100);
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
