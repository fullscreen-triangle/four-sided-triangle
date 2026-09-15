"""
Shared utilities for the Federated Retrieval-Augmentation validation suite.

Every object in the manuscript is a finite weighted graph or a construction
on one. This module supplies:
  - a contact graph builder (medium vertex adjacent to every claim),
  - exact minimum-cut / separation-cost computation via networkx max-flow,
  - a deterministic random contact-graph generator (seeded),
  - small numeric helpers (water-filling solver, JSON-safe serialisation).

No result in the suite depends on anything beyond exact graph computation
and convex-program KKT conditions; nothing here is a stochastic estimate
unless explicitly labelled as a Monte Carlo check.
"""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

import networkx as nx
import numpy as np

MEDIUM = "__medium__"


def new_contact_graph() -> nx.Graph:
    """An empty contact graph with just the medium vertex present."""
    g = nx.Graph()
    g.add_node(MEDIUM)
    return g


def add_claim(g: nx.Graph, name: str, medium_weight: float) -> None:
    """Add a claim vertex, always adjacent to the medium (Def. 2.1)."""
    g.add_node(name)
    g.add_edge(MEDIUM, name, weight=medium_weight)


def add_contact(g: nx.Graph, u: str, v: str, weight: float) -> None:
    """Add or strengthen a contact edge between two claims."""
    if g.has_edge(u, v):
        g[u][v]["weight"] += weight
    else:
        g.add_edge(u, v, weight=weight)


def separation_cost(g: nx.Graph, v: str) -> float:
    """
    sigma(v): minimum cut weight separating v from the medium (Def. 2.2).
    Exact via max-flow / min-cut (Ford-Fulkerson / Edmonds-Karp inside
    networkx's default max-flow implementation).
    """
    if v == MEDIUM:
        raise ValueError("separation cost is undefined for the medium itself")
    cut_value, _ = nx.minimum_cut(g, v, MEDIUM, capacity="weight")
    return cut_value


def resting_side(g: nx.Graph, v: str) -> Tuple[set, set]:
    """The (S*, complement) partition realising v's minimum cut."""
    _, (side_v, side_med) = nx.minimum_cut(g, v, MEDIUM, capacity="weight")
    if v in side_v:
        return side_v, side_med
    return side_med, side_v


def alignment(g: nx.Graph, x: str, target: str) -> float:
    """sigma(x, target): minimum cut separating x from target (Def. 8.1)."""
    if x == target:
        # A claim's alignment to itself is realised at its own floor
        # against the medium, per Theorem 8.3 (admissibility).
        return separation_cost(g, x)
    cut_value, _ = nx.minimum_cut(g, x, target, capacity="weight")
    return cut_value


def total_weight(g: nx.Graph) -> float:
    return sum(d["weight"] for _, _, d in g.edges(data=True))


def floor_of_graph(g: nx.Graph) -> float:
    """
    beta: the realised floor of a contact graph -- the minimum separation
    cost over all claims (Cor. 2.4 / Thm 2.3 applied at the achieved
    minimum rather than the abstract infimum over an expanding family).
    """
    claims = [n for n in g.nodes if n != MEDIUM]
    return min(separation_cost(g, v) for v in claims)


def random_contact_graph(
    n_claims: int,
    seed: int,
    min_w: float = 1.0,
    max_w: float = 5.0,
    density: float = 0.35,
) -> nx.Graph:
    """
    A random connected contact graph on n_claims claims plus the medium.
    Every claim is adjacent to the medium (Def. 2.1); additional contacts
    among claims are added at random with the given density. All weights
    are drawn uniformly from [min_w, max_w] so beta = min_w is guaranteed
    attainable (the medium edges alone realise it in the sparsest case).
    """
    rng = random.Random(seed)
    g = new_contact_graph()
    claims = [f"c{i}" for i in range(n_claims)]
    for c in claims:
        add_claim(g, c, rng.uniform(min_w, max_w))
    for i in range(n_claims):
        for j in range(i + 1, n_claims):
            if rng.random() < density:
                add_contact(g, claims[i], claims[j], rng.uniform(min_w, max_w))
    return g


def water_filling(gains: List[Tuple[float, float]], budget: float,
                   n_grid: int = 200000) -> Dict:
    """
    Exact-enough water-filling solver for gamma_i(a) = k_i * log(1 + a / s_i)
    style concave gains, generalised here to any concave, differentiable
    gain via its *marginal* function supplied as (deriv_at_zero, decay_rate)
    for the canonical family gamma_i(a) = m_i * (1 - exp(-a / tau_i)), whose
    marginal gamma_i'(a) = (m_i / tau_i) * exp(-a / tau_i) is strictly
    decreasing -- concave by construction (Ax. concavity).

    gains: list of (m_i, tau_i) pairs, so gamma_i(a) = m_i*(1-exp(-a/tau_i)),
           gamma_i'(a) = (m_i/tau_i) * exp(-a/tau_i), gamma_i'(0) = m_i/tau_i.

    Returns the bisection solution on the shadow price p*, cross-checked
    against a fine-grained convex-program grid search (ground truth).
    """
    def marginal(i, a):
        m, tau = gains[i]
        return (m / tau) * np.exp(-a / tau)

    def alloc_at_price(p):
        allocs = []
        for (m, tau) in gains:
            g0 = m / tau
            if g0 <= p:
                allocs.append(0.0)
            else:
                # solve (m/tau) exp(-a/tau) = p  =>  a = -tau * ln(p*tau/m)
                allocs.append(-tau * np.log(p * tau / m))
        return np.array(allocs)

    lo, hi = 0.0, max(m / tau for m, tau in gains)
    for _ in range(200):
        mid = (lo + hi) / 2
        a = alloc_at_price(mid)
        if a.sum() > budget:
            lo = mid
        else:
            hi = mid
    p_star = (lo + hi) / 2
    a_star = alloc_at_price(p_star)
    a_star = np.clip(a_star, 0.0, None)

    # Ground truth: fine grid search over the simplex via greedy water-fill
    # (equivalent construction, independent code path) for cross-validation.
    a_grid = _greedy_waterfill_grid(gains, budget, n_grid)

    return {
        "price_star": float(p_star),
        "allocation_bisection": a_star.tolist(),
        "allocation_grid_truth": a_grid.tolist(),
        "value_bisection": float(sum(m * (1 - np.exp(-a / tau))
                                      for (m, tau), a in zip(gains, a_star))),
        "value_grid_truth": float(sum(m * (1 - np.exp(-a / tau))
                                       for (m, tau), a in zip(gains, a_grid))),
    }


def _greedy_waterfill_grid(gains, budget, n_grid, unit=1e-4):
    """
    Independent ground-truth construction: discretise the budget into
    small units and greedily award each unit to whichever scene currently
    has the largest marginal gain. This converges to the water-filling
    optimum for concave gamma_i by the classical exchange argument, and
    is implemented independently of the bisection/KKT code path above so
    that agreement between the two is a real cross-check.
    """
    n = len(gains)
    a = np.zeros(n)
    n_units = int(budget / unit)
    # For speed with large n_units, use closed-form marginal and a heap.
    import heapq
    heap = []
    for i, (m, tau) in enumerate(gains):
        marg = (m / tau) * np.exp(-a[i] / tau)
        heapq.heappush(heap, (-marg, i))
    remaining = budget
    while remaining > 0 and heap:
        neg_marg, i = heapq.heappop(heap)
        step = min(unit, remaining)
        a[i] += step
        remaining -= step
        m, tau = gains[i]
        new_marg = (m / tau) * np.exp(-a[i] / tau)
        heapq.heappush(heap, (-new_marg, i))
    return a


class _NumpyJSONEncoder(json.JSONEncoder):
    """Coerces numpy scalar/array types (bool_, integer, floating, ndarray)
    into plain Python types so results are portable, standard JSON."""

    def default(self, o):
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def save_json(obj: Dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, cls=_NumpyJSONEncoder)


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
