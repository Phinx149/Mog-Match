import { Check, MessageCircle, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { cancelInvite, respondToInvite } from "../../services/api";
import type { InboxResponse, Invite } from "../../types/invite";
import Avatar from "../profiles/Avatar";

export default function MatchRequests({ inbox, onChange, onOpen }: {
  inbox: InboxResponse; onChange: () => void; onOpen: (id: string) => void;
}) {
  const [tab, setTab] = useState<"received" | "sent">("received");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState("");

  const act = async (invite: Invite, action: "accepted" | "declined" | "cancel") => {
    setBusy(invite.id);
    setError("");
    try {
      if (action === "cancel") await cancelInvite(invite.id);
      else await respondToInvite(invite.id, action);
      onChange();
      if (action === "accepted") onOpen(invite.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't update request."); }
    finally { setBusy(null); }
  };

  return <div className="h-full overflow-y-auto p-5 sm:p-8">
    <p className="text-xs font-semibold tracking-widest text-cyan-300 uppercase">Find your next collaborator</p>
    <h2 className="mt-2 text-2xl font-bold">Match requests</h2>
    <p className="mt-2 text-sm text-muted">Accept a request to open a private conversation and start building together.</p>
    <div className="my-6 flex gap-2" aria-label="Request direction">
      {(["received", "sent"] as const).map((key) => <button key={key} onClick={() => setTab(key)}
        aria-pressed={tab === key} className={`rounded-full px-4 py-2 text-sm capitalize ${tab === key ? "bg-violet-600 text-white" : "bg-surface-raised text-muted"}`}>{key}</button>)}
    </div>
    {error && <p role="alert" className="mb-4 text-sm text-rose-300">{error}</p>}
    {!inbox[tab].length && <p className="rounded-2xl border border-dashed border-line p-8 text-center text-sm text-muted">
      {tab === "received" ? "Your next connection starts here. New requests will appear in this inbox." : "No requests sent yet. Visit Match to connect with someone you liked."}
    </p>}
    <ul className="space-y-3">
      {inbox[tab].map((invite) => {
        const person = tab === "received" ? invite.sender : invite.recipient;
        return <li key={invite.id} className="rounded-2xl border border-line bg-canvas/40 p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <Avatar name={person.full_name} url={person.avatar_url} />
            <Link to={`/profile/${person.id}`} className="min-w-0 flex-1 hover:text-violet-300">
              <p className="truncate font-semibold">{person.full_name}</p>
              <p className="truncate text-xs text-muted">@{person.username}</p>
            </Link>
            <span className={`rounded-full px-2.5 py-1 text-xs capitalize ${invite.status === "accepted" ? "bg-emerald-500/10 text-emerald-300" : invite.status === "pending" ? "bg-violet-500/15 text-violet-200" : "bg-surface-raised text-muted"}`}>{invite.status}</span>
          </div>
          {invite.message && <p className="mt-4 rounded-xl bg-surface-raised p-3 text-sm leading-relaxed text-slate-300">{invite.message}</p>}
          <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
            <time className="mr-auto text-xs text-muted">{new Date(invite.created_at).toLocaleDateString()}</time>
            {invite.status === "accepted" && <button onClick={() => onOpen(invite.id)} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium hover:bg-violet-500"><MessageCircle className="size-4" />Open chat</button>}
            {invite.status === "pending" && (tab === "received" ? <>
              <button disabled={busy !== null} onClick={() => void act(invite, "declined")} className="inline-flex items-center gap-1 rounded-xl px-3 py-2 text-sm text-muted hover:text-rose-300 disabled:opacity-50"><X className="size-4" />Decline</button>
              <button disabled={busy !== null} onClick={() => void act(invite, "accepted")} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium hover:bg-violet-500 disabled:opacity-50"><Check className="size-4" />{busy === invite.id ? "Connecting…" : "Accept & chat"}</button>
            </> : <button disabled={busy !== null} onClick={() => void act(invite, "cancel")} className="rounded-xl border border-line px-3 py-2 text-sm text-muted disabled:opacity-50">Cancel request</button>)}
          </div>
        </li>;
      })}
    </ul>
  </div>;
}
