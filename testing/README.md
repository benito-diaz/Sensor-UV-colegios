# Testing y Validación

## Objetivo
Verificar que el prototipo mide, muestra y avisa correctamente el nivel de radiación UV, y validar con usuarios reales que la información es clara y útil para proteger a los niños durante la jornada escolar.

---

## Carpetas

| Carpeta | Contenido |
|---------|-----------|
| `reportes/` | [`protocolo_pruebas.md`](reportes/protocolo_pruebas.md) (Avance 3), [`reporte_testing.md`](reportes/reporte_testing.md) (resultados, fallas y validación) y [`pruebas_tecnicas.md`](reportes/pruebas_tecnicas.md) (Avance 2) |
| `evidencias/` | Capturas y fotos de las pruebas |
| `datos/` | CSV de la base, log del Monitor Serie y script `analizar_datos.py` |

---

## 1. Pruebas del Avance 3

Siete pruebas (P1–P7): captura continua y persistencia, latencia y tasa de error del envío, cero en oscuridad, comparación con MeteoChile, respuesta de extremo a extremo, autonomía con batería y seguridad de la API. Protocolo en [`reportes/protocolo_pruebas.md`](reportes/protocolo_pruebas.md) y resultados en [`reportes/reporte_testing.md`](reportes/reporte_testing.md).

## 2. Pruebas técnicas (realizadas – Avance 2)

Se hicieron **11 pruebas técnicas** de instalación, hardware, software y conectividad durante el desarrollo (14/10 – 19/10/2026). El detalle de cada prueba, el resultado y la acción tomada está en [`reportes/pruebas_tecnicas.md`](reportes/pruebas_tecnicas.md).

| Resultado | Cantidad |
|-----------|----------|
| Correctas al primer intento | 5 |
| Con falla, corregidas | 5 |
| Con falla, resuelta con un cambio de diseño (protoboard → conexión directa) | 1 |

**Principales hallazgos:**
- Sin GND común el sensor da lecturas falsas (UV 4 en oscuridad).
- El montaje en protoboard no es adecuado para este ESP32 y estos módulos.
- La comunicación con Telegram por hotspot necesita consultas espaciadas (10 s) y mayor tiempo de espera (15 s).

### Aprendizajes del proceso de testing
1. **Probar en condiciones conocidas primero.** Medir en oscuridad (donde el UV debe ser 0) permitió detectar la lectura falsa de UV 4 causada por el GND desconectado.
2. **Cambiar una sola cosa a la vez.** Al pasar a protoboard se cambiaron varias conexiones al mismo tiempo y fue difícil encontrar la falla del semáforo; volver a la versión que funcionaba resolvió el problema.
3. **Los mensajes del Monitor Serie son clave para diagnosticar.** Los códigos de error de Telegram (-11, 429, 502) indicaron exactamente qué ajustar.
4. **El ambiente de prueba importa.** Bajo techo el sensor marca cerca de 0 porque el vidrio bloquea el UV; para probar todos los niveles se necesita sol directo o una linterna UV de 365 nm.
5. **Guardar la versión que funciona** antes de agregar funciones nuevas permitió presentar aunque la versión con WiFi fallara.

---

