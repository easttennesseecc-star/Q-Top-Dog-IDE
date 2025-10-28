import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
import PluginMarketplace from "./PluginMarketplace";

describe("PluginMarketplace UI", () => {
  it("renders marketplace and installed tabs", () => {
  render(<PluginMarketplace onClose={() => {}} />);
  // Use getAllByText to avoid ambiguity, and check for at least one element
  expect(screen.getAllByText("Marketplace").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Installed").length).toBeGreaterThan(0);
  });

  it("shows example plugins and allows install/uninstall", () => {
    render(<PluginMarketplace onClose={() => {}} />);
    // Should see at least one plugin
    expect(screen.getByText("Dark+ Theme")).toBeInTheDocument();
    // Uninstall button for installed plugin
    const uninstallBtn = screen.getByText("Uninstall");
    fireEvent.click(uninstallBtn);
    // After uninstall, Install button should appear
    expect(screen.getAllByText("Install")[0]).toBeInTheDocument();
  });

  it("toggles enable/disable for installed plugin", () => {
    render(<PluginMarketplace onClose={() => {}} />);
    // Find the disable button
    const disableBtn = screen.getByText("Disable");
    fireEvent.click(disableBtn);
    expect(screen.getByText("Enable")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Enable"));
    expect(screen.getByText("Disable")).toBeInTheDocument();
  });

  it("opens and closes the settings modal", () => {
    render(<PluginMarketplace onClose={() => {}} />);
    const settingsBtn = screen.getAllByText("Settings")[0];
    fireEvent.click(settingsBtn);
  // Settings modal should open; check for the settings close button
  expect(screen.getByLabelText(/Close settings/i)).toBeInTheDocument();
  // Close the settings modal and ensure the settings UI is removed
  fireEvent.click(screen.getByLabelText(/Close settings/i));
  expect(screen.queryByLabelText(/Close settings/i)).not.toBeInTheDocument();
  });
});
