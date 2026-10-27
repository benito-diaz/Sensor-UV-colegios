# Historial de Iteraciones

## Propósito

Esta carpeta documenta cómo evolucionó el sistema desde el concepto inicial (Avance 1) hasta el prototipo funcional actual (Avance 2), y qué falta para la versión final.

```
iteraciones/
├── iteracion_1/    # Concepto inicial – Avance 1
├── iteracion_2/    # Prototipo funcional – Avance 2 (versiones v2.0 a v2.3)
└── iteracion_3/    # Versión final – Avance 3 (planificada)
```

---

## Tabla comparativa de iteraciones

| Aspecto | v1 – Concepto | v2 – Prototipo funcional | v3 – Final (planificada) |
|---------|---------------|--------------------------|--------------------------|
| **Fecha** | Septiembre 2026 | 14/10 – 27/10/2026 | [fecha Avance 3] |
| **Sensores** | Sensor UV (concepto) | GUVA-S12SD conectado al ESP32 | GUVA-S12SD calibrado con MeteoChile |
| **Actuadores** | — | Semáforo LED V1224 (5 niveles con parpadeo) | Semáforo integrado en la cápsula |
| **Conectividad** | — | WiFi + avisos por Telegram | WiFi + Telegram (posible grupo del colegio) |
| **Ubicación** | Fijo en un poste | Portátil (propuesta: instalar y retirar del poste) | Portátil con soporte para poste |
| **Encapsulado** | Cápsula básica (solo contener el sensor) | Modelo 3D v1 en Fusion 360 (113 × 116 × 76 mm) | Cápsula con encajes y tamaño ajustado |
| **Información entregada** | Color de riesgo general | Índice UV numérico + color + recomendación | Igual a v2, validada con usuarios |
| **Testing** | — | Pruebas técnicas del equipo | Pruebas con 5+ usuarios |

---

## Evolución del diseño

### Versión 1 (Iteración 1) – Concepto inicial
**Fecha:** septiembre 2026 (Avance 1)
**Estado:** concepto / propuesta

- Sensor UV fijo en un poste: los niños debían acercarse para consultar el nivel.
- Cápsula básica cuya única función era contener el sensor.
- Comunicación cualitativa: un color asociado a un riesgo general.

### Versión 2 (Iteración 2) – Prototipo funcional
**Fecha:** 14/10/2026 – 27/10/2026 (Avance 2)
**Estado:** prototipo funcional, presentado el 19/10/2026

**Mejoras implementadas:**
- Prototipo electrónico real: ESP32 + sensor GUVA-S12SD + semáforo LED.
- Medición cuantitativa: el voltaje del sensor se convierte a **índice UV** y cada color corresponde a un rango de la **escala OMS**.
- Mensaje de recomendación por nivel (de "se puede salir con tranquilidad" a "no se puede salir").
- Lectura estable: promedio de 64 muestras, suavizado y confirmación de 4 lecturas antes de cambiar de color.
- Avisos al celular por **Telegram** y comando `/estado`.
- Propuesta de dispositivo portátil, que se pueda instalar y retirar del poste.
- Primer modelo 3D del encapsulado en Fusion 360.

**Problemas pendientes:**
- Calibración aproximada (tabla típica del sensor, no verificada con una referencia oficial).
- Depende de una red WiFi de 2,4 GHz (en la demo, el hotspot de un celular).
- Encapsulado sin encajes ni tornillos y de tamaño provisorio.
- Falta probar con usuarios reales.

Detalle de cada versión intermedia en [`iteracion_2/README.md`](iteracion_2/README.md).

### Versión 3 (Iteración 3) – Versión final
**Fecha:** [Avance 3]
**Estado:** planificada. Ver [`iteracion_3/README.md`](iteracion_3/README.md).

---

## Justificación de cambios

### Hardware
**De v1 a v2:**
- Cambio: del concepto a un circuito real con ESP32, sensor GUVA-S12SD y semáforo LED.
- Razón: el ESP32 tiene WiFi integrado, lo que permite enviar avisos sin agregar módulos.
- Impacto: el dispositivo mide, muestra y avisa en tiempo real.

**Dentro de v2 (protoboard → conexión directa):**
- Cambio: se intentó armar en protoboard y se volvió a la conexión directa con cables hembra-hembra.
- Razón: el ESP32 deja solo una columna libre por lado, los módulos quedaban parados y frágiles, y hubo fallas de GND (lectura falsa de UV 4 a oscuras y semáforo apagado).
- Impacto: la conexión directa funcionó de forma confiable para la presentación.

### Software
**De v1 a v2:**
- De un color de riesgo general a un **índice UV numérico** con rangos OMS y mensajes de recomendación.
- Avisos remotos por Telegram ejecutándose en un núcleo separado, para que el semáforo nunca se trabe.
- Ajuste de la comunicación con Telegram (consulta cada 10 s, espera de 15 s) tras errores con el hotspot.

### Diseño 3D
**De v1 a v2:**
- De una cápsula básica a una caja con apertura para el semáforo, bandeja para el ESP32, agujero para el sensor en la tapa, ventilación y salida de cable.

---

## Decisiones técnicas

| Decisión | Alternativa descartada | Motivo |
|----------|------------------------|--------|
| ESP32 como microcontrolador | Arduino UNO | El ESP32 tiene WiFi integrado y trabaja a 3,3 V, igual que el sensor |
| Sensor en el pin D34 (ADC1) | Pines del ADC2 | El ADC2 no funciona con el WiFi encendido |
| 5 niveles OMS con 3 luces (parpadeo para 8–10 y 11+) | Solo 3 niveles | Respetar la escala oficial de la OMS con el semáforo disponible |
| Promedio de 64 muestras + suavizado + confirmación de 4 lecturas | Lectura única | Evitar saltos y parpadeos cuando el valor está en un límite |
| Avisos por Telegram | App propia, Blynk, ntfy | Gratis, funciona en iPhone y Android, envía notificaciones, permite grupos y responde comandos, sin programar una app |
| Internet en una tarea del núcleo 0 | Todo en el `loop` | Las peticiones HTTPS tardan 1–2 s; así el semáforo nunca se traba |
| Consultar Telegram cada 10 s | Cada 3 s | Errores 429/-11 con el hotspot del celular |
| Conexión directa con cables hembra-hembra | Protoboard | El ESP32 tapaba casi toda la protoboard, los módulos quedaban frágiles y hubo fallas de GND |
| Credenciales fuera del repositorio | Dejarlas en el código | El repositorio es público y el token permite controlar el bot |

---

## Incorporación de feedback

### Feedback del Avance #1 → cambios en v2
1. [Comentario del profesor/ayudante]
   - Acción tomada: [completar]

### Feedback de la presentación del 19/10 → cambios en v3
1. [Comentario del profesor/ayudante]
   - Acción tomada: [completar]

### Conversación con el profesor sobre energía
- Se evaluará incluir **energía solar**. Por eso la caja v1 se dejó más grande de lo necesario, para ajustarla cuando se defina la parte eléctrica.

---

## Métricas de mejora

| Métrica | v1 | v2 | Cómo se midió |
|---------|----|----|---------------|
| Niveles de riesgo distinguibles | 1 color general | 5 niveles OMS | Diseño del código |
| Intervalo de medición | — | 0,5 s | Parámetro del código |
| Tiempo máximo de respuesta a `/estado` | — | ≤ 10 s | Intervalo de consulta a Telegram |
| Satisfacción de usuarios (1–5) | — | [pendiente] | Testing con usuarios (Avance 3) |

---

## Lecciones aprendidas

### Técnicas
- El GND común entre todos los módulos es indispensable: sin él, la lectura del sensor queda "flotando" y da valores falsos.
- En el ESP32, las entradas analógicas usadas con WiFi deben estar en el ADC1 (por ejemplo, D34).
- Bajo techo el sensor marca cerca de 0 porque el vidrio bloquea casi todo el UV; las pruebas deben hacerse al aire libre o con una linterna UV de 365 nm.
- Los servicios en la nube (Telegram) tienen límites de consultas: hay que espaciar las peticiones.

### De proceso
- Probar primero la versión más simple (conexión directa) y cambiar una sola cosa a la vez facilitó encontrar los errores.
- Guardar siempre una copia del código que funciona antes de agregar funciones nuevas (WiFi).
- No subir credenciales (WiFi, token) al repositorio público.
