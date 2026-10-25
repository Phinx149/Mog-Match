import { X } from "lucide-react";
import { useId } from "react";
import { EMOJI_PACKS, MAX_EMOJIS, parseEmojis, sameList } from "../../utils/theme";
import { chipClass } from "./chipClass";

interface EmojiPickerProps {
  emojis: string[];
  onChange: (emojis: string[]) => void;
}

/** Edits the list of floating emoji: remove one, type or paste more, or swap in a whole pack. */
export default function EmojiPicker({ emojis, onChange }: EmojiPickerProps) {
  const inputId = useId();
  const full = emojis.length >= MAX_EMOJIS;
  const onlyOne = emojis.length === 1; // the server needs at least one, so the last can't be removed

  const add = (text: string) => {
    const added = parseEmojis(text).filter((emoji) => !emojis.includes(emoji));
    if (added.length > 0) onChange([...emojis, ...added].slice(0, MAX_EMOJIS));
  };

  return (
    <div className="grid gap-3">
      <div>
        <span className="mb-1.5 flex items-baseline justify-between text-sm text-slate-300">
          Your emoji
          <span className="font-mono text-xs text-cyan-300">
            {emojis.length}/{MAX_EMOJIS}
          </span>
        </span>
        <ul className="flex flex-wrap gap-2">
          {emojis.map((emoji) => (
            <li key={emoji}>
              <button
                type="button"
                title={onlyOne ? "You need at least one emoji" : "Click to remove"}
                aria-label={`Remove ${emoji}`}
                disabled={onlyOne}
                onClick={() => onChange(emojis.filter((item) => item !== emoji))}
                className="group relative grid size-10 place-items-center rounded-lg border border-line bg-surface-raised text-xl transition hover:border-rose-400/60 disabled:cursor-not-allowed"
              >
                {emoji}
                {!onlyOne && (
                  <X
                    aria-hidden
                    className="absolute -right-1.5 -top-1.5 size-4 rounded-full bg-rose-500 p-0.5 text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100"
                  />
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <label htmlFor={inputId} className="mb-1 block text-sm text-slate-300">
          Add your own
        </label>
        {/* The box stays empty: whatever is typed or pasted is turned into emoji chips above (and other characters are dropped). */}
        <input
          id={inputId}
          type="text"
          className="field"
          value=""
          disabled={full}
          placeholder={full ? `That's the most you can have (${MAX_EMOJIS})` : "Type or paste emoji here"}
          onChange={(e) => add(e.target.value)}
        />
        <span className="mt-1 block text-xs text-muted">
          Open your emoji keyboard with Ctrl+Cmd+Space on a Mac or Win+. on Windows.
        </span>
      </div>

      <div>
        <span className="mb-1.5 block text-sm text-slate-300">Or start from a pack</span>
        <div role="group" aria-label="Emoji packs" className="flex flex-wrap gap-2">
          {EMOJI_PACKS.map(({ name, emojis: packEmojis }) => {
            const selected = sameList(packEmojis, emojis);
            return (
              <button
                key={name}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(packEmojis)}
                className={chipClass(selected)}
              >
                {name}
                <span aria-hidden className="text-xs font-normal">
                  {packEmojis.slice(0, 4).join("")}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
