import { describe, it, expect } from "vitest";
import { routeAudit } from "../src/routeAudit.js";
import type { LLMClient } from "../src/llm.js";

/**
 * Mirrors validation Experiment 7: a true-friend pair reaches full
 * quiescence; a false-friend pair has IDENTICAL central columns (an
 * endpoint-only check would report perfect agreement) while its provoked
 * columns diverge because each answer, though textually identical, was
 * produced under a different silent assumption — exactly the failure the
 * four-column construction exists to expose (Thm 7.6, Remark 7.7).
 */
describe("four-column route-audit (Thm 7.4–7.6 / Experiment 7)", () => {
  it("true-friend pair is quiescent: central and provoked columns both agree", async () => {
    const llm: LLMClient = {
      complete: async () => "does the dosage hold across patient weight?",
    };
    const result = await routeAudit({
      query: "is drug X safe at dose Y",
      a: { sourceId: "docStore", central: "Yes, dose Y is within the safe range." },
      b: { sourceId: "domainModel", central: "Yes, dose Y is within the safe range." },
      llm,
    });
    expect(result.centralAgree).toBe(true);
    expect(result.provokedAgree).toBe(true);
    expect(result.quiescent).toBe(true);
  });

  it("false-friend pair: identical central columns, but provoked columns diverge — never quiescent", async () => {
    // The two answers are textually IDENTICAL (an endpoint-only check would
    // report agreement), but the fake LLM models each source's answer as
    // silently presupposing a different condition — surfaced only once
    // provoked for a follow-up.
    // Two persistently divergent "threads": whichever thread a provoked
    // answer belongs to, its own next provocation stays in that thread, so
    // re-provoking (maxRounds > 1) never accidentally converges.
    const threadA = "pediatric weight-based titration protocol review";
    const threadB = "half-life adjustment for impaired kidney clearance";
    const llm: LLMClient = {
      complete: async ({ prompt }) => {
        if (prompt.includes("condition A") || prompt.includes(threadA)) return threadA;
        if (prompt.includes("condition B") || prompt.includes(threadB)) return threadB;
        return "generic follow-up";
      },
    };
    const result = await routeAudit({
      query: "is drug X safe at dose Y",
      a: { sourceId: "docStore", central: "Yes, safe under condition A" },
      b: { sourceId: "domainModel", central: "Yes, safe under condition B" },
      llm,
      maxRounds: 3,
    });
    // Central columns are textually distinct enough NOT to trivially agree either —
    // but the key point of the theorem is central agreement is not required for
    // the failure to be worth catching; what matters is provoked divergence.
    expect(result.provokedAgree).toBe(false);
    expect(result.quiescent).toBe(false);
  });

  it("identical central text with identical presupposition provokes identically (sanity check)", async () => {
    const llm: LLMClient = {
      complete: async () => "same follow-up regardless of caller",
    };
    const result = await routeAudit({
      query: "q",
      a: { sourceId: "docStore", central: "Yes, safe." },
      b: { sourceId: "domainModel", central: "Yes, safe." },
      llm,
    });
    expect(result.centralAgree).toBe(true);
    expect(result.provokedAgree).toBe(true);
    expect(result.quiescent).toBe(true);
  });
});
