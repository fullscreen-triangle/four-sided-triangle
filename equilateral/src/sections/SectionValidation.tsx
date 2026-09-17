import { Section } from "../components/ui/Section";

const RESULTS = [
  { n: 1, theorem: "Resolution floor", figure: "0 / 930 violations across 120 random graphs" },
  { n: 2, theorem: "Content/meaning divergence", figure: "T: 10.0 vs 2.0 (content) → E: 13.5 vs 1.5 (meaning) — winners flip" },
  { n: 3, theorem: "Receiver-relativity", figure: "σ(target) ranges 1.0–9.0 across densities, every value at its own floor" },
  { n: 4, theorem: "Multiplicative law", figure: "predicted vs. simulated error < 10⁻⁹ across 400 chains" },
  { n: 5, theorem: "Coherence triangle", figure: "robustness jumps from 0 to 1 exactly at coalition size 3" },
  { n: 6, theorem: "Closure vs. threshold", figure: "θ = 0.999999 cleared while classes remain distinct (σ = 5.0 vs 10.0)" },
  { n: 7, theorem: "Route-audit", figure: "central demand 0.0, provoked demand 5.10 — false friend caught" },
  { n: 8, theorem: "Federation floor", figure: "10 = min(10, 25, 40); Monte Carlo error 7.6 × 10⁻⁵ on 200k trials" },
  { n: 9, theorem: "Water-filling", figure: "L₂ error < 9.5 × 10⁻⁵ vs. independent grid search; 40× gap when concavity fails" },
  { n: 10, theorem: "Monotone history", figure: "cached answer 8.0 vs. fresh answer 13.0 — 62.5% drift after 5 further acts" },
];

export function SectionValidation() {
  return (
    <Section
      id="validation"
      eyebrow="Part IV · Validation"
      title="Every Prediction Was Checked, and Held"
      lede="Ten seeded, reproducible computational experiments check every load-bearing theorem on explicitly constructed instances. All ten passed with zero violations of any load-bearing inequality — the same code paths reimplemented live in this page."
    >
      <div className="chart-card">
        <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "var(--font-sans)", fontSize: "0.88rem" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--rule-strong)", textAlign: "left" }}>
              <th style={{ padding: "0.6rem 0.4rem", width: "3rem" }}>#</th>
              <th style={{ padding: "0.6rem 0.4rem" }}>Theorem checked</th>
              <th style={{ padding: "0.6rem 0.4rem" }}>Key figure</th>
            </tr>
          </thead>
          <tbody>
            {RESULTS.map((r) => (
              <tr key={r.n} style={{ borderBottom: "1px solid var(--rule)" }}>
                <td style={{ padding: "0.6rem 0.4rem", fontFamily: "var(--font-mono)", color: "var(--ink-faint)" }}>{r.n}</td>
                <td style={{ padding: "0.6rem 0.4rem", fontWeight: 600 }}>{r.theorem}</td>
                <td style={{ padding: "0.6rem 0.4rem", fontFamily: "var(--font-mono)", fontSize: "0.82rem", color: "var(--ink-soft)" }}>
                  {r.figure}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="chart-caption" style={{ marginTop: "1.2rem", maxWidth: "var(--measure)" }}>
        Full details, raw JSON records, and the Python reference implementation are in the manuscript's{" "}
        <span className="mono">validation/</span> directory. Every chart on this page reimplements the same
        algorithms — exact min-cut via Edmonds–Karp, bisection water-filling, the bidirectional relaxation — directly
        in TypeScript, so the numbers you see by moving a slider are live recomputations, not illustrations.
      </p>
    </Section>
  );
}
