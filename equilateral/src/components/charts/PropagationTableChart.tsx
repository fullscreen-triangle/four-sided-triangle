import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { newGraph, addClaim, addContact, minCut, MEDIUM } from "../../lib/graph";

const WIDTH = 640;
const HEIGHT = 400;

function buildDemoGraph() {
  const g = newGraph();
  addClaim(g, "v0", 3.0);
  addClaim(g, "h1", 2.0);
  addClaim(g, "h2", 2.0);
  addClaim(g, "h3", 2.5);
  addClaim(g, "xstar", 1.5);
  addContact(g, "v0", "h1", 4.0);
  addContact(g, "h1", "h2", 3.5);
  addContact(g, "h2", "xstar", 4.5);
  addContact(g, "v0", "h3", 1.0);
  addContact(g, "h3", "xstar", 1.0);
  return g;
}

interface NodePos {
  id: string;
  x: number;
  y: number;
  fixed?: boolean;
}

const LAYOUT: NodePos[] = [
  { id: MEDIUM, x: 320, y: 40, fixed: true },
  { id: "v0", x: 90, y: 220, fixed: true },
  { id: "h1", x: 220, y: 140, fixed: true },
  { id: "h2", x: 340, y: 200, fixed: true },
  { id: "h3", x: 200, y: 320, fixed: true },
  { id: "xstar", x: 500, y: 260, fixed: true },
];

export function PropagationTableChart() {
  const [mode, setMode] = useState<"rest" | "process">("process");

  const graph = useMemo(() => buildDemoGraph(), []);

  const { cutEdges, pathEdges, cutValue } = useMemo(() => {
    if (mode === "rest") {
      const { value, sourceSide } = minCut(graph, "xstar", MEDIUM);
      const edges: [string, string][] = [];
      for (const [u, nbrs] of graph.adj) {
        for (const [v] of nbrs) {
          if (u < v) {
            const uIn = sourceSide.has(u);
            const vIn = sourceSide.has(v);
            if (uIn !== vIn) edges.push([u, v]);
          }
        }
      }
      return { cutEdges: edges, pathEdges: [] as [string, string][], cutValue: value };
    } else {
      // nontrivial propagation: walk v0 -> h1 -> h2 -> xstar (skipping h3)
      const path: [string, string][] = [
        ["v0", "h1"],
        ["h1", "h2"],
        ["h2", "xstar"],
      ];
      const { value } = minCut(graph, "xstar", MEDIUM);
      return { cutEdges: [] as [string, string][], pathEdges: path, cutValue: value };
    }
  }, [graph, mode]);

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const g = s.append("g");

      const posById = new Map(LAYOUT.map((n) => [n.id, n]));

      // edges
      const edgeList: { u: string; v: string; w: number }[] = [];
      const seen = new Set<string>();
      for (const [u, nbrs] of graph.adj) {
        for (const [v, w] of nbrs) {
          const key = [u, v].sort().join("|");
          if (!seen.has(key)) {
            seen.add(key);
            edgeList.push({ u, v, w });
          }
        }
      }

      const isCut = (u: string, v: string) =>
        cutEdges.some(([a, b]) => (a === u && b === v) || (a === v && b === u));
      const isPath = (u: string, v: string) =>
        pathEdges.some(([a, b]) => (a === u && b === v) || (a === v && b === u));

      g.selectAll("line.edge")
        .data(edgeList)
        .join("line")
        .attr("class", "edge")
        .attr("x1", (d) => posById.get(d.u)!.x)
        .attr("y1", (d) => posById.get(d.u)!.y)
        .attr("x2", (d) => posById.get(d.v)!.x)
        .attr("y2", (d) => posById.get(d.v)!.y)
        .attr("stroke", (d) => (isCut(d.u, d.v) ? "#e08b90" : isPath(d.u, d.v) ? "#2dd4bf" : "#3a4d61"))
        .attr("stroke-width", (d) => (isCut(d.u, d.v) || isPath(d.u, d.v) ? 3 : 1.4))
        .attr("stroke-dasharray", (d) => (isCut(d.u, d.v) ? "6,3" : "none"));

      g.selectAll("text.weight")
        .data(edgeList)
        .join("text")
        .attr("class", "weight")
        .attr("x", (d) => (posById.get(d.u)!.x + posById.get(d.v)!.x) / 2)
        .attr("y", (d) => (posById.get(d.u)!.y + posById.get(d.v)!.y) / 2 - 4)
        .attr("text-anchor", "middle")
        .attr("font-size", 9)
        .attr("font-family", "JetBrains Mono, monospace")
        .attr("fill", "#7f95a6")
        .text((d) => d.w.toFixed(1));

      // nodes
      const nodeSel = g
        .selectAll("g.node")
        .data(LAYOUT)
        .join("g")
        .attr("class", "node")
        .attr("transform", (d) => `translate(${d.x},${d.y})`);

      nodeSel
        .append("circle")
        .attr("r", (d) => (d.id === MEDIUM ? 22 : d.id === "xstar" ? 18 : 14))
        .attr("fill", (d) =>
          d.id === MEDIUM ? "#e8eef4" : d.id === "xstar" ? "#2dd4bf" : d.id === "v0" ? "#5fa8d3" : "#17222e",
        )
        .attr("stroke", "#3a4d61")
        .attr("stroke-width", 1.5);

      nodeSel
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dy", (d) => (d.id === MEDIUM || d.id === "xstar" || d.id === "v0" ? 4 : 4))
        .attr("font-size", 10.5)
        .attr("font-family", "JetBrains Mono, monospace")
        .attr("font-weight", 600)
        .attr("fill", (d) => (d.id === MEDIUM || d.id === "xstar" || d.id === "v0" ? "#0e1620" : "#e8eef4"))
        .text((d) => (d.id === MEDIUM ? "m" : d.id === "xstar" ? "x*" : d.id));
    },
    [graph, cutEdges, pathEdges],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: one table, two settings of the process argument</div>
      <svg ref={ref} />
      <div className="control-panel" style={{ display: "flex", gap: "0.6rem" }}>
        <button className={`btn ${mode === "rest" ? "btn-primary" : ""}`} onClick={() => setMode("rest")}>
          Π_rest (catalogue)
        </button>
        <button className={`btn ${mode === "process" ? "btn-primary" : ""}`} onClick={() => setMode("process")}>
          nontrivial Π (generation)
        </button>
      </div>
      <p className="chart-caption">
        {mode === "rest" ? (
          <>
            <span className="mono">Π_rest(x*)</span>: the table evaluated at the trivial process returns <span className="mono">x*</span>'s
            resting cut against the medium (dashed red) — exactly what a static knowledge-graph catalogue stores. Cut
            value <span className="mono">{cutValue.toFixed(2)}</span>.
          </>
        ) : (
          <>
            A nontrivial propagation (teal path <span className="mono">v0 → h1 → h2 → x*</span>) reaches the same target;
            by Theorem 5.2 its terminus is an accountable cut of the <em>same type</em> as the catalogue cell, computed
            under process rather than at rest. Note the walk skips <span className="mono">h3</span> entirely — by
            path-opacity, interior claims are unconstrained provided the walk converges.
          </>
        )}
      </p>
    </div>
  );
}
