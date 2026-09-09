import { HashRouter, Routes, Route, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import Dashboard from "./pages/Dashboard";
import FirmwareUpload from "./pages/FirmwareUpload";
import FirmwareAnalysis from "./pages/FirmwareAnalysis";
import FilesystemExplorer from "./pages/FilesystemExplorer";
import StaticFindings from "./pages/StaticFindings";
import Emulation from "./pages/Emulation";
import NetworkMonitor from "./pages/NetworkMonitor";
import ThreatDetection from "./pages/ThreatDetection";
import SecurityReportPage from "./pages/SecurityReportPage";
import SystemStatus from "./pages/SystemStatus";
import { SelectedFirmwareProvider } from "./hooks/useSelectedFirmware";

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/upload": "Firmware Upload",
  "/firmware": "Firmware Analysis",
  "/filesystem": "Filesystem Explorer",
  "/findings": "Static Findings",
  "/emulation": "Emulation",
  "/network": "Network Monitor",
  "/threats": "Threat Detection",
  "/report": "Security Report",
  "/system": "System / Tool Status",
};

function Layout() {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] ?? "FirmSight";

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <TopBar title={title} />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<FirmwareUpload />} />
            <Route path="/firmware" element={<FirmwareAnalysis />} />
            <Route path="/filesystem" element={<FilesystemExplorer />} />
            <Route path="/findings" element={<StaticFindings />} />
            <Route path="/emulation" element={<Emulation />} />
            <Route path="/network" element={<NetworkMonitor />} />
            <Route path="/threats" element={<ThreatDetection />} />
            <Route path="/report" element={<SecurityReportPage />} />
            <Route path="/system" element={<SystemStatus />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <SelectedFirmwareProvider>
      <HashRouter>
        <Layout />
      </HashRouter>
    </SelectedFirmwareProvider>
  );
}
