import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { randomContactGraph, claims, separationCost, floorOfGraph } from "../../lib/graph";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;
const MARGIN = { top: 16, right: 24, bottom: 40, left: 48 };

export function FloorChart() {
  const [density, setDensity] = useState(0.35);
  const [nGraphs, setNGraphs] = useState(24);
  const [seed, setSeed] = useState(7);

  const { points, beta } = useMemo(() => {
    const minW = 1.0;
    const maxW = 5.0;
    const pts: { size: number; sigma: number }[] = [];
    let globalMin = Infinity;
    for (let g = 0; g < nGraphs; g++) {
      const n = 3 + (g % 12);
      const graph = randomContactGraph(n, seed * 1000 + g, { density, minW, maxW });
      const b = floorOfGraph(graph);
      globalMin = Math.min(globalMin, b);
      for (const c of claims(graph)) {
        pts.push({ size: n, sigma: separationCost(graph, c) });
      }
    }
    return { points: pts, beta: globalMin };
  }, [density, nGraphs, seed]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;

      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([2, 15]).range([0, innerW]);
      const maxSigma = d3.max(points, (d) => d.sigma) ?? 10;
      const y = d3.scaleLinear().domain([0, maxSigma * 1.08]).range([innerH, 0]);

      // gridlines
      g.append("g")
        .selectAll("line")
        .data(y.ticks(6))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      // floor line
      g.append("line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", y(beta))
        .attr("y2", y(beta))
        .attr("stroke", "#e08b90")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", "5,3");

      g.append("text")
        .attr("x", innerW - 4)
        .attr("y", y(beta) - 6)
        .attr("text-anchor", "end")
        .attr("fill", "#e08b90")
        .attr("font-size", 11)
        .attr("font-family", "Inter, sans-serif")
        .text(`floor β = ${beta.toFixed(2)}`);

      // points
      g.append("g")
        .selectAll("circle")
        .data(points)
        .join("circle")
        .attr("cx", (d) => x(d.size) + (Math.random() - 0.5) * 8)
        .attr("cy", (d) => y(d.sigma))
        .attr("r", 3.2)
        .attr("fill", "#5fa8d3")
        .attr("fill-opacity", 0.55);

      // axes
      g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(8).tickFormat(d3.format("d")));

      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("claims in graph");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -36)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("separation cost σ(v)");
    },
    [points, beta],
  );

  const violations = points.filter((p) => p.sigma < beta - 1e-9).length;

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: separation cost never falls below the floor</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="contact density" value={density} min={0.05} max={0.9} step={0.05} onChange={setDensity} />
        <Slider label="graphs sampled" value={nGraphs} min={4} max={60} step={2} onChange={setNGraphs} format={(v) => v.toFixed(0)} />
        <Slider label="random seed" value={seed} min={1} max={99} step={1} onChange={setSeed} format={(v) => v.toFixed(0)} />
      </div>
      <p className="chart-caption">
        Each point is one claim's exact separation cost <span className="mono">σ(v)</span> (min-cut against the medium,
        computed live via Edmonds–Karp) in a randomly generated contact graph. Drag the sliders to regenerate —
        the floor line always sits at or below every point: <span className="mono">{violations}</span> violations
        observed out of <span className="mono">{points.length}</span> claims.
      </p>
    </div>
  );
}
