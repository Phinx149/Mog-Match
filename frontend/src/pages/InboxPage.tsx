import { Inbox, MessageCircle, RefreshCw, Search, Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { io, type Socket } from "socket.io-client";
import ChatWorkspace from "../components/inbox/ChatWorkspace";
import MatchRequests from "../components/inbox/MatchRequests";
import TeamMogReveal from "../components/inbox/TeamMogReveal";
import Navbar from "../components/layout/Navbar";
import Avatar from "../components/profiles/Avatar";
import { useAuth } from "../hooks/useAuth";
import { useTeamMogReveal } from "../hooks/useTeamMogReveal";
import { API_URL, getConversations, getInbox, INVITES_CHANGED_EVENT } from "../services/api";
import type { Conversation } from "../types/chat";
import type { InboxResponse } from "../types/invite";

export default function InboxPage() {
  const { user } = useAuth();
  const { match: newMatch, celebrate, dismiss } = useTeamMogReveal(user?.id);
  const [params, setParams] = useSearchParams();
  const activeId = params.get("chat");
  const [tab, setTab] = useState<"messages" | "requests">("messages");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [inbox, setInbox] = useState<InboxResponse | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const requestVersion = useRef(0);

  const refresh = useCallback(async () => {
    const version = ++requestVersion.current;
    try {
      const [threads, requests] = await Promise.all([getConversations(), getInbox()]);
      if (version !== requestVersion.current) return;
      setConversations(threads.conversations); setInbox(requests); setError("");
      [...requests.received, ...requests.sent].filter((invite) => invite.status === "accepted" && invite.team_mog)
        .sort((a, b) => b.updated_at.localeCompare(a.updated_at)).forEach(celebrate);
      window.dispatchEvent(new Event(INVITES_CHANGED_EVENT));
    } catch (err) {
      if (version === requestVersion.current) setError(err instanceof Error ? err.message : "Couldn't load your inbox.");
    } finally { if (version === requestVersion.current) setLoading(false); }
  }, [celebrate]);

  useEffect(() => {
    if (!user) return;
    const client = io(API_URL, { withCredentials: true,
      transports: import.meta.env.PROD ? ["websocket"] : ["websocket", "polling"] });
    setSocket(client);
    const onConnect = () => { setConnected(true); void refresh(); };
    const offline = () => setConnected(false);
    const changed = () => { void refresh(); };
    client.on("connect", onConnect);
    client.on("disconnect", offline);
    client.on("connect_error", offline);
    client.on("inbox:updated", changed);
    client.on("chat:message", changed);
    client.on("chat:read", changed);
    client.on("team:matched", celebrate);
    window.addEventListener("focus", changed);
    void refresh();
    return () => {
      ++requestVersion.current; client.disconnect(); window.removeEventListener("focus", changed);
    };
  }, [user?.id, refresh, celebrate]);

  const open = (id: string) => { setTab("messages"); setParams({ chat: id }); void refresh(); };
  const active = conversations.find((item) => item.id === activeId);
  const filtered = conversations.filter((item) => `${item.person.full_name} ${item.person.username}`.toLowerCase().includes(query.toLowerCase()));
  const unread = conversations.reduce((total, item) => total + item.unread_count, 0);
  const read = (id: string) => setConversations((old) => old.map((item) => item.id === id ? { ...item, unread_count: 0 } : item));

  return <>
    <Navbar><h1 className="truncate text-sm font-semibold">Inbox</h1>
      <button onClick={() => void refresh()} aria-label="Refresh inbox" className="ml-auto rounded-lg p-1.5 text-muted hover:text-cyan-300"><RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} /></button>
    </Navbar>
    <main className="flex min-h-0 w-full flex-1 flex-col p-2">
      {error && <p role="alert" className="mb-2 shrink-0 rounded-xl border border-rose-500/30 bg-rose-500/5 p-2 text-sm text-rose-300">{error} <button onClick={() => void refresh()} className="underline">Retry</button></p>}
      <div className={`grid min-h-0 flex-1 overflow-hidden rounded-2xl border border-line bg-surface shadow-2xl shadow-black/20 lg:grid-cols-[16rem_minmax(0,1fr)] lg:grid-rows-1 ${tab === "requests" ? "grid-rows-[auto_minmax(0,1fr)]" : "grid-rows-1"}`}>
        <aside aria-label="Inbox navigation" className={`min-h-0 flex-col border-line lg:flex lg:border-r ${activeId && tab === "messages" ? "hidden" : "flex"}`}>
          <div className="border-b border-line p-4">
            <div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">Inbox</h2><span title={connected ? "Live connection" : "Connecting"} className={`size-2 rounded-full ${connected ? "bg-emerald-400 shadow-[0_0_8px_#34d39960]" : "bg-amber-400"}`} /></div>
            <div className="grid grid-cols-2 gap-1 rounded-xl bg-canvas p-1">
              <button onClick={() => setTab("messages")} aria-pressed={tab === "messages"} className={`rounded-lg px-2 py-2 text-xs font-medium ${tab === "messages" ? "bg-violet-600 text-white" : "text-muted"}`}>Messages {unread > 0 && <span className="ml-1">({unread})</span>}</button>
              <button onClick={() => setTab("requests")} aria-pressed={tab === "requests"} className={`rounded-lg px-2 py-2 text-xs font-medium ${tab === "requests" ? "bg-violet-600 text-white" : "text-muted"}`}>Requests {inbox && inbox.pending_count > 0 && <span className="ml-1 rounded-full bg-fuchsia-500 px-1.5">{inbox.pending_count}</span>}</button>
            </div>
          </div>
          {tab === "messages" ? <>
            <div className="p-3"><label className="flex items-center gap-2 rounded-xl border border-line bg-canvas px-3 py-2"><Search className="size-4 text-muted" /><input aria-label="Search conversations" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Find a conversation" className="min-w-0 flex-1 bg-transparent text-xs outline-none placeholder:text-muted" /></label></div>
            <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-3">
              {loading && <p className="p-4 text-sm text-muted">Loading conversations…</p>}
              {!loading && !filtered.length && <div className="p-5 text-center text-sm text-muted"><MessageCircle className="mx-auto mb-3 size-7 text-violet-400" />{query ? "No conversations found." : "Accept a match request to start a conversation."}<button onClick={() => setTab("requests")} className="mt-3 block w-full text-violet-300">View requests</button></div>}
              {filtered.map((item) => <button key={item.id} onClick={() => open(item.id)} aria-pressed={activeId === item.id}
                className={`mb-1 flex w-full items-center gap-3 rounded-xl p-3 text-left transition-colors ${activeId === item.id ? "bg-violet-500/15 ring-1 ring-inset ring-violet-400/20" : "hover:bg-surface-raised"}`}>
                <Avatar name={item.person.full_name} url={item.person.avatar_url} />
                <div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{item.person.full_name}</p><p className={`mt-1 truncate text-xs ${item.unread_count ? "text-slate-200" : "text-muted"}`}>{item.last_message?.body ?? "You matched! Say hello."}</p></div>
                {item.unread_count > 0 && <span className="rounded-full bg-fuchsia-500 px-1.5 text-xs text-white">{item.unread_count}</span>}
              </button>)}
            </div>
          </> : <div className="hidden space-y-3 p-5 text-sm text-muted lg:block"><Inbox className="size-8 text-violet-300" /><p>A little hello could be the start of your next big build.</p><Link to="/match" className="inline-block text-cyan-300 hover:underline">Find more collaborators →</Link></div>}
        </aside>
        <div className={`min-h-0 min-w-0 ${tab === "messages" && !activeId ? "hidden lg:block" : "block"} ${tab === "requests" ? "overflow-y-auto" : ""}`}>
          {tab === "requests" && inbox ? <MatchRequests inbox={inbox} onChange={() => void refresh()} onOpen={open} onAccepted={celebrate} /> :
            active && user ? <ChatWorkspace key={`${user.id}:${active.id}`} conversation={active} userId={user.id} socket={socket} connected={connected} onBack={() => setParams({})} onRead={read} /> :
              <div className="flex h-full flex-col items-center justify-center gap-3 p-8 text-center">
                <div className="mb-2 rounded-3xl border border-violet-500/20 bg-gradient-to-br from-violet-600/20 to-cyan-500/10 p-6"><Sparkles className="size-10 text-violet-300" /></div>
                <h2 className="text-xl font-semibold">A match is just the beginning.</h2><p className="max-w-sm text-sm leading-relaxed text-muted">Pick a conversation, trade a few ideas, and turn your shared skills into your next project.</p>
                <button onClick={() => { setParams({}); setTab("requests"); }} className="mt-3 rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-semibold hover:bg-violet-500">View match requests</button>
                {activeId && !loading && <p className="text-xs text-muted">If this conversation is new, refresh to load it. Only accepted requests can open a chat.</p>}
              </div>}
        </div>
      </div>
    </main>
    {newMatch && <TeamMogReveal key={newMatch.id} invite={newMatch} onDismiss={dismiss} onContinue={() => { open(newMatch.id); dismiss(); }} />}
  </>;
}
