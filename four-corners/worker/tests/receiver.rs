//! Mirrors sdk-ts/tests/receiver.ts-adjacent behavior: monotone history
//! (Thm 8.9) and snapshot round-tripping compatible with the four-corners
//! server's receiver_snapshots JSON shape.

use four_corners_worker::receiver::ReceiverGraph;

#[test]
fn committed_count_strictly_increases_and_never_resets_on_rollback_attempt() {
    let mut receiver = ReceiverGraph::new("r1", None).unwrap();
    assert_eq!(receiver.committed_count(), 0);

    receiver.fix_distinction("a", 1.0).unwrap();
    assert_eq!(receiver.committed_count(), 1);

    receiver.fix_distinction("a", 1.0).unwrap(); // re-fixing an existing claim is not a new commit
    assert_eq!(receiver.committed_count(), 1);

    receiver.fix_distinction("b", 1.0).unwrap();
    assert_eq!(receiver.committed_count(), 2);

    receiver.acknowledge_rollback_attempt();
    assert_eq!(receiver.committed_count(), 3, "an 'undo' is itself a committed act — it must never lower the count");
}

#[test]
fn register_cell_always_reflects_the_current_graph() {
    let mut receiver = ReceiverGraph::new("r1", None).unwrap();
    let cell1 = receiver.register_cell("claim-a", 5.0).unwrap();
    assert_eq!(cell1.separation_cost, 5.0);

    receiver.fix_distinction("claim-b", 3.0).unwrap();
    receiver.fix_contact("claim-a", "claim-b", 1.0).unwrap();

    let cell2 = receiver.register_cell("claim-a", 5.0).unwrap();
    assert!(cell2.committed_count > cell1.committed_count, "each registration must reflect the graph as it currently stands");
}

#[test]
fn snapshot_round_trips_through_the_servers_json_shape() {
    let mut receiver = ReceiverGraph::new("r1", None).unwrap();
    receiver.fix_distinction("a", 4.0).unwrap();
    receiver.fix_distinction("b", 6.0).unwrap();
    receiver.fix_contact("a", "b", 2.0).unwrap();

    let snapshot = receiver.snapshot();
    let json = serde_json::to_string(&snapshot).unwrap();
    let parsed: four_corners_worker::receiver::ReceiverSnapshot = serde_json::from_str(&json).unwrap();

    let restored = ReceiverGraph::new("r1", Some(parsed)).unwrap();
    assert_eq!(restored.committed_count(), receiver.committed_count());
    assert_eq!(restored.floor(), receiver.floor());
}

#[test]
fn refuses_to_load_a_snapshot_from_a_different_receiver() {
    let mut receiver = ReceiverGraph::new("r1", None).unwrap();
    receiver.fix_distinction("a", 1.0).unwrap();
    let snapshot = receiver.snapshot();

    let result = ReceiverGraph::new("r2-not-r1", Some(snapshot));
    assert!(result.is_err());
}
