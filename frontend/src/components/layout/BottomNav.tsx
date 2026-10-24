import { Compass, Settings, User } from "lucide-react";
import { NavLink } from "react-router-dom";

const ITEMS = [
  { to: "/discover", label: "Discover", icon: Compass },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function BottomNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-surface/90 backdrop-blur">
      <ul className="mx-auto flex max-w-md justify-around px-4 py-2">
        {ITEMS.map(({ to, label, icon: Icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              // "/profile/edit" and "/profile/:id" keep Profile highlighted
              end={false}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 rounded-lg px-4 py-1.5 text-xs font-medium transition-colors ${
                  isActive ? "text-violet-300" : "text-muted hover:text-slate-200"
                }`
              }
            >
              <Icon className="size-5" aria-hidden />
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
