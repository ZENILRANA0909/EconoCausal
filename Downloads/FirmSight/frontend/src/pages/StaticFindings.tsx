import { useEffect, useMemo, useState } from "react";
import { getFindings } from "../services/api";
import type { StaticFinding, Severity } from "../types";
import SeverityBadge from "../components/SeverityBadge";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";

const SEVERITY_LEVELS: Severity[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function StaticFindings() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [findings, setFindings] = useState<StaticFinding[]>([]);
  const [activeFilter, setActiveFilter] = useState<Severity | "ALL">("ALL");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedFirmwareId) return;
    setLoading(true);
    getFindings(selectedFirmwareId)
      .then(setFindings)
      .catch(() => setFindings([]))
      .finally(() => setLoading(false));
  }, [selectedFirmwareId]);

  const filteredFindings = useMemo(
    () => (activeFilter === "ALL" ? findings : findings.filter((item) => item.severity === activeFilter)),
    [findings, activeFilter]
  );

  return (
    <div>
      <div className="page-header">
        <h1>Static Findings</h1>
        <p>Security-relevant strings and patterns identified in the firmware filesystem</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">No firmware selected. Go to Firmware Analysis first.</div>
        </div>
      ) : (
        <div className="panel">
          <div className="filter-row">
            <button
              className={`filter-chip${activeFilter === "ALL" ? " active" : ""}`}
              onClick={() => setActiveFilter("ALL")}
            >
              ALL ({findings.length})
            </button>
            {SEVERITY_LEVELS.map((level) => (
              <button
                key={level}
                className={`filter-chip${activeFilter === level ? " active" : ""}`}
                onClick={() => setActiveFilter(level)}
              >
                {level} ({findings.filter((item) => item.severity === level).length})
              </button>
            ))}
          </div>

          {loading ? (
            <div className="empty-state">Loading findings...</div>
          ) : filteredFindings.length === 0 ? (
            <div className="empty-state">No findings match this filter. Run analysis if none exist yet.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Category</th>
                  <th>File</th>
                  <th>Finding</th>
                  <th>Evidence</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {filteredFindings.map((item) => (
                  <tr key={item.id}>
                    <td><SeverityBadge severity={item.severity} /></td>
                    <td>{item.category}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{item.file_path}</td>
                    <td>{item.finding}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis" }}>
                      {item.evidence}
                    </td>
                    <td>{item.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
