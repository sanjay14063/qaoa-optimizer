"""
Run scheduling optimization experiments.

Includes:
- Solver comparison on small instances (with exact ground truth)
- Scaling experiment to evaluate runtime and solution quality
"""

import time
import itertools
import csv

from engine.problems.scheduling_problem import build_scheduling_problem
from engine.solvers.classical_solver import solve_qubo_classical as solve_classical
from engine.solvers.hybrid_qaoa_solver import solve_qubo_qaoa_simulated as solve_qaoa


def brute_force_optimum(problem):
    """
    Compute the exact optimal objective value by exhaustive search.
    Only feasible for small problem sizes due to exponential complexity.
    """
    n = problem.n_vars
    best_energy = float("inf")

    for bits in itertools.product([0, 1], repeat=n):
        solution = list(bits)
        result = problem.evaluate(solution)

        if isinstance(result, dict):
            energy = result["objective"]
            raw_violations = result["violations"]
        else:
            energy, raw_violations = result

        if isinstance(raw_violations, list):
            violations = sum(abs(v) for (_, v) in raw_violations)
        else:
            violations = raw_violations

        if isinstance(violations, (int, float)) and abs(violations) < 1e-6:
            if energy < best_energy:
                best_energy = energy

    return best_energy


def solver_comparison():
    """
    Compare solvers on small instances where exact solutions are available.
    """
    print("\n=== SOLVER COMPARISON ===")

    rows = []

    test_cases = [
        (2, 2),
        (3, 2),
        (4, 2),
        (3, 3),
    ]

    for tasks, slots in test_cases:
        print(f"\nProblem: {tasks} tasks x {slots} slots")

        problem = build_scheduling_problem(tasks, slots)

        # Ground truth
        start = time.time()
        true_energy = brute_force_optimum(problem)
        brute_time = time.time() - start

        qubo = problem.to_qubo(penalty_weight=10.0)

        # Classical
        start = time.time()
        classical_energies = []

        for _ in range(5):
            _, energy, _ = solve_classical(qubo)
            classical_energies.append(energy)

        classical_energy = min(classical_energies)
        classical_mean = sum(classical_energies) / len(classical_energies)
        classical_std = (sum((e - classical_mean) ** 2 for e in classical_energies) / len(classical_energies)) ** 0.5
        classical_time = time.time() - start

        # QAOA (safe)
        if problem.n_vars <= 20:
            start = time.time()
            qaoa_energies = []

            for _ in range(5):
                try:
                    _, energy, _ = solve_qaoa(qubo)
                    qaoa_energies.append(energy)
                except Exception:
                    continue

            qaoa_time = time.time() - start

            if len(qaoa_energies) > 0:
                qaoa_energy = min(qaoa_energies)
                qaoa_mean = sum(qaoa_energies) / len(qaoa_energies)
                qaoa_std = (sum((e - qaoa_mean) ** 2 for e in qaoa_energies) / len(qaoa_energies)) ** 0.5
            else:
                qaoa_energy = None
                qaoa_mean = None
                qaoa_std = None
        else:
            qaoa_energy = None
            qaoa_mean = None
            qaoa_std = None
            qaoa_time = None

        # Gaps
        if true_energy == float("inf"):
            classical_gap = None
            qaoa_gap = None
        else:
            classical_gap = classical_energy - true_energy
            qaoa_gap = (
                qaoa_energy - true_energy if qaoa_energy is not None else None
            )

        # Print
        print(f"True optimum: {true_energy:.4f} (time: {brute_time:.4f}s)")
        print("Classical:")
        print(f"  energy = {classical_energy:.4f}")
        print(f"  mean   = {classical_mean:.4f}")
        print(f"  std    = {classical_std:.4f}")
        print(f"  gap    = {classical_gap:.4f}" if classical_gap is not None else "  gap    = N/A")
        print(f"  time   = {classical_time:.4f}s")

        print("QAOA sim:")
        print(f"  energy = {qaoa_energy if qaoa_energy is not None else 'N/A'}")
        if qaoa_mean is not None:
            print(f"  mean   = {qaoa_mean:.4f}")
            print(f"  std    = {qaoa_std:.4f}")
        print(f"  gap    = {qaoa_gap:.4f}" if qaoa_gap is not None else "  gap    = N/A")
        print(f"  time   = {qaoa_time if qaoa_time is not None else 'N/A'}")

        # Save row
        rows.append([
            tasks,
            slots,
            true_energy,
            classical_energy,
            classical_mean,
            classical_std,
            qaoa_energy if qaoa_energy is not None else "N/A",
            qaoa_mean if qaoa_mean is not None else "N/A",
            qaoa_std if qaoa_std is not None else "N/A",
            classical_gap,
            qaoa_gap,
            classical_time,
            qaoa_time if qaoa_time is not None else "N/A",
        ])

    # Write CSV
    with open("solver_comparison_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tasks",
            "slots",
            "true_energy",
            "classical_best",
            "classical_mean",
            "classical_std",
            "qaoa_best",
            "qaoa_mean",
            "qaoa_std",
            "gap_classical",
            "gap_qaoa",
            "t_classical",
            "t_qaoa",
        ])
        writer.writerows(rows)

    print("\nSaved solver comparison results to solver_comparison_results.csv")


def scaling_experiment():
    """
    Evaluate solver performance as problem size increases.
    """
    print("\n=== SCALING EXPERIMENT ===")
    print("n_vars | t_classical | t_qaoa | E_classical | E_qaoa | gap_classical | gap_qaoa")

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
        (15, 2),
        (16, 2),
    ]

    for tasks, slots in test_cases:
        problem = build_scheduling_problem(tasks, slots)
        n = problem.n_vars

        qubo = problem.to_qubo(penalty_weight=10.0)

        # Classical
        start = time.time()
        classical_energies = []

        for _ in range(5):
            _, energy, _ = solve_classical(qubo)
            classical_energies.append(energy)

        classical_energy = min(classical_energies)
        classical_mean = sum(classical_energies) / len(classical_energies)
        classical_std = (sum((e - classical_mean) ** 2 for e in classical_energies) / len(classical_energies)) ** 0.5
        classical_time = time.time() - start

        # QAOA (safe)
        if n <= 16:
            start = time.time()
            qaoa_energies = []

            for _ in range(5):
                try:
                    _, energy, _ = solve_qaoa(qubo)
                    qaoa_energies.append(energy)
                except Exception:
                    continue

            qaoa_time = time.time() - start

            if len(qaoa_energies) > 0:
                qaoa_energy = min(qaoa_energies)
                qaoa_mean = sum(qaoa_energies) / len(qaoa_energies)
                qaoa_std = (sum((e - qaoa_mean) ** 2 for e in qaoa_energies) / len(qaoa_energies)) ** 0.5
            else:
                qaoa_energy = None
                qaoa_mean = None
                qaoa_std = None
        else:
            qaoa_energy = None
            qaoa_mean = None
            qaoa_std = None
            qaoa_time = None

        # Gaps
        if n <= 12:
            true_energy = brute_force_optimum(problem)

            if true_energy == float("inf"):
                gap_classical = None
                gap_qaoa = None
            else:
                gap_classical = classical_energy - true_energy
                gap_qaoa = (
                    qaoa_energy - true_energy if qaoa_energy is not None else None
                )
        else:
            gap_classical = None
            gap_qaoa = None

        # Print
        print(
            f"{n:6d} | "
            f"{classical_time:12.6f} | "
            f"{(f'{qaoa_time:.6f}' if qaoa_time is not None else 'N/A'):>8} | "
            f"{classical_energy:12.4f} | "
            f"{(f'{qaoa_energy:.4f}' if qaoa_energy is not None else 'N/A'):>10} | "
            f"{(f'{gap_classical:.4f}' if gap_classical is not None else 'N/A'):>13} | "
            f"{(f'{gap_qaoa:.4f}' if gap_qaoa is not None else 'N/A'):>10}"
        )

        # Save row
        rows.append([
            n,
            classical_time,
            qaoa_time if qaoa_time is not None else "N/A",
            classical_energy,
            classical_mean,
            classical_std,
            qaoa_energy if qaoa_energy is not None else "N/A",
            qaoa_mean if qaoa_mean is not None else "N/A",
            qaoa_std if qaoa_std is not None else "N/A",
            gap_classical if gap_classical is not None else "N/A",
            gap_qaoa if gap_qaoa is not None else "N/A",
        ])

    # Write CSV
    with open("scaling_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n_vars",
            "t_classical",
            "t_qaoa",
            "E_classical_best",
            "E_classical_mean",
            "E_classical_std",
            "E_qaoa_best",
            "E_qaoa_mean",
            "E_qaoa_std",
            "gap_classical",
            "gap_qaoa",
        ])
        writer.writerows(rows)

    print("\nSaved scaling results to scaling_results.csv")


if __name__ == "__main__":
    print("HYBRID OPTIMIZER EXPERIMENTS (V1)")

    solver_comparison()
    scaling_experiment()

    print("\nDone.")
