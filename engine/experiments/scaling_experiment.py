"""
scaling_experiment.py

Evaluates how solver performance scales with problem size.

Tracks:
- number of variables
- runtime (classical vs QAOA)
- energy (objective value)
- optional optimality gap (when brute force is feasible)

Design:
- Uses brute force ONLY for small problems (n_vars <= 12)
- Focuses on runtime growth and solution quality

This complements solver_comparison.py.
"""

import time
import csv

from engine.problems.scheduling_problem import build_scheduling_problem
from engine.solvers.classical_solver import solve as solve_classical
from engine.solvers.hybrid_qaoa_solver import solve as solve_qaoa


# -------------------------------
# OPTIONAL: BRUTE FORCE (SMALL ONLY)
# -------------------------------
def brute_force_optimum(problem):
    import itertools

    n = problem.n_vars

    best_energy = float("inf")

    for bits in itertools.product([0, 1], repeat=n):
        solution = list(bits)

        result = problem.evaluate(solution)

        # normalize
        if isinstance(result, dict):
            raw_violations = result["violations"]
            energy = result["objective"]
        else:
            energy, raw_violations = result

        if isinstance(raw_violations, list):
            violations = sum(abs(v) for (_, v) in raw_violations)
        else:
            violations = raw_violations

        if violations == 0:
            if energy < best_energy:
                best_energy = energy

    return best_energy


# -------------------------------
# SCALING EXPERIMENT
# -------------------------------
def run_scaling():
    print("\nSCALING EXPERIMENT")
    print("n_vars | classical_time | qaoa_time | classical_energy | qaoa_energy | gap_classical | gap_qaoa")
    rows = []

    test_cases = [
        (2, 2),
        (3, 2),
        (4, 2),
        (5, 2),
        (6, 2),
        (7, 2),
        (8, 2),
        (9, 2),
        (10, 2),
        (11, 2),
        (12, 2),
        (13, 2),
        (14, 2),
        (3, 3),
        (4, 3),
        (5, 3),
        (6, 3),
    ]

    for tasks, slots in test_cases:
        problem = build_scheduling_problem(tasks, slots)
        n = problem.n_vars

        # ---- Classical ----
        start = time.time()
        best_classical_energy = float("inf")

        for _ in range(5):
            _, energy = solve_classical(problem)
            if energy < best_classical_energy:
                best_classical_energy = energy

        classical_energy = best_classical_energy
        classical_time = time.time() - start

        # ---- QAOA (safe) ----
        if n <= 20:
            start = time.time()
            _, qaoa_energy = solve_qaoa(problem)
            qaoa_time = time.time() - start
        else:
            qaoa_energy = None
            qaoa_time = None

        # ---- Optional brute force ----
        if n <= 12:
            true_energy = brute_force_optimum(problem)
            gap_classical = classical_energy - true_energy
            gap_qaoa = (qaoa_energy - true_energy) if qaoa_energy is not None else None
        else:
            gap_classical = None
            gap_qaoa = None

        # ---- Print ----
        print(f"{n:6d} | "
              f"{classical_time:14.6f} | "
              f"{qaoa_time if qaoa_time is not None else 'N/A':>9} | "
              f"{classical_energy:16.4f} | "
              f"{qaoa_energy if qaoa_energy is not None else 'N/A':>11} | "
              f"{str(gap_classical):13} | "
              f"{str(gap_qaoa):8}")

        rows.append([
            n,
            classical_time,
            qaoa_time if qaoa_time is not None else "N/A",
            classical_energy,
            qaoa_energy if qaoa_energy is not None else "N/A",
            gap_classical,
            gap_qaoa,
        ])


    # ---- Save to CSV ----
    with open("scaling_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n_vars",
            "t_classical",
            "t_qaoa",
            "E_classical",
            "E_qaoa",
            "gap_classical",
            "gap_qaoa",
        ])
        writer.writerows(rows)

    print("\nSaved results to scaling_results.csv")


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    run_scaling()