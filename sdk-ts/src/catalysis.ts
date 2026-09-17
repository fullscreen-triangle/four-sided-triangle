/**
 * Catalytic composition and coherence (paper §6, Def 6.1–6.3, Thm 6.2, 6.4).
 *
 * A catalyst is any independently-sourced retrieval/reasoning step that
 * shifts alignment toward a target claim. Composing catalysts follows a
 * multiplicative law (Thm 6.2): repeating one source saturates strictly
 * below 1 and slower than diversifying (Cor 6.3) — this is *forced* by the
 * law, not a tuning heuristic.
 *
 * Coherence (Thm 6.4): a linear chain or a 2-cycle of mutual support is
 * never robust to removing one member. Only a strongly-connected triangle
 * (>=3 catalysts, each supported by the other two at θ>1/2) survives the
 * loss of any single member. This is enforced structurally below: a claim
 * can only be marked "grounded" once a real triangle exists.
 */

export interface Catalyst {
  id: string;
  /** Independent evidentiary channel this catalyst draws from — a file, a model, a record store. */
  source: string;
  /** power ∈ [0,1]: fraction of the above-floor alignment gap this catalyst closes (Def 6.1). */
  power: number;
}

/** Thm 6.2: composite power of catalysts applied in sequence, 1 - Π(1 - power_i). */
export function compositePower(catalysts: readonly Catalyst[]): number {
  return 1 - catalysts.reduce((acc, c) => acc * (1 - c.power), 1);
}

export interface SupportEdge {
  from: string; // catalyst id
  to: string; // catalyst id
  /** Degree to which `from`'s result reinforces `to`'s alignment shift, in (0,1]. */
  degree: number;
}

export type GroundingStatus = "single-sourced" | "two-sourced" | "grounded";

export interface GroundingResult {
  status: GroundingStatus;
  /** The catalysts backing the claim (all of them, regardless of status). */
  catalysts: readonly Catalyst[];
  /** Support edges at or above threshold θ. */
  activeSupport: SupportEdge[];
  /** True only for status "grounded": a strongly-connected triangle survives single-member removal (Thm 6.4(iii)). */
  robustToSingleRemoval: boolean;
}

const DEFAULT_THETA = 0.5;

/**
 * Thm 6.4: never silently promote a claim to "grounded" on fewer than three
 * independently sourced, mutually supporting catalysts. Mirrors Remark 6.5 —
 * one passage is never a grounded answer, and neither are two.
 */
export function assessGrounding(
  catalysts: readonly Catalyst[],
  support: readonly SupportEdge[],
  theta: number = DEFAULT_THETA,
): GroundingResult {
  const uniqueSources = new Set(catalysts.map((c) => c.source));
  const active = support.filter((e) => e.degree >= theta && e.degree > 0.5);

  if (catalysts.length <= 1) {
    return { status: "single-sourced", catalysts, activeSupport: active, robustToSingleRemoval: false };
  }
  if (catalysts.length === 2 || uniqueSources.size < 3) {
    // Thm 6.4(ii): a 2-cycle fails the majority condition θ>1/2 — removing either
    // leaves exactly one, unsupported, voter. Never promoted past "two-sourced."
    return { status: "two-sourced", catalysts, activeSupport: active, robustToSingleRemoval: false };
  }

  const robust = isStronglyConnectedRobust(catalysts.map((c) => c.id), active);
  return {
    status: robust ? "grounded" : "two-sourced",
    catalysts,
    activeSupport: active,
    robustToSingleRemoval: robust,
  };
}

/** Thm 6.4(iii): each catalyst supported by >=2 others at θ, and removal of any one leaves the rest mutually supporting. */
function isStronglyConnectedRobust(ids: string[], support: readonly SupportEdge[]): boolean {
  if (ids.length < 3) return false;
  const incoming = new Map<string, Set<string>>(ids.map((id) => [id, new Set<string>()]));
  for (const e of support) {
    if (!incoming.has(e.to)) continue;
    incoming.get(e.to)!.add(e.from);
  }
  // Every member needs >=2 independent supporters for the majority condition to
  // survive removing any single one of them.
  for (const id of ids) {
    if ((incoming.get(id)?.size ?? 0) < 2) return false;
  }
  // And removing any one member must leave every remaining member still with
  // >=1 supporter among what's left (Thm 6.4(iii) removal-survives check).
  for (const removed of ids) {
    for (const id of ids) {
      if (id === removed) continue;
      const supporters = [...(incoming.get(id) ?? [])].filter((s) => s !== removed);
      if (supporters.length < 1) return false;
    }
  }
  return true;
}
