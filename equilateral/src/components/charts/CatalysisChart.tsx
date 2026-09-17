import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { compositePower, repeatedCurve } from "../../lib/catalysis";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 44 };

export function CatalysisChart() {
  const [p1, setP1] = useState(0.5);
  const [p2, setP2] = useState(0.35);
  const [p3, setP3] = useState(0.3);
  const [p4, setP4] = useState(0.25);
  const [repeatedPower, setRepeatedPower] = useState(0.35);

  const diversePowers = [p1, p2, p3, p4];
  const diverseComposite = compositePower(diversePowers);
  const meanPower = diversePowers.reduce((a, b) => a + b, 0) / diversePowers.length;
  const repeatedComposite = compositePower([repeatedPower, repeatedPower, repeatedPower, repeatedPower]);

  const repeatedSingleCurve = useMemo(() => repeatedCurve(repeatedPower, 12), [repeatedPower]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0, 12]).range([0, innerW]);
      const y = d3.scaleLinear().domain([0, 1]).range([innerH, 0]);

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
        .attr("y1", y(1))
        .attr("y2", y(1))
        .attr("stroke", "#7f95a6")
        .attr("stroke-dasharray", "2,2");

      const line = d3
        .line<number>()
        .x((_, i) => x(i))
        .y((d) => y(d))
        .curve(d3.curveMonotoneX);

      g.append("path")
        .datum(repeatedSingleCurve)
        .attr("fill", "none")
        .attr("stroke", "#e0b464")
        .attr("stroke-width", 2.4)
        .attr("d", line as unknown as string);

      g.selectAll("circle.pt")
        .data(repeatedSingleCurve)
        .join("circle")
        .attr("class", "pt")
        .attr("cx", (_, i) => x(i))
        .attr("cy", (d) => y(d))
        .attr("r", 3)
        .attr("fill", "#e0b464");

      // mark the 4-repetition point for comparison against diverse composite
      g.append("circle")
        .attr("cx", x(4))
        .attr("cy", y(repeatedComposite))
        .attr("r", 6)
        .attr("fill", "none")
        .attr("stroke", "#e08b90")
        .attr("stroke-width", 2);

      g.append("circle")
        .attr("cx", x(4))
        .attr("cy", y(diverseComposite))
        .attr("r", 6)
        .attr("fill", "none")
        .attr("stroke", "#2dd4bf")
        .attr("stroke-width", 2);

      g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(12).tickFormat(d3.format("d")));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5).tickFormat(d3.format(".0%")));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("repetitions of one catalyst (orange curve)");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -32)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("composite power");
    },
    [repeatedSingleCurve, diverseComposite, repeatedComposite],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: repeating one catalyst vs. diversifying four</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="repeated catalyst power" value={repeatedPower} min={0.05} max={0.95} step={0.01} onChange={setRepeatedPower} />
      </div>
      <div className="control-panel">
        <Slider label="diverse: catalyst 1" value={p1} min={0.05} max={0.95} step={0.01} onChange={setP1} />
        <Slider label="diverse: catalyst 2" value={p2} min={0.05} max={0.95} step={0.01} onChange={setP2} />
        <Slider label="diverse: catalyst 3" value={p3} min={0.05} max={0.95} step={0.01} onChange={setP3} />
        <Slider label="diverse: catalyst 4" value={p4} min={0.05} max={0.95} step={0.01} onChange={setP4} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className="pill" style={{ borderLeft: "3px solid #e0b464" }}>
          repeated ×4 @ mean {repeatedPower.toFixed(2)}: {repeatedComposite.toFixed(4)}
        </span>
        <span className="pill" style={{ borderLeft: "3px solid #2dd4bf" }}>
          diverse ×4 @ mean {meanPower.toFixed(2)}: {diverseComposite.toFixed(4)}
        </span>
      </div>
      <p className="chart-caption">
        The orange curve is <span className="mono">1 − (1 − κ)ⁿ</span> for a single repeated catalyst — strictly
        increasing, never reaching 1. The teal and red rings mark the composite power of four{" "}
        <em>diverse</em> catalysts (teal) against four <em>repeated</em> applications at the matched mean power (red),
        both at chain length 4 — move the sliders to see diversity weakly dominate repetition at equal mean cost.
      </p>
    </div>
  );
}
