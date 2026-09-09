import { useEffect, useState } from "react";
import { getReport } from "../services/api";
import type { SecurityReport } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";
import SeverityBadge from "../components/SeverityBadge";
import DemoBanner from "../components/DemoBanner";

export default function SecurityReportPage() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [report, setReport] = useState<SecurityReport | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedFirmwareId) return;
    setLoading(true);
    getReport(selectedFirmwareId)
      .then(setReport)
      .catch(() => setReport(null))
      .finally(() => setLoading(false));
  }, [selectedFirmwareId]);

  const downloadJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `firmsight-report-${report.firmware_id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header">
        <h1>Security Report</h1>
        <p>Consolidated security analysis summary for this firmware</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">No firmware selected. Go to Firmware Analysis first.</div>
        </div>
      ) : loading ? (
        <div className="panel">
          <div className="empty-state">Generating report...</div>
        </div>
      ) : !report ? (
        <div className="panel">
          <div className="empty-state">No report available yet.</div>
        </div>
      ) : (
        <>
          <DemoBanner visible={report.is_demo} />
          <div className="panel">
            <div className="panel-title">
              <span>Report Summary</span>
              <button className="btn secondary" onClick={downloadJson}>Export JSON</button>
            </div>
            <div className="card-grid">
              <div><span className="field-label">Firmware</span><span className="field-value">{report.filename}</span></div>
              <div><span className="field-label">SHA-256</span><span className="field-value">{report.sha256}</span></div>
              <div><span className="field-label">Size</span><span className="field-value">{report.file_size_bytes.toLocaleString()} B</span></div>
              <div><span className="field-label">Architecture</span><span className="field-value">{report.architecture}</span></div>
              <div><span className="field-label">Filesystem</span><span className="field-value">{report.filesystem_type}</span></div>
              <div><span className="field-label">Extraction</span><span className="field-value">{report.extraction_status}</span></div>
              <div><span className="field-label">File Count</span><span className="field-value">{report.file_count}</span></div>
              <div><span className="field-label">Static Findings</span><span className="field-value">{report.static_findings_count}</span></div>
              <div><span className="field-label">Network Events</span><span className="field-value">{report.network_events_count}</span></div>
              <div><span className="field-label">Generated</span><span className="field-value">{new Date(report.generated_at).toLocaleString()}</span></div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">Threat Level</div>
            <div style={{ marginBottom: 12 }}>
              <SeverityBadge severity={report.threat_level} /> <strong>{report.threat_score}/100</strong>
            </div>
            <ul className="threat-reasons">
              {report.threat_reasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>

          <div className="panel">
            <div className="panel-title">Recommendations</div>
            <ul className="threat-reasons">
              {report.recommendations.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
