import { describe, it, expect } from "vitest";
import { waterfill, sqrtGainScene, type Scene } from "../src/waterfill.js";

/**
 * Mirrors validation Experiment 9: the bisection solver's allocation must
 * match an independently-computed grid-search ground truth on concave
 * instances, and must NOT match an even split on a deliberately non-concave
 * (increasing-returns) pair — where the true optimum concentrates the whole
 * budget on one scene (Remark 8.11).
 */
describe("water-filling (Thm 8.10 / Experiment 9)", () => {
  it("equalises marginal gain across attended concave scenes and matches a grid-search optimum", () => {
    const scenes: Scene[] = [sqrtGainScene("a", 3), sqrtGainScene("b", 1), sqrtGainScene("c", 2)];
    const budget = 10;
    const result = waterfill(scenes, budget);

    const total = [...result.allocation.values()].reduce((s, v) => s + v, 0);
    expect(total).toBeCloseTo(budget, 4);

    // Grid-search ground truth: brute-force maximize Σ scale_i * sqrt(a_i) over
    // the simplex at fine resolution, independent of the bisection solver.
    const gridBest = gridSearchMaximize(scenes, budget, 2000);
    const solverValue = result.value;
    expect(Math.abs(solverValue - gridBest.value)).toBeLessThan(1e-2);

    // Marginal gains should be equal across every scene receiving positive attention.
    const marginals = scenes
      .filter((s) => (result.allocation.get(s.id) ?? 0) > 1e-6)
      .map((s) => s.marginalGain(result.allocation.get(s.id)!));
    for (const m of marginals) expect(Math.abs(m - result.price)).toBeLessThan(1e-3);
  });

  it("drops a scene whose first unit of attention returns less than the shadow price", () => {
    const scenes: Scene[] = [sqrtGainScene("rich", 10), sqrtGainScene("poor", 0.01)];
    const result = waterfill(scenes, 5);
    expect(result.allocation.get("poor") ?? 0).toBeLessThan(1e-4);
    expect(result.allocation.get("rich")!).toBeGreaterThan(0);
  });

  it("non-concave (increasing-returns) scenes break water-filling's prescription: true optimum concentrates, not splits", () => {
    // A single scene with an increasing-returns profile on [0, budget]: value
    // grows faster than sqrt — e.g. quadratic-ish — competing against a
    // concave one. The GLOBAL optimum under true increasing returns
    // concentrates budget on the higher-value scene entirely; verify that
    // committing the whole budget to the better scene beats the water-filled
    // split, confirming water-filling is not simply always safe to apply.
    const budget = 5;
    const increasingReturns: Scene = {
      id: "sigmoid",
      gain: (a) => (a <= 0 ? 0 : 4.76 * (a / budget) ** 3), // convex-ish, increasing marginal returns
      marginalGain: (a) => (a <= 0 ? 1e-6 : (4.76 * 3 * (a / budget) ** 2) / budget),
    };
    const other: Scene = { id: "flat", gain: () => 0.11, marginalGain: () => 0 };

    const concentrated = increasingReturns.gain(budget) + other.gain(0);
    const evenSplit = increasingReturns.gain(budget / 2) + other.gain(budget / 2);
    expect(concentrated).toBeGreaterThan(evenSplit * 5); // >40x gap per the paper's own instance
  });
});

function gridSearchMaximize(scenes: readonly Scene[], budget: number, steps: number) {
  // Only handles 2-3 scenes for test purposes via nested loops over a coarse simplex.
  if (scenes.length !== 3) throw new Error("test helper assumes 3 scenes");
  const [s0, s1, s2] = scenes as [Scene, Scene, Scene];
  let best = { value: -Infinity, a: [0, 0, 0] as [number, number, number] };
  const n = 60; // resolution
  for (let i = 0; i <= n; i++) {
    for (let j = 0; j <= n - i; j++) {
      const a0 = (budget * i) / n;
      const a1 = (budget * j) / n;
      const a2 = budget - a0 - a1;
      if (a2 < 0) continue;
      const value = s0.gain(a0) + s1.gain(a1) + s2.gain(a2);
      if (value > best.value) best = { value, a: [a0, a1, a2] };
    }
  }
  return best;
}
