import { Check, RefreshCw, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States";
import Navbar from "../components/layout/Navbar";
import Avatar from "../components/profiles/Avatar";
import { cancelInvite, getInbox, respondToInvite } from "../services/api";
import type { InboxResponse, Invite, InviteStatus } from "../types/invite";

type Tab = "received" | "sent";

const POLL_MS = 5000;

const STATUS_STYLES: Record<InviteStatus, string> = {
  pending: "border-amber-400/40 bg-amber-400/10 text-amber-200",
  accepted: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  declined: "border-line bg-surface-raised text-muted",
};

/** Invites people sent me (accept/decline) and invites I sent (cancel while pending). */
export default function InboxPage() {
  const [inbox, setInbox] = useState<InboxResponse | null>(null);
  const [tab, setTab] = useState<Tab>("received");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    getInbox(controller.signal)
      .then(setInbox)
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Failed to load your inbox.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [reloadKey]);

  const refresh = () => setReloadKey((key) => key + 1);

  // New invites can arrive while this page is open: re-check quietly every few seconds and when
  // you come back to the tab. (No spinner, so the list doesn't flicker.)
  useEffect(() => {
    const quietReload = () => {
      if (document.visibilityState === "visible") getInbox().then(setInbox).catch(() => {});
    };
    const timer = window.setInterval(quietReload, POLL_MS);
    window.addEventListener("focus", quietReload);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", quietReload);
    };
  }, []);

  const respond = (invite: Invite, status: "accepted" | "declined") => {
    setBusyId(invite.id);
    setNotice(null);
    respondToInvite(invite.id, status)
      .then((updated) => {
        setInbox((current) =>
          current && {
            ...current,
            received: current.received.map((i) => (i.id === updated.id ? updated : i)),
            pending_count: current.pending_count - 1,
          },
        );
        setNotice(
          status === "accepted"
            ? `You and ${invite.sender.full_name} are connected.`
            : `Declined ${invite.sender.full_name}'s invite.`,
        );
      })
      .catch((err: unknown) => setNotice(err instanceof Error ? err.message : "Couldn't save, try again."))
      .finally(() => setBusyId(null));
  };

  const cancel = (invite: Invite) => {
    setBusyId(invite.id);
    setNotice(null);
    cancelInvite(invite.id)
      .then(() => {
        setInbox((current) => current && { ...current, sent: current.sent.filter((i) => i.id !== invite.id) });
        setNotice(`Cancelled your invite to ${invite.recipient.full_name}.`);
      })
      .catch((err: unknown) => setNotice(err instanceof Error ? err.message : "Couldn't cancel, try again."))
      .finally(() => setBusyId(null));
  };

  const list = inbox ? inbox[tab] : [];

  return (
    <>
      <Navbar>
        <h1 className="truncate text-sm font-semibold text-slate-200">Inbox</h1>
        <button
          type="button"
          onClick={refresh}
          title="Check for new invites"
          aria-label="Refresh"
          className="ml-auto shrink-0 rounded-full border border-line bg-surface p-2 text-muted transition-colors hover:border-cyan-500/50 hover:text-cyan-200"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
        </button>
      </Navbar>

      <main className="mx-auto max-w-3xl px-4 py-6">
        <div role="tablist" className="mb-5 inline-flex rounded-xl border border-line bg-surface p-1">
          {(["received", "sent"] as const).map((key) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={tab === key}
              onClick={() => setTab(key)}
              className={`rounded-lg px-4 py-1.5 text-sm font-medium transition-colors ${
                tab === key ? "bg-violet-600 text-white" : "text-muted hover:text-slate-200"
              }`}
            >
              {key === "received" ? "Received" : "Sent"}
              {key === "received" && inbox && inbox.pending_count > 0 && (
                <span className="ml-2 rounded-full bg-rose-500 px-1.5 font-mono text-xs text-white">
                  {inbox.pending_count}
                </span>
              )}
            </button>
          ))}
        </div>

        {notice && <p className="mb-4 text-sm text-violet-200">{notice}</p>}

        {error ? (
          <ErrorState message={error} onRetry={refresh} />
        ) : loading && !inbox ? (
          <LoadingState label="Checking your inbox…" />
        ) : list.length === 0 ? (
          <EmptyState title={tab === "received" ? "No invites yet" : "You haven't invited anyone"}>
            {tab === "received" ? (
              "When someone invites you to connect, it shows up here."
            ) : (
              <>
                Open{" "}
                <Link to="/match" className="text-cyan-300 hover:underline">
                  Match
                </Link>{" "}
                and press Invite on someone you liked.
              </>
            )}
          </EmptyState>
        ) : (
          <ul className={`flex flex-col gap-3 transition-opacity ${loading ? "opacity-60" : ""}`}>
            {list.map((invite) => {
              const person = tab === "received" ? invite.sender : invite.recipient;
              const busy = busyId === invite.id;
              return (
                <li key={invite.id} className="rounded-2xl border border-line bg-surface p-4">
                  <div className="flex items-center gap-4">
                    <Link to={`/profile/${person.id}`} className="group flex min-w-0 flex-1 items-center gap-4">
                      <Avatar name={person.full_name} url={person.avatar_url} />
                      <div className="min-w-0">
                        <p className="truncate font-semibold group-hover:text-violet-300">{person.full_name}</p>
                        <p className="truncate font-mono text-xs text-cyan-300">@{person.username}</p>
                        <p className="mt-0.5 text-xs text-muted">
                          {new Date(invite.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </Link>
                    <span
                      className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs capitalize ${STATUS_STYLES[invite.status]}`}
                    >
                      {invite.status}
                    </span>
                  </div>

                  {invite.message && (
                    <p className="mt-3 rounded-xl bg-surface-raised px-4 py-3 text-sm text-slate-200">
                      “{invite.message}”
                    </p>
                  )}

                  {invite.status === "pending" && (
                    <div className="mt-3 flex justify-end gap-2">
                      {tab === "received" ? (
                        <>
                          <button
                            type="button"
                            disabled={busy}
                            onClick={() => respond(invite, "declined")}
                            className="inline-flex items-center gap-2 rounded-lg border border-line px-4 py-2 text-sm text-muted transition-colors hover:text-slate-200 disabled:opacity-60"
                          >
                            <X className="size-4" aria-hidden />
                            Decline
                          </button>
                          <button
                            type="button"
                            disabled={busy}
                            onClick={() => respond(invite, "accepted")}
                            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-500 disabled:opacity-60"
                          >
                            <Check className="size-4" aria-hidden />
                            Accept
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => cancel(invite)}
                          className="rounded-lg border border-line px-4 py-2 text-sm text-muted transition-colors hover:text-slate-200 disabled:opacity-60"
                        >
                          Cancel invite
                        </button>
                      )}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </>
  );
}
