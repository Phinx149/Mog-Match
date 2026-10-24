import { Bot, Code2, Heart, MapPin, X } from "lucide-react";
import { Link } from "react-router-dom";
import type { Profile, SwipeDecision } from "../../types/profile";
import Avatar from "./Avatar";
import SkillBadge from "./SkillBadge";

const MAX_SKILLS = 6;

interface ProfileCardProps {
  profile: Profile;
  activeSkills: string[];
  activeLookingFor: string[];
  onDecide: (profile: Profile, decision: SwipeDecision) => void;
}

export default function ProfileCard({ profile, activeSkills, activeLookingFor, onDecide }: ProfileCardProps) {
  const active = new Set(activeSkills.map((s) => s.toLowerCase()));
  const activeLooking = new Set(activeLookingFor.map((s) => s.toLowerCase()));
  const extraSkills = profile.skills.length - MAX_SKILLS;

  return (
    <article className="flex items-stretch gap-3 sm:gap-4">
      <DecisionButton kind="pass" onClick={() => onDecide(profile, "pass")} name={profile.full_name} />

      <div className="min-w-0 flex-1 rounded-2xl border border-line bg-surface p-5 transition-colors hover:border-violet-500/40">
        <Link to={`/profile/${profile.id}`} className="group flex items-center gap-4">
          <Avatar name={profile.full_name} url={profile.avatar_url} size="lg" />
          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold group-hover:text-violet-300">{profile.full_name}</h2>
            <p className="truncate font-mono text-xs text-cyan-300">@{profile.username}</p>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
              {profile.location && (
                <span className="inline-flex items-center gap-1">
                  <MapPin className="size-3" aria-hidden />
                  {profile.location}
                </span>
              )}
              {profile.experience_level && (
                <span className="rounded-full bg-surface-raised px-2 py-0.5 text-slate-300">
                  {profile.experience_level}
                </span>
              )}
            </p>
          </div>
        </Link>

        {profile.bio && <p className="mt-4 line-clamp-2 text-sm text-slate-300">{profile.bio}</p>}

        <div className="mt-4 flex flex-wrap gap-1.5">
          {profile.skills.slice(0, MAX_SKILLS).map((skill) => (
            <SkillBadge key={skill} label={skill} highlighted={active.has(skill.toLowerCase())} />
          ))}
          {extraSkills > 0 && <SkillBadge label={`+${extraSkills}`} variant="neutral" />}
        </div>

        {profile.looking_for.length > 0 && (
          <div className="mt-3 flex flex-wrap items-center gap-1.5 text-xs text-muted">
            <span>Looking for</span>
            {profile.looking_for.map((item) => (
              <SkillBadge key={item} label={item} variant="neutral" highlighted={activeLooking.has(item.toLowerCase())} />
            ))}
          </div>
        )}

        {(profile.favorite_ide || profile.favorite_ai_agents.length > 0) && (
          <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 border-t border-line pt-3 text-xs text-muted">
            {profile.favorite_ide && (
              <span className="inline-flex items-center gap-1.5">
                <Code2 className="size-3.5" aria-hidden />
                {profile.favorite_ide}
              </span>
            )}
            {profile.favorite_ai_agents.length > 0 && (
              <span className="inline-flex items-center gap-1.5">
                <Bot className="size-3.5" aria-hidden />
                {profile.favorite_ai_agents.join(", ")}
              </span>
            )}
          </div>
        )}
      </div>

      <DecisionButton kind="like" onClick={() => onDecide(profile, "like")} name={profile.full_name} />
    </article>
  );
}

function DecisionButton({ kind, onClick, name }: { kind: SwipeDecision; onClick: () => void; name: string }) {
  const isLike = kind === "like";
  const Icon = isLike ? Heart : X;
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`${isLike ? "Like" : "Pass on"} ${name}`}
      title={isLike ? "Like" : "Pass"}
      className={`flex w-12 shrink-0 items-center justify-center rounded-2xl border transition-colors sm:w-16 ${
        isLike
          ? "border-violet-500/30 bg-violet-500/10 text-violet-300 hover:bg-violet-500/25"
          : "border-line bg-surface text-muted hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-300"
      }`}
    >
      <Icon className="size-6" aria-hidden />
    </button>
  );
}
