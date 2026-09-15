"""
Experiment 9: Water-filling attention allocation against an exact
convex-program solver (Theorem 10.4), including the concave / non-concave
boundary case (Remark on water-filling's failure mode).

We solve max sum_i gamma_i(a_i) s.t. sum a_i <= budget, a_i >= 0, for
gamma_i(a) = m_i * (1 - exp(-a/tau_i)) (strictly concave), via:
  (a) bisection on the KKT shadow price (closed-form per-scene inversion),
  (b) an independent greedy grid-search ground truth,
and confirm they agree to high precision across many random instances.
We then construct a NON-concave scene (a sigmoid gain with an initial
flat region) and confirm the water-filling price-equalisation rule is
violated there, i.e. that the guarantee is correctly conditional on
concavity, exactly as flagged in the manuscript.
"""
from __future__ import annotations
import os
import random
import numpy as np
from common import water_filling, save_json, RESULTS_DIR


def run(seed: int = 9) -> dict:
    rng = random.Random(seed)
    checks = []
    max_alloc_l2_error = 0.0
    max_value_error = 0.0

    for trial in range(30):
        n = rng.randint(2, 6)
        gains = [(rng.uniform(1.0, 5.0), rng.uniform(0.5, 3.0)) for _ in range(n)]
        budget = rng.uniform(1.0, 10.0)
        res = water_filling(gains, budget)
        a_bis = np.array(res["allocation_bisection"])
        a_grid = np.array(res["allocation_grid_truth"])
        l2_err = float(np.linalg.norm(a_bis - a_grid))
        val_err = abs(res["value_bisection"] - res["value_grid_truth"])
        max_alloc_l2_error = max(max_alloc_l2_error, l2_err)
        max_value_error = max(max_value_error, val_err)
        checks.append({
            "trial": trial, "n_scenes": n, "budget": budget,
            "gains": gains, "price_star": res["price_star"],
            "allocation_l2_error_bisection_vs_grid": l2_err,
            "value_error_bisection_vs_grid": val_err,
            "budget_respected": bool(a_bis.sum() <= budget + 1e-6),
        })

    solver_agrees = max_alloc_l2_error < 0.05 and max_value_error < 0.01

    # --- Non-concave boundary case ---
    # gamma(a) with an increasing-returns region: a sigmoid that starts
    # flat then rises steeply. Water-filling (equal-marginal) is NOT
    # optimal here; the true optimum concentrates budget on one scene.
    def sigmoid_gain(a, midpoint=4.0, steepness=3.0, scale=5.0):
        # Subtract the value at a=0 so gamma(0)=0 (Def. 10.2 requires
        # gamma(0)=0); the increasing-returns region below the midpoint
        # is what breaks concavity.
        raw = scale / (1 + np.exp(-steepness * (a - midpoint)))
        raw0 = scale / (1 + np.exp(steepness * midpoint))
        return raw - raw0

    budget_nc = 5.0  # strictly less than the midpoint: neither scene alone
                      # can reach the steep part on a 50/50 split, but one
                      # scene concentrating the whole budget can approach it
    a_grid_nc = np.linspace(0, budget_nc, 5001)

    # Two identical non-concave scenes; check whether the value-maximising
    # split is "concentrate on one" vs "equal split" (what water-filling
    # would prescribe by symmetry).
    def total_value(a1):
        a2 = budget_nc - a1
        return sigmoid_gain(a1) + sigmoid_gain(a2)

    values = [total_value(a1) for a1 in a_grid_nc]
    best_idx = int(np.argmax(values))
    best_a1 = float(a_grid_nc[best_idx])
    best_value = float(values[best_idx])
    equal_split_value = total_value(budget_nc / 2)
    # The water-filling equal-marginal point is the interior equal split;
    # the true grid optimum over the WHOLE non-concave objective must beat
    # it strictly for the failure mode to be real (rather than merely
    # comparing two arbitrary points, we compare the true optimum against
    # what water-filling would have prescribed).
    grid_optimum_beats_equal_split = best_value > equal_split_value + 1e-6
    optimum_is_at_or_near_extreme = best_a1 < 0.5 or best_a1 > budget_nc - 0.5

    result = {
        "experiment": "water_filling_attention_allocation",
        "theorem": "Theorem 10.4 (Water-Filling Attention Division); non-concave failure mode",
        "concave_case": {
            "n_trials": len(checks),
            "max_allocation_l2_error_bisection_vs_grid": max_alloc_l2_error,
            "max_value_error_bisection_vs_grid": max_value_error,
            "solver_agrees_with_independent_ground_truth": solver_agrees,
            "sample_checks": checks[:8],
        },
        "non_concave_boundary_case": {
            "budget": budget_nc,
            "equal_split_value": equal_split_value,
            "grid_optimum_a1": best_a1,
            "grid_optimum_value": best_value,
            "grid_optimum_beats_equal_split": grid_optimum_beats_equal_split,
            "optimum_is_at_or_near_extreme": optimum_is_at_or_near_extreme,
        },
        "passed": solver_agrees and grid_optimum_beats_equal_split and optimum_is_at_or_near_extreme,
        "interpretation": (
            "In the concave regime, the bisection water-filling solver "
            "matches an independent greedy grid-search ground truth to "
            "high precision across random instances, confirming Theorem "
            "10.4. In the constructed non-concave (sigmoidal, increasing- "
            "returns) regime, concentrating the whole budget on one scene "
            "strictly beats an equal split, and the true grid optimum sits "
            "at or near an extreme allocation rather than the interior "
            "equal-marginal point water-filling would prescribe -- exactly "
            "the failure mode the manuscript flags as conditional on the "
            "diminishing-returns assumption, confirmed rather than merely "
            "asserted."
        ),
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp09_waterfilling.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp09] concave_ok={r['concave_case']['solver_agrees_with_independent_ground_truth']} "
          f"nonconcave_confirmed={r['non_concave_boundary_case']['grid_optimum_beats_equal_split']} passed={r['passed']}")
