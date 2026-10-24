import { Check } from "lucide-react";

interface ToggleChipsProps {
  /** Accessible name for the group, e.g. "Looking for". */
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

/** A row of pills where each one switches on/off. Use it when the allowed values are a fixed list. */
export default function ToggleChips({ label, options, selected, onChange }: ToggleChipsProps) {
  const toggle = (option: string) =>
    onChange(selected.includes(option) ? selected.filter((item) => item !== option) : [...selected, option]);

  return (
    <div role="group" aria-label={label} className="flex flex-wrap gap-1.5">
      {options.map((option) => {
        const on = selected.includes(option);
        return (
          <button
            key={option}
            type="button"
            onClick={() => toggle(option)}
            aria-pressed={on}
            className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs transition-colors ${
              on
                ? "border-violet-500/60 bg-violet-500/20 text-violet-100"
                : "border-line text-slate-300 hover:border-violet-500/40"
            }`}
          >
            {on && <Check className="size-3" aria-hidden />}
            {option}
          </button>
        );
      })}
    </div>
  );
}
