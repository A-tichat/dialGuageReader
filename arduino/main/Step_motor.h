#define dirPin 2 // Orange Line CW+
#define stepPin 3 // Yellow Line CLK+

void run_stepping(int deg = 1) {
  //Spin the stepper motor 1 revolution slowly:
  for (int i = 0; i < deg*84; i++) {
    // These four lines result in 1 step:
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(100);
    digitalWrite(stepPin, LOW); 
    delayMicroseconds(100);
  }
}

void step_recording(){
  // Set the spinning direction clockwise:
  digitalWrite(dirPin,HIGH);
  run_stepping(360);
  delay(1000);
  run_stepping(360);
  is_record = true;

  int j = 0;
  while (is_record){
    if (j < 360){
      //Spin the stepper motor 1 revolution slowly:
      run_stepping(1);
//      delay(100);
      j++;
    } else {
      break;
    }
  }
  is_record = false;
}
