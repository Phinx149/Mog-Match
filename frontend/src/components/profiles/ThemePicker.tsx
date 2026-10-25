import { useId } from "react";
import type { ProfileTheme, ThemeEffect } from "../../types/profile";
import { BACKGROUND_SWATCHES, DEFAULT_BACKGROUND, isDarkEnough, sameTheme, THEME_PRESETS } from "../../utils/theme";
import Avatar from "./Avatar";
import SkillBadge from "./SkillBadge";
import ThemeScope from "./ThemeScope";

/** Effects the picker offers, in order. `null` = no effect. */
const EFFECT_OPTIONS: { label: string; value: ThemeEffect | null }[] = [
  { label: "None", value: null },
  { label: "Matrix rain", value: "matrix" },
];

interface ThemePickerProps {
  theme: ProfileTheme;
  onChange: (theme: ProfileTheme) => void;
  /** Errors from the server for `theme.background` / `theme.effect`; the background one shows when the color itself looks fine. */
  error?: string;
  effectError?: string;
  /** What the preview card shows; pass the form's current values so it updates as you type. */
  preview: { name: string; username: string; avatarUrl: string | null; skills: string[] };
}

/** Controlled picker for a profile's look: presets, a background color, an animated effect, and a live preview. */
export default function ThemePicker({ theme, onChange, error, effectError, preview }: ThemePickerProps) {
  const inputId = useId();
  const { background, effect } = theme;
  // Warn right away; the server re-checks on save and is the one that actually enforces it.
  const message =
    background !== null && !isDarkEnough(background)
      ? "That color is too light for the text. Pick a darker one."
      : error;

  return (
    <>
      <div>
        <span className="mb-1.5 block text-sm font-medium text-slate-300">Presets</span>
        <div role="group" aria-label="Theme presets" className="flex flex-wrap gap-2">
          {THEME_PRESETS.map((preset) => {
            const selected = sameTheme(theme, preset.theme);
            return (
              <button
                key={preset.name}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(preset.theme)}
                className={chipClass(selected)}
              >
                <span
                  aria-hidden
                  style={{ backgroundColor: preset.theme.background ?? DEFAULT_BACKGROUND }}
                  className="size-3 rounded-full border border-white/20"
                />
                {preset.name}
                <span className="text-xs font-normal text-muted">{preset.description}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <span className="mb-1.5 block text-sm font-medium text-slate-300">Card background</span>
        <div role="group" aria-label="Card background quick picks" className="flex flex-wrap gap-2">
          {BACKGROUND_SWATCHES.map(({ name, hex }) => {
            const selected = background?.toLowerCase() === hex;
            return (
              <button
                key={hex}
                type="button"
                title={name}
                aria-label={name}
                aria-pressed={selected}
                onClick={() => onChange({ ...theme, background: hex })}
                style={{ backgroundColor: hex }}
                className={`size-8 rounded-full border border-white/20 transition ${
                  selected ? "ring-2 ring-cyan-400 ring-offset-2 ring-offset-surface" : "hover:scale-110"
                }`}
              />
            );
          })}
        </div>
      </div>

      <div>
        <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-slate-300">
          Custom color
        </label>
        <input
          id={inputId}
          type="color"
          className="h-10 w-16 cursor-pointer rounded-lg border border-line bg-canvas p-1"
          value={background ?? DEFAULT_BACKGROUND}
          aria-invalid={!!message}
          aria-describedby={`${inputId}-help`}
          onChange={(e) => onChange({ ...theme, background: e.target.value })}
        />
        <div id={`${inputId}-help`}>
          {message ? (
            <span className="mt-1 block text-xs text-rose-300">{message}</span>
          ) : (
            <span className="mt-1 block text-xs text-muted">Dark colors only, so the text stays readable.</span>
          )}
        </div>
      </div>

      <div>
        <span className="mb-1.5 block text-sm font-medium text-slate-300">Animated effect</span>
        <div role="group" aria-label="Animated effect" className="flex flex-wrap gap-2">
          {EFFECT_OPTIONS.map(({ label, value }) => (
            <button
              key={label}
              type="button"
              aria-pressed={effect === value}
              onClick={() => onChange({ ...theme, effect: value })}
              className={chipClass(effect === value)}
            >
              {label}
            </button>
          ))}
        </div>
        {effectError ? (
          <span className="mt-1 block text-xs text-rose-300">{effectError}</span>
        ) : (
          <span className="mt-1 block text-xs text-muted">Plays behind your card. Viewers who prefer reduced motion see a still frame instead.</span>
        )}
      </div>

      <div>
        <span className="mb-1.5 block text-sm font-medium text-slate-300">Preview</span>
        <ThemeScope theme={theme} className="flex flex-col gap-3 rounded-2xl border border-line bg-surface p-5">
          <div className="flex items-center gap-4">
            <Avatar name={preview.name || "You"} url={preview.avatarUrl} size="lg" />
            <div className="min-w-0">
              <p className="truncate text-lg font-semibold">{preview.name || "Your name"}</p>
              <p className="truncate font-mono text-xs text-cyan-300">@{preview.username || "username"}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {preview.skills.slice(0, 4).map((skill) => (
              <SkillBadge key={skill} label={skill} />
            ))}
            <SkillBadge label="Looking for a team" variant="neutral" />
          </div>
          <p className="rounded-lg border border-line bg-surface-raised px-3 py-2 text-xs text-muted">
            This is how your card looks on Discover and on your profile.
          </p>
        </ThemeScope>
      </div>
    </>
  );
}

/** Look shared by the preset and effect buttons. */
function chipClass(selected: boolean): string {
  return `inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
    selected
      ? "border-cyan-400 bg-cyan-400/10 text-cyan-200"
      : "border-line text-slate-200 hover:border-cyan-500/50 hover:text-cyan-200"
  }`;
}
