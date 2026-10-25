import { Check, ChevronDown, Loader2, Send, Sparkles } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import type { Socket } from "socket.io-client";
import { applyStudioRevision, askStudio, getStudioHistory } from "../../services/api";
import type { DesignDocument, ProjectIdea, StudioTurn } from "../../types/chat";
import DesignDocumentView, { SECTION_LABELS, sectionText } from "./DesignDocumentView";

const mergeTurns = (old: StudioTurn[], next: StudioTurn[]) =>
  [...new Map([...old, ...next].map((turn) => [turn.id, turn])).values()].sort((a, b) => a.id - b.id);

export default function StudioAssistant({ conversationId, idea, version, socket, onSaved }: {
  conversationId: string; idea: ProjectIdea; version: number; socket: Socket | null; onSaved: (idea: ProjectIdea) => void;
}) {
  const [turns, setTurns] = useState<StudioTurn[]>([]);
  const [mode, setMode] = useState<"ask" | "revise">("ask");
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [olderLoading, setOlderLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [applying, setApplying] = useState<number | null>(null);
  const [error, setError] = useState("");
  const token = useRef(crypto.randomUUID());
  const bottom = useRef<HTMLDivElement>(null);
  const follow = useRef(true);

  useEffect(() => {
    const controller = new AbortController();
    const load = () => getStudioHistory(conversationId, idea.id, controller.signal)
      .then((result) => { setTurns((old) => mergeTurns(old, result.turns)); setHasMore(result.has_more); setError(""); })
      .catch((err) => { if (!controller.signal.aborted) setError(err.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    const receive = (turn: StudioTurn) => {
      if (turn.idea_id === idea.id && turn.conversation_id === conversationId) setTurns((old) => mergeTurns(old, [turn]));
    };
    void load(); socket?.on("chat:studio", receive); socket?.on("connect", load);
    return () => { controller.abort(); socket?.off("chat:studio", receive); socket?.off("connect", load); };
  }, [conversationId, idea.id, socket]);

  useEffect(() => {
    if (follow.current) bottom.current?.scrollIntoView({ block: "end", behavior: "instant" });
    follow.current = true;
  }, [turns.at(-1)?.id, busy]);

  const send = async (event: FormEvent) => {
    event.preventDefault();
    if (!draft.trim() || busy) return;
    setBusy(true); setError("");
    try {
      const turn = await askStudio(conversationId, idea.id, draft.trim(), mode, token.current);
      setTurns((old) => mergeTurns(old, [turn])); setDraft(""); token.current = crypto.randomUUID();
    } catch (err) { setError(err instanceof Error ? err.message : "The AI couldn't respond. Your draft is kept for retry."); }
    finally { setBusy(false); }
  };

  const apply = async (turn: StudioTurn) => {
    setApplying(turn.id); setError("");
    try {
      const result = await applyStudioRevision(conversationId, idea.id, turn.id);
      setTurns((old) => mergeTurns(old, [result.turn])); onSaved(result.idea);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't save this revision."); }
    finally { setApplying(null); }
  };

  const older = async () => {
    setOlderLoading(true);
    try {
      const result = await getStudioHistory(conversationId, idea.id, undefined, turns[0]?.id);
      follow.current = false; setTurns((old) => mergeTurns(old, result.turns)); setHasMore(result.has_more);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't load earlier discussion."); }
    finally { setOlderLoading(false); }
  };

  return <section aria-label="AI plan discussion" className="flex min-h-0 flex-1 flex-col">
    <div role="log" aria-label="AI discussion" aria-live="polite" className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
      <details className="rounded-xl border border-violet-400/20 bg-violet-500/5 px-3 py-2 text-xs leading-relaxed text-muted">
        <summary className="cursor-pointer font-semibold text-violet-200">Discussing version {version} · shared with your teammate</summary>
        <p className="mt-1">Ask about this plan, or propose a revision. A preview changes the document only after you choose Save as new version.</p>
        <p className="mt-1">Uses this version, both profiles, and recent discussion. Sends context to OpenAI.</p>
      </details>
      {loading && <p className="text-sm text-muted">Loading AI discussion…</p>}
      {hasMore && <button onClick={() => void older()} disabled={olderLoading} className="mx-auto block rounded-full border border-line px-3 py-1.5 text-xs text-muted">{olderLoading ? "Loading…" : "Earlier AI discussion"}</button>}
      {!loading && !turns.length && <div className="space-y-2">
        <p className="text-xs text-muted">Try a question or a concrete scope change:</p>
        {[{ text: "Why this architecture?", mode: "ask" as const }, { text: "Simplify this into a weekend MVP.", mode: "revise" as const }].map((item) =>
          <button key={item.text} disabled={busy} onClick={() => { setMode(item.mode); setDraft(item.text); token.current = crypto.randomUUID(); }} className="block w-full rounded-xl border border-line px-3 py-2 text-left text-xs text-violet-200 hover:border-violet-400/50">{item.text}</button>)}
      </div>}
      {turns.map((turn) => <article key={turn.id} className="space-y-3">
        <div className="ml-5 rounded-2xl rounded-br-sm bg-violet-600/30 p-3">
          <p className="mb-1 text-[10px] text-violet-200">@{turn.author.username} · {turn.mode === "revise" ? "Revision request" : "Question"}</p>
          <p className="text-sm whitespace-pre-wrap [overflow-wrap:anywhere]">{turn.prompt}</p>
        </div>
        <div className="space-y-3 rounded-2xl rounded-bl-sm border border-line bg-canvas/50 p-3">
          <p className="flex items-center gap-1.5 text-xs font-semibold text-cyan-300"><Sparkles className="size-3.5" aria-hidden />Project assistant</p>
          <p className="text-sm leading-relaxed whitespace-pre-wrap text-slate-300 [overflow-wrap:anywhere]">{turn.answer}</p>
          {turn.proposal && <div className="space-y-3 rounded-xl border border-violet-400/30 bg-violet-500/5 p-3">
            <p className="text-xs font-semibold text-violet-200">Revision preview · based on version {version}</p>
            <ul className="list-disc space-y-1 pl-4 text-xs leading-relaxed text-slate-300 marker:text-violet-400">{turn.change_summary.map((change, i) => <li key={i}>{change}</li>)}</ul>
            <RevisionPreview original={idea.content} proposal={turn.proposal} />
            {turn.saved_idea_id ? <p className="flex items-center gap-1.5 text-xs text-emerald-300"><Check className="size-3.5" />Saved as a shared version</p> :
              <button onClick={() => void apply(turn)} disabled={applying !== null || busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-3 py-2.5 text-xs font-semibold hover:bg-violet-500 disabled:opacity-50">{applying === turn.id && <Loader2 className="size-3.5 animate-spin" />}{applying === turn.id ? "Saving…" : "Save as new version"}</button>}
          </div>}
          <time dateTime={turn.created_at} className="block text-[10px] text-muted">{new Date(turn.created_at).toLocaleString()}</time>
        </div>
      </article>)}
      {busy && <div role="status" className="flex items-center gap-2 text-sm text-violet-200"><Loader2 className="size-4 animate-spin" />{mode === "revise" ? "Preparing a revision preview…" : "Thinking about this plan…"}</div>}
      <div ref={bottom} />
    </div>
    <form onSubmit={(event) => void send(event)} className="shrink-0 space-y-2 border-t border-line bg-surface p-3">
      {error && <p role="alert" className="text-xs text-rose-300">{error}</p>}
      <div className="flex gap-1 rounded-lg bg-canvas p-1">
        {([{ mode: "ask", text: "Ask a question" }, { mode: "revise", text: "Propose changes" }] as const).map((item) => <button key={item.mode} type="button" disabled={busy} aria-pressed={mode === item.mode}
          onClick={() => { setMode(item.mode); token.current = crypto.randomUUID(); }} className={`flex-1 rounded-md px-2 py-1.5 text-xs font-medium ${mode === item.mode ? "bg-violet-600 text-white" : "text-muted"}`}>{item.text}</button>)}
      </div>
      <div className="flex items-end gap-2 rounded-xl border border-line bg-canvas p-2 focus-within:border-violet-500/60">
        <textarea aria-label="Message the project assistant" rows={2} maxLength={2000} disabled={busy} value={draft}
          onChange={(event) => { setDraft(event.target.value); token.current = crypto.randomUUID(); }}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault(); event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder={mode === "ask" ? "Ask why, explore tradeoffs, clarify the plan…" : "Describe the changes you want to preview…"}
          className="min-w-0 flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted disabled:opacity-60" />
        <button type="submit" aria-label="Send to project assistant" disabled={busy || !draft.trim()} className="rounded-lg bg-violet-600 p-2.5 hover:bg-violet-500 disabled:opacity-40"><Send className="size-4" /></button>
      </div>
    </form>
  </section>;
}

function RevisionPreview({ original, proposal }: { original: DesignDocument; proposal: DesignDocument }) {
  const changed = (Object.keys(SECTION_LABELS) as (keyof DesignDocument)[])
    .filter((key) => JSON.stringify(original[key]) !== JSON.stringify(proposal[key]));
  return <div className="space-y-2">
    <details>
      <summary className="flex cursor-pointer items-center gap-1 text-xs font-medium text-cyan-300"><ChevronDown className="size-3" />Review {changed.length} changed section{changed.length === 1 ? "" : "s"}</summary>
      <div className="mt-3 space-y-3">{changed.map((key) => <details key={key} className="rounded-lg border border-line p-2">
        <summary className="cursor-pointer text-xs font-semibold text-violet-200">{SECTION_LABELS[key]}</summary>
        <div className="mt-2 space-y-2 text-xs leading-relaxed [overflow-wrap:anywhere]">
          <div className="rounded-lg bg-canvas p-2"><p className="mb-1 font-semibold text-muted">Before</p><p className="whitespace-pre-wrap text-slate-400">{sectionText(original, key)}</p></div>
          <div className="rounded-lg bg-violet-500/10 p-2"><p className="mb-1 font-semibold text-cyan-200">Proposed</p><p className="whitespace-pre-wrap text-slate-200">{sectionText(proposal, key)}</p></div>
        </div>
      </details>)}</div>
    </details>
    <details><summary className="cursor-pointer text-xs font-medium text-cyan-300">Read full revised document</summary><div className="mt-3"><DesignDocumentView doc={proposal} /></div></details>
  </div>;
}
