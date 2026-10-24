import { Crown } from "lucide-react";
import type { MogTier } from "../../types/profile";

// Funny labels for each minimum tier.
const OPTIONS: { value: MogTier | ""; label: string }[] = [
  { value: "", label: "Anyone with a pulse" },
  { value: "Junior Mogger", label: "🐣 Knows what Git is" },
  { value: "Mid Mogger", label: "🧑‍💻 Mid Mogger or better" },
  { value: "Senior Mogger", label: "🔥 Seniors only, no juniors" },
  { value: "Gigamogger", label: "👑 Gigamoggers (good luck)" },
];

interface MogFilterProps {
  minTier: MogTier | "";
  sortByMog: boolean;
  onMinTierChange: (tier: MogTier | "") => void;
  onSortByMogChange: (value: boolean) => void;
}

export default function MogFilter({ minTier, sortByMog, onMinTierChange, onSortByMogChange }: MogFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <label className="inline-flex items-center gap-2 rounded-full border border-line bg-surface py-1 pr-1 pl-3 text-sm text-slate-200">
        <Crown className="size-4 text-amber-300" aria-hidden />
        <span className="sr-only">Minimum Mog tier</span>
        <select
          value={minTier}
          onChange={(event) => onMinTierChange(event.target.value as MogTier | "")}
          className="rounded-full bg-transparent py-0.5 pr-2 text-sm outline-none"
        >
          {OPTIONS.map((option) => (
            <option key={option.label} value={option.value} className="bg-surface-raised">
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        onClick={() => onSortByMogChange(!sortByMog)}
        aria-pressed={sortByMog}
        className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors ${
          sortByMog
            ? "border-amber-400/50 bg-amber-400/15 text-amber-200"
            : "border-line bg-surface text-slate-200 hover:border-amber-400/50"
        }`}
      >
        Biggest moggers first
      </button>
    </div>
  );
}
