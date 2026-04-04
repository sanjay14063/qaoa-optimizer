import itertools
import time
import csv
from engine.problems.scheduling_problem import build_scheduling_problem


def brute_force_optimum(problem):
    """
    Exhaustively search all possible binary assignments to find the true optimum.
    Only feasible for small n due to exponential complexity.
    """

    if not hasattr(problem, "n_vars"):
        raise AttributeError("OptimizationProblem must have attribute 'n_vars'")

    n = problem.n_vars
    best_energy = float("inf")
    best_solution = None

    for bits in itertools.product([0, 1], repeat=n):
        solution = list(bits)
        result = problem.evaluate(solution)

        # Handle multiple return formats
        if isinstance(result, dict):
            energy = result["objective"]
            raw_violations = result["violations"]
        else:
            energy, raw_violations = result

        # Normalize violations
        if isinstance(raw_violations, list):
            violations = sum(abs(v) for (_, v) in raw_violations)
        else:
            violations = raw_violations

        # Feasibility check with tolerance
        if isinstance(violations, (int, float)) and abs(violations) < 1e-6:
            if energy < best_energy:
                best_energy = energy
                best_solution = solution

    if best_solution is None:
        raise ValueError("No feasible solution found in brute force search")

    return best_solution, best_energy


def run_bruteforce_sweep():
    """
    Run brute force across multiple small scheduling instances
    and export results to CSV.
    """

    print("\n=== BRUTE FORCE SWEEP ===")

    test_cases = [
        (2, 2),
        (3, 2),
        (4, 2),
        (3, 3),
        (4, 3),
    ]

    rows = []

    for tasks, slots in test_cases:
        problem = build_scheduling_problem(tasks, slots)
        n = problem.n_vars

        start = time.time()
        solution, energy = brute_force_optimum(problem)
        runtime = time.time() - start

        print(f"\nProblem: {tasks} tasks x {slots} slots (n={n})")
        print(f"  Energy: {energy}")
        print(f"  Time: {runtime:.6f}s")

        rows.append([
            tasks,
            slots,
            n,
            energy,
            runtime,
            solution
        ])

    # Save results
    output_file = "bruteforce_results.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tasks",
            "slots",
            "n_vars",
            "energy",
            "runtime",
            "solution"
        ])
        writer.writerows(rows)

    print(f"\nSaved results to {output_file}")


if __name__ == "__main__":
    run_bruteforce_sweep()