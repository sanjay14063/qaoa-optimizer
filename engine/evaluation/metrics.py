"""
Lightweight metrics for evaluating optimization results.

Provides:
- objective value on the original problem
- number of violated constraints
- simple wall-clock runtime
"""

import time
from typing import Callable, List, Tuple

# Import for type hints and use in function bodies.
from engine.core.optimization_problem import OptimizationProblem


def objective_score(solution: List[int], problem: OptimizationProblem) -> float:
    """
    Return the objective value of a solution on the original problem.
    """
    return problem.evaluate(solution)[0]


def constraint_violation_count(
    solution: List[int], problem: OptimizationProblem
) -> int:
    """
    Count how many constraints are violated by a solution.
    A violation is any constraint with positive violation magnitude.
    """
    _, violations = problem.evaluate(solution)
    return sum(1 for _, v in violations if v > 0)


def runtime_seconds(f: Callable[[], None]) -> float:
    """
    Measure wall-clock time to execute a callable using perf_counter.
    """
    start = time.perf_counter()
    f()
    return time.perf_counter() - start
