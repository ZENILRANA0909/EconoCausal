import { useEffect, useState } from "react";
import { getThreatAssessment } from "../services/api";
import type { ThreatAssessment } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";

const LEVEL_COLOR: Record<string, string> = {
  LOW: "var(--color-low)",
  MEDIUM: "var(--color-medium)",
  HIGH: "var(--color-high)",
  CRITICAL: "var(--color-critical)",
};

export default function ThreatDetection() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [assessment, setAssessment] = useState<ThreatAssessment | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedFirmwareId) return;
    setLoading(true);
    getThreatAssessment(selectedFirmwareId)
      .then(setAssessment)
      .catch(() => setAssessment(null))
      .finally(() => setLoading(false));
  }, [selectedFirmwareId]);

  return (
    <div>
      <div className="page-header">
        <h1>Threat Detection</h1>
        <p>Explainable threat score derived from static findings and network behavior</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">No firmware selected. Go to Firmware Analysis first.</div>
        </div>
      ) : loading ? (
        <div className="panel">
          <div className="empty-state">Calculating threat assessment...</div>
        </div>
      ) : !assessment ? (
        <div className="panel">
          <div className="empty-state">No threat assessment available yet.</div>
        </div>
      ) : (
        <div className="panel">
          <div className="threat-indicator" style={{ color: LEVEL_COLOR[assessment.level] }}>
            <div className="threat-score-circle">
              <div className="threat-score-number">{assessment.score}</div>
              <div className="threat-score-max">/100</div>
            </div>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>
                {assessment.level} — {assessment.score}/100
              </div>
              <div style={{ color: "var(--color-text-secondary)", marginBottom: 4, fontSize: 13 }}>Reasons:</div>
              <ul className="threat-reasons">
                {assessment.reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
