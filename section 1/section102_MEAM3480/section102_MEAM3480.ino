#include <math.h>

#define THERMISTORPIN A0
#define THERMISTORNOMINAL 10000
#define TEMPERATURENOMINAL 25
#define NUMSAMPLES 5
#define BCOEFFICIENT 3950
#define SERIESRESISTOR 10000

const int LEDPIN = 13;
const int Source = 7;
const float UPTHRESHOLD_C = 26.0; 
const float LOTHRESHOLD_C = 24.0; 
  

int samples[NUMSAMPLES];
bool autoMode = true; 

void setup(void) {
  Serial.begin(9600);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, LOW);

  pinMode(PIN7, OUTPUT);
  digitalWrite(PIN7, LOW);

  // You are using external 3.3V on AREF
  analogReference(EXTERNAL);
}



float readTemperatureC() {
  float average = 0;

  for (uint8_t i = 0; i < NUMSAMPLES; i++) {
    samples[i] = analogRead(THERMISTORPIN);
    delay(10);
  }

  for (uint8_t i = 0; i < NUMSAMPLES; i++) average += samples[i];
  average /= NUMSAMPLES;

  // R_therm = R_series / (1023/ADC - 1)
  float resistance = 1023.0 / average - 1.0;
  resistance = SERIESRESISTOR / resistance;

  float steinhart = resistance / THERMISTORNOMINAL;                 // (R/Ro)
  steinhart = log(steinhart);                                       // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                                        // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15);                 // + (1/To)
  steinhart = 1.0 / steinhart;                                      // invert
  steinhart -= 273.15;                                              // K -> C

  Serial.print("ADC avg: "); Serial.print(average);
  Serial.print(" | R(ohm): "); Serial.print(resistance);
  Serial.print(" | T(C): "); Serial.println(steinhart);

  return steinhart;
}

void loop(void) {

  float tempC = readTemperatureC();

 bool ledState = (tempC <= UPTHRESHOLD_C && tempC >= LOTHRESHOLD_C );
  digitalWrite(LEDPIN, ledState ? HIGH : LOW);
 digitalWrite(PIN7, ledState ? HIGH : LOW);   // follow pin13

  Serial.println(ledState ? "AUTO: LED ON, PIN7 ON" : "AUTO: LED OFF, PIN7 OFF");

  delay(500);
}
