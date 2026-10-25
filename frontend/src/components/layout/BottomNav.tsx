import { Compass, Inbox, Settings, Sparkles, User } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { getInbox, INVITES_CHANGED_EVENT } from "../../services/api";

const ITEMS = [
  { to: "/discover", label: "Discover", icon: Compass },
  { to: "/match", label: "Match", icon: Sparkles },
  { to: "/inbox", label: "Inbox", icon: Inbox },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
];

/** Invites waiting for my answer. Re-checked on page change, tab focus, every 15s, and after I answer one. */
function usePendingInvites(): number {
  const { pathname } = useLocation();
  const [count, setCount] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const recount = () =>
      getInbox(controller.signal)
        .then((inbox) => setCount(inbox.pending_count))
        .catch(() => {}); // the badge is a nice-to-have; pages show their own errors
    recount();
    window.addEventListener(INVITES_CHANGED_EVENT, recount);
    window.addEventListener("focus", recount);
    const timer = window.setInterval(recount, 15000); // so new invites light up the badge
    return () => {
      controller.abort();
      window.clearInterval(timer);
      window.removeEventListener(INVITES_CHANGED_EVENT, recount);
      window.removeEventListener("focus", recount);
    };
  }, [pathname]);

  return count;
}

export default function BottomNav() {
  const pending = usePendingInvites();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-surface/90 backdrop-blur">
      <ul className="mx-auto flex max-w-md justify-around px-2 py-2">
        {ITEMS.map(({ to, label, icon: Icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              // "/profile/edit" and "/profile/:id" keep Profile highlighted
              end={false}
              className={({ isActive }) =>
                `relative flex flex-col items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  isActive ? "text-violet-300" : "text-muted hover:text-slate-200"
                }`
              }
            >
              <Icon className="size-5" aria-hidden />
              {label}
              {to === "/inbox" && pending > 0 && (
                <span
                  aria-label={`${pending} new invite${pending === 1 ? "" : "s"}`}
                  className="absolute top-0 right-1 min-w-4 rounded-full bg-rose-500 px-1 text-center font-mono text-[10px] leading-4 text-white"
                >
                  {pending}
                </span>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
