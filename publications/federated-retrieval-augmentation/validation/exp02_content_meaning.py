"""
Experiment 2: Content and meaning provably diverge (Theorem 3.2).

Construction: two contact graphs over the same underlying claim labels --
a corpus graph Gph_C carved by lexical/topical similarity (content), and a
receiver graph Gph_R carved by a specific researcher's already-fixed
distinctions (meaning). We build an explicit instance in which the
content-nearest claim to a query is demonstrably NOT the meaning-nearest
claim in the receiver graph, and measure the gap.

Scenario (mirrors Example 3.1, "the true, irrelevant passage"):
  - query: an assay-failure question
  - claim T: a true, general textbook passage, high lexical overlap
  - claim E: the specific explanation the researcher actually needs,
             low lexical overlap
  - Gph_C ranks T above E by content similarity (edge weight to query
    proxy vertex = similarity)
  - Gph_R (already holding the specific assay/buffer/failure fixed)
    resolves E as individuating against "other candidate causes" (a rich,
    tightly-bound cell) while T individuates only against "other general
    kinetics statements" (a cell the researcher already holds as settled
    background, i.e. large separation cost from the *live* question node)
"""
from __future__ import annotations
import os
from common import (new_contact_graph, add_claim, add_contact, separation_cost,
                     alignment, MEDIUM, save_json, RESULTS_DIR)


def build_content_graph():
    """
    Gph_C: carved purely by lexical/topical similarity to the query.

    Alignment sigma(x, target) is a MINIMUM CUT separating x from target:
    a LARGE min-cut means x and target are densely, redundantly connected
    (hard to separate = similar / close); a SMALL min-cut means they are
    weakly connected (easy to separate = dissimilar / far). So "content
    winner" (higher lexical similarity) must be the claim with the LARGER
    alignment to the query proxy, not the smaller.
    """
    g = new_contact_graph()
    add_claim(g, "query_proxy", medium_weight=1.0)
    add_claim(g, "T_general_kinetics", medium_weight=1.0)
    add_claim(g, "E_specific_cause", medium_weight=1.0)
    # High lexical overlap: query_proxy <-> T is a dense, hard-to-cut bundle
    add_contact(g, "query_proxy", "T_general_kinetics", weight=9.0)
    # Low lexical overlap: query_proxy <-> E is a thin, easy-to-cut link
    add_contact(g, "query_proxy", "E_specific_cause", weight=1.0)
    return g


def build_receiver_graph():
    """
    Gph_R: the researcher's own graph, already holding the specific assay,
    buffer, and observed failure fixed as a tightly-linked cluster. T is
    background the researcher already possesses (individuates only against
    OTHER general statements, weakly tied to the live question); E
    individuates richly against the live cluster of candidate causes. As
    in build_content_graph, "closer to the live question" (usefulness)
    corresponds to a LARGER min-cut alignment (dense, hard-to-separate
    connection), not a smaller one.
    """
    g = new_contact_graph()
    add_claim(g, "live_question", medium_weight=1.0)
    add_claim(g, "T_general_kinetics", medium_weight=1.0)
    add_claim(g, "E_specific_cause", medium_weight=1.0)
    add_claim(g, "other_candidate_cause_1", medium_weight=1.0)
    add_claim(g, "other_candidate_cause_2", medium_weight=1.0)
    # T is isolated background: barely touches the live question
    add_contact(g, "live_question", "T_general_kinetics", weight=0.5)
    # E is richly tied to the live question and the other live candidates
    add_contact(g, "live_question", "E_specific_cause", weight=6.0)
    add_contact(g, "E_specific_cause", "other_candidate_cause_1", weight=4.0)
    add_contact(g, "E_specific_cause", "other_candidate_cause_2", weight=4.0)
    add_contact(g, "live_question", "other_candidate_cause_1", weight=3.0)
    add_contact(g, "live_question", "other_candidate_cause_2", weight=3.0)
    return g


def run(seed: int = 2) -> dict:
    gc = build_content_graph()
    gr = build_receiver_graph()

    # Content ranking: alignment of T and E to the query proxy in Gph_C.
    # A LARGER min-cut alignment means a denser, harder-to-separate (more
    # similar) connection, so the content winner is the claim with the
    # HIGHER alignment value.
    align_T_content = alignment(gc, "T_general_kinetics", "query_proxy")
    align_E_content = alignment(gc, "E_specific_cause", "query_proxy")
    content_winner = "T_general_kinetics" if align_T_content > align_E_content else "E_specific_cause"

    # Meaning ranking: alignment of T and E to the live_question in Gph_R,
    # same higher-is-closer convention.
    align_T_meaning = alignment(gr, "T_general_kinetics", "live_question")
    align_E_meaning = alignment(gr, "E_specific_cause", "live_question")
    meaning_winner = "T_general_kinetics" if align_T_meaning > align_E_meaning else "E_specific_cause"

    divergence = content_winner != meaning_winner

    result = {
        "experiment": "content_vs_meaning_divergence",
        "theorem": "Theorem 3.2 (Content and Meaning Come Apart), Example 3.1",
        "content_graph_alignment": {
            "T_general_kinetics": align_T_content,
            "E_specific_cause": align_E_content,
            "content_winner_higher_is_more_similar": content_winner,
        },
        "receiver_graph_alignment": {
            "T_general_kinetics": align_T_meaning,
            "E_specific_cause": align_E_meaning,
            "meaning_winner_higher_is_more_similar": meaning_winner,
        },
        "content_and_meaning_diverge": divergence,
        "passed": divergence and content_winner == "T_general_kinetics" and meaning_winner == "E_specific_cause",
        "interpretation": (
            "The passage a content-similarity retriever ranks first (T, the "
            "true general textbook statement) is exactly the passage the "
            "researcher's own receiver graph ranks as farther from the live "
            "question than the actually-useful specific explanation (E). "
            "This is the formal 'true but useless' failure of the paper's "
            "introduction, constructed explicitly rather than merely asserted."
        ),
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp02_content_meaning.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp02] content_winner={r['content_graph_alignment']['content_winner_higher_is_more_similar']} "
          f"meaning_winner={r['receiver_graph_alignment']['meaning_winner_higher_is_more_similar']} "
          f"passed={r['passed']}")
