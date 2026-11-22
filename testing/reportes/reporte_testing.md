# Reporte de testing – Avance 3

Protocolo en [`protocolo_pruebas.md`](protocolo_pruebas.md). Pruebas técnicas del Avance 2 en [`pruebas_tecnicas.md`](pruebas_tecnicas.md).

> Los campos `[completar]` se llenan con los datos reales de las pruebas (CSV del panel y log del Monitor Serie, procesados con `testing/datos/analizar_datos.py`). No se inventan valores.

---

## Resumen de resultados

| Prueba | Métrica | Resultado | Criterio | ¿Cumple? |
|---|---|---|---|---|
| P1 Captura continua | Lecturas recibidas / esperadas | [completar] % ([n] de [m]) | ≥ 95 % | [ ] |
| P1 Persistencia | Lecturas antes del reinicio siguen en la base | [sí/no] | sí | [ ] |
| P1 Huecos | Hueco más largo | [completar] s | ≤ 60 s (salvo reinicio) | [ ] |
| P2 Tasa de éxito | Respuestas 201 | [completar] % | ≥ 95 % | [ ] |
| P2 Latencia | Media / máxima | [completar] / [completar] ms | media < 3 s | [ ] |
| P3 Oscuridad | Índice con el sensor tapado | [completar] ([mV] mV) | ≤ 0,5 | [ ] |
| P4 Exactitud | Error medio vs MeteoChile | [completar] puntos | ≤ 2 | [ ] |
| P5 Respuesta | Semáforo / panel / Telegram | [ ] s / [ ] s / [ ] s | < 3 / 20 / 30 s | [ ] |
| P6 Autonomía | Horas con batería | [completar] h | ≈ 7 h estimadas | [ ] |
| P7 Seguridad API | Clave mala / fuera de rango / texto | 401 / 400 / 400 | 401 / 400 / 400 | ✅ |

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

## P4 – Comparación con MeteoChile

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

### F4 – [completar si aparece alguna falla en P1–P6]

---

## Mejoras propuestas (fundamentadas)
1. **Calibración:** ajustar `TABLA_MV` con las mediciones de P4 (la tabla actual es típica del sensor, no medida).
2. **Energía:** dormir el ESP32 de noche y operar solo en horario escolar; el balance estimado (0,55 W de consumo contra ≈ 0,9 W de panel solo en horas de sol) no alcanza para 24 h.
3. **Conectividad:** usar la red WiFi del colegio (2,4 GHz, sin usuario) y guardar lecturas en memoria cuando no hay Internet para enviarlas después.

---

## Validación contra el problema del Avance 1

**Problema:** en los colegios de Peñalolén no existe un indicador local y en tiempo real del riesgo UV que permita al personal decidir cómo proteger a los niños.

| Lo que el problema necesita | Evidencia del sistema |
|---|---|
| Medir en el lugar, no un pronóstico general de la ciudad | P1: [n] lecturas reales del patio en [t] min, guardadas en la nube |
| Saber cuándo el riesgo es alto | Alerta con UV ≥ 6; P5: aviso en [ ] s |
| Saber qué hacer | Recomendación por nivel adaptada al colegio (recreo, Ed. Física) |
| Planificar la jornada | Máximo del día a las [hh:mm]; [ ] min con protección necesaria; [ ] alertas |
| Confiar en el valor | P4: diferencia de [ ] puntos con MeteoChile |

**Conclusión:** [completar con los datos: por ejemplo, "el día X el medidor registró un máximo de N a las HH:MM y estuvo M minutos sobre el nivel moderado; con el panel, el personal podría haber movido el recreo de las HH:MM a la sombra"].
