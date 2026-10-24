import { X } from "lucide-react";

const VARIANTS = {
  skill: "border-cyan-500/30 bg-cyan-500/10 text-cyan-200 font-mono",
  interest: "border-violet-500/30 bg-violet-500/10 text-violet-200",
  neutral: "border-line bg-surface-raised text-slate-300",
};

interface SkillBadgeProps {
  label: string;
  variant?: keyof typeof VARIANTS;
  /** Emphasize the badge, e.g. when it matches an active filter. */
  highlighted?: boolean;
  onRemove?: () => void;
}

export default function SkillBadge({ label, variant = "skill", highlighted, onRemove }: SkillBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs ${VARIANTS[variant]} ${
        highlighted ? "ring-2 ring-cyan-400/60" : ""
      }`}
    >
      {label}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label={`Remove ${label}`}
          className="-mr-1 rounded-full p-0.5 opacity-70 transition hover:bg-white/10 hover:opacity-100"
        >
          <X className="size-3" aria-hidden />
        </button>
      )}
    </span>
  );
}
