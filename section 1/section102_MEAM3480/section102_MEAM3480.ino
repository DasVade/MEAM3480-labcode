#include <math.h>

#define THERMISTORPIN A0
#define THERMISTORNOMINAL 10000
#define TEMPERATURENOMINAL 25
#define NUMSAMPLES 5
#define BCOEFFICIENT 3950
#define SERIESRESISTOR 10000

const int LEDPIN = 13;
const int Source = 7;

const float T_SET = 96.0;
const float HYST  = 0.5;          // +/- 0.5C hysteresis band
const float T_HIGH = T_SET + HYST; // turn OFF above this
const float T_LOW  = T_SET - HYST; // turn ON below this

static bool heaterOn = false;      // normally OFF, remember previous state
  

int samples[NUMSAMPLES];
bool autoMode = true; 

void setup(void) {
  Serial.begin(9600);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, LOW);

  pinMode(Source, OUTPUT);
  digitalWrite(Source, LOW);

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

  // Hysteresis control (bang-bang with memory)
  if (heaterOn && tempC >= T_HIGH) {
    heaterOn = false;              // too hot -> turn off
  } else if (!heaterOn && tempC <= T_LOW) {
    heaterOn = true;               // too cold -> turn on
  }
  // else: keep heaterOn as-is

  digitalWrite(Source, heaterOn ? HIGH : LOW); // pin7 output
  digitalWrite(LEDPIN, heaterOn ? HIGH : LOW); // LED follows heater

  // CSV-friendly logging: time(s), tempC, heater(0/1)
  Serial.print(millis() / 1000.0);
  Serial.print(",");
  Serial.print(tempC);
  Serial.print(",");
  Serial.println(heaterOn ? 1 : 0);

  delay(500);
}
