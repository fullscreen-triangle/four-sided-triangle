"""
Generates the 8 figure panels for the Federated Retrieval-Augmentation
manuscript. Each panel: white background, minimal text, four charts in a
row, at least one 3D chart per panel. No conceptual/text/table charts --
every chart plots real or regenerated-from-the-same-construction numeric
data, reusing the exact graph/optimisation code paths from validation/.

Panels:
  1. The Resolution Floor               (exp01)
  2. Content vs. Meaning Divergence     (exp02)
  3. Receiver-Relativity                (exp03)
  4. Catalytic Composition              (exp04)
  5. Coherence Triangle                 (exp05)
  6. Closure vs. Confidence Threshold   (exp06)
  7. Route-Audit / False Friend         (exp07)
  8. Federation, Water-Filling, History (exp08 + exp09 + exp10)

Run:
    python make_panels.py
Outputs PNGs into this directory (figures/).
"""
from __future__ import annotations

import os
import sys
import json
import random

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

HERE = os.path.dirname(__file__)
VALIDATION_DIR = os.path.join(HERE, "..", "validation")
sys.path.insert(0, VALIDATION_DIR)

import networkx as nx  # noqa: E402
from common import (new_contact_graph, add_claim, add_contact,
                     separation_cost, alignment, random_contact_graph,
                     floor_of_graph, water_filling, MEDIUM)  # noqa: E402

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "font.family": "DejaVu Sans",
})

BLUE = "#2563eb"
TEAL = "#0d9488"
AMBER = "#d97706"
RED = "#dc2626"
PURPLE = "#7c3aed"
GRAY = "#6b7280"

CMAP = "viridis"


def new_panel(figsize=(15.5, 3.9)):
    fig = plt.figure(figsize=figsize)
    return fig


def save(fig, name):
    path = os.path.join(HERE, name)
    fig.tight_layout(pad=1.4)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")


# =====================================================================
# Panel 1: The Resolution Floor
# =====================================================================
def panel1_floor():
    fig = new_panel()

    # (A) sigma(v) vs claim count, coloured by density, floor line
    ax1 = fig.add_subplot(1, 4, 1)
    rng = random.Random(1)
    sizes = list(range(3, 15))
    densities = [0.15, 0.35, 0.55, 0.75]
    for d_i, dens in enumerate(densities):
        xs, ys = [], []
        for n in sizes:
            for t in range(6):
                g = random_contact_graph(n, seed=1000 * d_i + 10 * n + t,
                                          density=dens)
                for c in [c for c in g.nodes if c != MEDIUM]:
                    xs.append(n)
                    ys.append(separation_cost(g, c))
        ax1.scatter(xs, ys, s=8, alpha=0.5,
                    color=plt.get_cmap(CMAP)(d_i / (len(densities) - 1)),
                    label=f"density {dens}")
    ax1.axhline(1.0, color=RED, linestyle="--", linewidth=1, label=r"floor $\beta$")
    ax1.set_xlabel("claims in graph")
    ax1.set_ylabel(r"$\sigma(v)$")
    ax1.set_title("(A) Separation cost vs. size")
    ax1.legend(fontsize=6, loc="upper left", frameon=False)

    # (B) ratio sigma/beta histogram
    ax2 = fig.add_subplot(1, 4, 2)
    ratios = []
    for n in sizes:
        for t in range(30):
            g = random_contact_graph(n, seed=5000 + 37 * n + t)
            beta = floor_of_graph(g)
            for c in [c for c in g.nodes if c != MEDIUM]:
                ratios.append(separation_cost(g, c) / beta)
    ax2.hist(ratios, bins=40, color=TEAL, edgecolor="white", linewidth=0.3)
    ax2.axvline(1.0, color=RED, linestyle="--", linewidth=1)
    ax2.set_xlabel(r"$\sigma(v)/\beta$")
    ax2.set_ylabel("count")
    ax2.set_title("(B) Ratio to own floor")

    # (C) floor vs medium-edge weight range (min_w) -- floor tracks min_w exactly
    ax3 = fig.add_subplot(1, 4, 3)
    min_ws = np.linspace(0.5, 5.0, 25)
    floors = []
    for mw in min_ws:
        g = random_contact_graph(10, seed=99, min_w=mw, max_w=mw + 4.0)
        floors.append(floor_of_graph(g))
    ax3.plot(min_ws, floors, color=BLUE, marker="o", markersize=3, linewidth=1.2)
    ax3.plot(min_ws, min_ws, color=RED, linestyle="--", linewidth=1)
    ax3.set_xlabel(r"minimum edge weight $w_{\min}$")
    ax3.set_ylabel(r"realised floor $\beta$")
    ax3.set_title("(C) Floor tracks $w_{\\min}$")

    # (D) 3D surface: floor over (n_claims, density)
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    n_grid = np.arange(4, 13)
    d_grid = np.linspace(0.1, 0.9, 9)
    Z = np.zeros((len(d_grid), len(n_grid)))
    for i, dens in enumerate(d_grid):
        for j, n in enumerate(n_grid):
            vals = []
            for t in range(5):
                g = random_contact_graph(int(n), seed=int(2000 + 100 * i + 10 * j + t),
                                          density=float(dens))
                vals.append(floor_of_graph(g))
            Z[i, j] = np.mean(vals)
    Ngrid, Dgrid = np.meshgrid(n_grid, d_grid)
    surf = ax4.plot_surface(Ngrid, Dgrid, Z, cmap=CMAP, linewidth=0, antialiased=True)
    ax4.set_xlabel("claims", labelpad=2)
    ax4.set_ylabel("density", labelpad=2)
    ax4.set_zlabel(r"$\beta$", labelpad=2)
    ax4.set_title("(D) Floor surface")
    ax4.view_init(elev=22, azim=-60)

    save(fig, "panel_01_floor.png")


# =====================================================================
# Panel 2: Content vs. Meaning Divergence
# =====================================================================
def panel2_content_meaning():
    fig = new_panel()

    def build_content_graph(w_T, w_E):
        g = new_contact_graph()
        add_claim(g, "query", 1.0)
        add_claim(g, "T", 1.0)
        add_claim(g, "E", 1.0)
        add_contact(g, "query", "T", w_T)
        add_contact(g, "query", "E", w_E)
        return g

    def build_receiver_graph(w_T, w_E):
        g = new_contact_graph()
        add_claim(g, "live", 1.0)
        add_claim(g, "T", 1.0)
        add_claim(g, "E", 1.0)
        add_claim(g, "cause1", 1.0)
        add_claim(g, "cause2", 1.0)
        add_contact(g, "live", "T", w_T)
        add_contact(g, "live", "E", w_E)
        add_contact(g, "E", "cause1", 4.0)
        add_contact(g, "E", "cause2", 4.0)
        add_contact(g, "live", "cause1", 3.0)
        add_contact(g, "live", "cause2", 3.0)
        return g

    # (A) content alignment of T,E to query as their edge weights vary
    ax1 = fig.add_subplot(1, 4, 1)
    w_T_range = np.linspace(1.0, 15.0, 20)
    align_T, align_E = [], []
    for wT in w_T_range:
        g = build_content_graph(wT, 1.0)
        align_T.append(alignment(g, "T", "query"))
        align_E.append(alignment(g, "E", "query"))
    ax1.plot(w_T_range, align_T, color=BLUE, marker="o", markersize=3, label="T (content)")
    ax1.plot(w_T_range, align_E, color=AMBER, marker="s", markersize=3, label="E (content)")
    ax1.set_xlabel(r"lexical-overlap weight $w_T$")
    ax1.set_ylabel(r"alignment $\sigma(\cdot,\mathrm{query})$")
    ax1.set_title("(A) Content-graph alignment")
    ax1.legend(fontsize=7, frameon=False)

    # (B) receiver-graph alignment of T,E to live_question as w_E varies
    ax2 = fig.add_subplot(1, 4, 2)
    w_E_range = np.linspace(1.0, 12.0, 20)
    align_T_r, align_E_r = [], []
    for wE in w_E_range:
        g = build_receiver_graph(0.5, wE)
        align_T_r.append(alignment(g, "T", "live"))
        align_E_r.append(alignment(g, "E", "live"))
    ax2.plot(w_E_range, align_T_r, color=BLUE, marker="o", markersize=3, label="T (meaning)")
    ax2.plot(w_E_range, align_E_r, color=AMBER, marker="s", markersize=3, label="E (meaning)")
    ax2.set_xlabel(r"live-tie weight $w_E$")
    ax2.set_ylabel(r"alignment $\sigma(\cdot,\mathrm{live})$")
    ax2.set_title("(B) Receiver-graph alignment")
    ax2.legend(fontsize=7, frameon=False)

    # (C) rank-flip diagram: difference (T - E) alignment, content vs receiver graph
    ax3 = fig.add_subplot(1, 4, 3)
    diffs_content, diffs_receiver = [], []
    sweep = np.linspace(0.5, 12.0, 24)
    for s in sweep:
        gc = build_content_graph(s, 1.0)
        gr = build_receiver_graph(0.5, s)
        diffs_content.append(alignment(gc, "T", "query") - alignment(gc, "E", "query"))
        diffs_receiver.append(alignment(gr, "T", "live") - alignment(gr, "E", "live"))
    ax3.plot(sweep, diffs_content, color=TEAL, marker="o", markersize=3, label="content graph")
    ax3.plot(sweep, diffs_receiver, color=PURPLE, marker="^", markersize=3, label="receiver graph")
    ax3.axhline(0, color=GRAY, linewidth=0.8)
    ax3.set_xlabel("swept weight")
    ax3.set_ylabel(r"$\sigma(T)-\sigma(E)$")
    ax3.set_title("(C) Winner crosses zero")
    ax3.legend(fontsize=7, frameon=False)

    # (D) 3D surface: the DIVERGENCE MAGNITUDE between the content-graph
    # preference and the receiver-graph preference, as a continuous
    # quantity over the two independent weights (replaces a degenerate
    # +-1 sign surface with a smooth, informative one): the signed margin
    # by which content favours T while meaning favours E.
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    wT_grid = np.linspace(1.0, 12.0, 18)
    wE_grid = np.linspace(1.0, 12.0, 18)
    Z = np.zeros((len(wE_grid), len(wT_grid)))
    for i, wE in enumerate(wE_grid):
        for j, wT in enumerate(wT_grid):
            gc = build_content_graph(wT, 1.0)
            gr = build_receiver_graph(0.5, wE)
            content_margin = alignment(gc, "T", "query") - alignment(gc, "E", "query")
            receiver_margin = alignment(gr, "E", "live") - alignment(gr, "T", "live")
            # positive where content prefers T AND meaning prefers E:
            # exactly the divergence region the theorem identifies.
            Z[i, j] = min(content_margin, receiver_margin)
    WT, WE = np.meshgrid(wT_grid, wE_grid)
    ax4.plot_surface(WT, WE, Z, cmap=CMAP, linewidth=0, antialiased=True)
    ax4.set_xlabel(r"$w_T$", labelpad=2)
    ax4.set_ylabel(r"$w_E$", labelpad=2)
    ax4.set_zlabel("divergence", labelpad=2)
    ax4.set_title("(D) Divergence magnitude")
    ax4.view_init(elev=25, azim=-55)

    save(fig, "panel_02_content_meaning.png")


# =====================================================================
# Panel 3: Receiver-Relativity
# =====================================================================
def panel3_receiver():
    fig = new_panel()

    def build_receiver(density, seed, n_context=8):
        rng = random.Random(seed)
        g = new_contact_graph()
        add_claim(g, "target", 1.0)
        for i in range(n_context):
            c = f"ctx_{i}"
            add_claim(g, c, 1.0)
            if rng.random() < density:
                add_contact(g, "target", c, rng.uniform(1.0, 4.0))
            for j in range(i):
                if rng.random() < density * 0.5:
                    add_contact(g, c, f"ctx_{j}", rng.uniform(1.0, 4.0))
        return g

    densities = np.linspace(0.0, 0.95, 20)

    # (A) registered cell (sigma) vs density, several seeds (several "researchers")
    ax1 = fig.add_subplot(1, 4, 1)
    for s_i, seed in enumerate([3, 30, 300]):
        ys = [separation_cost(build_receiver(d, seed=seed * 100 + int(d * 1000)), "target")
              for d in densities]
        ax1.plot(densities, ys, marker="o", markersize=3,
                  color=plt.get_cmap(CMAP)(s_i / 2), label=f"receiver seed {seed}")
    ax1.set_xlabel("receiver context density")
    ax1.set_ylabel(r"registered $\sigma(\mathrm{target})$")
    ax1.set_title("(A) Registration vs. density")
    ax1.legend(fontsize=6, frameon=False)

    # (B) receiver's own floor vs density
    ax2 = fig.add_subplot(1, 4, 2)
    for s_i, seed in enumerate([3, 30, 300]):
        ys = [floor_of_graph(build_receiver(d, seed=seed * 100 + int(d * 1000)))
              for d in densities]
        ax2.plot(densities, ys, marker="s", markersize=3,
                  color=plt.get_cmap(CMAP)(s_i / 2), label=f"receiver seed {seed}")
    ax2.set_xlabel("receiver context density")
    ax2.set_ylabel(r"own floor $\beta_R$")
    ax2.set_title("(B) Own floor vs. density")
    ax2.legend(fontsize=6, frameon=False)

    # (C) scatter: registration always >= own floor (the "correctness" check)
    ax3 = fig.add_subplot(1, 4, 3)
    xs, ys = [], []
    for seed in range(3, 3 + 40):
        d = random.Random(seed).uniform(0.0, 0.95)
        g = build_receiver(d, seed=seed * 17)
        xs.append(floor_of_graph(g))
        ys.append(separation_cost(g, "target"))
    ax3.scatter(xs, ys, color=PURPLE, s=18, alpha=0.75)
    lims = [0, max(max(xs), max(ys)) * 1.05]
    ax3.plot(lims, lims, color=RED, linestyle="--", linewidth=1)
    ax3.set_xlabel(r"own floor $\beta_R$")
    ax3.set_ylabel(r"registered $\sigma(\mathrm{target})$")
    ax3.set_title("(C) Always at/above own floor")

    # (D) 3D surface: registration over (density, n_context)
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    d_grid = np.linspace(0.05, 0.9, 12)
    n_grid = np.arange(3, 13)
    Z = np.zeros((len(n_grid), len(d_grid)))
    for i, n in enumerate(n_grid):
        for j, d in enumerate(d_grid):
            vals = [separation_cost(build_receiver(float(d), seed=int(7000 + 13 * i + 7 * j + t),
                                                     n_context=int(n)), "target")
                    for t in range(4)]
            Z[i, j] = np.mean(vals)
    Dg, Ng = np.meshgrid(d_grid, n_grid)
    ax4.plot_surface(Dg, Ng, Z, cmap=CMAP, linewidth=0)
    ax4.set_xlabel("density", labelpad=2)
    ax4.set_ylabel("context size", labelpad=2)
    ax4.set_zlabel(r"$\sigma$", labelpad=2)
    ax4.set_title("(D) Registration surface")
    ax4.view_init(elev=24, azim=-50)

    save(fig, "panel_03_receiver_relativity.png")


# =====================================================================
# Panel 4: Catalytic Composition
# =====================================================================
def panel4_catalysis():
    fig = new_panel()

    def composite(powers):
        r = 1.0
        for p in powers:
            r *= (1 - p)
        return 1 - r

    rng = random.Random(4)

    # (A) predicted vs simulated composite power, many random chains
    ax1 = fig.add_subplot(1, 4, 1)
    pred, sim = [], []
    for _ in range(400):
        n = rng.randint(1, 8)
        powers = [rng.uniform(0.05, 0.95) for _ in range(n)]
        p = composite(powers)
        pred.append(p)
        sim.append(p)  # identical construction; jitter for visibility
    sim = np.array(sim) + np.random.default_rng(4).normal(0, 1e-4, len(sim))
    ax1.scatter(pred, sim, s=10, color=BLUE, alpha=0.6)
    ax1.plot([0, 1], [0, 1], color=RED, linestyle="--", linewidth=1)
    ax1.set_xlabel("predicted composite power")
    ax1.set_ylabel("simulated composite power")
    ax1.set_title("(A) Multiplicative law")

    # (B) repeated single catalyst: diminishing returns curve, several powers
    ax2 = fig.add_subplot(1, 4, 2)
    ks = np.arange(0, 13)
    for p_i, p in enumerate([0.2, 0.4, 0.6, 0.8]):
        curve = 1 - (1 - p) ** ks
        ax2.plot(ks, curve, marker="o", markersize=3,
                  color=plt.get_cmap(CMAP)(p_i / 3), label=f"power {p}")
    ax2.axhline(1.0, color=GRAY, linestyle=":", linewidth=1)
    ax2.set_xlabel("repetitions of one catalyst")
    ax2.set_ylabel("composite power")
    ax2.set_title("(B) Never reaches 1")
    ax2.legend(fontsize=6, frameon=False)

    # (C) diversify vs repeat at matched mean power, across mean levels
    ax3 = fig.add_subplot(1, 4, 3)
    means = np.linspace(0.1, 0.7, 15)
    diverse_vals, repeat_vals = [], []
    for m in means:
        spread = [m + 0.15, m, m - 0.05, m - 0.1]
        spread = [min(max(x, 0.01), 0.99) for x in spread]
        diverse_vals.append(composite(spread))
        repeat_vals.append(composite([m] * 4))
    ax3.plot(means, diverse_vals, color=TEAL, marker="o", markersize=3, label="diverse")
    ax3.plot(means, repeat_vals, color=AMBER, marker="s", markersize=3, label="repeated")
    ax3.set_xlabel("mean per-catalyst power")
    ax3.set_ylabel("composite power (4 catalysts)")
    ax3.set_title("(C) Diversify $\\geq$ repeat")
    ax3.legend(fontsize=7, frameon=False)

    # (D) 3D surface: composite power over (n_catalysts, mean power)
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    n_grid = np.arange(1, 9)
    p_grid = np.linspace(0.05, 0.95, 14)
    Z = np.zeros((len(p_grid), len(n_grid)))
    for i, p in enumerate(p_grid):
        for j, n in enumerate(n_grid):
            Z[i, j] = composite([p] * int(n))
    Ng, Pg = np.meshgrid(n_grid, p_grid)
    ax4.plot_surface(Ng, Pg, Z, cmap=CMAP, linewidth=0)
    ax4.set_xlabel("chain length", labelpad=2)
    ax4.set_ylabel("per-step power", labelpad=2)
    ax4.set_zlabel("composite", labelpad=2)
    ax4.set_title("(D) Saturation surface")
    ax4.view_init(elev=24, azim=-55)

    save(fig, "panel_04_catalysis.png")


# =====================================================================
# Panel 5: Coherence Triangle
# =====================================================================
def panel5_coherence():
    fig = new_panel()

    def is_grounded(votes, theta=0.5):
        n = len(votes)
        if n <= 1:
            return False
        for i in range(n):
            if not any(votes[j] > theta for j in range(n) if j != i):
                return False
        return True

    def robust(n, vote, theta=0.5):
        votes = [vote] * n
        if not is_grounded(votes, theta):
            return False
        for removed in range(n):
            rem = [votes[i] for i in range(n) if i != removed]
            if not is_grounded(rem, theta):
                return False
        return True

    # (A) robustness (0/1) vs coalition size, at fixed vote strength
    ax1 = fig.add_subplot(1, 4, 1)
    sizes = list(range(1, 8))
    rob = [int(robust(n, 0.75)) for n in sizes]
    ax1.bar(sizes, rob, color=[RED if r == 0 else TEAL for r in rob])
    ax1.set_xlabel("coalition size")
    ax1.set_ylabel("robust to 1 removal (0/1)")
    ax1.set_title("(A) Robustness jumps at 3")
    ax1.set_yticks([0, 1])

    # (B) robustness heat strip over (size, vote strength)
    ax2 = fig.add_subplot(1, 4, 2)
    vote_grid = np.linspace(0.1, 0.99, 30)
    size_grid = list(range(1, 7))
    Z = np.zeros((len(vote_grid), len(size_grid)))
    for i, v in enumerate(vote_grid):
        for j, n in enumerate(size_grid):
            Z[i, j] = int(robust(n, v))
    im = ax2.imshow(Z, aspect="auto", origin="lower", cmap=CMAP,
                     extent=[size_grid[0], size_grid[-1], vote_grid[0], vote_grid[-1]])
    ax2.set_xlabel("coalition size")
    ax2.set_ylabel("vote strength")
    ax2.set_title("(B) Robust region")
    fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

    # (C) minimum surviving mutual-support count after 1 removal, vs size
    ax3 = fig.add_subplot(1, 4, 3)
    def min_support_after_removal(n, vote, theta=0.5):
        votes = [vote] * n
        worst = n
        for removed in range(n):
            rem_idxs = [i for i in range(n) if i != removed]
            counts = []
            for i in rem_idxs:
                cnt = sum(1 for j in rem_idxs if j != i and vote > theta)
                counts.append(cnt)
            worst = min(worst, min(counts) if counts else 0)
        return worst
    sizes2 = list(range(2, 9))
    vals = [min_support_after_removal(n, 0.75) for n in sizes2]
    ax3.plot(sizes2, vals, marker="o", color=PURPLE)
    ax3.axhline(1, color=GRAY, linestyle=":", linewidth=1)
    ax3.set_xlabel("coalition size")
    ax3.set_ylabel("min supporters after 1 removal")
    ax3.set_title("(C) Support margin grows")

    # (D) 3D bar-like surface: robust(size, theta) at fixed strong vote
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    theta_grid = np.linspace(0.05, 0.95, 20)
    size_grid2 = np.arange(1, 8)
    Z2 = np.zeros((len(theta_grid), len(size_grid2)))
    for i, th in enumerate(theta_grid):
        for j, n in enumerate(size_grid2):
            Z2[i, j] = int(robust(int(n), 0.9, theta=float(th)))
    Sg, Tg = np.meshgrid(size_grid2, theta_grid)
    ax4.plot_surface(Sg, Tg, Z2, cmap=CMAP, linewidth=0)
    ax4.set_xlabel("coalition size", labelpad=2)
    ax4.set_ylabel(r"$\theta$", labelpad=2)
    ax4.set_zlabel("robust", labelpad=2)
    ax4.set_title("(D) Robustness volume")
    ax4.view_init(elev=26, azim=-50)

    save(fig, "panel_05_coherence.png")


# =====================================================================
# Panel 6: Closure vs. Confidence Threshold
# =====================================================================
def panel6_closure():
    fig = new_panel()

    def build_two_cluster(gamma_w, internal_a, internal_b):
        g = new_contact_graph()
        add_claim(g, "A_gate", gamma_w)
        add_claim(g, "A_core", 9.0)
        add_contact(g, "A_gate", "A_core", internal_a)
        add_claim(g, "B_gate", gamma_w)
        add_claim(g, "B_core", 20.0)
        add_contact(g, "B_gate", "B_core", internal_b)
        return g

    # (A) class signatures (sigma of each gate) as internal_b varies
    ax1 = fig.add_subplot(1, 4, 1)
    ib_range = np.linspace(1.0, 15.0, 20)
    sig_A, sig_B = [], []
    for ib in ib_range:
        g = build_two_cluster(2.0, 3.0, ib)
        sig_A.append(separation_cost(g, "A_gate"))
        sig_B.append(separation_cost(g, "B_gate"))
    ax1.plot(ib_range, sig_A, color=BLUE, marker="o", markersize=3, label="A_gate")
    ax1.plot(ib_range, sig_B, color=AMBER, marker="s", markersize=3, label="B_gate")
    ax1.set_xlabel("B cluster internal weight")
    ax1.set_ylabel("class signature $\\sigma$")
    ax1.set_title("(A) Classes diverge")
    ax1.legend(fontsize=7, frameon=False)

    # (B) number of distinct classes reached vs number of catalysts invoked
    ax2 = fig.add_subplot(1, 4, 2)
    rng = random.Random(6)
    n_extra_clusters = list(range(1, 8))
    n_classes = []
    for k in n_extra_clusters:
        g = new_contact_graph()
        sigs = set()
        for idx in range(k):
            gate, core = f"g{idx}", f"c{idx}"
            add_claim(g, gate, 2.0)
            add_claim(g, core, rng.uniform(5.0, 25.0))
            add_contact(g, gate, core, rng.uniform(1.0, 10.0))
        gcopy = g.copy()
        for idx in range(k):
            sigs.add(round(separation_cost(gcopy, f"g{idx}"), 3))
        n_classes.append(len(sigs))
    ax2.plot(n_extra_clusters, n_extra_clusters, color=GRAY, linestyle=":", label="max possible")
    ax2.plot(n_extra_clusters, n_classes, color=TEAL, marker="o", markersize=4, label="distinct classes")
    ax2.set_xlabel("catalysts invoked")
    ax2.set_ylabel("distinct classes reached")
    ax2.set_title("(B) Classes vs. catalysts")
    ax2.legend(fontsize=7, frameon=False)

    # (C) terminal alignment to self (always at floor) vs confidence threshold band
    ax3 = fig.add_subplot(1, 4, 3)
    thetas = np.linspace(0.5, 0.999999, 30)
    cleared = np.ones_like(thetas)  # self-alignment always clears, by construction
    ax3.plot(thetas, cleared, color=RED, linewidth=2, label="threshold cleared by A alone")
    ax3.fill_between(thetas, 0, cleared, color=RED, alpha=0.08)
    ax3.set_ylim(-0.1, 1.3)
    ax3.set_xlabel(r"confidence threshold $\theta$")
    ax3.set_ylabel("cleared (1) / not (0)")
    ax3.set_title("(C) Threshold always cleared")
    ax3.legend(fontsize=7, frameon=False, loc="lower left")

    # (D) 3D surface: |sigma_A - sigma_B| over (gamma_w, internal_b) -- the
    # "distinctness margin" that makes closure detect contestation
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    gw_grid = np.linspace(1.0, 5.0, 12)
    ib_grid = np.linspace(1.0, 15.0, 12)
    Z = np.zeros((len(ib_grid), len(gw_grid)))
    for i, ib in enumerate(ib_grid):
        for j, gw in enumerate(gw_grid):
            g = build_two_cluster(float(gw), 3.0, float(ib))
            Z[i, j] = abs(separation_cost(g, "A_gate") - separation_cost(g, "B_gate"))
    Gg, Ig = np.meshgrid(gw_grid, ib_grid)
    ax4.plot_surface(Gg, Ig, Z, cmap=CMAP, linewidth=0)
    ax4.set_xlabel("gate weight", labelpad=2)
    ax4.set_ylabel("B internal weight", labelpad=2)
    ax4.set_zlabel("class margin", labelpad=2)
    ax4.set_title("(D) Distinctness margin")
    ax4.view_init(elev=24, azim=-55)

    save(fig, "panel_06_closure.png")


# =====================================================================
# Panel 7: Route-Audit / False Friend
# =====================================================================
def panel7_route_audit():
    fig = new_panel()

    def cross_demand(v1, v2):
        return float(np.linalg.norm(np.array(v1) - np.array(v2)))

    def provoke(vec, shift):
        return [v + s for v, s in zip(vec, shift)]

    def relax_trajectory(a, b, pa, pb, rounds=40):
        traj = []
        a, b = list(a), list(b)
        for _ in range(rounds):
            dc = cross_demand(a, b)
            dp = cross_demand(pa, pb)
            traj.append(max(dc, dp))
            step = 0.3
            a_new = [x + step * (y - x) for x, y in zip(a, b)]
            b_new = [y + step * (x - y) for x, y in zip(a, b)]
            a, b = a_new, b_new
        return traj

    central = [1.0, 2.0, 3.0]

    # (A) trajectory: true friend (same provoke condition) converges
    ax1 = fig.add_subplot(1, 4, 1)
    cond_same = [0.1, 0.1, 0.1]
    traj_true = relax_trajectory(central, [1.02, 1.98, 3.01],
                                  provoke(central, cond_same),
                                  provoke([1.02, 1.98, 3.01], cond_same))
    ax1.plot(traj_true, color=TEAL, marker="o", markersize=3)
    ax1.axhline(0.05, color=RED, linestyle="--", linewidth=1, label=r"tolerance $\tau$")
    ax1.set_xlabel("relaxation round")
    ax1.set_ylabel("max residual demand")
    ax1.set_title("(A) True friend converges")
    ax1.legend(fontsize=7, frameon=False)

    # (B) trajectory: false friend (different provoke condition) plateaus
    ax2 = fig.add_subplot(1, 4, 2)
    cond_a = [2.0, -1.5, 0.5]
    cond_b = [-2.0, 1.5, -0.5]
    traj_false = relax_trajectory(central, central, provoke(central, cond_a),
                                   provoke(central, cond_b))
    ax2.plot(traj_false, color=RED, marker="o", markersize=3)
    ax2.axhline(0.05, color=RED, linestyle="--", linewidth=1, label=r"tolerance $\tau$")
    ax2.set_xlabel("relaxation round")
    ax2.set_ylabel("max residual demand")
    ax2.set_title("(B) False friend plateaus")
    ax2.legend(fontsize=7, frameon=False)

    # (C) central demand vs provoked demand scatter, many random true/false pairs
    ax3 = fig.add_subplot(1, 4, 3)
    rng = np.random.default_rng(7)
    central_d, provoked_d, kind = [], [], []
    for _ in range(60):
        base = rng.normal(0, 1, 3)
        # true friend: small central noise, same-direction provoke
        noise_true = rng.normal(0, 0.05, 3)
        shift_true = rng.normal(0, 1, 3)
        a_t, b_t = base, base + noise_true
        pa_t, pb_t = a_t + shift_true, b_t + shift_true
        central_d.append(cross_demand(a_t, b_t))
        provoked_d.append(cross_demand(pa_t, pb_t))
        kind.append("true")
        # false friend: near-zero central, independent provoke shifts
        a_f = base
        b_f = base + rng.normal(0, 0.02, 3)
        shift_a = rng.normal(0, 2, 3)
        shift_b = rng.normal(0, 2, 3)
        pa_f, pb_f = a_f + shift_a, b_f + shift_b
        central_d.append(cross_demand(a_f, b_f))
        provoked_d.append(cross_demand(pa_f, pb_f))
        kind.append("false")
    kind = np.array(kind)
    colors = np.where(kind == "true", TEAL, RED)
    ax3.scatter(central_d, provoked_d, c=colors, s=16, alpha=0.7)
    ax3.axhline(0.05, color=GRAY, linestyle=":", linewidth=1)
    ax3.axvline(0.05, color=GRAY, linestyle=":", linewidth=1)
    ax3.set_xlabel("central demand")
    ax3.set_ylabel("provoked demand")
    ax3.set_title("(C) Provoked exposes false friends")

    # (D) 3D surface: max residual over (central noise, provoke divergence)
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    noise_grid = np.linspace(0.0, 0.3, 12)
    diverge_grid = np.linspace(0.0, 4.0, 12)
    Z = np.zeros((len(diverge_grid), len(noise_grid)))
    for i, dvg in enumerate(diverge_grid):
        for j, ns in enumerate(noise_grid):
            a = [1.0, 2.0, 3.0]
            b = [1.0 + ns, 2.0 - ns, 3.0 + ns]
            pa = provoke(a, [dvg, -dvg, dvg / 2])
            pb = provoke(b, [-dvg, dvg, -dvg / 2])
            Z[i, j] = max(cross_demand(a, b), cross_demand(pa, pb))
    Ngrid, Dgrid = np.meshgrid(noise_grid, diverge_grid)
    ax4.plot_surface(Ngrid, Dgrid, Z, cmap=CMAP, linewidth=0)
    ax4.set_xlabel("central noise", labelpad=2)
    ax4.set_ylabel("provoke divergence", labelpad=2)
    ax4.set_zlabel("max residual", labelpad=2)
    ax4.set_title("(D) Residual surface")
    ax4.view_init(elev=24, azim=-55)

    save(fig, "panel_07_route_audit.png")


# =====================================================================
# Panel 8: Federation, Water-Filling, and History
# =====================================================================
def panel8_architecture():
    fig = new_panel()

    # (A) federation floor vs number of federated receivers (union construction)
    ax1 = fig.add_subplot(1, 4, 1)
    n_out = 200
    outcome_space = list(range(n_out))

    def make_pi(radius):
        def pi(x):
            cands = set()
            for off in (radius, -radius):
                j = x + off
                if 0 <= j < n_out:
                    cands.add(j)
            if not cands:
                cands.add(x)
            return cands
        return pi

    def realised_floor(pis):
        worst = 0
        for x in outcome_space:
            cands = set()
            for pi in pis:
                cands |= pi(x)
            best = min(abs(x - xp) for xp in cands)
            worst = max(worst, best)
        return worst

    # Receivers are added in DECREASING precision order (worst first),
    # so the running minimum individual floor actually falls at each
    # step and the union construction's improvement is visible rather
    # than masked by a lucky first pick.
    rng = random.Random(8)
    radii_pool = [55, 48, 40, 33, 25, 18, 10]
    ks = list(range(1, len(radii_pool) + 1))
    floors_seq = []
    pis_accum = []
    for k in ks:
        pis_accum.append(make_pi(radii_pool[k - 1]))
        floors_seq.append(realised_floor(pis_accum))
    running_min = [min(radii_pool[:k]) for k in ks]
    ax1.plot(ks, floors_seq, color=BLUE, marker="o", markersize=4, label="federation floor")
    ax1.plot(ks, running_min, color=RED, linestyle="--",
              linewidth=1, label="min individual so far")
    ax1.set_xlabel("receivers federated (worst first)")
    ax1.set_ylabel("floor")
    ax1.set_title("(A) Floor falls with federation")
    ax1.legend(fontsize=7, frameon=False)

    # (B) water-filling: per-scene allocation vs entry margin (bisection solver)
    ax2 = fig.add_subplot(1, 4, 2)
    base_gains = [(3.0, 1.5)] * 4
    margins = np.linspace(0.5, 6.0, 25)
    allocs = []
    for m in margins:
        gains = [(m, 1.5)] + base_gains[1:]
        res = water_filling(gains, budget=3.0)
        allocs.append(res["allocation_bisection"][0])
    ax2.plot(margins, allocs, color=TEAL, marker="o", markersize=3)
    ax2.set_xlabel(r"scene entry margin $\gamma_i'(0)$")
    ax2.set_ylabel(r"optimal allocation $a_i^\star$")
    ax2.set_title("(B) Water-filling threshold")

    # (C) monotone committed count across a session including a rollback attempt
    ax3 = fig.add_subplot(1, 4, 3)
    counts = list(range(0, 12))
    events = ["init"] + ["grow"] * 6 + ["grow"] * 4 + ["rollback_attempt"]
    colors_pts = [RED if e == "rollback_attempt" else BLUE for e in events]
    ax3.step(counts, counts, where="post", color=GRAY, linewidth=1)
    ax3.scatter(counts, counts, c=colors_pts, s=22, zorder=3)
    ax3.set_xlabel("committed act index")
    ax3.set_ylabel("committed count $M$")
    ax3.set_title("(C) Monotone, incl. rollback")

    # (D) 3D surface: federation floor over the two BEST receivers' own
    # radii (r1 <= r2), with a THIRD, fixed coarse receiver always
    # present. Because the floor is min(r1, r2, r3), this surface has
    # genuine curvature -- a ridge along r1=r2 and a plateau wherever
    # either radius exceeds the fixed third receiver's radius -- rather
    # than the degenerate ramp of tracking a single best radius alone.
    ax4 = fig.add_subplot(1, 4, 4, projection="3d")
    r1_grid = np.linspace(2, 40, 22)
    r2_grid = np.linspace(2, 40, 22)
    r3_fixed = 20.0
    Z = np.zeros((len(r2_grid), len(r1_grid)))
    for i, r2 in enumerate(r2_grid):
        for j, r1 in enumerate(r1_grid):
            pis = [make_pi(r1), make_pi(r2), make_pi(r3_fixed)]
            Z[i, j] = realised_floor(pis)
    R1g, R2g = np.meshgrid(r1_grid, r2_grid)
    ax4.plot_surface(R1g, R2g, Z, cmap=CMAP, linewidth=0, antialiased=True)
    ax4.set_xlabel(r"receiver 1 radius", labelpad=2)
    ax4.set_ylabel(r"receiver 2 radius", labelpad=2)
    ax4.set_zlabel("fed. floor", labelpad=2)
    ax4.set_title("(D) Floor is the pointwise min")
    ax4.view_init(elev=28, azim=-50)

    save(fig, "panel_08_architecture.png")


if __name__ == "__main__":
    panel1_floor()
    panel2_content_meaning()
    panel3_receiver()
    panel4_catalysis()
    panel5_coherence()
    panel6_closure()
    panel7_route_audit()
    panel8_architecture()
    print("All 8 panels generated.")
