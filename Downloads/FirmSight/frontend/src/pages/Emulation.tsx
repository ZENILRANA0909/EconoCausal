import { useEffect, useState } from "react";
import { startEmulation, stopEmulation, getEmulationStatus } from "../services/api";
import type { EmulationSession } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";
import DemoBanner from "../components/DemoBanner";

export default function Emulation() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [session, setSession] = useState<EmulationSession | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    if (!selectedFirmwareId) return;
    getEmulationStatus(selectedFirmwareId)
      .then(setSession)
      .catch(() => undefined);
  };

  useEffect(() => {
    refresh();
  }, [selectedFirmwareId]);

  const handleStart = async () => {
    if (!selectedFirmwareId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await startEmulation(selectedFirmwareId, false);
      setSession(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start emulation");
    } finally {
      setBusy(false);
    }
  };

  const handleStop = async () => {
    if (!selectedFirmwareId) return;
    setBusy(true);
    try {
      const result = await stopEmulation(selectedFirmwareId);
      setSession(result);
    } finally {
      setBusy(false);
    }
  };

  const runtimeSeconds = session?.started_at
    ? Math.max(
        0,
        Math.round(
          ((session.stopped_at ? new Date(session.stopped_at) : new Date()).getTime() -
            new Date(session.started_at).getTime()) /
            1000
        )
      )
    : 0;

  return (
    <div>
      <div className="page-header">
        <h1>Emulation</h1>
        <p>Start QEMU-based emulation where supported, or run in safe demo mode</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">No firmware selected. Go to Firmware Analysis first.</div>
        </div>
      ) : (
        <>
          <DemoBanner visible={!!session?.is_demo} />

          <div className="panel">
            <div className="panel-title">Emulation Control</div>
            <div className="card-grid">
              <div>
                <span className="field-label">Mode</span>
                <span className="field-value">{session?.mode ?? "not started"}</span>
              </div>
              <div>
                <span className="field-label">QEMU Binary</span>
                <span className="field-value">{session?.qemu_binary || "n/a"}</span>
              </div>
              <div>
                <span className="field-label">Status</span>
                <span className="field-value">{session?.status ?? "stopped"}</span>
              </div>
              <div>
                <span className="field-label">Process ID</span>
                <span className="field-value">{session?.process_id || "n/a"}</span>
              </div>
              <div>
                <span className="field-label">Runtime</span>
                <span className="field-value">{runtimeSeconds}s</span>
              </div>
            </div>

            <div className="btn-row" style={{ marginTop: 16 }}>
              <button className="btn" disabled={busy || session?.status === "running"} onClick={handleStart}>
                Start Emulation
              </button>
              <button className="btn danger" disabled={busy || session?.status !== "running"} onClick={handleStop}>
                Stop Emulation
              </button>
            </div>
            {error && <p style={{ color: "var(--color-critical)", marginTop: 12 }}>{error}</p>}
          </div>

          <div className="panel">
            <div className="panel-title">Terminal Output</div>
            <div className="terminal">{session?.output_log || "No output yet. Start emulation to see logs."}</div>
          </div>
        </>
      )}
    </div>
  );
}
