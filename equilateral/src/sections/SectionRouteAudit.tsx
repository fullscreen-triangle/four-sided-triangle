import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { RouteAuditChart } from "../components/charts/RouteAuditChart";

export function SectionRouteAudit() {
  return (
    <Section
      id="route-audit"
      eyebrow="Part II · Retrieval as Individuation"
      title="Cross-Source Verification Without a Shared Representation"
      lede="Two sources with no shared internal representation can certify mutual agreement without either exposing its internals — by auditing what each answer provokes as a follow-up, not just what it says on the surface."
    >
      <div className="grid-2">
        <div className="prose">
          <p>
            Two receivers are an <em>opaque pair</em> if no computable map relates their internal states — a trained
            domain adapter's weights share no decoding with a structured database's schema. Given a common query,
            each produces a <em>column</em> (its answer) and a <em>provoked column</em> — the follow-up its own
            answer would generate under its own internal policy.
          </p>

          <DefinitionBox label="Definition 9.2" title="Quiescence">
            <p>
              The relaxation is <em>quiescent</em> at tolerance <Formula>τ = β(A) + β(B)</Formula> if all four
              pairwise cross-demands among the central and provoked columns fall below <Formula>τ</Formula> and
              remain there.
            </p>
          </DefinitionBox>

          <TheoremBox label="Theorem 9.3" title="The four-column criterion">
            <p>
              The system is quiescent iff the central columns agree <em>and</em> the provoked columns agree.
              Quiescence certifies identity of meaning by the <em>route</em>, not merely the endpoints — computed
              without either receiver disclosing its internal state.
            </p>
          </TheoremBox>

          <TheoremBox label="Theorem 9.4" title="Route-audit catches a false friend">
            <p>
              There exist opaque pairs and queries for which the central cross-demands are both below tolerance
              while the provoked cross-demands are not — the pair is non-quiescent although an endpoint-only
              comparison would report agreement.
            </p>
          </TheoremBox>

          <RemarkBox label="Remark" title="Two internal documents can agree for different reasons">
            <p>
              A protocol write-up and a results summary may state numerically identical conclusions while one holds
              under an assumption the other's context silently violates. A system comparing only stated content
              reports agreement; the four-column route-audit exposes the divergence.
            </p>
          </RemarkBox>
        </div>

        <RouteAuditChart />
      </div>
    </Section>
  );
}
