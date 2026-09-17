import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { buildTwoCluster, classSignatures } from "../../lib/closure";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 320;
const MARGIN = { top: 16, right: 16, bottom: 40, left: 48 };

export function ClosureChart() {
  const [internalB, setInternalB] = useState(8.0);
  const [invokedB, setInvokedB] = useState(false);

  const curve = useMemo(() => {
    const pts: { ib: number; sigA: number; sigB: number }[] = [];
    for (let i = 0; i <= 20; i++) {
      const ib = 1.0 + (14.0 * i) / 20;
      const g = buildTwoCluster(2.0, 3.0, ib);
      const { aGate, bGate } = classSignatures(g);
      pts.push({ ib, sigA: aGate, sigB: bGate });
    }
    return pts;
  }, []);

  const current = useMemo(() => classSignatures(buildTwoCluster(2.0, 3.0, internalB)), [internalB]);
  const distinct = Math.abs(current.aGate - current.bGate) > 1e-6;

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([1, 15]).range([0, innerW]);
      const maxY = d3.max(curve, (d) => Math.max(d.sigA, d.sigB)) ?? 20;
      const y = d3.scaleLinear().domain([0, maxY * 1.08]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(5))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const lineA = d3.line<{ ib: number; sigA: number }>().x((d) => x(d.ib)).y((d) => y(d.sigA));
      const lineB = d3.line<{ ib: number; sigB: number }>().x((d) => x(d.ib)).y((d) => y(d.sigB));

      g.append("path").datum(curve).attr("fill", "none").attr("stroke", "#5fa8d3").attr("stroke-width", 2).attr("d", lineA as unknown as string);
      g.append("path").datum(curve).attr("fill", "none").attr("stroke", "#e0b464").attr("stroke-width", 2).attr("d", lineB as unknown as string);

      // current marker
      g.append("line")
        .attr("x1", x(internalB))
        .attr("x2", x(internalB))
        .attr("y1", 0)
        .attr("y2", innerH)
        .attr("stroke", "#7f95a6")
        .attr("stroke-dasharray", "2,2");

      g.append("circle").attr("cx", x(internalB)).attr("cy", y(current.aGate)).attr("r", 5).attr("fill", "#5fa8d3");
      g.append("circle").attr("cx", x(internalB)).attr("cy", y(current.bGate)).attr("r", 5).attr("fill", "#e0b464");

      g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(6));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("B-cluster internal weight");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -36)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("class signature σ");

      const legend = g.append("g").attr("transform", `translate(12, 8)`);
      [
        { c: "#5fa8d3", l: "A_gate class" },
        { c: "#e0b464", l: "B_gate class" },
      ].forEach((item, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 15})`);
        row.append("circle").attr("r", 3.5).attr("fill", item.c);
        row.append("text").attr("x", 9).attr("y", 3).attr("font-size", 9.5).attr("fill", "#a9bccd").attr("font-family", "Inter, sans-serif").text(item.l);
      });
    },
    [curve, internalB, current],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: gate A clears any threshold trivially while a distinct class waits</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="B internal weight" value={internalB} min={1} max={15} step={0.25} onChange={setInternalB} />
        <div className="control-row">
          <label>invoke gate B?</label>
          <button className={`btn ${invokedB ? "btn-primary" : ""}`} onClick={() => setInvokedB((v) => !v)}>
            {invokedB ? "invoked" : "not yet invoked"}
          </button>
        </div>
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className="pill pill-ok">gate A clears θ ≤ 0.999999 trivially</span>
        <span className={`pill ${distinct ? "pill-bad" : "pill-ok"}`}>
          {distinct ? "classes are distinct" : "classes coincide"}
        </span>
        {invokedB && distinct && <span className="pill pill-bad">contested closure — decline</span>}
      </div>
      <p className="chart-caption">
        Gate A alone always reaches a terminus whose self-alignment trivially clears any confidence threshold — that is
        what "terminal alignment to itself" means. But its class signature is numerically distinct from gate B's for
        almost every internal weight. A confidence-threshold rule stops after A; a closure rule waits for B and, once
        both are invoked, correctly reports contested closure rather than picking one silently.
      </p>
    </div>
  );
}
