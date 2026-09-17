import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { relax, provoke } from "../../lib/relaxation";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 320;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 48 };
const TOLERANCE = 0.05;

export function RouteAuditChart() {
  const [conditionDivergence, setConditionDivergence] = useState(3.5);
  const [centralNoise, setCentralNoise] = useState(0.0);

  const result = useMemo(() => {
    const central = [1.0, 2.0, 3.0];
    const b = central.map((v) => v + centralNoise);
    const conditionA = [conditionDivergence, -conditionDivergence * 0.7, conditionDivergence * 0.3];
    const conditionB = [-conditionDivergence, conditionDivergence * 0.7, -conditionDivergence * 0.3];
    const pa = provoke(central, conditionA);
    const pb = provoke(b, conditionB);
    return relax(central, b, pa, pb, TOLERANCE, 50);
  }, [conditionDivergence, centralNoise]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0, result.steps.length - 1]).range([0, innerW]);
      const maxY = d3.max(result.steps, (d) => d.maxResidual) ?? 1;
      const y = d3.scaleLinear().domain([0, Math.max(maxY * 1.1, TOLERANCE * 2)]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(5))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      g.append("line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", y(TOLERANCE))
        .attr("y2", y(TOLERANCE))
        .attr("stroke", "#e08b90")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", "5,3");

      g.append("text")
        .attr("x", innerW - 4)
        .attr("y", y(TOLERANCE) - 6)
        .attr("text-anchor", "end")
        .attr("font-size", 10)
        .attr("fill", "#e08b90")
        .attr("font-family", "Inter, sans-serif")
        .text(`tolerance τ = ${TOLERANCE}`);

      const lineCentral = d3.line<{ round: number; central: number }>().x((d) => x(d.round)).y((d) => y(d.central));
      const lineProvoked = d3.line<{ round: number; provoked: number }>().x((d) => x(d.round)).y((d) => y(d.provoked));

      g.append("path")
        .datum(result.steps)
        .attr("fill", "none")
        .attr("stroke", "#5fa8d3")
        .attr("stroke-width", 2)
        .attr("d", lineCentral as unknown as string);

      g.append("path")
        .datum(result.steps)
        .attr("fill", "none")
        .attr("stroke", "#e08b90")
        .attr("stroke-width", 2)
        .attr("d", lineProvoked as unknown as string);

      g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(8));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("relaxation round");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -36)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("cross-demand");

      const legend = g.append("g").attr("transform", `translate(12, 8)`);
      [
        { c: "#5fa8d3", l: "central demand" },
        { c: "#e08b90", l: "provoked demand" },
      ].forEach((item, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 15})`);
        row.append("line").attr("x1", 0).attr("x2", 16).attr("stroke", item.c).attr("stroke-width", 2);
        row.append("text").attr("x", 22).attr("y", 3).attr("font-size", 9.5).attr("fill", "#a9bccd").attr("font-family", "Inter, sans-serif").text(item.l);
      });
    },
    [result],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: central agreement is not enough</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="central noise" value={centralNoise} min={0} max={0.3} step={0.01} onChange={setCentralNoise} />
        <Slider label="provoke divergence" value={conditionDivergence} min={0} max={5} step={0.1} onChange={setConditionDivergence} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className={`pill ${result.finalCentral < TOLERANCE ? "pill-ok" : "pill-bad"}`}>
          central demand {result.finalCentral.toFixed(3)}
        </span>
        <span className={`pill ${result.finalProvoked < TOLERANCE ? "pill-ok" : "pill-bad"}`}>
          provoked demand {result.finalProvoked.toFixed(3)}
        </span>
        <span className={`pill ${result.quiescent ? "pill-ok" : "pill-bad"}`}>
          {result.quiescent ? "quiescent — same meaning" : "non-quiescent — false friend detected"}
        </span>
      </div>
      <p className="chart-caption">
        Push <em>central noise</em> to zero and <em>provoke divergence</em> up: the two receivers' surface answers are
        identical (blue line collapses immediately) while what each answer provokes as a follow-up diverges (red line
        plateaus above tolerance). An endpoint-only comparison sees perfect agreement; the four-column route-audit does
        not — exactly Theorem 9.4's constructed false friend.
      </p>
    </div>
  );
}
