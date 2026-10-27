/*
  Medidor de radiación UV con semáforo
  ------------------------------------
  Placa:    ESP32 (DevKit / "ESP32 Dev Module")
  Sensor:   GUVA-S12SD (módulo Keyes) -> salida analógica
  Salida:   Mini semáforo LED (pines R, Y, G, GND)

  Conexiones (cables hembra-hembra directo al ESP32):
    Sensor UV   S            -> D34
                VCC          -> 3V3  (o D32, que el código también deja en 3,3 V)
                GND          -> GND
    Semáforo    R            -> D25
                Y            -> D26
                G            -> D27
                GND          -> GND (el otro pin GND)

  Escala de colores (Índice UV de la OMS):
    0 - 2   Bajo        -> VERDE
    3 - 5   Moderado    -> AMARILLO
    6 - 7   Alto        -> ROJO fijo
    8 - 10  Muy alto    -> ROJO parpadeo lento
    11+     Extremo     -> ROJO parpadeo rápido

  Monitor Serie: 115200 baudios. Muestra un mensaje cada 15 s
  o apenas cambia el color del semáforo.

  Celular (Telegram):
    - Avisa cuando el medidor se conecta y cada vez que cambia el nivel UV.
    - Escribe /estado al bot para ver la radiación actual.
    - El semáforo funciona igual aunque no haya WiFi.
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// ================== CONFIGURA ESTO ==================
const char* WIFI_NOMBRE      = "NOMBRE_DE_TU_RED";    // nombre exacto del WiFi o hotspot
const char* WIFI_CLAVE       = "CLAVE_DE_TU_RED";     // contraseña del WiFi
const char* TELEGRAM_TOKEN   = "PEGA_AQUI_EL_TOKEN";  // te lo da @BotFather
const char* TELEGRAM_CHAT_ID = "PEGA_AQUI_TU_ID";     // te lo dice el bot la primera vez
// ====================================================

// ---------------- Pines ----------------
const int PIN_UV       = 34;  // ADC1 (funciona aunque después se use WiFi)
const int PIN_ROJO     = 25;
const int PIN_AMARILLO = 26;
const int PIN_VERDE    = 27;
const int PIN_VCC_SENSOR = 32;  // alimenta el sensor UV con 3,3 V

// Si tu semáforo enciende con LOW en vez de HIGH, cambia esto a true
const bool LOGICA_INVERTIDA = false;

// ---------------- Ajustes ----------------
const int      MUESTRAS_POR_LECTURA = 64;    // promedia ruido del ADC
const uint32_t INTERVALO_LECTURA_MS = 500;   // cada cuánto se mide
const uint32_t INTERVALO_MENSAJE_MS = 15000; // cada cuánto se muestra el mensaje (15 s)
const float    SUAVIZADO            = 0.3;   // 0..1 (más bajo = más suave)
const int      LECTURAS_PARA_CAMBIO = 4;     // lecturas seguidas antes de cambiar color

// Tabla de calibración típica del GUVA-S12SD: voltaje de salida (mV) para cada índice UV.
// Índice:             0    1    2    3    4    5    6    7    8    9    10    11
const int TABLA_MV[] = {50, 227, 318, 408, 503, 606, 696, 795, 881, 976, 1079, 1170};
const int N_TABLA = sizeof(TABLA_MV) / sizeof(TABLA_MV[0]);

// ---------------- Estado ----------------
enum Nivel { BAJO, MODERADO, ALTO, MUY_ALTO, EXTREMO };
const char* NOMBRE_NIVEL[] = {"BAJO", "MODERADO", "ALTO", "MUY ALTO", "EXTREMO"};

const char* COLOR_NIVEL[] = {
  "LUZ VERDE",
  "LUZ AMARILLA",
  "LUZ ROJA",
  "LUZ ROJA PARPADEANDO",
  "LUZ ROJA PARPADEO RAPIDO"
};

// Colores de la escala UV de la OMS para los mensajes del celular
const char* EMOJI_NIVEL[] = {"🟢", "🟡", "🟠", "🔴", "🟣"};

const char* MENSAJE_NIVEL[] = {
  "Radiacion UV baja. Se puede salir a la calle con tranquilidad.",
  "Radiacion UV moderada. Se puede salir, pero usando bloqueador solar, gorro y lentes de sol.",
  "Radiacion UV alta. Salir solo si es necesario, buscar sombra y usar bloqueador, gorro, lentes y ropa que cubra la piel.",
  "Radiacion UV muy alta. Evitar salir. Si es indispensable, que sea por poco tiempo y con proteccion completa.",
  "Radiacion UV extrema. NO SE PUEDE SALIR por el alto riesgo para la salud. Permanecer bajo techo."
};

// Estas variables también las lee la tarea de Internet (por eso "volatile")
volatile float uvSuavizado = 0;
volatile bool  primeraLectura = true;
volatile Nivel nivelActual = BAJO;
Nivel nivelCandidato = BAJO;
int   contadorCandidato = 0;
int   ultimoMv = 0;

uint32_t tUltimaLectura = 0;
uint32_t tUltimoMensaje = 0;
int      nivelMostrado   = -1;  // ultimo nivel informado en pantalla

// ---------------- Funciones ----------------
void escribirLed(int pin, bool encendido) {
  digitalWrite(pin, (encendido != LOGICA_INVERTIDA) ? HIGH : LOW);
}

void luces(bool r, bool y, bool g) {
  escribirLed(PIN_ROJO, r);
  escribirLed(PIN_AMARILLO, y);
  escribirLed(PIN_VERDE, g);
}

int leerMilivoltios() {
  uint32_t suma = 0;
  for (int i = 0; i < MUESTRAS_POR_LECTURA; i++) {
    suma += analogReadMilliVolts(PIN_UV);  // usa la calibración interna del ESP32
    delayMicroseconds(200);
  }
  return suma / MUESTRAS_POR_LECTURA;
}

// Convierte mV a índice UV interpolando en la tabla
float milivoltiosAIndiceUV(int mv) {
  if (mv <= TABLA_MV[0]) return 0.0;
  for (int i = 1; i < N_TABLA; i++) {
    if (mv <= TABLA_MV[i]) {
      float fraccion = (float)(mv - TABLA_MV[i - 1]) / (TABLA_MV[i] - TABLA_MV[i - 1]);
      return (i - 1) + fraccion;
    }
  }
  // Sobre 11: se extrapola con la pendiente del último tramo
  float pendiente = TABLA_MV[N_TABLA - 1] - TABLA_MV[N_TABLA - 2];
  return (N_TABLA - 1) + (mv - TABLA_MV[N_TABLA - 1]) / pendiente;
}

Nivel indiceANivel(float uv) {
  int i = (int)(uv + 0.5);  // redondeo
  if (i <= 2)  return BAJO;
  if (i <= 5)  return MODERADO;
  if (i <= 7)  return ALTO;
  if (i <= 10) return MUY_ALTO;
  return EXTREMO;
}

void actualizarNivel(Nivel nuevo) {
  // Evita parpadeos cuando el valor está justo en un límite
  if (nuevo == nivelActual) {
    contadorCandidato = 0;
    return;
  }
  if (nuevo == nivelCandidato) {
    contadorCandidato++;
  } else {
    nivelCandidato = nuevo;
    contadorCandidato = 1;
  }
  if (contadorCandidato >= LECTURAS_PARA_CAMBIO) {
    nivelActual = nuevo;
    contadorCandidato = 0;
  }
}

void mostrarNivel(uint32_t ahora) {
  switch (nivelActual) {
    case BAJO:     luces(false, false, true);  break;
    case MODERADO: luces(false, true,  false); break;
    case ALTO:     luces(true,  false, false); break;
    case MUY_ALTO: luces((ahora / 500) % 2 == 0, false, false); break;  // 1 Hz
    case EXTREMO:  luces((ahora / 150) % 2 == 0, false, false); break;  // rápido
  }
}

void mostrarMensaje() {
  Serial.println("--------------------------------------------------");
  Serial.printf("%s - %s\n", COLOR_NIVEL[nivelActual], MENSAJE_NIVEL[nivelActual]);
  Serial.printf("Indice UV: %.1f (%s) | Sensor: %d mV\n", uvSuavizado, NOMBRE_NIVEL[nivelActual], ultimoMv);
}

// ---------------- Internet: WiFi + Telegram ----------------
long ultimoUpdateId = 0;  // último mensaje de Telegram ya leído

String urlEncode(const String& texto) {
  const char* hex = "0123456789ABCDEF";
  String salida;
  for (unsigned int i = 0; i < texto.length(); i++) {
    uint8_t c = (uint8_t)texto[i];
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
      salida += (char)c;
    } else {
      salida += '%';
      salida += hex[c >> 4];
      salida += hex[c & 15];
    }
  }
  return salida;
}

// Llama a la API de Telegram. Devuelve true si respondió OK (código 200).
bool telegramGet(const String& metodo, const String& parametros, String* respuesta) {
  if (WiFi.status() != WL_CONNECTED) return false;
  WiFiClientSecure cliente;
  cliente.setInsecure();  // no verifica el certificado (suficiente para el prototipo)
  HTTPClient http;
  http.setTimeout(15000);
  String url = String("https://api.telegram.org/bot") + TELEGRAM_TOKEN + "/" + metodo + "?" + parametros;
  if (!http.begin(cliente, url)) return false;
  int codigo = http.GET();
  if (respuesta != nullptr && codigo > 0) *respuesta = http.getString();
  http.end();
  if (codigo != 200) {
    Serial.printf("[Telegram] Error %d en %s", codigo, metodo.c_str());
    Serial.println(codigo == 401 ? " (revisa el TOKEN)" : codigo == 400 ? " (revisa el CHAT_ID)" : "");
    return false;
  }
  return true;
}

bool enviarTelegram(const String& chatId, const String& texto) {
  return telegramGet("sendMessage", "chat_id=" + chatId + "&text=" + urlEncode(texto), nullptr);
}

String textoEstado() {
  Nivel n = nivelActual;
  String t = String(EMOJI_NIVEL[n]) + " UV " + NOMBRE_NIVEL[n] + " (indice " + String((float)uvSuavizado, 1) + ")\n";
  t += String("Semaforo: ") + COLOR_NIVEL[n] + "\n";
  t += MENSAJE_NIVEL[n];
  return t;
}

bool chatIdConfigurado() {
  return String(TELEGRAM_CHAT_ID).indexOf("PEGA") < 0;
}

// Lee si alguien le escribió al bot y le responde
void revisarTelegram() {
  String r;
  if (!telegramGet("getUpdates", "timeout=0&limit=1&offset=" + String(ultimoUpdateId + 1), &r)) return;

  int p = r.indexOf("\"update_id\":");
  if (p < 0) return;  // no hay mensajes nuevos
  ultimoUpdateId = r.substring(p + 12).toInt();

  int c = r.indexOf("\"chat\":{\"id\":");
  if (c < 0) return;
  String chat = r.substring(c + 13, r.indexOf(',', c + 13));

  int t = r.indexOf("\"text\":\"");
  String texto = (t >= 0) ? r.substring(t + 8, r.indexOf('"', t + 8)) : "";
  texto.toLowerCase();
  Serial.printf("[Telegram] Mensaje del chat %s: %s\n", chat.c_str(), texto.c_str());

  if (chat != String(TELEGRAM_CHAT_ID)) {
    enviarTelegram(chat, String("Tu ID de chat es: ") + chat +
                         "\nCopialo en TELEGRAM_CHAT_ID dentro del codigo y vuelve a subirlo al ESP32.");
    return;
  }
  if (texto.startsWith("/estado") || texto.startsWith("estado")) {
    enviarTelegram(chat, textoEstado());
  } else {
    enviarTelegram(chat, "Hola! Escribe /estado para ver la radiacion UV actual.");
  }
}

// Corre en paralelo al semáforo, así las luces nunca se traban esperando a Internet
void tareaInternet(void* parametro) {
  bool estabaConectado = false;
  int nivelNotificado = -1;
  uint32_t tInicioConexion = millis();
  uint32_t tUltimaRevision = 0;
  uint32_t tUltimoIntentoAviso = 0;

  for (;;) {
    bool conectado = (WiFi.status() == WL_CONNECTED);

    if (conectado && !estabaConectado) {
      Serial.print("[WiFi] Conectado a ");
      Serial.print(WIFI_NOMBRE);
      Serial.print(". IP: ");
      Serial.println(WiFi.localIP());
      if (!chatIdConfigurado()) {
        Serial.println("[Telegram] Falta el CHAT_ID: abre tu bot en Telegram y presiona Iniciar.");
      }
    }
    if (!conectado && estabaConectado) {
      Serial.println("[WiFi] Se perdio la conexion. Reintentando...");
      tInicioConexion = millis();
    }
    estabaConectado = conectado;

    // Si no logra conectarse en 20 s, vuelve a intentar desde cero
    if (!conectado && millis() - tInicioConexion > 20000) {
      Serial.println("[WiFi] No conecta. Revisa nombre y clave del WiFi (debe ser de 2,4 GHz).");
      WiFi.disconnect();
      WiFi.begin(WIFI_NOMBRE, WIFI_CLAVE);
      tInicioConexion = millis();
    }

    if (conectado && !primeraLectura) {
      // Aviso al celular cuando cambia el nivel (o al conectarse por primera vez)
      if (chatIdConfigurado() && (int)nivelActual != nivelNotificado &&
          (tUltimoIntentoAviso == 0 || millis() - tUltimoIntentoAviso > 10000)) {
        tUltimoIntentoAviso = millis();
        int nivelAEnviar = nivelActual;
        String titulo = (nivelNotificado < 0) ? "Medidor UV conectado." : "Cambio el nivel de radiacion UV.";
        if (enviarTelegram(TELEGRAM_CHAT_ID, titulo + "\n" + textoEstado())) {
          nivelNotificado = nivelAEnviar;
          Serial.println("[Telegram] Aviso enviado al celular.");
        }
      }
      // Revisa si le escribieron al bot cada 10 s
      if (millis() - tUltimaRevision >= 10000) {
        tUltimaRevision = millis();
        revisarTelegram();
      }
    }
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

void pruebaInicial() {
  luces(true, false, false);  delay(300);
  luces(false, true, false);  delay(300);
  luces(false, false, true);  delay(300);
  luces(false, false, false);
}

// ---------------- Programa ----------------
void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(PIN_ROJO, OUTPUT);
  pinMode(PIN_AMARILLO, OUTPUT);
  pinMode(PIN_VERDE, OUTPUT);

  pinMode(PIN_VCC_SENSOR, OUTPUT);
  digitalWrite(PIN_VCC_SENSOR, HIGH);  // enciende el sensor
  delay(50);

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);  // rango ~0-3,1 V

  pruebaInicial();
  Serial.println();
  Serial.println("Medidor UV listo. Mensaje cada 15 segundos o al cambiar de color.");

  // WiFi + Telegram en una tarea aparte (núcleo 0)
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_NOMBRE, WIFI_CLAVE);
  Serial.print("[WiFi] Conectando a ");
  Serial.println(WIFI_NOMBRE);
  xTaskCreatePinnedToCore(tareaInternet, "internet", 12288, NULL, 1, NULL, 0);
}

void loop() {
  uint32_t ahora = millis();

  if (ahora - tUltimaLectura >= INTERVALO_LECTURA_MS) {
    tUltimaLectura = ahora;

    ultimoMv = leerMilivoltios();
    float uv = milivoltiosAIndiceUV(ultimoMv);

    if (primeraLectura) {
      uvSuavizado = uv;
      nivelActual = indiceANivel(uv);
      primeraLectura = false;
    } else {
      uvSuavizado = SUAVIZADO * uv + (1 - SUAVIZADO) * uvSuavizado;
    }
    actualizarNivel(indiceANivel(uvSuavizado));
  }

  // Mensaje cada 15 s, o de inmediato si cambia el color
  if (!primeraLectura &&
      ((int)nivelActual != nivelMostrado || ahora - tUltimoMensaje >= INTERVALO_MENSAJE_MS)) {
    tUltimoMensaje = ahora;
    nivelMostrado = nivelActual;
    mostrarMensaje();
  }

  mostrarNivel(ahora);
}
