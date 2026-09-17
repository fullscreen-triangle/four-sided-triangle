/**
 * Split-attention agent (paper §8.2, Def 8.6). A bounded agent divides a
 * fixed attention budget across the scenes (sources) currently competing
 * for it, by water-filling (Thm 8.10). Each pipeline stage in a consuming
 * application is one of these, not a stateless function call (Remark 8.9):
 * it carries a conserved self-graph identity across calls.
 */

import { ContactGraph } from "./graph.js";
import { waterfill, type Scene, type WaterfillResult } from "./waterfill.js";

export class SplitAttentionAgent {
  readonly id: string;
  private readonly selfGraph = new ContactGraph();

  constructor(id: string) {
    this.id = id;
  }

  /** Record an internal distinction this agent draws — grows its self-graph, never resets it. */
  drawDistinction(name: string, weight = 1): void {
    this.selfGraph.addClaim(name, weight);
  }

  /** Character invariant lower bound: the self-graph's own floor (Thm 8.9 references the underlying identity theorem). */
  characterFloor(): number {
    return this.selfGraph.floor();
  }

  /** Divide `budget` across the scenes currently competing for this agent's attention (Thm 8.10). */
  allocate(scenes: readonly Scene[], budget: number): WaterfillResult {
    return waterfill(scenes, budget);
  }
}
