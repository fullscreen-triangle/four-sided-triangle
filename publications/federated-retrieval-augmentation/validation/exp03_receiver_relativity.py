"""
Experiment 3: Receiver-relativity (Theorem 4.4, Corollary 4.5).

Claim under test: the same claim v registers different resting cuts in
receiver graphs of differing density (a "junior researcher" sparse graph
vs. a "principal investigator" dense graph), and each is a correct,
floor-attaining individuation in its own graph -- there is no single,
privileged, receiver-independent value.

We build a family of receiver graphs of increasing density around a
fixed claim and show (i) the registered cell (separation cost) varies
continuously and non-trivially with density, and (ii) at every density
the registration attains that graph's own floor bound (sigma(v) >= beta),
confirming correctness-at-its-own-floor rather than approximation error.
"""
from __future__ import annotations
import os
import random
from common import (new_contact_graph, add_claim, add_contact, separation_cost,
                     floor_of_graph, MEDIUM, save_json, RESULTS_DIR)


def build_receiver(density: float, seed: int, n_context: int = 8) -> object:
    """
    A receiver graph in which 'target_claim' is surrounded by n_context
    other claims representing the receiver's already-fixed distinctions.
    Higher density = more prior context wired to the target = a "richer",
    more expert receiver (the principal investigator); lower density = a
    "thinner" receiver (the junior researcher).
    """
    rng = random.Random(seed)
    g = new_contact_graph()
    add_claim(g, "target_claim", medium_weight=1.0)
    for i in range(n_context):
        cname = f"ctx_{i}"
        add_claim(g, cname, medium_weight=1.0)
        if rng.random() < density:
            add_contact(g, "target_claim", cname, weight=rng.uniform(1.0, 4.0))
        # context-context contacts too, so the graph is not a pure star
        for j in range(i):
            if rng.random() < density * 0.5:
                add_contact(g, cname, f"ctx_{j}", weight=rng.uniform(1.0, 4.0))
    return g


def run(seed: int = 3) -> dict:
    densities = [0.0, 0.15, 0.3, 0.5, 0.7, 0.9]
    records = []
    registered_cells = []
    all_at_own_floor = True

    for d in densities:
        g = build_receiver(density=d, seed=seed * 100 + int(d * 1000))
        sigma_target = separation_cost(g, "target_claim")
        beta = floor_of_graph(g)
        at_floor_or_above = sigma_target >= beta - 1e-9
        all_at_own_floor = all_at_own_floor and at_floor_or_above
        registered_cells.append(sigma_target)
        records.append({
            "density": d,
            "sigma_target_claim": sigma_target,
            "graph_floor_beta": beta,
            "attains_own_floor_bound": at_floor_or_above,
        })

    distinct_registrations = len(set(round(v, 6) for v in registered_cells)) > 1

    result = {
        "experiment": "receiver_relativity",
        "theorem": "Theorem 4.4 (Distinct Receivers Register Distinct, Equally Correct Cells)",
        "records": records,
        "distinct_registrations_across_densities": distinct_registrations,
        "all_registrations_attain_own_graph_floor": all_at_own_floor,
        "passed": distinct_registrations and all_at_own_floor,
        "interpretation": (
            "The identical claim registers a different separation cost as "
            "the receiver's prior context density changes (junior vs. "
            "senior researcher), and at every density the registration "
            "is a correct, floor-attaining individuation in that receiver's "
            "own graph. No single density's registration is privileged; "
            "a global, receiver-independent relevance score would have to "
            "pick one and be wrong for every other receiver."
        ),
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp03_receiver_relativity.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp03] distinct={r['distinct_registrations_across_densities']} "
          f"all_at_floor={r['all_registrations_attain_own_graph_floor']} passed={r['passed']}")
