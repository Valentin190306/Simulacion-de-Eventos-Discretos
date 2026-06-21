"""
Generación de horarios de servicio para la empresa de ómnibus.
Usa el P95 de la simulación como tiempo de ciclo (RTT).
"""

import numpy as np
import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from cargar_config import cargar_config
from simulacion_omnibus import simular_viaje


def _min(s):
    h, m = map(int, s.split(":"))
    return h * 60 + m


def _hora(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def generar_horario(frecuencia_min=30, inicio="06:00", fin="22:00", descanso_min=10):
    cfg = cargar_config()
    np.random.seed(cfg["simulacion"]["seed"])

    resultados = np.array(
        [simular_viaje() for _ in range(cfg["simulacion"]["N"])]
    )
    p95 = np.percentile(resultados[:, 0], 95)
    ciclo = int(np.ceil(p95))

    ciclo_con_descanso = ciclo + descanso_min
    unidades = int(np.ceil(ciclo_con_descanso / frecuencia_min))
    turno = unidades * frecuencia_min
    descanso_real = turno - ciclo
    t_ini = _min(inicio)
    t_fin = _min(fin)

    print("=" * 68)
    print("   HORARIO DE SERVICIOS — ÓMNIBUS INTERURBANO")
    print("=" * 68)
    print(f"  Tiempo de ciclo (P95) : {ciclo} min  ({ciclo // 60:02d}:{ciclo % 60:02d} h)")
    print(f"  Descanso mínimo      : {descanso_min} min por vuelta")
    print(f"  Frecuencia            : cada {frecuencia_min} min")
    print(f"  Unidades necesarias   : {unidades}")
    print(f"  Turno por unidad      : cada {turno} min  ({turno // 60}:{turno % 60:02d} h)")
    print(f"  Descanso real         : {descanso_real} min por vuelta")
    if descanso_real < descanso_min:
        print(f"  ⚠ Descanso insuficiente (mínimo {descanso_min} min). Aumentar frecuencia o unidades.")
    total_salidas = 0

    for u in range(unidades):
        t = t_ini + u * frecuencia_min
        salidas = []
        while t < t_fin:
            salidas.append(t)
            t += turno
        total_salidas += len(salidas)

        print()
        print(f"  Unidad {u + 1} ───────────────────────────────────────")
        for i in range(0, len(salidas), 6):
            print("    " + "  |  ".join(_hora(s) for s in salidas[i:i + 6]))

    t_ultima = t_ini + (total_salidas - 1) * frecuencia_min + ciclo
    print()
    print(f"  Total de servicios    : {total_salidas}")
    print(f"  Última llegada aprox. : {_hora(t_ultima)}")
    print("=" * 68)

    return {
        "ciclo": ciclo,
        "descanso_min": descanso_min,
        "descanso_real": descanso_real,
        "frecuencia_min": frecuencia_min,
        "unidades": unidades,
        "turno": turno,
        "t_ini": t_ini,
        "t_fin": t_fin,
        "total_salidas": total_salidas,
        "t_ultima": t_ultima,
    }


def graficar_horario(info):
    ciclo = info["ciclo"]
    frecuencia_min = info["frecuencia_min"]
    unidades = info["unidades"]
    turno = info["turno"]
    t_ini = info["t_ini"]
    t_fin = info["t_fin"]

    fig, ax = plt.subplots(figsize=(14, max(4, unidades * 0.7)))

    colores = plt.colormaps["tab10"]
    h_ini = t_ini / 60
    h_fin = t_fin / 60

    for u in range(unidades):
        t = t_ini + u * frecuencia_min
        viajes = []
        while t < t_fin:
            viajes.append(t)
            t += turno
        n = len(viajes)
        y = unidades - u
        color = colores(u % 10)
        for i, t_part in enumerate(viajes):
            t_lleg = t_part + ciclo
            ax.barh(y, (t_lleg - t_part) / 60, left=t_part / 60,
                    height=0.55, color=color, edgecolor="white",
                    linewidth=0.5, alpha=0.85, zorder=3)
            if n <= 6:
                ax.text((t_part + t_lleg) / 2 / 60, y, _hora(t_part),
                        ha="center", va="center", fontsize=7, color="white",
                        fontweight="bold")

    ax.set_yticks(range(1, unidades + 1))
    ax.set_yticklabels([f"Unidad {u}" for u in range(unidades, 0, -1)], fontsize=10)
    ax.set_xlabel("Hora del día", fontsize=11)
    ax.set_xlim(h_ini, h_fin + 0.5)
    ax.set_xticks(range(int(h_ini), int(h_fin) + 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(int(h_ini), int(h_fin) + 2)],
                       fontsize=9, rotation=30)
    ax.grid(axis="x", alpha=0.3, zorder=0)
    ax.grid(axis="y", alpha=0.15, zorder=0)
    ax.set_axisbelow(True)

    ax.text(0.02, 0.97,
            f"Frecuencia: cada {frecuencia_min} min  |  "
            f"Ciclo (P95): {ciclo} min  |  "
            f"{unidades} unidades  |  "
            f"Descanso: {info['descanso_real']} min/vuelta  |  "
            f"Servicios: {info['total_salidas']}",
            transform=ax.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                      edgecolor="gray", alpha=0.9))

    fig.suptitle("Programación de Horarios — Ómnibus Interurbano",
                 fontsize=13, y=0.95)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Generar horario de servicio")
    parser.add_argument("--frecuencia", type=int, default=30, help="Frecuencia en minutos")
    parser.add_argument("--descanso", type=int, default=10, help="Descanso mínimo en terminal (min)")
    parser.add_argument("--inicio", default="06:00", help="Inicio del servicio")
    parser.add_argument("--fin", default="22:00", help="Fin del servicio")
    parser.add_argument("--no-plot", action="store_true", help="Solo texto, sin gráfico")
    args = parser.parse_args()

    info = generar_horario(args.frecuencia, args.inicio, args.fin, args.descanso)
    if not args.no_plot:
        graficar_horario(info)
