import { Lightbulb } from "lucide-react";
import { type CSSProperties, useId } from "react";
import mascot from "../../assets/mog-mascot.png";
import chadLevels from "../../assets/chad-levels.png";
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
  const score = Number.isFinite(mog.score) ? Math.min(100, Math.max(0, mog.score)) : 0;
  const level = Math.max(1, Math.ceil(score / 20));
  // Pixel bounds in the 2172 × 457 neon artwork, excluding panel dividers.
  const artworkWidth = 2172;
  const artworkHeight = 457;
  const panels = [[0, 422], [426, 857], [860, 1308], [1311, 1744], [1747, 2172]];
  const [start, end] = panels[level - 1];
  const portraitWidth = end - start;
  const gradientId = useId();
  const flameStyle = {
    width: `${38 + score * 0.38}px`,
    "--mog-flame-peak": 1.05 + score * 0.0025,
    "--mog-flame-duration": `${2.4 - score * 0.01}s`,
  } as CSSProperties;

  return (
    <section className="rounded-2xl border border-amber-400/30 bg-surface p-6">
      <div className="mb-4 flex h-32 items-center justify-between gap-4">
        <img src={mascot} alt="Neon flame matchstick mascot" width={100} height={120}
          className="h-30 w-25 rounded-xl object-contain" />
        <div className="flex h-full w-28 shrink-0 items-center justify-center" aria-hidden="true">
          <svg viewBox="0 0 64 80" className="mog-score-flame" style={flameStyle}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="1" x2="0.7" y2="0">
                <stop stopColor="#22d3ee" />
                <stop offset="0.5" stopColor="#8b5cf6" />
                <stop offset="1" stopColor="#e879f9" />
              </linearGradient>
            </defs>
            <path fill={`url(#${gradientId})`} d="M34 2C40 23 56 26 53 44C59 41 60 35 59 31C72 59 57 78 32 78C7 78-4 58 6 39C8 50 13 51 15 48C9 29 30 24 34 2Z" />
            <path fill="#a5f3fc" d="M32 39C34 51 44 53 44 63C44 71 39 76 32 76C21 76 17 66 22 59C23 63 25 64 27 63C24 53 32 50 32 39Z" />
          </svg>
        </div>
      </div>
      <div className="grid grid-cols-[minmax(0,1fr)_7rem] items-center gap-x-3 gap-y-2">
        <h2 className="text-sm font-semibold tracking-wide text-amber-300 uppercase">Mog Score:</h2>
        <p className="text-center font-mono text-4xl font-bold text-amber-200">
          {mog.score}
          <span className="text-base text-muted">/100</span>
        </p>
        <div className="min-w-0 self-start">
          <p className="mt-1 text-xl font-bold">
            <span aria-hidden>{mog.emoji}</span> {mog.tier}
          </p>
          <p className="text-sm text-muted italic">{mog.roast}</p>
        </div>
        <div role="img" aria-label={`Chad level ${level} of 5`}
          className="w-full justify-self-center rounded-xl border border-violet-400/30 bg-no-repeat"
          style={{
            aspectRatio: `${portraitWidth} / ${artworkHeight}`,
            backgroundImage: `url(${chadLevels})`,
            backgroundSize: `${(artworkWidth / portraitWidth) * 100}% 100%`,
            backgroundPosition: `${(start / (artworkWidth - portraitWidth)) * 100}% center`,
          }} />
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
