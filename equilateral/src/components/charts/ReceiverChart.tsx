import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { newGraph, addClaim, addContact, separationCost, floorOfGraph, mulberry32, type ContactGraph } from "../../lib/graph";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;
const MARGIN = { top: 16, right: 24, bottom: 40, left: 48 };

function buildReceiver(density: number, seed: number, nContext = 8): ContactGraph {
  const rng = mulberry32(seed);
  const g = newGraph();
  addClaim(g, "target", 1.0);
  for (let i = 0; i < nContext; i++) {
    const c = `ctx_${i}`;
    addClaim(g, c, 1.0);
    if (rng() < density) addContact(g, "target", c, 1.0 + rng() * 3.0);
    for (let j = 0; j < i; j++) {
      if (rng() < density * 0.5) addContact(g, c, `ctx_${j}`, 1.0 + rng() * 3.0);
    }
  }
  return g;
}

const SEEDS = [3, 30, 300];
const COLORS = ["#2dd4bf", "#5fa8d3", "#e0b464"];

export function ReceiverChart() {
  const [contextSize, setContextSize] = useState(8);

  const series = useMemo(() => {
    return SEEDS.map((seed) => {
      const pts: { density: number; sigma: number; beta: number }[] = [];
      for (let i = 0; i <= 20; i++) {
        const density = i / 20;
        const g = buildReceiver(density, seed * 100 + Math.round(density * 1000), contextSize);
        pts.push({ density, sigma: separationCost(g, "target"), beta: floorOfGraph(g) });
      }
      return { seed, pts };
    });
  }, [contextSize]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0, 1]).range([0, innerW]);
      const maxSigma = d3.max(series.flatMap((s2) => s2.pts.map((p) => p.sigma))) ?? 10;
      const y = d3.scaleLinear().domain([0, maxSigma * 1.08]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(6))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const line = d3
        .line<{ density: number; sigma: number }>()
        .x((d) => x(d.density))
        .y((d) => y(d.sigma))
        .curve(d3.curveMonotoneX);

      series.forEach((ser, i) => {
        g.append("path")
          .datum(ser.pts)
          .attr("fill", "none")
          .attr("stroke", COLORS[i])
          .attr("stroke-width", 2)
          .attr("d", line as unknown as string);
        g.selectAll(`.pt-${i}`)
          .data(ser.pts)
          .join("circle")
          .attr("class", `pt-${i}`)
          .attr("cx", (d) => x(d.density))
          .attr("cy", (d) => y(d.sigma))
          .attr("r", 2.6)
          .attr("fill", COLORS[i]);
      });

      g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(".1f")));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("receiver context density");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -36)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("registered σ(target)");

      const legend = g.append("g").attr("transform", `translate(12, 8)`);
      SEEDS.forEach((seed, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 16})`);
        row.append("circle").attr("r", 3.5).attr("fill", COLORS[i]);
        row
          .append("text")
          .attr("x", 10)
          .attr("y", 3)
          .attr("font-size", 9.5)
          .attr("fill", "#a9bccd")
          .attr("font-family", "Inter, sans-serif")
          .text(`receiver ${seed}`);
      });
    },
    [series],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: the same claim registers a different cell in every receiver</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider
          label="context size"
          value={contextSize}
          min={3}
          max={14}
          step={1}
          onChange={setContextSize}
          format={(v) => v.toFixed(0)}
        />
      </div>
      <p className="chart-caption">
        Three simulated receivers (a junior researcher, a colleague, a principal investigator — different seeded prior
        context) register the identical claim <span className="mono">target</span> at a different separation cost as
        their own context density varies. Every registration is independently floor-attaining in its own graph; none is
        privileged.
      </p>
    </div>
  );
}
