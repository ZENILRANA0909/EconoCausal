import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFirmware, extractFirmware, analyzeFirmware } from "../services/api";
import type { Firmware } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";

export default function FirmwareUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFirmware, setUploadedFirmware] = useState<Firmware | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const { setSelectedFirmwareId } = useSelectedFirmware();
  const navigate = useNavigate();

  const handleFile = useCallback(async (file: File) => {
    setUploading(true);
    setError(null);
    setActionMessage(null);
    try {
      const response = await uploadFirmware(file);
      setUploadedFirmware(response.firmware);
      setSelectedFirmwareId(response.firmware.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [setSelectedFirmwareId]);

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      const file = event.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) handleFile(file);
  };

  const runAction = async (action: "analyze" | "extract" | "emulate") => {
    if (!uploadedFirmware) return;
    setActionMessage(`Running ${action}...`);
    try {
      if (action === "extract") {
        await extractFirmware(uploadedFirmware.id);
        setActionMessage("Extraction complete. View it in Filesystem Explorer.");
        navigate("/filesystem");
      } else if (action === "analyze") {
        await extractFirmware(uploadedFirmware.id);
        await analyzeFirmware(uploadedFirmware.id);
        setActionMessage("Analysis complete. View findings in Static Findings.");
        navigate("/findings");
      } else {
        navigate("/emulation");
      }
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : "Action failed");
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Firmware Upload</h1>
        <p>Upload an IoT firmware binary (.bin, .img, .fw) for analysis</p>
      </div>

      <div className="panel">
        <div
          className={`upload-dropzone${isDragging ? " dragging" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById("firmware-file-input")?.click()}
        >
          <input
            id="firmware-file-input"
            type="file"
            accept=".bin,.img,.fw"
            style={{ display: "none" }}
            onChange={onFileSelect}
          />
          <div style={{ fontSize: 32, marginBottom: 12 }}>⇧</div>
          <div>{uploading ? "Uploading..." : "Drag & drop firmware here, or click to select a file"}</div>
          <div style={{ fontSize: 12, marginTop: 8 }}>Accepted: .bin, .img, .fw — max 128MB</div>
        </div>
        {error && <p style={{ color: "var(--color-critical)", marginTop: 12 }}>{error}</p>}
      </div>

      {uploadedFirmware && (
        <div className="panel">
          <div className="panel-title">Uploaded Firmware</div>
          <div className="card-grid">
            <div>
              <span className="field-label">Firmware ID</span>
              <span className="field-value">{uploadedFirmware.id}</span>
            </div>
            <div>
              <span className="field-label">Filename</span>
              <span className="field-value">{uploadedFirmware.filename}</span>
            </div>
            <div>
              <span className="field-label">Size</span>
              <span className="field-value">{uploadedFirmware.file_size_bytes.toLocaleString()} bytes</span>
            </div>
            <div>
              <span className="field-label">Architecture</span>
              <span className="field-value">{uploadedFirmware.architecture}</span>
            </div>
            <div>
              <span className="field-label">SHA-256</span>
              <span className="field-value">{uploadedFirmware.sha256}</span>
            </div>
            <div>
              <span className="field-label">Status</span>
              <span className="field-value">{uploadedFirmware.extraction_status}</span>
            </div>
          </div>

          <div className="btn-row" style={{ marginTop: 16 }}>
            <button className="btn" onClick={() => runAction("analyze")}>Analyze</button>
            <button className="btn secondary" onClick={() => runAction("extract")}>Extract</button>
            <button className="btn secondary" onClick={() => runAction("emulate")}>Emulate</button>
          </div>
          {actionMessage && <p style={{ marginTop: 12, color: "var(--color-text-secondary)" }}>{actionMessage}</p>}
        </div>
      )}
    </div>
  );
}
