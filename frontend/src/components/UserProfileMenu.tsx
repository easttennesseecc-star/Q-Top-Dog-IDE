import React, { useState, useRef, useEffect } from "react";

interface UserProfileMenuProps {
  user?: { name: string; avatarUrl?: string };
}

export const UserProfileMenu: React.FC<UserProfileMenuProps> = ({ user = { name: "User" } }) => {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    window.addEventListener("mousedown", handleClick);
    return () => window.removeEventListener("mousedown", handleClick);
  }, [open]);

  return (
    <div className="relative" ref={menuRef}>
      <button
        className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-700/20 hover:bg-cyan-700/40 transition-colors border border-cyan-400/40 shadow"
        onClick={() => setOpen(o => !o)}
        aria-label="Open user menu"
        title="User menu"
      >
        {user.avatarUrl ? (
          <img src={user.avatarUrl} alt="avatar" className="w-8 h-8 rounded-full border-2 border-cyan-400" />
        ) : (
          <span className="w-8 h-8 flex items-center justify-center rounded-full bg-cyan-500 text-white font-bold text-lg border-2 border-cyan-400">
            {user.name[0]}
          </span>
        )}
        <span className="text-cyan-100 font-semibold text-base hidden sm:block">{user.name}</span>
      </button>
      {open && (
        <div
          className="absolute top-full mt-2 min-w-[12rem] max-w-[calc(100vw-2rem)] max-h-[60vh] overflow-y-auto overflow-x-hidden rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-40 transition-all duration-200 opacity-100 translate-y-0"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="user-menu"
          style={{ 
            right: 0,
            left: 'auto'
          }}
        >
          <div className="py-1">
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => setOpen(false)}
            >
              Profile
            </button>
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => setOpen(false)}
            >
              Settings
            </button>
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => setOpen(false)}
            >
              Logout
            </button>
          </div>
        </div>
      )}
	</div>
  );
};
