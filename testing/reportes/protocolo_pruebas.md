# Protocolo de pruebas – Avance 3

**Sistema:** ESP32 + GUVA-S12SD + semáforo + LiPo Rider Pro / batería / panel → Railway → Aiven → panel web + Telegram
**Firmware:** `software/src/main.ino` (v3) · **Servidor:** `software/servidor/`
**Herramientas:** Monitor Serie (115200), panel web, descarga `/api/exportar.csv`, consola SQL de Aiven, cronómetro del celular, MeteoChile.

Cada prueba indica objetivo, condiciones, pasos, criterio de éxito y evidencia. Los resultados van en [`reporte_testing.md`](reporte_testing.md).

---

## P1 – Captura continua y persistencia
- **Objetivo:** comprobar que las lecturas llegan a la base sin cortes y que no se pierden al reiniciar.
- **Condiciones:** al aire libre (o junto a una ventana abierta), WiFi del hotspot en 2,4 GHz, al menos **30 min**.
- **Pasos:**
  1. Anotar la hora de inicio y encender el medidor.
  2. A los 15 min, desconectar y reconectar la alimentación del ESP32 (reinicio).
  3. A los 30 min, descargar `/api/exportar.csv?horas=1` y guardarlo en `testing/datos/`.
  4. Correr `python3 testing/datos/analizar_datos.py testing/datos/<archivo>.csv`.
- **Criterio de éxito:** ≥ 95 % de las lecturas esperadas (1 cada 10 s) y ningún hueco mayor a 60 s salvo el reinicio; las lecturas anteriores al reinicio siguen en la base.
- **Evidencia:** CSV, salida del script, captura del panel.

## P2 – Latencia y tasa de error del envío
- **Objetivo:** medir cuánto tarda cada envío y cuántos fallan.
- **Condiciones:** las mismas de P1.
- **Pasos:**
  1. Durante P1, copiar el texto del Monitor Serie a `testing/datos/log_serial.txt`.
  2. Correr `python3 testing/datos/analizar_datos.py --log testing/datos/log_serial.txt`.
- **Criterio de éxito:** ≥ 95 % de respuestas `201`; latencia media < 3 s.
- **Evidencia:** log y salida del script.

## P3 – Cero en oscuridad (condición conocida)
- **Objetivo:** verificar que el sensor no da lecturas falsas (falla real del Avance 2: UV 4 sin GND).
- **Pasos:** tapar completamente la ventana del sensor 2 min; leer índice y mV en el panel y el Monitor Serie.
- **Criterio de éxito:** índice ≤ 0,5 y nivel BAJO (verde).
- **Evidencia:** captura del Monitor Serie o de la tabla del panel.

## P4 – Comparación con la referencia oficial
- **Objetivo:** estimar el error del medidor contra el índice UV oficial.
- **Condiciones:** al aire libre, sin sombra, sensor apuntando al cielo; 3 horarios distintos (por ejemplo 11:00, 13:00, 16:00).
- **Pasos:** registrar el índice del medidor (promedio de 5 min del panel) y el índice UV publicado por la Dirección Meteorológica de Chile (MeteoChile) para Santiago a la misma hora.
- **Criterio de éxito:** diferencia ≤ 2 puntos de índice (no más de un nivel OMS de diferencia).
- **Evidencia:** tabla con hora, valor del medidor, valor oficial y captura de MeteoChile.

## P5 – Respuesta de extremo a extremo (semáforo, panel y Telegram)
- **Objetivo:** medir el tiempo desde que cambia la radiación hasta que el usuario recibe la información.
- **Pasos:** con sol, tapar y destapar el sensor; cronometrar cuándo cambia el semáforo, cuándo se actualiza el panel y cuándo llega el aviso de Telegram. Repetir 5 veces.
- **Criterio de éxito:** semáforo < 3 s; panel < 20 s; Telegram < 30 s; los tres muestran el mismo nivel.
- **Evidencia:** tabla de tiempos y captura del aviso.

## P6 – Autonomía con batería
- **Objetivo:** medir cuántas horas funciona sin sol ni USB.
- **Pasos:** batería cargada; desconectar panel y USB; anotar la hora; ver en el panel la última lectura recibida cuando se apague.
- **Criterio de referencia:** estimación de diseño ≈ 7 h (ver `hardware/README.md`).
- **Evidencia:** hora de inicio y hora de la última lectura en la base.

## P7 – Seguridad y validación de la API
- **Objetivo:** que nadie sin la clave pueda llenar la base y que se rechacen datos imposibles.
- **Pasos:** enviar un POST con una clave equivocada; enviar un índice fuera de rango; enviar un texto en vez de número.
- **Criterio de éxito:** 401, 400 y 400 respectivamente; nada se guarda.
- **Evidencia:** respuestas del servidor.
