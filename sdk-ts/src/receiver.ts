/**
 * Receiver graphs (paper §4.3, Def 4.7) and monotone agent history (§8.2, Thm 8.9).
 *
 * A receiver is a specific querying agent's own decoder structure — the
 * distinctions it already holds fixed (a researcher's project history, a
 * user's prior queries). A claim's "meaning" relative to a receiver is its
 * resting cut *in that receiver's own graph*, never a receiver-independent
 * score (Thm 4.9: distinct receivers register distinct, equally correct cells).
 *
 * Thm 8.9 (monotone, irreversible history): the committed count strictly
 * increases under every committed act and is never restored, including by
 * "rollback." Consequently every `registerCell` call is a fresh walk against
 * the *current* graph — never a cached value (Remark 8.10: caching an answer
 * across a growing corpus returns an answer appropriate to a self the system
 * has already left).
 */

import { ContactGraph, MEDIUM } from "./graph.js";

export interface RegisteredCell {
  claim: string;
  /** The claim's resting cut in this receiver, i.e. its meaning here — never "the" relevance. */
  separationCost: number;
  /** This receiver's own floor at the moment of registration. */
  floor: number;
  /** Monotone act count at which this registration was computed (Thm 8.9). */
  committedCount: number;
}

export interface ReceiverSnapshot {
  receiverId: string;
  committedCount: number;
  claims: string[];
  edges: Array<{ a: string; b: string; weight: number }>;
}

export class ReceiverGraph {
  readonly receiverId: string;
  private readonly graph = new ContactGraph();
  private committedCount = 0;

  constructor(receiverId: string, snapshot?: ReceiverSnapshot) {
    this.receiverId = receiverId;
    if (snapshot) {
      if (snapshot.receiverId !== receiverId) {
        throw new Error(
          `snapshot receiverId "${snapshot.receiverId}" does not match "${receiverId}"; refusing to load another receiver's state`,
        );
      }
      this.committedCount = snapshot.committedCount;
      for (const c of snapshot.claims) this.graph.addClaim(c, 1);
      for (const e of snapshot.edges) {
        if (e.b === "__medium__") this.graph.addClaim(e.a, e.weight);
        else this.graph.addContact(e.a, e.b, e.weight);
      }
    }
  }

  /** Every mutation is a committed act: the count only ever increases (Thm 8.9). */
  private commit(): void {
    this.committedCount += 1;
  }

  /**
   * Fix a distinction the receiver already holds: a new claim (or a stronger
   * contact between existing claims). This is how "prior queries and project
   * context" accrete into the receiver's own graph over a session (Principle 9.2).
   */
  fixDistinction(claim: string, mediumWeight = 1): void {
    const isNew = !this.graph.has(claim);
    this.graph.addClaim(claim, mediumWeight);
    if (isNew) this.commit();
  }

  fixContact(a: string, b: string, weight: number): void {
    this.graph.addContact(a, b, weight);
    this.commit();
  }

  /** An explicit "undo" is itself a further committed act — it never lowers the count (Thm 8.9 proof). */
  acknowledgeRollbackAttempt(): void {
    this.commit();
  }

  get history(): { committedCount: number } {
    return { committedCount: this.committedCount };
  }

  /**
   * Def 4.7 / Thm 4.9: register the cell a claim occupies *in this receiver*.
   * Always a fresh walk against the current graph, never a cached fetch
   * (Remark 8.10) — the committedCount on the result proves it was computed now.
   */
  registerCell(claim: string, mediumWeight = 1): RegisteredCell {
    this.fixDistinction(claim, mediumWeight);
    return {
      claim,
      separationCost: this.graph.separationCost(claim),
      floor: this.graph.floor(),
      committedCount: this.committedCount,
    };
  }

  floor(): number {
    return this.graph.floor();
  }

  snapshot(): ReceiverSnapshot {
    // edges() may return either endpoint as `a` or `b` — only correct because
    // ContactGraph's adjacency Map happens to insert MEDIUM first, making JS's
    // insertion-order iteration put it on the `a` side for every medium-
    // adjacent edge; check both sides explicitly rather than depend on that.
    const edges = this.graph.edges().map((e) => {
      if (e.a === MEDIUM) return { a: String(e.b), b: "__medium__", weight: e.weight };
      if (e.b === MEDIUM) return { a: String(e.a), b: "__medium__", weight: e.weight };
      return { a: String(e.a), b: String(e.b), weight: e.weight };
    });
    return {
      receiverId: this.receiverId,
      committedCount: this.committedCount,
      claims: this.graph.claims(),
      edges,
    };
  }
}
