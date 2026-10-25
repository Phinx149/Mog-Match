import { Check, ChevronDown, Search, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import type { FilterOptions, MogTier } from "../../types/profile";
import ToggleChips from "../forms/ToggleChips";
import MogFilter from "../mog/MogFilter";
import SkillBadge from "../profiles/SkillBadge";

interface FilterBarProps {
  options: FilterOptions;
  skills: string[];
  lookingFor: string[];
  minTier: MogTier | "";
  sortByMog: boolean;
  onSkillsChange: (skills: string[]) => void;
  onLookingForChange: (lookingFor: string[]) => void;
  onMinTierChange: (tier: MogTier | "") => void;
  onSortByMogChange: (value: boolean) => void;
}

/** Ignore case, spaces, dots and hyphens so "nodejs" finds "Node.js" (the same rule the backend catalog uses). */
const normalize = (text: string) => text.toLowerCase().replace(/[\s._-]+/g, "");

const has = (list: string[], value: string) => list.some((item) => item.toLowerCase() === value.toLowerCase());
const toggleIn = (list: string[], value: string) =>
  has(list, value) ? list.filter((item) => item.toLowerCase() !== value.toLowerCase()) : [...list, value];

export default function FilterBar({
  options,
  skills,
  lookingFor,
  minTier,
  sortByMog,
  onSkillsChange,
  onLookingForChange,
  onMinTierChange,
  onSortByMogChange,
}: FilterBarProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
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

  const matchingSkills = useMemo(() => {
    const needle = normalize(query);
    if (!needle) return options.skills;
    const hits = options.skills.filter((skill) => normalize(skill).includes(needle));
    // Names that start with the query come first, so "c" lists C, C++ and C# before Docker.
    const startsWith = (skill: string) => normalize(skill).startsWith(needle);
    return [...hits.filter(startsWith), ...hits.filter((skill) => !startsWith(skill))];
  }, [options.skills, query]);

  const toggleSkill = (skill: string) => onSkillsChange(toggleIn(skills, skill));
  const toggleLookingFor = (item: string) => onLookingForChange(toggleIn(lookingFor, item));

  // Enter in the search box picks the top result, then clears the box for the next search.
  const onSearchKeyDown = (event: ReactKeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    if (matchingSkills.length === 0) return;
    toggleSkill(matchingSkills[0]);
    setQuery("");
  };

  const activeCount = skills.length + lookingFor.length + (minTier ? 1 : 0) + (sortByMog ? 1 : 0);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <div ref={containerRef} className="relative">
        <button
          type="button"
          onClick={() => {
            setOpen((value) => !value);
            setQuery("");
          }}
          aria-expanded={open}
          className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3.5 py-1.5 text-sm text-slate-200 transition-colors hover:border-violet-500/50"
        >
          <SlidersHorizontal className="size-4 text-violet-300" aria-hidden />
          Filters
          {activeCount > 0 && (
            <span className="rounded-full bg-violet-600 px-1.5 text-xs font-semibold text-white">{activeCount}</span>
          )}
          <ChevronDown className={`size-4 text-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden />
        </button>

        {open && (
          <div className="absolute left-0 z-30 mt-2 w-72 rounded-xl border border-line bg-surface-raised p-3 shadow-2xl shadow-black/50 sm:w-80">
            <section className="mb-3">
              <h3 className="pb-2 text-xs font-medium tracking-wide text-muted uppercase">Mog score</h3>
              <MogFilter
                minTier={minTier}
                sortByMog={sortByMog}
                onMinTierChange={onMinTierChange}
                onSortByMogChange={onSortByMogChange}
              />
            </section>

            {options.looking_for.length > 0 && (
              <section className="mb-3">
                <h3 className="pb-2 text-xs font-medium tracking-wide text-muted uppercase">Looking for</h3>
                <ToggleChips label="Looking for" options={options.looking_for} selected={lookingFor} onChange={onLookingForChange} />
              </section>
            )}

            <section>
              <h3 className="pb-2 text-xs font-medium tracking-wide text-muted uppercase">Skills</h3>
              <label className="relative block">
                <span className="sr-only">Search skills</span>
                <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted" aria-hidden />
                <input
                  type="search"
                  autoFocus
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onKeyDown={onSearchKeyDown}
                  placeholder="Search skills…"
                  className="field pl-8 text-sm"
                />
              </label>

              <ul className="mt-2 max-h-56 overflow-y-auto">
                {options.skills.length === 0 && <li className="px-2 py-1 text-sm text-muted">No skills available.</li>}
                {options.skills.length > 0 && matchingSkills.length === 0 && (
                  <li className="px-2 py-1 text-sm text-muted">No skills match “{query.trim()}”.</li>
                )}
                {matchingSkills.map((skill) => {
                  const on = has(skills, skill);
                  return (
                    <li key={skill}>
                      <button
                        type="button"
                        onClick={() => toggleSkill(skill)}
                        aria-pressed={on}
                        className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm text-slate-200 hover:bg-white/5"
                      >
                        <span className="font-mono">{skill}</span>
                        {on && <Check className="size-4 text-cyan-300" aria-hidden />}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          </div>
        )}
      </div>

      {minTier && <SkillBadge label={`${minTier}+`} variant="neutral" highlighted onRemove={() => onMinTierChange("")} />}
      {sortByMog && (
        <SkillBadge label="Biggest moggers first" variant="neutral" highlighted onRemove={() => onSortByMogChange(false)} />
      )}
      {lookingFor.map((item) => (
        <SkillBadge key={`looking-${item}`} label={item} variant="neutral" highlighted onRemove={() => toggleLookingFor(item)} />
      ))}
      {skills.map((skill) => (
        <SkillBadge key={`skill-${skill}`} label={skill} highlighted onRemove={() => toggleSkill(skill)} />
      ))}
      {activeCount > 1 && (
        <button
          type="button"
          onClick={() => {
            onSkillsChange([]);
            onLookingForChange([]);
            onMinTierChange("");
            onSortByMogChange(false);
          }}
          className="text-xs text-muted underline-offset-2 hover:text-slate-200 hover:underline"
        >
          Clear all
        </button>
      )}
    </div>
  );
}
