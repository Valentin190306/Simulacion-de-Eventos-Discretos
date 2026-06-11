"""
Simulación Monte Carlo — Empresa de Ómnibus Interurbanos
Materia: Modelos, Simulación y Teoría de la Decisión
Universidad Nacional de Luján
"""

import numpy as np
import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────
# Parámetros generales
# ──────────────────────────────────────────────────────────────
N     = 1000
ALPHA = 0.05
np.random.seed(42)

# ──────────────────────────────────────────────────────────────
# Datos del modelo
# ──────────────────────────────────────────────────────────────

# Tramos: {id: (distancia_km, v_normal[P=0.7], v_p02[P=0.2], v_p01[P=0.1])}
TRAMOS = {
     1: ( 3, 30, 40, 20),
     2: ( 5, 40, 45, 30),
     3: ( 5, 40, 50, 40),
     4: ( 1, 30, 40, 10),
     5: ( 4, 40, 40, 40),
     6: ( 2, 10, 30, 40),
     7: ( 5, 40, 45, 30),
     8: (10, 30, 40, 60),
     9: (20, 50, 55, 40),
    10: ( 5, 30, 30, 30),
    11: ( 1, 30, 35, 30),
    12: ( 1, 30, 35, 20),
    13: ( 1, 30, 35, 10),
}

# Modelos de semáforo: {modelo: (p_verde, p_rojo, p_amarillo)}
MODELOS_SEMAFORO = {
    'A': (0.40, 0.50, 0.10),
    'B': (0.30, 0.60, 0.10),
    'C': (0.60, 0.30, 0.10),
}

# Asignación semáforos a modelo: {num_semaforo: modelo}
SEMAFOROS = {
    1: 'A', 2: 'A', 3: 'A',
    4: 'B', 6: 'B', 8: 'B',
    5: 'C', 7: 'C',
}

# Demoras en paradas: {id_parada: [(prob, minutos), ...]}
PARADAS = {
    1: [(0.4, 1.0), (0.3, 2.0), (0.2, 3.0), (0.1, 4.0)],
    2: [(0.4, 0.5), (0.3, 2.0), (0.2, 3.0), (0.1, 4.0)],
    3: [(0.4, 0.0), (0.3, 1.0), (0.2, 2.0), (0.1, 3.0)],
    4: [(0.4, 3.0), (0.3, 4.0), (0.2, 5.0), (0.1, 6.0)],
}

# Demoras FFCC dado barrera baja: [(prob, minutos), ...]
FFCC_DEMORAS = [(0.6, 3.0), (0.3, 1.5), (0.1, 5.0)]

# Secuencia del recorrido: (tipo, id)
#   T = tramo, S = semáforo, P = parada, F = cruce ferroviario
RECORRIDO = [
    ('T', 1), ('S', 1),
    ('T', 2), ('S', 2),
    ('T', 3), ('P', 1),
    ('T', 4), ('S', 3),
    ('T', 5), ('P', 2),
    ('T', 6), ('S', 4),
    ('T', 7), ('S', 5),
    ('T', 8), ('P', 3),
    ('T', 9), ('S', 6),
    ('T',10), ('S', 7),
    ('T',11), ('F', 0),
    ('S', 8),
    ('T',12), ('P', 4),
    ('T',13),
]

# ──────────────────────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────────────────────

def _muestrear(distribucion):
    """Muestrea un valor de una distribución discreta [(prob, valor), ...]."""
    r = np.random.random()
    acum = 0.0
    for prob, valor in distribucion:
        acum += prob
        if r < acum:
            return valor
    return distribucion[-1][1]


def tiempo_tramo(t_id):
    """Tiempo de viaje en minutos para un tramo (velocidad aleatoria)."""
    d, v0, v1, v2 = TRAMOS[t_id]
    velocidad = _muestrear([(0.7, v0), (0.2, v1), (0.1, v2)])
    return (d / velocidad) * 60


def demora_semaforo(s_id):
    """Demora en minutos en un semáforo."""
    p_v, p_r, p_a = MODELOS_SEMAFORO[SEMAFOROS[s_id]]
    estado = _muestrear([(p_v, 'V'), (p_r, 'R'), (p_a, 'A')])
    if estado == 'V':
        return 0.0
    if estado == 'R':
        return 1.0
    # Amarillo: 50% pasa sin demora, 50% pierde ciclo completo (2 min)
    return 0.0 if np.random.random() < 0.5 else 2.0


def demora_parada(p_id):
    """Demora en minutos en una parada de pasajeros."""
    return _muestrear(PARADAS[p_id])


def demora_ffcc():
    """Demora en minutos en el cruce ferroviario."""
    if np.random.random() >= 0.2:   # 80%: barrera levantada
        return 0.0
    return _muestrear(FFCC_DEMORAS) # 20%: barrera baja → demora variable


# ──────────────────────────────────────────────────────────────
# Simulación de un viaje completo
# ──────────────────────────────────────────────────────────────

def simular_viaje():
    """Retorna el tiempo total de un viaje en minutos."""
    total = 0.0
    for tipo, id_ in RECORRIDO:
        if   tipo == 'T': total += tiempo_tramo(id_)
        elif tipo == 'S': total += demora_semaforo(id_)
        elif tipo == 'P': total += demora_parada(id_)
        elif tipo == 'F': total += demora_ffcc()
    return total


# ──────────────────────────────────────────────────────────────
# Validación analítica del valor esperado
# ──────────────────────────────────────────────────────────────

def valor_esperado_analitico():
    """Calcula el E[tiempo] teórico para validar la simulación."""

    # Segmentos: E[t] = sum_i P_i * (d / v_i)
    e_tramos = sum(
        0.7*(d/v0) + 0.2*(d/v1) + 0.1*(d/v2)
        for d, v0, v1, v2 in TRAMOS.values()
    ) * 60  # horas → minutos

    # Semáforos: E[demora] por modelo
    e_sem = {
        m: p_r * 1.0 + p_a * (0.5 * 0.0 + 0.5 * 2.0)
        for m, (p_v, p_r, p_a) in MODELOS_SEMAFORO.items()
    }
    e_semaforos = sum(e_sem[SEMAFOROS[s]] for s in SEMAFOROS)

    # FFCC: E[demora]
    e_ffcc = 0.2 * sum(p * d for p, d in FFCC_DEMORAS)

    # Paradas: E[demora]
    e_paradas = sum(
        sum(p * d for p, d in dist)
        for dist in PARADAS.values()
    )

    return e_tramos, e_semaforos, e_ffcc, e_paradas


# ──────────────────────────────────────────────────────────────
# Ejecución principal
# ──────────────────────────────────────────────────────────────

tiempos = np.array([simular_viaje() for _ in range(N)])

media  = np.mean(tiempos)
desvio = np.std(tiempos, ddof=1)
p5     = np.percentile(tiempos, int(ALPHA * 100))
p95    = np.percentile(tiempos, int((1 - ALPHA) * 100))

e_t, e_s, e_f, e_p = valor_esperado_analitico()
e_total = e_t + e_s + e_f + e_p

# ──────────────────────────────────────────────────────────────
# Salida por consola
# ──────────────────────────────────────────────────────────────

SEP = "=" * 58

print(SEP)
print("   SIMULACIÓN MONTE CARLO — ÓMNIBUS INTERURBANO")
print(f"   N = {N} viajes  |  α = {ALPHA}  |  seed = 42")
print(SEP)

print("\n── Descomposición del E[tiempo] analítico ──────────────")
print(f"  Tramos          : {e_t:6.2f} min")
print(f"  Semáforos       : {e_s:6.2f} min")
print(f"  Cruce FFCC      : {e_f:6.2f} min")
print(f"  Paradas         : {e_p:6.2f} min")
print(f"  TOTAL analítico : {e_total:6.2f} min  ({e_total/60:.2f} h)")

print("\n── Resultados de la simulación ─────────────────────────")
print(f"  Media simulada  : {media:6.2f} min  ({media/60:.2f} h)")
print(f"  Desvío estándar : {desvio:6.2f} min")
print(f"  Error vs E[X]   : {abs(media - e_total):6.2f} min")

print("\n── Horario y percentiles (α = 0,05) ────────────────────")
print(f"  Horario sugerido          : {round(media):.0f} min")
print(f"  Tiempo mínimo esperado P5 : {p5:.2f} min")
print(f"  Tiempo máximo esperado P95: {p95:.2f} min")
print(SEP)

# ──────────────────────────────────────────────────────────────
# Visualización
# ──────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# — Histograma de distribución —
ax1 = axes[0]
ax1.hist(tiempos, bins=40, color='steelblue', edgecolor='white', alpha=0.85, label='Viajes simulados')
ax1.axvline(media, color='crimson',    ls='--', lw=2, label=f'Media: {media:.1f} min')
ax1.axvline(p5,    color='seagreen',   ls=':',  lw=2, label=f'P5  (mín): {p5:.1f} min')
ax1.axvline(p95,   color='darkorange', ls=':',  lw=2, label=f'P95 (máx): {p95:.1f} min')
ax1.set_xlabel('Tiempo de viaje (minutos)', fontsize=11)
ax1.set_ylabel('Frecuencia', fontsize=11)
ax1.set_title(f'Distribución de tiempos — {N} simulaciones', fontsize=12)
ax1.legend(fontsize=10)

# — Comparación analítico vs simulado (barras apiladas del E[X]) —
ax2 = axes[1]
componentes   = ['Tramos', 'Semáforos', 'FFCC', 'Paradas']
valores_anali = [e_t, e_s, e_f, e_p]
colores       = ['steelblue', 'tomato', 'goldenrod', 'mediumseagreen']

bottom = 0
for comp, val, col in zip(componentes, valores_anali, colores):
    ax2.bar('Analítico', val, bottom=bottom, color=col, label=f'{comp}: {val:.1f} min')
    bottom += val

ax2.bar('Simulado', media, color='slategray', alpha=0.7, label=f'Media sim.: {media:.1f} min')
ax2.set_ylabel('Minutos', fontsize=11)
ax2.set_title('E[tiempo] analítico vs media simulada', fontsize=12)
ax2.legend(fontsize=9, loc='upper right')

plt.suptitle('Simulación Monte Carlo — Ómnibus Interurbano | UNLu', fontsize=13, y=1.01)
plt.tight_layout()
plt.show()
