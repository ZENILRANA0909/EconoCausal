export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Firmware {
  id: string;
  filename: string;
  file_size_bytes: number;
  sha256: string;
  architecture: string;
  endianness: string;
  binary_type: string;
  is_demo: boolean;
  extraction_status: string;
  analysis_status: string;
  uploaded_at: string;
}

export interface FirmwareListItem {
  id: string;
  filename: string;
  file_size_bytes: number;
  architecture: string;
  extraction_status: string;
  analysis_status: string;
  is_demo: boolean;
  uploaded_at: string;
}

export interface ExtractionResult {
  id: string;
  firmware_id: string;
  status: string;
  extracted_path: string;
  file_count: number;
  directory_count: number;
  filesystem_type: string;
  method: string;
  created_at: string;
}

export interface StaticFinding {
  id: string;
  firmware_id: string;
  severity: Severity;
  category: string;
  file_path: string;
  finding: string;
  evidence: string;
  recommendation: string;
  created_at: string;
}

export interface FileTreeNode {
  name: string;
  path: string;
  is_directory: boolean;
  size_bytes: number;
  children: FileTreeNode[];
}

export interface NetworkEvent {
  id: string;
  firmware_id: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  is_dns: boolean;
  dns_query: string;
  http_destination: string;
  is_simulated: boolean;
  captured_at: string;
}

export interface EmulationSession {
  id: string;
  firmware_id: string;
  mode: string;
  qemu_binary: string;
  status: string;
  process_id: number;
  is_demo: boolean;
  started_at: string;
  stopped_at: string | null;
  output_log: string;
}

export interface ThreatAssessment {
  firmware_id: string;
  score: number;
  level: Severity;
  reasons: string[];
  created_at: string;
}

export interface SecurityReport {
  firmware_id: string;
  filename: string;
  sha256: string;
  file_size_bytes: number;
  architecture: string;
  filesystem_type: string;
  extraction_status: string;
  file_count: number;
  static_findings_count: number;
  network_events_count: number;
  threat_score: number;
  threat_level: Severity;
  threat_reasons: string[];
  recommendations: string[];
  is_demo: boolean;
  generated_at: string;
}

export interface ToolStatus {
  name: string;
  available: boolean;
  path: string;
  install_hint: string;
}

export interface SystemInfo {
  system: string;
  release: string;
  machine: string;
  python_version: string;
  demo_mode_recommended: boolean;
}

export interface ActivityItem {
  id: string;
  event_type: string;
  message: string;
  firmware_id: string;
  created_at: string;
}
