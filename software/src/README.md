# Código Fuente

## `main.ino`

Archivo único del proyecto para el ESP32. Las credenciales están reemplazadas por textos de ejemplo (`NOMBRE_DE_TU_RED`, `PEGA_AQUI_EL_TOKEN`, etc.) y deben completarse antes de subir el código a la placa.

**Estructura:**

| Sección | Líneas aprox. | Qué hace |
|---------|---------------|----------|
| Configuración | 37–42 | WiFi y Telegram |
| Pines y ajustes | 44–64 | Pines, parámetros y tabla de calibración |
| Estado | 66–99 | Niveles OMS, mensajes y variables compartidas |
| Lectura y procesamiento | 101–160 | Promedio del sensor, conversión a índice UV, nivel con confirmación |
| Semáforo y mensajes | 162–176 | Control de LEDs y Monitor Serie |
| Internet: WiFi + Telegram | 178–317 | Envío de avisos, lectura de comandos, tarea en el núcleo 0 |
| `setup()` | 327–352 | Inicialización |
| `loop()` | 354–382 | Ciclo principal (núcleo 1) |

---

## Estándares de código

- Comentarios en español que explican qué hace cada parte y por qué.
- Variables y funciones en `camelCase`, constantes en `UPPER_SNAKE_CASE`.
- Monitor Serie a **115200 baud**, con prefijos `[WiFi]` y `[Telegram]` para los mensajes de conexión.

## Mensajes del Monitor Serie (ejemplo)

```
Medidor UV listo. Mensaje cada 15 segundos o al cambiar de color.
[WiFi] Conectando a NOMBRE_DE_TU_RED
[WiFi] Conectado a NOMBRE_DE_TU_RED. IP: 172.20.10.2
--------------------------------------------------
LUZ VERDE - Radiacion UV baja. Se puede salir a la calle con tranquilidad.
Indice UV: 0.5 (BAJO) | Sensor: 142 mV
[Telegram] Aviso enviado al celular.
```
