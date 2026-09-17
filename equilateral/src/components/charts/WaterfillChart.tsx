import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { waterFill, gainCurve, type Scene } from "../../lib/waterfilling";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 44 };
const COLORS = ["#5fa8d3", "#2dd4bf", "#e0b464", "#a78bfa"];

export function WaterfillChart() {
  const [budget, setBudget] = useState(3.0);
  const [m1, setM1] = useState(4.0);
  const [m2, setM2] = useState(3.0);
  const [m3, setM3] = useState(2.0);
  const [tau, setTau] = useState(1.5);

  const scenes: Scene[] = [
    { id: "docs", label: "document index", m: m1, tau },
    { id: "kg", label: "structured records", m: m2, tau },
    { id: "model", label: "domain model", m: m3, tau },
  ];

  const result = useMemo(() => waterFill(scenes, budget), [m1, m2, m3, tau, budget]);
  const curves = useMemo(() => scenes.map((s) => gainCurve(s, 6, 60)), [m1, m2, m3, tau]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0, 6]).range([0, innerW]);
      const maxGamma = Math.max(m1, m2, m3) * 1.05;
      const y = d3.scaleLinear().domain([0, maxGamma]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(5))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const line = d3.line<{ a: number; gamma: number }>().x((d) => x(d.a)).y((d) => y(d.gamma));

      curves.forEach((curve, i) => {
        g.append("path")
          .datum(curve)
          .attr("fill", "none")
          .attr("stroke", COLORS[i])
          .attr("stroke-width", 2)
          .attr("d", line as unknown as string);

        // allocation marker
        const a = result.allocations[i];
        const val = result.values[i];
        g.append("line")
          .attr("x1", x(a))
          .attr("x2", x(a))
          .attr("y1", innerH)
          .attr("y2", y(val))
          .attr("stroke", COLORS[i])
          .attr("stroke-dasharray", "3,2")
          .attr("stroke-width", 1.2);
        g.append("circle").attr("cx", x(a)).attr("cy", y(val)).attr("r", 5).attr("fill", COLORS[i]);
      });

      g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(6));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("attention committed to scene");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -32)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("purpose gain γ(a)");

      const legend = g.append("g").attr("transform", `translate(${innerW - 170}, 8)`);
      scenes.forEach((sc, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 15})`);
        row.append("circle").attr("r", 3.5).attr("fill", COLORS[i]);
        row.append("text").attr("x", 9).attr("y", 3).attr("font-size", 9.5).attr("fill", "#a9bccd").attr("font-family", "Inter, sans-serif").text(sc.label);
      });
    },
    [curves, result],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: dividing a finite attention budget across three sources</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="budget" value={budget} min={0.2} max={8} step={0.1} onChange={setBudget} />
        <Slider label="doc index scale m₁" value={m1} min={0.5} max={6} step={0.1} onChange={setM1} />
        <Slider label="structured records m₂" value={m2} min={0.5} max={6} step={0.1} onChange={setM2} />
        <Slider label="domain model m₃" value={m3} min={0.5} max={6} step={0.1} onChange={setM3} />
        <Slider label="decay τ (shared)" value={tau} min={0.3} max={4} step={0.1} onChange={setTau} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className="pill">shadow price p* = {result.priceStar.toFixed(3)}</span>
        {scenes.map((sc, i) => (
          <span key={sc.id} className="pill" style={{ borderLeft: `3px solid ${COLORS[i]}` }}>
            {sc.label}: a* = {result.allocations[i].toFixed(2)}
          </span>
        ))}
      </div>
      <p className="chart-caption">
        Dashed markers show the water-filling optimum: every attended scene's marginal gain equals the same shadow
        price <span className="mono">p*</span>, and a scene whose entry margin falls below <span className="mono">p*</span> receives
        zero allocation. Raise the budget or lower <span className="mono">p*</span> and watch previously-dropped scenes activate.
      </p>
    </div>
  );
}
