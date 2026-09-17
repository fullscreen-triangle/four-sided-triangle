import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { realisedFloor } from "../../lib/federation";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 320;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 48 };
const OUTCOME_SIZE = 200;

export function FederationChart() {
  const [radiusA, setRadiusA] = useState(30);
  const [radiusB, setRadiusB] = useState(45);
  const [includeThird, setIncludeThird] = useState(true);
  const thirdRadius = 20;

  const radii = includeThird ? [radiusA, radiusB, thirdRadius] : [radiusA, radiusB];
  const fedFloor = useMemo(() => realisedFloor(radii, OUTCOME_SIZE), [radiusA, radiusB, includeThird]);
  const minIndividual = Math.min(...radii);

  const stepSeries = useMemo(() => {
    const sorted = [...radii].sort((a, b) => b - a); // worst first
    const pts: { k: number; floor: number; minSoFar: number }[] = [];
    for (let k = 1; k <= sorted.length; k++) {
      const subset = sorted.slice(0, k);
      pts.push({ k, floor: realisedFloor(subset, OUTCOME_SIZE), minSoFar: Math.min(...subset) });
    }
    return pts;
  }, [radiusA, radiusB, includeThird]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([1, stepSeries.length]).range([0, innerW]);
      const maxY = d3.max(stepSeries, (d) => d.floor) ?? 50;
      const y = d3.scaleLinear().domain([0, maxY * 1.1]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(5))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const lineFloor = d3.line<{ k: number; floor: number }>().x((d) => x(d.k)).y((d) => y(d.floor));
      const lineMin = d3.line<{ k: number; minSoFar: number }>().x((d) => x(d.k)).y((d) => y(d.minSoFar));

      g.append("path").datum(stepSeries).attr("fill", "none").attr("stroke", "#3a4d61").attr("stroke-width", 4).attr("d", lineMin as unknown as string);
      g.append("path").datum(stepSeries).attr("fill", "none").attr("stroke", "#5fa8d3").attr("stroke-width", 2).attr("d", lineFloor as unknown as string);

      g.selectAll("circle")
        .data(stepSeries)
        .join("circle")
        .attr("cx", (d) => x(d.k))
        .attr("cy", (d) => y(d.floor))
        .attr("r", 4)
        .attr("fill", "#5fa8d3");

      g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(radii.length).tickFormat(d3.format("d")));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("receivers federated (worst first)");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -36)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("floor");
    },
    [stepSeries],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: the federation floor tracks the sharpest receiver</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="receiver A radius" value={radiusA} min={5} max={60} step={1} onChange={setRadiusA} format={(v) => v.toFixed(0)} />
        <Slider label="receiver B radius" value={radiusB} min={5} max={60} step={1} onChange={setRadiusB} format={(v) => v.toFixed(0)} />
        <div className="control-row">
          <label>include third (fixed r=20)</label>
          <button className={`btn ${includeThird ? "btn-primary" : ""}`} onClick={() => setIncludeThird((v) => !v)}>
            {includeThird ? "included" : "excluded"}
          </button>
        </div>
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className="pill pill-ok">federation floor = {fedFloor}</span>
        <span className="pill">min individual = {minIndividual}</span>
      </div>
      <p className="chart-caption">
        Blue is the measured federation floor (brute-force search over a discretised outcome space, independent of any
        closed-form). Grey is the running minimum individual receiver floor. The union construction never exceeds the
        sharpest member — exactly Theorem 8.1's bound, with equality whenever the sharpest receiver's coverage already
        subsumes what the others would add.
      </p>
    </div>
  );
}
