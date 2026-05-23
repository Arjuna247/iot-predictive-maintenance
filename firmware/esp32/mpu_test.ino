//usedto connect with databse latest version

// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>
// #include <DHT.h>
// #include <Wire.h>
// #include <MPU6050_light.h>

// // =======================
// // Wi-Fi Settings
// // =======================
// const char* ssid = SECRET_SSID;
// const char* password = SECRET_PASS;

// // Point to physical_node.py proxy (Port 5000)
// const char* serverUrl = "http://" SECRET_SERVER_IP ":" STRINGIFY(SECRET_SERVER_PORT) "/sensor-data";

// // =======================
// // Flask Server
// // =======================
// const char* serverUrl = "http://10.183.110.118:5000/sensor-data";

// // =======================
// // Sensor Pins
// // =======================
// #define DHT_PIN 27
// #define DHT_TYPE DHT22
// #define ACS712_PIN 34          // ADC1 pin
// #define SDA_PIN 33
// #define SCL_PIN 25

// // =======================
// // Objects
// // =======================
// DHT dht(DHT_PIN, DHT_TYPE);
// MPU6050 mpu(Wire);

// // =======================
// // ACS712 parameters (5A)
// // =======================
// const float ADC_REF = 3.3;
// const int ADC_RES = 4095;
// const float ACS_OFFSET = 1.65;     // ESP32 midpoint
// const float ACS_SENS = 0.185;      // 185 mV/A

// void setup() {
//   Serial.begin(115200);
//   delay(1000);

//   // ---------- Wi-Fi ----------
//   WiFi.begin(ssid, password);
//   Serial.print("Connecting to Wi-Fi");

//   unsigned long startAttempt = millis();
//   while (WiFi.status() != WL_CONNECTED &&
//          millis() - startAttempt < 15000) {
//     delay(500);
//     Serial.print(".");
//   }

//   if (WiFi.status() == WL_CONNECTED) {
//     Serial.println("\nWi-Fi connected");
//     Serial.println(WiFi.localIP());
//   } else {
//     Serial.println("\nWi-Fi FAILED");
//   }

//   // ---------- DHT ----------
//   dht.begin();
//   delay(2000);

//   // ---------- MPU6050 ----------
//   Wire.begin(SDA_PIN, SCL_PIN);
//   if (mpu.begin() != 0) {
//     Serial.println("MPU6050 connection failed!");
//   } else {
//     Serial.println("MPU6050 connected. Calibrating...");
//     delay(1000);
//     mpu.calcOffsets();
//     Serial.println("MPU6050 calibration complete!");
//   }

//   // ---------- ADC ----------
//   analogReadResolution(12);
//   analogSetPinAttenuation(ACS712_PIN, ADC_11db);
// }

// void loop() {
//   mpu.update();   // MUST be continuous

//   if (WiFi.status() == WL_CONNECTED) {

//     // ---------- Read DHT ----------
//     float temperature = dht.readTemperature();
//     float humidity = dht.readHumidity();
//     if (isnan(temperature) || isnan(humidity)) {
//       Serial.println("DHT read failed. Skipping send.");
//       delay(2000);
//       return;   // stop this loop iteration
//     }
//     // ---------- Read MPU ----------
//     float accelX = mpu.getAccX();
//     float accelY = mpu.getAccY();
//     float accelZ = mpu.getAccZ();

//     // ---------- Read ACS712 ----------
//     int raw = analogRead(ACS712_PIN);
//     float voltage = (raw * ADC_REF) / ADC_RES;
//     float current_amps = abs((voltage - ACS_OFFSET) / ACS_SENS);

//     // ---------- JSON ----------
//     StaticJsonDocument<256> doc;
//     doc["device_id"] = "ESP32_01";
//     doc["temperature"] = temperature;
//     doc["humidity"] = humidity;
//     doc["ax"] = accelX;
//     doc["ay"] = accelY;
//     doc["az"] = accelZ;
//     doc["current_voltage"] = current_amps;

//     String payload;
//     serializeJson(doc, payload);

//     // ---------- HTTP POST ----------
//     HTTPClient http;
//     http.begin(serverUrl);
//     http.addHeader("Content-Type", "application/json");
//     int code = http.POST(payload);

//     if (code > 0) {
//       Serial.printf("POST OK: %d\n", code);
//     } else {
//       Serial.printf("POST Error: %s\n",
//                     http.errorToString(code).c_str());
//     }
//     http.end();

//   } else {
//     Serial.println("Wi-Fi disconnected. Reconnecting...");
//     WiFi.reconnect();
//   }

//   delay(1000);
// }


// connects to sensor and collect only the readings



// #include <Wire.h>
// #include <I2Cdev.h>
// #include <MPU6050.h>
// #include <DHT.h>
// #include <WiFi.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>
  

// // -------- PIN DEFINITIONS --------
// #define DHT_PIN     27
// #define DHT_TYPE    DHT22

// #define ACS_PIN     34      // ADC input only

// #define I2C_SDA     33
// #define I2C_SCL     25
// // -------- SERVER CONFIG --------
//nst char* ssid = SECRET_SSID;
//nst char* password = SECRET_PASS;

// Point to physical_node.py proxy (Port 5000)
//nst char* serverUrl = "http://" SECRET_SERVER_IP ":" STRINGIFY(SECRET_SERVER_PORT) "/sensor-data";
// // ---------- OBJECTS ----------
// MPU6050 mpu;                // Jeff Rowberg style
// DHT dht(DHT_PIN, DHT_TYPE);

// // ---------- ACS712 CONFIG ----------
// const float ADC_REF = 3.3;
// const int ADC_RES  = 4095;

// // ---------- TIMING ----------
// unsigned long lastReadTime = 0;
// const unsigned long interval = 2000;
// void sendToServer(float t,float h,float ax,float ay,float az,float voltage){
//   if(WiFi.status()==WL_CONNECTED){
//     HTTPClient http;
//     http.begin(serverUrl);
//     http.addHeader("Content-Type", "application/json");
//         StaticJsonDocument<256> doc;
//     doc["device_id"] = "ESP32_01";
//     doc["temperature"] = t;
//     doc["humidity"] = h;
//     doc["ax"] = ax;
//     doc["ay"] = ay;
//     doc["az"] = az;
//     doc["current_voltage"] = voltage;
//     doc["timestamp"] = millis();

//     String payload;
//     serializeJson(doc, payload);

//     int httpResponseCode = http.POST(payload);

//     Serial.print("POST response: ");
//     Serial.println(httpResponseCode);

//     http.end();
//   } else {
//     Serial.println("WiFi not connected");
//   }

//   }


// void setup() {
//   Serial.begin(115200);
//   delay(1000);

//   Serial.println("\n=== SENSOR TEST (Jeff Rowberg MPU6050) ===");

//   // ---- I2C ----
//  WiFi.begin(ssid, password);
//   Serial.print("Connecting to WiFi");

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }

//   Serial.println("\nWiFi connected");
//   Serial.print("ESP32 IP: ");
//   Serial.println(WiFi.localIP());

//   // ---- I2C ----
//   Wire.begin(I2C_SDA, I2C_SCL);
//   // ---- MPU6050 ----
//   mpu.initialize();
//   if (!mpu.testConnection()) {
//     Serial.println("ERROR: MPU6050 not connected");
//     while (1);
//   }
//   Serial.println("MPU6050 connected");

//   // ---- DHT22 ----
//   dht.begin();
//   Serial.println("DHT22 initialized");

//   // ---- ADC ----
//   analogReadResolution(12);
//   Serial.println("ADC ready");

//   Serial.println("System ready\n");
// }

// void loop() {
//   if (millis() - lastReadTime >= interval) {
//     lastReadTime = millis();

//     // ===== DHT22 =====
//     float t = dht.readTemperature();
//     float h = dht.readHumidity();

//     if (!isnan(t) && !isnan(h)) {
//       Serial.print("[DHT22] T: ");
//       Serial.print(t);
//       Serial.print(" °C  H: ");
//       Serial.print(h);
//       Serial.println(" %");
//     } else {
//       Serial.println("[DHT22] Read failed");
//     }

//     // ===== MPU6050 =====
//     int16_t ax, ay, az;
//     mpu.getAcceleration(&ax, &ay, &az);

//     Serial.print("[MPU6050] AX: ");
//     Serial.print(ax / 16384.0, 3);
//     Serial.print(" AY: ");
//     Serial.print(ay / 16384.0, 3);
//     Serial.print(" AZ: ");
//     Serial.println(az / 16384.0, 3);

//     // ===== ACS712 =====
//     int raw = analogRead(ACS_PIN);
//     float voltage = (raw * ADC_REF) / ADC_RES;

//     Serial.print("[ACS712] Raw: ");
//     Serial.print(raw);
//     Serial.print(" Vout: ");
//     Serial.print(voltage, 3);
//     Serial.println(" V");

//     Serial.println("----------------------------------");
//   }
// }

// usedto connect with databse latest version with abnormal mode

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <MPU6050_light.h>
#include "secrets.h"

// =======================
// Settings from secrets.h
// =======================
const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;

// Point to physical_node.py proxy (Port 5000)
const char* serverUrl = "http://" SECRET_SERVER_IP ":" STRINGIFY(SECRET_SERVER_PORT) "/sensor-data";

// =======================
// Sensor Pins
// =======================
#define DHT_PIN 27
#define DHT_TYPE DHT22
#define ACS712_PIN 34          // ADC1 pin
#define SDA_PIN 33
#define SCL_PIN 25

// =======================
// Objects
// =======================
DHT dht(DHT_PIN, DHT_TYPE);
MPU6050 mpu(Wire);

// =======================
// Demo Control
// =======================
bool abnormalMode = false;

// =======================
// ACS712 parameters (5A)
// =======================
const float ADC_REF = 3.3;
const int ADC_RES = 4095;
const float ACS_OFFSET = 1.65;     // ESP32 midpoint
const float ACS_SENS = 0.185;      // 185 mV/A

void setup() {
  Serial.begin(115200);
  delay(1000);

  // ---------- Wi-Fi ----------
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");

  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - startAttempt < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connected");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWi-Fi FAILED");
  }

  // ---------- DHT ----------
  dht.begin();
  delay(1000);

  // ---------- MPU6050 ----------
  Wire.begin(SDA_PIN, SCL_PIN);
  if (mpu.begin() != 0) {
    Serial.println("MPU6050 connection failed!");
  } else {
    Serial.println("MPU6050 connected. Calibrating...");
    delay(1000);
    mpu.calcOffsets();
    Serial.println("MPU6050 calibration complete!");
  }

  // ---------- ADC ----------
  analogReadResolution(12);
  analogSetPinAttenuation(ACS712_PIN, ADC_11db);
}

void loop() {
  // =======================
  // Serial command control
  // =======================
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == 'a') {
      abnormalMode = true;
      //Serial.println("⚠️ Abnormal demo mode ACTIVATED");
    }

    if (cmd == 'n') {
      abnormalMode = false;
      //Serial.println("✅ Normal sensor mode ACTIVATED");
    }
  }
  mpu.update();   // MUST be continuous

  if (WiFi.status() == WL_CONNECTED) {

    // ---------- Read DHT ----------
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("DHT read failed. Skipping send.");
      delay(2000);
      return;   // stop this loop iteration
    }
    // ---------- Read MPU ----------
    float accelX = mpu.getAccX();
    float accelY = mpu.getAccY();
    float accelZ = mpu.getAccZ();

    // ---------- Read ACS712 ----------
    int raw = analogRead(ACS712_PIN);
    float voltage = (raw * ADC_REF) / ADC_RES;
    float current_amps = abs((voltage - ACS_OFFSET) / ACS_SENS);

    // ---------- JSON ----------
StaticJsonDocument<256> doc;
    doc["device_id"] = "ESP32_01";

    if (abnormalMode) {

      // Demo abnormal values
      doc["temperature"] = 95;
      doc["humidity"] = 10;
      doc["ax"] = 3.5;
      doc["ay"] = 3.0;
      doc["az"] = 4.0;
      doc["current_voltage"] = 10;

    } else {

      // Real sensor values
      doc["temperature"] = temperature;
      doc["humidity"] = humidity;
      doc["ax"] = accelX;
      doc["ay"] = accelY;
      doc["az"] = accelZ;
      doc["current_voltage"] = current_amps;
    }

    String payload;
    serializeJson(doc, payload);

    // ---------- HTTP POST ----------
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(payload);

    if (code > 0) {
      Serial.printf("POST OK: %d\n", code);
    } else {
      Serial.printf("POST Error: %s\n",
                    http.errorToString(code).c_str());
    }
    http.end();

  } else {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    //WiFi.reconnect();
    if (WiFi.status() != WL_CONNECTED) {
  Serial.println("Reconnecting Wi-Fi...");
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  delay(5000);
}
  }

  delay(2000);
}
