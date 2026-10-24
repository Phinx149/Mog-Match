import { useId, useState, type KeyboardEvent } from "react";
import SkillBadge from "../profiles/SkillBadge";

interface TagInputProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  variant?: "skill" | "interest" | "neutral";
  maxTags?: number;
}

/** Chips plus a text box: Enter or comma adds a tag, Backspace on an empty box removes the last one. */
export default function TagInput({ label, values, onChange, placeholder, variant = "skill", maxTags }: TagInputProps) {
  const [draft, setDraft] = useState("");
  const inputId = useId();

  const add = (raw: string) => {
    const tag = raw.trim().slice(0, 40);
    if (!tag || values.some((v) => v.toLowerCase() === tag.toLowerCase())) return;
    if (maxTags && values.length >= maxTags) return;
    onChange([...values, tag]);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      add(draft);
      setDraft("");
    } else if (event.key === "Backspace" && !draft && values.length) {
      onChange(values.slice(0, -1));
    }
  };

  return (
    <div>
      <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-slate-300">
        {label}
      </label>
      <div className="flex flex-wrap items-center gap-1.5 rounded-lg border border-line bg-canvas p-2 focus-within:border-violet-500 focus-within:ring-2 focus-within:ring-violet-500/30">
        {values.map((value) => (
          <SkillBadge key={value} label={value} variant={variant} onRemove={() => onChange(values.filter((v) => v !== value))} />
        ))}
        <input
          id={inputId}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => {
            add(draft);
            setDraft("");
          }}
          placeholder={values.length ? "" : placeholder}
          className="min-w-24 flex-1 bg-transparent px-1 py-0.5 text-sm outline-none placeholder:text-muted"
        />
      </div>
      <p className="mt-1 text-xs text-muted">Press Enter or comma to add.</p>
    </div>
  );
}
