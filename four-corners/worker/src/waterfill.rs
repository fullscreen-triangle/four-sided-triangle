//! Water-filling attention allocation (paper §8.2, Def 8.6, Thm 8.10). Under
//! the diminishing-returns axiom (Ax 8.7: every gain profile is concave),
//! the value-maximising split of a finite attention budget across competing
//! scenes is characterised by a single price p*: marginal gain is equalised
//! across every attended scene, and a scene is dropped if its first unit of
//! attention already returns less than p* (KKT stationarity of the
//! Lagrangian, solved here by bisection on the price).
//!
//! Remark 8.11: a non-concave (increasing-returns) gain profile breaks the
//! guarantee — the true optimum there concentrates the whole budget on one
//! scene instead of dividing it. Callers with such a scene should not use
//! this solver.
//!
//! Direct Rust port of `sdk-ts/src/waterfill.ts`.

use std::collections::HashMap;

pub struct Scene {
    pub id: String,
    /// Concave, nondecreasing gain profile γ(a), γ(0)=0. Caller's responsibility to keep it concave (Ax 8.7).
    pub gain: Box<dyn Fn(f64) -> f64>,
    /// Derivative γ'(a) — required for the KKT / bisection solve.
    pub marginal_gain: Box<dyn Fn(f64) -> f64>,
    /// Upper bound on attention this scene can usefully absorb (None = unbounded by budget alone).
    pub max_attention: Option<f64>,
}

pub struct WaterfillResult {
    pub allocation: HashMap<String, f64>,
    pub price: f64,
    pub value: f64,
}

const EPS_ATTENTION: f64 = 1e-6;

/// Thm 8.10: solves max Σ γ_i(a_i) s.t. Σ a_i <= budget, a_i >= 0, by
/// bisecting on the shared price p until Σ a_i(p) matches the budget (or the
/// budget is slack because every scene saturates its own max_attention first).
pub fn waterfill(scenes: &[Scene], budget: f64, tolerance: f64, max_iterations: u32) -> WaterfillResult {
    assert!(budget >= 0.0, "waterfill: budget must be >= 0");
    if scenes.is_empty() {
        return WaterfillResult { allocation: HashMap::new(), price: 0.0, value: 0.0 };
    }

    let attention_at = |scene: &Scene, price: f64| -> f64 {
        if finite_marginal(scene) <= price {
            return 0.0;
        }
        let mut lo = 0.0_f64;
        let mut hi = scene.max_attention.unwrap_or(budget);
        while (scene.marginal_gain)(hi) > price && hi < 1e12 {
            hi *= 2.0;
        }
        for _ in 0..max_iterations {
            let mid = (lo + hi) / 2.0;
            if (scene.marginal_gain)(mid) > price {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        let level = (lo + hi) / 2.0;
        match scene.max_attention {
            Some(max) => level.min(max),
            None => level,
        }
    };

    let total_at = |price: f64| -> f64 { scenes.iter().map(|s| attention_at(s, price)).sum() };

    let mut price_lo = 0.0_f64;
    let mut price_hi = scenes.iter().map(finite_marginal).fold(1e-9_f64, f64::max);
    while total_at(price_hi) > budget && price_hi < 1e15 {
        price_hi *= 2.0;
    }

    if total_at(price_lo) <= budget + tolerance {
        price_hi = price_lo;
    } else {
        for _ in 0..max_iterations {
            let mid = (price_lo + price_hi) / 2.0;
            if total_at(mid) > budget {
                price_lo = mid;
            } else {
                price_hi = mid;
            }
            if (total_at(mid) - budget).abs() < tolerance {
                break;
            }
        }
    }

    let price = price_hi;
    let mut allocation = HashMap::new();
    let mut value = 0.0;
    for scene in scenes {
        let a = attention_at(scene, price);
        allocation.insert(scene.id.clone(), a);
        value += (scene.gain)(a);
    }
    WaterfillResult { allocation, price, value }
}

/// marginal_gain evaluated at a small positive attention level, sidestepping +Infinity at exactly 0 for profiles like sqrt.
fn finite_marginal(scene: &Scene) -> f64 {
    let m = (scene.marginal_gain)(EPS_ATTENTION);
    if m.is_finite() {
        m
    } else {
        (scene.marginal_gain)(EPS_ATTENTION * 10.0)
    }
}

/// Convenience constructor for a concave power-law-ish gain profile, γ(a) = scale * sqrt(a), used widely in tests/examples.
pub fn sqrt_gain_scene(id: &str, scale: f64, max_attention: Option<f64>) -> Scene {
    Scene {
        id: id.to_string(),
        gain: Box::new(move |a| scale * a.max(0.0).sqrt()),
        marginal_gain: Box::new(move |a| if a <= 0.0 { f64::INFINITY } else { scale / (2.0 * a.sqrt()) }),
        max_attention,
    }
}
