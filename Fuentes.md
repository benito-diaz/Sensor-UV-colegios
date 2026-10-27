# Fuentes del Proyecto
## Librerias utilizadas
| Libreria | Version | Fuente |
| - - - - - - - - - - - - - - -| - - - - - - - - -| - - - - - - - - - - - - - - - - - - - - -|
| DHT sensor | 1.4.4 | github . com / adafruit |
| FirebaseESP32 | 4.3.0 | github . com / mobizt |
## Codigo externo adaptado
### reconexion WiFi ( main . ino , lineas 45 -62)
- Fuente : randomnerdtutorials . com
- Adaptacion : espera 500 ms -> 2000 ms ;
reintentos maximos (5) .
## Uso de Inteligencia Artificial
### promedio movil ( main . ino , lineas 78 -95)
- Herramienta : ChatGPT -4 o ( mayo 2026)
- Prompt : " funcion C ++ Arduino para promedio
movil de las ultimas 10 lecturas "
- Adaptacion : buffer de 10 a 5 muestras .
- Comprension : arreglo circular , media
aritmetica por iteracion .
