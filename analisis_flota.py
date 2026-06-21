"""
Análisis de flota requerida según frecuencia y percentil de tiempo de viaje.
"""
import numpy as np
from cargar_config import cargar_config
from simulacion_omnibus import simular_viaje

cfg = cargar_config()
N = cfg["simulacion"]["N"]
np.random.seed(cfg["simulacion"]["seed"])

resultados = np.array([simular_viaje() for _ in range(N)])
tiempos = resultados[:, 0]

media = np.mean(tiempos)
desvio = np.std(tiempos, ddof=1)
p50 = np.percentile(tiempos, 50)
p75 = np.percentile(tiempos, 75)
p85 = np.percentile(tiempos, 85)
p90 = np.percentile(tiempos, 90)
p95 = np.percentile(tiempos, 95)
p99 = np.percentile(tiempos, 99)

# ── Tabla de flota ────────────────────────────────────────

HEADWAYS = [15, 20, 25, 30, 45, 60]
PERCENTILES = [
    ("Media", round(media)),
    ("P50", round(p50)),
    ("P75", round(p75)),
    ("P85", round(p85)),
    ("P90", round(p90)),
    ("P95", round(p95)),
]

print("=" * 65)
print("   ANÁLISIS DE FLOTA — Unidades necesarias por frecuencia")
print(f"   Tiempo de viaje: {media:.1f} ± {desvio:.1f} min  (N = {N})")
print("=" * 65)
print()
print(f"{'Criterio':>8}  {'T. ciclo':>9}  ", end="")
for h in HEADWAYS:
    print(f"{'c/' + str(h) + 'min':>9}", end="")
print()
print(f"{'─' * 8}  {'─' * 9}  " + "  ".join(["─" * 9] * len(HEADWAYS)))

for nombre, ciclo in PERCENTILES:
    print(f"{nombre:>8}  {ciclo:>4} min    ", end="")
    for h in HEADWAYS:
        unidades = int(np.ceil(ciclo / h))
        print(f"{unidades:>9}", end="")
    print()

# ── Interpretación ────────────────────────────────────────
print()
print("─" * 65)
print("  Ej: si el criterio es P95 (ciclo ≈ 129 min) y se")
print("  desea frecuencia cada 30 min, se necesitan")
print(f"  ceil(129/30) = {int(np.ceil(129/30))} unidades.")
print("─" * 65)
