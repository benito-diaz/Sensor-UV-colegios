# Reporte de pruebas técnicas – Avance 2

**Período:** 14/10/2026 – 19/10/2026
**Realizadas por:** equipo del proyecto
**Prototipo:** ESP32 DevKit + sensor UV GUVA-S12SD + semáforo LED V1224 (ver `hardware/`)

## Resumen

| ID | Prueba | Resultado |
|----|--------|-----------|
| T01 | Reconocimiento del ESP32 por USB | ❌ → ✅ corregida |
| T02 | Compilación y carga del código | ✅ |
| T03 | Prueba de luces al encender | ✅ |
| T04 | Lectura del sensor bajo techo | ✅ |
| T05 | Mensajes de recomendación en el Monitor Serie | ✅ |
| T06 | Montaje del ESP32 en protoboard | ❌ → ✅ corregida |
| T07 | Lectura a oscuras con el montaje en protoboard | ❌ → ✅ corregida |
| T08 | Semáforo con el montaje en protoboard | ❌ → cambio de diseño |
| T09 | Conexión WiFi al hotspot del celular | ✅ |
| T10 | Avisos y comandos por Telegram | ❌ → ✅ corregida |
| T11 | Uso del dispositivo desde otro computador | ❌ → ✅ corregida |

**Total:** 11 pruebas · 5 correctas al primer intento · 5 con falla corregida · 1 resuelta con un cambio de diseño.

---

## Detalle

### T01 – Reconocimiento del ESP32 por USB (14/10)
- **Procedimiento:** conectar el ESP32 al PC y buscar su puerto en Arduino IDE.
- **Esperado:** aparece un puerto COM nuevo.
- **Obtenido:** solo aparecía COM1 ("Unknown"). En el Administrador de dispositivos: *CP2102 USB to UART Bridge Controller* con advertencia.
- **Causa:** faltaba el driver del chip USB CP2102.
- **Acción:** instalar "CP210x Windows Drivers" (Silicon Labs, v6.7.6).
- **Resultado final:** aparece **COM3**. ✅
- **Evidencia:** `evidencias/01_driver_cp2102_faltante.png`, `evidencias/02_paquete_esp32_instalado.png`

### T02 – Compilación y carga del código (14/10)
- **Procedimiento:** compilar y subir `main.ino` con la placa *ESP32 Dev Module* en COM3.
- **Esperado:** carga sin errores.
- **Obtenido:** *"Hash of data verified" / "Hard resetting via RTS pin"*. ✅
- **Evidencia:** `evidencias/03_carga_exitosa_codigo.png`

### T03 – Prueba de luces al encender (14/10)
- **Procedimiento:** reiniciar el ESP32 con el semáforo conectado directamente.
- **Esperado:** secuencia rojo → amarillo → verde y luego el color del nivel actual.
- **Obtenido:** secuencia correcta y semáforo en verde. ✅

### T04 – Lectura del sensor bajo techo
- **Procedimiento:** observar el Monitor Serie con el sensor en interior.
- **Esperado:** índice UV bajo (el vidrio bloquea casi todo el UV) y luz verde.
- **Obtenido:** lectura registrada el 19/10: **142 mV ≈ índice UV 0,5 (BAJO)**, luz verde. ✅
- **Nota:** queda pendiente la prueba al aire libre y la comparación con MeteoChile.

### T05 – Mensajes de recomendación en el Monitor Serie (14/10)
- **Procedimiento:** abrir el Serial Monitor a 115200 baud y esperar.
- **Esperado:** mensaje cada 15 s con color, recomendación, índice UV y voltaje.
- **Obtenido:** mensajes correctos (ej. *"LUZ VERDE – Radiación UV baja. Se puede salir a la calle con tranquilidad."*). ✅

### T06 – Montaje del ESP32 en protoboard (18/10)
- **Procedimiento:** insertar el ESP32 en una protoboard de 830 puntos.
- **Esperado:** al menos un agujero libre a cada lado de los pines.
- **Obtenido:** el ESP32 ocupó de la columna A a la I; solo quedó libre la columna J por un lado. El pin 3V3 quedó sin acceso. Además, los módulos (pines hacia el costado) quedaban parados y frágiles.
- **Acción:** alimentar el sensor desde **D32** configurado en 3,3 V y conectar los módulos fuera de la protoboard con cables hembra-macho. ✅
- **Evidencia:** `evidencias/04_prueba_protoboard.jpg`

### T07 – Lectura a oscuras con el montaje en protoboard (18/10, noche)
- **Procedimiento:** medir en una pieza cerrada, de noche.
- **Esperado:** índice UV 0.
- **Obtenido:** **índice UV 4,0** (≈500 mV) y semáforo apagado.
- **Causa:** el GND del ESP32 no estaba conectado al riel de tierra; la salida del sensor quedaba "flotando".
- **Acción:** corregir el cable de GND al riel azul (−).
- **Resultado final:** índice UV **bajo**. ✅

### T08 – Semáforo con el montaje en protoboard (18/10)
- **Procedimiento:** verificar la secuencia de luces tras corregir el GND.
- **Esperado:** secuencia rojo → amarillo → verde.
- **Obtenido:** ninguna luz encendía, aunque el sensor ya funcionaba con el mismo GND.
- **Causa probable:** cable del semáforo en una fila incorrecta o cable dañado (no se alcanzó a confirmar).
- **Acción:** **cambio de diseño**: volver a la conexión directa con cables hembra-hembra (R→D25, Y→D26, G→D27, GND→GND).
- **Resultado final:** semáforo y sensor funcionando. ✅

### T09 – Conexión WiFi al hotspot del celular (18/10)
- **Procedimiento:** hotspot de iPhone con "Maximizar compatibilidad" (2,4 GHz); credenciales en el código.
- **Esperado:** `[WiFi] Conectado a …` en el Monitor Serie.
- **Obtenido:** conexión correcta. ✅

### T10 – Avisos y comandos por Telegram (18/10)
- **Procedimiento:** crear el bot con @BotFather, escribirle `/start` y esperar la respuesta con el chat ID.
- **Esperado:** el bot responde y luego envía "Medidor UV conectado".
- **Obtenido:** sin respuesta; errores **-11** (tiempo de espera agotado), **429** (demasiadas consultas) y **502** (servidor ocupado).
- **Acción:** consultar Telegram cada 10 s (antes 3 s), tiempo de espera 15 s (antes 8 s), y obtener el chat ID con @userinfobot.
- **Resultado final:** aviso recibido en el celular y `/estado` respondido. ✅

### T11 – Uso del dispositivo desde otro computador (19/10)
- **Procedimiento:** conectar el ESP32 a un computador distinto.
- **Esperado:** reconocer la placa y ver los mensajes.
- **Obtenido:** Arduino mostraba *"Unknown COM3"* (placa no seleccionada / paquete esp32 no instalado en ese PC).
- **Acción:** seleccionar *ESP32 Dev Module* e instalar el paquete esp32. Se comprobó además que el programa queda guardado en el ESP32 y funciona con solo alimentarlo.
- **Resultado final:** Monitor Serie con lecturas (142 mV, UV bajo). ✅
- **Evidencia:** `evidencias/05_conexion_en_otro_pc.jpg`

---

## Pruebas pendientes
- [ ] Medición al aire libre a distintas horas y comparación con el índice UV de MeteoChile.
- [ ] Prueba con linterna UV de 365 nm para recorrer todos los niveles del semáforo.
- [ ] Prueba de duración con power bank.
- [ ] Pruebas con usuarios (ver `testing/README.md`).
