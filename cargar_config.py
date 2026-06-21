import json

CLAVES_OBLIGATORIAS = [
    "simulacion", "tramos", "modelos_semaforo", "semaforos",
    "semaforo_amarillo", "paradas", "ffcc", "recorrido",
]


def _validar_estructura(cfg):
    for key in CLAVES_OBLIGATORIAS:
        if key not in cfg:
            raise ValueError(f"Falta clave obligatoria en config: '{key}'")

    sim = cfg["simulacion"]
    if not isinstance(sim.get("N"), int) or sim["N"] <= 0:
        raise ValueError("simulacion.N debe ser un entero positivo")
    if not (0 < sim.get("alpha", 0) < 1):
        raise ValueError("simulacion.alpha debe estar entre 0 y 1")

    for k, v in cfg["tramos"].items():
        d = v["distancia_km"]
        probs = [p for p, _ in v["velocidades"]]
        if abs(sum(probs) - 1.0) > 1e-9:
            raise ValueError(f"tramos[{k}]: probabilidades no suman 1")

    for modelo, probs in cfg["modelos_semaforo"].items():
        if abs(sum(probs.values()) - 1.0) > 1e-9:
            raise ValueError(f"modelos_semaforo[{modelo}]: probabilidades no suman 1")

    for k, dist in cfg["paradas"].items():
        probs = [p for p, _ in dist]
        if abs(sum(probs) - 1.0) > 1e-9:
            raise ValueError(f"paradas[{k}]: probabilidades no suman 1")

    probs_ffcc = [p for p, _ in cfg["ffcc"]["demoras"]]
    if abs(sum(probs_ffcc) - 1.0) > 1e-9:
        raise ValueError("ffcc.demoras: probabilidades no suman 1")

    tipos_validos = {"T", "S", "P", "F"}
    for i, (tipo, _) in enumerate(cfg["recorrido"]):
        if tipo not in tipos_validos:
            raise ValueError(f"recorrido[{i}]: tipo '{tipo}' inválido")


def cargar_config(ruta="config.json"):
    with open(ruta, encoding="utf-8") as f:
        cfg = json.load(f)
    _validar_estructura(cfg)
    return cfg
