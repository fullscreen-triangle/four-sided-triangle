import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { ClosureChart } from "../components/charts/ClosureChart";

export function SectionClosure() {
  return (
    <Section
      id="closure"
      eyebrow="Part II · Retrieval as Individuation"
      title="Closure: The Correct Stopping Rule"
      lede="A search is finished when no further available source can add a new answer class — never when a confidence score crosses a threshold. The two criteria are provably different, and closure is strictly stronger."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            Let <Formula>Cell(v₀, Π)</Formula> be the set of target claims reachable by admissible propagations of
            seed <Formula>v₀</Formula>, partitioned into classes under endpoint-indistinguishability. A search is{" "}
            <em>closed</em> if extending it by any available, uninvoked catalyst cannot add a new class.
          </p>

          <TheoremBox label="Theorem 8.10" title="Closure is strictly stronger than a confidence threshold">
            <p>
              There exist process graphs and thresholds such that a propagation's terminal alignment trivially
              clears any confidence threshold, while a further, uninvoked catalyst reaches a target in a distinct
              class — the search is not closed although the threshold is cleared.
            </p>
          </TheoremBox>

          <DefinitionBox label="Theorem 8.11" title="Convergent closure or honest decline">
            <p>
              Over a finite catalyst registry, every search terminates in exactly one of: convergent closure (the
              class set stabilises to one class), or contested closure (more than one class survives, reported as{" "}
              <em>decline</em> together with the distinct classes found).
            </p>
          </DefinitionBox>

          <RemarkBox label="Remark" title="Decline is a correct output, not an error">
            <p>
              A retrieval system must be able to report "the sources disagree, here are the distinct positions" as a
              first-class, correctly-terminating outcome — not loop indefinitely, and not silently emit one
              contested class as though it were unique because it ranked highest by content similarity.
            </p>
          </RemarkBox>
        </div>

        <ClosureChart />
      </div>
    </Section>
  );
}
