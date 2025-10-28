import React, { useEffect, useRef, useState } from "react";

interface Command {
  label: string;
  action: () => void;
  shortcut?: string;
}

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  commands: Command[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ open, onClose, commands }) => {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setQuery("");
      setSelected(0);
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [open]);

  const filtered = commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase()));

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowDown") setSelected(s => Math.min(s + 1, filtered.length - 1));
      if (e.key === "ArrowUp") setSelected(s => Math.max(s - 1, 0));
      if (e.key === "Enter" && filtered[selected]) {
        filtered[selected].action();
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, selected, filtered, onClose]);

  return open ? (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40" onClick={onClose}>
      <div
        className="mt-32 w-full max-w-xl bg-[#23272e] rounded-xl shadow-2xl border border-cyan-400/40 p-4"
        onClick={e => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          className="w-full p-3 rounded-lg bg-[#181a20] text-white text-lg outline-none mb-2"
          placeholder="Type a command..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <ul className="max-h-64 overflow-y-auto">
          {filtered.length === 0 && <li className="text-gray-400 p-2">No commands found</li>}
          {filtered.map((cmd, i) => (
            <li
              key={cmd.label}
              className={`p-2 rounded cursor-pointer flex items-center justify-between ${i === selected ? "bg-cyan-700/40 text-cyan-200" : "text-white hover:bg-cyan-700/20"}`}
              onMouseEnter={() => setSelected(i)}
              onClick={() => { cmd.action(); onClose(); }}
            >
              <span>{cmd.label}</span>
              {cmd.shortcut && <span className="ml-4 text-xs text-cyan-300 bg-cyan-900/40 px-2 py-1 rounded">{cmd.shortcut}</span>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  ) : null;
};
