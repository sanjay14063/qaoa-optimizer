"""
Simple task scheduling problem used for V1 experiments.

We assign each task to exactly one time slot while minimizing assignment cost.
The formulation is intentionally small and explicit to keep the focus on the
optimization pipeline rather than problem complexity.
"""

from typing import List, Optional

from engine.core.optimization_problem import OptimizationProblem


def build_scheduling_problem(
    num_tasks: int = 3,
    num_slots: int = 2,
    cost_matrix: Optional[List[List[float]]] = None,
) -> OptimizationProblem:
    """
    Construct a scheduling instance as an OptimizationProblem.

    If no cost matrix is provided, a simple deterministic pattern is used to
    ensure the problem is non-trivial but easy to scale.
    """
    n = num_tasks * num_slots
    if cost_matrix is None:
        # Simple deterministic cost pattern (keeps instances consistent and scalable)
        cost_matrix = [
            [(t + 1) + (s + 1) for s in range(num_slots)]
            for t in range(num_tasks)
        ]
    linear = [cost_matrix[t][s] for t in range(num_tasks) for s in range(num_slots)]
    quadratic = [[0.0] * n for _ in range(n)]

    equality_constraints = []
    for t in range(num_tasks):
        coeffs = [0.0] * n
        for s in range(num_slots):
            coeffs[t * num_slots + s] = 1.0
        equality_constraints.append((coeffs, 1.0))

    return OptimizationProblem(
        n_vars=n,
        linear_objective=linear,
        quadratic_objective=quadratic,
        equality_constraints=equality_constraints,
        inequality_constraints=[],
    )


# Default V1 instance (3 tasks, 2 slots) used in experiments
SCHEDULING_PROBLEM_V1 = build_scheduling_problem()
