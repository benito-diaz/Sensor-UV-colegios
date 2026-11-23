# Fuentes del Proyecto

Declaración de librerías, servicios, código externo, modelos 3D de terceros y uso de inteligencia artificial, según la sección 6 de la guía del Avance 3.

\---

## 1\. Librerías y dependencias

### Firmware (ESP32, `software/src/main.ino`)

|Librería|Versión|Uso en el proyecto|Fuente|
|-|-|-|-|
|Arduino core para ESP32 (`WiFi.h`, `WiFiClientSecure.h`, `HTTPClient.h`)|3.3.x (Espressif)|Conexión WiFi, HTTPS a Telegram y al servidor|https://github.com/espressif/arduino-esp32|
|ArduinoJson|7.x|Armar el JSON de cada lectura que se envía al servidor (`enviarLecturaNube`)|https://arduinojson.org · https://github.com/bblanchon/ArduinoJson|
|FreeRTOS (incluido en el core ESP32)|—|Tarea de Internet en el núcleo 0 (`xTaskCreatePinnedToCore`)|https://www.freertos.org|

**Herramientas:** Arduino IDE 2.3.10 · driver CP210x de Silicon Labs (v6.7.6).

### Servidor y panel web (`software/servidor/`)

|Librería|Versión|Uso en el proyecto|Fuente|
|-|-|-|-|
|Node.js|≥ 18|Entorno del servidor|https://nodejs.org|
|Express|^4.21.0|API HTTP y entrega de la página web|https://expressjs.com|
|pg (node-postgres)|^8.13.0|Conexión a PostgreSQL con SSL|https://node-postgres.com|
|dotenv|^16.4.5|Leer variables de entorno en local|https://github.com/motdotla/dotenv|
|Chart.js|4.4.1 (CDN jsDelivr)|Gráfico histórico y gráfico de máximos diarios del panel|https://www.chartjs.org|

\---

## 2\. Servicios externos

|Servicio|Uso|Documentación|
|-|-|-|
|Railway (plan Trial)|Ejecuta el servidor Express y publica el panel con una URL pública|https://docs.railway.com|
|Aiven for PostgreSQL (plan Free)|Base de datos donde se guardan las lecturas|https://aiven.io/docs/products/postgresql|
|GitHub|Código del servidor (despliegue automático en Railway) y respaldo del proyecto|https://github.com|
|Telegram Bot API|Avisos al celular (`sendMessage`) y comando `/estado` (`getUpdates`)|https://core.telegram.org/bots/api|

\---

## 3\. Código externo adaptado

### Servidor, página y envío desde el ESP32 (`server.js`, `public/index.html`, `enviarLecturaNube` en `main.ino`)

* **Fuente:** *Guía TEI: ESP32 + Aiven + Railway* (TEI201, 2026), entregada por el ayudante del curso, y su repositorio de ejemplo https://github.com/ferjomendez/esp32-railway-demo.
* **Qué se tomó:** estructura del servidor (pool de conexiones con SSL, `crearTabla`, `revisarClave` con `x-api-key`, rutas `/api/salud` y `/api/lecturas`), la página con Chart.js que se refresca cada 5 s y la función de envío con `HTTPClient` + ArduinoJson.
* **Adaptación:**

  * La tabla genérica `lecturas (sensor, valor)` se cambió por `lecturas\_uv (indice\_uv, milivoltios, nivel)`.
  * Se validan rangos físicos del sensor (índice 0–20, 0–3300 mV) antes de guardar.
  * El servidor recibe el nivel ya confirmado por el semáforo (4 lecturas seguidas) o lo calcula con la escala OMS.
  * Rutas nuevas: `/api/ultima`, `/api/historial` (agrupa por tramos para no pasar de \~300 puntos), `/api/resumen` (máximo del día y su hora, minutos en cada nivel, alertas) y `/api/exportar.csv`.
  * La página se rehízo: estado actual con color OMS, recomendación para el colegio, alerta, estadísticas, franjas de color en el gráfico, filtros de tiempo, máximo diario y tabla.
  * El envío a la nube se integró en la tarea de Internet existente (núcleo 0), junto a Telegram, con contadores de envíos OK/fallidos y latencia para el testing.

### Escala del Índice UV y recomendaciones

* **Fuente:** Organización Mundial de la Salud (OMS), *Global Solar UV Index: A Practical Guide* (2002). https://www.who.int/publications/i/item/9241590076
* **Uso:** rangos 0–2, 3–5, 6–7, 8–10, 11+, colores oficiales de la escala (verde, amarillo, naranja, rojo, violeta) y las medidas de protección de cada nivel.
* **Adaptación:** las recomendaciones se tradujeron a decisiones concretas para un colegio (recreo, Educación Física).

### Tabla de calibración del sensor (`TABLA\_MV` en `main.ino`)

* **Fuente:** valores típicos de voltaje por índice UV para módulos GUVA-S12SD, entregados por la IA (ver sección 5). No fueron medidos por el equipo.
* **Adaptación:** interpolación lineal entre valores de la tabla.
* **Pendiente:** verificar comparando con el índice UV publicado por MeteoChile (ver `testing/`).

\---

## 4\. Modelos 3D de terceros

|Modelo|Uso|Fuente|
|-|-|-|
|ESP32 WROOM CP2102 30 pines (`esp32\_Wroom\_CP2102\_USMmicro.step`)|Volumen del ESP32 dentro del gemelo 3D|Modelo de la comunidad GrabCAD (grabcad.com), descargado por el equipo ("esp32-wroom-cp2102-30pins")|
|Módulo LED semáforo (`ModLed.STEP`)|Volumen del semáforo dentro del gemelo 3D|Modelo de la comunidad GrabCAD (grabcad.com), descargado por el equipo ("moduloledsemaforo")|

Los demás componentes (LiPo Rider Pro, batería 603450, panel solar 100 × 80, sensor UV) se modelaron como volúmenes con las medidas de las placas reales (ver `diseno\_3d/README.md`). La carcasa es diseño propio del equipo.

\---

## 5\. Uso de Inteligencia Artificial

**Herramientas:** Claude (Anthropic), en el chat de claude.ai y en Claude Code. Octubre – noviembre de 2026.

### 5.1 Firmware (`software/src/main.ino`)

* **Prompts principales:**

  * "Tengo que hacer el dispositivo que detecte cuánto UV hay y que me ayudes con el código. Tengo un ESP32, un GUVA-S12SD marca Keyes y un mini semáforo V1224."
  * "Me gustaría un mensaje cada 15 segundos (…) con amarillo que se pueda salir pero usando bloqueador, y así con los demás colores."
  * "Quiero conectarme con el celular para que me avise vía WiFi."
  * (Avance 3) Adaptar el código para mandar las lecturas a Railway siguiendo la guía del ayudante, sin perder el semáforo ni Telegram.
* **Qué generó la IA:** lectura y promedio del sensor, conversión a índice UV, suavizado y confirmación de nivel, control del semáforo, conexión WiFi, Telegram y la función `enviarLecturaNube`.
* **Adaptaciones del equipo:** mensajes de cada nivel; conexión directa hembra-hembra tras las fallas en protoboard; alimentación opcional por D32; intervalo de Telegram de 3 s → 10 s y tiempo de espera de 8 s → 15 s por los errores 429, -11 y 502; credenciales reemplazadas por textos de ejemplo.
* **Comprensión:**

  * El sensor entrega un voltaje proporcional al UV; se promedian 64 lecturas y se interpola en la tabla para obtener el índice.
  * El valor se suaviza (30 % nuevo / 70 % historial) y el color cambia solo tras 4 lecturas seguidas del nuevo nivel.
  * D34 pertenece al ADC1, que funciona con WiFi encendido.
  * Internet corre en una tarea del núcleo 0 para que el semáforo nunca se trabe. Cada 10 s se arma un JSON con ArduinoJson y se manda por POST HTTPS con la `x-api-key`; el servidor responde 201 si lo guardó.

### 5.2 Servidor y panel web (`software/servidor/`)

* **Prompt:** "sigue la guía de Railway y Aiven, por ejemplo una alerta o color cuando el índice UV pasa un umbral."
* **Qué generó la IA:** adaptación de `server.js` y `index.html` descrita en la sección 3.
* **Comprensión:** el ESP32 no se conecta directo a la base de datos: el servidor hace de intermediario, revisa la clave y usa consultas parametrizadas (`$1, $2`) para evitar inyección SQL. `/api/resumen` calcula los minutos en cada nivel sumando el tiempo entre lecturas consecutivas (máximo 60 s por tramo, para no contar cortes de conexión) y cuenta una alerta cada vez que el nivel sube a ALTO o más.

### 5.3 Modelo 3D 

* **Herramienta:** Claude
* **Uso:** generación de los scripts de Python, que personaliza la carcasa del modelo: como persianas que esten a 45°, techo solar a 20°, postes con insertos metálicos.
* **Adaptación del equipo:** se definieron las medidas reales de agujeros de cada placa con regla, los materiales y las correcciones de cada iteración (quitar la peineta, mover la traba, quitar el tubo de cables, pasos del techo a 4 mm).

### 5.4 Esquemático y documentación

* **Uso:** Dibujo del esquemático con el sistema solar; protocolo de pruebas y estructura de esta declaración.
* **Revisión del equipo:** medidas, materiales y conexiones revisadas contra el prototipo real.

