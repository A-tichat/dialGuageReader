#include "Shahe_DialRead.h"

#define UARTBaudRate 9600
#define INIT_STEPPER 360
#define STEP_INTERVAL 100

#define dirPin 2 // Orange Line CW+
#define stepPin 3 // Yellow Line CLK+

String inputString = "";

bool init_motor = false;
bool running_motor = false;
bool process_done = false;

unsigned short counter_degree = 0;
unsigned long previousMillis = 0;

void get_dial_data();
void motor_one_degree();

void setup() {
  // set ADC prescale to 16 (set ADC clock to 1MHz)
  // this gives as a sampling rate of ~77kSps
  sbi(ADCSRA, ADPS2);
  cbi(ADCSRA, ADPS1);
  cbi(ADCSRA, ADPS0);
  
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  
  Serial.begin(UARTBaudRate);
  Serial.println("..c..");
  inputString.reserve(50);
}

void loop() {
  if (init_motor) {
    if (counter_degree < INIT_STEPPER) {
      motor_one_degree();
      counter_degree++;
    } else {
      init_motor = false;
      running_motor = true;
      counter_degree = 0;
      delay(1000);
    }
  }
  if (running_motor) {
    if (counter_degree < 360) {
      unsigned long currentMillis = millis();
      if ((unsigned long)(currentMillis - previousMillis) >= STEP_INTERVAL) {
        get_dial_data();
        motor_one_degree();
        counter_degree++;
        previousMillis = currentMillis;
      }
    } else {
      init_motor = false;
      running_motor = false;
      process_done = true;
      counter_degree = 0;
    }
  }
  if (process_done & !init_motor & !running_motor) {
    Serial.println("..s..");
    process_done = false; // call only one time
  }
}


void serialEvent() {
  while (Serial.available()) {
    char inChar = (char) Serial.read();
    inputString += inChar;
    
    if (inChar == '\n') { // if string completed
        Serial.print("COMMAND: ");
        if (inputString == "start\n" & !init_motor & !running_motor){
          Serial.println(inputString);
          init_motor = true;
          process_done = false;
        } else if (inputString == "stop\n"){
          Serial.println(inputString);
          init_motor = false;
          running_motor = false;
          process_done = false;
          counter_degree = 0;
        }else {
          Serial.println("invalid!!");  
        }
        inputString="";
    }
  }
}

void get_dial_data(){
    bool is_inch;
    prettyPrintValue(getValue(is_inch), is_inch);
    Serial.println();
}

void motor_one_degree() {
  //Spin the stepper motor 1 revolution slowly:
  for (int i = 0; i < 84; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(100);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(100);
  }
}
