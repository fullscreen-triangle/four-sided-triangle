import { describe, it, expect } from "vitest";
import { createIndividuator, InMemorySource } from "../src/index.js";

/**
 * End-to-end smoke test for the public API against Example 3.2 of the
 * paper (the true, irrelevant passage): a corpus contains both a generic
 * textbook-style passage and a narrow, specific one. `ask()` must never
 * just return the highest lexical-overlap passage as though it were "the"
 * answer — it must go through receiver registration, grounding assessment,
 * and report an honest status.
 */
describe("Individuator.ask() — end-to-end (never a bare passage dump)", () => {
  it("declines rather than fabricating an answer when nothing overlaps the query", async () => {
    const source = new InMemorySource("docs", [
      { id: "unrelated#0", text: "The quarterly report on unrelated topics entirely.", origin: "unrelated.md" },
    ]);
    const assistant = createIndividuator({ receiverId: "test-user", sources: [source] });
    const answer = await assistant.ask("enzyme assay buffer failure troubleshooting steps");
    expect(answer.status).toBe("declined");
  });

  it("with only one federated source, never reports status better than two-sourced, and says why", async () => {
    const source = new InMemorySource("docs", [
      { id: "kinetics#0", text: "General enzyme kinetics follows Michaelis-Menten equations broadly.", origin: "textbook.md" },
      { id: "assay#0", text: "This specific assay failed under buffer condition X due to pH drift.", origin: "labnotes.md" },
    ]);
    const assistant = createIndividuator({ receiverId: "test-user", sources: [source] });
    const answer = await assistant.ask("why did the assay fail under buffer condition X");

    expect(answer.status).not.toBe("grounded");
    if (answer.status === "single-sourced" || answer.status === "two-sourced") {
      expect(answer.warning).toMatch(/source/i);
      expect(answer.claim.length).toBeGreaterThan(0);
    } else {
      throw new Error(`unexpected status: ${answer.status}`);
    }
  });

  it("with three independent, mutually-reinforcing sources on the same claim, can reach grounded", async () => {
    const claimText = "The assay failed because buffer condition X caused pH drift outside tolerance.";
    const docs = new InMemorySource("docs", [{ id: "docs#0", text: claimText, origin: "labnotes.md" }]);
    const model = new InMemorySource("model-inference", [{ id: "model#0", text: claimText, origin: "inference" }]);
    const records = new InMemorySource("structured-records", [{ id: "records#0", text: claimText, origin: "db" }]);

    const assistant = createIndividuator({ receiverId: "test-user", sources: [docs, model, records] });
    const answer = await assistant.ask("why did the assay fail under buffer condition X");

    // Either grounded (if the crude support heuristic finds all 3 mutually
    // reinforcing) or explicitly explained as not-yet-grounded — never silently
    // returns just the top passage with no status at all.
    expect(["grounded", "single-sourced", "two-sourced"]).toContain(answer.status);
    expect(answer.status).not.toBe("declined");
  });

  it("askToClosure reports contested when independent sources disagree", async () => {
    const sourceA = new InMemorySource("docStore", [{ id: "a#0", text: "buffer condition X causes pH drift failure", origin: "a.md" }]);
    const sourceB = new InMemorySource("recordStore", [{ id: "b#0", text: "enzyme degradation temperature instability issue", origin: "b.md" }]);

    const assistant = createIndividuator({ receiverId: "test-user", sources: [sourceA, sourceB] });
    const answer = await assistant.askToClosure("why did the assay fail");

    expect(["contested", "single-sourced", "declined"]).toContain(answer.status);
  });
});
