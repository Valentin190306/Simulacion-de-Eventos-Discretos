"""
Simulación DES secuencial — Empresa de Ómnibus Interurbanos
Materia: Modelos, Simulación y Teoría de la Decisión
Universidad Nacional de Luján

Enfoque de Simulación de Eventos Discretos (DES) secuencial:
  - Se mantiene un reloj (clock) que avanza con cada evento del recorrido.
  - Cada elemento (tramo, semáforo, parada, FFCC) se modela como un evento
    con tiempo de llegada y tiempo de salida.
  - El estado del sistema (posición del bus, tiempo transcurrido) evoluciona
    secuencialmente a medida que se procesan los eventos.
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

TRAMOS          = {int(k): v            for k, v in cfg["tramos"].items()}
MODELOS_SEMAFORO = cfg["modelos_semaforo"]
SEMAFOROS       = {int(k): v            for k, v in cfg["semaforos"].items()}
SEM_AMARILLO    = cfg["semaforo_amarillo"]
PARADAS         = {int(k): v            for k, v in cfg["paradas"].items()}
FFCC            = cfg["ffcc"]
RECORRIDO       = [(t, i) for t, i in cfg["recorrido"]]

# ──────────────────────────────────────────────────────────────
# Funciones auxiliares de muestreo
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
    tramo = TRAMOS[t_id]
    velocidad = _muestrear(tramo["velocidades"])
    return (tramo["distancia_km"] / velocidad) * 60


def demora_semaforo(s_id):
    modelo = MODELOS_SEMAFORO[SEMAFOROS[s_id]]
    estado = _muestrear([(modelo["verde"], 'V'), (modelo["rojo"], 'R'), (modelo["amarillo"], 'A')])
    if estado == 'V':
        return 0.0
    if estado == 'R':
        return SEM_AMARILLO["demora_rojo_min"]
    return 0.0 if np.random.random() < SEM_AMARILLO["pasa_sin_demora"] else SEM_AMARILLO["demora_ciclo_min"]


def demora_parada(p_id):
    return _muestrear(PARADAS[p_id])


def demora_ffcc():
    if np.random.random() >= FFCC["prob_barrera_baja"]:
        return 0.0
    return _muestrear(FFCC["demoras"])


# ──────────────────────────────────────────────────────────────
# Manejadores de eventos (DES pattern)
# ──────────────────────────────────────────────────────────────

def procesar_tramo(clock, t_id):
    demora = tiempo_tramo(t_id)
    t_salida = clock + demora
    return t_salida, demora


def procesar_semaforo(clock, s_id):
    demora = demora_semaforo(s_id)
    t_salida = clock + demora
    return t_salida, demora


def procesar_parada(clock, p_id):
    demora = demora_parada(p_id)
    t_salida = clock + demora
    return t_salida, demora


def procesar_ffcc(clock):
    demora = demora_ffcc()
    t_salida = clock + demora
    return t_salida, demora


# ──────────────────────────────────────────────────────────────
# DES secuencial — Simulación de un viaje
# ──────────────────────────────────────────────────────────────

def _etiqueta_evento(tipo, id_):
    etiquetas = {
        'T': f'Tramo {id_}',
        'S': f'Semáforo {id_}',
        'P': f'Parada {id_}',
        'F': 'Cruce FFCC',
    }
    return etiquetas.get(tipo, f'Evento {tipo}{id_}')


def _handler(tipo, id_):
    handlers = {
        'T': procesar_tramo,
        'S': procesar_semaforo,
        'P': procesar_parada,
        'F': lambda clock, _: procesar_ffcc(clock),
    }
    return handlers[tipo]


def simular_viaje_des(verbose=False):
    """
    Simula un viaje completo con DES secuencial.

    El reloj (clock) representa el tiempo de simulación actual.
    Cada evento recibe el clock, lo avanza según su demora,
    y devuelve el nuevo tiempo. Esto refleja cómo el estado del
    sistema (posición del bus, tiempo transcurrido) evoluciona
    secuencialmente.
    """
    clock = 0.0
    eventos = []
    t_tramos = t_semaforos = t_ffcc = t_paradas = 0.0

    for tipo, id_ in RECORRIDO:
        handler = _handler(tipo, id_)
        t_llegada = clock
        t_salida, demora = handler(clock, id_)
        clock = t_salida

        if   tipo == 'T': t_tramos    += demora
        elif tipo == 'S': t_semaforos += demora
        elif tipo == 'P': t_paradas   += demora
        elif tipo == 'F': t_ffcc      += demora

        if verbose:
            eventos.append((t_llegada, t_salida, demora, tipo, id_))

    if verbose:
        print("  DES — Traza de eventos del viaje:")
        print(f"  {'Llegada':>8} {'Salida':>8} {'Demora':>7}  {'Evento':<20}")
        print(f"  {'───────':>8} {'───────':>8} {'──────':>7}  {'──────':<20}")
        for llegada, salida, demora, tipo, id_ in eventos:
            print(f"  {llegada:8.2f} {salida:8.2f} {demora:7.2f}  {_etiqueta_evento(tipo, id_):<20}")
        print(f"  {'───────':>8} {'───────':>8} {'──────':>7}  {'──────':<20}")
        print(f"  {clock:8.2f}  {'(total viaje)':>15}\n")

    total = clock
    return total, t_tramos, t_semaforos, t_ffcc, t_paradas


# ──────────────────────────────────────────────────────────────
# Validación analítica del valor esperado
# ──────────────────────────────────────────────────────────────

def valor_esperado_analitico():
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

    e_paradas = sum(
        sum(p * d for p, d in dist)
        for dist in PARADAS.values()
    )

    return e_tramos, e_semaforos, e_ffcc, e_paradas


# ──────────────────────────────────────────────────────────────
# Ejecución principal
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 62)
    print("   SIMULACIÓN DES SECUENCIAL — ÓMNIBUS INTERURBANO")
    print(f"   N = {N} viajes  |  α = {ALPHA}  |  seed = {cfg['simulacion']['seed']}")
    print("=" * 62)

    print("\n▸ Traza de eventos — primeros 3 viajes:\n")
    for i in range(3):
        print(f"  Viaje #{i + 1} ───────────────────────────────")
        simular_viaje_des(verbose=True)

    resultados = np.array([simular_viaje_des() for _ in range(N)])
    tiempos = resultados[:, 0]
    sim_t, sim_s, sim_f, sim_p = resultados[:, 1:].mean(axis=0)

    media  = np.mean(tiempos)
    desvio = np.std(tiempos, ddof=1)
    p5     = np.percentile(tiempos, int(ALPHA * 100))
    p95    = np.percentile(tiempos, int((1 - ALPHA) * 100))

    e_t, e_s, e_f, e_p = valor_esperado_analitico()
    e_total = e_t + e_s + e_f + e_p

    print("── Resultados de la simulación DES ─────────────────----")
    print(f"  Media simulada  : {media:7.2f} min  ({media/60:.2f} h)")
    print(f"  Desvío estándar : {desvio:7.2f} min")
    print(f"  Tramos          : {sim_t:7.2f} min")
    print(f"  Semáforos       : {sim_s:7.2f} min")
    print(f"  Cruce FFCC      : {sim_f:7.2f} min")
    print(f"  Paradas         : {sim_p:7.2f} min")
    print()
    print("── Validación analítica ───────────────────────────────")
    print(f"  E[tiempo] analítico : {e_total:7.2f} min  ({e_total/60:.2f} h)")
    print(f"  Error vs E[X]       : {abs(media - e_total):7.2f} min")
    print()
    print(f"── Horario sugerido (α = {ALPHA}) ─────────────────────")
    print(f"  Horario estimado                : {round(media):.0f} min")
    print(f"  Tiempo mínimo esperado (P{int(ALPHA*100):02d}) : {p5:7.2f} min")
    print(f"  Tiempo máximo esperado (P{int((1-ALPHA)*100):02d}): {p95:7.2f} min")
    print("=" * 62)

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
    total_anali   = sum(valores_anali)
    total_sim     = sum(valores_sim)

    bottom = 0
    for comp, val, col in zip(componentes, valores_anali, colores):
        ax2.bar('Analítico', val, bottom=bottom, color=col, label=f'{comp}: {val:.1f} min')
        bottom += val

    bottom = 0
    for val, col in zip(valores_sim, colores):
        ax2.bar('Simulado', val, bottom=bottom, color=col)
        bottom += val

    # Totales sobre cada barra
    ax2.text(0, total_anali + 0.5, f'{total_anali:.2f} min',
             ha='center', va='bottom', fontweight='bold')
    ax2.text(1, total_sim + 0.5, f'{total_sim:.2f} min',
             ha='center', va='bottom', fontweight='bold')

    # Diferencia
    diff = abs(total_anali - total_sim)
    ax2.text(0.5, max(total_anali, total_sim) + 3,
             f'Diferencia: {diff:.2f} min  ({diff / max(total_anali, total_sim) * 100:.2f}%)',
             ha='center', va='bottom', fontsize=9, style='italic',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    # Componentes dentro de cada segmento
    for i, val in enumerate(valores_anali):
        y = sum(valores_anali[:i]) + val / 2
        ax2.text(0, y, f'{val:.1f}', ha='center', va='center',
                 fontsize=7, color='white', fontweight='bold')
    for i, val in enumerate(valores_sim):
        y = sum(valores_sim[:i]) + val / 2
        ax2.text(1, y, f'{val:.1f}', ha='center', va='center',
                 fontsize=7, color='white', fontweight='bold')

    ax2.set_ylabel('Minutos', fontsize=11)
    ax2.set_title('E[tiempo] analítico vs media simulada (por componente)', fontsize=12)
    ax2.legend(fontsize=9, loc='upper right')

    plt.suptitle('Simulación DES Secuencial — Ómnibus Interurbano | UNLu', fontsize=13, y=0.95)
    plt.tight_layout()
    plt.show()
