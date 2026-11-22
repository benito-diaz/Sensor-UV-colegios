# Librerías y versiones

## Firmware (Arduino IDE)

| Librería | Versión | Cómo se instala |
|---|---|---|
| esp32 by Espressif Systems (incluye `WiFi.h`, `WiFiClientSecure.h`, `HTTPClient.h`, FreeRTOS) | 3.3.x | Boards Manager |
| ArduinoJson (Benoit Blanchon) | 7.x | Library Manager |

## Servidor (Node.js ≥ 18)

Definidas en `../servidor/package.json` y fijadas en `package-lock.json`:

| Paquete | Versión |
|---|---|
| express | ^4.21.0 |
| pg | ^8.13.0 |
| dotenv | ^16.4.5 |

Panel web: Chart.js 4.4.1 desde jsDelivr (`https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js`).
