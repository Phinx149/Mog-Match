import { Lightbulb } from "lucide-react";
import type { MogComponent, MogScore } from "../../types/profile";

const LABELS: Record<MogComponent, string> = {
  esoteric: "Language esotericness",
  breadth: "Skill breadth",
  links: "Links",
  projects: "Projects",
  descriptions: "Project descriptions",
  completeness: "Profile completeness",
  experience: "Experience",
  bio: "Bio",
};

interface MogScoreCardProps {
  mog: MogScore;
  /** Tips are only useful on your own profile. */
  showTips?: boolean;
}

export default function MogScoreCard({ mog, showTips }: MogScoreCardProps) {
  const components = Object.keys(LABELS) as MogComponent[];

  return (
    <section className="rounded-2xl border border-amber-400/30 bg-surface p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-amber-300 uppercase">Mog Score</h2>
          <p className="mt-1 text-xl font-bold">
            <span aria-hidden>{mog.emoji}</span> {mog.tier}
          </p>
          <p className="text-sm text-muted italic">{mog.roast}</p>
        </div>
        <p className="font-mono text-4xl font-bold text-amber-200">
          {mog.score}
          <span className="text-base text-muted">/100</span>
        </p>
      </div>

      <dl className="mt-5 grid gap-3">
        {components.map((key) => {
          const value = mog.breakdown[key];
          const max = mog.max_breakdown[key];
          return (
            <div key={key}>
              <dt className="flex justify-between text-xs text-slate-300">
                {LABELS[key]}
                <span className="font-mono text-muted">
                  {value}/{max}
                </span>
              </dt>
              <dd className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-raised">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-400 to-fuchsia-500"
                  style={{ width: `${max ? (value / max) * 100 : 0}%` }}
                />
              </dd>
            </div>
          );
        })}
      </dl>

      {showTips && mog.tips.length > 0 && (
        <ul className="mt-5 flex flex-col gap-2 border-t border-line pt-4 text-sm text-slate-300">
          {mog.tips.map((tip) => (
            <li key={tip} className="flex gap-2">
              <Lightbulb className="mt-0.5 size-4 shrink-0 text-amber-300" aria-hidden />
              {tip}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
