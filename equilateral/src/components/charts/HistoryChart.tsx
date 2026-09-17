import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { simulateHistory } from "../../lib/history";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 320;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 44 };

export function HistoryChart() {
  const [growBefore, setGrowBefore] = useState(6);
  const [growAfter, setGrowAfter] = useState(5);
  const [seed, setSeed] = useState(10);

  const result = useMemo(() => simulateHistory(seed, growBefore, growAfter), [seed, growBefore, growAfter]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0, result.events.length - 1]).range([0, innerW]);
      const maxCount = d3.max(result.events, (d) => d.count) ?? 10;
      const y = d3.scaleLinear().domain([0, maxCount * 1.1]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(6))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const step = d3
        .line<{ i: number; count: number }>()
        .x((d) => x(d.i))
        .y((d) => y(d.count))
        .curve(d3.curveStepAfter);

      const indexed = result.events.map((e, i) => ({ i, count: e.count, event: e.event }));

      g.append("path")
        .datum(indexed)
        .attr("fill", "none")
        .attr("stroke", "#7f95a6")
        .attr("stroke-width", 1.5)
        .attr("d", step as unknown as string);

      g.selectAll("circle")
        .data(indexed)
        .join("circle")
        .attr("cx", (d) => x(d.i))
        .attr("cy", (d) => y(d.count))
        .attr("r", (d) => (d.event === "rollback_attempt" ? 6 : 4))
        .attr("fill", (d) => (d.event === "rollback_attempt" ? "#e08b90" : "#5fa8d3"));

      // snapshot marker
      const snapshotIdx = indexed.findIndex((d) => d.count === result.snapshotCount);
      if (snapshotIdx >= 0) {
        g.append("line")
          .attr("x1", x(snapshotIdx))
          .attr("x2", x(snapshotIdx))
          .attr("y1", 0)
          .attr("y2", innerH)
          .attr("stroke", "#2dd4bf")
          .attr("stroke-dasharray", "4,3");
        g.append("text")
          .attr("x", x(snapshotIdx) + 4)
          .attr("y", 12)
          .attr("font-size", 9.5)
          .attr("fill", "#2dd4bf")
          .attr("font-family", "Inter, sans-serif")
          .text("cached here");
      }

      g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(8).tickFormat(d3.format("d")));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("committed act index");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -32)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("committed count M");
    },
    [result],
  );

  const staleDiff = Math.abs(result.freshAnswer - result.snapshotAnswer);

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: the count never decreases, and a cached answer goes stale</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="growth before snapshot" value={growBefore} min={1} max={12} step={1} onChange={setGrowBefore} format={(v) => v.toFixed(0)} />
        <Slider label="growth after snapshot" value={growAfter} min={0} max={12} step={1} onChange={setGrowAfter} format={(v) => v.toFixed(0)} />
        <Slider label="seed" value={seed} min={1} max={99} step={1} onChange={setSeed} format={(v) => v.toFixed(0)} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className="pill">snapshot answer @ M={result.snapshotCount}: {result.snapshotAnswer.toFixed(2)}</span>
        <span className="pill">fresh answer @ M={result.currentCount}: {result.freshAnswer.toFixed(2)}</span>
        <span className={`pill ${staleDiff > 1e-9 ? "pill-bad" : "pill-ok"}`}>
          {staleDiff > 1e-9 ? `stale by ${staleDiff.toFixed(2)}` : "no drift yet"}
        </span>
      </div>
      <p className="chart-caption">
        The red point is a deliberate rollback attempt — it raises the count rather than lowering it, exactly as
        Theorem 10.6 forces. The teal line marks where an answer was cached; every committed act afterwards changes
        the graph, so a fetch of the cached value silently disagrees with what a fresh search now returns.
      </p>
    </div>
  );
}
