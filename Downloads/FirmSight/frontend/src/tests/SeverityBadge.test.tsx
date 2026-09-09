import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import SeverityBadge from "../components/SeverityBadge";

describe("SeverityBadge", () => {
  it("renders the severity text", () => {
    render(<SeverityBadge severity="CRITICAL" />);
    expect(screen.getByText("CRITICAL")).toBeTruthy();
  });

  it("applies the severity class name", () => {
    render(<SeverityBadge severity="HIGH" />);
    const badge = screen.getByText("HIGH");
    expect(badge.className).toContain("HIGH");
  });
});
