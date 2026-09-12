import { FileStack, LogOut, MessageSquare, Sparkles } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { useLogoutMutation } from "../api/authApi";
import { baseApi } from "../api/baseApi";
import { reportError } from "../api/errors";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { loggedOut } from "../features/auth/authSlice";

const NAV_ITEMS = [
  { to: "/documents", label: "Documents", icon: FileStack },
  { to: "/chat", label: "Chat", icon: MessageSquare },
];

export function Sidebar() {
  const user = useAppSelector((state) => state.auth.user);
  const [logout] = useLogoutMutation();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await logout().unwrap();
    } catch (err) {
      reportError(err);
    }
    // Clears every cached query (getMe included) so nothing stale survives
    // into the next login, regardless of whether the logout call itself
    // succeeded - the cookie may already be gone or expired either way.
    dispatch(baseApi.util.resetApiState());
    dispatch(loggedOut());
    navigate("/login");
  }

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 text-white">
          <Sparkles className="size-4" />
        </div>
        <span className="text-base font-semibold text-slate-900">ContextForge</span>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-200 p-3">
        {user && (
          <p className="mb-2 truncate px-3 text-xs text-slate-400" title={user.email}>
            {user.email}
          </p>
        )}
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-slate-900"
        >
          <LogOut className="size-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
