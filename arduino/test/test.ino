#define UARTBaudRate 9600
#define INIT_STEPPER 36
#define STEP_INTERVAL 100

#define dirPin 2 // Orange Line CW+
#define stepPin 3 // Yellow Line CLK+
#define ledPin 13

bool ledStage = false;
String inputString = "";

bool init_motor = false;
bool running_motor = false;
bool process_done = false;

unsigned short counter_degree = 0;
unsigned long previousMillis = 0;
unsigned int gearTeeth = 84;

void get_dial_data(){
  ledStage = !ledStage;
  digitalWrite(ledPin, ledStage);
  Serial.print(random(-100, 100) / 100.0);
  Serial.println();
}

void setup() {
  pinMode(ledPin, OUTPUT);
  
  Serial.begin(UARTBaudRate);
  Serial.println("..c..");
  inputString.reserve(50);
}

void loop() {
  if (init_motor) {
    if (counter_degree < INIT_STEPPER) {
      delay(100);
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
        if (inputString == "start\n" & !init_motor & !running_motor){
          init_motor = true;
          process_done = false;
        } else if (inputString == "stop\n"){
          init_motor = false;
          running_motor = false;
          process_done = true;
          counter_degree = 0;
        } else if (inputString.indexOf("setTeeth") >= 0){
          gearTeeth = inputString.substring(9, inputString.length()-1).toInt();
        }
        inputString="";
    }
  }
}
