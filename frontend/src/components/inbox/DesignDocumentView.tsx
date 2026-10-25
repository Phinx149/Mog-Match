import type { DesignDocument } from "../../types/chat";

export const SECTION_LABELS: Record<keyof DesignDocument, string> = {
  title: "Title", summary: "Summary", problem: "The problem", target_users: "Target users",
  features: "MVP features", discussion_notes: "From your conversation", architecture: "Architecture",
  tech_stack: "Tech stack", data_model: "Data model", api_contracts: "API contracts",
  team_roles: "Who builds what", milestones: "Build plan", testing: "Testing",
  deployment: "Deployment", risks: "Risks", open_questions: "Open questions",
};

export function sectionText(doc: DesignDocument, key: keyof DesignDocument): string {
  if (key === "tech_stack") return doc.tech_stack.map((s) => `${s.component}: ${s.technology}\n${s.rationale}`).join("\n\n");
  if (key === "team_roles") return doc.team_roles.map((r) => `@${r.username}: ${r.responsibility}\nLearning goal: ${r.learning_goal}`).join("\n\n");
  if (key === "milestones") return doc.milestones.map((m) => `${m.title} (${m.estimate})\n${m.deliverables.map((d) => `• ${d}`).join("\n")}`).join("\n\n");
  const value = doc[key];
  return typeof value === "string" ? value : (value as string[]).map((item) => `• ${item}`).join("\n");
}

export default function DesignDocumentView({ doc }: { doc: DesignDocument }) {
  return <div className="space-y-5 text-sm leading-relaxed text-slate-300 [overflow-wrap:anywhere]">
    <div><p className="text-xs tracking-widest text-cyan-300 uppercase">Your next build</p><h4 className="mt-2 text-xl font-bold text-white">{doc.title}</h4><p className="mt-2">{doc.summary}</p></div>
    {(Object.keys(SECTION_LABELS) as (keyof DesignDocument)[]).filter((key) => key !== "title" && key !== "summary").map((key) =>
      <section key={key}><h5 className="mb-2 text-xs font-semibold tracking-widest text-violet-300 uppercase">{SECTION_LABELS[key]}</h5>
        <p className="whitespace-pre-wrap">{sectionText(doc, key)}</p>
      </section>)}
    <p className="border-t border-line pt-3 text-xs text-muted">AI-generated proposal. Review assumptions and agree on scope together.</p>
  </div>;
}
