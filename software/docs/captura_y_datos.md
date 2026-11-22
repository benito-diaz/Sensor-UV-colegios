# Captura, almacenamiento y generación de información

Este documento responde a los 4 primeros criterios de Software del Avance 3.

---

## 1. Captura de datos

| Parámetro | Valor | Justificación |
|---|---|---|
| Sensor | GUVA-S12SD (módulo Keyes), fotodiodo UV con amplificador | Responde entre ~240 y 370 nm (UVA + UVB), que es la radiación que produce daño en piel y ojos |
| Pin | D34 (ADC1, 12 bits, atenuación 11 dB, ~0–3,1 V) | El ADC2 no funciona con WiFi encendido |
| Muestreo interno | 64 muestras promediadas cada 0,5 s | Reduce el ruido del ADC sin atrasar el semáforo |
| Filtro | Promedio exponencial (30 % lectura nueva, 70 % historial) + 4 lecturas seguidas para cambiar de nivel | Evita que el semáforo parpadee cuando el valor está justo en un límite |
| Envío a la nube | **cada 10 s** | La radiación cambia en minutos con la altura del sol y en segundos cuando pasa una nube. 10 s capta una nube y genera ~8.600 filas al día, muy poco para el 1 GB de la base gratuita |
| Conversión | Tabla mV → índice UV con interpolación lineal (valores típicos del sensor) | Ver pendiente de calibración en `testing/` |

Cada lectura enviada:

```json
{"dispositivo":"uv-colegio-1","indice_uv":6.4,"milivoltios":730,"nivel":"ALTO"}
```

El semáforo y la lectura funcionan **aunque no haya WiFi**; Internet corre en una tarea aparte (núcleo 0 del ESP32).

---

## 2. Repositorio de datos

- **Base:** PostgreSQL en **Aiven** (plan Free, 1 GB). **Servidor:** Node.js + Express en **Railway**.
- **Tabla `lecturas_uv`:** `id`, `dispositivo`, `indice_uv`, `milivoltios`, `nivel`, `creado_en` (con zona horaria). Índice por fecha para consultas rápidas.
- **Seguridad:** el ESP32 manda una clave en el header `x-api-key`; sin ella el servidor responde 401. Las consultas usan parámetros (`$1, $2…`) para evitar inyección SQL. Las claves viven en variables de entorno de Railway, nunca en GitHub.
- **Validación:** se rechazan lecturas fuera del rango físico (índice < 0 o > 20, mV < 0 o > 3300) con error 400.
- **Histórico accesible:** `GET /api/lecturas`, `GET /api/historial?horas=…`, descarga `GET /api/exportar.csv?horas=…` y el editor SQL de la consola de Aiven.

---

## 3. Dashboard

Página `software/servidor/public/index.html`, servida por el mismo servidor. Se actualiza sola cada 5 s y funciona en el celular.

| Elemento | Para qué sirve |
|---|---|
| Índice UV actual + color OMS + estado del semáforo | Saber el riesgo de un vistazo |
| Indicador "en línea / sin datos" | Saber si el medidor está funcionando (sin datos hace más de 60 s) |
| Alerta roja (UV ≥ 6) | Llamar la atención cuando hay que actuar |
| Gráfico con franjas OMS: última hora, 6 h, 24 h, 7 días | Ver la tendencia y cuándo se cruzan los umbrales |
| Máximo diario de los últimos 7 días | Comparar días |
| Tabla de últimas lecturas + descarga CSV | Revisar datos crudos y usarlos en el testing |

---

## 4. Información que genera el sistema (y la decisión que apoya)

| Indicador | Cómo se calcula | Decisión que apoya |
|---|---|---|
| **Nivel OMS + recomendación para el colegio** | Índice redondeado → BAJO…EXTREMO | Recreo normal, con bloqueador, a la sombra o bajo techo |
| **Alerta** | Nivel ≥ ALTO (índice ≥ 6) | Mover Educación Física bajo techo o a otro horario |
| **Máximo del día y su hora** | `MAX(indice_uv)` desde las 00:00 (hora de Chile) | Planificar el horario de recreos y clases al aire libre |
| **Tiempo con protección necesaria** | Suma del tiempo entre lecturas con nivel ≥ MODERADO (máx. 60 s por tramo) | Dimensionar cuánto bloqueador y sombra se necesita |
| **Minutos en cada nivel** | Igual, separado por nivel | Ver qué parte de la jornada es riesgosa |
| **Alertas del día** | Veces que el nivel subió a ALTO o más | Cuántas veces hubo que actuar |
| **Máximo diario 7 días** | `MAX` por día | Detectar días de mayor riesgo |

Además, **Telegram** avisa al celular cada vez que cambia el nivel, y el comando `/estado` responde el valor actual.

### Ejemplo de uso
> "A las 12:40 el panel marca UV 7 (ALTO) y aparece la alerta. El inspector recibe el aviso en Telegram y envía el recreo de las 13:00 a la zona techada. El panel muestra que el máximo del día fue a las 13:20 y que hubo 2 h 30 min con protección necesaria."

*(Ejemplo ilustrativo: los valores reales medidos están en `testing/reportes/reporte_testing.md`.)*
