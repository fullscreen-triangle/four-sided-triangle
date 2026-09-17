const ITEMS = [
  { num: "§1", href: "#floor", label: "The Resolution Floor", desc: "Why every retrieval costs something strictly positive." },
  { num: "§2", href: "#content-meaning", label: "Content vs. Meaning", desc: "The provable rank-flip behind 'true but useless.'" },
  { num: "§3", href: "#receiver", label: "Receiver-Relativity", desc: "Recognition and search as one relation, two readings." },
  { num: "§4", href: "#table", label: "The Propagation Table", desc: "Lookup and generation are one object, two settings." },
  { num: "§5", href: "#catalysis", label: "Catalytic Composition", desc: "The multiplicative law; diversify, don't repeat." },
  { num: "§6", href: "#coherence", label: "Coherence Triangle", desc: "Grounding requires three sources, never one or two." },
  { num: "§7", href: "#closure", label: "Closure vs. Threshold", desc: "The correct, stricter stopping rule for a search." },
  { num: "§8", href: "#route-audit", label: "Route-Audit", desc: "Catching false friends between opaque sources." },
  { num: "§9", href: "#architecture", label: "Society of Agents", desc: "Federation, water-filling, and monotone history." },
  { num: "§10", href: "#deployment", label: "Deployment", desc: "A concrete instantiation for a research group." },
  { num: "§11", href: "#validation", label: "Validation", desc: "Every prediction checked, and held." },
];

export function TableOfContents() {
  return (
    <div id="toc" className="section" style={{ borderTop: "1px solid var(--rule)" }}>
      <div className="page">
        <div className="section-eyebrow">Contents</div>
        <h2 className="section-title">Eleven ideas, each with a chart you can operate</h2>
        <div className="toc">
          {ITEMS.map((item) => (
            <a className="toc-item" href={item.href} key={item.href}>
              <div className="toc-num">{item.num}</div>
              <div className="toc-label">{item.label}</div>
              <div className="toc-desc">{item.desc}</div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
