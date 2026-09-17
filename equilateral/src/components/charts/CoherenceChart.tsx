import { useMemo, useState } from "react";
import * as d3 from "d3";
import { useD3 } from "../ui/useD3";
import { robustnessDetail } from "../../lib/coherence";
import { Slider } from "../ui/Slider";

const WIDTH = 640;
const HEIGHT = 340;

const LAYOUTS: Record<number, { x: number; y: number }[]> = {
  1: [{ x: 320, y: 170 }],
  2: [
    { x: 240, y: 170 },
    { x: 400, y: 170 },
  ],
  3: [
    { x: 320, y: 90 },
    { x: 220, y: 250 },
    { x: 420, y: 250 },
  ],
  4: [
    { x: 320, y: 80 },
    { x: 460, y: 190 },
    { x: 320, y: 300 },
    { x: 180, y: 190 },
  ],
};

export function CoherenceChart() {
  const [size, setSize] = useState<2 | 3 | 4>(3);
  const [voteStrength, setVoteStrength] = useState(0.75);
  const [theta] = useState(0.5);
  const [removedIndex, setRemovedIndex] = useState<number | null>(null);

  const detail = useMemo(() => robustnessDetail(size, voteStrength, theta), [size, voteStrength, theta]);

  const activeIndices = useMemo(
    () => Array.from({ length: size }, (_, i) => i).filter((i) => i !== removedIndex),
    [size, removedIndex],
  );

  const stillGrounded = removedIndex === null ? detail.initiallyGrounded : detail.removals[removedIndex].stillGrounded;

  const ref = useD3(
    (svg) => {
      const s = d3.select(svg).attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`);
      const g = s.append("g");
      const positions = LAYOUTS[size];

      // edges: all pairs among active nodes, colored by whether support exceeds theta
      for (let i = 0; i < size; i++) {
        for (let j = i + 1; j < size; j++) {
          if (!activeIndices.includes(i) || !activeIndices.includes(j)) continue;
          const supports = voteStrength > theta;
          g.append("line")
            .attr("x1", positions[i].x)
            .attr("y1", positions[i].y)
            .attr("x2", positions[j].x)
            .attr("y2", positions[j].y)
            .attr("stroke", supports ? "#2dd4bf" : "#3a4d61")
            .attr("stroke-width", supports ? 2.4 : 1.4);
        }
      }

      positions.forEach((pos, i) => {
        const removed = i === removedIndex;
        const nodeG = g.append("g").attr("transform", `translate(${pos.x},${pos.y})`).attr("opacity", removed ? 0.25 : 1);
        nodeG
          .append("circle")
          .attr("r", 20)
          .attr("fill", removed ? "#26374a" : "#5fa8d3")
          .attr("stroke", "#3a4d61")
          .attr("stroke-width", 1.5)
          .style("cursor", "pointer")
          .on("click", () => setRemovedIndex(removed ? null : i));
        nodeG
          .append("text")
          .attr("text-anchor", "middle")
          .attr("dy", 4)
          .attr("font-size", 11)
          .attr("font-family", "JetBrains Mono, monospace")
          .attr("fill", removed ? "#7f95a6" : "#ffffff")
          .style("pointer-events", "none")
          .text(`c${i + 1}`);
      });
    },
    [size, voteStrength, removedIndex, activeIndices],
  );

  return (
    <div className="chart-card">
      <div className="chart-title">Live simulation: click a node to test removal-robustness</div>
      <svg ref={ref} />
      <div className="control-panel">
        <div className="control-row">
          <label>coalition size</label>
          {[2, 3, 4].map((n) => (
            <button
              key={n}
              className={`btn ${size === n ? "btn-primary" : ""}`}
              style={{ marginRight: "0.4rem" }}
              onClick={() => {
                setSize(n as 2 | 3 | 4);
                setRemovedIndex(null);
              }}
            >
              {n}
            </button>
          ))}
        </div>
        <Slider label="vote strength" value={voteStrength} min={0.1} max={0.99} step={0.01} onChange={setVoteStrength} />
      </div>
      <div className="stat-row" style={{ marginTop: "0.8rem" }}>
        <span className={`pill ${detail.initiallyGrounded ? "pill-ok" : "pill-bad"}`}>
          {detail.initiallyGrounded ? "grounded" : "not grounded"} (full coalition)
        </span>
        {removedIndex !== null && (
          <span className={`pill ${stillGrounded ? "pill-ok" : "pill-bad"}`}>
            {stillGrounded ? "still grounded" : "collapses"} after removing c{removedIndex + 1}
          </span>
        )}
        <span className={`pill ${detail.robust ? "pill-ok" : "pill-bad"}`}>
          {detail.robust ? "robust to any single removal" : "not robust"}
        </span>
      </div>
      <p className="chart-caption">
        A coalition is grounded at threshold θ={theta} if every member is supported by at least one other member above
        θ. Click any node to remove it and watch whether the remaining coalition stays grounded. At strong votes, size 2
        always collapses on removal; size 3 and 4 do not — the sharp transition Theorem 8.8 proves is structural, not
        gradual.
      </p>
    </div>
  );
}
