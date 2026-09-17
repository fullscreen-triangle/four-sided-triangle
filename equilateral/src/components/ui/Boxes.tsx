import type { ReactNode } from "react";

interface BoxProps {
  label: string;
  title?: string;
  children: ReactNode;
}

export function TheoremBox({ label, title, children }: BoxProps) {
  return (
    <div className="box box-theorem">
      <div className="box-label">
        {label}
        {title ? ` — ${title}` : ""}
      </div>
      {children}
    </div>
  );
}

export function DefinitionBox({ label, title, children }: BoxProps) {
  return (
    <div className="box box-definition">
      <div className="box-label">
        {label}
        {title ? ` — ${title}` : ""}
      </div>
      {children}
    </div>
  );
}

export function RemarkBox({ label, title, children }: BoxProps) {
  return (
    <div className="box box-remark">
      <div className="box-label">
        {label}
        {title ? ` — ${title}` : ""}
      </div>
      {children}
    </div>
  );
}

export function Formula({ children }: { children: ReactNode }) {
  return <span className="formula">{children}</span>;
}

export function FormulaBlock({ children }: { children: ReactNode }) {
  return <div className="formula-block">{children}</div>;
}
