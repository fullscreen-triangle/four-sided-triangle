import { describe, it, expect } from "vitest";
import { compositePower, assessGrounding, type Catalyst, type SupportEdge } from "../src/catalysis.js";

describe("multiplicative catalytic law (Thm 6.2 / Experiment 4)", () => {
  it("matches independent sequential simulation for repeated application of one catalyst", () => {
    const single = (power: number, reps: number): Catalyst[] =>
      Array.from({ length: reps }, (_, i) => ({ id: `c${i}`, source: "same", power }));

    // 0, 0.4, 0.64, 0.784, ... -> approaches 1, matching the paper's worked example.
    const expected = [0, 0.4, 0.64, 0.784, 0.8704];
    for (let reps = 0; reps < expected.length; reps++) {
      expect(compositePower(single(0.4, reps))).toBeCloseTo(expected[reps]!, 9);
    }
  });

  it("never reaches 1 under repetition, but does under an idealized infinite diverse chain limit", () => {
    const reps = 12;
    const power = compositePower(Array.from({ length: reps }, (_, i) => ({ id: `c${i}`, source: "same", power: 0.4 })));
    expect(power).toBeLessThan(1);
    expect(power).toBeGreaterThan(0.99); // ~0.998 per the paper
  });

  it("diverse catalysts weakly dominate homogeneous repeats at matched mean power (Cor 6.3)", () => {
    const diverse: Catalyst[] = [
      { id: "a", source: "docs", power: 0.5 },
      { id: "b", source: "model", power: 0.35 },
      { id: "c", source: "records", power: 0.3 },
      { id: "d", source: "web", power: 0.25 },
    ];
    const mean = diverse.reduce((s, c) => s + c.power, 0) / diverse.length;
    const homogeneous: Catalyst[] = Array.from({ length: 4 }, (_, i) => ({ id: `h${i}`, source: "same", power: mean }));

    expect(compositePower(diverse)).toBeGreaterThanOrEqual(compositePower(homogeneous));
    expect(compositePower(diverse)).toBeCloseTo(0.8294, 3);
    expect(compositePower(homogeneous)).toBeCloseTo(0.8215, 3);
  });
});

describe("coherence triangle (Thm 6.4 / Experiment 5)", () => {
  const cat = (id: string, source: string): Catalyst => ({ id, source, power: 0.6 });

  it("a single source is never grounded", () => {
    const result = assessGrounding([cat("a", "docs")], []);
    expect(result.status).toBe("single-sourced");
  });

  it("a mutually-supporting pair fails robustness (Thm 6.4(ii)) — never promoted past two-sourced", () => {
    const catalysts = [cat("a", "docs"), cat("b", "model")];
    const support: SupportEdge[] = [
      { from: "a", to: "b", degree: 0.9 },
      { from: "b", to: "a", degree: 0.9 },
    ];
    const result = assessGrounding(catalysts, support);
    expect(result.status).toBe("two-sourced");
    expect(result.robustToSingleRemoval).toBe(false);
  });

  it("a strongly-connected triangle of 3 independent sources is grounded and robust to any single removal", () => {
    const catalysts = [cat("a", "docs"), cat("b", "model"), cat("c", "records")];
    const support: SupportEdge[] = [
      { from: "a", to: "b", degree: 0.75 },
      { from: "b", to: "a", degree: 0.75 },
      { from: "b", to: "c", degree: 0.75 },
      { from: "c", to: "b", degree: 0.75 },
      { from: "a", to: "c", degree: 0.75 },
      { from: "c", to: "a", degree: 0.75 },
    ];
    const result = assessGrounding(catalysts, support);
    expect(result.status).toBe("grounded");
    expect(result.robustToSingleRemoval).toBe(true);
  });

  it("a 4-cycle also survives (robustness holds at n=3 and beyond, transition is exactly at 2->3)", () => {
    const catalysts = [cat("a", "docs"), cat("b", "model"), cat("c", "records"), cat("d", "web")];
    const ids = catalysts.map((c) => c.id);
    const support: SupportEdge[] = [];
    for (const from of ids) for (const to of ids) if (from !== to) support.push({ from, to, degree: 0.75 });
    const result = assessGrounding(catalysts, support);
    expect(result.status).toBe("grounded");
  });
});
