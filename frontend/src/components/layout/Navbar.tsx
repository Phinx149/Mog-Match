import { LogOut } from "lucide-react";
import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import PingIndicator from "./PingIndicator";

interface NavbarProps {
  /** Page-specific controls (search, refresh...) shown between the logo and the ping. */
  children?: ReactNode;
}

export default function Navbar({ children }: NavbarProps) {
  const { user, logOut } = useAuth();
  const navigate = useNavigate();

  const leave = () => {
    logOut()
      .catch(() => {}) // even if the API is down, forget the user locally and show the login page
      .finally(() => navigate("/login"));
  };

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-canvas/85 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3">
        <Link to="/discover" className="shrink-0 font-mono text-lg font-bold tracking-tight">
          <span className="text-violet-400">mog</span>
          <span className="text-cyan-400">match</span>
        </Link>
        <div className="flex min-w-0 flex-1 items-center gap-2">{children}</div>
        <PingIndicator />
        {user && (
          <div className="flex shrink-0 items-center gap-1">
            <Link
              to="/profile"
              title="Logged in as"
              className="max-w-24 truncate font-mono text-xs text-cyan-300 hover:underline sm:max-w-none"
            >
              @{user.username}
            </Link>
            <button
              type="button"
              onClick={leave}
              aria-label="Log out"
              title="Log out"
              className="rounded-full border border-line bg-surface p-2 text-muted transition-colors hover:border-rose-500/50 hover:text-rose-200"
            >
              <LogOut className="size-4" aria-hidden />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
