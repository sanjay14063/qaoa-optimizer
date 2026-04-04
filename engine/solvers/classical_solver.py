"""
Classical solver for QUBO problems using simulated annealing. This serves as a simple baseline: easy to understand, reasonably effective,
but not guaranteed to find the global optimum.
"""

import math
import random
import time
from typing import List, Tuple

from engine.core.qubo_compiler import QUBORepresentation


def solve_qubo_classical(
    qubo: QUBORepresentation,
    max_iterations: int = 10000,
    initial_temperature: float = 10.0,
    cooling_rate: float = 0.995,
    seed: int | None = None,
    n_restarts: int = 5,
) -> Tuple[List[int], float, float]:
    """
    Minimize a QUBO using simulated annealing. And at each step, a single variable is flipped and accepted if it improves
    the objective, or probabilistically accepted if it worsens it (to escape
    local minima).

    Returns:
        (best_solution, best_objective_value, runtime_seconds)
    """
    n = qubo.n
    start_time = time.perf_counter()
    global_best = None
    global_best_obj = float("inf")

    for r in range(n_restarts):
        if seed is not None:
            random.seed(seed + r)

        # Start from a random binary assignment
        current = [random.randint(0, 1) for _ in range(n)]
        current_obj = qubo.objective_value(current)

        best = list(current)
        best_obj = current_obj

        temperature = initial_temperature

        for _ in range(max_iterations):
            i = random.randint(0, n - 1)
            neighbor = list(current)
            neighbor[i] = 1 - neighbor[i]
            neighbor_obj = qubo.objective_value(neighbor)

            delta = neighbor_obj - current_obj

            if delta <= 0 or random.random() < (
                1.0 if temperature <= 0 else math.exp(-delta / temperature)
            ):
                current = neighbor
                current_obj = neighbor_obj

                if current_obj < best_obj:
                    best = list(current)
                    best_obj = current_obj

            temperature *= cooling_rate

        # Track global best across restarts
        if best_obj < global_best_obj:
            global_best = best
            global_best_obj = best_obj

    runtime = time.perf_counter() - start_time
    return (global_best, global_best_obj, runtime)
