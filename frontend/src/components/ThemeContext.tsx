import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface ThemeContextType {
  theme: "dark" | "light";
  toggle: () => void;
  highContrast: boolean;
  toggleContrast: () => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  theme: "dark",
  toggle: () => {},
  highContrast: false,
  toggleContrast: () => {},
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [highContrast, setHighContrast] = useState(false);

  // Initialize from localStorage or prefers-color-scheme
  useEffect(() => {
    try {
      const lsTheme = localStorage.getItem("topdog.theme") as "dark" | "light" | null;
      const lsHC = localStorage.getItem("topdog.highContrast");
      let initialTheme: "dark" | "light" = "dark";
      if (lsTheme === "dark" || lsTheme === "light") {
        initialTheme = lsTheme;
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        initialTheme = "light";
      }
      setTheme(initialTheme);
      setHighContrast(lsHC === "true");
    } catch {
      // ignore storage/matchMedia errors
    }
  }, []);

  const toggle = () => setTheme(t => (t === "dark" ? "light" : "dark"));
  const toggleContrast = () => setHighContrast(c => !c);

  // Apply classes and persist
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    try { localStorage.setItem("topdog.theme", theme); } catch {}
  }, [theme]);

  useEffect(() => {
    document.documentElement.classList.toggle("hc", highContrast);
    try { localStorage.setItem("topdog.highContrast", String(highContrast)); } catch {}
  }, [highContrast]);

  return (
    <ThemeContext.Provider value={{ theme, toggle, highContrast, toggleContrast }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
