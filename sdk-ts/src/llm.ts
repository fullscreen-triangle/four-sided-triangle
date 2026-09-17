/**
 * The one interface a caller must supply to use generative individuation
 * (table.ts, nontrivial process) or the four-column route-audit
 * (routeAudit.ts). Everything else in this package works with zero
 * dependencies; this is the sole integration seam for "bring your own model."
 */
export interface LLMClient {
  /** A single-turn completion. `system` carries role/constraints; `prompt` carries the actual ask. */
  complete(args: { system?: string; prompt: string }): Promise<string>;
}
