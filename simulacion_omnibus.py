"""
Simulación Monte Carlo — Empresa de Ómnibus Interurbanos
Materia: Modelos, Simulación y Teoría de la Decisión
Universidad Nacional de Luján
"""

import numpy as np
import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
from cargar_config import cargar_config

cfg = cargar_config()
N     = cfg["simulacion"]["N"]
ALPHA = cfg["simulacion"]["alpha"]
np.random.seed(cfg["simulacion"]["seed"])

TRAMOS         = {int(k): v            for k, v in cfg["tramos"].items()}
MODELOS_SEMAFORO = cfg["modelos_semaforo"]
SEMAFOROS      = {int(k): v            for k, v in cfg["semaforos"].items()}
SEM_AMARILLO   = cfg["semaforo_amarillo"]
PARADAS        = {int(k): v            for k, v in cfg["paradas"].items()}
FFCC           = cfg["ffcc"]
RECORRIDO      = [(t, i) for t, i in cfg["recorrido"]]

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
    tramo = TRAMOS[t_id]
    velocidad = _muestrear(tramo["velocidades"])
    return (tramo["distancia_km"] / velocidad) * 60


def demora_semaforo(s_id):
    """Demora en minutos en un semáforo."""
    modelo = MODELOS_SEMAFORO[SEMAFOROS[s_id]]
    estado = _muestrear([(modelo["verde"], 'V'), (modelo["rojo"], 'R'), (modelo["amarillo"], 'A')])
    if estado == 'V':
        return 0.0
    if estado == 'R':
        return SEM_AMARILLO["demora_rojo_min"]
    return 0.0 if np.random.random() < SEM_AMARILLO["pasa_sin_demora"] else SEM_AMARILLO["demora_ciclo_min"]


def demora_parada(p_id):
    """Demora en minutos en una parada de pasajeros."""
    return _muestrear(PARADAS[p_id])


def demora_ffcc():
    """Demora en minutos en el cruce ferroviario."""
    if np.random.random() >= FFCC["prob_barrera_baja"]:
        return 0.0
    return _muestrear(FFCC["demoras"])


# ──────────────────────────────────────────────────────────────
# Simulación de un viaje completo
# ──────────────────────────────────────────────────────────────

def simular_viaje():
    """Retorna el tiempo total y el desglose por componente, en minutos."""
    t_tramos = t_semaforos = t_ffcc = t_paradas = 0.0
    for tipo, id_ in RECORRIDO:
        if   tipo == 'T': t_tramos    += tiempo_tramo(id_)
        elif tipo == 'S': t_semaforos += demora_semaforo(id_)
        elif tipo == 'P': t_paradas   += demora_parada(id_)
        elif tipo == 'F': t_ffcc      += demora_ffcc()
    total = t_tramos + t_semaforos + t_ffcc + t_paradas
    return total, t_tramos, t_semaforos, t_ffcc, t_paradas


# ──────────────────────────────────────────────────────────────
# Validación analítica del valor esperado
# ──────────────────────────────────────────────────────────────

def valor_esperado_analitico():
    """Calcula el E[tiempo] teórico para validar la simulación."""

    e_tramos = sum(
        sum(p * (t["distancia_km"] / v) for p, v in t["velocidades"])
        for t in TRAMOS.values()
    ) * 60

    p_pasa = SEM_AMARILLO["pasa_sin_demora"]
    e_sem = {
        m: m_cfg["rojo"] * SEM_AMARILLO["demora_rojo_min"]
           + m_cfg["amarillo"] * (p_pasa * 0.0 + (1 - p_pasa) * SEM_AMARILLO["demora_ciclo_min"])
        for m, m_cfg in MODELOS_SEMAFORO.items()
    }
    e_semaforos = sum(e_sem[SEMAFOROS[s]] for s in SEMAFOROS)

    e_ffcc = FFCC["prob_barrera_baja"] * sum(p * d for p, d in FFCC["demoras"])

    # Paradas: E[demora]
    e_paradas = sum(
        sum(p * d for p, d in dist)
        for dist in PARADAS.values()
    )

    return e_tramos, e_semaforos, e_ffcc, e_paradas


# ──────────────────────────────────────────────────────────────
# Ejecución principal
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    resultados = np.array([simular_viaje() for _ in range(N)])
    tiempos = resultados[:, 0]
    sim_t, sim_s, sim_f, sim_p = resultados[:, 1:].mean(axis=0)

    media  = np.mean(tiempos)
    desvio = np.std(tiempos, ddof=1)
    p5     = np.percentile(tiempos, int(ALPHA * 100))
    p95    = np.percentile(tiempos, int((1 - ALPHA) * 100))

    e_t, e_s, e_f, e_p = valor_esperado_analitico()
    e_total = e_t + e_s + e_f + e_p

    SEP = "=" * 58

    print(SEP)
    print("   SIMULACIÓN MONTE CARLO — ÓMNIBUS INTERURBANO")
    print(f"   N = {N} viajes  |  α = {ALPHA}  |  seed = {cfg['simulacion']['seed']}")
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
    print(f"  Tramos          : {sim_t:6.2f} min")
    print(f"  Semáforos       : {sim_s:6.2f} min")
    print(f"  Cruce FFCC      : {sim_f:6.2f} min")
    print(f"  Paradas         : {sim_p:6.2f} min")

    print("\n── Horario y percentiles (α = 0,05) ────────────────────")
    print(f"  Horario sugerido          : {round(media):.0f} min")
    print(f"  Tiempo mínimo esperado P5 : {p5:.2f} min")
    print(f"  Tiempo máximo esperado P95: {p95:.2f} min")
    print(SEP)

    # ── Visualización ────────────────────────────────────────

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    componentes = ['Tramos', 'Semáforos', 'FFCC', 'Paradas']
    colores     = ['steelblue', 'tomato', 'goldenrod', 'mediumseagreen']

    ax1 = axes[0]
    n_bins = 40
    counts, bin_edges = np.histogram(tiempos, bins=n_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width   = bin_edges[1] - bin_edges[0]

    composicion = np.zeros((n_bins, 4))
    for i in range(n_bins):
        if i < n_bins - 1:
            mask = (tiempos >= bin_edges[i]) & (tiempos < bin_edges[i + 1])
        else:
            mask = (tiempos >= bin_edges[i]) & (tiempos <= bin_edges[i + 1])
        if mask.sum() > 0:
            medias = resultados[mask, 1:].mean(axis=0)
            composicion[i] = (medias / medias.sum()) * counts[i]

    bottom = np.zeros(n_bins)
    for j, (comp, col) in enumerate(zip(componentes, colores)):
        ax1.bar(bin_centers, composicion[:, j], width=bin_width, bottom=bottom,
                color=col, edgecolor='white', linewidth=0.2, label=comp)
        bottom += composicion[:, j]

    ax1.axvline(media, color='crimson', ls='--', lw=2, label=f'Media: {media:.1f} min')
    ax1.axvline(p5,    color='black',   ls=':',  lw=2, label=f'P5  (mín): {p5:.1f} min')
    ax1.axvline(p95,   color='dimgray', ls=':',  lw=2, label=f'P95 (máx): {p95:.1f} min')
    ax1.set_xlabel('Tiempo de viaje (minutos)', fontsize=11)
    ax1.set_ylabel('Frecuencia', fontsize=11)
    ax1.set_title(f'Distribución de tiempos por componente — {N} simulaciones', fontsize=12)
    ax1.legend(fontsize=9)

    ax2 = axes[1]
    valores_anali = [e_t, e_s, e_f, e_p]
    valores_sim   = [sim_t, sim_s, sim_f, sim_p]

    bottom = 0
    for comp, val, col in zip(componentes, valores_anali, colores):
        ax2.bar('Analítico', val, bottom=bottom, color=col, label=f'{comp}: {val:.1f} min')
        bottom += val

    bottom = 0
    for val, col in zip(valores_sim, colores):
        ax2.bar('Simulado', val, bottom=bottom, color=col)
        bottom += val

    ax2.set_ylabel('Minutos', fontsize=11)
    ax2.set_title('E[tiempo] analítico vs media simulada (por componente)', fontsize=12)
    ax2.legend(fontsize=9, loc='upper right')

    plt.suptitle('Simulación Monte Carlo — Ómnibus Interurbano | UNLu', fontsize=13, y=0.95)
    plt.tight_layout()
    plt.show()
