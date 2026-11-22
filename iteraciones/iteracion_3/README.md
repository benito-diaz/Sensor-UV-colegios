# Iteración 3 – Versión final (Avance 3)

**Fecha:** 22-11-2026 (presentación 23-11-2026)
**Estado:** prototipo IoT completo

## Qué se agregó respecto de la v2

| Área | v2 (Avance 2) | v3 (Avance 3) |
|---|---|---|
| Datos | Solo en tiempo real (Monitor Serie y Telegram) | Cada lectura se guarda en PostgreSQL (Aiven) cada 10 s |
| Visualización | Monitor Serie | Panel web público (Railway) con gráfico, tabla, CSV |
| Información | Nivel y recomendación | + alerta UV ≥ 6, máximo del día y su hora, tiempo con protección, alertas del día, máximos de 7 días |
| Energía | USB del computador / power bank | Panel solar 5,5 V + LiPo Rider Pro + batería 1200 mAh |
| Encapsulado | Caja v1 sin fijaciones | Carcasa v4 en ASA con insertos, junta TPU, techo solar y soporte de pared |
| Firmware | `v2.3_telegram_final.ino` | `software/src/main.ino` (+ `enviarLecturaNube`) |

## Decisiones
- **Railway + Aiven** en vez de Firebase: es la arquitectura de la guía del curso; PostgreSQL permite calcular las estadísticas con SQL en el servidor.
- **Envío cada 10 s:** capta el paso de nubes sin llenar la base (≈ 8.600 filas al día).
- **Se mantiene Telegram:** ya funcionaba y llega al celular aunque nadie mire el panel.
- **El servidor recibe el nivel del semáforo:** así el panel y el semáforo nunca muestran colores distintos.
