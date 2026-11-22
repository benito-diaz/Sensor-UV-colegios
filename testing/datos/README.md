# Datos de las pruebas

| Archivo | Contenido |
|---|---|
| `analizar_datos.py` | Calcula tasa de captura, huecos, máximo, minutos por nivel, alertas (desde el CSV) y tasa de éxito y latencia (desde el log del Monitor Serie) |
| `lecturas_uv_<fecha>.csv` | Datos reales descargados del panel (`/api/exportar.csv`) – agregar |
| `log_serial_<fecha>.txt` | Texto copiado del Monitor Serie durante la prueba – agregar |

Uso:
```bash
python3 analizar_datos.py lecturas_uv_2026-11-22.csv
python3 analizar_datos.py --log log_serial_2026-11-22.txt
```
