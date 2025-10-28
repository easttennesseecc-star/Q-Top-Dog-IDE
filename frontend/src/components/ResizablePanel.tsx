import React, { useRef, useState } from "react";


interface ResizablePanelProps {
  minWidth?: number;
  maxWidth?: number;
  initialWidth?: number;
  minHeight?: number;
  maxHeight?: number;
  initialHeight?: number;
  direction?: "horizontal" | "vertical";
  className?: string;
  children: React.ReactNode;
}


export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  minWidth = 220,
  maxWidth = 700,
  initialWidth = 340,
  minHeight = 120,
  maxHeight = 600,
  initialHeight = 180,
  direction = "horizontal",
  className = "",
  children,
}) => {
  // State for width/height
  const [size, setSize] = useState(direction === "vertical" ? initialHeight : initialWidth);
  const panelRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const onMouseDown = (e: React.MouseEvent) => {
    dragging.current = true;
    const startPos = direction === "vertical" ? e.clientY : e.clientX;
    const startSize = size;
    const onMouseMove = (moveEvent: MouseEvent) => {
      if (!dragging.current) return;
      if (direction === "vertical") {
        const newHeight = Math.min(
          Math.max(minHeight, startSize + moveEvent.clientY - startPos),
          maxHeight
        );
        setSize(newHeight);
      } else {
        const newWidth = Math.min(
          Math.max(minWidth, startSize + moveEvent.clientX - startPos),
          maxWidth
        );
        setSize(newWidth);
      }
    };
    const onMouseUp = () => {
      dragging.current = false;
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  };

  // Style for panel size
  const style = direction === "vertical"
    ? { height: size, minHeight, maxHeight }
    : { width: size, minWidth, maxWidth };

  return (
    <div
      ref={panelRef}
      className={"relative flex flex-col bg-[#23272e] border-2 border-[#2a2d36] rounded-lg shadow " + className}
      style={style}
    >
      {children}
      <div
        className={direction === "vertical"
          ? "absolute bottom-0 left-0 w-full h-2 cursor-ns-resize z-20 bg-transparent hover:bg-cyan-400/20 transition-colors"
          : "absolute top-0 right-0 h-full w-2 cursor-ew-resize z-20 bg-transparent hover:bg-cyan-400/20 transition-colors"}
        onMouseDown={onMouseDown}
        title="Resize panel"
        aria-label="Resize panel"
        style={{ userSelect: "none" }}
      />
    </div>
  );
};
