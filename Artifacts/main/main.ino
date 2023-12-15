#define BATTERY1_INDICATOR_PIN 15  //A1
//#define BATTERY2_INDICATOR_PIN 16  //A2
#define LDR_PIN 17  //A3

#define MAX_LDR_VOLTAGE 5.0

#define NUM_MEASUREMENT 200
#define MAX_ARDUINO_INPUT_VOLTAGE 4.90531

#define MAX_BATTERY_VOLTAGE 14.656291

#define RUN_INTERVAL 5  // In Minutes


#include <Wire.h>
#include <DS3231.h>

DS3231 clockModule;
RTCDateTime currDate;

float capacity_voltage[] = { 10.0, 10.22, 10.44, 10.67, 10.89, 11.11, 11.33, 11.56, 11.78, 12.0,
                             12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.83, 12.87,
                             12.9, 12.91, 12.92, 12.93, 12.94, 12.95, 12.96, 12.97, 12.98, 12.99,
                             13.0, 13.01, 13.02, 13.03, 13.04, 13.05, 13.06, 13.07, 13.08, 13.09,
                             13.1, 13.11, 13.12, 13.13, 13.14, 13.15, 13.16, 13.17, 13.18, 13.19,
                             13.2, 13.21, 13.22, 13.23, 13.24, 13.25, 13.26, 13.27, 13.28, 13.29,
                             13.3, 13.31, 13.32, 13.33, 13.35, 13.36, 13.37, 13.38, 13.39,
                             13.4, 13.41, 13.43, 13.44, 13.45, 13.46, 13.47, 13.48, 13.49,
                             13.5, 13.51, 13.52, 13.53, 13.54, 13.56, 13.57, 13.59,
                             13.6, 13.64, 13.68, 13.72, 13.76, 13.8, 13.84, 13.88, 13.92, 13.96,
                             14.0, 14.15, 14.3, 14.45, 14.65 };

struct BatteryInfo {
      float chargeLevel;
      float chargeRate;

      float outVoltage;
};

struct WeatherInfo {
      float sensorVoltage;
      float intensity;
};

struct pFIONA {
      int totalRun;
      int currentState;
};
//PFIONA STATE: 0 : Not Running
//              1 : Running
//

BatteryInfo batteryInfo = { 0.0, 0.0, 0.0 };
WeatherInfo weatherInfo = { 0.0, 0.0 };
pFIONA pFiona = { 0, 0 };

void makeDecision() {
      if (pFiona.currentState == 1)
            return;
}
void paramInitReset() {
      pFiona.totalRun = 0;
      pFiona.currentState = 0;
}


void updateVoltageAndChargeLevel() {
      float batteryVoltage = 0;
      float actualVoltage;

      for (int i = 0; i < NUM_MEASUREMENT; i++) {
            batteryVoltage += analogRead(BATTERY1_INDICATOR_PIN);
            delay(3);
      }

      batteryVoltage /= NUM_MEASUREMENT;
      actualVoltage = batteryVoltage * (5.0 / 1023.0);
      actualVoltage = actualVoltage * MAX_ARDUINO_INPUT_VOLTAGE;

      batteryInfo.outVoltage = actualVoltage;
      batteryInfo.chargeLevel = 0;

      for (int i = 0; i < 100; i++) {
            if (capacity_voltage[i] < actualVoltage)
                  batteryInfo.chargeLevel = i;
            else
                  break;
      }
      if (actualVoltage >= capacity_voltage[100])
            batteryInfo.chargeLevel = 100;
}
void updateBatteryStatus() {
      float prevVoltage = batteryInfo.outVoltage;
      updateVoltageAndChargeLevel();

      if (prevVoltage >= batteryInfo.outVoltage) {
            batteryInfo.chargeRate = 0.0;
      } else {
            float idealTime = 0.0;
            float diff = 0.0;
            if (prevVoltage < 12.6 && batteryInfo.outVoltage >= 10.0) {
                  diff = batteryInfo.outVoltage;
                  if (batteryInfo.outVoltage >= 12.6)
                        diff = 12.6;
                  diff = diff - prevVoltage;
                  idealTime += (25 * diff) / 2.6;
                  prevVoltage = 12.6;
            }
            if (12.6 <= prevVoltage && prevVoltage < 13.5 && batteryInfo.outVoltage >= 12.6) {
                  diff = batteryInfo.outVoltage;
                  if (batteryInfo.outVoltage >= 13.5)
                        diff = 13.5;

                  diff = diff - prevVoltage;
                  idealTime += (5 * diff) / 0.9;
                  prevVoltage = 13.5;
            }
            if (13.5 <= prevVoltage && prevVoltage < 14.0 && batteryInfo.outVoltage >= 13.5) {
                  diff = batteryInfo.outVoltage;
                  if (batteryInfo.outVoltage >= 14.0)
                        diff = 14.0;

                  diff = diff - prevVoltage;
                  idealTime += (90 * diff) / 0.5;
                  prevVoltage = 14.0;
            }
            if (14.0 <= prevVoltage && prevVoltage < 14.5 && batteryInfo.outVoltage >= 14.0) {
                  diff = batteryInfo.outVoltage;
                  if (batteryInfo.outVoltage >= 14.5)
                        diff = 14.5;

                  diff = diff - prevVoltage;
                  idealTime += (20 * diff) / 0.5;
                  prevVoltage = 14.5;
            }
            if (14.5 <= prevVoltage && batteryInfo.outVoltage >= 14.5) {
                  diff = batteryInfo.outVoltage - prevVoltage;
                  idealTime += (15 * diff) / 0.15;
            }
            batteryInfo.chargeRate = (idealTime / RUN_INTERVAL) * 100;
            //Serial.print("\n\t\tIDEAL TIME:");
            //Serial.println(idealTime);
      }
}
void updateWeatherInfo() {
      float ldrVoltage = 0.0;

      for (int i = 0; i < NUM_MEASUREMENT; i++) {
            ldrVoltage += analogRead(LDR_PIN);
            delay(3);
      }
      ldrVoltage = ldrVoltage / NUM_MEASUREMENT;
      weatherInfo.sensorVoltage = (ldrVoltage / 1023.0) * MAX_LDR_VOLTAGE;
      weatherInfo.intensity = (weatherInfo.sensorVoltage / MAX_LDR_VOLTAGE) * 100;
}
void updateDate() {
      RTCDateTime prevDate = currDate;
      currDate = clockModule.getDateTime();
      if (prevDate.day != currDate.day) {
            paramInitReset();
      }
}
void logWeathterInfo() {
      Serial.print("LDR_VOLTAGE:");
      Serial.print(weatherInfo.sensorVoltage);
      Serial.print("\tIntensity:");
      Serial.print(weatherInfo.intensity);
}
void logBatteryStatus() {
      Serial.print("Average_Voltage:");
      Serial.print(batteryInfo.outVoltage);
      Serial.print("\tCharge_Level:");
      Serial.print(batteryInfo.chargeLevel / 100);
      Serial.print("\tCharge Rate:");
      Serial.print(batteryInfo.chargeRate);
}
void log() {
      logBatteryStatus();
      Serial.print("\t");
      logWeathterInfo();
      Serial.println();
}
void setup() {
      Serial.begin(9600);

      clockModule.begin();
      paramInitReset();
      // Uncomment this to set date and time to current time;
      /*
	Wire.beginTransmission(0x68); // address DS3231
      Wire.write(0x0E); // select register
      Wire.write(0b00011100); // write register bitmap, bit 7 is /EOSC
      Wire.endTransmission();

      clockModule.setDateTime(__DATE__, __TIME__);
*/
      currDate = clockModule.getDateTime();
      Serial.print(currDate.year);
      Serial.print("-");
      Serial.print(currDate.month);
      Serial.print("-");
      Serial.print(currDate.day);
      Serial.print(" ");
      Serial.print(currDate.hour);
      Serial.print(":");
      Serial.print(currDate.minute);
      Serial.print(":");
      Serial.print(currDate.second);
      Serial.println("");
      Serial.println("------------");
      //Configuring the Indicators Pins as INPUT
      pinMode(BATTERY1_INDICATOR_PIN, INPUT);
      //pinMode(BATTERY2_INDICATOR_PIN, INPUT);

      pinMode(LDR_PIN, INPUT);
}
void loop() {
      updateDate();
      updateBatteryStatus();
      updateWeatherInfo();
      log();
      delay(5000);
      //delay(RUN_INTERVAL * 60 * 1000);
}
