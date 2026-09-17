import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, Formula } from "../components/ui/Boxes";
import { CatalysisChart } from "../components/charts/CatalysisChart";

// small shim so we don't need a separate export just for a spacer div
function Spacer() {
  return <div style={{ height: "0.2rem" }} />;
}

export function SectionCatalysis() {
  return (
    <Section
      id="catalysis"
      eyebrow="Part II · Retrieval as Individuation"
      title="Catalytic Composition"
      lede="Combining independent search steps is a multiplicative operation with a precise law of diminishing returns — and diversifying sources beats repeating one, as a forced mathematical fact rather than a heuristic."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            A <em>catalyst</em> is the operation that realises one contact edge: a search-engine query, a local
            index scan, a database lookup, or an inference drawn from a trained model. Its <em>power</em> is the
            fraction of above-floor alignment gap it closes in one application.
          </p>

          <TheoremBox label="Theorem 8.6" title="Multiplicative composition">
            <p>
              For catalysts applied in sequence with powers <Formula>κ₁, …, κₙ</Formula>, the composite power is{" "}
              <Formula>κ(γ₁⋯γₙ) = 1 − ∏ᵢ(1 − κᵢ)</Formula>.
            </p>
          </TheoremBox>

          <DefinitionBox label="Corollary 8.7" title="Diversify sources, do not repeat them">
            <p>
              Repeating one source <Formula>n</Formula> times yields power <Formula>1 − (1 − κ)ⁿ</Formula>: strictly
              increasing, never reaching 1. A chain of near-duplicate calls to one index accrues power slowly and
              may fail to saturate even in principle; a chain of independent catalysts addressing distinct
              evidentiary channels saturates faster and more robustly.
            </p>
          </DefinitionBox>

          <Spacer />

          <p>
            This is forced by the multiplicative law itself, not an empirical heuristic about retrieval engines.
            Drag the sliders to see the composite power of four diverse catalysts against four repeated applications
            at the matched mean power — diversity weakly dominates at every setting.
          </p>
        </div>

        <CatalysisChart />
      </div>
    </Section>
  );
}
