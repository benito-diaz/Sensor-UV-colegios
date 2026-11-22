"""
Analiza los datos de las pruebas P1 y P2 (testing/reportes/protocolo_pruebas.md).

Uso:
  python3 analizar_datos.py lecturas_uv.csv          # CSV descargado de /api/exportar.csv
  python3 analizar_datos.py --log log_serial.txt     # texto copiado del Monitor Serie

Solo usa la librería estándar de Python.
"""
import csv, re, sys
from datetime import datetime
from statistics import mean, median

INTERVALO_S = 10      # el ESP32 envía cada 10 s
HUECO_S = 60          # más de 60 s sin datos se considera un corte
NIVELES = ["BAJO", "MODERADO", "ALTO", "MUY ALTO", "EXTREMO"]


def analizar_csv(ruta):
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    if not filas:
        print("El CSV no tiene lecturas."); return
    t = [datetime.strptime(f["fecha_chile"], "%Y-%m-%d %H:%M:%S") for f in filas]
    uv = [float(f["indice_uv"]) for f in filas]
    mv = [int(f["milivoltios"]) for f in filas]
    nivel = [f["nivel"] for f in filas]

    dur = (t[-1] - t[0]).total_seconds()
    esperadas = int(dur // INTERVALO_S) + 1
    difs = [(t[i + 1] - t[i]).total_seconds() for i in range(len(t) - 1)]
    huecos = [(t[i], d) for i, d in enumerate(difs) if d > HUECO_S]

    minutos = {n: 0.0 for n in NIVELES}
    for i, d in enumerate(difs):
        minutos[nivel[i]] += min(d, HUECO_S) / 60
    alertas = sum(1 for i in range(1, len(nivel))
                  if NIVELES.index(nivel[i]) >= 2 and NIVELES.index(nivel[i - 1]) < 2)
    imax = max(range(len(uv)), key=lambda i: uv[i])

    print(f"Periodo: {t[0]} -> {t[-1]} ({dur/60:.1f} min)")
    print(f"Lecturas recibidas: {len(filas)} de {esperadas} esperadas ({100*len(filas)/esperadas:.1f} %)")
    print(f"Intervalo entre lecturas: mediana {median(difs):.1f} s, máximo {max(difs):.1f} s" if difs else "")
    print(f"Huecos > {HUECO_S} s: {len(huecos)}" + "".join(f"\n  {h} ({d:.0f} s)" for h, d in huecos))
    print(f"Índice UV: mínimo {min(uv):.2f}, promedio {mean(uv):.2f}, máximo {uv[imax]:.2f} a las {t[imax].time()}")
    print(f"Sensor: {min(mv)} – {max(mv)} mV")
    print("Minutos por nivel: " + ", ".join(f"{n} {m:.1f}" for n, m in minutos.items()))
    print(f"Alertas (subidas a ALTO o más): {alertas}")


def analizar_log(ruta):
    patron = re.compile(r"\[Nube\] POST .* -> (-?\d+) \((\d+) ms\)")
    codigos, lat = [], []
    for linea in open(ruta, encoding="utf-8", errors="ignore"):
        m = patron.search(linea)
        if m:
            codigos.append(int(m.group(1))); lat.append(int(m.group(2)))
    if not codigos:
        print("No se encontraron líneas [Nube] POST en el log."); return
    ok = [l for c, l in zip(codigos, lat) if c == 201]
    print(f"Envíos: {len(codigos)} · 201: {len(ok)} ({100*len(ok)/len(codigos):.1f} %)")
    otros = sorted(set(c for c in codigos if c != 201))
    if otros:
        print("Otros códigos: " + ", ".join(f"{c} ×{codigos.count(c)}" for c in otros))
    if ok:
        s = sorted(ok)
        print(f"Latencia (201): media {mean(ok):.0f} ms, mediana {median(ok):.0f} ms, "
              f"p95 {s[min(len(s)-1, -(-95*len(s)//100)-1)]} ms, máx {max(ok)} ms")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--log":
        analizar_log(sys.argv[2])
    elif len(sys.argv) == 2:
        analizar_csv(sys.argv[1])
    else:
        print(__doc__)
