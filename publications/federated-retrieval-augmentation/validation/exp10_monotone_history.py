"""
Experiment 10: Monotone, irreversible agent history and the incoherence
of a cached fetch across a state change (Theorem 10.6, Remark 10.7).

We simulate an agent's committed count across a session of acts,
including deliberate "attack" operations (rollback attempt, fetch-cache
attempt) and confirm:
  (a) the committed count never decreases under any legitimate operation,
  (b) an attempted rollback is itself registered as a further committed
      act (raising the count further, never restoring a prior one),
  (c) a "fetch" that returns an answer computed at an earlier count is
      demonstrably stale relative to a fresh search run against the
      CURRENT graph once the graph has changed between the two counts.
"""
from __future__ import annotations
import os
import random
from common import (new_contact_graph, add_claim, add_contact, separation_cost,
                     MEDIUM, save_json, RESULTS_DIR)


class Agent:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.graph = new_contact_graph()
        add_claim(self.graph, "q_target", medium_weight=2.0)
        self.count = 0
        self.history = [{"count": 0, "event": "init"}]

    def commit_act(self, event_name):
        self.count += 1
        self.history.append({"count": self.count, "event": event_name})

    def grow_graph(self):
        """A committed act that adds a new claim, strengthening the
        answer's individuation (mirrors the corpus/graph accreting over
        a session, e.g. new documents ingested or new context fixed)."""
        cname = f"ctx_{self.count}"
        add_claim(self.graph, cname, medium_weight=1.0)
        add_contact(self.graph, "q_target", cname, weight=self.rng.uniform(1.0, 3.0))
        self.commit_act(f"grow_graph:{cname}")

    def fresh_search_answer(self):
        """Search-not-fetch: always recompute against the CURRENT graph."""
        self.commit_act("fresh_search")
        return separation_cost(self.graph, "q_target")

    def attempt_rollback(self):
        """An 'undo' is itself a further committed act -- it cannot lower
        the count (Theorem 10.6(ii))."""
        count_before = self.count
        self.commit_act("attempted_rollback")
        return self.count > count_before  # must be True: count only rose


def run(seed: int = 10) -> dict:
    agent = Agent(seed)

    counts_over_time = [agent.count]
    for _ in range(6):
        agent.grow_graph()
        counts_over_time.append(agent.count)

    # Snapshot a "fetch" answer at this count.
    stale_count = agent.count
    stale_answer = separation_cost(agent.graph, "q_target")

    # Agent continues to grow (new committed acts change the graph).
    for _ in range(5):
        agent.grow_graph()
        counts_over_time.append(agent.count)

    current_count = agent.count
    fresh_answer = agent.fresh_search_answer()
    counts_over_time.append(agent.count)

    # Rollback attempt: must raise the count, never lower it.
    rollback_raised_count = agent.attempt_rollback()
    counts_over_time.append(agent.count)

    monotone = all(counts_over_time[i] <= counts_over_time[i + 1]
                   for i in range(len(counts_over_time) - 1))
    strictly_increasing_on_acts = len(set(counts_over_time)) == len(counts_over_time)

    fetch_is_stale = abs(stale_answer - fresh_answer) > 1e-9
    fetch_count_mismatch = stale_count != current_count

    result = {
        "experiment": "monotone_irreversible_history",
        "theorem": "Theorem 10.6 (Monotone History), Remark 10.7 (No Caching Across Sessions)",
        "counts_over_time": counts_over_time,
        "monotone_nondecreasing": monotone,
        "strictly_increasing_per_committed_act": strictly_increasing_on_acts,
        "rollback_attempt_raised_count_never_lowered": rollback_raised_count,
        "stale_fetch": {
            "count_at_snapshot": stale_count,
            "answer_at_snapshot": stale_answer,
            "count_at_current": current_count,
            "fresh_answer_at_current": fresh_answer,
            "counts_differ": fetch_count_mismatch,
            "answers_differ": fetch_is_stale,
        },
        "passed": (monotone and strictly_increasing_on_acts and rollback_raised_count
                   and fetch_count_mismatch and fetch_is_stale),
        "interpretation": (
            "The committed count is strictly monotone across every "
            "legitimate act and even across an explicit rollback attempt, "
            "which itself only ever raises the count -- confirming no "
            "operation restores a prior state. A value cached at an "
            "earlier count and returned as a 'fetch' once the graph has "
            "since grown is numerically stale relative to a fresh search "
            "against the current graph, the direct computational "
            "confirmation of Proposition 10.5's fetch-incoherence argument."
        ),
    }
    save_json(result, os.path.join(RESULTS_DIR, "exp10_monotone_history.json"))
    return result


if __name__ == "__main__":
    r = run()
    print(f"[exp10] monotone={r['monotone_nondecreasing']} "
          f"fetch_stale={r['stale_fetch']['answers_differ']} passed={r['passed']}")
