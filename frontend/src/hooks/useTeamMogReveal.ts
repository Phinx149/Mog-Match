import { useCallback, useEffect, useRef, useState } from "react";
import type { Invite } from "../types/invite";

/** Queue each new accepted match once per user/browser, even if HTTP and Socket.IO both report it. */
export function useTeamMogReveal(userId?: string) {
  const [queue, setQueue] = useState<Invite[]>([]);
  const seen = useRef(new Set<string>());
  useEffect(() => { setQueue([]); }, [userId]);

  const celebrate = useCallback((invite: Invite) => {
    if (!userId || invite.status !== "accepted" || !invite.team_mog) return;
    if (invite.sender.id !== userId && invite.recipient.id !== userId) return;
    const key = `mogmatch:team-reveal:${userId}:${invite.id}`;
    if (seen.current.has(key)) return;
    try { if (localStorage.getItem(key)) return; } catch { /* In-memory deduplication still works. */ }
    seen.current.add(key);
    try { localStorage.setItem(key, "1"); } catch { /* Storage can be disabled. */ }
    setQueue((current) => [...current, invite]);
  }, [userId]);

  const dismiss = useCallback(() => setQueue((current) => current.slice(1)), []);
  return { match: queue[0] ?? null, celebrate, dismiss };
}
