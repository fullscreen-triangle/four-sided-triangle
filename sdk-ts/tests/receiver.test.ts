import { describe, it, expect } from "vitest";
import { ReceiverGraph } from "../src/receiver.js";

/**
 * Thm 8.9 (monotone history) plus snapshot round-tripping: a receiver's
 * state must survive a full snapshot -> reload cycle exactly, regardless of
 * which order the underlying graph's internal edge iteration happens to
 * visit vertices in (see the medium-edge-direction fix in receiver.ts —
 * snapshot() must not assume MEDIUM always appears on one particular side
 * of an edge).
 */
describe("ReceiverGraph — monotone history and snapshot round-trip", () => {
  it("committed count strictly increases, and an explicit rollback attempt still increases it", () => {
    const r = new ReceiverGraph("r1");
    expect(r.history.committedCount).toBe(0);

    r.fixDistinction("a");
    expect(r.history.committedCount).toBe(1);

    r.fixDistinction("a"); // re-fixing an existing claim is not a new commit
    expect(r.history.committedCount).toBe(1);

    r.fixDistinction("b");
    expect(r.history.committedCount).toBe(2);

    r.acknowledgeRollbackAttempt();
    expect(r.history.committedCount).toBe(3);
  });

  it("snapshot -> reload round-trips claims, floor, and committed count exactly", () => {
    const r = new ReceiverGraph("r1");
    r.fixDistinction("a", 4);
    r.fixDistinction("b", 6);
    r.fixContact("a", "b", 2);

    const snapshot = r.snapshot();
    const reloaded = new ReceiverGraph("r1", snapshot);

    expect(reloaded.history.committedCount).toBe(r.history.committedCount);
    expect(reloaded.floor()).toBe(r.floor());
    expect(new Set(snapshot.claims)).toEqual(new Set(["a", "b"]));
  });

  it("every medium-adjacent edge in a snapshot has b === '__medium__', regardless of internal edge order", () => {
    const r = new ReceiverGraph("r1");
    r.fixDistinction("a", 4);
    r.fixDistinction("b", 6);
    r.fixDistinction("c", 3);
    r.fixContact("a", "b", 2);
    r.fixContact("b", "c", 1);

    const snapshot = r.snapshot();
    const mediumEdges = snapshot.edges.filter((e) => e.a === "__medium__" || e.b === "__medium__");
    // Exactly one medium-edge per claim (a, b, c), and always oriented with
    // the medium marker on b — never silently dropped or misoriented.
    expect(mediumEdges).toHaveLength(3);
    for (const edge of mediumEdges) {
      expect(edge.b).toBe("__medium__");
      expect(edge.a).not.toBe("__medium__");
    }
  });

  it("refuses to load a snapshot from a different receiver", () => {
    const r = new ReceiverGraph("r1");
    r.fixDistinction("a");
    const snapshot = r.snapshot();

    expect(() => new ReceiverGraph("r2-not-r1", snapshot)).toThrow();
  });
});
