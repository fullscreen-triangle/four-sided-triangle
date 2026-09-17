/**
 * Water-filling attention allocation (paper §8.2, Def 8.6, Thm 8.10). Under
 * the diminishing-returns axiom (Ax 8.7: every gain profile is concave), the
 * value-maximising split of a finite attention budget across competing
 * scenes is characterised by a single price p*: marginal gain is equalised
 * across every attended scene, and a scene is dropped if its first unit of
 * attention already returns less than p* (KKT stationarity of the
 * Lagrangian, solved here by bisection on the price).
 *
 * Remark 8.11: this is exactly as strong as Ax 8.7 and no stronger — a
 * non-concave (increasing-returns) gain profile breaks the guarantee, and
 * the true optimum there concentrates the whole budget on one scene instead
 * of dividing it. Callers with such a scene should not use this solver
 * (Experiment 9's second case in the paper demonstrates the >40x gap).
 */

export interface Scene {
  id: string;
  /** Concave, nondecreasing gain profile γ(a), γ(0)=0. Caller's responsibility to keep it concave (Ax 8.7). */
  gain: (attention: number) => number;
  /** Derivative γ'(a) — required for the KKT / bisection solve. */
  marginalGain: (attention: number) => number;
  /** Upper bound on attention this scene can usefully absorb (optional; default: unbounded by budget alone). */
  maxAttention?: number;
}

export interface WaterfillResult {
  allocation: Map<string, number>;
  price: number;
  value: number;
}

/**
 * Thm 8.10: solves max Σ γ_i(a_i) s.t. Σ a_i <= budget, a_i >= 0, by
 * bisecting on the shared price p until Σ a_i(p) matches the budget (or the
 * budget is slack because every scene saturates its own maxAttention first).
 */
export function waterfill(scenes: readonly Scene[], budget: number, tolerance = 1e-9, maxIterations = 200): WaterfillResult {
  if (budget < 0) throw new Error("waterfill: budget must be >= 0");
  if (scenes.length === 0) return { allocation: new Map(), price: 0, value: 0 };

  const EPS_ATTENTION = 1e-6;

  // a_i(p): the attention level at which γ_i'(a) = p, found by per-scene
  // bisection on attention (concavity => marginalGain is nonincreasing).
  // marginalGain(0) may be +Infinity (e.g. sqrt profiles), so "does this
  // scene want any attention at this price" is tested at a small positive
  // level rather than exactly 0.
  const attentionAt = (scene: Scene, price: number): number => {
    if (finiteMarginal(scene, EPS_ATTENTION) <= price) return 0;
    let lo = 0;
    let hi = scene.maxAttention ?? budget;
    // Expand hi if the scene could plausibly still want more than the current bound.
    while (scene.marginalGain(hi) > price && hi < 1e12) hi *= 2;
    for (let i = 0; i < maxIterations; i++) {
      const mid = (lo + hi) / 2;
      if (scene.marginalGain(mid) > price) lo = mid;
      else hi = mid;
    }
    const level = (lo + hi) / 2;
    return scene.maxAttention !== undefined ? Math.min(level, scene.maxAttention) : level;
  };

  const totalAt = (price: number): number => scenes.reduce((sum, s) => sum + attentionAt(s, price), 0);

  // marginalGain(0) may be +Infinity for profiles like sqrt (unbounded
  // marginal return at zero attention). Seed priceHi from a small positive
  // attention level instead, so the bisection has a finite, achievable
  // starting price rather than converging on Infinity and starving every scene.
  let priceLo = 0;
  let priceHi = Math.max(...scenes.map((s) => finiteMarginal(s, EPS_ATTENTION)), 1e-9);
  while (totalAt(priceHi) > budget && priceHi < 1e15) priceHi *= 2;

  // Guard: if even a near-zero price can't consume the whole budget (every
  // scene capped below its share), there's no positive price to bisect for.
  if (totalAt(priceLo) <= budget + tolerance) {
    priceHi = priceLo;
  } else {
    for (let i = 0; i < maxIterations; i++) {
      const mid = (priceLo + priceHi) / 2;
      if (totalAt(mid) > budget) priceLo = mid;
      else priceHi = mid;
      if (Math.abs(totalAt(mid) - budget) < tolerance) break;
    }
  }

  const price = priceHi;
  const allocation = new Map<string, number>();
  let value = 0;
  for (const scene of scenes) {
    const a = attentionAt(scene, price);
    allocation.set(scene.id, a);
    value += scene.gain(a);
  }
  return { allocation, price, value };
}

/** marginalGain evaluated at a small positive attention level, sidestepping +Infinity at exactly 0 for profiles like sqrt. */
function finiteMarginal(scene: Scene, epsAttention: number): number {
  const m = scene.marginalGain(epsAttention);
  return Number.isFinite(m) ? m : scene.marginalGain(epsAttention * 10);
}

/** Convenience constructor for a concave power-law-ish gain profile, γ(a) = scale * sqrt(a), used widely in tests/examples. */
export function sqrtGainScene(id: string, scale: number, maxAttention?: number): Scene {
  return {
    id,
    gain: (a) => scale * Math.sqrt(Math.max(a, 0)),
    marginalGain: (a) => (a <= 0 ? Infinity : scale / (2 * Math.sqrt(a))),
    ...(maxAttention !== undefined ? { maxAttention } : {}),
  };
}
