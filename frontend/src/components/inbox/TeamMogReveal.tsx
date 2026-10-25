import { Flame, MessageCircle, Sparkles, X } from "lucide-react";
import { useEffect, useId, useRef, useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";
import type { Invite } from "../../types/invite";
import Avatar from "../profiles/Avatar";
import "./TeamMogReveal.css";

export default function TeamMogReveal({ invite, onDismiss, onContinue }: {
  invite: Invite; onDismiss: () => void; onContinue: () => void;
}) {
  const team = invite.team_mog!;
  const flameGradient = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const [reduced, setReduced] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  const [phase, setPhase] = useState<"vortex" | "impact" | "reveal">(reduced ? "reveal" : "vortex");

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    dialog.current?.showModal();
    const element = dialog.current;
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const change = () => setReduced(media.matches);
    media.addEventListener("change", change);
    return () => {
      media.removeEventListener("change", change); element?.close();
      if (previous?.isConnected && previous !== document.body) previous.focus();
      else document.querySelector<HTMLTextAreaElement>('textarea[aria-label^="Message "]')?.focus();
    };
  }, []);

  useEffect(() => {
    if (reduced) { setPhase("reveal"); return; }
    if (phase === "reveal") return;
    const timer = window.setTimeout(() => setPhase(phase === "vortex" ? "impact" : "reveal"), phase === "vortex" ? 2200 : 650);
    return () => window.clearTimeout(timer);
  }, [phase, reduced]);

  return createPortal(<dialog ref={dialog} aria-label="Team Mog Score reveal" data-phase={phase}
    onCancel={(event) => { event.preventDefault(); onDismiss(); }}
    className="team-mog-dialog fixed inset-0 m-0 h-dvh max-h-none w-screen max-w-none border-0 bg-transparent p-0 text-white">
    <div className="team-mog-backdrop flex h-full items-center justify-center overflow-y-auto p-3 sm:p-6">
      <button onClick={onDismiss} aria-label="Dismiss team score" className="absolute top-4 right-4 z-20 rounded-full border border-emerald-200/30 bg-emerald-950/90 p-2 text-emerald-50 hover:bg-emerald-950 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-200"><X className="size-5" /></button>
      {phase !== "reveal" ? <div className="flex w-full max-w-lg flex-col items-center text-center">
        <p className="mb-2 text-xs font-semibold tracking-[0.3em] text-teal-200 uppercase">Match accepted</p>
        <h2 className="text-3xl font-bold sm:text-4xl">A match is igniting.</h2>
        <div aria-hidden="true" className={`team-mog-stage ${phase === "impact" ? "team-mog-impact" : ""}`}>
          <div className="team-mog-trail" /><div className="team-mog-trail team-mog-trail-inner" />
          <div className="team-mog-vortex">
            {team.members.map((member, index) => <div className={`team-mog-orbiter team-mog-orbiter-${index}`} key={member.id}>
              <div className="team-mog-face"><Avatar name={member.full_name} url={member.avatar_url} size="lg" /></div>
            </div>)}
          </div>
          {phase === "impact" && <div className="team-mog-explosion">
            <div className="team-mog-fireball" /><div className="team-mog-shockwave" />
            {Array.from({ length: 12 }, (_, i) => <span key={i} className="team-mog-spark" style={{ "--spark-angle": `${i * 30}deg` } as CSSProperties} />)}
          </div>}
        </div>
        <p className="text-lg font-semibold text-teal-100">{team.members.map((member) => member.full_name).join(" × ")}</p>
        <p role="status" className="mt-2 text-sm text-emerald-100/70">{phase === "impact" ? "Your combined potential just hit." : "Two profiles. One powerful team."}</p>
        <button onClick={() => setPhase("reveal")} className="mt-6 rounded-full border border-teal-200/30 bg-gradient-to-r from-emerald-400/15 to-cyan-300/15 px-5 py-2 text-sm text-teal-100 hover:bg-teal-500/10 focus-visible:outline-2 focus-visible:outline-teal-200">Skip animation</button>
      </div> : <article className="team-mog-card relative flex max-h-[calc(100dvh-1.5rem)] w-full max-w-xl flex-col overflow-hidden rounded-3xl border border-teal-200/30 bg-[#4b5057] text-slate-50 shadow-2xl shadow-emerald-400/10">
        <div className="min-h-0 overflow-y-auto px-5 pt-6 pb-4 sm:px-7">
          <header className="text-center">
            <p className="flex items-center justify-center gap-2 text-xs font-bold tracking-[0.2em] text-teal-200 uppercase"><Sparkles className="size-4" aria-hidden />Better together</p>
            <Flame aria-hidden="true" className="team-mog-score-fire mx-auto mt-3 size-20 text-emerald-600" fill={`url(#${flameGradient})`} stroke="#a7f3d0" strokeWidth={1.4}
              style={{ "--team-fire-peak": 1.14 + (team.score / team.max_score) * 0.12 } as CSSProperties}>
              <defs><linearGradient id={flameGradient} x1="0" y1="1" x2="1" y2="0"><stop stopColor="#34d399" /><stop offset="1" stopColor="#67e8f9" /></linearGradient></defs>
            </Flame>
            <h2 className="mt-2 text-sm font-bold tracking-[0.15em] text-teal-100 uppercase">Team Mog Score</h2>
            <output aria-label={`Team Mog Score: ${team.score} out of ${team.max_score}`} className="mt-1 block font-mono text-6xl font-black tracking-tight text-slate-50 sm:text-7xl">{team.score}<span className="text-xl font-medium text-teal-200/70">/{team.max_score}</span></output>
            <p className="mt-1 text-lg font-bold text-teal-200">{team.tier}</p>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-4">
              {team.members.map((member) => <div key={member.id} className="flex items-center gap-2 text-left">
                <Avatar name={member.full_name} url={member.avatar_url} />
                <div className="max-w-36"><p className="truncate text-sm font-bold">{member.full_name}</p><p className="text-xs text-slate-300">Mog {member.mog_score}/100</p></div>
              </div>)}
            </div>
          </header>
          <h3 className="mt-6 mb-3 text-sm font-bold text-slate-50">Why your team earned this score</h3>
          <ul aria-label="Team score breakdown" className="space-y-2">
            {team.breakdown.map((row) => <li key={row.key} className="rounded-xl border border-white/10 bg-black/15 p-3">
              <div className="flex items-center justify-between gap-3 text-sm font-bold"><span>{row.label}</span><span className="shrink-0 font-mono text-teal-200">+{row.points}<span className="text-xs font-normal text-slate-300">/{row.max}</span></span></div>
              <p className="mt-1 text-xs leading-relaxed text-slate-200">{row.reason}</p>
              <div aria-hidden="true" className="mt-2 h-1 overflow-hidden rounded-full bg-black/25"><div className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-300" style={{ width: `${(row.points / row.max) * 100}%` }} /></div>
            </li>)}
          </ul>
          <p className="mt-3 text-center text-[11px] text-slate-300">A playful profile-based score, captured when you matched. Grow your skills and build something together.</p>
        </div>
        <footer className="shrink-0 border-t border-white/10 bg-[#41464d] p-4">
          <button onClick={onContinue} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-300 px-5 py-3 text-sm font-bold text-emerald-950 shadow-lg shadow-emerald-950/10 hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-950"><MessageCircle className="size-4" aria-hidden />Start chatting</button>
        </footer>
      </article>}
    </div>
  </dialog>, document.body);
}
