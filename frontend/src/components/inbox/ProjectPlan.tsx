import { Download, FileText, GripVertical, Loader2, MessageSquare, Sparkles, X } from "lucide-react";
import { useEffect, useId, useRef, useState, type CSSProperties, type PointerEvent } from "react";
import type { Socket } from "socket.io-client";
import { generateProjectIdea } from "../../services/api";
import type { ProjectIdea } from "../../types/chat";
import DesignDocumentView from "./DesignDocumentView";
import StudioAssistant from "./StudioAssistant";

const MIN_WIDTH = 320;
const DEFAULT_WIDTH = 420;
const WIDTH_KEY = "mogmatch:studio-width";

function markdown(idea: ProjectIdea) {
  const d = idea.content;
  const list = (items: string[]) => items.map((text) => `- ${text}`).join("\n");
  return `# ${d.title}\n\n${d.summary}\n\n## Problem\n${d.problem}\n\n## Target users\n${d.target_users}\n\n## MVP\n${list(d.features)}\n\n## Conversation decisions\n${d.discussion_notes}\n\n## Architecture\n${d.architecture}\n\n## Tech stack\n${d.tech_stack.map((s) => `- **${s.component}: ${s.technology}** — ${s.rationale}`).join("\n")}\n\n## Data model\n${list(d.data_model)}\n\n## API contracts\n${list(d.api_contracts)}\n\n## Team responsibilities\n${d.team_roles.map((r) => `- **@${r.username}**: ${r.responsibility}\n  Learning goal: ${r.learning_goal}`).join("\n")}\n\n## Build plan\n${d.milestones.map((m) => `### ${m.title} (${m.estimate})\n${list(m.deliverables)}`).join("\n\n")}\n\n## Testing\n${list(d.testing)}\n\n## Deployment\n${d.deployment}\n\n## Risks\n${list(d.risks)}\n\n## Open questions\n${list(d.open_questions)}\n`;
}

export default function ProjectPlan({ id, ideas, socket, onGenerated, onClose }: {
  id: string; ideas: ProjectIdea[]; socket: Socket | null; onGenerated: (idea: ProjectIdea) => void; onClose: () => void;
}) {
  const [brief, setBrief] = useState("");
  const [selected, setSelected] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"document" | "assistant">("document");
  const [width, setWidth] = useState(() => {
    try {
      const saved = Number(localStorage.getItem(WIDTH_KEY));
      return Number.isFinite(saved) && saved >= MIN_WIDTH ? Math.min(saved, 800) : DEFAULT_WIDTH;
    } catch { return DEFAULT_WIDTH; }
  });
  const [maxWidth, setMaxWidth] = useState(800);
  const [resizing, setResizing] = useState(false);
  const panel = useRef<HTMLElement>(null);
  const drag = useRef<{ x: number; width: number } | null>(null);
  const panelId = useId();
  const idea = ideas.find((item) => item.id === selected) ?? ideas[0];
  const doc = idea?.content;
  const version = idea ? ideas.length - ideas.findIndex((item) => item.id === idea.id) : 0;
  const parentIndex = ideas.findIndex((item) => item.id === idea?.parent_idea_id);

  useEffect(() => {
    // Keep this version selected when a teammate publishes a newer plan.
    if (!selected && ideas[0]) setSelected(ideas[0].id);
  }, [selected, ideas]);

  useEffect(() => {
    const container = panel.current?.parentElement;
    if (!container) return;
    const measure = () => {
      if (!window.matchMedia("(min-width: 1280px)").matches) return;
      // Keep enough space for the conversation and message composer beside the studio.
      const limit = Math.max(MIN_WIDTH, Math.min(800, container.clientWidth - 300));
      setMaxWidth(limit);
      setWidth((current) => Math.min(current, limit));
    };
    const observer = new ResizeObserver(measure);
    observer.observe(container); measure();
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    try { localStorage.setItem(WIDTH_KEY, String(width)); } catch { /* Resizing still works without storage. */ }
  }, [width]);

  const resize = (value: number) => setWidth(Math.round(Math.min(maxWidth, Math.max(MIN_WIDTH, value))));
  const stopDrag = (event: PointerEvent<HTMLDivElement>) => {
    drag.current = null; setResizing(false);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
  };

  const generate = async () => {
    setBusy(true); setError("");
    try {
      const result = await generateProjectIdea(id, brief);
      onGenerated(result); setSelected(result.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Couldn't generate a project plan."); }
    finally { setBusy(false); }
  };

  const download = () => {
    if (!idea) return;
    const url = URL.createObjectURL(new Blob([markdown(idea)], { type: "text/markdown;charset=utf-8" }));
    const anchor = document.createElement("a");
    const title = idea.content.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "project-plan";
    const version = ideas.length - ideas.findIndex((item) => item.id === idea.id);
    anchor.href = url; anchor.download = `${title}-v${version}.md`; anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return <aside ref={panel} id={panelId} aria-label="Shared project studio"
    style={{ "--studio-width": `${width}px` } as CSSProperties}
    className={`absolute inset-0 z-10 flex min-h-0 min-w-0 flex-col border-line bg-surface xl:relative xl:inset-auto xl:w-[var(--studio-width)] xl:shrink-0 xl:border-l ${resizing ? "cursor-col-resize select-none" : ""}`}>
    <div role="separator" aria-label="Resize project studio" aria-orientation="vertical" aria-controls={panelId}
      aria-valuemin={MIN_WIDTH} aria-valuemax={maxWidth} aria-valuenow={width} tabIndex={0}
      title="Drag left to widen. Use the arrow keys to resize, or double-click to reset."
      className="group absolute inset-y-0 -left-2 z-20 hidden w-4 cursor-col-resize touch-none items-center justify-center outline-none xl:flex"
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        event.preventDefault(); event.currentTarget.focus();
        drag.current = { x: event.clientX, width }; setResizing(true);
        event.currentTarget.setPointerCapture(event.pointerId);
      }}
      onPointerMove={(event) => { if (drag.current) resize(drag.current.width + drag.current.x - event.clientX); }}
      onPointerUp={stopDrag} onPointerCancel={stopDrag}
      onLostPointerCapture={() => { drag.current = null; setResizing(false); }}
      onDoubleClick={() => resize(DEFAULT_WIDTH)}
      onKeyDown={(event) => {
        const next = event.key === "ArrowLeft" ? width + 32 : event.key === "ArrowRight" ? width - 32 : event.key === "Home" ? MIN_WIDTH : event.key === "End" ? maxWidth : null;
        if (next !== null) { event.preventDefault(); resize(next); }
      }}>
      <span className="flex h-16 w-3 items-center justify-center rounded-full border border-violet-400/40 bg-surface-raised text-violet-300 shadow-lg transition-colors group-hover:border-cyan-300 group-hover:bg-violet-500/30 group-focus-visible:ring-2 group-focus-visible:ring-cyan-300"><GripVertical className="h-6 w-3" aria-hidden /></span>
    </div>
    <div className="shrink-0 border-b border-line">
    <header className="flex items-center gap-2 px-3 py-2">
      <Sparkles className="size-4 shrink-0 text-cyan-300" aria-hidden />
      <h3 className={`shrink-0 text-sm font-semibold whitespace-nowrap ${idea ? "" : "flex-1"}`}>Project studio</h3>
      {idea && <select aria-label="Project plan version" value={idea.id} onChange={(event) => setSelected(event.target.value)} className="field min-w-0 flex-1 px-2 py-1.5 text-xs" title={`Version ${version} · ${new Date(idea.created_at).toLocaleString()}`}>
        {ideas.map((item, i) => <option value={item.id} key={item.id}>Version {ideas.length - i} · {new Date(item.created_at).toLocaleDateString([], { month: "short", day: "numeric" })}, {new Date(item.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</option>)}
      </select>}
      <button onClick={onClose} aria-label="Close project studio" className="shrink-0 rounded-lg p-1.5 text-muted hover:bg-surface-raised"><X className="size-4" /></button>
    </header>
    {idea && <div className="flex items-center gap-2 px-3 pb-2">
      <div role="tablist" aria-label="Project studio views" className="flex min-w-0 rounded-lg bg-canvas p-0.5">
        {([{ key: "document", label: "Document", icon: FileText }, { key: "assistant", label: "Ask AI", icon: MessageSquare }] as const).map(({ key, label, icon: Icon }) =>
          <button key={key} id={`${panelId}-${key}`} role="tab" aria-selected={tab === key} aria-controls={`${panelId}-${key}-panel`} onClick={() => setTab(key)} className={`flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-semibold whitespace-nowrap ${tab === key ? "bg-violet-600 text-white" : "text-muted hover:text-slate-200"}`}><Icon className="size-3.5" aria-hidden />{label}</button>)}
      </div>
      <button onClick={download} aria-label="Download design document" title="Download selected design document (.md)" className="ml-auto inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-cyan-400/30 px-2 py-1.5 text-xs text-cyan-200 hover:bg-cyan-500/10"><Download className="size-3.5" aria-hidden />Download</button>
    </div>}
    </div>
    {tab === "assistant" && idea ? <div id={`${panelId}-assistant-panel`} role="tabpanel" aria-labelledby={`${panelId}-assistant`} className="flex min-h-0 flex-1 flex-col">
      <StudioAssistant key={idea.id} conversationId={id} idea={idea} version={version} socket={socket}
        onSaved={(saved) => { onGenerated(saved); setSelected(saved.id); setTab("document"); }} />
    </div> : <div id={`${panelId}-document-panel`} role="tabpanel" aria-labelledby={idea ? `${panelId}-document` : undefined} className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
      {doc && <>
        {parentIndex >= 0 && <p className="text-xs text-muted">Revision based on version {ideas.length - parentIndex}. The source version is preserved.</p>}
        <DesignDocumentView doc={doc} />
      </>}
      <details open={!doc} className="rounded-2xl border border-violet-500/30 bg-gradient-to-br from-violet-500/10 to-cyan-500/5 p-4">
        <summary className="cursor-pointer text-sm font-semibold text-violet-200">{doc ? "Generate another idea" : "Start with a project idea"}</summary>
        <div className="mt-3">
        <p className="text-sm leading-relaxed text-slate-300">Turn your combined skills and conversation into something worth building.</p>
        <label htmlFor="project-brief" className="mt-4 mb-2 block text-xs text-muted">Direction or constraints (optional)</label>
        <textarea id="project-brief" value={brief} onChange={(e) => setBrief(e.target.value)} maxLength={1000} rows={3}
          placeholder="A weekend MVP, no paid services, something for students…" className="field resize-none text-sm" disabled={busy} />
        <button onClick={() => void generate()} disabled={busy}
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-3 py-2.5 text-sm font-semibold hover:bg-violet-500 disabled:opacity-60">
          {busy ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
          {busy ? "Designing your project…" : ideas.length ? "Generate another idea" : "Generate project idea"}
        </button>
        <p className="mt-2 text-xs leading-relaxed text-muted">Uses both profiles and up to 100 recent messages (24,000 characters). Plans are shared in this chat. Generation sends this context to OpenAI.</p>
        {error && <p role="alert" className="mt-3 text-sm text-rose-300">{error}</p>}
        </div>
      </details>
      {!doc && <div className="py-5 text-center text-sm text-muted"><Sparkles className="mx-auto mb-3 size-8 text-violet-400/60" />Start with an idea. Leave with an architecture, a tech stack, and a plan for both of you.</div>}
    </div>}
  </aside>;
}

