import { describe, it, expect } from "vitest";
import { ContactGraph } from "../src/graph.js";

/**
 * Mirrors validation Experiment 1 (paper §9.1): across many random contact
 * graphs, no claim ever registers a separation cost below its own graph's
 * floor, and the floor is tight (attained exactly by a claim whose only
 * individuating structure is a single minimum-weight contact).
 */
describe("ContactGraph — resolution floor (Thm 2.7 / Experiment 1)", () => {
  it("no claim separation cost ever falls below the graph floor, across random graphs", () => {
    let observations = 0;
    let violations = 0;
    const rng = mulberry32(1234);

    for (let trial = 0; trial < 60; trial++) {
      const n = 3 + Math.floor(rng() * 10); // 3..12 claims
      const g = new ContactGraph();
      const ids = Array.from({ length: n }, (_, i) => `c${i}`);
      for (const id of ids) g.addClaim(id, 1 + rng() * 9);
      // sparse extra contacts among claims
      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          if (rng() < 0.3) g.addContact(ids[i]!, ids[j]!, 1 + rng() * 9);
        }
      }
      const floor = g.floor();
      for (const id of ids) {
        observations++;
        const sigma = g.separationCost(id);
        if (sigma < floor - 1e-9) violations++;
      }
    }

    expect(observations).toBeGreaterThan(100);
    expect(violations).toBe(0);
  });

  it("the floor is attained exactly by a minimum-weight singleton contact", () => {
    // "weak" has only its one medium-contact (weight 2) individuating it — no
    // other path to the medium exists, so its min-cut equals that edge exactly.
    const g = new ContactGraph();
    g.addClaim("weak", 2);
    g.addClaim("strong", 9);
    expect(g.floor()).toBe(2);
    expect(g.separationCost("weak")).toBe(2);
  });

  it("rejects zero/negative weights (Thm 2.7: no zero-cost contact)", () => {
    const g = new ContactGraph();
    expect(() => g.addClaim("x", 0)).toThrow();
    expect(() => g.addClaim("x", -1)).toThrow();
  });
});

/** Deterministic PRNG so the test is reproducible without a runtime dependency. */
function mulberry32(seed: number) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
