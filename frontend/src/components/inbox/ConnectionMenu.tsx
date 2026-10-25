import { Ban, MoreHorizontal, UserMinus } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { endConnection } from "../../services/api";
import type { Conversation } from "../../types/chat";

export default function ConnectionMenu({ conversation, onChanged }: {
  conversation: Conversation; onChanged: (id: string, action: "unmatch" | "block") => void;
}) {
  const details = useRef<HTMLDetailsElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [position, setPosition] = useState({ left: 16, top: 16 });
  useEffect(() => {
    const close = (event: PointerEvent) => {
      if (!details.current?.contains(event.target as Node)) details.current?.removeAttribute("open");
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && details.current?.open) {
        details.current.removeAttribute("open");
        details.current.querySelector("summary")?.focus();
      }
    };
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("pointerdown", close); document.removeEventListener("keydown", escape); };
  }, []);

  if (!conversation.can_message) return null;
  const act = async (action: "unmatch" | "block") => {
    if (busy) return;
    setBusy(true); setError("");
    try {
      await endConnection(conversation.id, action);
      details.current?.removeAttribute("open");
      onChanged(conversation.id, action);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't update connection."); }
    finally { setBusy(false); }
  };

  return <details ref={details} className="relative shrink-0" onToggle={() => {
    if (!details.current?.open) return;
    const rect = details.current.getBoundingClientRect();
    setPosition({ left: Math.max(16, Math.min(rect.right - 240, window.innerWidth - 256)),
      top: Math.max(16, Math.min(rect.bottom + 6, window.innerHeight - 260)) });
  }}>
    <summary aria-label={`Match options for ${conversation.person.full_name}`} className="flex cursor-pointer list-none rounded-lg p-2 text-muted hover:bg-surface-raised hover:text-white focus-visible:outline-2 focus-visible:outline-cyan-300 [&::-webkit-details-marker]:hidden">
      <MoreHorizontal className="size-5" aria-hidden />
    </summary>
    <div style={position} className="fixed z-50 w-60 max-w-[calc(100vw-2rem)] rounded-xl border border-line bg-surface-raised p-1.5 shadow-xl shadow-black/40">
      <button disabled={busy} onClick={() => void act("unmatch")} className="flex w-full items-center gap-2 rounded-lg p-3 text-left text-sm text-slate-100 hover:bg-white/10 disabled:opacity-50"><UserMinus className="size-4" aria-hidden />Unmatch</button>
      <p className="px-3 pb-2 text-xs text-muted">Keep history. Pause messaging until you rematch.</p>
      <button disabled={busy} onClick={() => void act("block")} className="flex w-full items-center gap-2 rounded-lg p-3 text-left text-sm text-rose-300 hover:bg-rose-400/10 disabled:opacity-50"><Ban className="size-4" aria-hidden />Block user</button>
      <p className="px-3 pb-2 text-xs text-muted">Hide this conversation for both of you.</p>
      {error && <p role="alert" className="px-3 pb-2 text-xs text-rose-300">{error}</p>}
    </div>
  </details>;
}
