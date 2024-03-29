// pins - voltage on outputs are ~1.5V so we use the ADC
#define DataPin A0 // Blue Line
#define ClkPin  A1 // Red Line

// Dial Indicator resolution: 100 - 0.01mm, 1000 - 0.001mm
//#define Resolution 100
#define Resolution 100

// ADC threshold, ADC values greater than this are interpreted as logical 1, see loop()
#define ADC_Threshold 140

// data format
#define DATA_BITS_LEN 24
#define INCH_BIT 23
#define SIGN_BIT 20
#define START_BIT -1 // -1 - no start bit

// data capture and decode functions
bool getRawBit() {
    bool data;
    while (analogRead(ClkPin) > ADC_Threshold)
        ;
    while (analogRead(ClkPin) < ADC_Threshold)
        ;
    data = analogRead(DataPin) > ADC_Threshold;
    return data;
}

long getRawData() {
    long out = 0;
    for (int i = 0; i < DATA_BITS_LEN; i++) {
        out |= getRawBit() ? 1L << DATA_BITS_LEN : 0L;
        out >>= 1;
    }
    return out;
}

long getValue(bool &inch) {
    long out = getRawData();
    inch = out & (1L << INCH_BIT);
    bool sign = out & (1L << SIGN_BIT);
    out &= (1L << SIGN_BIT) - 1L;
    out >>= (START_BIT+1);
    if (sign)
        out = -out;
    return out;
}

// printing functions
void printBits(long v) {
    char buf[DATA_BITS_LEN + 1];
    for (int i = DATA_BITS_LEN - 1; i >= 0; i--) {
        buf[i] = v & 1 ? '1' : '0';
        v >>= 1;
    }
    buf[DATA_BITS_LEN] = 0;
    Serial.print(buf);
}

int Iabs(int v) { return v<0 ? -v : v; }
int _abs(int v) {
     if (v == INT16_MIN)
        return INT16_MAX;
     else
        return v<0 ? -v : v;
}

void prettyPrintValue(long value, bool inch) {
    double v = value;
#if Resolution == 100
    if (inch) {
        Serial.print(v / 2000, 4);
        //Serial.print(" in");
    } else {
        Serial.print(v / 100, 2);
        //Serial.print(" mm");
    }
#else
    if (inch) {
        if (v < 0){
          Serial.print("Z");
          Serial.print(" 0");
          Serial.print(-(v / 20000), 5);
          //Serial.print(" in");
        }
        else if (v >= 0){ 
          Serial.print("Y");
          Serial.print(" 0");
          Serial.print(v / 20000, 5);
          //Serial.print(" in");
        }
    }
    else {
        if (v < 0){
          Serial.print("XXZ");
          Serial.print(" 0");
          Serial.print(-(v / 1000), 3); 
          //
          Serial.print(" mm");
        }
        if ((v >= 0)&&(v < 10000)){ 
          Serial.print("XXY");
          Serial.print(" 0");
          Serial.print(v / 1000, 3);
          //
          Serial.print(" mm");
        }
        if (v >= 10000){ 
          Serial.print("XXY");
          Serial.print(" ");
          Serial.print(v / 1000, 3);
          //
          Serial.print(" mm");
        }
    }
#endif
}

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
