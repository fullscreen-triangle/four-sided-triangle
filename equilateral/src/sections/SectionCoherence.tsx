import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { CoherenceChart } from "../components/charts/CoherenceChart";

export function SectionCoherence() {
  return (
    <Section
      id="coherence"
      eyebrow="Part II · Retrieval as Individuation"
      title="Coherence Requires a Triangle"
      lede="A claim is robustly grounded only by a strongly connected cycle of at least three independently sourced, mutually supporting catalysts — never a single passage, and never two, however strongly they agree."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            Say catalyst <Formula>γⱼ</Formula> <em>supports</em> <Formula>γᵢ</Formula> at threshold{" "}
            <Formula>θ</Formula> if its result reinforces, to degree at least <Formula>θ</Formula>, the alignment
            shift <Formula>γᵢ</Formula> induces. This gives a directed <em>support graph</em>.
          </p>

          <TheoremBox label="Theorem 8.8" title="Linear chains and pairs fail; a triangle grounds">
            <p>
              (i) No acyclic chain, whose terminal member is justified by nothing internal to the chain, is robust to
              removal of that member. (ii) A 2-cycle fails the majority condition{" "}
              <Formula>θ &gt; 1/2</Formula>: removing either catalyst leaves exactly one, unsupported. (iii) Three
              catalysts mutually supporting one another at <Formula>θ &gt; 1/2</Formula>, forming a strongly
              connected triangle, ground the claim robustly — surviving removal of any single member.
            </p>
          </TheoremBox>

          <DefinitionBox label="Corollary" title="Coherence is decidable from signs alone">
            <p>
              Whether a coalition is coherent is decidable from the <em>signs</em> of pairwise support — whether
              each pair reinforces or undercuts the other — with no access to numerical confidence magnitudes at all.
            </p>
          </DefinitionBox>

          <RemarkBox label="Remark" title="One passage is never a grounded answer, and neither are two">
            <p>
              A system returning one top-ranked passage has a support graph of one vertex and no cycle. A system
              requiring agreement between exactly two sources has a support graph whose only possible cycle has
              length two — proved insufficient. Robust grounding is a structural minimum of three.
            </p>
          </RemarkBox>

          <p>Click any node in the diagram to remove it and watch whether the remaining coalition stays grounded.</p>
        </div>

        <CoherenceChart />
      </div>
    </Section>
  );
}
