import type {
  Firmware,
  FirmwareListItem,
  ExtractionResult,
  StaticFinding,
  FileTreeNode,
  NetworkEvent,
  EmulationSession,
  ThreatAssessment,
  SecurityReport,
  ToolStatus,
  SystemInfo,
  ActivityItem,
} from "../types";

const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: options?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<{ status: string; app_name: string; version: string; timestamp: string }>("/health");
}

export function getSystemInfo() {
  return request<SystemInfo>("/system-info");
}

export function getToolStatus() {
  return request<ToolStatus[]>("/tools");
}

export function getActivity() {
  return request<ActivityItem[]>("/activity");
}

export function listFirmware() {
  return request<FirmwareListItem[]>("/firmware");
}

export function getFirmware(id: string) {
  return request<Firmware>(`/firmware/${id}`);
}

export async function uploadFirmware(file: File): Promise<{ firmware: Firmware; message: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/firmware/upload`, { method: "POST", body: formData });
}

export function extractFirmware(id: string) {
  return request<ExtractionResult>(`/firmware/${id}/extract`, { method: "POST" });
}

export function analyzeFirmware(id: string, forceDemo = false) {
  return request<{
    firmware_id: string;
    architecture: string;
    endianness: string;
    binary_type: string;
    findings_count: number;
    is_demo: boolean;
    message: string;
  }>(`/firmware/${id}/analyze`, {
    method: "POST",
    body: JSON.stringify({ force_demo: forceDemo }),
  });
}

export function getFileTree(id: string) {
  return request<FileTreeNode>(`/firmware/${id}/files`);
}

export function getFindings(id: string) {
  return request<StaticFinding[]>(`/firmware/${id}/findings`);
}

export function getNetworkEvents(id: string) {
  return request<NetworkEvent[]>(`/firmware/${id}/network`);
}

export function startEmulation(id: string, forceDemo = false) {
  return request<EmulationSession>(`/firmware/${id}/emulate`, {
    method: "POST",
    body: JSON.stringify({ force_demo: forceDemo }),
  });
}

export function stopEmulation(id: string) {
  return request<EmulationSession>(`/firmware/${id}/stop`, { method: "POST" });
}

export function getEmulationStatus(id: string) {
  return request<EmulationSession>(`/firmware/${id}/emulation-status`);
}

export function getThreatAssessment(id: string) {
  return request<ThreatAssessment>(`/firmware/${id}/threats`);
}

export function getReport(id: string) {
  return request<SecurityReport>(`/firmware/${id}/report`);
}
