import React, { useState } from "react";

interface UISnapshotReviewProps {
  snapshots: string[]; // base64 or URLs
  onApprove: () => void;
  onRequestChange: (message: string) => void;
  onClose: () => void;
}

export const UISnapshotReview: React.FC<UISnapshotReviewProps> = ({
  snapshots,
  onApprove,
  onRequestChange,
  onClose,
}) => {
  const [message, setMessage] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
  <div className="bg-gradient-to-br from-[#1b2430] to-[#0e1720] rounded-xl shadow-2xl p-6 w-[640px] max-w-full flex flex-col gap-4 border border-cyan-900/30 relative">
        <button
          className="absolute top-2 right-2 text-gray-400 hover:text-red-400 text-xl"
          onClick={onClose}
          aria-label="Close review modal"
        >
          ×
        </button>
  <h2 className="text-2xl font-bold text-cyan-300 mb-2">UI Snapshot Review</h2>
        <div className="flex flex-row gap-2 overflow-x-auto">
          {snapshots.map((src, i) => (
            <img
              key={i}
              src={src}
              alt={`UI Snapshot ${i + 1}`}
              className="rounded-lg border border-cyan-800/40 max-h-48 shadow-md"
              style={{ maxWidth: 200 }}
            />
          ))}
        </div>
        <div className="flex flex-col gap-2 mt-4">
          <textarea
            className="w-full rounded-md border border-cyan-800/40 bg-[#0b0f12] text-gray-200 p-3 resize-none"
            rows={4}
            placeholder="Type feedback or instructions for Q Assistant..."
            value={message}
            onChange={e => setMessage(e.target.value)}
          />
          <div className="flex gap-3 justify-end">
            <button
              className="btn-primary"
              onClick={onApprove}
            >
              Approve
            </button>
            <button
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-md font-semibold disabled:opacity-60"
              onClick={() => onRequestChange(message)}
              disabled={!message.trim()}
            >
              Request Change
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
