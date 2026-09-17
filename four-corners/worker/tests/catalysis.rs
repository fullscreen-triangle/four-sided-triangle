//! Mirrors sdk-ts/tests/catalysis.test.ts (Experiments 4 & 5 / Thm 6.2, 6.4).

use four_corners_worker::catalysis::{assess_grounding, composite_power, Catalyst, GroundingStatus, SupportEdge};

fn catalyst(id: &str, source: &str, power: f64) -> Catalyst {
    Catalyst { id: id.to_string(), source: source.to_string(), power }
}

#[test]
fn multiplicative_law_matches_worked_example() {
    let expected = [0.0, 0.4, 0.64, 0.784, 0.8704];
    for (reps, exp) in expected.iter().enumerate() {
        let catalysts: Vec<Catalyst> = (0..reps).map(|i| catalyst(&format!("c{i}"), "same", 0.4)).collect();
        let power = composite_power(&catalysts);
        assert!((power - exp).abs() < 1e-9, "reps={reps} expected={exp} got={power}");
    }
}

#[test]
fn never_reaches_one_under_repetition() {
    let catalysts: Vec<Catalyst> = (0..12).map(|i| catalyst(&format!("c{i}"), "same", 0.4)).collect();
    let power = composite_power(&catalysts);
    assert!(power < 1.0);
    assert!(power > 0.99);
}

#[test]
fn diverse_catalysts_weakly_dominate_homogeneous_repeats_at_matched_mean_power() {
    let diverse = vec![catalyst("a", "docs", 0.5), catalyst("b", "model", 0.35), catalyst("c", "records", 0.3), catalyst("d", "web", 0.25)];
    let mean = diverse.iter().map(|c| c.power).sum::<f64>() / diverse.len() as f64;
    let homogeneous: Vec<Catalyst> = (0..4).map(|i| catalyst(&format!("h{i}"), "same", mean)).collect();

    let diverse_power = composite_power(&diverse);
    let homogeneous_power = composite_power(&homogeneous);
    assert!(diverse_power >= homogeneous_power);
    assert!((diverse_power - 0.8294).abs() < 1e-3);
    assert!((homogeneous_power - 0.8215).abs() < 1e-3);
}

#[test]
fn single_source_is_never_grounded() {
    let result = assess_grounding(&[catalyst("a", "docs", 0.6)], &[], None);
    assert_eq!(result.status, GroundingStatus::SingleSourced);
}

#[test]
fn mutually_supporting_pair_fails_robustness() {
    let catalysts = vec![catalyst("a", "docs", 0.6), catalyst("b", "model", 0.6)];
    let support = vec![
        SupportEdge { from: "a".to_string(), to: "b".to_string(), degree: 0.9 },
        SupportEdge { from: "b".to_string(), to: "a".to_string(), degree: 0.9 },
    ];
    let result = assess_grounding(&catalysts, &support, None);
    assert_eq!(result.status, GroundingStatus::TwoSourced);
    assert!(!result.robust_to_single_removal);
}

#[test]
fn strongly_connected_triangle_of_three_is_grounded_and_robust() {
    let catalysts = vec![catalyst("a", "docs", 0.6), catalyst("b", "model", 0.6), catalyst("c", "records", 0.6)];
    let ids = ["a", "b", "c"];
    let mut support = Vec::new();
    for from in ids {
        for to in ids {
            if from != to {
                support.push(SupportEdge { from: from.to_string(), to: to.to_string(), degree: 0.75 });
            }
        }
    }
    let result = assess_grounding(&catalysts, &support, None);
    assert_eq!(result.status, GroundingStatus::Grounded);
    assert!(result.robust_to_single_removal);
}

#[test]
fn four_cycle_also_survives() {
    let catalysts = vec![catalyst("a", "docs", 0.6), catalyst("b", "model", 0.6), catalyst("c", "records", 0.6), catalyst("d", "web", 0.6)];
    let ids = ["a", "b", "c", "d"];
    let mut support = Vec::new();
    for from in ids {
        for to in ids {
            if from != to {
                support.push(SupportEdge { from: from.to_string(), to: to.to_string(), degree: 0.75 });
            }
        }
    }
    let result = assess_grounding(&catalysts, &support, None);
    assert_eq!(result.status, GroundingStatus::Grounded);
}
