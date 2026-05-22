# Hybrid Optimizer Experiments (QAOA vs Classical)

## Overview
This project benchmarks a classical optimization method against a quantum-inspired QAOA simulator on a constrained scheduling problem. The goal is to compare solution quality, stability, and runtime as the problem size increases.

A small set of controlled experiments was run, with results exported to CSV and visualized using plots included below.

---

## Paper

[Read the full paper (PDF)](docs/hybrid_optimizer_paper.pdf)

---

## Key Results

### Runtime Scaling
![Runtime Scaling](results/plots/runtime_scaling.png)

### Solution Quality
![Solution Quality](results/plots/energy_comparison.png)

### QAOA Variance
![QAOA Variance](results/plots/qaoa_variance.png)

**Summary:**
- Classical optimization consistently finds optimal solutions.
- QAOA produces competitive but generally less reliable solutions.
- QAOA runtime scales exponentially due to statevector simulation.

---

## Problem Formulation
The task scheduling problem is encoded as a QUBO (Quadratic Unconstrained Binary Optimization):

- Each task must be assigned to exactly one time slot.
- Each assignment has an associated cost.
- Constraints are enforced through the QUBO formulation.

Objective: minimize total cost while satisfying all constraints.

---

## Methods

### Classical Solver
- Simulated annealing
- Run multiple times per instance (best result selected)
- Serves as a baseline for performance and accuracy

### QAOA Simulator
- Classical simulation of a single-layer (p=1) QAOA circuit
- Grid search over parameters (γ, β)
- Evaluated using expectation values
- Limited to small problem sizes due to 2^n scaling

---

## Experimental Setup
- Problem sizes range from small benchmark instances (n = 4) to larger cases approaching n ≈ 20 for QAOA simulation
- Metrics recorded:
  - Solution energy
  - Runtime
  - Optimality gap (when ground truth is available)
- Results exported to `results/data/` as CSV files

---

## Interpretation

**Solution Quality**
- Classical solver consistently achieves optimal solutions
- QAOA results degrade slightly as problem size increases

**Stability**
- QAOA variance is low
- Results are consistent but not always optimal

**Runtime Scaling**
- Classical runtime grows gradually
- QAOA runtime grows exponentially due to full statevector simulation and becomes impractical beyond n ≈ 18–20

---

## Conclusion
In this setup, QAOA does not outperform classical optimization:

- Classical methods are faster and more reliable
- QAOA is limited by simulation constraints
- Useful primarily as a conceptual or research tool at small scales

---

## Future Work
- Increase QAOA circuit depth (p > 1)
- Replace grid search with gradient-based optimization
- Incorporate noise models
- Test on real quantum hardware

---

## Project Structure

```
OPTIMIZER/
├── engine/                 # core implementation
├── results/
│   ├── plots/              # generated figures
│   └── data/               # CSV outputs
├── docs/
│   ├── hybrid_optimizer_paper.md   # editable paper draft
│   └── hybrid_optimizer_paper.pdf  # PDF version of paper
├── README.md
├── requirements.txt
```

---

## Notes
- Python 3.x required
- Dependencies: pandas, matplotlib
- All experiments are reproducible via provided scripts
