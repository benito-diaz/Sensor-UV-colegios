# Documentación de Software

## Diagrama de flujo

El diagrama de flujo completo del programa está en [`software/README.md`](../README.md#arquitectura-del-software).

## Funciones principales

**`leerMilivoltios()`**
- **Propósito:** leer el voltaje del sensor UV reduciendo el ruido.
- **Parámetros:** ninguno.
- **Retorna:** `int` – voltaje promedio en milivoltios (64 lecturas).

**`milivoltiosAIndiceUV(int mv)`**
- **Propósito:** convertir el voltaje del sensor a índice UV.
- **Parámetros:** `mv` – voltaje en milivoltios.
- **Retorna:** `float` – índice UV (0 a 11+), interpolando en la tabla `TABLA_MV`.
- **Ejemplo:** `milivoltiosAIndiceUV(142)` → ≈ 0,5 (nivel bajo).

**`indiceANivel(float uv)`**
- **Propósito:** clasificar el índice UV según la escala de la OMS.
- **Retorna:** `Nivel` – `BAJO`, `MODERADO`, `ALTO`, `MUY_ALTO` o `EXTREMO`.

**`actualizarNivel(Nivel nuevo)`**
- **Propósito:** cambiar el nivel solo si el nuevo se confirma en 4 lecturas seguidas, para evitar parpadeos en los límites.

**`enviarTelegram(String chatId, String texto)`**
- **Propósito:** enviar un mensaje al celular mediante la API de Telegram (HTTPS).
- **Retorna:** `bool` – `true` si Telegram respondió con código 200.

**`revisarTelegram()`**
- **Propósito:** leer el último mensaje enviado al bot (`getUpdates`) y responder a `/estado`.

## Variables clave

| Variable | Tipo | Qué guarda |
|----------|------|------------|
| `ultimoMv` | `int` | Último voltaje promedio del sensor (mV) |
| `uvSuavizado` | `float` | Índice UV suavizado que se muestra y se envía |
| `nivelActual` | `Nivel` | Nivel OMS vigente (decide el color del semáforo) |
| `nivelCandidato` / `contadorCandidato` | `Nivel` / `int` | Nivel nuevo que se está confirmando y cuántas lecturas seguidas lleva |
| `primeraLectura` | `bool` | Evita usar el suavizado antes de la primera medición |
| `ultimoUpdateId` | `long` | Último mensaje de Telegram ya respondido (para no responder dos veces) |
| `TABLA_MV[]` | `int[12]` | Voltaje típico del sensor para índice UV 0 a 11 |

`uvSuavizado`, `nivelActual` y `primeraLectura` son `volatile` porque las leen dos tareas a la vez: el `loop` (núcleo 1) y la tarea de Internet (núcleo 0).

## Lógica principal (resumen)

1. Cada 0,5 s se leen 64 muestras del sensor y se promedian → voltaje en mV.
2. El voltaje se convierte a índice UV buscando entre qué valores de `TABLA_MV` está e interpolando.
3. Se suaviza: `uvSuavizado = 0,3 × lectura nueva + 0,7 × valor anterior`.
4. Se clasifica según la OMS y, si el nivel es distinto al actual, se cambia solo después de 4 lecturas seguidas.
5. Se enciende el LED del nivel (con parpadeo en niveles muy alto y extremo).
6. En paralelo, la tarea de Internet envía un aviso por Telegram cada vez que cambia `nivelActual` y cada 10 s revisa si alguien escribió `/estado`.

---

## Manual de instalación

1. Instalar **Arduino IDE 2** desde arduino.cc/en/software.
2. En **File → Preferences**, agregar en *Additional boards manager URLs*:
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
3. En **Tools → Board → Boards Manager**, instalar **esp32 by Espressif Systems**.
4. Conectar el ESP32 por USB. Si en el Administrador de dispositivos aparece *"CP2102 USB to UART Bridge Controller"* con un triángulo amarillo, instalar el driver **CP210x Windows Drivers** de Silicon Labs (`CP210xVCPInstaller_x64.exe`).
5. Seleccionar **ESP32 Dev Module** y el puerto COM nuevo.
6. Crear el bot de Telegram:
   1. En Telegram, abrir **@BotFather** → `/newbot`.
   2. Elegir un nombre (ej. *Medidor UV*) y un usuario terminado en `bot` (ej. `MedidorUV_bot`).
   3. Copiar el **token** que entrega BotFather.
   4. Obtener el **chat ID** escribiendo a **@userinfobot** (responde con `Id: …`) o escribiéndole `/start` al propio bot con el ESP32 conectado.
7. Completar `WIFI_NOMBRE`, `WIFI_CLAVE`, `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `main.ino` y subir el código.

**Hotspot de iPhone:** activar *Ajustes → Compartir internet → Permitir a otros conectarse* y **Maximizar compatibilidad** (el ESP32 solo usa redes de 2,4 GHz). Mantener esa pantalla abierta mientras el ESP32 se conecta.

---

## Manual de operación

### Encendido del sistema
1. Conectar el ESP32 a un cargador USB, power bank o computador. El programa queda guardado en la placa y parte solo.
2. El semáforo hace la prueba **rojo → amarillo → verde**.
3. En unos segundos se conecta al WiFi y llega al celular el mensaje **"Medidor UV conectado."** con el estado actual.

### Operación normal
1. El semáforo muestra el nivel UV en todo momento (ver tabla de colores en el README principal).
2. Cuando el nivel cambia, llega un aviso **"Cambio el nivel de radiacion UV."** al celular.
3. Para consultar en cualquier momento, escribir **`/estado`** al bot (responde en hasta 10 s).
4. Para ver el detalle técnico, abrir el **Serial Monitor** a 115200 baud (mensaje cada 15 s con índice UV y voltaje del sensor).

### Apagado del sistema
1. Desconectar el cable USB. No es necesario detener el programa antes.
2. Antes de mover cables o módulos, desconectar siempre la alimentación.

---

## Troubleshooting

Problemas reales encontrados durante el desarrollo:

**Problema 1: el computador no reconoce el ESP32 (no aparece puerto COM, solo COM1)**
- Causa probable: falta el driver del chip USB CP2102, o el cable USB es solo de carga.
- Solución: instalar el driver CP210x; probar con otro cable USB de datos.

**Problema 2: Arduino muestra "Unknown COM3" en otro computador**
- Causa probable: ese computador no tiene el paquete esp32 instalado o no se eligió la placa.
- Solución: instalar el paquete esp32 y elegir **ESP32 Dev Module** en *Select other board and port*. Si solo se necesita que funcione, no hace falta volver a cargar el código: basta con alimentar el ESP32.

**Problema 3: la carga se queda en `Connecting....`**
- Solución: mantener presionado el botón **BOOT** del ESP32 hasta que empiece a escribir.

**Problema 4: marca índice UV ≈ 4 a oscuras y el semáforo no enciende**
- Causa: falta la conexión a **GND** común (el sensor queda "flotando" y los LEDs no tienen retorno).
- Solución: revisar que el GND del ESP32, del sensor y del semáforo estén conectados entre sí.

**Problema 5: el sensor siempre marca 0 bajo techo**
- Causa: comportamiento normal. Los vidrios bloquean casi todo el UVB y las ampolletas casi no emiten UV.
- Solución: probar al sol, en una ventana abierta o con una linterna UV de 365 nm (no de 395 nm, que el sensor casi no detecta).

**Problema 6: no conecta a WiFi**
- Causa probable: nombre o clave mal escritos, o red de 5 GHz.
- Solución: copiar el nombre exacto de la red; en iPhone activar *Maximizar compatibilidad*. La red de la universidad (con usuario y clave de alumno) no es compatible.

**Problema 7: el Monitor Serie muestra `[Telegram] Error 401`**
- Causa: token incorrecto.
- Solución: copiar el token directamente desde BotFather (no transcribirlo a mano).

**Problema 8: errores `-11`, `429` o `502` de Telegram**
- Causa: Internet lento (-11 = tiempo de espera agotado), demasiadas consultas (429) o servidor de Telegram ocupado (502).
- Solución aplicada: consultar Telegram cada 10 s en vez de cada 3 s y aumentar el tiempo de espera a 15 s. Mantener el celular cerca del dispositivo.
