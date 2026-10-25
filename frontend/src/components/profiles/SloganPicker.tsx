import { X } from "lucide-react";
import { useId, useState } from "react";
import { MAX_SLOGAN_LENGTH, MAX_SLOGANS, SLOGAN_PACKS, sameList } from "../../utils/theme";
import { chipClass } from "./chipClass";

interface SloganPickerProps {
  slogans: string[];
  onChange: (slogans: string[]) => void;
}

/** Edits the list of scrolling slogans: remove one, type a new one, or swap in a whole pack. */
export default function SloganPicker({ slogans, onChange }: SloganPickerProps) {
  const inputId = useId();
  const [draft, setDraft] = useState("");
  const full = slogans.length >= MAX_SLOGANS;
  const onlyOne = slogans.length === 1; // the server needs at least one, so the last can't be removed

  // Same tidying as the server: runs of spaces become one, and repeats (ignoring case) are skipped.
  const text = draft.split(/\s+/).filter(Boolean).join(" ");
  const repeat = slogans.some((slogan) => slogan.toLowerCase() === text.toLowerCase());
  const canAdd = text !== "" && !repeat && !full;
  const add = () => {
    if (!canAdd) return;
    onChange([...slogans, text]);
    setDraft("");
  };

  return (
    <div className="grid gap-3">
      <div>
        <span className="mb-1.5 flex items-baseline justify-between text-sm text-slate-300">
          Your slogans
          <span className="font-mono text-xs text-cyan-300">
            {slogans.length}/{MAX_SLOGANS}
          </span>
        </span>
        <ul className="flex flex-wrap gap-2">
          {slogans.map((slogan) => (
            <li
              key={slogan}
              className="inline-flex items-center gap-1 rounded-lg border border-line bg-surface-raised py-1 pl-3 pr-1 text-sm font-semibold"
            >
              {slogan}
              <button
                type="button"
                title={onlyOne ? "You need at least one slogan" : "Remove"}
                aria-label={`Remove ${slogan}`}
                disabled={onlyOne}
                onClick={() => onChange(slogans.filter((item) => item !== slogan))}
                className="grid size-6 place-items-center rounded-md text-muted transition hover:bg-rose-500/20 hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-muted"
              >
                <X aria-hidden className="size-3.5" />
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <label htmlFor={inputId} className="mb-1 block text-sm text-slate-300">
          Add your own
        </label>
        <div className="flex gap-2">
          <input
            id={inputId}
            type="text"
            className="field"
            value={draft}
            maxLength={MAX_SLOGAN_LENGTH}
            disabled={full}
            placeholder={full ? `That's the most you can have (${MAX_SLOGANS})` : "LIGHT WEIGHT BABY"}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              // This sits inside the edit form, where Enter would otherwise save the whole profile.
              if (e.key === "Enter") {
                e.preventDefault();
                add();
              }
            }}
          />
          <button type="button" disabled={!canAdd} onClick={add} className={`${chipClass(false)} shrink-0 disabled:opacity-40`}>
            Add
          </button>
        </div>
        <span className="mt-1 block text-xs text-muted">
          {repeat ? "That one is already on the list." : "Press Enter to add. Short and loud works best."}
        </span>
      </div>

      <div>
        <span className="mb-1.5 block text-sm text-slate-300">Or start from a pack</span>
        <div role="group" aria-label="Slogan packs" className="flex flex-wrap gap-2">
          {SLOGAN_PACKS.map((pack) => {
            const selected = sameList(pack.slogans, slogans);
            return (
              <button
                key={pack.name}
                type="button"
                title={pack.slogans.join(" · ")}
                aria-pressed={selected}
                onClick={() => onChange(pack.slogans)}
                className={chipClass(selected)}
              >
                {pack.name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
