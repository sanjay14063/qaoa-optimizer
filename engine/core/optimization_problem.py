"""
Solver-agnostic representation of a constrained binary optimization problem.

Stores variables, objective (linear + quadratic), and constraints.
Conversion to QUBO is delegated to the compiler.
"""

from typing import List, Tuple, Optional


class OptimizationProblem:
    """
    Binary optimization problem container.

    - x ∈ {0,1}^n
    - Objective: c^T x + x^T Q x
    - Constraints: linear equalities and inequalities

    This class holds data and exposes:
    - to_qubo(): compile to QUBO via penalties
    - evaluate(): score a candidate and report violations
    """

    def __init__(
        self,
        n_vars: int,
        linear_objective: List[float],
        quadratic_objective: List[List[float]],
        equality_constraints: Optional[List[Tuple[List[float], float]]] = None,
        inequality_constraints: Optional[List[Tuple[List[float], float]]] = None,
    ) -> None:
        """
        Initialize problem data.

        Args:
            n_vars: number of binary variables
            linear_objective: coefficients c_i
            quadratic_objective: matrix Q (n x n)
            equality_constraints: list of (coeffs, rhs) for a^T x = b
            inequality_constraints: list of (coeffs, rhs) for a^T x <= b
        """
        self.n_vars = n_vars
        self.linear_objective = list(linear_objective)
        self.quadratic_objective = [list(row) for row in quadratic_objective]
        self.equality_constraints = equality_constraints or []
        self.inequality_constraints = inequality_constraints or []

    def to_qubo(self, penalty_weight: float) -> "QUBORepresentation":
        """
        Compile to QUBO by adding penalty terms for constraints.

        Returns a QUBORepresentation (Q matrix + constant offset).
        """
        from engine.core.qubo_compiler import compile_to_qubo
        return compile_to_qubo(self, penalty_weight)

    def evaluate(
        self, solution: List[int]
    ) -> Tuple[float, List[Tuple[str, float]]]:
        """
        Evaluate a solution.

        Returns:
            (objective_value, [(constraint_name, violation_amount), ...])

        Equality violation: |a^T x - b|
        Inequality violation: max(0, a^T x - b)
        """
        if len(solution) != self.n_vars:
            raise ValueError(
                f"Solution length {len(solution)} does not match n_vars {self.n_vars}"
            )
        # Compute objective: linear + quadratic terms
        obj = 0.0
        for i in range(self.n_vars):
            obj += self.linear_objective[i] * solution[i]
        for i in range(self.n_vars):
            for j in range(self.n_vars):
                obj += self.quadratic_objective[i][j] * solution[i] * solution[j]
        # Assumes Q already encodes the intended coefficients; no symmetry adjustment here

        violations: List[Tuple[str, float]] = []
        for idx, (coeffs, rhs) in enumerate(self.equality_constraints):
            lhs = sum(c * solution[i] for i, c in enumerate(coeffs))
            violations.append((f"eq_{idx}", abs(lhs - rhs)))
        for idx, (coeffs, rhs) in enumerate(self.inequality_constraints):
            lhs = sum(c * solution[i] for i, c in enumerate(coeffs))
            violations.append((f"ineq_{idx}", max(0.0, lhs - rhs)))

        return (obj, violations)
