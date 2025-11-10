import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./styles/theme.css"; // CSS variable theme tokens (light/dark/high-contrast)
// Root-level router wrapper now handles landing/login/signup vs main App
import Root from "./Root";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
