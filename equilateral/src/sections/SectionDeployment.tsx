import { Section } from "../components/ui/Section";
import { RemarkBox, Formula } from "../components/ui/Boxes";

const PRINCIPLES = [
  {
    label: "Individuate against the researcher, not the query alone",
    body:
      "Retrieval must be computed against a specific researcher's own receiver graph — a graph accreting the distinctions their project and prior queries have already fixed — not against the bare query string. One persistent, monotonically accreting self-graph per researcher or active project thread.",
  },
  {
    label: "Coherence before serving a claim as grounded",
    body:
      "A claim is served as grounded only once a strongly connected triangle of independently sourced, mutually supporting catalysts backs it — a document passage, a structured record, and the domain-adapted model's own inference, each independently reinforcing the others. Single- or two-sourced claims are marked as such, never silently promoted.",
  },
  {
    label: "Closure, not a similarity threshold, ends a search",
    body:
      "A query is answered once the federated registry is closed: no further available source can add a new answer class. Contested closure is served as a first-class output — the distinct positions found, attributed to their sources.",
  },
  {
    label: "Route-audit cross-source claims",
    body:
      "Whenever the domain-adapted model's inference and document or structured-record retrieval agree on a claim's surface content, the four-column relaxation runs before the claim is served as corroborated, since surface agreement alone provably cannot exclude a false friend.",
  },
];

export function SectionDeployment() {
  return (
    <Section
      id="deployment"
      eyebrow="Part III · Architecture"
      title="A Concrete Instantiation for a Research-Group Deployment"
      lede="Internal documents, a domain-adapted model trained on the group's own data, and structured records are federated receivers in one contact graph, individuated against a named researcher's own decoder rather than scored against a receiver-independent notion of relevance."
    >
      <div className="prose" style={{ marginBottom: "2rem" }}>
        <p>
          Instantiate one contact graph per source: <Formula>Γ_doc</Formula> over document chunks weighted by
          lexical and citation proximity, <Formula>Γ_model</Formula> over the domain-adapted model's inferable
          claims — trained restricted to the domain's <em>extremal regime</em>, its hardest, fullest-coverage task
          instances, which provably transfers competence downward to every easier query without further training —
          and <Formula>Γ_struct</Formula> over structured records weighted by schema-defined relations. Federate the
          three under the union construction.
        </p>
      </div>

      <div className="toc" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
        {PRINCIPLES.map((p, i) => (
          <div className="toc-item" key={i} style={{ cursor: "default" }}>
            <div className="toc-num">Principle {i + 1}</div>
            <div className="toc-label">{p.label}</div>
            <div className="toc-desc">{p.body}</div>
          </div>
        ))}
      </div>

      <RemarkBox label="Remark" title="What changes concretely in an existing eight-stage pipeline">
        <p>
          A pipeline organised as a fixed sequence — query processing, semantic gap detection, domain-knowledge
          extraction, reasoning optimisation, solution generation, scoring, comparison, verification — is
          reorganised as a society graph in which each former stage is a bounded agent rather than a stateless
          function: each carries its own conserved identity across queries, divides its own attention by
          water-filling across the sources or sub-tasks concurrently competing for it, and answers by search against
          its own current self-graph rather than by returning a cached intermediate. The orchestrator's role narrows
          to maintaining the society's own shared purpose, running the coherence and closure checks before a final
          answer is served, and dividing collective budget across concurrently open research questions by the
          identical water-filling law one level up.
        </p>
      </RemarkBox>
    </Section>
  );
}
