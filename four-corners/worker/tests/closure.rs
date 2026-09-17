//! Mirrors sdk-ts/tests/closure.test.ts (Experiment 6 / Thm 6.6-6.7).

use four_corners_worker::closure::{run_to_closure, AnswerClass, AvailableSource, ClosureResult};

fn source_returning(id: &str, key: &str, representative: &str) -> AvailableSource {
    let id_owned = id.to_string();
    let key = key.to_string();
    let representative = representative.to_string();
    AvailableSource {
        id: id_owned.clone(),
        invoke: Box::new(move || {
            let key = key.clone();
            let representative = representative.clone();
            let id = id_owned.clone();
            Box::pin(async move { Some(AnswerClass { key, representative, supporting_catalyst_ids: vec![id] }) })
        }),
    }
}

#[tokio::test]
async fn reports_contested_closure_for_two_disjoint_gates() {
    let gate_a = source_returning("gateA", "clusterA", "answer from cluster A");
    let gate_b = source_returning("gateB", "clusterB", "answer from cluster B");

    let result = run_to_closure(&[gate_a, gate_b]).await;
    match result {
        ClosureResult::Contested { classes } => {
            let mut keys: Vec<&str> = classes.iter().map(|c| c.key.as_str()).collect();
            keys.sort();
            assert_eq!(keys, vec!["clusterA", "clusterB"]);
        }
        other => panic!("expected Contested, got {other:?}"),
    }
}

#[tokio::test]
async fn reports_convergent_closure_when_every_source_lands_in_the_same_class() {
    let sources = vec![
        source_returning("s1", "sameClass", "agreed answer"),
        source_returning("s2", "sameClass", "agreed answer"),
        source_returning("s3", "sameClass", "agreed answer"),
    ];
    let result = run_to_closure(&sources).await;
    match result {
        ClosureResult::Closed { class } => {
            let mut ids = class.supporting_catalyst_ids.clone();
            ids.sort();
            assert_eq!(ids, vec!["s1", "s2", "s3"]);
        }
        other => panic!("expected Closed, got {other:?}"),
    }
}

#[tokio::test]
async fn declines_with_no_sources() {
    let result = run_to_closure(&[]).await;
    assert!(matches!(result, ClosureResult::Declined { .. }));
}

#[tokio::test]
async fn declines_when_sources_are_exhausted_and_none_reach_an_answer() {
    let dead = AvailableSource { id: "dead".to_string(), invoke: Box::new(|| Box::pin(async { None })) };
    let result = run_to_closure(&[dead]).await;
    assert!(matches!(result, ClosureResult::Declined { .. }));
}
