import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: "◈" },
  { to: "/upload", label: "Firmware Upload", icon: "⇧" },
  { to: "/firmware", label: "Firmware Analysis", icon: "⚙" },
  { to: "/filesystem", label: "Filesystem Explorer", icon: "⌂" },
  { to: "/findings", label: "Static Findings", icon: "⚠" },
  { to: "/emulation", label: "Emulation", icon: "▶" },
  { to: "/network", label: "Network Monitor", icon: "◎" },
  { to: "/threats", label: "Threat Detection", icon: "☠" },
  { to: "/report", label: "Security Report", icon: "▤" },
  { to: "/system", label: "System / Tool Status", icon: "✓" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-title">FIRMSIGHT</div>
        <div className="sidebar-brand-subtitle">
          IoT Firmware Emulation &amp; Dynamic Analysis Sandbox
        </div>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
