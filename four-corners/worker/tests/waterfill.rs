//! Mirrors sdk-ts/tests/waterfill.test.ts (Experiment 9 / Thm 8.10).

use four_corners_worker::waterfill::{sqrt_gain_scene, waterfill, Scene};

#[test]
fn equalises_marginal_gain_and_matches_grid_search_optimum() {
    let scenes = vec![sqrt_gain_scene("a", 3.0, None), sqrt_gain_scene("b", 1.0, None), sqrt_gain_scene("c", 2.0, None)];
    let budget = 10.0;
    let result = waterfill(&scenes, budget, 1e-9, 200);

    let total: f64 = result.allocation.values().sum();
    assert!((total - budget).abs() < 1e-4);

    let grid_best = grid_search_maximize(&scenes, budget, 60);
    assert!((result.value - grid_best).abs() < 1e-2);
}

#[test]
fn drops_a_scene_whose_first_unit_returns_less_than_the_shadow_price() {
    let scenes = vec![sqrt_gain_scene("rich", 10.0, None), sqrt_gain_scene("poor", 0.01, None)];
    let result = waterfill(&scenes, 5.0, 1e-9, 200);
    assert!(*result.allocation.get("poor").unwrap_or(&0.0) < 1e-4);
    assert!(*result.allocation.get("rich").unwrap() > 0.0);
}

#[test]
fn non_concave_scenes_break_waterfillings_prescription() {
    let budget = 5.0_f64;
    let increasing_returns: Scene = Scene {
        id: "sigmoid".to_string(),
        gain: Box::new(move |a| if a <= 0.0 { 0.0 } else { 4.76 * (a / budget).powi(3) }),
        marginal_gain: Box::new(move |a| if a <= 0.0 { 1e-6 } else { (4.76 * 3.0 * (a / budget).powi(2)) / budget }),
        max_attention: None,
    };
    let other: Scene = Scene { id: "flat".to_string(), gain: Box::new(|_| 0.11), marginal_gain: Box::new(|_| 0.0), max_attention: None };

    let concentrated = (increasing_returns.gain)(budget) + (other.gain)(0.0);
    let even_split = (increasing_returns.gain)(budget / 2.0) + (other.gain)(budget / 2.0);
    assert!(concentrated > even_split * 5.0);
}

/// Brute-force grid search over a 3-scene simplex, independent of the bisection solver — the cross-check ground truth.
fn grid_search_maximize(scenes: &[Scene], budget: f64, n: u32) -> f64 {
    assert_eq!(scenes.len(), 3, "test helper assumes 3 scenes");
    let (s0, s1, s2) = (&scenes[0], &scenes[1], &scenes[2]);
    let mut best = f64::NEG_INFINITY;
    for i in 0..=n {
        for j in 0..=(n - i) {
            let a0 = budget * i as f64 / n as f64;
            let a1 = budget * j as f64 / n as f64;
            let a2 = budget - a0 - a1;
            if a2 < 0.0 {
                continue;
            }
            let value = (s0.gain)(a0) + (s1.gain)(a1) + (s2.gain)(a2);
            if value > best {
                best = value;
            }
        }
    }
    best
}
