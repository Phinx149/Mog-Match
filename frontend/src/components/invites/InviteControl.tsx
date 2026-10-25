import { Check, Clock, Inbox, MessageCircle, Send, UserPlus, X } from "lucide-react";
import { useId, useState } from "react";
import { Link } from "react-router-dom";
import { MAX_INVITE_MESSAGE_LENGTH, type Invite } from "../../types/invite";

interface InviteControlProps {
  name: string;
  /** The invite between me and this person, if there is one (sent by either side). */
  invite: Invite | null;
  /** True when `invite` was sent by them, not me. */
  fromThem: boolean;
  onSend: (message: string) => Promise<void>;
}

/** "Invite" button on a match card. Once an invite exists, shows where it stands instead. */
export default function InviteControl({ name, invite, fromThem, onSend }: InviteControlProps) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messageId = useId();

  if (invite?.status === "accepted") {
    return <Link to={`/inbox?chat=${invite.id}`} className="inline-flex items-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-4 py-2.5 text-sm font-semibold text-cyan-200 hover:bg-cyan-500/20"><MessageCircle className="size-4" aria-hidden />Open chat</Link>;
  }

  if (invite && invite.status !== "unmatched" && fromThem) {
    const text = invite.status === "pending" ? `${name} invited you` : `You ${invite.status} their invite`;
    return (
      <Link to="/inbox" className="inline-flex items-center gap-2 text-sm text-cyan-300 hover:underline">
        <Inbox className="size-4" aria-hidden />
        {text}
      </Link>
    );
  }

  if (invite && invite.status !== "unmatched") {
    const STATUS = {
      pending: { icon: Clock, text: "Invite sent · waiting", tone: "text-amber-200" },
      accepted: { icon: Check, text: "Invite accepted", tone: "text-emerald-300" },
      declined: { icon: X, text: "Invite declined", tone: "text-muted" },
    } as const;
    const { icon: Icon, text, tone } = STATUS[invite.status];
    return (
      <span className={`inline-flex items-center gap-2 text-sm ${tone}`}>
        <Icon className="size-4" aria-hidden />
        {text}
      </span>
    );
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-xl border border-violet-500/50 bg-violet-500/15 px-5 py-2.5 text-sm font-semibold text-violet-100 transition-colors hover:bg-violet-500/30"
      >
        <UserPlus className="size-4" aria-hidden />
        Match request
      </button>
    );
  }

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    setSending(true);
    setError(null);
    onSend(message)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Couldn't send, try again."))
      .finally(() => setSending(false));
  };

  return (
    <form onSubmit={submit} className="flex w-full flex-col gap-2">
      <label htmlFor={messageId} className="text-xs text-muted">
        Say hi to {name} (optional)
      </label>
      <textarea
        id={messageId}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        maxLength={MAX_INVITE_MESSAGE_LENGTH}
        rows={2}
        placeholder="Want to build something together?"
        className="field resize-none"
      />
      {error && <p className="text-xs text-rose-300">{error}</p>}
      <div className="flex items-center justify-end gap-2">
        <span className="mr-auto font-mono text-xs text-muted">
          {message.length}/{MAX_INVITE_MESSAGE_LENGTH}
        </span>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="rounded-lg px-3 py-2 text-sm text-muted hover:text-slate-200"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={sending}
          className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-60"
        >
          <Send className="size-4" aria-hidden />
          {sending ? "Sending…" : "Send match request"}
        </button>
      </div>
    </form>
  );
}
