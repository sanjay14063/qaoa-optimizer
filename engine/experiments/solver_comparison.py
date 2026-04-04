"""
solver_comparison.py

Runs a comparison between:
1. Brute force (ground truth)
2. Classical solver
3. QAOA-style simulator

Outputs:
- Objective values
- Optimality gap
- Runtime

This is the core experimental script for V1.
"""

import time
import csv

from engine.problems.scheduling_problem import build_scheduling_problem
from engine.solvers.classical_solver import solve_classical
from engine.solvers.hybrid_qaoa_solver import solve_qaoa


# -------------------------------
# BRUTE FORCE (GROUND TRUTH)
# -------------------------------
def brute_force_optimum(problem):
    import itertools

    n = problem.n_vars

    best_energy = float("inf")
    best_solution = None

    for bits in itertools.product([0, 1], repeat=n):
        solution = list(bits)

        result = problem.evaluate(solution)

        # normalize result
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
                best_solution = solution

    return best_solution, best_energy


# -------------------------------
# EXPERIMENT RUNNER
# -------------------------------
def run_experiment(num_tasks, num_slots):
    print(f"\nProblem: {num_tasks} tasks x {num_slots} slots")

    problem = build_scheduling_problem(num_tasks, num_slots)

    # ---- Ground truth ----
    start = time.time()
    true_sol, true_energy = brute_force_optimum(problem)
    brute_time = time.time() - start

    # ---- Classical solver ----
    start = time.time()
    best_classical_energy = float("inf")
    best_classical_sol = None

    for _ in range(5):
        sol, energy = solve_classical(problem)
        if energy < best_classical_energy:
            best_classical_energy = energy
            best_classical_sol = sol

    classical_sol = best_classical_sol
    classical_energy = best_classical_energy
    classical_time = time.time() - start

    # ---- QAOA solver (safe) ----
    if problem.n_vars <= 20:
        start = time.time()
        qaoa_sol, qaoa_energy = solve_qaoa(problem)
        qaoa_time = time.time() - start
    else:
        qaoa_sol, qaoa_energy = None, None
        qaoa_time = None

    # ---- Metrics ----
    classical_gap = classical_energy - true_energy
    qaoa_gap = (qaoa_energy - true_energy) if qaoa_energy is not None else None

    # ---- Output ----
    print(f"  True optimum: {true_energy:.4f} (time: {brute_time:.4f}s)")

    print("  Classical:")
    print(f"    energy = {classical_energy:.4f}")
    print(f"    gap    = {classical_gap:.4f}")
    print(f"    time   = {classical_time:.4f}s")

    print("  QAOA sim:")
    print(f"    energy = {qaoa_energy if qaoa_energy is not None else 'N/A'}")
    print(f"    gap    = {qaoa_gap}")
    print(f"    time   = {qaoa_time if qaoa_time is not None else 'N/A'}")


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    test_cases = [
        (2, 2),
        (3, 2),
        (4, 2),
        (3, 3),
    ]

    rows = []

    for tasks, slots in test_cases:
        print(f"\nProblem: {tasks} tasks x {slots} slots")

        problem = build_scheduling_problem(tasks, slots)

        # Ground truth
        start = time.time()
        _, true_energy = brute_force_optimum(problem)
        brute_time = time.time() - start

        # Classical
        start = time.time()
        best_classical_energy = float("inf")

        for _ in range(5):
            _, energy = solve_classical(problem)
            if energy < best_classical_energy:
                best_classical_energy = energy

        classical_energy = best_classical_energy
        classical_time = time.time() - start

        # QAOA (safe)
        if problem.n_vars <= 20:
            start = time.time()
            _, qaoa_energy = solve_qaoa(problem)
            qaoa_time = time.time() - start
        else:
            qaoa_energy = None
            qaoa_time = None

        classical_gap = classical_energy - true_energy
        qaoa_gap = (qaoa_energy - true_energy) if qaoa_energy is not None else None

        print(f"  True optimum: {true_energy:.4f} (time: {brute_time:.4f}s)")
        print(f"  Classical: E={classical_energy:.4f}, gap={classical_gap:.4f}, t={classical_time:.4f}s")
        print(f"  QAOA: E={qaoa_energy if qaoa_energy is not None else 'N/A'}, gap={qaoa_gap}, t={qaoa_time if qaoa_time is not None else 'N/A'}")

        rows.append([
            tasks,
            slots,
            true_energy,
            classical_energy,
            qaoa_energy if qaoa_energy is not None else "N/A",
            classical_gap,
            qaoa_gap,
            classical_time,
            qaoa_time if qaoa_time is not None else "N/A",
        ])

    with open("solver_comparison_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tasks",
            "slots",
            "true_energy",
            "classical_energy",
            "qaoa_energy",
            "gap_classical",
            "gap_qaoa",
            "t_classical",
            "t_qaoa",
        ])
        writer.writerows(rows)

    print("\nSaved results to solver_comparison_results.csv")