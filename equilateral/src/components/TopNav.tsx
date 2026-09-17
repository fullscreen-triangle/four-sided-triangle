const LINKS = [
  { href: "#floor", label: "Floor" },
  { href: "#content-meaning", label: "Content/Meaning" },
  { href: "#receiver", label: "Receiver-Relativity" },
  { href: "#table", label: "Propagation Table" },
  { href: "#catalysis", label: "Catalysis" },
  { href: "#coherence", label: "Coherence" },
  { href: "#closure", label: "Closure" },
  { href: "#route-audit", label: "Route-Audit" },
  { href: "#architecture", label: "Architecture" },
  { href: "#deployment", label: "Deployment" },
  { href: "#validation", label: "Validation" },
];

export function TopNav() {
  return (
    <nav className="topnav">
      <div className="topnav-inner">
        <a className="brand" href="#top">
          <svg className="brand-mark" viewBox="0 0 24 24" fill="none">
            <path d="M12 2 L22 20 L2 20 Z" stroke="#5fa8d3" strokeWidth="2" strokeLinejoin="round" />
            <path d="M12 2 L12 20 M2 20 L22 20 M12 2 L2 20 M12 2 L22 20" stroke="#2dd4bf" strokeWidth="1" opacity="0.5" />
          </svg>
          equilateral
        </a>
        <div className="navlinks">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href}>
              {l.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
