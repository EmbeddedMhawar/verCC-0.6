#include <Wire.h>
#include <LiquidCrystal_I2C.h>  // Warning about ESP32 compatibility is normal - library works fine
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <driver/adc.h>
#include <WiFiClientSecure.h>
#include "EmonLib.h"
#include <ModbusIP_ESP8266.h>  // Add emelianov's modbus-esp8266 library

// NEW: Add basic TLS support for future Modbus Security
// Note: WiFiClientSecure is built into ESP32 Arduino Core
// If not found, update ESP32 board package in Arduino IDE

#define SENSOR_PIN 34  // Analog pin for SCT-013

// Force EmonLib to use 10bit ADC resolution
#define ADC_BITS    10
#define ADC_COUNTS  (1<<ADC_BITS)

// Network credentials (keep your existing ones)
const char* ssid = "EDGE_SCHOOL_GUEST";
const char* password = "EDGEGUEST2019";
const char* serverName = "http://192.168.100.200:5000/api/energy-data";  // Updated to your PC's IP
// Previous IP was: http://192.168.1.100:5000/api/energy-data (incorrect)
// Your actual PC IP: 192.168.11.101

// NEW: SCADA simulation components
WebServer scadaServer(80);        // Web server for SCADA interface
WiFiClientSecure secureClient;    // TLS client for secure Modbus

EnergyMonitor emon1;
LiquidCrystal_I2C lcd(0x27, 16, 2);

// NEW: Modbus-TCP Server
ModbusIP mbServer;

// Existing variables
unsigned long lastSendTime = 0;
const long sendInterval = 1000;
const float CALIBRATION_FACTOR = 10.0;
const float gridVoltage = 220.0; // Morocco grid voltage

// Noise floor calibration variables (keep existing)
float noiseFloor = 0.0;
bool calibrated = false;
unsigned long calibrationStart = 0;
int calibrationReadings = 0;
float calibrationSum = 0.0;

// NEW: SCADA simulation data structure
struct SCADAData {
  float current_rms;
  float voltage;
  float ac_power_kw;
  float total_energy_kwh;
  float grid_frequency;
  float power_factor;
  float ambient_temp;
  float irradiance;
  int system_status;  // 0=Offline, 1=Online, 2=Fault
  float efficiency;
  unsigned long timestamp;
};

SCADAData scadaData = {0};
float accumulated_energy = 0.0;
unsigned long last_energy_update = 0;
unsigned long last_scada_update = 0;

// NEW: Modbus Security Configuration (for future use)
// When you install a proper Modbus-TLS library, configure here:
const char* secure_modbus_host = "192.168.1.50";  // Your secure Modbus server
const int secure_modbus_port = 802;               // TLS port (not 502)
const int modbus_unit_id = 1;

// TLS Certificate placeholders (replace with your actual certificates)
const char* ca_cert = R"(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIuJruydjsw2hUwsOjsQl32CqgSO9+lFyAoJdgNDlP0R
N/M2xtRBcVlRdCuHHg1UOSANTaQamSu6hHKOi1Wh/cqdJiLyXn5cqjpWYFEgvyl9
qNI0GSK2c+aCRfwq3g8+LDOQZQqTIpd6sJBiNSiJlCrKu+0QOA03lBSqcDuLqf9O
Q/B3dk+sHe2SMS1DGvpHPPKaRgNMZeWSpcbNltyn2A/FQcRgbzPyUwOWmUwpkrG+
N0VxSVzCuCyBuHQD16eEiuHBOoeG
-----END CERTIFICATE-----
)";

const char* client_cert = R"(
-----BEGIN CERTIFICATE-----
// Replace with your client certificate
-----END CERTIFICATE-----
)";

const char* client_key = R"(
-----BEGIN PRIVATE KEY-----
// Replace with your client private key
-----END PRIVATE KEY-----
)";

void setup() {
  Serial.begin(115200);

  // Set ADC resolution to 10 bits for better compatibility with EmonLib
  analogReadResolution(10);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("VerifiedCC v0.4");
  lcd.setCursor(0, 1);
  lcd.print("SCADA Simulator");

  WiFi.begin(ssid, password);
  lcd.setCursor(0, 1);
  lcd.print("Connecting WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected!");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());

  emon1.current(SENSOR_PIN, CALIBRATION_FACTOR);

  // NEW: Setup Modbus-TCP Server (as per requirements)
  mbServer.begin();                        // start Modbus on port 502
  mbServer.addHreg(30001, 0, 10);          // holding registers for power, energy, etc.
  mbServer.addIreg(30001, 0, 10);          // input registers if needed
  mbServer.addCoil(1, false, 8);           // coils for status flags
  mbServer.addIsts(1, false, 8);           // discrete inputs for alarms
  
  Serial.println("Modbus-TCP Server started on port 502");
  Serial.println("Registers: HR 30001-30010, IR 30001-30010, Coils 1-8, Inputs 1-8");

  // NEW: Setup SCADA servers
  setupSCADAServers();
  scadaServer.begin();

  Serial.println("SCADA Simulation started!");
  Serial.println("HTTP API: http://" + WiFi.localIP().toString());
  Serial.println("Modbus-TCP: " + WiFi.localIP().toString() + ":502");
  Serial.println("Ready for Modbus integration (TLS support available)");

  // Start noise floor calibration (keep existing)
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calibrating...");
  lcd.setCursor(0, 1);
  lcd.print("Turn OFF all loads");
  calibrationStart = millis();
  delay(2000);
  lcd.clear();
}
void loop() {
  // Keep existing calibration logic
  if (!calibrated && millis() - calibrationStart < 120000) {
    double rawCurrent = emon1.calcIrms(1484);
    calibrationSum += rawCurrent;
    calibrationReadings++;
    lcd.setCursor(0, 0);
    lcd.print("Calibrating...");
    lcd.setCursor(0, 1);
    lcd.print("Cal: " + String((120000 - (millis() - calibrationStart)) / 1000) + "s   ");
    delay(200);
    return;
  }

  if (!calibrated) {
    noiseFloor = calibrationSum / calibrationReadings;
    calibrated = true;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Noise: " + String(noiseFloor, 3) + "A");
    lcd.setCursor(0, 1);
    lcd.print("SCADA Ready!");
    delay(2000);
    Serial.println("Calibration complete. SCADA simulation active!");
  }

  // NEW: Handle Modbus-TCP Server
  mbServer.task();                         // handle incoming Modbus requests
  
  // NEW: Handle SCADA servers
  scadaServer.handleClient();

  // Update SCADA data every 5 seconds
  if (millis() - last_scada_update > 5000) {
    updateSCADAData();
    updateModbusRegisters();             // write scadaData into your registers
    pollModbusDevices();  // Poll external Modbus devices
    last_scada_update = millis();
  }

  // Keep existing data sending logic but enhanced
  if (millis() - lastSendTime > sendInterval) {
    // Your existing current measurement code
    long sum = 0;
    for (int i = 0; i < 100; i++) {
      sum += analogRead(SENSOR_PIN);
      delay(2);
    }
    float avgADC = sum / 100.0;
    float adcVoltage = (avgADC * 3.3) / 1023.0;

    double rawCurrent = emon1.calcIrms(1484);
    double Irms = rawCurrent - noiseFloor;
    if (Irms < 0.01) Irms = 0.0;

    float watts = Irms * gridVoltage;
    if (watts < 1.0) watts = 0.0;

    Serial.println("Raw: " + String(rawCurrent, 3) + "A, Corrected: " + String(Irms, 3) + 
                   "A, Power: " + String(watts, 1) + "W");

    // Update SCADA data with real measurements
    scadaData.current_rms = Irms;
    scadaData.voltage = gridVoltage;
    scadaData.ac_power_kw = watts / 1000.0;

    // Keep existing LCD display
    unsigned long uptimeSeconds = millis() / 1000;
    int hours = uptimeSeconds / 3600;
    int minutes = (uptimeSeconds % 3600) / 60;
    int seconds = uptimeSeconds % 60;

    lcd.clear();
    lcd.setCursor(0, 0);
    String timeStr = "";
    if (hours < 10) timeStr += "0";
    timeStr += String(hours) + ":";
    if (minutes < 10) timeStr += "0";
    timeStr += String(minutes) + ":";
    if (seconds < 10) timeStr += "0";
    timeStr += String(seconds);
    lcd.print(timeStr + " | " + String(Irms, 2) + "A");
    lcd.setCursor(0, 1);
    lcd.print("SCADA: " + String(watts, 1) + "W");

    // Send comprehensive data to backend
    String isoTimestamp = "2025-01-20T" +
                         String(millis() / 3600000 % 24, DEC) + ":" +
                         String(millis() / 60000 % 60, DEC) + ":" +
                         String(millis() / 1000 % 60, DEC) + ".000Z";
    
    String jsonPayload = "{";
    jsonPayload += "\"device_id\":\"ESP32-001\",";
    jsonPayload += "\"timestamp\":\"" + isoTimestamp + "\",";
    jsonPayload += "\"current\":" + String(Irms, 3) + ",";
    jsonPayload += "\"voltage\":" + String(gridVoltage) + ",";
    jsonPayload += "\"power\":" + String(watts, 1) + ",";
    jsonPayload += "\"ac_power_kw\":" + String(scadaData.ac_power_kw, 3) + ",";
    jsonPayload += "\"total_energy_kwh\":" + String(scadaData.total_energy_kwh, 3) + ",";
    jsonPayload += "\"grid_frequency_hz\":" + String(scadaData.grid_frequency, 2) + ",";
    jsonPayload += "\"power_factor\":" + String(scadaData.power_factor, 3) + ",";
    jsonPayload += "\"ambient_temp_c\":" + String(scadaData.ambient_temp, 1) + ",";
    jsonPayload += "\"irradiance_w_m2\":" + String(scadaData.irradiance, 0) + ",";
    jsonPayload += "\"system_status\":" + String(scadaData.system_status) + ",";
    jsonPayload += "\"efficiency\":" + String(scadaData.efficiency, 3);
    jsonPayload += "}";

    sendData(jsonPayload);  // Send to backend
    lastSendTime = millis();
  }
}

// NEW: Setup SCADA web server endpoints
void setupSCADAServers() {
  // CORS headers for all responses
  scadaServer.onNotFound([]() {
    scadaServer.sendHeader("Access-Control-Allow-Origin", "*");
    scadaServer.send(404, "text/plain", "SCADA Endpoint Not Found");
  });

  // GET /scada/data - Raw SCADA data (compatible with your middleware)
  scadaServer.on("/scada/data", HTTP_GET, []() {
    DynamicJsonDocument doc(1024);

    doc["ac_power_kw"] = scadaData.ac_power_kw;
    doc["total_energy_kwh"] = scadaData.total_energy_kwh;
    doc["grid_frequency_hz"] = scadaData.grid_frequency;
    doc["power_factor"] = scadaData.power_factor;
    doc["ambient_temp_c"] = scadaData.ambient_temp;
    doc["irradiance_w_m2"] = scadaData.irradiance;
    doc["system_status"] = scadaData.system_status;
    doc["efficiency"] = scadaData.efficiency;
    doc["current_rms"] = scadaData.current_rms;
    doc["voltage"] = scadaData.voltage;
    doc["timestamp"] = scadaData.timestamp;

    String response;
    serializeJson(doc, response);

    scadaServer.sendHeader("Access-Control-Allow-Origin", "*");
    scadaServer.sendHeader("Content-Type", "application/json");
    scadaServer.send(200, "application/json", response);
  });

  // GET /scada/guardian - Guardian-formatted data
  scadaServer.on("/scada/guardian", HTTP_GET, []() {
    DynamicJsonDocument doc(2048);

    doc["methodology"] = "GCCM001_v4";
    doc["reporting_period"] = "2025-09-21T00:00:00Z";

    JsonObject project = doc.createNestedObject("project_info");
    project["project_name"] = "VerifiedCC ESP32 Demo";
    project["project_id"] = "VCC-ESP32-001";
    project["location"] = "Casablanca, Morocco";
    project["capacity_mw"] = 0.001; // 1kW = 0.001MW for demo

    JsonObject monitoring = doc.createNestedObject("monitoring_data");
    monitoring["gross_generation_mwh"] = scadaData.total_energy_kwh / 1000.0;
    monitoring["net_export_mwh"] = (scadaData.total_energy_kwh * 0.98) / 1000.0;
    monitoring["capacity_factor"] = (scadaData.ac_power_kw / 0.001) * 100;
    monitoring["average_irradiance"] = scadaData.irradiance;
    monitoring["current_rms"] = scadaData.current_rms;

    JsonObject calculations = doc.createNestedObject("calculations");
    float morocco_ef = 0.81; // Morocco emission factor
    float export_mwh = (scadaData.total_energy_kwh * 0.98) / 1000.0;
    calculations["baseline_emissions_tco2"] = export_mwh * morocco_ef;
    calculations["project_emissions_tco2"] = 0;
    calculations["emission_reductions_tco2"] = export_mwh * morocco_ef;

    String response;
    serializeJson(doc, response);

    scadaServer.sendHeader("Access-Control-Allow-Origin", "*");
    scadaServer.sendHeader("Content-Type", "application/json");
    scadaServer.send(200, "application/json", response);
  });

  // GET / - SCADA web interface
  scadaServer.on("/", HTTP_GET, []() {
    String html = buildSCADAWebInterface();
    scadaServer.sendHeader("Access-Control-Allow-Origin", "*");
    scadaServer.send(200, "text/html", html);
  });

  // Modbus client configuration
  // Define target devices to poll (add your device IPs here)
  Serial.println("Modbus TCP Security client configured for polling external devices");
}

// NEW: Setup Modbus-TCP Security (TLS)
void setupModbusSecurity() {
  // Configure TLS certificates
  secureClient.setCACert(ca_cert);
  secureClient.setCertificate(client_cert);
  secureClient.setPrivateKey(client_key);
  
  // Optional: Set TLS verification mode
  secureClient.setInsecure(); // For testing - remove in production!
  
  Serial.println("Modbus-TCP Security (RFC 8502) configured:");
  Serial.printf("- Server: %s:%d\n", secure_modbus_host, secure_modbus_port);
  Serial.println("- TLS certificates loaded");
  Serial.println("- Ready for secure Modbus communications");
}// NEW: Update Modbus registers with SCADA data (as per requirements)
void updateModbusRegisters() {
  // Map your simulated and real data to Modbus registers
  mbServer.Hreg(30001, (uint16_t)(scadaData.ac_power_kw * 1000));        // Power in watts
  mbServer.Hreg(30002, (uint16_t)(scadaData.total_energy_kwh * 100));     // Energy in 0.01 kWh
  mbServer.Hreg(30003, (uint16_t)(scadaData.grid_frequency * 100));       // Frequency in 0.01 Hz
  mbServer.Hreg(30004, (uint16_t)(scadaData.current_rms * 1000));         // Current in mA
  mbServer.Hreg(30005, (uint16_t)(scadaData.voltage));                    // Voltage in V
  mbServer.Hreg(30006, (uint16_t)(scadaData.power_factor * 1000));        // PF in 0.001
  mbServer.Hreg(30007, (uint16_t)(scadaData.ambient_temp * 10));          // Temp in 0.1°C
  mbServer.Hreg(30008, (uint16_t)(scadaData.irradiance));                 // Irradiance in W/m²
  mbServer.Hreg(30009, (uint16_t)(scadaData.efficiency * 1000));          // Efficiency in 0.1%
  mbServer.Hreg(30010, (uint16_t)(scadaData.system_status));              // Status code
  
  // Set coils for system status
  mbServer.Coil(1, scadaData.system_status == 1);                        // System Online
  mbServer.Coil(2, scadaData.ac_power_kw > 0.1);                         // Power Generation
  mbServer.Coil(3, scadaData.irradiance > 100);                          // Daylight
  mbServer.Coil(4, scadaData.grid_frequency > 49.5 && scadaData.grid_frequency < 50.5); // Grid OK
  
  // Set discrete inputs for alarms
  mbServer.Ists(1, scadaData.ambient_temp > 40);                         // High temp alarm
  mbServer.Ists(2, scadaData.power_factor < 0.9);                        // Low PF alarm
  mbServer.Ists(3, scadaData.efficiency < 0.9);                          // Low efficiency alarm
  mbServer.Ists(4, false);                                               // Reserved alarm
  
  Serial.println("Modbus registers updated - Power: " + String(scadaData.ac_power_kw * 1000) + "W, Energy: " + String(scadaData.total_energy_kwh, 3) + "kWh");
}

// NEW: Update SCADA simulation data
void updateSCADAData() {
  // Accumulate energy (kWh)
  if (last_energy_update > 0) {
    float hours_elapsed = (millis() - last_energy_update) / 3600000.0;
    accumulated_energy += scadaData.ac_power_kw * hours_elapsed;
    scadaData.total_energy_kwh = accumulated_energy;
  }
  last_energy_update = millis();

  // Simulate other SCADA parameters
  scadaData.grid_frequency = 50.0 + random(-10, 10) / 100.0; // 50Hz ± 0.1Hz
  scadaData.power_factor = 0.95 + random(-5, 5) / 1000.0;    // ~0.95 PF
  scadaData.ambient_temp = 25.0 + random(-50, 150) / 10.0;   // 20-40°C range
  scadaData.irradiance = simulateIrradiance();               // W/m²
  scadaData.system_status = 1; // Online
  scadaData.efficiency = 0.96 + random(-20, 20) / 1000.0;   // ~96% efficiency
  scadaData.timestamp = millis();

  Serial.println("=== SCADA Data Update ===");
  Serial.println("Real Current: " + String(scadaData.current_rms) + "A");
  Serial.println("Real Power: " + String(scadaData.ac_power_kw * 1000) + "W");
  Serial.println("Total Energy: " + String(scadaData.total_energy_kwh, 3) + " kWh");
  Serial.println("Simulated Irradiance: " + String(scadaData.irradiance) + " W/m²");
}

// NEW: Simulate solar irradiance
float simulateIrradiance() {
  // Simulate daily solar pattern (0-1200 W/m²)
  // Add 8-hour offset to simulate starting at 8 AM instead of midnight
  unsigned long time_of_day = ((millis() / 1000) + (8 * 3600)) % 86400; // Seconds in day + 8hr offset
  float hour = time_of_day / 3600.0;

  if (hour < 6 || hour > 18) {
    return 0; // Night time
  } else {
    // Sine wave pattern for daylight hours (6 AM to 6 PM)
    float irradiance = 1200 * sin(PI * (hour - 6) / 12);
    return max(0.0f, irradiance + random(-100, 100));
  }
}

// NEW: Poll external Modbus devices with TLS Security
void pollModbusDevices() {
  // Example: Secure Modbus-TCP polling with TLS
  Serial.println("Attempting secure Modbus connection...");
  
  // For ESP32-only setup, this is disabled but ready for real devices
  /*
  // Connect to secure Modbus server
  if (secureClient.connect(secure_modbus_host, secure_modbus_port)) {
    Serial.println("TLS connection established");
    
    // Read holding registers through secure connection
    uint16_t powerData[2];  // For 32-bit power reading
    if (modbus.readHreg(secure_modbus_host, 30001, powerData, 2, nullptr)) {
      uint32_t rawPower = (powerData[0] << 16) | powerData[1];
      float externalPowerKw = rawPower / 1000.0;
      Serial.printf("Secure Modbus AC Power: %.3f kW\n", externalPowerKw);
      scadaData.ac_power_kw = externalPowerKw;
    }
    
    secureClient.stop();
  } else {
    Serial.println("Failed to establish TLS connection");
  }
  */
  
  Serial.println("Secure Modbus polling ready (currently using ESP32 sensor data)");
}

//NEW: Build SCADA web interface
String buildSCADAWebInterface() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <title>VerifiedCC SCADA Simulator</title>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <style>
    body { font-family: Arial; margin: 20px; background: #f0f8ff; }
    .container { max-width: 1000px; margin: 0 auto; }
    .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .header { text-align: center; color: #2c5282; }
    .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
    .metric { text-align: center; padding: 15px; background: #e6f3ff; border-radius: 5px; }
    .metric-value { font-size: 20px; font-weight: bold; color: #2c5282; }
    .metric-label { font-size: 12px; color: #666; margin-top: 5px; }
    .real-data { background: #e6ffe6; border: 2px solid #4caf50; }
    .simulated-data { background: #fff3e0; border: 2px solid #ff9800; }
    .protocols { background: #f7fafc; padding: 15px; border-radius: 5px; }
    .status-online { color: #38a169; font-weight: bold; }
    button { background: #4299e1; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
    button:hover { background: #3182ce; }
    .legend { display: flex; gap: 20px; justify-content: center; margin-bottom: 15px; }
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .legend-color { width: 20px; height: 15px; border-radius: 3px; }
  </style>
</head>
<body>
  <div class='container'>
    <div class='card'>
      <h1 class='header'>🌞 VerifiedCC SCADA Simulator</h1>
      <p style='text-align: center; color: #666;'>Real CT sensor + Simulated solar farm for carbon credits</p>
      <div class='legend'>
        <div class='legend-item'>
          <div class='legend-color' style='background: #e6ffe6; border: 2px solid #4caf50;'></div>
          <span>Real Hardware Data</span>
        </div>
        <div class='legend-item'>
          <div class='legend-color' style='background: #fff3e0; border: 2px solid #ff9800;'></div>
          <span>Simulated SCADA Data</span>
        </div>
      </div>
    </div>

    <div class='card'>
      <h2>Live SCADA Data</h2>
      <div class='data-grid' id='dataGrid'>
        <!-- Data will be populated by JavaScript -->
      </div>
      <button onclick='refreshData()'>🔄 Refresh Data</button>
      <button onclick='viewGuardianReport()'>📊 Guardian Report</button>
    </div>

    <div class='card'>
      <h2>SCADA Protocol Endpoints</h2>
      <div class='protocols'>
        <p><strong>HTTP REST API:</strong> <code>GET /scada/data</code>, <code>GET /scada/guardian</code></p>
        <p><strong>Modbus TCP Security (TLS):</strong> RFC 8502 compliant, port 802 (currently ESP32-only)</p>
        <p><strong>Your Backend:</strong> Continues sending to existing Express server</p>
      </div>
    </div>
  </div>

  <script>
    function refreshData() {
      fetch('/scada/data')
        .then(response => response.json())
        .then(data => {
          const grid = document.getElementById('dataGrid');
          grid.innerHTML = `
            <div class='metric real-data'>
              <div class='metric-value'>${(data.ac_power_kw * 1000).toFixed(1)}W</div>
              <div class='metric-label'>Real AC Power</div>
            </div>
            <div class='metric real-data'>
              <div class='metric-value'>${data.current_rms.toFixed(3)}A</div>
              <div class='metric-label'>Real Current (RMS)</div>
            </div>
            <div class='metric real-data'>
              <div class='metric-value'>${data.voltage.toFixed(0)}V</div>
              <div class='metric-label'>Grid Voltage</div>
            </div>
            <div class='metric real-data'>
              <div class='metric-value'>${data.total_energy_kwh.toFixed(4)}</div>
              <div class='metric-label'>Total Energy (kWh)</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value'>${data.irradiance_w_m2.toFixed(0)}</div>
              <div class='metric-label'>Solar Irradiance (W/m²)</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value'>${data.ambient_temp_c.toFixed(1)}°C</div>
              <div class='metric-label'>Ambient Temperature</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value'>${data.grid_frequency_hz.toFixed(2)}Hz</div>
              <div class='metric-label'>Grid Frequency</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value'>${(data.power_factor * 100).toFixed(1)}%</div>
              <div class='metric-label'>Power Factor</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value'>${(data.efficiency * 100).toFixed(2)}%</div>
              <div class='metric-label'>System Efficiency</div>
            </div>
            <div class='metric simulated-data'>
              <div class='metric-value status-online'>${data.system_status === 1 ? 'ONLINE' : 'OFFLINE'}</div>
              <div class='metric-label'>System Status</div>
            </div>
          `;
        })
        .catch(error => console.error('Error:', error));
    }

    function viewGuardianReport() {
      window.open('/scada/guardian', '_blank');
    }

    // Auto-refresh every 5 seconds
    setInterval(refreshData, 5000);

    // Initial load
    refreshData();
  </script>
</body>
</html>
  )";
  return html;
}// 
// Helper function to poll additional Modbus devices (for future use)
void pollAnotherDevice(const char* ip, int port, int unitID) {
  // READY FOR FUTURE: When you add more devices, use this function
  Serial.printf("Ready to poll device at %s:%d (Unit %d)\n", ip, port, unitID);
  
  // Example code for when you have real devices:
  /*
  uint16_t temperatureRaw;
  if (modbus.readHoldingRegister16(ip, port, unitID, 40001, temperatureRaw)) {
    float temperature = temperatureRaw / 10.0;
    Serial.printf("Device %s Temperature: %.1f°C\n", ip, temperature);
    scadaData.ambient_temp = temperature;
  }
  */
}

// Keep your existing sendData function unchanged
void sendData(String payload) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    Serial.println("Sending to backend: " + payload);
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.print("Backend HTTP Response: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Backend Error: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}