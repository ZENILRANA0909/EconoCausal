import { useEffect, useState } from "react";
import { getNetworkEvents } from "../services/api";
import type { NetworkEvent } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";
import DemoBanner from "../components/DemoBanner";

function riskBadgeFor(event: NetworkEvent): "LOW" | "MEDIUM" | "HIGH" {
  if (event.destination_port === 23 || event.destination_port === 4444) return "HIGH";
  if (event.destination_port === 21) return "MEDIUM";
  return "LOW";
}

export default function NetworkMonitor() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [events, setEvents] = useState<NetworkEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedFirmwareId) return;
    setLoading(true);
    getNetworkEvents(selectedFirmwareId)
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [selectedFirmwareId]);

  const isSimulated = events.some((event) => event.is_simulated);

  return (
    <div>
      <div className="page-header">
        <h1>Network Monitor</h1>
        <p>Network activity observed from the emulated environment</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">No firmware selected. Go to Firmware Analysis first.</div>
        </div>
      ) : (
        <>
          <DemoBanner visible={isSimulated} />
          <div className="panel">
            <div className="panel-title">Captured Events ({events.length})</div>
            {loading ? (
              <div className="empty-state">Loading network events...</div>
            ) : events.length === 0 ? (
              <div className="empty-state">No network events captured yet.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Source</th>
                    <th>Destination</th>
                    <th>Protocol</th>
                    <th>Port</th>
                    <th>DNS / HTTP</th>
                    <th>Threat</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((event) => (
                    <tr key={event.id}>
                      <td>{new Date(event.captured_at).toLocaleTimeString()}</td>
                      <td style={{ fontFamily: "var(--font-mono)" }}>{event.source_ip}:{event.source_port}</td>
                      <td style={{ fontFamily: "var(--font-mono)" }}>{event.destination_ip}:{event.destination_port}</td>
                      <td>{event.protocol}</td>
                      <td>{event.destination_port}</td>
                      <td>{event.dns_query || event.http_destination || "—"}</td>
                      <td><span className={`badge ${riskBadgeFor(event)}`}>{riskBadgeFor(event)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
