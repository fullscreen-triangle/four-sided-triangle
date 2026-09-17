/**
 * Society (paper §8.3, Thm 8.13–8.14). A society composes several agents;
 * synchronisation across concurrently advanceable shared purposes solves
 * the identical convex program as a single agent's water-filling, one level
 * up, because the society graph satisfies the same structural hypotheses
 * (Thm 8.13). We reuse the exact same `waterfill` solver rather than a
 * second implementation — the paper's point is that there is no separate
 * scheduling heuristic required at the society level (Remark 8.15).
 */

import { SplitAttentionAgent } from "./agent.js";
import { waterfill, type Scene, type WaterfillResult } from "./waterfill.js";

export class Society {
  private readonly agents = new Map<string, SplitAttentionAgent>();

  addAgent(agent: SplitAttentionAgent): void {
    this.agents.set(agent.id, agent);
  }

  getAgent(id: string): SplitAttentionAgent | undefined {
    return this.agents.get(id);
  }

  /** Thm 8.13: society-level identity floor is the minimum character floor over connected agents. */
  characterFloor(): number {
    const floors = [...this.agents.values()].map((a) => a.characterFloor());
    return floors.length ? Math.min(...floors) : Infinity;
  }

  /**
   * Thm 8.14: divide a collective budget across concurrently open shared
   * purposes (society-level scenes) by the identical water-filling rule.
   */
  allocateCollective(sharedPurposes: readonly Scene[], budget: number): WaterfillResult {
    return waterfill(sharedPurposes, budget);
  }
}
