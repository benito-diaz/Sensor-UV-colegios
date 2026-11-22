# Software – Documentación

## Contenido

| Carpeta / archivo | Contenido |
|---|---|
| `src/main.ino` | Firmware del ESP32 v3: semáforo + Telegram + envío a la nube |
| `servidor/` | Servidor Express + panel web (se despliega en Railway; base en Aiven) |
| `docs/captura_y_datos.md` | Captura, almacenamiento, dashboard e información generada |
| `docs/capturas/` | Capturas del panel funcionando |
| `librerias/` | Dependencias y versiones |

Versiones anteriores del firmware en [`../iteraciones/iteracion_2/codigo/`](../iteraciones/iteracion_2/codigo/).

---

## Arquitectura

```
                 núcleo 1 (loop)                         núcleo 0 (tareaInternet)
 sensor ─▶ leerMilivoltios() ─▶ milivoltiosAIndiceUV()     ├─ reconectar WiFi (cada 20 s si se cae)
           (64 muestras)         (tabla + interpolación)   ├─ enviarLecturaNube()  cada 10 s ──▶ Railway ─▶ Aiven
                 │                                          ├─ aviso Telegram si cambia el nivel
           suavizado 0,3 ─▶ actualizarNivel() (4 lecturas)  └─ revisarTelegram()    cada 10 s (/estado)
                 │
           mostrarNivel() ─▶ semáforo (fijo / parpadeo)
```

Las variables que comparten los dos núcleos (`uvSuavizado`, `nivelActual`, `ultimoMv`) son `volatile`. Si no hay Internet, el semáforo sigue funcionando.

### Funciones del firmware

| Función | Qué hace |
|---|---|
| `leerMilivoltios()` | Promedia 64 lecturas calibradas del ADC (`analogReadMilliVolts`) |
| `milivoltiosAIndiceUV()` | Interpola el voltaje en `TABLA_MV` (índice 0 a 11; sobre 11 extrapola) |
| `indiceANivel()` | Escala OMS: 0–2, 3–5, 6–7, 8–10, 11+ |
| `actualizarNivel()` | Cambia de nivel solo tras 4 lecturas seguidas (evita parpadeos en los límites) |
| `mostrarNivel()` | Verde, amarillo, rojo fijo, rojo 1 Hz o rojo rápido |
| `enviarLecturaNube()` | POST HTTPS con JSON (ArduinoJson) y `x-api-key`; cuenta envíos OK/fallidos y mide la latencia |
| `telegramGet()`, `enviarTelegram()`, `revisarTelegram()` | Avisos y comando `/estado` |
| `tareaInternet()` | Tarea FreeRTOS del núcleo 0 que maneja WiFi, nube y Telegram |

### Rutas del servidor (`servidor/server.js`)

| Ruta | Uso |
|---|---|
| `GET /api/salud` | Comprueba la conexión con la base |
| `POST /api/lecturas` | Guarda una lectura (requiere `x-api-key`) |
| `GET /api/lecturas?limite=` | Últimas lecturas |
| `GET /api/ultima` | Lectura más reciente y segundos desde que llegó |
| `GET /api/historial?horas=` | Promedio y máximo por tramo para el gráfico |
| `GET /api/resumen` | Máximo del día y su hora, promedio, minutos por nivel, alertas, máximos de 7 días |
| `GET /api/exportar.csv?horas=` | Descarga de datos |

---

## Firmware: instalación

1. **Arduino IDE 2** (https://www.arduino.cc/en/software).
2. **File → Preferences → Additional boards manager URLs:** `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
3. **Tools → Board → Boards Manager:** instalar **esp32 by Espressif Systems**.
4. **Tools → Manage Libraries:** instalar **ArduinoJson** (Benoit Blanchon, v7).
5. Si el PC no muestra un puerto COM nuevo, instalar el driver **CP210x** de Silicon Labs.
6. Abrir `src/main.ino` (aceptar si Arduino pide crear la carpeta `main`), elegir **ESP32 Dev Module** y el puerto, y **Subir**. Si se queda en `Connecting....`, mantener presionado **BOOT**.

### Configuración (bloque `CONFIGURA ESTO`)

```cpp
const char* WIFI_NOMBRE      = "NOMBRE_DE_TU_RED";      // WiFi de 2,4 GHz (no sirve eduroam)
const char* WIFI_CLAVE       = "CLAVE_DE_TU_RED";
const char* TELEGRAM_TOKEN   = "PEGA_AQUI_EL_TOKEN";    // de @BotFather (si se deja así, no usa Telegram)
const char* TELEGRAM_CHAT_ID = "PEGA_AQUI_TU_ID";
const char* SERVER_URL  = "https://TU-APP.up.railway.app/api/lecturas";
const char* API_KEY     = "LA_MISMA_CLAVE_QUE_EN_RAILWAY";
const char* DISPOSITIVO = "uv-colegio-1";
```

> ⚠️ No subir al repositorio la clave del WiFi, el token de Telegram ni la API_KEY.

### Parámetros ajustables

| Constante | Valor | Qué controla |
|---|---|---|
| `PIN_UV` / `PIN_ROJO` / `PIN_AMARILLO` / `PIN_VERDE` | 34 / 25 / 26 / 27 | Pines |
| `MUESTRAS_POR_LECTURA` | 64 | Muestras promediadas por lectura |
| `INTERVALO_LECTURA_MS` | 500 | Cada cuánto se mide |
| `INTERVALO_ENVIO_MS` | 10000 | Cada cuánto se manda a la nube |
| `INTERVALO_MENSAJE_MS` | 15000 | Mensaje en el Monitor Serie |
| `SUAVIZADO` | 0.3 | Peso de la lectura nueva |
| `LECTURAS_PARA_CAMBIO` | 4 | Lecturas seguidas para cambiar de color |
| `TABLA_MV[]` | 12 valores | Voltaje típico para índice UV 0 a 11 |

### Monitor Serie (115200 baud)

```
[WiFi] Conectado a ... IP: 172.20.10.3
[Nube] POST {"dispositivo":"uv-colegio-1","indice_uv":0.52,"milivoltios":142,"nivel":"BAJO"} -> 201 (843 ms) | OK: 12, fallidos: 0
--------------------------------------------------
LUZ VERDE - Radiacion UV baja. Se puede salir a la calle con tranquilidad.
Indice UV: 0.5 (BAJO) | Sensor: 142 mV
```

---

## Servidor y panel web

El servidor vive también en un repositorio aparte (`sensor-uv-web`) porque Railway despliega desde la raíz de un repositorio. Esta carpeta es la copia de respaldo.

1. **Aiven** (https://console.aiven.io): *Create service → PostgreSQL →* plan **Free** (revisar que diga *Monthly price: Free*). Copiar la **Service URI** y el **CA certificate**.
2. **GitHub:** repositorio con el contenido de `servidor/` en la raíz (sin `.env` ni `node_modules`).
3. **Railway** (https://railway.com): *Continue with GitHub → GitHub Repository →* elegir el repositorio.
4. Pestaña **Variables**: `DATABASE_URL` (Service URI), `DB_CA_CERT` (certificado completo), `API_KEY` (clave larga inventada). Presionar **Deploy**.
5. **Settings → Networking → Generate Domain**, puerto **8080**. Activar *Auto deploy*.
6. Comprobar `https://SU-APP.up.railway.app/api/salud` → `{"ok":true,"db":"conectada"}`.

Errores comunes: 401 = `API_KEY` distinta; 400 = JSON mal armado o fuera de rango; 500 = el servidor no llega a la base (revisar logs); -1 = URL mal escrita.

---

## Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| Se queda en "Conectando a WiFi" | Red de 5 GHz o con usuario (eduroam) | Hotspot del celular en 2,4 GHz ("Maximizar compatibilidad" en iPhone) |
| `[Nube] ... -> 401` | API_KEY distinta en el ESP32 y en Railway | Copiar la misma clave, sin espacios |
| `[Nube] ... -> -1` | URL mal escrita o sin `https://` | Copiar la URL de Railway y agregar `/api/lecturas` |
| Telegram error 429 / -11 / 502 | Consultas muy seguidas o red lenta | Ya resuelto: consulta cada 10 s, espera 15 s |
| Índice UV ≈ 4 a oscuras | GND del sensor suelto | Revisar GND |
| UV ≈ 0 bajo techo | Normal: el vidrio bloquea el UV | Probar al aire libre |
