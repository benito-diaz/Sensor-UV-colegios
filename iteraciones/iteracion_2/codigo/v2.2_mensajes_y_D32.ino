/*
  Medidor de radiación UV con semáforo
  ------------------------------------
  Placa:    ESP32 (DevKit / "ESP32 Dev Module")
  Sensor:   GUVA-S12SD (módulo Keyes) -> salida analógica
  Salida:   Mini semáforo LED (pines R, Y, G, GND)

  Conexiones (protoboard, módulos con cables hembra-macho):
    Sensor UV   S            -> GPIO 34 (D34)
                VCC          -> GPIO 32 (D32, entrega 3,3 V desde el código)
                GND          -> riel - (GND)
    Semáforo    R            -> GPIO 25
                Y            -> GPIO 26
                G            -> GPIO 27
                GND          -> riel - (GND)
    ESP32       GND          -> riel - (GND)

  Escala de colores (Índice UV de la OMS):
    0 - 2   Bajo        -> VERDE
    3 - 5   Moderado    -> AMARILLO
    6 - 7   Alto        -> ROJO fijo
    8 - 10  Muy alto    -> ROJO parpadeo lento
    11+     Extremo     -> ROJO parpadeo rápido

  Monitor Serie: 115200 baudios. Muestra un mensaje cada 15 s
  o apenas cambia el color del semáforo.
*/

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

const char* MENSAJE_NIVEL[] = {
  "Radiacion UV baja. Se puede salir a la calle con tranquilidad.",
  "Radiacion UV moderada. Se puede salir, pero usando bloqueador solar, gorro y lentes de sol.",
  "Radiacion UV alta. Salir solo si es necesario, buscar sombra y usar bloqueador, gorro, lentes y ropa que cubra la piel.",
  "Radiacion UV muy alta. Evitar salir. Si es indispensable, que sea por poco tiempo y con proteccion completa.",
  "Radiacion UV extrema. NO SE PUEDE SALIR por el alto riesgo para la salud. Permanecer bajo techo."
};

float uvSuavizado = 0;
bool  primeraLectura = true;
Nivel nivelActual = BAJO;
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
