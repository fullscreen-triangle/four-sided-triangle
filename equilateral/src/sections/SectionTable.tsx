import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { PropagationTableChart } from "../components/charts/PropagationTableChart";

export function SectionTable() {
  return (
    <Section
      id="table"
      eyebrow="Part II · Retrieval as Individuation"
      title="The Causal Propagation Table: One Object, Two Readings"
      lede="A static knowledge-graph lookup and a generative multi-hop answer are not two subsystems requiring an interface. They are the identical table, evaluated at two settings of one process argument."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            Fix a contact graph, a seed claim, and a target claim. A <em>propagation</em> is a walk along edges from
            seed to target. The <em>trivial process</em> has only one available operation: the direct contact
            between a claim and the medium.
          </p>

          <DefinitionBox label="Definition 5.1" title="Causal propagation table">
            <p>
              <Formula>T(v₀, x*, Π) := cut(S*(x*))</Formula> if some propagation under process{" "}
              <Formula>Π</Formula> is accountable, else <Formula>∅</Formula>.
            </p>
          </DefinitionBox>

          <TheoremBox label="Theorem 5.2" title="The directional identity">
            <p>
              For every claim <Formula>v</Formula>: <Formula>cut(S*(v)) = T(v, v, Π_rest(v))</Formula> — the resting
              catalogue is exactly the table restricted to trivial processes. For a nontrivial process, the table's
              output is an object of the <em>same type</em>: an accountable cut of weight <Formula>≥ β</Formula>,
              the convergent terminus of a walk, computed under process rather than at rest.
            </p>
          </TheoremBox>

          <p>
            Toggle the chart between the two settings: at rest, the table returns claim <Formula>x*</Formula>'s
            resting cut against the medium — a catalogue entry. Under a nontrivial process, it returns the terminus
            of an actual multi-hop walk — a generated answer. Same table, same type of output, two settings of one
            argument.
          </p>

          <TheoremBox label="Theorem 5.3" title="Path opacity">
            <p>
              A propagation is admissible if and only if its terminal claim is the target; interior claims are
              entirely unconstrained. No invariant computed from the endpoints alone distinguishes two admissible
              propagations differing only in their interior.
            </p>
          </TheoremBox>

          <RemarkBox label="Remark" title="A strange intermediate step is not evidence of failure">
            <p>
              A multi-hop retrieval-and-reasoning trajectory may pass through an intermediate claim that looks
              unrelated to the eventual answer without this being evidence the search has gone wrong. Evidence of
              failure is non-convergence — never the appearance of any single intermediate step.
            </p>
          </RemarkBox>
        </div>

        <PropagationTableChart />
      </div>
    </Section>
  );
}
