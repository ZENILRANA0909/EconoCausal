import type { Severity } from "../types";

interface SeverityBadgeProps {
  severity: Severity;
}

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  return <span className={`badge ${severity}`}>{severity}</span>;
}
