/**
 * Four-column route-audit (paper §7, Def 7.1–7.3, Thm 7.4–7.6). Certifies
 * agreement between two opaque sources (no shared internal representation —
 * a domain model against a document index, say) by comparing what each
 * answer PROVOKES as a follow-up, not just their surface content.
 *
 * Thm 7.6 (the false-friend construction): two receivers can produce
 * numerically identical central columns (surface agreement) while their
 * provoked columns diverge — invisible to endpoint-only comparison,
 * exactly the failure this module exists to catch (Remark 7.7: two
 * internal documents can agree for different reasons).
 */

import type { LLMClient } from "./llm.js";

export interface OpaqueAnswer {
  sourceId: string;
  /** The central column: this source's answer to the query. */
  central: string;
}

export interface FourColumnResult {
  quiescent: boolean;
  centralAgree: boolean;
  provokedAgree: boolean;
  columns: { aCentral: string; bCentral: string; aProvoked: string; bProvoked: string };
  rounds: number;
}

export interface RouteAuditOptions {
  query: string;
  a: OpaqueAnswer;
  b: OpaqueAnswer;
  llm: LLMClient;
  /** Tolerance for textual-similarity-based "agreement" between columns, in [0,1]. Default 0.85 (near-identity). */
  similarityThreshold?: number;
  maxRounds?: number;
}

/**
 * Thm 7.4: the system is quiescent iff (a) central columns agree AND (b)
 * provoked columns agree. Thm 7.5 dichotomy: either reaches quiescence in
 * finitely many rounds, or the residual is bounded away from zero — no
 * third outcome, so this always terminates within maxRounds.
 */
export async function routeAudit(options: RouteAuditOptions): Promise<FourColumnResult> {
  const { query, a, b, llm, similarityThreshold = 0.85, maxRounds = 5 } = options;

  const [aProvoked, bProvoked] = await Promise.all([provoke(llm, query, a.central), provoke(llm, query, b.central)]);

  let centralAgree = textualAgreement(a.central, b.central) >= similarityThreshold;
  let provokedAgree = textualAgreement(aProvoked, bProvoked) >= similarityThreshold;
  let rounds = 1;

  // Thm 7.5 dichotomy: re-provoke a bounded number of times in case the
  // first-round provoked columns were noisy; residual either falls below
  // tolerance (quiescent) or stays bounded away from zero (never quiescent).
  let currentAProvoked = aProvoked;
  let currentBProvoked = bProvoked;
  while (!provokedAgree && rounds < maxRounds) {
    [currentAProvoked, currentBProvoked] = await Promise.all([
      provoke(llm, query, currentAProvoked),
      provoke(llm, query, currentBProvoked),
    ]);
    provokedAgree = textualAgreement(currentAProvoked, currentBProvoked) >= similarityThreshold;
    rounds++;
  }

  return {
    quiescent: centralAgree && provokedAgree,
    centralAgree,
    provokedAgree,
    columns: { aCentral: a.central, bCentral: b.central, aProvoked: currentAProvoked, bProvoked: currentBProvoked },
    rounds,
  };
}

async function provoke(llm: LLMClient, query: string, answer: string): Promise<string> {
  return llm.complete({
    system:
      "Given an answer to a query, state the single most important follow-up question " +
      "this answer would provoke — the thing that would need to be true, or checked next, " +
      "for this answer to hold. Respond with just the follow-up question.",
    prompt: `Original query: ${query}\nAnswer: ${answer}`,
  });
}

/** Cheap, dependency-free textual similarity (token Jaccard) — swap for embeddings if the caller wants finer resolution. */
function textualAgreement(x: string, y: string): number {
  const tokenize = (s: string) =>
    new Set(
      s
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/)
        .filter(Boolean),
    );
  const tx = tokenize(x);
  const ty = tokenize(y);
  if (tx.size === 0 && ty.size === 0) return 1;
  const intersection = [...tx].filter((t) => ty.has(t)).length;
  const union = new Set([...tx, ...ty]).size;
  return union === 0 ? 1 : intersection / union;
}
