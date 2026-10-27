# Iteración 2 – Prototipo funcional (Avance 2)

**Fecha:** 14/10/2026 – 27/10/2026
**Estado:** prototipo funcional, presentado el 19/10/2026

Esta iteración tuvo cuatro versiones intermedias. Cada una resolvió un problema detectado en la anterior.

---

## v2.0 – Primer prototipo (14/10)

**Qué se hizo**
- Circuito con ESP32 DevKit, sensor GUVA-S12SD y semáforo V1224, conectados directamente con cables hembra-hembra.
- Código que lee el sensor (promedio de 64 muestras), convierte el voltaje a índice UV y enciende el color según la escala OMS (0–2 verde, 3–5 amarillo, 6–7 rojo, 8–10 rojo parpadeo lento, 11+ rojo parpadeo rápido).
- Prueba de luces al encender (rojo → amarillo → verde).

**Problemas encontrados**
- El computador no reconocía el ESP32: solo aparecía COM1. El Administrador de dispositivos mostraba *"CP2102 USB to UART Bridge Controller"* con advertencia → faltaba el driver.

**Solución**
- Instalación del driver CP210x de Silicon Labs → apareció **COM3** y el código se cargó correctamente (*"Hash of data verified"*). Evidencias: `testing/evidencias/01_driver_cp2102_faltante.png`, `03_carga_exitosa_codigo.png`.

**Resultado:** semáforo en verde bajo techo (comportamiento esperado).

---

## v2.1 – Mensajes de recomendación (14/10)

**Qué se agregó**
- Mensaje en el Monitor Serie cada 15 segundos (o apenas cambia el color) con la recomendación de cada nivel. Ejemplos:
  - *LUZ VERDE – Radiación UV baja. Se puede salir a la calle con tranquilidad.*
  - *LUZ AMARILLA – Se puede salir, pero usando bloqueador solar, gorro y lentes de sol.*
  - *LUZ ROJA PARPADEO RÁPIDO – Radiación UV extrema. NO SE PUEDE SALIR por el alto riesgo para la salud.*

**Razón:** pasar de un color sin explicación a información que indique qué hacer (mejora 3 de la iteración 1).

---

## v2.2 – Prueba en protoboard (18/10)

**Objetivo:** ordenar las conexiones en una protoboard de 830 puntos.

**Problemas encontrados**
1. **Ancho del ESP32:** al montarlo en la protoboard quedaba ocupando de la columna A a la I, con una sola columna libre (J) por un lado y ninguna por el otro.
   - Solución: usar los pines del lado libre (D25, D26, D27, D34, GND) y alimentar el sensor desde **D32** configurado en 3,3 V, ya que el pin 3V3 quedó sin acceso.
2. **Módulos frágiles:** el sensor y el semáforo tienen los pines hacia el costado; clavados en la protoboard quedaban parados.
   - Solución: dejarlos fuera de la protoboard y conectarlos con cables hembra-macho.
3. **Lectura falsa de UV 4,0 en una pieza oscura de noche** y semáforo apagado.
   - Causa: el GND del ESP32 no estaba conectado al riel de tierra; el sensor quedaba sin referencia ("flotando") y los LEDs sin retorno.
   - Solución: corregir el cable de GND → la lectura pasó a **UV bajo**.
4. **El semáforo seguía sin encender** después de corregir el GND.
   - Diagnóstico: el sensor ya funcionaba (GND común correcto), por lo que la falla estaba en los cables del semáforo (fila incorrecta o cable dañado). No se alcanzó a confirmar cuál.

**Decisión:** volver a la conexión directa con cables hembra-hembra, que había funcionado en v2.0. Con esa conexión el semáforo y el sensor funcionaron correctamente. Evidencia: `testing/evidencias/04_prueba_protoboard.jpg`.

---

## v2.3 – Avisos al celular por WiFi (18/10)

**Qué se agregó**
- Conexión del ESP32 al WiFi (hotspot de iPhone con "Maximizar compatibilidad", 2,4 GHz).
- Bot de Telegram creado con @BotFather:
  - Aviso **"Medidor UV conectado"** al encender.
  - Aviso cada vez que cambia el nivel UV.
  - Comando `/estado` que responde con el índice UV, el color y la recomendación.
- Todo lo relacionado con Internet corre en el **otro núcleo** del ESP32, para que el semáforo siga funcionando aunque se caiga el WiFi.

**Problemas encontrados**
- El bot no respondía y el Monitor Serie mostraba errores **-11** (tiempo de espera agotado), **429** (demasiadas consultas) y **502** (servidor ocupado).
  - Solución: consultar Telegram cada **10 s** en vez de cada 3 s y aumentar el tiempo de espera de 8 a **15 s**.
- No se obtenía el chat ID desde el ESP32 por los errores anteriores.
  - Solución: obtenerlo con **@userinfobot**.

**Resultado:** avisos recibidos correctamente en el celular. Prototipo presentado el 19/10/2026.

---

## Diseño 3D (26–27/10)

- Primer modelo del encapsulado en Fusion 360: caja de 113 × 116 × 76 mm con tapa, ventilación, salida de cable, apertura para el semáforo, bandeja para el ESP32 y agujero en la tapa para el sensor. Ver `diseno_3d/`.

---

## Código de esta iteración
- Código de cada versión (v2.0, v2.1, v2.2): [`codigo/`](codigo/)
- Versión final de la iteración (v2.3): [`software/src/main.ino`](../../software/src/main.ino)
- Evolución del cableado: [`hardware/esquemas/README.md`](../../hardware/esquemas/README.md)

## Mejoras planificadas para la iteración 3
Ver [`iteracion_3/README.md`](../iteracion_3/README.md).
