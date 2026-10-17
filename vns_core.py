"""Basic Variable Neighborhood Search for continuous 2D optimization.

All optimization logic is hand-written using only Python's standard library.
No scipy.optimize, numpy, or other optimization framework.

One iteration = Shaking -> adaptive Local Search -> Neighborhood Change.
"""

from __future__ import annotations
from dataclasses import dataclass
import math
import random
import time

TOL = 1e-12
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1),
              (1, 1), (1, -1), (-1, 1), (-1, -1))


def rosenbrock(x: float, y: float) -> float:
    return (1 - x)**2 + 100 * (y - x*x)**2


def rastrigin(x: float, y: float) -> float:
    return 20 + x*x + y*y - 10*(math.cos(2*math.pi*x) + math.cos(2*math.pi*y))


@dataclass(frozen=True)
class Settings:
    start: tuple[float, float] = (-1., 1.)
    bounds: tuple[float, float] = (-2., 2.)
    k_max: int = 3
    shaking_radius: float = 0.6
    local_step: float = 0.3
    local_min_step: float = 0.0002
    local_max_moves: int = 180
    iterations: int = 100


def in_bounds(point, bounds):
    lo, hi = bounds
    return lo <= point[0] <= hi and lo <= point[1] <= hi


def neighborhood(point, step, bounds):
    """Hand-written 8 directions around a continuous (x,y) candidate."""
    x, y = point
    result = []
    for dx, dy in DIRECTIONS:
        p = (x + dx*step, y + dy*step)
        if in_bounds(p, bounds):
            result.append(p)
    return result


def shake(point, k, radius, bounds, rng):
    """Random direction AND continuous radius (not snapping to 0.2 grid).

    Samples from a ring of radii [0.45*k*r, k*r], retry near bounds.
    A fallback to the bound-clipped point prevents corner crashes.
    """
    lo, hi = bounds
    for _ in range(60):
        angle = rng.uniform(0.0, 2*math.pi)
        distance = rng.uniform(0.45*k*radius, k*radius)
        p = (point[0] + distance*math.cos(angle),
             point[1] + distance*math.sin(angle))
        if in_bounds(p, bounds):
            return p
    # Boundary-safe fallback (almost never needed at normal settings).
    a = rng.uniform(0, 2*math.pi)
    d = rng.uniform(0.45*k*radius, k*radius)
    p = (min(max(point[0] + d*math.cos(a), lo), hi),
         min(max(point[1] + d*math.sin(a), lo), hi))
    return p


def local_search(start, objective, settings, keep_trace=False):
    """Own derivative-free best-improvement pattern search.

    Scan 8 neighbors at current step size. Choose strictly better fitness.
    When stalled, halve the step, allowing continuous precision refinement.
    Return best point and optional exact moves for hand calculations.
    """
    current = tuple(start)
    fitness = objective(*current)
    step = settings.local_step
    trace = [(current, fitness, step)] if keep_trace else []
    evaluations = 1
    improvements = 0
    while step >= settings.local_min_step and improvements < settings.local_max_moves:
        best = current
        best_value = fitness
        for candidate in neighborhood(current, step, settings.bounds):
            v = objective(*candidate)
            evaluations += 1
            if v < best_value - TOL:
                best, best_value = candidate, v
        if best != current:
            current, fitness = best, best_value
            improvements += 1
            if keep_trace:
                trace.append((current, fitness, step))
        else:
            step *= 0.5
    return current, fitness, trace, evaluations


def run_vns(objective, settings, seed=7, trace=False):
    """Fixed-budget Basic VNS; k reset on improvement and cycles on failure."""
    if settings.iterations < 1 or settings.k_max < 1:
        raise ValueError('iterations and k_max must be >= 1')
    if not (0 < settings.local_min_step <= settings.local_step):
        raise ValueError('Need 0 < local_min_step <= local_step')
    if settings.shaking_radius <= 0 or settings.local_max_moves < 1:
        raise ValueError('Positive radius and local_max_moves required')
    if not in_bounds(settings.start, settings.bounds):
        raise ValueError('Starting point is outside bounds')

    rng = random.Random(seed)
    current = tuple(settings.start)
    fitness = objective(*current)
    history = [fitness]
    accepted_path = [current]
    log = []
    k = 1
    evaluations = 1
    t0 = time.perf_counter()
    for i in range(1, settings.iterations + 1):
        before, before_value, old_k = current, fitness, k
        shaken = shake(current, k, settings.shaking_radius, settings.bounds, rng)
        shaken_value = objective(*shaken)
        candidate, candidate_value, path, n_evals = local_search(
            shaken, objective, settings, keep_trace=trace and i <= 2
        )
        evaluations += 1 + n_evals
        accepted = candidate_value < fitness - TOL
        if accepted:
            current, fitness = candidate, candidate_value
            k = 1
            accepted_path.append(current)
        else:
            k = 1 if k == settings.k_max else k + 1
        history.append(fitness)
        log.append({
            'iteration': i, 'k': old_k,
            'before': before, 'before_fitness': before_value,
            'shaken': shaken, 'shaken_fitness': shaken_value,
            'local': candidate, 'local_fitness': candidate_value,
            'accepted': accepted, 'after': current,
            'after_fitness': fitness, 'next_k': k,
            'local_path': path,
        })
    duration = time.perf_counter() - t0
    return {
        'seed': seed, 'best_point': current, 'best_fitness': fitness,
        'history': history, 'accepted_path': accepted_path,
        'logs': log, 'runtime': duration, 'evaluations': evaluations
    }


def experiment(objective, settings, runs=30, first_seed=7):
    if runs < 1:
        raise ValueError('runs must be positive')
    trials = [run_vns(objective, settings, seed=first_seed+i, trace=(i==0))
              for i in range(runs)]
    best_run = min(trials, key=lambda r: r['best_fitness'])
    values = [r['best_fitness'] for r in trials]
    summary = {
        'best': min(values),
        'mean': sum(values)/len(values),
        'worst': max(values),
        'best_point': best_run['best_point'],
        'best_seed': best_run['seed'],
        'average_runtime': sum(r['runtime'] for r in trials)/runs,
        'success_count': sum(v <= 1e-6 for v in values),
        'runs': runs, 'iterations': settings.iterations,
    }
    return trials, summary
