import { describe, it, expect } from "vitest";
import { runToClosure, type AvailableSource } from "../src/closure.js";

/**
 * Mirrors validation Experiment 6: a two-cluster construction where gate A
 * alone reaches a terminal claim that would trivially clear any confidence
 * threshold, while gate B (not yet invoked) reaches a genuinely distinct
 * class. Closure — running every available source to exhaustion — correctly
 * reports "contested" instead of stopping early on A's high self-alignment.
 */
describe("closure vs. confidence threshold (Thm 6.6–6.7 / Experiment 6)", () => {
  it("reports contested closure when two disjoint gates reach distinct classes", async () => {
    const gateA: AvailableSource = {
      id: "gateA",
      invoke: async () => ({ key: "clusterA", representative: "answer from cluster A", supportingCatalystIds: ["gateA"] }),
    };
    const gateB: AvailableSource = {
      id: "gateB",
      invoke: async () => ({ key: "clusterB", representative: "answer from cluster B", supportingCatalystIds: ["gateB"] }),
    };

    const result = await runToClosure([gateA, gateB]);
    expect(result.status).toBe("contested");
    if (result.status === "contested") {
      expect(result.classes.map((c) => c.key).sort()).toEqual(["clusterA", "clusterB"]);
    }
  });

  it("reports convergent closure when every source lands in the same class", async () => {
    const sources: AvailableSource[] = ["s1", "s2", "s3"].map((id) => ({
      id,
      invoke: async () => ({ key: "sameClass", representative: "agreed answer", supportingCatalystIds: [id] }),
    }));
    const result = await runToClosure(sources);
    expect(result.status).toBe("closed");
    if (result.status === "closed") {
      expect(result.classes[0]!.supportingCatalystIds.sort()).toEqual(["s1", "s2", "s3"]);
    }
  });

  it("declines rather than guessing when no source and no registry exist", async () => {
    const result = await runToClosure([]);
    expect(result.status).toBe("declined");
  });

  it("declines when sources are exhausted and none reach an answer class", async () => {
    const dead: AvailableSource = { id: "dead", invoke: async () => null };
    const result = await runToClosure([dead]);
    expect(result.status).toBe("declined");
  });
});
