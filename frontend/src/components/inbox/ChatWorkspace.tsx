import { ArrowLeft, Loader2, Send, Sparkles } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import type { Socket } from "socket.io-client";
import { getMessages, getProjectIdeas, markConversationRead, respondToInvite, sendInvite } from "../../services/api";
import type { ChatMessage, Conversation, ProjectIdea } from "../../types/chat";
import Avatar from "../profiles/Avatar";
import ProjectPlan from "./ProjectPlan";
import ConnectionMenu from "./ConnectionMenu";

const mergeMessages = (old: ChatMessage[], next: ChatMessage[]) =>
  [...new Map([...old, ...next].map((m) => [m.id, m])).values()].sort((a, b) => a.id - b.id);

export default function ChatWorkspace({ conversation, userId, socket, connected, onBack, onRead, onConnectionChanged, onRefresh }: {
  conversation: Conversation; userId: string; socket: Socket | null; connected: boolean;
  onBack: () => void; onRead: (id: string) => void;
  onConnectionChanged: (id: string, action: "unmatch" | "block") => void; onRefresh: () => void;
}) {
  const { id, person } = conversation;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [ideas, setIdeas] = useState<ProjectIdea[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [olderLoading, setOlderLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [rematching, setRematching] = useState(false);
  const [studio, setStudio] = useState(false);
  const [error, setError] = useState("");
  const bottom = useRef<HTMLDivElement>(null);
  const token = useRef(crypto.randomUUID());
  const readCallback = useRef(onRead);
  readCallback.current = onRead;
  const lastRead = useRef(0);
  const alive = useRef(true);
  const scrollOnNext = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);

  const addIdea = (idea: ProjectIdea) => {
    if (idea.conversation_id === id) setIdeas((old) => [idea, ...old.filter((item) => item.id !== idea.id)]
      .sort((a, b) => b.created_at.localeCompare(a.created_at)));
  };

  useEffect(() => {
    const controller = new AbortController();
    const load = () => {
      Promise.all([getMessages(id, controller.signal), getProjectIdeas(id, controller.signal)])
        .then(([history, plans]) => {
          setMessages((old) => mergeMessages(old, history.messages));
          setHasMore(history.has_more);
          // A realtime plan can arrive while the initial HTTP history is still in flight.
          setIdeas((old) => [...new Map([...plans.ideas, ...old].map((plan) => [plan.id, plan])).values()]
            .sort((a, b) => b.created_at.localeCompare(a.created_at)));
          setError("");
        }).catch((err) => { if (!controller.signal.aborted) setError(err.message); })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    };
    const receive = (message: ChatMessage) => {
      if (message.conversation_id !== id) return;
      scrollOnNext.current = true;
      setMessages((old) => mergeMessages(old, [message]));
    };
    load();
    socket?.on("chat:message", receive);
    socket?.on("chat:idea", addIdea);
    socket?.on("connect", load);
    return () => {
      controller.abort(); socket?.off("chat:message", receive); socket?.off("chat:idea", addIdea); socket?.off("connect", load);
    };
  }, [id, socket]);

  const latestId = messages.at(-1)?.id;
  useEffect(() => {
    if (scrollOnNext.current) bottom.current?.scrollIntoView({ behavior: "instant", block: "end" });
    scrollOnNext.current = true;
    const read = () => {
      if (!latestId || document.visibilityState !== "visible" || lastRead.current >= latestId) return;
      markConversationRead(id, latestId).then(() => {
        lastRead.current = latestId; readCallback.current(id);
      }).catch(() => {});
    };
    read(); window.addEventListener("focus", read); document.addEventListener("visibilitychange", read);
    return () => { window.removeEventListener("focus", read); document.removeEventListener("visibilitychange", read); };
  }, [id, latestId]);

  const older = async () => {
    setOlderLoading(true);
    try {
      const result = await getMessages(id, undefined, messages[0]?.id);
      scrollOnNext.current = false;
      setMessages((old) => mergeMessages(old, result.messages)); setHasMore(result.has_more);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't load messages."); }
    finally { setOlderLoading(false); }
  };

  const send = (event?: FormEvent) => {
    event?.preventDefault();
    if (!conversation.can_message || !socket || !connected || !draft.trim() || sending) return;
    setSending(true); setError("");
    socket.timeout(10000).emit("chat:send", { conversation_id: id, body: draft.trim(), client_token: token.current },
      (timeout: Error | null, ack?: { message?: ChatMessage; error?: string }) => {
        if (!alive.current) return;
        setSending(false);
        if (timeout || !ack?.message) { setError(ack?.error ?? "Delivery wasn't confirmed. Your draft is kept; retry safely."); return; }
        setMessages((old) => mergeMessages(old, [ack.message!]));
        setDraft(""); token.current = crypto.randomUUID();
      });
  };

  const rematch = async () => {
    if (rematching) return;
    setRematching(true); setError("");
    try {
      if (conversation.status === "pending" && conversation.rematch_requested_by !== userId) {
        await respondToInvite(id, "accepted");
      } else await sendInvite(person.id);
      onRefresh();
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't request a rematch."); }
    finally { setRematching(false); }
  };

  return <section aria-label={`Chat with ${person.full_name}`} className="flex h-full min-h-0 min-w-0 flex-col">
    <header className="flex shrink-0 items-center gap-3 border-b border-line px-3 py-2">
      <button onClick={onBack} aria-label="Back to conversations" className="rounded-lg p-1 text-muted hover:text-white lg:hidden"><ArrowLeft className="size-5" /></button>
      <Link to={`/profile/${person.id}`} className="flex min-w-0 flex-1 items-center gap-3">
        <span className="hidden sm:block"><Avatar name={person.full_name} url={person.avatar_url} /></span>
        <div className="min-w-0"><h2 className="truncate font-semibold">{person.full_name}</h2><p className="text-xs text-muted">{conversation.can_message ? "You matched. Make something great." : "Unmatched · conversation history"}</p></div>
      </Link>
      <ConnectionMenu conversation={conversation} onChanged={onConnectionChanged} />
      <button disabled={!conversation.can_message} aria-expanded={studio && conversation.can_message} onClick={() => setStudio(!studio)} className={`inline-flex shrink-0 items-center gap-2 rounded-xl border px-4 py-3 text-sm font-bold text-white shadow-lg transition-all hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 motion-safe:hover:-translate-y-0.5 sm:px-5 ${studio ? "border-cyan-300/70 bg-gradient-to-r from-violet-500 to-cyan-600 shadow-cyan-500/20" : "border-fuchsia-300/50 bg-gradient-to-r from-violet-600 to-fuchsia-500 shadow-fuchsia-500/25"}`}><Sparkles className="size-5" aria-hidden /><span>Project studio</span></button>
    </header>
    <div className="relative flex min-h-0 flex-1">
      <div className="flex min-h-0 min-w-0 flex-1 flex-col bg-gradient-to-b from-violet-500/[0.025] to-transparent">
        <div role="log" aria-label="Messages" aria-live="polite" className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4 sm:p-6">
          {loading && <p className="text-center text-sm text-muted">Loading conversation…</p>}
          {hasMore && <button onClick={() => void older()} disabled={olderLoading} className="mx-auto block rounded-full border border-line px-4 py-2 text-xs text-muted">{olderLoading ? "Loading…" : "Load earlier messages"}</button>}
          <div className="mx-auto max-w-sm py-5 text-center">
            <div className="mx-auto mb-3 flex w-fit -space-x-2"><Avatar name={person.full_name} url={person.avatar_url} /></div>
            <p className="font-semibold text-violet-200">It's a match worth building on.</p>
            <p className="mt-1 text-xs leading-relaxed text-muted">Say hello, swap ideas, or open Project studio to find your first collaboration.</p>
            {conversation.opening_message && <p className="mt-3 rounded-xl border border-line p-3 text-sm text-slate-300">{conversation.opening_message}</p>}
          </div>
          {messages.map((message) => {
            const mine = message.sender_id === userId;
            return <div key={message.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
              <div className="max-w-[85%] sm:max-w-[75%]">
                <p className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap [overflow-wrap:anywhere] ${mine ? "rounded-br-md bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white" : "rounded-bl-md border border-line bg-surface-raised text-slate-200"}`}>{message.body}</p>
                <time dateTime={message.created_at} className={`mt-1 block px-1 text-[10px] text-muted ${mine ? "text-right" : ""}`}>{new Date(message.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}{mine && " · Sent"}</time>
              </div>
            </div>;
          })}
          <div ref={bottom} />
        </div>
        <form onSubmit={send} className="shrink-0 border-t border-line bg-surface p-3 sm:p-4">
          {error && <p role="alert" className="mb-2 text-xs text-rose-300">{error}</p>}
          {!conversation.can_message && <div role="status" className="mb-3 rounded-xl border border-teal-400/20 bg-teal-400/5 p-3 text-sm text-teal-100">
            <p>You are unmatched. New messages are paused until you both agree to rematch.</p>
            {conversation.status === "pending" && conversation.rematch_requested_by === userId ?
              <p className="mt-2 text-xs text-muted">Rematch requested. Waiting for {person.full_name} to accept.</p> :
              <button type="button" disabled={rematching} onClick={() => void rematch()} className="mt-2 rounded-lg bg-teal-300 px-3 py-2 text-xs font-semibold text-teal-950 hover:bg-teal-200 disabled:opacity-50">{rematching ? "Updating…" : conversation.status === "pending" ? "Accept rematch" : "Request rematch"}</button>}
          </div>}
          {conversation.can_message && !connected && <p role="status" className="mb-2 text-xs text-amber-200">Reconnecting… Your draft is safe.</p>}
          <div className="flex items-end gap-2 rounded-2xl border border-line bg-canvas p-2 focus-within:border-violet-500/50">
            <textarea aria-label={`Message ${person.full_name}`} value={draft} disabled={sending || !conversation.can_message} maxLength={2000} rows={2}
              onChange={(e) => { setDraft(e.target.value); token.current = crypto.randomUUID(); }}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(); } }}
              placeholder="Say something worth matching for…" className="max-h-32 min-w-0 flex-1 resize-none bg-transparent px-2 py-1 text-sm outline-none placeholder:text-muted disabled:opacity-60" />
            <button type="submit" disabled={!conversation.can_message || !connected || sending || !draft.trim()} aria-label="Send message" className="rounded-xl bg-violet-600 p-3 text-white hover:bg-violet-500 disabled:opacity-40">{sending ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}</button>
          </div>
          <p className="mt-1.5 flex justify-between px-1 text-[10px] text-muted"><span>Enter to send · Shift + Enter for a new line</span><span>{draft.length}/2000</span></p>
        </form>
      </div>
      {studio && conversation.can_message && <ProjectPlan id={id} ideas={ideas} socket={socket} onGenerated={addIdea} onClose={() => setStudio(false)} />}
    </div>
  </section>;
}
