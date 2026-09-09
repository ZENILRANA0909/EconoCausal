import { useEffect, useState } from "react";
import { listFirmware, getActivity } from "../services/api";
import type { FirmwareListItem, ActivityItem } from "../types";
import StatCard from "../components/StatCard";
import SeverityBadge from "../components/SeverityBadge";

export default function Dashboard() {
  const [firmwareList, setFirmwareList] = useState<FirmwareListItem[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listFirmware(), getActivity()])
      .then(([firmwareData, activityData]) => {
        setFirmwareList(firmwareData);
        setActivity(activityData);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  const totalFirmware = firmwareList.length;
  const analysesCompleted = firmwareList.filter((item) => item.analysis_status === "completed").length;
  const activeEmulations = activity.filter(
    (item) => item.event_type === "emulation" && item.message.includes("started")
  ).length;
  const threatsDetected = activity.filter((item) => item.event_type === "threat_detection").length;
  const criticalFindings = activity.filter(
    (item) => item.event_type === "threat_detection" && item.message.includes("CRITICAL")
  ).length;

  return (
    <div>
      <div className="page-header">
        <h1>FIRMSIGHT</h1>
        <p>IoT Firmware Emulation &amp; Dynamic Analysis Sandbox</p>
      </div>

      <div className="card-grid">
        <StatCard label="Total Firmware" value={totalFirmware} />
        <StatCard label="Analyses Completed" value={analysesCompleted} />
        <StatCard label="Active Emulations" value={activeEmulations} />
        <StatCard label="Threats Detected" value={threatsDetected} />
        <StatCard label="Critical Findings" value={criticalFindings} />
      </div>

      <div className="panel">
        <div className="panel-title">Recent Firmware</div>
        {loading ? (
          <div className="empty-state">Loading...</div>
        ) : firmwareList.length === 0 ? (
          <div className="empty-state">No firmware uploaded yet. Go to Firmware Upload to get started.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Architecture</th>
                <th>Extraction</th>
                <th>Analysis</th>
                <th>Mode</th>
              </tr>
            </thead>
            <tbody>
              {firmwareList.slice(0, 8).map((item) => (
                <tr key={item.id}>
                  <td>{item.filename}</td>
                  <td>{item.architecture}</td>
                  <td>{item.extraction_status}</td>
                  <td>{item.analysis_status}</td>
                  <td>{item.is_demo ? <span className="badge demo">DEMO</span> : "Real"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="panel">
        <div className="panel-title">Activity Timeline</div>
        {activity.length === 0 ? (
          <div className="empty-state">No activity yet.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Event</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {activity.slice(0, 10).map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleTimeString()}</td>
                  <td>{item.event_type}</td>
                  <td>{item.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
