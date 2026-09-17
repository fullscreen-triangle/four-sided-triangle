import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { ContentMeaningChart } from "../components/charts/ContentMeaningChart";

export function SectionContentMeaning() {
  return (
    <Section
      id="content-meaning"
      eyebrow="Part I · Foundations"
      title="Content and Meaning Provably Diverge"
      lede="A retrieved passage's literal tokens and its individuating cut against a specific researcher's own graph are different objects. A retriever tuned to the first can be arbitrarily wrong about the second — and this is the exact, provable content of a true, well-sourced, high-similarity result being useless."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            Consider the ordinary failure: a query is embedded, the nearest chunk by cosine similarity is retrieved,
            and it is a genuine, correctly cited, factually accurate passage — and it does not answer the question,
            because the question was never really about those tokens. It was about a specific configuration of a
            specific problem, for which the retrieved passage is a true statement about something adjacent.
          </p>

          <DefinitionBox label="Definition 3.1" title="Content versus meaning">
            <p>
              The <em>content</em> of a claim is its label — the literal tokens of the passage it names. The{" "}
              <em>meaning</em> of a claim relative to a receiver graph is its resting cut in that graph: the region
              of contrasts individuating it against that receiver's own rest. They coincide only when the literal
              form is itself the operative individuation — the degenerate case.
            </p>
          </DefinitionBox>

          <TheoremBox label="Theorem 3.2" title="Content and meaning come apart">
            <p>
              A content map sending each claim to its highest-similarity correspondent does not in general preserve
              meaning. Two independent obstructions guarantee this: different carvings (a corpus graph may resolve
              one cell where a receiver graph resolves several), and content is not meaning even within one carving
              (a correspondent's content is preserved by construction, but content is exactly what meaning is not).
            </p>
          </TheoremBox>

          <p>
            The chart alongside constructs this explicitly rather than merely asserting it: two claims,{" "}
            <Formula>T</Formula> (a true general statement) and <Formula>E</Formula> (the specific explanation
            actually needed), ranked in opposite orders by two different graphs over the identical pair of weights.
          </p>

          <RemarkBox label="Corollary 3.3" title="A content-similarity score is not a meaning score">
            <p>
              Cosine similarity, BM25, or a learned reranker trained on content-pair relevance labels computes an
              approximation to content correspondence — never to meaning. It can be improved on the first axis while
              remaining arbitrarily wrong on the second. This is the precise, provable content behind "true but
              useless": the system was never computing the quantity the researcher needed.
            </p>
          </RemarkBox>
        </div>

        <ContentMeaningChart />
      </div>
    </Section>
  );
}
