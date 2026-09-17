import type { ReactNode } from "react";

interface SectionProps {
  id: string;
  eyebrow: string;
  title: string;
  lede?: ReactNode;
  children: ReactNode;
}

export function Section({ id, eyebrow, title, lede, children }: SectionProps) {
  return (
    <section id={id} className="section">
      <div className="page">
        <div className="section-eyebrow">{eyebrow}</div>
        <h2 className="section-title">{title}</h2>
        {lede && <p className="section-lede">{lede}</p>}
        {children}
      </div>
    </section>
  );
}
