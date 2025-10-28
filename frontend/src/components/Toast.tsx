import React, { useEffect, useState } from 'react';

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  onClose: () => void;
  duration?: number;
}

const toastColors: Record<string, string> = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  info: 'bg-blue-500',
  warning: 'bg-yellow-500',
};

export const Toast: React.FC<ToastProps> = ({ message, type = 'info', onClose, duration = 3000 }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const hideAt = Math.max(220, duration - 220);
    const timer = setTimeout(() => setVisible(false), hideAt);
    const finish = setTimeout(onClose, duration);
    return () => {
      clearTimeout(timer);
      clearTimeout(finish);
    };
  }, [onClose, duration]);

  return (
    <div
      className={`fixed bottom-8 right-8 z-50 px-5 py-3 rounded-lg shadow-xl text-white text-sm font-medium flex items-center gap-3 ${visible ? 'animate-fade-in-up' : 'animate-fade-out-down'} ${toastColors[type]} bg-opacity-95 backdrop-blur-md`}
      role="status"
      aria-live="polite"
    >
      <div className="w-8 h-8 rounded-full flex items-center justify-center bg-white/12">
        {/* simple icon */}
        {type === 'success' ? '✓' : type === 'error' ? '!' : 'i'}
      </div>
      <div className="flex-1 text-sm">{message}</div>
      <button
        onClick={() => {
          setVisible(false);
          setTimeout(onClose, 180);
        }}
        className="ml-2 text-white/80 hover:text-white focus:outline-none px-2 py-1 rounded"
        aria-label="Close notification"
      >
        ×
      </button>
    </div>
  );
};
