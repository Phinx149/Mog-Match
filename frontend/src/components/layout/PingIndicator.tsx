import { useCallback, useEffect, useState } from "react";
import { getHealth } from "../../services/api";

type PingState = { status: "checking" } | { status: "up"; ms: number } | { status: "down" };

const PING_INTERVAL_MS = 30_000;

/** Shows whether the Flask API is reachable; click to ping again. */
export default function PingIndicator() {
  const [state, setState] = useState<PingState>({ status: "checking" });

  const ping = useCallback(async () => {
    const started = performance.now();
    try {
      const health = await getHealth();
      if (health.database !== "ok") throw new Error("database unavailable");
      setState({ status: "up", ms: Math.round(performance.now() - started) });
    } catch {
      setState({ status: "down" });
    }
  }, []);

  useEffect(() => {
    void ping();
    const timer = window.setInterval(() => void ping(), PING_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [ping]);

  const dot =
    state.status === "up" ? "bg-emerald-400" : state.status === "down" ? "bg-rose-500" : "bg-amber-400";
  const label =
    state.status === "up" ? `${state.ms} ms` : state.status === "down" ? "offline" : "…";

  return (
    <button
      type="button"
      onClick={() => void ping()}
      title="Ping the API"
      className="flex shrink-0 items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 font-mono text-xs text-muted transition-colors hover:border-cyan-500/50 hover:text-slate-200"
    >
      <span className={`size-2 rounded-full ${dot}`} aria-hidden />
      <span className="hidden sm:inline">ping</span> {label}
    </button>
  );
}
