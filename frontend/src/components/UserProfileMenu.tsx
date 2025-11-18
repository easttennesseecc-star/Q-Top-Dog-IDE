import React, { useState, useRef, useEffect, useLayoutEffect } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { clearToken } from "../services/authClient";

interface UserProfileMenuProps {
  user?: { name: string; avatarUrl?: string };
}

export const UserProfileMenu: React.FC<UserProfileMenuProps> = ({ user = { name: "User" } }) => {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number; maxHeight: number } | null>(null);
  const [anchor, setAnchor] = useState<DOMRect | null>(null);
  const navigate = useNavigate();
  const { setToken } = useAuth();

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      const t = e.target as Node;
      if (
        menuRef.current && !menuRef.current.contains(t) &&
        btnRef.current && !btnRef.current.contains(t)
      ) {
        setOpen(false);
      }
    };
    window.addEventListener("mousedown", handleClick);
    return () => window.removeEventListener("mousedown", handleClick);
  }, [open]);

  // Capture anchor rect when opening
  useEffect(() => {
    if (!open) return;
    const btn = btnRef.current;
    if (btn) setAnchor(btn.getBoundingClientRect());
  }, [open]);

  // Position after menu has mounted so we can measure actual size
  useLayoutEffect(() => {
    if (!open || !menuRef.current || !anchor) return;
    const gutter = 8;
    const menuEl = menuRef.current;
    // Temporarily ensure it's visible for measurement
    menuEl.style.visibility = 'hidden';
    menuEl.style.maxHeight = 'none';
    menuEl.style.left = '0px';
    menuEl.style.top = '0px';
    const menuWidth = Math.min(menuEl.offsetWidth || 240, window.innerWidth - gutter * 2);
    const menuHeight = Math.min(menuEl.offsetHeight || 240, window.innerHeight - gutter * 2);

    const left = Math.min(
      Math.max(anchor.right - menuWidth, gutter),
      window.innerWidth - gutter - menuWidth
    );
    const proposedTop = anchor.bottom + gutter;
    const top = Math.min(proposedTop, Math.max(gutter, window.innerHeight - gutter - menuHeight));
    const maxHeight = Math.max(160, window.innerHeight - top - gutter);
    setPos({ top, left, maxHeight });
    // Restore visibility
    menuEl.style.visibility = '';
  }, [open, anchor]);

  // Recompute on resize/scroll with current measured size
  useEffect(() => {
    if (!open) return;
    const handler = () => {
      if (!menuRef.current || !anchor) return;
      const gutter = 8;
      const menuWidth = Math.min(menuRef.current.offsetWidth || 240, window.innerWidth - gutter * 2);
      const menuHeight = Math.min(menuRef.current.offsetHeight || 240, window.innerHeight - gutter * 2);
      const left = Math.min(
        Math.max(anchor.right - menuWidth, gutter),
        window.innerWidth - gutter - menuWidth
      );
      const proposedTop = anchor.bottom + gutter;
      const top = Math.min(proposedTop, Math.max(gutter, window.innerHeight - gutter - menuHeight));
      const maxHeight = Math.max(160, window.innerHeight - top - gutter);
      setPos({ top, left, maxHeight });
    };
    window.addEventListener('resize', handler);
    window.addEventListener('scroll', handler, { passive: true });
    return () => {
      window.removeEventListener('resize', handler);
      window.removeEventListener('scroll', handler as any);
    };
  }, [open, anchor]);

  return (
    <div className="relative">
      <button
        ref={btnRef}
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
      {open && pos && createPortal(
        <div
          ref={menuRef}
          className="fixed min-w-[12rem] max-w-[calc(100vw-1rem)] rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-[1000] transition-opacity duration-150"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="user-menu"
          style={{
            top: pos.top,
            left: pos.left,
            maxHeight: pos.maxHeight,
            overflowY: 'auto',
            overflowX: 'hidden'
          }}
        >
          <div className="py-1">
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => { setOpen(false); navigate('/app/account'); }}
            >
              Profile
            </button>
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => { setOpen(false); navigate('/app/settings'); }}
            >
              Settings
            </button>
            <button
              className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
              role="menuitem"
              onClick={() => {
                setOpen(false);
                clearToken();
                setToken(null);
                navigate('/login');
              }}
            >
              Logout
            </button>
          </div>
        </div>,
        document.body
      )}
	</div>
  );
};
