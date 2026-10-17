"""Toy application: one-vehicle delivery-route optimization using manually written VNS."""
import math
import random

# Made-up Euclidean coordinates; not traffic-aware road distances.
STOPS = [(0,0), (2,4), (5,3), (6,-1), (2,-3), (-2,-2)]
INITIAL = (0, 1, 3, 5, 2, 4, 0)


def route_length(route):
    length = 0.0
    for i in range(len(route)-1):
        a = STOPS[route[i]]
        b = STOPS[route[i+1]]
        length += math.hypot(b[0]-a[0], b[1]-a[1])
    return length


def nearby_routes(route, k):
    # k=1: swap customer positions; k=2: 2-opt reversal.
    for i in range(1, len(route)-2):
        for j in range(i+1, len(route)-1):
            r = list(route)
            if k == 1:
                r[i], r[j] = r[j], r[i]
            else:
                r[i:j+1] = reversed(r[i:j+1])
            yield tuple(r)


def refine(route):
    current = route
    while True:
        best = current
        for k in (1, 2):
            for option in nearby_routes(current, k):
                if route_length(option) < route_length(best)-1e-12:
                    best = option
        if best == current:
            return current
        current = best


def run_demo(seed=7, iterations=20):
    rng = random.Random(seed)
    route = INITIAL
    old = route_length(route)
    k = 1
    trace = []
    for i in range(1, iterations+1):
        shaken = rng.choice(list(nearby_routes(route, k)))
        candidate = refine(shaken)
        accepted = route_length(candidate) < route_length(route)-1e-12
        if accepted:
            route, k = candidate, 1
        else:
            k = 2 if k == 1 else 1
        trace.append((i, shaken, candidate, accepted, route_length(route)))
    return {'start_route':INITIAL, 'end_route':route,
            'initial_distance':old, 'best_distance':route_length(route),
            'improvement':old-route_length(route), 'trace':trace}
