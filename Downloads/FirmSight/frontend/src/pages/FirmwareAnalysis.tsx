import { useEffect, useState } from "react";
import { listFirmware, extractFirmware, analyzeFirmware } from "../services/api";
import type { FirmwareListItem } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";

export default function FirmwareAnalysis() {
  const [firmwareList, setFirmwareList] = useState<FirmwareListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const { selectedFirmwareId, setSelectedFirmwareId } = useSelectedFirmware();

  const refresh = () => {
    setLoading(true);
    listFirmware()
      .then(setFirmwareList)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
  }, []);

  const runFullAnalysis = async (id: string) => {
    setBusyId(id);
    try {
      await extractFirmware(id);
      await analyzeFirmware(id);
      refresh();
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Firmware Analysis</h1>
        <p>Select firmware to run extraction and static security analysis</p>
      </div>

      <div className="panel">
        {loading ? (
          <div className="empty-state">Loading...</div>
        ) : firmwareList.length === 0 ? (
          <div className="empty-state">No firmware available. Upload firmware first.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Size</th>
                <th>Architecture</th>
                <th>Extraction</th>
                <th>Analysis</th>
                <th>Mode</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {firmwareList.map((item) => (
                <tr
                  key={item.id}
                  style={{
                    background: selectedFirmwareId === item.id ? "rgba(0,212,255,0.05)" : undefined,
                  }}
                >
                  <td>{item.filename}</td>
                  <td>{item.file_size_bytes.toLocaleString()} B</td>
                  <td>{item.architecture}</td>
                  <td>{item.extraction_status}</td>
                  <td>{item.analysis_status}</td>
                  <td>{item.is_demo ? <span className="badge demo">DEMO</span> : "Real"}</td>
                  <td>
                    <div className="btn-row">
                      <button
                        className="btn secondary"
                        onClick={() => setSelectedFirmwareId(item.id)}
                      >
                        Select
                      </button>
                      <button
                        className="btn"
                        disabled={busyId === item.id}
                        onClick={() => runFullAnalysis(item.id)}
                      >
                        {busyId === item.id ? "Running..." : "Run Analysis"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
