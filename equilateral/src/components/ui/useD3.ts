import { useEffect, useRef } from "react";
import * as d3 from "d3";

/**
 * Standard pattern: React owns the <svg> element via ref; D3 owns
 * everything drawn inside it. The render function receives the raw SVG
 * node and is re-run whenever any dependency changes.
 */
export function useD3(
  renderFn: (svg: SVGSVGElement) => void,
  dependencies: React.DependencyList,
) {
  const ref = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    d3.select(ref.current).selectAll("*").remove();
    renderFn(ref.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return ref;
}
