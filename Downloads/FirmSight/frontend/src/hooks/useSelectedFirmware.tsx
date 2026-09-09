import { createContext, useContext, useState, type ReactNode } from "react";

interface SelectedFirmwareContextValue {
  selectedFirmwareId: string | null;
  setSelectedFirmwareId: (id: string | null) => void;
}

const SelectedFirmwareContext = createContext<SelectedFirmwareContextValue | undefined>(undefined);

export function SelectedFirmwareProvider({ children }: { children: ReactNode }) {
  const [selectedFirmwareId, setSelectedFirmwareId] = useState<string | null>(null);
  return (
    <SelectedFirmwareContext.Provider value={{ selectedFirmwareId, setSelectedFirmwareId }}>
      {children}
    </SelectedFirmwareContext.Provider>
  );
}

export function useSelectedFirmware() {
  const context = useContext(SelectedFirmwareContext);
  if (!context) {
    throw new Error("useSelectedFirmware must be used within SelectedFirmwareProvider");
  }
  return context;
}
