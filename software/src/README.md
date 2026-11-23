# Código fuente del ESP32

`main.ino` – firmware v3 (Avance 3): semáforo UV + avisos por Telegram + envío de cada lectura al servidor en Railway cada 10 s.

Al abrirlo, Arduino IDE pide crear una carpeta `main` con el archivo adentro: aceptar.

Antes de subirlo a la placa, llenar el bloque `CONFIGURA ESTO` (WiFi, Telegram, `SERVER_URL`, `API_KEY`). En el repositorio esos campos quedan con textos de ejemplo a propósito.

Documentación completa en [`../README.md`](../README.md).
