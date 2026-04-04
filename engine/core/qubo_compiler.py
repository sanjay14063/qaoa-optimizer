"""
QUBO compiler: converts a constrained OptimizationProblem into a QUBO.

We encode constraints as quadratic penalties and return a matrix Q such that
the objective is x^T Q x (x ∈ {0,1}^n) plus a constant offset.

V1 scope:
- Supports equality constraints via squared penalties
- Leaves inequalities uncompiled (documented limitation)
"""

from typing import List, Tuple

# Type-hint import to avoid runtime circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.core.optimization_problem import OptimizationProblem


class QUBORepresentation:
    """
    QUBO container.

    - Q: symmetric n×n matrix for x^T Q x
    - constant_offset: added to the objective value
    """

    def __init__(self, Q: List[List[float]], constant_offset: float = 0.0) -> None:
        self.Q = Q
        self.constant_offset = constant_offset
        self.n = len(Q)

    def objective_value(self, solution: List[int]) -> float:
        """Return x^T Q x + constant_offset for a binary solution."""
        val = self.constant_offset
        for i in range(self.n):
            val += self.Q[i][i] * solution[i] * solution[i]
            for j in range(i + 1, self.n):
                val += 2 * self.Q[i][j] * solution[i] * solution[j]
        return val


def compile_to_qubo(
    problem: "OptimizationProblem", penalty_weight: float
) -> QUBORepresentation:
    """
    Compile an OptimizationProblem into QUBO form.

    Approach:
    - Fold linear terms into the diagonal (x_i^2 = x_i)
    - Add penalty_weight * (g(x))^2 for each equality constraint

    Limitations:
    - Inequality constraints are not compiled in V1
    - Penalty weight is not auto-tuned
    """
    n = problem.n_vars
    # Initialize Q: copy quadratic terms and fold linear terms into the diagonal
    Q = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            Q[i][j] = problem.quadratic_objective[i][j]
        Q[i][i] += problem.linear_objective[i]

    constant = 0.0

    # Add penalty for each equality constraint via squared penalty
    # Q_ij += w * a_i * a_j, Q_ii += -2w * b * a_i, constant += w * b^2
    for coeffs, rhs in problem.equality_constraints:
        # g(x) = sum_i coeffs[i] * x_i - rhs
        for i in range(n):
            for j in range(n):
                Q[i][j] += penalty_weight * coeffs[i] * coeffs[j]
            Q[i][i] += -2.0 * penalty_weight * rhs * coeffs[i]
        constant += penalty_weight * (rhs ** 2)

    # V1 limitation: inequalities are not compiled
    # TODO: add slack-variable encoding for inequalities
    # TODO: auto-tune penalty_weight to prefer feasible solutions

    # Ensure Q is symmetric (important for correct evaluation)
    for i in range(n):
        for j in range(i + 1, n):
            avg = 0.5 * (Q[i][j] + Q[j][i])
            Q[i][j] = avg
            Q[j][i] = avg

    return QUBORepresentation(Q, constant)
