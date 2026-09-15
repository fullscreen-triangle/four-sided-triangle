"""
Experiment 1: The resolution floor (Theorem 2.3 / Corollary 2.4).

Claim under test: for every claim v in a random connected contact graph,
sigma(v) >= beta > 0, where beta is the graph's realised floor (the
minimum edge weight, since every edge lies in some singleton's cut and
the medium is reachable by construction). We verify this holds with zero
violations across many random graphs and sizes, and report the margin by
which it is exceeded.
"""
from __future__ import annotations
import os
from common import random_contact_graph, separation_cost, floor_of_graph, MEDIUM, save_json, RESULTS_DIR


def run(seed: int = 1) -> dict:
    sizes = [3, 4, 5, 6, 8, 10, 12, 14]
    trials_per_size = 15
    records = []
    violations = 0
    min_ratio = float("inf")

    trial_id = 0
    for n in sizes:
        for t in range(trials_per_size):
            g = random_contact_graph(n_claims=n, seed=seed * 10000 + trial_id)
            beta = floor_of_graph(g)
            claims = [c for c in g.nodes if c != MEDIUM]
            for c in claims:
                sigma_v = separation_cost(g, c)
                ratio = sigma_v / beta
                min_ratio = min(min_ratio, ratio)
                if sigma_v < beta - 1e-9:
                    violations += 1
                records.append({
                    "n_claims": n,
                    "trial": trial_id,
                    "claim": c,
                    "sigma": sigma_v,
                    "beta": beta,
                    "ratio": ratio,
                })
            trial_id += 1

    result = {
        "experiment": "floor_from_noncompletability",
        "theorem": "Theorem 2.3 (Resolution Floor), Corollary 2.4 (No Exact Result)",
        "n_graphs": trial_id,
        "n_claim_observations": len(records),
        "violations": violations,
        "min_observed_ratio_sigma_over_beta": min_ratio,
        "passed": violations == 0 and min_ratio >= 1.0 - 1e-9,
        "sample_records": records[:20],
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp01_floor.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp01] violations={r['violations']} min_ratio={r['min_observed_ratio_sigma_over_beta']:.4f} passed={r['passed']}")
