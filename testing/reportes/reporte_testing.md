# Reporte de testing – Avance 3

Protocolo en [`protocolo_pruebas.md`](protocolo_pruebas.md). Pruebas técnicas del Avance 2 en [`pruebas_tecnicas.md`](pruebas_tecnicas.md).

> Todos los valores salen de los datos reales del 22-11-2026. Las pruebas que no se alcanzaron a hacer quedan marcadas como pendientes.

---

## Resumen de resultados

Datos: `testing/datos/lecturas_uv_2026-11-22.csv` (200 lecturas descargadas de `/api/exportar.csv`), prototipo con el hotspot de un iPhone, 22-11-2026 entre 17:18 y 20:06, bajo techo y de tarde (sin radiación UV).

| Prueba | Métrica | Resultado | Criterio | ¿Cumple? |
|---|---|---|---|---|
| P1 Captura continua | Lecturas recibidas / esperadas (1 cada 10 s) | **96,9 %** (156 de 161, de 19:39:21 a 20:06:05, 26,7 min) | ≥ 95 % | ✅ |
| P1 Intervalo | Mediana / promedio entre lecturas | **10,0 s / 10,35 s** | 10 s | ✅ |
| P1 Huecos | Hueco más largo en la prueba larga | **27 s** (19:49:24) | ≤ 60 s | ✅ |
| P1 Persistencia | Lecturas guardadas antes de apagar el equipo siguen en la base | **Sí**: los 200 registros (id 1 a 200, sin saltos) siguen después de apagar y volver a encender el equipo (cortes de 17:24 a 18:55 y de 18:59 a 19:39) | sí | ✅ |
| P2 Tasa de éxito | Respuestas 201 | Sin log completo del Monitor Serie; la base no muestra lecturas perdidas fuera del hueco de 27 s | ≥ 95 % | ⚠️ parcial |
| P2 Latencia | Tiempo de un POST | **1.968 ms** (una medición en el Monitor Serie, 17:18) | media < 3 s | ✅ (1 muestra) |
| P3 Cero sin UV | Índice sin radiación (bajo techo, de noche) | **0,52 (142 mV)**, nivel BAJO, verde | ≤ 0,5 | ❌ por 0,02 → ver F5 |
| P4 Exactitud | Error vs MeteoChile | Pendiente (requiere sol de mediodía) | ≤ 2 puntos | — |
| P5 Respuesta | Semáforo / panel / Telegram | Pendiente de cronometrar | < 3 / 20 / 30 s | — |
| P6 Autonomía | Horas con batería | Pendiente (falta descargar la batería por completo) | ≈ 7 h estimadas | — |
| P7 Seguridad API | Clave mala / fuera de rango / texto | 401 / 400 / 400 | 401 / 400 / 400 | ✅ |

### Cómo se calcularon
- `python3 testing/datos/analizar_datos.py testing/datos/lecturas_uv_2026-11-22.csv`, considerando solo el tramo continuo de 19:39:21 a 20:06:05 para P1.
- Esperadas = duración / 10 s + 1. El intervalo real es un poco mayor que 10 s (10,35 s en promedio) porque cada envío espera la respuesta del servidor y la consulta a Telegram comparte la misma tarea; por eso el porcentaje queda bajo 100 % aunque solo falten ~2 lecturas en el hueco de 27 s.

### Todas las sesiones del día
| Tramo | Lecturas | Observación |
|---|---|---|
| 17:18:55 – 17:24:04 | 31 de 31 (100 %) | Alimentado por USB del computador; primer envío 201 en 1.968 ms |
| 18:55:22 – 18:59:40 | 13 | Prueba con batería; incluye la falla F4 (GND suelto) |
| 19:39:21 – 20:06:05 | 156 de 161 (96,9 %) | Prueba larga, sin tocar el equipo |

---

## P7 – Seguridad de la API (realizada)
Probada el 22-11-2026 con el código de `software/servidor/` ejecutado en un computador con PostgreSQL local:

| Envío | Respuesta |
|---|---|
| `x-api-key` equivocada | `401 {"error":"API key invalida"}` |
| `indice_uv: 30` | `400 {"error":"Lectura fuera de rango"}` |
| `indice_uv: "a"` | `400 {"error":"Faltan campos o no son numeros"}` |
| Lectura válida (`6.4`, `730 mV`) | `201 {"ok":true,"id":1,"nivel":"ALTO"}` |

Repetir con la URL de Railway el día de la demo.

---

## P4 – Comparación con MeteoChile (pendiente)

Las pruebas del 22-11 fueron bajo techo y de tarde, sin radiación UV. Esta tabla se completa con mediciones al sol de mediodía.

| Hora | Medidor (promedio 5 min) | MeteoChile | Diferencia |
|---|---|---|---|
| [hh:mm] | [ ] | [ ] | [ ] |
| [hh:mm] | [ ] | [ ] | [ ] |
| [hh:mm] | [ ] | [ ] | [ ] |

---

## Fallas encontradas y cómo se resolvieron

### F1 – Lectura falsa de UV 4 en oscuridad (Avance 2, real)
- **Síntoma:** de noche, en una pieza cerrada, el medidor marcaba **índice 4,0 (≈ 500 mV)** y el semáforo quedaba apagado.
- **Causa:** el GND del ESP32 no estaba conectado al riel de tierra; la salida del sensor quedaba "flotando".
- **Solución:** GND común y conexión directa con cables hembra-hembra. Resultado: índice **0,5 (142 mV)** bajo techo.
- **Prevención:** la prueba P3 (cero en oscuridad) quedó en el protocolo.

### F2 – Errores 429, -11 y 502 de Telegram (Avance 2, real)
- **Síntoma:** el bot no respondía; el Monitor Serie mostraba esos códigos.
- **Causa:** se consultaba Telegram cada 3 s (429 = demasiadas consultas) con un tiempo de espera de 8 s, corto para el hotspot del celular (-11 = tiempo agotado).
- **Solución:** consulta cada **10 s** y espera de **15 s**. El aviso llegó al celular y `/estado` respondió.

### F3 – Alertas falsas cuando el índice está justo en un límite (Avance 3, desarrollo del servidor)
- **Síntoma:** al probar el servidor con datos simulados con ruido alrededor de 5,5, el contador de alertas del día subía muchas veces aunque la radiación no cambiaba de verdad.
- **Causa:** el servidor recalculaba el nivel con cada lectura, sin la confirmación de 4 lecturas que usa el semáforo.
- **Solución:** el ESP32 envía el **mismo nivel confirmado** que muestra el semáforo, y el servidor lo usa. Así el panel, el semáforo y Telegram coinciden.

### F4 – GND del sensor suelto: lectura imposible de 2.827 mV (Avance 3, real)
- **Síntoma:** a las 18:59:31 se guardó una lectura con **índice 19,41 y 2.827 mV**, mientras el sensor estaba en interior. La lectura siguiente (18:59:40) volvió a 0,54 y 142 mV.
- **Causa:** el cable GND del sensor se desconectó; sin tierra, la entrada D34 queda "flotando" y lee un voltaje cualquiera (la misma causa de F1).
- **Lo que funcionó bien:** el **nivel guardado siguió en BAJO**, el **semáforo no cambió** y **Telegram no mandó una alerta falsa**, porque el nivel solo cambia tras 4 lecturas seguidas y la falla duró menos que eso.
- **Lo que quedó mal:** el valor 19,41 se guardó y el panel lo mostró como "máximo de hoy".
- **Solución propuesta:** que el servidor rechace lecturas sobre 2.000 mV (el sensor entrega ≈ 1,2 V con índice 11; más de 2 V solo puede ser una falla eléctrica). El dato real no se borró de la base: queda como evidencia de la falla.

### F5 – El cero del sensor marca 0,52 sin radiación (Avance 3, real)
- **Síntoma:** bajo techo y de noche el sensor entrega **142 mV constantes**, que la tabla convierte en índice **0,52**.
- **Causa:** la tabla `TABLA_MV` usa valores típicos (50 mV para índice 0), pero este sensor y el ADC del ESP32 tienen un desfase de ≈ 92 mV.
- **Efecto:** ninguno en la decisión (sigue en BAJO, luz verde), pero el índice mínimo no llega a 0.
- **Solución propuesta:** calibrar el cero cambiando el primer valor de `TABLA_MV` a 142 mV, y ajustar el resto con la comparación contra MeteoChile (P4).

---

## Mejoras propuestas (fundamentadas)
1. **Calibración:** fijar el cero en 142 mV (F5) y ajustar `TABLA_MV` con las mediciones de P4 (la tabla actual es típica del sensor, no medida).
2. **Filtro de fallas eléctricas:** rechazar en el servidor lecturas sobre 2.000 mV (F4).
3. **Energía (recomendación del profesor):** operar en horario escolar: despertar antes de cada recreo, avisar, mostrar el semáforo durante el recreo y dormir el ESP32 (deep sleep) el resto del tiempo. Con WiFi siempre encendido el balance estimado (0,55 W de consumo contra ≈ 0,9 W de panel solo en horas de sol) no alcanza para 24 h.
4. **Conectividad:** usar la red WiFi del colegio (2,4 GHz, sin usuario) y guardar lecturas en memoria cuando no hay Internet para enviarlas después.

---

## Validación contra el problema del Avance 1

**Problema:** en los colegios de Peñalolén no existe un indicador local y en tiempo real del riesgo UV que permita al personal decidir cómo proteger a los niños.

| Lo que el problema necesita | Evidencia del sistema |
|---|---|
| Medir en el lugar, no un pronóstico general de la ciudad | P1: 200 lecturas reales guardadas en la nube el 22-11; 96,9 % de captura en la prueba de 26,7 min |
| Saber cuándo el riesgo es alto | Alerta con UV ≥ 6 en panel, semáforo y Telegram; F4 muestra que una lectura falsa no dispara alertas |
| Saber qué hacer | Recomendación por nivel adaptada al colegio (recreo, Ed. Física) |
| Planificar la jornada | El panel calcula máximo del día y su hora, minutos con protección y alertas (las pruebas fueron sin sol: todo el tiempo en BAJO) |
| Confiar en el valor | Pendiente P4 con MeteoChile; F5 identifica el desfase del cero a corregir |

**Conclusión:** la cadena completa (sensor → ESP32 → Railway → Aiven → panel y Telegram) funcionó de forma continua: 96,9 % de las lecturas llegaron en la prueba larga, no se perdió ningún dato guardado al apagar el equipo y una falla de cableado no generó alertas falsas. Falta validar la exactitud con sol real (P4) y corregir el cero del sensor (F5) antes de usarlo en un colegio.
