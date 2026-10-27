# Código de cada versión de la iteración 2

| Archivo | Versión | Qué cambió respecto a la anterior |
|---------|---------|-----------------------------------|
| `v2.0_semaforo_basico.ino` | v2.0 (14/10) | Primera versión: lectura del sensor, conversión a índice UV y semáforo según la escala OMS. Imprime `mV | UV | nivel` cada 1 s. |
| `v2.1_mensajes.ino` | v2.1 (14/10) | Mensaje de recomendación por nivel cada 15 s (o al cambiar de color). |
| `v2.2_mensajes_y_D32.ino` | v2.2 (18/10) | Pin D32 en 3,3 V para alimentar el sensor en la protoboard (el pin 3V3 quedaba tapado). |
| [`software/src/main.ino`](../../../software/src/main.ino) | v2.3 (18/10) | WiFi + avisos por Telegram en el otro núcleo del ESP32; consulta cada 10 s. Versión actual. |
