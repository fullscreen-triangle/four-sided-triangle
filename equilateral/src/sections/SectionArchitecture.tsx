import { Section } from "../components/ui/Section";
import { DefinitionBox, TheoremBox, RemarkBox, Formula } from "../components/ui/Boxes";
import { FederationChart } from "../components/charts/FederationChart";
import { WaterfillChart } from "../components/charts/WaterfillChart";
import { HistoryChart } from "../components/charts/HistoryChart";

export function SectionArchitecture() {
  return (
    <Section
      id="architecture"
      eyebrow="Part III · Architecture"
      title="A Society of Split-Attention Agents"
      lede="Each former pipeline stage becomes a bounded agent: its own conserved identity, its own finite attention budget divided by a provably optimal rule across competing sources, and a monotone history that forbids ever answering from a stale cache."
    >
      <div className="prose" style={{ marginBottom: "2.5rem" }}>
        <p>
          A <em>receiver</em> is a bounded map from queries to candidate answers with a positive floor. A{" "}
          <em>federation</em> of receivers takes the <strong>union</strong> of their candidate sets — every
          receiver's candidate is offered as admissible, so a query on which one federation member is precise
          benefits the whole federation even where the others are not.
        </p>

        <TheoremBox label="Theorem 8.1" title="Federation lowers the floor">
          <p>
            <Formula>β(Fed) ≤ min ᵢ β(Recᵢ)</Formula>, strictly whenever non-redundant at every member; under
            independent resolution failure, <Formula>1 − β(Fed)/Ω = ∏ᵢ (1 − β(Recᵢ)/Ω)</Formula>.
          </p>
        </TheoremBox>
      </div>

      <FederationChart />

      <div className="prose" style={{ margin: "2.5rem 0" }}>
        <p>
          Each agent faces several concurrent <em>scenes</em> — competing information sources — and divides a
          finite attention budget among them.
        </p>

        <DefinitionBox label="Axiom" title="Diminishing returns of attention">
          <p>
            Every gain profile is concave: the first unit of attention committed to a scene removes at least as much
            purpose residual as any later unit. This is an assumption about the sources an agent faces, not a
            consequence of the agent's own structure.
          </p>
        </DefinitionBox>

        <TheoremBox label="Theorem 10.4" title="Water-filling attention division">
          <p>
            Under the concavity axiom, the value-maximising allocation is characterised by a single price{" "}
            <Formula>p* ≥ 0</Formula>: the agent equalises marginal gain across every attended scene and drops any
            scene whose first unit of attention returns less than <Formula>p*</Formula>.
          </p>
        </TheoremBox>
      </div>

      <WaterfillChart />

      <div className="prose" style={{ margin: "2.5rem 0" }}>
        <p>Each agent also carries a committed count that only ever increases, never restored by any operation.</p>

        <TheoremBox label="Theorem 10.6" title="Monotone, irreversible agent history">
          <p>
            Every committed act strictly increases the committed count; no operation — including an explicit
            rollback — decreases it. Recalling is searching: every answer is the terminus of a fresh
            residual-descending walk over the agent's <em>current</em> self-graph, never a cached value returned
            without a walk.
          </p>
        </TheoremBox>

        <RemarkBox label="Remark" title="Why a research assistant must not cache answers across sessions">
          <p>
            Caching an answer computed at an earlier state of the corpus and returning it verbatim once the corpus
            has grown returns an answer appropriate to a self the system has irreversibly left — no operation
            restores the graph to its earlier state. This is a correctness requirement once the corpus is understood
            to grow monotonically with the group's own work, not merely a freshness preference.
          </p>
        </RemarkBox>
      </div>

      <HistoryChart />
    </Section>
  );
}
