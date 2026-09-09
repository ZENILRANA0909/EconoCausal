import { useEffect, useState } from "react";
import { getHealth } from "../services/api";

interface TopBarProps {
  title: string;
}

export default function TopBar({ title }: TopBarProps) {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then(() => {
        if (!cancelled) setIsOnline(true);
      })
      .catch(() => {
        if (!cancelled) setIsOnline(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <header className="top-bar">
      <div className="top-bar-title">{title}</div>
      <div className="top-bar-status">
        <span>
          <span className={`status-dot ${isOnline ? "online" : "offline"}`} />
          {isOnline === null ? "Checking backend..." : isOnline ? "Backend Online" : "Backend Offline"}
        </span>
      </div>
    </header>
  );
}
