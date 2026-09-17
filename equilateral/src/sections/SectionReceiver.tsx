import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { ReceiverChart } from "../components/charts/ReceiverChart";

export function SectionReceiver() {
  return (
    <Section
      id="receiver"
      eyebrow="Part I · Foundations"
      title="Individuation by Negation and Receiver-Relativity"
      lede="Recognising a thing and searching for it are inverse readings of one relation — so there is no third, privileged place, neither in the corpus nor in the querier, where 'the answer' resides. Relevance is not a receiver-independent fact."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            In a medium with no privileged claim, a claim can only be fixed as the complement of what it is not — a
            selector naming a distinguished member would itself need to be selected, and the regress terminates only
            at a rule that names no member: specifying the negation set and taking the claim as the remainder.
          </p>

          <DefinitionBox label="Definition 4.2" title="Query; decoder; projector">
            <p>
              A decoder <Formula>Dec: Q → V</Formula> sends a query to the claim it individuates. A projector{" "}
              <Formula>Proj: V → 2^Q</Formula> sends a claim to the set of queries that decode to it,{" "}
              <Formula>Proj(v) := Dec⁻¹({"{v}"})</Formula>.
            </p>
          </DefinitionBox>

          <TheoremBox label="Theorem 4.3" title="Recognition/search identity">
            <p>
              For every claim <Formula>v</Formula> and query <Formula>q</Formula>:{" "}
              <Formula>Dec(q) = v ⟺ q ∈ Proj(v)</Formula>. Recognition and search are inverse readings of the single
              relation <Formula>{"{(q, v) : Dec(q) = v}"}</Formula> — neither is definable without the other. Neither
              the document nor the querier holds the answer prior to the encounter; it is a joint fact.
            </p>
          </TheoremBox>

          <TheoremBox label="Theorem 4.4" title="Distinct receivers register distinct, equally correct cells">
            <p>
              The same claim registers different cells in receivers with different decoder graphs, and each
              registration is a correct individuation at that receiver's own floor. No registration is privileged as
              "the" relevance of the claim.
            </p>
          </TheoremBox>

          <RemarkBox label="Remark" title="The two researchers">
            <p>
              A junior researcher new to a project and the project's own principal investigator, issuing the
              identical query, are different receivers: the junior researcher's graph holds few prior distinctions
              fixed, so a broad textbook passage may correctly register as the useful cell; the senior researcher's
              graph holds the entire project history fixed, so the same passage correctly registers as{" "}
              <em>already known, uninformative</em>. Neither is wrong.
            </p>
          </RemarkBox>
        </div>

        <ReceiverChart />
      </div>
    </Section>
  );
}
