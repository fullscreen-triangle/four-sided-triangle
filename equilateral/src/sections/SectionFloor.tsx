import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { FloorChart } from "../components/charts/FloorChart";

export function SectionFloor() {
  return (
    <Section
      id="floor"
      eyebrow="Part I · Foundations"
      title="The Resolution Floor"
      lede="Every retrieval, in a corpus that is never fully indexed, costs something strictly positive. No result is a point — every result is a bounded region, and the bound is derived, not assumed."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            A corpus, a knowledge base, and a querying agent are each modelled as a <strong>contact graph</strong>: a
            finite weighted graph with one distinguished vertex, the <em>medium</em>, standing for everything not yet
            individuated — every document not yet ingested, every record not yet linked, every inference the model
            has not yet drawn. Vertices other than the medium are <em>claims</em>: candidate individuated units of
            information.
          </p>

          <DefinitionBox label="Definition 2.1" title="Contact graph; the medium">
            <p>
              A contact graph is a finite weighted graph <Formula>Γ = (V, E, w)</Formula> together with a
              distinguished vertex <Formula>m</Formula>, adjacent to every other vertex. An edge between two claims
              is a <em>contact</em>; its weight is the cost of the distinction separating them.
            </p>
          </DefinitionBox>

          <p>
            The central hypothesis is an order condition, not a cardinality claim: the medium is never exhausted by
            any finite stage of search. However large the index, however well the model was trained, there is always
            a further source not yet consulted.
          </p>

          <TheoremBox label="Theorem 2.3" title="Resolution floor">
            <p>
              There is a constant <Formula>β &gt; 0</Formula> such that <Formula>w(e) ≥ β</Formula> for every
              contact and <Formula>σ(v) ≥ β</Formula> for every claim: no retrieval separates a claim from the medium
              at zero cost, and no result is returned for free.
            </p>
          </TheoremBox>

          <RemarkBox label="Remark" title="Not an engineering defect">
            <p>
              This does not say retrieval is imprecise because indexes are imperfect. It says that retrieval against
              a genuinely inexhaustible medium cannot, even with a perfect instrument, terminate at zero residual —
              because that would require completing a comparison against a medium that, by hypothesis, is never
              completed. This becomes the basis of an honest stopping rule (closure, §7) rather than a caveat to
              apologise for.
            </p>
          </RemarkBox>
        </div>

        <FloorChart />
      </div>
    </Section>
  );
}
