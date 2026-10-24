import { Check, ChevronDown, SlidersHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import SkillBadge from "../profiles/SkillBadge";

interface FilterBarProps {
  availableSkills: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export default function FilterBar({ availableSkills, selected, onChange }: FilterBarProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close the dropdown on outside click or Escape.
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => event.key === "Escape" && setOpen(false);
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const isSelected = (skill: string) => selected.some((s) => s.toLowerCase() === skill.toLowerCase());
  const toggle = (skill: string) =>
    onChange(isSelected(skill) ? selected.filter((s) => s.toLowerCase() !== skill.toLowerCase()) : [...selected, skill]);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <div ref={containerRef} className="relative">
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3.5 py-1.5 text-sm text-slate-200 transition-colors hover:border-violet-500/50"
        >
          <SlidersHorizontal className="size-4 text-violet-300" aria-hidden />
          Filters
          {selected.length > 0 && (
            <span className="rounded-full bg-violet-600 px-1.5 text-xs font-semibold text-white">{selected.length}</span>
          )}
          <ChevronDown className={`size-4 text-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden />
        </button>

        {open && (
          <div className="absolute left-0 z-30 mt-2 max-h-80 w-64 overflow-y-auto rounded-xl border border-line bg-surface-raised p-2 shadow-2xl shadow-black/50">
            <p className="px-2 pt-1 pb-2 text-xs font-medium tracking-wide text-muted uppercase">Skills</p>
            {availableSkills.length === 0 && <p className="px-2 py-1 text-sm text-muted">No skills loaded yet.</p>}
            {availableSkills.map((skill) => (
              <button
                key={skill}
                type="button"
                onClick={() => toggle(skill)}
                className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm text-slate-200 hover:bg-white/5"
              >
                <span className="font-mono">{skill}</span>
                {isSelected(skill) && <Check className="size-4 text-cyan-300" aria-hidden />}
              </button>
            ))}
          </div>
        )}
      </div>

      {selected.map((skill) => (
        <SkillBadge key={skill} label={skill} highlighted onRemove={() => toggle(skill)} />
      ))}
      {selected.length > 1 && (
        <button type="button" onClick={() => onChange([])} className="text-xs text-muted underline-offset-2 hover:text-slate-200 hover:underline">
          Clear all
        </button>
      )}
    </div>
  );
}
