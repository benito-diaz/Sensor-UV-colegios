# Fuentes del Proyecto

## Librerías utilizadas

No se usan librerías externas. Todas las librerías vienen incluidas en el paquete oficial del ESP32 para Arduino.

| Librería | Versión | Fuente |
|----------|---------|--------|
| WiFi.h | incluida en esp32 3.3.x | github.com/espressif/arduino-esp32 |
| WiFiClientSecure.h | incluida en esp32 3.3.x | github.com/espressif/arduino-esp32 |
| HTTPClient.h | incluida en esp32 3.3.x | github.com/espressif/arduino-esp32 |

**Herramientas:** Arduino IDE 2.3.10 · paquete de placas "esp32 by Espressif Systems" 3.3.12 · driver CP210x de Silicon Labs.

## Servicios externos

| Servicio | Uso | Documentación |
|----------|-----|---------------|
| Telegram Bot API | Envío de avisos al celular (`sendMessage`) y lectura de comandos (`getUpdates`) | https://core.telegram.org/bots/api |
| @BotFather (Telegram) | Creación del bot y obtención del token | https://core.telegram.org/bots#how-do-i-create-a-bot |

## Referencias técnicas

### Escala de colores del Índice UV (main.ino, líneas 17-22 y 135-142)
- Fuente: Organización Mundial de la Salud (OMS), *Global Solar UV Index: A Practical Guide* (2002).
- Uso: rangos 0-2 bajo, 3-5 moderado, 6-7 alto, 8-10 muy alto, 11+ extremo, y las recomendaciones de protección de cada nivel.

### Tabla de calibración del sensor (main.ino, líneas 61-64 y 121-133)
- Fuente: tabla de valores típicos de voltaje de salida por índice UV para el módulo GUVA-S12SD, entregada por la IA (ver Uso de Inteligencia Artificial). No fue medida por el equipo.
- Adaptación: interpolación lineal entre valores de la tabla.
- Pendiente: verificar la tabla comparando con el índice UV publicado por MeteoChile.

## Código externo adaptado

No se copió código de tutoriales externos. El código fue generado con asistencia de IA (ver sección siguiente) usando las librerías oficiales del ESP32.

## Uso de Inteligencia Artificial

**Herramienta:** Claude (Anthropic), octubre 2026.

### Firmware completo (software/src/main.ino)
- **Prompts principales:**
  - "Tengo que hacer el dispositivo que detecte cuánto UV hay y que me ayudes con el código. Tengo un ESP32, un GUVA-S12SD marca Keyes y un mini semáforo V1224."
  - "Me gustaría un mensaje cada 15 segundos, por ejemplo LUZ VERDE: se puede salir a la calle con tranquilidad; con amarillo que se pueda salir pero usando bloqueador, y así con los demás colores."
  - "Quiero conectarme con el celular para que me avise vía WiFi." (iPhone)
- **Qué generó la IA:** lectura y promedio del sensor, conversión de voltaje a índice UV, suavizado y confirmación del cambio de nivel, control del semáforo, mensajes por nivel, conexión WiFi y envío/recepción de mensajes de Telegram.
- **Adaptaciones del equipo:**
  - Se definieron los mensajes de recomendación de cada nivel.
  - Se cambió de protoboard a conexión directa con cables hembra-hembra porque los módulos quedaban frágiles y hubo fallas de conexión a GND.
  - Se alimentó el sensor también desde el pin D32 para poder armarlo en protoboard.
  - Se subió el intervalo de consulta a Telegram de 3 s a 10 s y el tiempo de espera de 8 s a 15 s, por errores 429, -11 y 502 con el hotspot del celular.
  - Se reemplazaron las credenciales (WiFi, token y chat ID) por textos de ejemplo antes de subir el código.
- **Comprensión:**
  - El sensor entrega un voltaje (mV) proporcional a la radiación UV. Se promedian 64 lecturas para reducir el ruido.
  - El voltaje se convierte a índice UV interpolando entre valores de una tabla de calibración.
  - El valor se suaviza (30 % lectura nueva, 70 % historial) y el color solo cambia tras 4 lecturas seguidas del nuevo nivel.
  - Se usa el pin D34 porque pertenece al ADC1, que sigue funcionando con el WiFi encendido.
  - Internet corre en una tarea separada en el otro núcleo del ESP32, para que el semáforo no se trabe. Telegram se consulta cada 10 s (*polling*) porque el ESP32 no puede recibir conexiones desde Internet.

### Diagnóstico y armado
- **Uso:** guía para instalar Arduino IDE, el paquete esp32 y el driver CP210x, armar las conexiones y diagnosticar fallas (lectura de UV 4 a oscuras por falta de GND, semáforo apagado, errores de Telegram).

### Documentación del repositorio
- **Uso:** redacción inicial de los README de `software/`, `hardware/`, `testing/` e `iteraciones/` y del esquema de conexiones, a partir del trabajo realizado por el equipo. Revisado y completado por el equipo.
