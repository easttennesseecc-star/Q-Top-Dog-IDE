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
  const toggle = () => setTheme(t => (t === "dark" ? "light" : "dark"));
  const toggleContrast = () => setHighContrast(c => !c);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggle, highContrast, toggleContrast }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
