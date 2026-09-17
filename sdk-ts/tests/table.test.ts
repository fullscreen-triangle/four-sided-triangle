import { describe, it, expect } from "vitest";
import { ContactGraph } from "../src/graph.js";
import { causalPropagationTable } from "../src/table.js";
import type { LLMClient } from "../src/llm.js";

/**
 * Mirrors Thm 5.4: the trivial process (seed === target) returns exactly the
 * resting catalogue cell — a static lookup — while a nontrivial process
 * (seed !== target, LLM-driven walk) returns an accountable terminus of the
 * same type. Both are the SAME function at two settings of the process arg.
 */
describe("causal propagation table (Thm 5.4)", () => {
  it("trivial process: seed === target returns the resting catalogue cell directly, no LLM needed", async () => {
    const g = new ContactGraph();
    g.addClaim("v", 5);
    const result = await causalPropagationTable({ graph: g, seed: "v", target: "v" });
    expect(result.accountable).toBe(true);
    expect(result.terminalSeparationCost).toBe(5);
  });

  it("nontrivial process without an LLM correctly declines rather than guessing", async () => {
    const g = new ContactGraph();
    g.addClaim("a", 3);
    g.addClaim("b", 4);
    const result = await causalPropagationTable({ graph: g, seed: "a", target: "b" });
    expect(result.accountable).toBe(false);
    expect(result.steps).toHaveLength(0);
  });

  it("nontrivial process with an LLM walks the graph and reaches the target (Thm 5.6: interior steps unconstrained)", async () => {
    const g = new ContactGraph();
    g.addClaim("a", 1);
    g.addClaim("mid", 1);
    g.addClaim("target", 1);
    g.addContact("a", "mid", 2);
    g.addContact("mid", "target", 2);

    const llm: LLMClient = {
      complete: async ({ prompt }) => {
        if (prompt.includes("Current claim: a")) return "mid";
        if (prompt.includes("Current claim: mid")) return "target";
        return "";
      },
    };

    const result = await causalPropagationTable({ graph: g, seed: "a", target: "target", llm });
    expect(result.accountable).toBe(true);
    expect(result.steps.map((s) => s.claim)).toEqual(["a", "mid", "target"]);
  });

  it("reports non-convergence honestly when the walk never reaches the target within maxHops", async () => {
    const g = new ContactGraph();
    g.addClaim("a", 1);
    g.addClaim("dead", 1);
    g.addClaim("target", 1);
    g.addContact("a", "dead", 2);

    const llm: LLMClient = { complete: async () => "dead" };
    const result = await causalPropagationTable({ graph: g, seed: "a", target: "target", llm, maxHops: 3 });
    expect(result.accountable).toBe(false);
  });
});
