"""
Quantum-inspired QAOA-style solver, classically simulated.
The purpose is to compare the performance of a quantum-inspired workflow (parameterized ansatz + classical parameter optimization)
Simulated QAOA solver (p=1). In this, we model QAOA using a full state-vector simulation and optimize parameters
via grid search. This is a classical approximation intended for comparison
with heuristic solvers, not a claim of quantum advantage.
V1: we use p=1 layer and small n so we can store the full state vector (2^n).
We optimize gamma, beta via a simple grid search. Expectation values are computed
by summing over all 2^n basis states.
"""

import cmath
import math
import time
import random
from typing import List, Tuple

from engine.core.qubo_compiler import QUBORepresentation


def _qubo_diagonal(qubo: QUBORepresentation) -> List[float]:
    n = qubo.n
    diag = []
    for z in range(1 << n):
        solution = [(z >> i) & 1 for i in range(n)]
        diag.append(qubo.objective_value(solution))
    return diag


def _apply_cost_unitary(state: List[complex], diag: List[float], gamma: float) -> None:
    for i in range(len(state)):
        state[i] *= cmath.exp(-1j * gamma * diag[i])


def _apply_mixer(state: List[complex], n: int, beta: float) -> None:
    """
    Apply X rotation to qubit i.
    """
    for i in range(n):
        bit = 1 << i
        for z in range(len(state)):
            if (z & bit) != 0:
                continue
            other = z | bit
            a, b = state[z], state[other]
            state[z] = math.cos(beta) * a - 1j * math.sin(beta) * b
            state[other] = math.cos(beta) * b - 1j * math.sin(beta) * a


def _expectation_value(state: List[complex], diag: List[float]) -> float:
    return sum(abs(state[z]) ** 2 * diag[z] for z in range(len(state)))


def _best_measurement(state: List[complex], n: int) -> List[int]:
    best_z = max(range(len(state)), key=lambda z: abs(state[z]) ** 2)
    return [(best_z >> i) & 1 for i in range(n)]


def solve_qubo_qaoa_simulated(
    qubo: QUBORepresentation,
    gamma_steps: int = 10,
    beta_steps: int = 10,
    max_runtime_seconds: float = 10.0,
    n_restarts: int = 3,
    gamma_range: Tuple[float, float] = (0.0, 2.0),
    beta_range: Tuple[float, float] = (0.0, math.pi),
) -> Tuple[List[int], float, float]:
    """
    Simulated QAOA solver (p=1) for QUBO problems.

    This implementation uses a full state-vector simulation (size 2^n) and a simple
    grid search over parameters (gamma, beta). It is intended as a clear, minimal
    baseline for comparing quantum-inspired optimization against classical heuristics.

    Limitations:
    Exponential runtime and memory (state size = 2^n)
    Single-layer QAOA (p=1)
    Grid search instead of a continuous optimizer

    Returns:
        (best_solution, best_objective_value, runtime_seconds)
    """
    start_time = time.perf_counter()
    deadline = start_time + max_runtime_seconds
    n = qubo.n
    dim = 1 << n
    if dim > 2 ** 20:
        raise ValueError(
            "QAOA simulation state vector too large. Use n <= 20."
        )

    diag = _qubo_diagonal(qubo)
    # Initial state |+>^n: uniform superposition
    init_amp = 1.0 / math.sqrt(dim)
    best_obj = float("inf")
    best_solution: List[int] = []

    gamma_vals = [
        gamma_range[0] + (gamma_range[1] - gamma_range[0]) * i / max(1, gamma_steps - 1)
        for i in range(gamma_steps)
    ]
    beta_vals = [
        beta_range[0] + (beta_range[1] - beta_range[0]) * i / max(1, beta_steps - 1)
        for i in range(beta_steps)
    ]

    random.shuffle(gamma_vals)
    random.shuffle(beta_vals)

    for r in range(n_restarts):
        # slight randomness in initialization (break symmetry)
        state_base = [
            init_amp * (1 + 0.01 * (random.random() - 0.5))
            for _ in range(dim)
        ]

        # renormalize state
        norm = math.sqrt(sum(abs(a) ** 2 for a in state_base))
        state_base = [a / norm for a in state_base]

        for gamma in gamma_vals:
            for beta in beta_vals:
                if time.perf_counter() > deadline:
                    break

                state = list(state_base)
                _apply_cost_unitary(state, diag, gamma)
                _apply_mixer(state, n, beta)

                exp_val = _expectation_value(state, diag)
                if exp_val < best_obj:
                    solution = _best_measurement(state, n)
                    best_obj = exp_val
                    best_solution = solution

            if time.perf_counter() > deadline:
                break

        if time.perf_counter() > deadline:
            break

    runtime = min(time.perf_counter() - start_time, max_runtime_seconds)
    # TODO: support p>1 layers; use a classical optimizer (for example, scipy) instead of grid search.
    return (best_solution, best_obj, runtime)