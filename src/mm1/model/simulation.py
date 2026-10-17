"""Simulación M/M/1 con SimPy.

Modelo de eventos discretos con:
- Llegadas según distribución exponencial (Poisson)
- Servicio exponencial
- Un solo servidor (capacidad 1)
- Cola FIFO

Solo se registran clientes que terminan su servicio dentro del tiempo simulado.
"""

from __future__ import annotations

import random
from collections.abc import Generator
from dataclasses import dataclass

import simpy

from .metrics import is_stable

# Límite superior de la semilla dibujada cuando el caller pasa ``seed=None``.
_MAX_SEED = 2**32


@dataclass(frozen=True)
class CustomerRecord:
    """Datos de un cliente atendido durante la simulación."""

    customer_id: int
    arrival_time: float  # Hora de llegada
    service_start: float # Hora en que empieza a ser atendido
    departure_time: float # Hora en que sale del sistema
    wait_time: float     # Tiempo esperando en cola
    service_time: float  # Tiempo de atención


@dataclass(frozen=True)
class ScenarioRun:
    """Resultado agregado de una corrida de simulación."""

    scenario: int
    lam: float
    mu: float
    seed: int
    sim_time: float
    warmup: float
    n_customers: int
    mean_wait: float        # Promedio de tiempo en cola
    mean_queue: float       # Promedio de longitud de cola
    mean_system_time: float # Promedio de tiempo en sistema
    mean_in_system: float   # Promedio de clientes en sistema
    utilization: float      # Uso del servidor
    customers: tuple[CustomerRecord, ...]
    queue_trace: tuple[tuple[float, int], ...]


def _validate(lam: float, mu: float, sim_time: float, warmup: float) -> None:
    """Revisa que los parámetros sean válidos."""
    if lam <= 0 or mu <= 0:
        raise ValueError("las tasas lam y mu deben ser positivas")
    if sim_time <= 0:
        raise ValueError("sim_time debe ser mayor que 0")
    if warmup < 0 or warmup >= sim_time:
        raise ValueError("warmup debe cumplir 0 <= warmup < sim_time")
    if not is_stable(lam, mu):
        raise ValueError("El sistema no es estable")


def _arrivals(
    env: simpy.Environment,
    server: simpy.Resource,
    rng: random.Random,
    lam: float,
    mu: float,
    sim_time: float,
    customers: list[CustomerRecord],
    queue_trace: list[tuple[float, int]],
) -> Generator[simpy.Event, None, None]:
    """Genera llegadas con tiempo entre llegadas exponencial."""
    customer_id = 0
    while True:
        yield env.timeout(rng.expovariate(lam))
        if env.now >= sim_time:
            return
        env.process(
            _customer(
                env,
                server,
                rng,
                mu,
                sim_time,
                customer_id,
                float(env.now),
                customers,
                queue_trace,
            )
        )
        customer_id += 1


def _customer(
    env: simpy.Environment,
    server: simpy.Resource,
    rng: random.Random,
    mu: float,
    sim_time: float,
    customer_id: int,
    arrival_time: float,
    customers: list[CustomerRecord],
    queue_trace: list[tuple[float, int]],
) -> Generator[simpy.Event, None, None]:
    """Espera en cola, es atendido (FIFO) y se registra si termina dentro del tiempo."""
    with server.request() as request:
        queue_trace.append((float(env.now), len(server.queue)))
        yield request

        service_start = float(env.now)
        queue_trace.append((service_start, len(server.queue)))

        service_time = rng.expovariate(mu)
        departure_time = service_start + service_time
        if departure_time > sim_time:
            # Aún en servicio al finalizar: no se registra este cliente
            yield env.timeout(max(sim_time - service_start, 0.0))
            return

        yield env.timeout(service_time)
        customers.append(
            CustomerRecord(
                customer_id=customer_id,
                arrival_time=arrival_time,
                service_start=service_start,
                departure_time=departure_time,
                wait_time=service_start - arrival_time,
                service_time=service_time,
            )
        )


def _value_at(breakpoints: list[tuple[float, float]], when: float) -> float:
    """Obtiene el valor de una función a trozos (constante entre cambios)
    en el instante 'when'. Busca el último cambio con tiempo <= when."""
    value = 0.0
    for time, candidate in breakpoints:
        if time > when:
            break
        value = candidate
    return value


def _time_average(breakpoints: list[tuple[float, float]], start: float, end: float) -> float:
    """Promedio ponderado por tiempo de una función a trozos entre start y end.
    Se usa para obtener promedios de cola y de clientes en sistema.
    """
    if end <= start:
        return 0.0

    total = 0.0
    cursor = start
    current = _value_at(breakpoints, start)
    for time, value in breakpoints:
        if time <= start:
            continue
        if time >= end:
            break
        total += current * (time - cursor)
        cursor, current = time, value
    total += current * (end - cursor)
    return total / (end - start)


def _in_system_breakpoints(customers: list[CustomerRecord]) -> list[tuple[float, float]]:
    """Obtiene el número de clientes dentro del sistema a lo largo del tiempo.
    Para cada llegada +1, para cada salida -1. Se convierte a función a trozos.
    """
    events: list[tuple[float, float]] = []
    for customer in customers:
        events.append((customer.arrival_time, 1.0))
        events.append((customer.departure_time, -1.0))
    events.sort(key=lambda event: event[0])

    breakpoints: list[tuple[float, float]] = []
    inside = 0.0
    for time, delta in events:
        inside += delta
        breakpoints.append((time, inside))
    return breakpoints


def run_mm1(
    lam: float,
    mu: float,
    sim_time: float = 1000.0,
    seed: int | None = None,
    scenario: int = 0,
    warmup: float = 0.0,
) -> ScenarioRun:
    """Ejecuta una simulación M/M/1 y devuelve los resultados."""
    _validate(lam, mu, sim_time, warmup)

    resolved_seed = seed if seed is not None else random.Random().randrange(_MAX_SEED)
    rng = random.Random(resolved_seed)

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)  # Un solo servidor (atención uno por uno)
    customers: list[CustomerRecord] = []        # Clientes que terminaron y se registraron
    # Traza de cola: (tiempo, longitud_cola). Guarda cambios en el tamaño de cola
    queue_trace: list[tuple[float, int]] = [(0.0, 0)]

    env.process(_arrivals(env, server, rng, lam, mu, sim_time, customers, queue_trace))
    env.run(until=sim_time)

    window = sim_time - warmup
    # Solo contamos clientes que llegaron después (o en) el periodo de calentamiento
    # según criterio usado: se excluyen los que llegaron antes de warmup
    counted = [customer for customer in customers if customer.arrival_time >= warmup]
    completed = len(customers)

    if counted:
        mean_wait = sum(c.wait_time for c in counted) / len(counted)
        mean_system_time = sum(c.departure_time - c.arrival_time for c in counted) / len(counted)
    else:
        mean_wait = 0.0
        mean_system_time = 0.0

    # Tiempo que el servidor estuvo ocupado (para calcular utilización)
    busy = 0.0
    for customer in customers:
        start = max(customer.service_start, warmup)
        stop = min(customer.departure_time, sim_time)
        if stop > start:
            busy += stop - start

    trace = [(float(time), float(length)) for time, length in queue_trace]
    return ScenarioRun(
        scenario=scenario,
        lam=lam,
        mu=mu,
        seed=resolved_seed,
        sim_time=sim_time,
        warmup=warmup,
        n_customers=completed,
        mean_wait=mean_wait,
        mean_queue=_time_average(trace, warmup, sim_time),  # promedio de cola por tiempo
        mean_system_time=mean_system_time,
        mean_in_system=_time_average(_in_system_breakpoints(customers), warmup, sim_time),  # clientes en sistema por tiempo
        utilization=busy / window if window > 0 else 0.0,  # ρ_sim = tiempo ocupado / tiempo observado
        customers=tuple(customers),
        queue_trace=tuple(queue_trace),
    )
