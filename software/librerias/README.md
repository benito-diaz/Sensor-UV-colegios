# Librerías

## Librerías estándar

El proyecto **no usa librerías externas**. Todas vienen incluidas en el paquete **esp32 by Espressif Systems** que se instala desde el Boards Manager de Arduino IDE.

## Librerías personalizadas o modificadas

Ninguna.

## Dependencias completas

| Librería / herramienta | Versión | Fuente | Obligatoria |
|------------------------|---------|--------|-------------|
| Paquete esp32 (Espressif) | 3.3.12 | Arduino IDE → Boards Manager | ✅ |
| WiFi | incluida en el paquete esp32 | ESP32 Core | ✅ |
| WiFiClientSecure | incluida en el paquete esp32 | ESP32 Core | ✅ |
| HTTPClient | incluida en el paquete esp32 | ESP32 Core | ✅ |
| Driver CP210x (Windows) | v6.7.6 | silabs.com, "CP210x Windows Drivers" | ✅ si el PC no reconoce el ESP32 |
| App Telegram + bot de @BotFather | — | App Store / Google Play | ✅ para los avisos al celular |
