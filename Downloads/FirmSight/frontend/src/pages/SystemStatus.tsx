import { useEffect, useState } from "react";
import { getToolStatus, getSystemInfo } from "../services/api";
import type { ToolStatus, SystemInfo } from "../types";

export default function SystemStatus() {
  const [tools, setTools] = useState<ToolStatus[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getToolStatus(), getSystemInfo()])
      .then(([toolData, infoData]) => {
        setTools(toolData);
        setSystemInfo(infoData);
      })
      .finally(() => setLoading(false));
  }, []);

  const coreTools = tools.filter((tool) => !tool.name.startsWith("qemu"));
  const qemuTools = tools.filter((tool) => tool.name.startsWith("qemu"));

  return (
    <div>
      <div className="page-header">
        <h1>System / Tool Status</h1>
        <p>Checks whether required native tools are installed on this machine</p>
      </div>

      {loading ? (
        <div className="panel"><div className="empty-state">Checking system...</div></div>
      ) : (
        <>
          {systemInfo && (
            <div className="panel">
              <div className="panel-title">Platform</div>
              <div className="card-grid">
                <div><span className="field-label">OS</span><span className="field-value">{systemInfo.system} {systemInfo.release}</span></div>
                <div><span className="field-label">Architecture</span><span className="field-value">{systemInfo.machine}</span></div>
                <div><span className="field-label">Python</span><span className="field-value">{systemInfo.python_version}</span></div>
                <div><span className="field-label">Demo Mode Recommended</span><span className="field-value">{systemInfo.demo_mode_recommended ? "Yes" : "No"}</span></div>
              </div>
            </div>
          )}

          <div className="panel">
            <div className="panel-title">Core Tools</div>
            <table>
              <thead>
                <tr><th>Tool</th><th>Status</th><th>Path</th><th>Install Hint</th></tr>
              </thead>
              <tbody>
                {coreTools.map((tool) => (
                  <tr key={tool.name}>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{tool.name}</td>
                    <td>
                      <span className={`badge ${tool.available ? "available" : "unavailable"}`}>
                        {tool.available ? "✓ Available" : "✗ Not Installed"}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{tool.path || "—"}</td>
                    <td style={{ fontSize: 12 }}>{tool.install_hint}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="panel">
            <div className="panel-title">QEMU Binaries</div>
            <table>
              <thead>
                <tr><th>Binary</th><th>Status</th><th>Path</th><th>Install Hint</th></tr>
              </thead>
              <tbody>
                {qemuTools.map((tool) => (
                  <tr key={tool.name}>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{tool.name}</td>
                    <td>
                      <span className={`badge ${tool.available ? "available" : "unavailable"}`}>
                        {tool.available ? "✓ Available" : "✗ Not Installed"}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{tool.path || "—"}</td>
                    <td style={{ fontSize: 12 }}>{tool.install_hint}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
