//! Mirrors sdk-ts/tests/graph.test.ts (Experiment 1 / Thm 2.7): no claim
//! ever registers a separation cost below its own graph's floor, and the
//! floor is attained exactly by a minimum-weight singleton contact.

use four_corners_worker::graph::ContactGraph;

fn mulberry32(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = a;
        t = (t ^ (t >> 15)).wrapping_mul(t | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        ((t ^ (t >> 14)) as f64) / 4294967296.0
    }
}

#[test]
fn no_claim_separation_cost_falls_below_the_floor() {
    let mut rng = mulberry32(1234);
    let mut observations = 0;
    let mut violations = 0;

    for _ in 0..60 {
        let n = 3 + (rng() * 10.0) as usize;
        let mut g = ContactGraph::new();
        let ids: Vec<String> = (0..n).map(|i| format!("c{i}")).collect();
        for id in &ids {
            g.add_claim(id, 1.0 + rng() * 9.0).unwrap();
        }
        for i in 0..n {
            for j in (i + 1)..n {
                if rng() < 0.3 {
                    let a = four_corners_worker::graph::VertexId::Claim(ids[i].clone());
                    let b = four_corners_worker::graph::VertexId::Claim(ids[j].clone());
                    g.add_contact(&a, &b, 1.0 + rng() * 9.0).unwrap();
                }
            }
        }
        let floor = g.floor();
        for id in &ids {
            observations += 1;
            let sigma = g.separation_cost(id).unwrap();
            if sigma < floor - 1e-9 {
                violations += 1;
            }
        }
    }

    assert!(observations > 100);
    assert_eq!(violations, 0);
}

#[test]
fn floor_is_attained_exactly_by_a_minimum_weight_singleton_contact() {
    let mut g = ContactGraph::new();
    g.add_claim("weak", 2.0).unwrap();
    g.add_claim("strong", 9.0).unwrap();
    assert_eq!(g.floor(), 2.0);
    assert_eq!(g.separation_cost("weak").unwrap(), 2.0);
}

#[test]
fn rejects_zero_and_negative_weights() {
    let mut g = ContactGraph::new();
    assert!(g.add_claim("x", 0.0).is_err());
    assert!(g.add_claim("x", -1.0).is_err());
}
