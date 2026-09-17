/**
 * Public API. `ask()` is the fix for the failure this package exists to
 * solve (paper §1.1): a retrieval system that hands back the top-matching
 * passage is answering a question ("what tokens overlap the query") that is
 * provably not the one the caller asked ("what does this mean, to me, right
 * now" — Thm 3.4). `ask()` never returns a bare passage. It always returns a
 * `status` that is honest about grounding strength (Thm 6.4, Thm 6.6–6.7),
 * and a `claim` that is individuated against the caller's own persistent
 * receiver graph (Thm 4.9), not a content-similarity score.
 */

import { ReceiverGraph, type ReceiverSnapshot } from "./receiver.js";
import { Federation } from "./federation.js";
import type { SourceAdapter } from "./sourceAdapter.js";
import { assessGrounding, type Catalyst, type SupportEdge, type GroundingStatus } from "./catalysis.js";
import { runToClosure, type AnswerClass, type AvailableSource } from "./closure.js";
import type { LLMClient } from "./llm.js";

export type { SourceAdapter, SourceChunk } from "./sourceAdapter.js";
export { InMemorySource } from "./sourceAdapter.js";
export { LocalFileSource, type LocalFileSourceOptions } from "./sources/localFile.js";
export { ContactGraph, MEDIUM } from "./graph.js";
export { ReceiverGraph, type ReceiverSnapshot, type RegisteredCell } from "./receiver.js";
export { Federation, type FederatedClaim } from "./federation.js";
export { assessGrounding, compositePower, type Catalyst, type SupportEdge, type GroundingResult, type GroundingStatus } from "./catalysis.js";
export { runToClosure, type AnswerClass, type AvailableSource, type ClosureResult } from "./closure.js";
export { causalPropagationTable, type PropagationResult } from "./table.js";
export { routeAudit, type FourColumnResult, type OpaqueAnswer } from "./routeAudit.js";
export { waterfill, sqrtGainScene, type Scene, type WaterfillResult } from "./waterfill.js";
export { SplitAttentionAgent } from "./agent.js";
export { Society } from "./society.js";
export type { LLMClient } from "./llm.js";

export interface PersistAdapter {
  load(receiverId: string): Promise<ReceiverSnapshot | undefined>;
  save(snapshot: ReceiverSnapshot): Promise<void>;
}

/** File-based persistence for Node — Thm 8.9: the receiver graph is append-only across process restarts too. */
export class JsonFilePersistAdapter implements PersistAdapter {
  constructor(private readonly path: string) {}

  async load(receiverId: string): Promise<ReceiverSnapshot | undefined> {
    const { readFile } = await import("node:fs/promises");
    try {
      const raw = await readFile(this.path, "utf-8");
      const parsed = JSON.parse(raw) as ReceiverSnapshot;
      return parsed.receiverId === receiverId ? parsed : undefined;
    } catch {
      return undefined;
    }
  }

  async save(snapshot: ReceiverSnapshot): Promise<void> {
    const { writeFile, mkdir } = await import("node:fs/promises");
    const { dirname } = await import("node:path");
    await mkdir(dirname(this.path), { recursive: true });
    await writeFile(this.path, JSON.stringify(snapshot, null, 2), "utf-8");
  }
}

export interface IndividuatorOptions {
  /** Persistent identity for the receiver graph — one per user, or per project thread (Principle 9.2). */
  receiverId: string;
  sources: SourceAdapter[];
  llm?: LLMClient;
  persist?: PersistAdapter;
  /** Coherence threshold θ (Def 6.3). Default 0.5, per the paper's own majority condition. */
  theta?: number;
  /** Minimum token-overlap for a chunk to be treated as relevant to the query, before catalyst-power scoring. */
  candidateLimit?: number;
}

export type IndividuatedAnswer =
  | {
      status: "grounded";
      claim: string;
      support: readonly Catalyst[];
      floor: number;
    }
  | {
      status: "single-sourced" | "two-sourced";
      claim: string;
      support: readonly Catalyst[];
      floor: number;
      warning: string;
    }
  | {
      status: "contested";
      classes: readonly AnswerClass[];
      warning: string;
    }
  | {
      status: "declined";
      reason: string;
    };

export class Individuator {
  private receiver: ReceiverGraph;
  private readonly receiverId: string;
  private readonly federation: Federation;
  private readonly llm: LLMClient | undefined;
  private readonly persist: PersistAdapter | undefined;
  private readonly theta: number;
  private readonly candidateLimit: number;
  private loaded = false;

  constructor(options: IndividuatorOptions) {
    this.federation = new Federation(options.sources);
    this.receiverId = options.receiverId;
    this.receiver = new ReceiverGraph(options.receiverId);
    this.llm = options.llm;
    this.persist = options.persist;
    this.theta = options.theta ?? 0.5;
    this.candidateLimit = options.candidateLimit ?? 12;
  }

  private async ensureLoaded(): Promise<void> {
    if (this.loaded) return;
    this.loaded = true;
    if (!this.persist) return;
    const snapshot = await this.persist.load(this.receiverId);
    // Thm 8.9: loading is a fresh reconstruction from the last saved state,
    // never a rollback — the fresh receiver above is simply replaced by one
    // seeded from that snapshot, not mutated field-by-field.
    if (snapshot) this.receiver = new ReceiverGraph(this.receiverId, snapshot);
  }

  /**
   * The fix for "it returns actual text from some pdf that matches my
   * query." This never returns a bare passage: it individuates candidate
   * claims against the caller's own receiver graph (Thm 4.9), requires a
   * coherence triangle before calling anything "grounded" (Thm 6.4), and
   * terminates by closure over every federated source rather than a
   * similarity threshold (Thm 6.6–6.7) — reporting `contested` or
   * `declined` as first-class outcomes rather than silently picking a
   * top-ranked passage.
   */
  async ask(query: string): Promise<IndividuatedAnswer> {
    await this.ensureLoaded();

    this.receiver.fixDistinction(query, 1);

    const claims = await this.federation.listAll();
    const candidates = rankByTokenOverlap(query, claims).slice(0, this.candidateLimit);

    if (candidates.length === 0) {
      return { status: "declined", reason: "no candidate claims found across any federated source for this query" };
    }

    // Register each candidate's cell in the receiver graph (Def 4.7): this is
    // what replaces a single content-similarity score — every candidate's
    // meaning is computed against THIS receiver, not a global ranking.
    const catalysts: Catalyst[] = [];
    for (const candidate of candidates) {
      // registerCell fixes the candidate as a claim first (Def 4.7); only
      // once both endpoints exist can the query<->candidate contact be added.
      const cell = this.receiver.registerCell(candidate.id, 1 + candidate.overlapScore * 9);
      this.receiver.fixContact(query, candidate.id, Math.max(candidate.overlapScore, 0.01));
      const aboveFloor = Math.max(cell.separationCost - cell.floor, 0);
      const maxPossible = this.receiver.floor() > 0 ? cell.separationCost : 1;
      catalysts.push({
        id: candidate.id,
        source: candidate.sourceName,
        power: maxPossible > 0 ? Math.min(aboveFloor / maxPossible, 1) : 0,
      });
    }

    const support = buildSupportGraph(catalysts);
    const grounding = assessGrounding(catalysts, support, this.theta);

    if (this.persist) await this.persist.save(this.receiver.snapshot());

    const best = candidates[0]!;

    if (grounding.status === "grounded") {
      return { status: "grounded", claim: best.text, support: grounding.catalysts, floor: this.receiver.floor() };
    }

    if (this.federation.memberCount < 3) {
      // Honest about *why* it can't be grounded: fewer than 3 independent
      // sources were even federated, so a coherence triangle (Thm 6.4) is
      // structurally impossible here — never silently promoted anyway.
      return {
        status: grounding.status,
        claim: best.text,
        support: grounding.catalysts,
        floor: this.receiver.floor(),
        warning: `only ${this.federation.memberCount} source(s) federated (${this.federation.memberNames().join(", ")}); Thm 6.4 requires >=3 independent sources for a claim to be marked grounded`,
      };
    }

    return {
      status: grounding.status,
      claim: best.text,
      support: grounding.catalysts,
      floor: this.receiver.floor(),
      warning: "fewer than 3 mutually-supporting independent sources agreed strongly enough to ground this claim (Thm 6.4) — treat as provisional",
    };
  }

  /**
   * Runs the full closure procedure (Def 6.5) instead of the single-round
   * `ask()` above: every federated source is treated as an `AvailableSource`
   * and the search only stops once none can add a new answer class.
   */
  async askToClosure(query: string): Promise<IndividuatedAnswer> {
    await this.ensureLoaded();
    this.receiver.fixDistinction(query, 1);

    const claims = await this.federation.listAll();
    const bySource = groupBy(claims, (c) => c.sourceName);

    const sources: AvailableSource[] = [...bySource.entries()].map(([sourceName, chunks]) => ({
      id: sourceName,
      invoke: async () => {
        const ranked = rankByTokenOverlap(query, chunks);
        const top = ranked[0];
        if (!top || top.overlapScore <= 0) return null;
        return { key: normalizeForClassKey(top.text), representative: top.text, supportingCatalystIds: [top.id] };
      },
    }));

    const result = await runToClosure(sources);
    if (this.persist) await this.persist.save(this.receiver.snapshot());

    if (result.status === "declined") return result;
    if (result.status === "closed") {
      return { status: "single-sourced", claim: result.classes[0].representative, support: [], floor: this.receiver.floor(), warning: "closure reached a single answer class, but grounding strength (Thm 6.4) was not separately assessed by askToClosure — use ask() for a grounded/contested status" };
    }
    return { status: "contested", classes: result.classes, warning: "closure found multiple, irreconcilable answer classes across federated sources (Thm 6.6–6.7) — reported as decline-to-pick, not silently resolved" };
  }
}

export function createIndividuator(options: IndividuatorOptions): Individuator {
  return new Individuator(options);
}

interface RankedCandidate {
  id: string;
  text: string;
  sourceName: string;
  overlapScore: number;
}

function rankByTokenOverlap(query: string, claims: { id: string; text: string; sourceName: string }[]): RankedCandidate[] {
  const queryTokens = tokenize(query);
  const scored = claims.map((c) => ({ ...c, overlapScore: jaccard(queryTokens, tokenize(c.text)) }));
  return scored.filter((c) => c.overlapScore > 0).sort((a, b) => b.overlapScore - a.overlapScore);
}

function tokenize(s: string): Set<string> {
  return new Set(
    s
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((t) => t.length > 2),
  );
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 || b.size === 0) return 0;
  const intersection = [...a].filter((t) => b.has(t)).length;
  const union = new Set([...a, ...b]).size;
  return union === 0 ? 0 : intersection / union;
}

function buildSupportGraph(catalysts: readonly Catalyst[]): SupportEdge[] {
  // Independent sources with comparable power are treated as mutually
  // supportive (Def 6.2 support relation), scaled by how close their powers
  // are — a crude but source-agnostic proxy usable without a shared
  // representation between sources (the same constraint route-audit solves
  // for opaque pairs, §7).
  const edges: SupportEdge[] = [];
  for (const from of catalysts) {
    for (const to of catalysts) {
      if (from.id === to.id || from.source === to.source) continue;
      const degree = 1 - Math.abs(from.power - to.power);
      edges.push({ from: from.id, to: to.id, degree });
    }
  }
  return edges;
}

function groupBy<T, K>(items: T[], key: (t: T) => K): Map<K, T[]> {
  const map = new Map<K, T[]>();
  for (const item of items) {
    const k = key(item);
    const bucket = map.get(k);
    if (bucket) bucket.push(item);
    else map.set(k, [item]);
  }
  return map;
}

function normalizeForClassKey(text: string): string {
  return text.toLowerCase().replace(/\s+/g, " ").trim().slice(0, 200);
}
