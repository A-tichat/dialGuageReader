//* Example sketch to control a stepper motor with TB6560 stepper motor driver and Arduino without a library. More info: https://www.makerguides.com */
// Define stepper motor connections and steps per revolution:
#define dirPin 2 // Orange Line CW+
#define stepPin 3 // Yellow Line CLK+
#define stepsPerRevolution 30240 /// 28800 = 200 pulse*8(S3,S4)*18:1 GearHead

void setup() {
  // Declare pins as output:
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  int b = 0;
  int a = 1; 
  Serial.begin(115200);
  Serial.println("Test for myarduino");
do {
{
  // Set the spinning direction clockwise:
  digitalWrite(dirPin,HIGH);
  //Spin the stepper motor 1 revolution slowly:
 for (int i = 0; i < 30240; i++) {
    // These four lines result in 1 step:
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(100);
    digitalWrite(stepPin, LOW); 
    delayMicroseconds(100);
  }
  delay(1000);
}
  b++;
 
}while (b < 2);

do {
  {// Set the spinning direction clockwise:
  digitalWrite(dirPin,HIGH);
  //Spin the stepper motor 1 revolution slowly:
 for (int i = 0; i < 84; i++) {
    // These four lines result in 1 step:
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(100);
    digitalWrite(stepPin, LOW); 
    delayMicroseconds(100);
    Serial.println(a);
 }
  delay(500);
}
a++;
}
while (a < 361);
}

void loop()
{

  }
