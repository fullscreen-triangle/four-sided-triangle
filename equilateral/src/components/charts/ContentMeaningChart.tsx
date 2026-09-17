import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { newGraph, addClaim, addContact, alignment } from "../../lib/graph";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;
const MARGIN = { top: 16, right: 24, bottom: 40, left: 52 };

function buildContentGraph(wT: number) {
  const g = newGraph();
  addClaim(g, "query", 1.0);
  addClaim(g, "T", 1.0);
  addClaim(g, "E", 1.0);
  addContact(g, "query", "T", wT);
  addContact(g, "query", "E", 1.0);
  return g;
}

function buildReceiverGraph(wE: number) {
  const g = newGraph();
  addClaim(g, "live", 1.0);
  addClaim(g, "T", 1.0);
  addClaim(g, "E", 1.0);
  addClaim(g, "cause1", 1.0);
  addClaim(g, "cause2", 1.0);
  addContact(g, "live", "T", 0.5);
  addContact(g, "live", "E", wE);
  addContact(g, "E", "cause1", 4.0);
  addContact(g, "E", "cause2", 4.0);
  addContact(g, "live", "cause1", 3.0);
  addContact(g, "live", "cause2", 3.0);
  return g;
}

export function ContentMeaningChart() {
  const [sweep, setSweep] = useState(6.0);

  const { content, receiver } = useMemo(() => {
    const points: { w: number; contentT: number; contentE: number; receiverT: number; receiverE: number }[] = [];
    for (let i = 0; i <= 20; i++) {
      const w = 0.5 + (12.0 * i) / 20;
      const gc = buildContentGraph(w);
      const gr = buildReceiverGraph(w);
      points.push({
        w,
        contentT: alignment(gc, "T", "query"),
        contentE: alignment(gc, "E", "query"),
        receiverT: alignment(gr, "T", "live"),
        receiverE: alignment(gr, "E", "live"),
      });
    }
    const gcCurrent = buildContentGraph(sweep);
    const grCurrent = buildReceiverGraph(sweep);
    return {
      content: {
        points,
        current: { T: alignment(gcCurrent, "T", "query"), E: alignment(gcCurrent, "E", "query") },
      },
      receiver: {
        current: { T: alignment(grCurrent, "T", "live"), E: alignment(grCurrent, "E", "live") },
      },
    };
  }, [sweep]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const innerW = WIDTH - MARGIN.left - MARGIN.right;
      const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;
      const g = s.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      const x = d3.scaleLinear().domain([0.5, 12.5]).range([0, innerW]);
      const allVals = content.points.flatMap((p) => [p.contentT, p.contentE, p.receiverT, p.receiverE]);
      const y = d3.scaleLinear().domain([0, (d3.max(allVals) ?? 20) * 1.05]).range([innerH, 0]);

      g.append("g")
        .selectAll("line")
        .data(y.ticks(6))
        .join("line")
        .attr("class", "grid-line")
        .attr("x1", 0)
        .attr("x2", innerW)
        .attr("y1", (d) => y(d))
        .attr("y2", (d) => y(d));

      const lineGen = (key: "contentT" | "contentE" | "receiverT" | "receiverE") =>
        d3
          .line<{ w: number }>()
          .x((d) => x(d.w))
          .y((d) => y((d as unknown as Record<string, number>)[key]));

      const series: { key: "contentT" | "contentE" | "receiverT" | "receiverE"; color: string; dash?: string; label: string }[] = [
        { key: "contentT", color: "#5fa8d3", label: "T — content graph" },
        { key: "contentE", color: "#5fa8d3", dash: "4,3", label: "E — content graph" },
        { key: "receiverT", color: "#a78bfa", label: "T — receiver graph" },
        { key: "receiverE", color: "#a78bfa", dash: "4,3", label: "E — receiver graph" },
      ];

      for (const ser of series) {
        g.append("path")
          .datum(content.points)
          .attr("fill", "none")
          .attr("stroke", ser.color)
          .attr("stroke-width", 2)
          .attr("stroke-dasharray", ser.dash ?? "none")
          .attr("d", lineGen(ser.key) as unknown as string);
      }

      // current sweep marker
      g.append("line")
        .attr("x1", x(sweep))
        .attr("x2", x(sweep))
        .attr("y1", 0)
        .attr("y2", innerH)
        .attr("stroke", "#7f95a6")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "2,2");

      g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(6));
      g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));

      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH + 34)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("swept weight (lexical overlap / live-tie strength)");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerH / 2)
        .attr("y", -38)
        .attr("text-anchor", "middle")
        .attr("font-size", 11)
        .attr("fill", "#a9bccd")
        .attr("font-family", "Inter, sans-serif")
        .text("alignment σ(·, target)");

      // legend
      const legend = g.append("g").attr("transform", `translate(${innerW - 190}, 4)`);
      series.forEach((ser, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 16})`);
        row
          .append("line")
          .attr("x1", 0)
          .attr("x2", 18)
          .attr("y1", 0)
          .attr("y2", 0)
          .attr("stroke", ser.color)
          .attr("stroke-width", 2)
          .attr("stroke-dasharray", ser.dash ?? "none");
        row
          .append("text")
          .attr("x", 24)
          .attr("y", 3)
          .attr("font-size", 9.5)
          .attr("fill", "#a9bccd")
          .attr("font-family", "Inter, sans-serif")
          .text(ser.label);
      });
    },
    [content, sweep],
  );

  const contentWinner = content.current.T > content.current.E ? "T (general textbook passage)" : "E (specific explanation)";
  const meaningWinner = receiver.current.T > receiver.current.E ? "T (general textbook passage)" : "E (specific explanation)";
  const diverge = contentWinner !== meaningWinner;

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: the content-optimal and meaning-optimal claim can be different claims</div>
      <svg ref={ref} />
      <div className="control-panel">
        <Slider label="sweep weight" value={sweep} min={0.5} max={12.5} step={0.25} onChange={setSweep} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className={`pill ${diverge ? "pill-bad" : "pill-ok"}`}>
          content prefers {contentWinner.split(" ")[0]}
        </span>
        <span className={`pill ${diverge ? "pill-bad" : "pill-ok"}`}>
          meaning prefers {meaningWinner.split(" ")[0]}
        </span>
        {diverge && <span className="pill pill-bad">divergence at this weight</span>}
      </div>
      <p className="chart-caption">
        Solid lines are claim <span className="mono">T</span>; dashed are claim <span className="mono">E</span>. Blue is the
        content graph (lexical similarity to the query); purple is the researcher's own receiver graph. Across almost the
        entire sweep, the content graph ranks <span className="mono">T</span> above <span className="mono">E</span> while
        the receiver graph ranks them in the opposite order — the exact, constructed instance of Theorem 3.2.
      </p>
    </div>
  );
}
