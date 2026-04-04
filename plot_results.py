import pandas as pd
import matplotlib.pyplot as plt

# Load data
scaling = pd.read_csv("results/data/scaling_results.csv")

# Remove rows where QAOA failed
scaling_qaoa = scaling.dropna(subset=["t_qaoa", "E_qaoa_mean"])

# ---- Plot 1: Runtime scaling ----
plt.figure()
plt.plot(scaling["n_vars"], scaling["t_classical"], label="Classical")
plt.plot(scaling_qaoa["n_vars"], scaling_qaoa["t_qaoa"], label="QAOA")
plt.xlabel("Number of variables")
plt.ylabel("Time (seconds)")
plt.title("Runtime Scaling")
plt.legend()
plt.savefig("results/plots/runtime_scaling.png")

# ---- Plot 2: Energy comparison ----
plt.figure()
plt.plot(scaling["n_vars"], scaling["E_classical_mean"], label="Classical")
plt.plot(scaling_qaoa["n_vars"], scaling_qaoa["E_qaoa_mean"], label="QAOA")
plt.xlabel("Number of variables")
plt.ylabel("Energy")
plt.title("Solution Quality")
plt.legend()
plt.savefig("results/plots/energy_comparison.png")

# ---- Plot 3: QAOA error bars ----
plt.figure()
plt.errorbar(
    scaling_qaoa["n_vars"],
    scaling_qaoa["E_qaoa_mean"],
    yerr=scaling_qaoa["E_qaoa_std"],
    label="QAOA",
    capsize=5
)
plt.xlabel("Number of variables")
plt.ylabel("Energy")
plt.title("QAOA Stability (Error Bars)")
plt.legend()
plt.savefig("results/plots/qaoa_variance.png")