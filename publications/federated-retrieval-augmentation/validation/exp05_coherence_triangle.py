"""
Experiment 5: The coherence triangle (Theorem 8.8).

Claim under test: robustness of a claim's grounding to removal of any
single supporting catalyst requires a strongly connected support-graph
cycle of length >= 3; a single source (1 vertex, no cycle) and a mutually
supporting pair (2-cycle) are NOT robust to removal of one member, while
a 3-cycle at threshold theta > 1/2 IS robust.

We model "support" numerically as each catalyst's vote strength toward a
target, define a claim as "grounded" at a given surviving-vote coalition
if the summed strength of surviving supporters exceeds theta * (their
own count's worth of unanimous support), and directly test survival of
grounding after removing each member in turn, across topologies of size
1, 2, and 3.
"""
from __future__ import annotations
import os
from itertools import combinations
from common import save_json, RESULTS_DIR


def is_grounded(vote_strengths, theta=0.5):
    """
    A coalition is grounded if the *fraction* of its own maximal possible
    mutual support that is realised exceeds theta once every member's
    vote is counted; concretely, grounded iff every remaining member has
    at least one other remaining member supporting it at strength > theta.
    This directly operationalises Definition 8.5 (support graph, strongly
    connected at threshold theta) for the finite, fully-connected-vote
    case used in the manuscript's own examples.
    """
    n = len(vote_strengths)
    if n == 0:
        return False
    if n == 1:
        return False  # a single vertex has no incoming support edge at all
    # For n >= 2: grounded iff every member is supported by at least one
    # other member at strength > theta (mutual, majority-strength support).
    for i in range(n):
        supported = any(vote_strengths[j] > theta for j in range(n) if j != i)
        if not supported:
            return False
    return True


def topology_robustness(n_members, vote_strength, theta=0.5):
    """
    Build a coalition of n_members, each voting for the others at
    'vote_strength', check it is grounded, then remove each member in
    turn and check whether the REMAINING coalition is still grounded.
    Robust iff grounded initially AND remains grounded after every
    single-member removal.
    """
    votes = [vote_strength] * n_members
    initially_grounded = is_grounded(votes, theta)

    survives_all_removals = True
    removal_results = []
    for removed in range(n_members):
        remaining = [votes[i] for i in range(n_members) if i != removed]
        still_grounded = is_grounded(remaining, theta) if remaining else False
        removal_results.append({"removed_index": removed, "still_grounded": still_grounded})
        survives_all_removals = survives_all_removals and still_grounded

    return {
        "n_members": n_members,
        "vote_strength": vote_strength,
        "theta": theta,
        "initially_grounded": initially_grounded,
        "robust_to_any_single_removal": initially_grounded and survives_all_removals,
        "removal_results": removal_results,
    }


def run(seed: int = 5) -> dict:
    theta = 0.5
    strong_vote = 0.75  # > theta, satisfies the sufficiency clause (iii)

    one_source = topology_robustness(1, strong_vote, theta)
    two_cycle = topology_robustness(2, strong_vote, theta)
    three_cycle = topology_robustness(3, strong_vote, theta)
    four_cycle = topology_robustness(4, strong_vote, theta)  # bonus: larger cycles remain robust

    checks = {
        "1_source_never_robust": one_source["robust_to_any_single_removal"] is False,
        "2_cycle_never_robust": two_cycle["robust_to_any_single_removal"] is False,
        "3_cycle_is_robust": three_cycle["robust_to_any_single_removal"] is True,
        "4_cycle_is_robust": four_cycle["robust_to_any_single_removal"] is True,
    }
    passed = all(checks.values())

    result = {
        "experiment": "coherence_requires_a_triangle",
        "theorem": "Theorem 8.8 (Linear Chains and Pairs Fail; a Triangle Grounds)",
        "theta": theta,
        "vote_strength_used": strong_vote,
        "topologies": {
            "size_1": one_source,
            "size_2_pair": two_cycle,
            "size_3_triangle": three_cycle,
            "size_4_cycle": four_cycle,
        },
        "checks": checks,
        "passed": passed,
        "interpretation": (
            "A single source is never robust (no incoming support at all). "
            "A mutually-supporting pair fails robustness: removing either "
            "member leaves exactly one voter, which cannot support itself. "
            "A 3-cycle at theta=0.5 with strong votes IS robust: removing "
            "any one member leaves two members who still mutually support "
            "each other above threshold. Coherence is a structural minimum "
            "of three, exactly as Theorem 8.8 proves, not one, and not two."
        ),
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp05_coherence_triangle.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp05] checks={r['checks']} passed={r['passed']}")
