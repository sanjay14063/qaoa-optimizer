# Hybrid Optimizer Experiments (QAOA vs Classical)

## Overview
This project benchmarks a classical optimizer against a QAOA-based simulator on a constrained scheduling problem. The focus is straightforward: compare solution quality, stability, and runtime as problem size increases.

---

## How to Run

```bash
pip install -r requirements.txt
python engine/plot_results.py
```

---

## Results (Visual)

![Runtime Scaling](results/plots/runtime_scaling.png)
![Solution Quality](results/plots/energy_comparison.png)
![QAOA Variance](results/plots/qaoa_variance.png)

---

## Problem Setup
Tasks are assigned to time slots under constraints, formulated as a QUBO (Quadratic Unconstrained Binary Optimization).

Objective: minimize total cost while respecting all constraints.

---

## Approach

**Classical solver**
- Deterministic
- Used as the ground truth baseline

**QAOA simulator**
- Parameterized quantum circuit
- Grid search with multiple restarts
- Evaluated via expectation values

---

## Results Interpretation

**Solution quality**
- Classical consistently reaches the optimum
- QAOA produces higher-energy (worse) solutions
- The gap increases with problem size

**Stability**
- QAOA variance is low
- Results are consistent but converge to suboptimal regions

**Runtime scaling**
- Classical scales gradually
- QAOA runtime increases rapidly and becomes impractical

---

## Conclusion
QAOA in this setup is:
- Stable but not competitive in solution quality
- Significantly slower as scale increases
- Limited by shallow circuits and basic parameter search

Overall: baseline QAOA does not outperform classical optimization here.

---

## Future Work
- Increase circuit depth (p)
- Use more advanced optimizers (e.g. gradient-based methods)
- Test under realistic noise models
- Run on actual quantum hardware

---

## Project Structure

```
OPTIMIZER/
├── engine/
├── results/
│   ├── plots/
│   └── data/
├── README.md
├── requirements.txt
├── .gitignore
```

---

## Notes
- Requires Python 3.x
- Only external dependencies: pandas, matplotlib
