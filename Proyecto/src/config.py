# src/config.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math
 

# -----------------------------
# Especificación de distribuciones (para SciPy después)
# -----------------------------
@dataclass(frozen=True)
class DistSpec:
    """
    Representa una distribución de SciPy.
    name: nombre en scipy.stats (ej: "expon", "norm", "triang", "lognorm", "gamma", "poisson"...)
    shape: parámetros de forma (si aplica), en orden.
    loc, scale: parámetros loc/scale (si aplica).
    units: "min" normalmente (para que no se confundan tiempos).
    """
    name: str
    shape: Tuple[float, ...] = ()
    loc: float = 0.0
    scale: float = 1.0
    units: str = "min"


@dataclass(frozen=True)
class OrderType:
    """
    Un tipo de pedido y las estaciones que requiere (además de CAJA).
    prob: probabilidad de ese pedido (deben sumar 1.0 entre todos).
    stations: estaciones extra requeridas luego de caja.
    """
    name: str
    prob: float
    stations: Tuple[str, ...]


@dataclass(frozen=True)
class SystemCosts:
    # costo por unidad de equipo (según enunciado)
    cost_per_server: Dict[str, float]


@dataclass(frozen=True)
class SimulationSettings:
    # Ajustable luego: cantidad de clientes o tiempo total, warmup y repeticiones
    n_customers: int = 2000
    warmup_customers: int = 200
    replications: int = 30
    seed: int = 12345


@dataclass(frozen=True)
class ModelConfig:
    arrival_dist: DistSpec
    service_dists: Dict[str, DistSpec]  # por estación
    order_types: List[OrderType]
    costs: SystemCosts
    settings: SimulationSettings

    # objetivos del enunciado
    wait_threshold_minutes: float = 3.0


# Estaciones (constantes)
CAJA = "caja"
FREIDORA = "freidora"
REFRESCOS = "refrescos"
POLLO = "pollo"

ALL_STATIONS = (CAJA, FREIDORA, REFRESCOS, POLLO)


def _validate_order_types(order_types: List[OrderType]) -> None:
    if not order_types:
        raise ValueError("order_types está vacío. Debe haber al menos 1 tipo de pedido.")

    total = sum(o.prob for o in order_types)
    if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"Las probabilidades de order_types deben sumar 1.0. Actualmente suman {total}.")

    for o in order_types:
        if o.prob < 0:
            raise ValueError(f"Probabilidad negativa en {o.name}.")
        # Validar estaciones
        for st in o.stations:
            if st not in ALL_STATIONS:
                raise ValueError(f"Estación inválida '{st}' en pedido '{o.name}'. Usa: {ALL_STATIONS}.")
            if st == CAJA:
                raise ValueError(f"No incluyas 'caja' dentro de stations en '{o.name}'. Caja siempre se usa.")


def make_base_config() -> ModelConfig:
    """
    Config base. Aquí es donde SOLO vas a reemplazar las distribuciones y probabilidades
    cuando tengas los datos de la Tarea V.
    """

    # ---- DISTRIBUCIONES (PLACEHOLDER) ----
    # TODO: Reemplazar con las distribuciones reales de Tarea V.
    # Ejemplo de placeholder: exponencial con media 1 min => scale=1.
    arrival = DistSpec(name="expon", shape=(), loc=0.0, scale=1.0, units="min")

    services = {
        CAJA: DistSpec(name="expon", scale=3.0, units="min"),        # placeholder
        FREIDORA: DistSpec(name="expon", scale=2.5, units="min"),    # placeholder
        REFRESCOS: DistSpec(name="expon", scale=1.5, units="min"),   # placeholder
        POLLO: DistSpec(name="expon", scale=4.0, units="min"),       # placeholder
    }

    # ---- TIPOS DE PEDIDO (PLACEHOLDER) ----
    # Caja SIEMPRE se usa; aquí se ponen las estaciones extra.
    # TODO: Ajustar probabilidades reales (enunciado/tarea previa).
    order_types = [
        OrderType("solo_refresco", 0.30, (REFRESCOS,)),
        OrderType("frito_y_refresco", 0.35, (FREIDORA, REFRESCOS)),
        OrderType("pollo_y_refresco", 0.25, (POLLO, REFRESCOS)),
        OrderType("combo_completo", 0.10, (FREIDORA, POLLO, REFRESCOS)),
    ]

    _validate_order_types(order_types)

    # ---- COSTOS (del enunciado) ----
    costs = SystemCosts(
        cost_per_server={
            FREIDORA: 200.0,
            CAJA: 500.0,
            REFRESCOS: 750.0,
            POLLO: 100.0,
        }
    )

    settings = SimulationSettings(
        n_customers=2000,
        warmup_customers=200,
        replications=30,
        seed=12345,
    )

    return ModelConfig(
        arrival_dist=arrival,
        service_dists=services,
        order_types=order_types,
        costs=costs,
        settings=settings,
        wait_threshold_minutes=3.0,
    )
