# Hardware – Documentación

## Contenido

| Carpeta | Contenido |
|---------|-----------|
| `esquemas/` | Esquema de conexiones (SVG y PNG) |
| `bom/` | Lista de materiales |
| `fotos/` | Fotos del prototipo |

---

## Componentes principales

1. **ESP32 DevKit (30 pines, chip USB CP2102)** – microcontrolador con WiFi y Bluetooth integrados, 2 núcleos, lógica de 3,3 V y conversor analógico-digital (ADC) de 12 bits. Lee el sensor, controla el semáforo y envía los avisos por WiFi.
2. **Sensor UV GUVA-S12SD (módulo Keyes)** – fotodiodo sensible a la luz ultravioleta (≈240–370 nm, UVA y UVB) con amplificador integrado. Entrega un voltaje analógico proporcional a la radiación (≈0,1 V por punto de índice UV). Pines: S, VCC, GND.
3. **Mini semáforo LED V1224** – módulo con tres LEDs (rojo, amarillo, verde) y sus resistencias. Pines: R, Y, G, GND. Cada LED enciende cuando su pin recibe 3,3 V.
4. **Cables dupont hembra-hembra** – unen los pines de los módulos directamente al ESP32.

---

## Conexiones

![Esquema de conexiones](esquemas/esquema_conexiones.png)

| Componente | Pin | Pin del ESP32 | Tipo de señal |
|------------|-----|---------------|---------------|
| Sensor UV | S | D34 | Entrada analógica (ADC1) |
| Sensor UV | VCC | 3V3 | Alimentación 3,3 V |
| Sensor UV | GND | GND | Tierra |
| Semáforo | R | D25 | Salida digital |
| Semáforo | Y | D26 | Salida digital |
| Semáforo | G | D27 | Salida digital |
| Semáforo | GND | GND (el otro pin) | Tierra |

**¿Por qué D34?** El ESP32 tiene dos conversores analógicos (ADC1 y ADC2). El ADC2 deja de funcionar cuando el WiFi está encendido, por eso el sensor va en un pin del ADC1.

---

## Pasos de ensamblaje

1. Con el USB **desconectado**, conectar el sensor UV: S → D34, VCC → 3V3, GND → GND.
2. Conectar el semáforo: R → D25, Y → D26, G → D27, GND → el otro pin GND del ESP32.
3. Revisar que **todos los GND** estén conectados (si falta uno, el sensor marca valores falsos y los LEDs no encienden).
4. Conectar el USB: el semáforo debe hacer la secuencia rojo → amarillo → verde.

### Precauciones
- ⚠️ El VCC del sensor va a **3V3**, nunca a VIN/5V: el ESP32 solo tolera 3,3 V en sus entradas.
- ⚠️ Desconectar la alimentación antes de mover cables.
- ⚠️ No mirar directamente linternas UV usadas para las pruebas.

---

## Especificaciones técnicas

**Alimentación:** 5 V por USB (cargador, power bank o computador); el ESP32 regula a 3,3 V.
**Consumo:** [medir con un medidor USB].
**Dimensiones del encapsulado (v1):** 113 mm × 116 mm × 76 mm (ver `diseno_3d/`).
**Peso:** [completar].

---

## Troubleshooting

| Problema | Posible causa | Solución |
|----------|---------------|----------|
| Índice UV ≈ 4 a oscuras | GND del sensor desconectado | Revisar conexión a GND |
| Ninguna luz enciende | GND del semáforo desconectado o cable dañado | Revisar GND; probar cada LED conectándolo a 3V3 |
| El PC no detecta el ESP32 | Falta driver CP210x o cable solo de carga | Instalar driver / cambiar cable |
| Siempre UV 0 bajo techo | Normal: el vidrio bloquea el UV | Probar al aire libre o con linterna UV de 365 nm |
