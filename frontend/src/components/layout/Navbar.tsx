import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import PingIndicator from "./PingIndicator";

interface NavbarProps {
  /** Page-specific controls (search, refresh...) shown between the logo and the ping. */
  children?: ReactNode;
}

export default function Navbar({ children }: NavbarProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-canvas/85 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3">
        <Link to="/discover" className="shrink-0 font-mono text-lg font-bold tracking-tight">
          <span className="text-violet-400">mog</span>
          <span className="text-cyan-400">match</span>
        </Link>
        <div className="flex min-w-0 flex-1 items-center gap-2">{children}</div>
        <PingIndicator />
      </div>
    </header>
  );
}
