import { describe, it, expect } from "vitest";
import { ContactGraph } from "../src/graph.js";

/**
 * Mirrors validation Experiment 2 / Example 3.2 (the true, irrelevant
 * passage): a content graph ranks the general textbook passage T above the
 * specific explanation E (T wins on content-alignment), while the SAME two
 * claims rank in the OPPOSITE order in the researcher's receiver graph (E
 * wins on meaning). Content-optimal and meaning-optimal are different
 * claims entirely — this is what Thm 3.4 proves and the SDK must exhibit,
 * not just assert.
 */
describe("content vs meaning diverge (Thm 3.4 / Experiment 2)", () => {
  it("rank-flips T and E between the corpus graph and the receiver graph", () => {
    // Corpus/content graph: T is lexically/topically close to lots of general
    // material (many strong contacts), E is a narrow, thinly-connected claim.
    const corpus = new ContactGraph();
    corpus.addClaim("T", 10.0); // strongly anchored: high content alignment
    corpus.addClaim("E", 2.0); // weakly anchored: low content alignment
    corpus.addClaim("generalKinetics1", 8.0);
    corpus.addClaim("generalKinetics2", 8.0);
    corpus.addContact("T", "generalKinetics1", 9.0);
    corpus.addContact("T", "generalKinetics2", 9.0);

    const alignT_corpus = corpus.separationCost("T");
    const alignE_corpus = corpus.separationCost("E");
    expect(alignT_corpus).toBeGreaterThan(alignE_corpus); // T wins on content

    // Receiver graph: the researcher already holds fixed the specific assay
    // and buffer condition, so E is densely individuated against those, while
    // T sits nearly isolated as "textbook background."
    const receiver = new ContactGraph();
    receiver.addClaim("T", 1.5); // weakly anchored here: low meaning-alignment
    receiver.addClaim("E", 13.5); // strongly individuated against the fixed project context
    receiver.addClaim("thisAssay", 12.0);
    receiver.addClaim("thisBuffer", 12.0);
    receiver.addContact("E", "thisAssay", 13.0);
    receiver.addContact("E", "thisBuffer", 13.0);

    const alignT_receiver = receiver.separationCost("T");
    const alignE_receiver = receiver.separationCost("E");
    expect(alignE_receiver).toBeGreaterThan(alignT_receiver); // E wins on meaning — opposite order

    // The flip itself: the winner under content is the loser under meaning.
    expect(alignT_corpus > alignE_corpus).toBe(true);
    expect(alignE_receiver > alignT_receiver).toBe(true);
  });
});
