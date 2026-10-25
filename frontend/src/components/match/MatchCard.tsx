import { HeartOff, MapPin } from "lucide-react";
import { Link } from "react-router-dom";
import type { MatchComponent, MatchedProfile } from "../../types/profile";
import MogBadge from "../mog/MogBadge";
import Avatar from "../profiles/Avatar";
import SkillBadge from "../profiles/SkillBadge";

const LABELS: Record<MatchComponent, string> = {
  skills: "Tech stack",
  interests: "Interests",
  looking_for: "Goals",
  experience: "Experience",
  ai_agents: "AI agents",
  ide: "IDE",
  location: "Location",
};

const plural = (count: number, word: string) => `${count} shared ${word}${count === 1 ? "" : "s"}`;

/** A plain-English sentence for what a component found, or null when it found nothing. */
function explain(key: MatchComponent, profile: MatchedProfile): string | null {
  const { match } = profile;
  const points = match.breakdown[key];
  if (points === 0) return null;
  switch (key) {
    case "skills":
      return `${plural(match.shared.skills.length, "skill")}: ${match.shared.skills.join(", ")}`;
    case "interests":
      return `${plural(match.shared.interests.length, "interest")}: ${match.shared.interests.join(", ")}`;
    case "looking_for":
      return `Goals that line up: ${match.shared.looking_for.join(", ")}`;
    case "experience":
      return points === match.max_breakdown.experience
        ? `Same experience level (${profile.experience_level})`
        : `Close in experience (they're ${profile.experience_level})`;
    case "ai_agents":
      return `You both use ${match.shared.ai_agents.join(" and ")}`;
    case "ide":
      return `You both code in ${profile.favorite_ide}`;
    case "location":
      return `You're both in ${profile.location}`;
  }
}

interface MatchCardProps {
  profile: MatchedProfile;
  rank: number;
  onUnlike: (profile: MatchedProfile) => void;
}

export default function MatchCard({ profile, rank, onUnlike }: MatchCardProps) {
  const { match } = profile;
  const components = Object.keys(LABELS) as MatchComponent[];
  const reasons = components
    .map((key) => ({ key, text: explain(key, profile), points: match.breakdown[key] }))
    .filter((reason): reason is { key: MatchComponent; text: string; points: number } => reason.text !== null)
    .sort((a, b) => b.points - a.points);
  const missing = components.filter((key) => match.breakdown[key] === 0).map((key) => LABELS[key]);
  const sharesNothing = !match.shared.skills.length && !match.shared.interests.length && !match.shared.looking_for.length;

  return (
    <article className="rounded-2xl border border-line bg-surface p-5 transition-colors hover:border-violet-500/40">
      <Link to={`/profile/${profile.id}`} className="group flex items-center gap-4">
        <span className="w-6 shrink-0 text-center font-mono text-sm text-muted">#{rank}</span>
        <Avatar name={profile.full_name} url={profile.avatar_url} size="md" />
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-lg font-semibold group-hover:text-violet-300">{profile.full_name}</h2>
          <p className="truncate font-mono text-xs text-cyan-300">@{profile.username}</p>
          <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
            {profile.location && (
              <span className="inline-flex items-center gap-1">
                <MapPin className="size-3" aria-hidden />
                {profile.location}
              </span>
            )}
            <MogBadge mog={profile.mog} />
          </p>
        </div>
        <div className="shrink-0 text-right">
          <p className="font-mono text-3xl font-bold text-violet-200">
            {match.score}
            <span className="text-sm text-muted">%</span>
          </p>
          <p className="text-xs font-medium text-violet-300">similar to you</p>
          <p className="text-xs text-muted italic">{match.label}</p>
        </div>
      </Link>

      <div className="mt-4 flex flex-col gap-2 text-xs text-muted">
        {sharesNothing && <p>No shared skills, interests or goals. Opposites attract?</p>}
        <SharedRow label="Both know" items={match.shared.skills} variant="skill" />
        <SharedRow label="Both into" items={match.shared.interests} variant="interest" />
        <SharedRow label="Both want" items={match.shared.looking_for} variant="neutral" />
      </div>

      <details className="mt-4 border-t border-line pt-3">
        <summary className="cursor-pointer text-xs text-muted hover:text-slate-200">
          Why you're {match.score}% similar
        </summary>
        <p className="mt-3 text-xs text-muted">
          The more you have in common, the higher the score. Shared tech and interests count the most.
        </p>
        {reasons.length > 0 && (
          <ul className="mt-3 flex flex-col gap-2.5">
            {reasons.map(({ key, text, points }) => (
              <li key={key}>
                <div className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="text-slate-200">{text}</span>
                  <span className="shrink-0 font-mono text-xs text-violet-300">+{points}%</span>
                </div>
                <div className="mt-1 h-1 overflow-hidden rounded-full bg-surface-raised">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 to-cyan-400"
                    style={{ width: `${(points / match.max_breakdown[key]) * 100}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
        {missing.length > 0 && (
          <p className="mt-3 text-xs text-muted">Nothing in common yet: {missing.join(", ")}.</p>
        )}
      </details>

      <div className="mt-3 flex justify-end">
        <button
          type="button"
          onClick={() => onUnlike(profile)}
          aria-label={`Unlike ${profile.full_name}`}
          title="Remove from your matches and show them on Discover again"
          className="inline-flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-xs text-muted transition-colors hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-300"
        >
          <HeartOff className="size-3.5" aria-hidden />
          Unlike
        </button>
      </div>
    </article>
  );
}

function SharedRow({ label, items, variant }: { label: string; items: string[]; variant: "skill" | "interest" | "neutral" }) {
  if (items.length === 0) return null;
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span>{label}</span>
      {items.map((item) => (
        <SkillBadge key={item} label={item} variant={variant} />
      ))}
    </div>
  );
}
