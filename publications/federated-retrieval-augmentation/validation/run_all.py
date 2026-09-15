"""
Runs the full Federated Retrieval-Augmentation validation suite and
writes a machine-readable summary alongside the individual per-experiment
JSON records already written by each module into results/.

Usage:
    python run_all.py
"""
from __future__ import annotations
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from common import save_json, RESULTS_DIR  # noqa: E402

import exp01_floor
import exp02_content_meaning
import exp03_receiver_relativity
import exp04_multiplicative_law
import exp05_coherence_triangle
import exp06_closure_vs_threshold
import exp07_route_audit
import exp08_federation_floor
import exp09_waterfilling
import exp10_monotone_history

EXPERIMENTS = [
    ("exp01_floor", exp01_floor),
    ("exp02_content_meaning", exp02_content_meaning),
    ("exp03_receiver_relativity", exp03_receiver_relativity),
    ("exp04_multiplicative_law", exp04_multiplicative_law),
    ("exp05_coherence_triangle", exp05_coherence_triangle),
    ("exp06_closure_vs_threshold", exp06_closure_vs_threshold),
    ("exp07_route_audit", exp07_route_audit),
    ("exp08_federation_floor", exp08_federation_floor),
    ("exp09_waterfilling", exp09_waterfilling),
    ("exp10_monotone_history", exp10_monotone_history),
]


def main():
    summary = {"experiments": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    all_passed = True

    for name, module in EXPERIMENTS:
        entry = {"name": name}
        t0 = time.time()
        try:
            result = module.run()
            entry["passed"] = result.get("passed", False)
            entry["theorem"] = result.get("theorem", "")
            entry["error"] = None
        except Exception as e:  # noqa: BLE001
            entry["passed"] = False
            entry["theorem"] = ""
            entry["error"] = f"{type(e).__name__}: {e}"
            traceback.print_exc()
        entry["elapsed_seconds"] = round(time.time() - t0, 4)
        all_passed = all_passed and entry["passed"]
        summary["experiments"].append(entry)
        status = "PASS" if entry["passed"] else "FAIL"
        print(f"[{status}] {name} ({entry['elapsed_seconds']}s)"
              + (f" -- {entry['error']}" if entry["error"] else ""))

    summary["all_passed"] = all_passed
    summary["n_experiments"] = len(EXPERIMENTS)
    summary["n_passed"] = sum(1 for e in summary["experiments"] if e["passed"])
    summary["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    save_json(summary, os.path.join(RESULTS_DIR, "summary.json"))
    print(f"\n{summary['n_passed']}/{summary['n_experiments']} experiments passed. "
          f"Summary written to {os.path.join(RESULTS_DIR, 'summary.json')}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
