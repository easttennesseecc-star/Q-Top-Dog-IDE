import React from "react";

export interface ActivityIndicatorProps {
  status: "idle" | "running" | "success" | "error";
  label: string;
  type?: "build" | "test" | "ai";
}

const colorMap = {
  build: {
    idle: "bg-gray-400",
    running: "bg-cyan-400 animate-pulse",
    success: "bg-green-500",
    error: "bg-red-500",
  },
  test: {
    idle: "bg-gray-400",
    running: "bg-yellow-400 animate-pulse",
    success: "bg-green-500",
    error: "bg-red-500",
  },
  ai: {
    idle: "bg-gray-400",
    running: "bg-fuchsia-400 animate-pulse",
    success: "bg-green-500",
    error: "bg-red-500",
  },
};

export const ActivityIndicator: React.FC<ActivityIndicatorProps> = ({ status, label, type = "build" }) => {
  const statusColor = colorMap[type][status]
  return (
    <div className="flex items-center gap-2" title={label} aria-label={label}>
      <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full ring-1 ring-white/6 ${statusColor} shadow-sm`}> 
        <span className={`inline-block w-2 h-2 rounded-full bg-white/90 ${status === 'running' ? 'animate-pulse' : ''}`}></span>
      </span>
      <span className="text-xs text-cyan-100 font-semibold tracking-wide">{label}</span>
    </div>
  );
};
