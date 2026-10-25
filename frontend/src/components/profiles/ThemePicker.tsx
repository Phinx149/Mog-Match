import { ArrowRight } from "lucide-react";
import { useId, type ReactNode } from "react";
import {
  EMOJI_PATHS,
  RAIN_SYMBOL_SETS,
  SLOGAN_STYLES,
  THEME_EFFECTS,
  type EffectOptions,
  type ProfileTheme,
  type ThemeEffect,
} from "../../types/profile";
import {
  BACKGROUND_SWATCHES,
  DEFAULT_BACKGROUND,
  EFFECT_INFO,
  EMOJI_PATH_INFO,
  EFFECT_OPTION_RANGES,
  isDarkEnough,
  RAIN_COLOR_SWATCHES,
  RAIN_SYMBOLS,
  sameTheme,
  SLOGAN_COLOR_SWATCHES,
  SLOGAN_STYLE_INFO,
  THEME_PRESETS,
} from "../../utils/theme";
import Avatar from "./Avatar";
import { chipClass } from "./chipClass";
import EmojiPicker from "./EmojiPicker";
import SkillBadge from "./SkillBadge";
import SloganPicker from "./SloganPicker";
import ThemeScope from "./ThemeScope";

/** Effects the picker offers, in order. `null` = no effect. */
const EFFECT_OPTIONS: { label: string; value: ThemeEffect | null }[] = [
  { label: "None", value: null },
  ...THEME_EFFECTS.map((value) => ({ label: EFFECT_INFO[value].label, value })),
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
  const { background, effect, effect_options: options } = theme;
  const setOption = (patch: Partial<EffectOptions>) => onChange({ ...theme, effect_options: { ...options, ...patch } });
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

        {effect && (
          <fieldset className="mt-3 grid gap-3 rounded-lg border border-line p-3 sm:grid-cols-2">
            <legend className="px-1 text-xs font-medium uppercase tracking-wide text-muted">
              {EFFECT_INFO[effect].tuneTitle}
            </legend>
            {EFFECT_INFO[effect].hasEmojiStyle && (
              <div className="sm:col-span-2">
                <EmojiPicker emojis={options.emojis} onChange={(emojis) => setOption({ emojis })} />
              </div>
            )}
            {EFFECT_INFO[effect].hasSloganStyle && (
              <div className="sm:col-span-2">
                <SloganPicker slogans={options.slogans} onChange={(slogans) => setOption({ slogans })} />
              </div>
            )}
            {EFFECT_INFO[effect].sliders.map((key) => {
              const { label, min, max, step, unit } = EFFECT_OPTION_RANGES[key];
              return (
                <RangeField
                  key={key}
                  label={key === "size" ? EFFECT_INFO[effect].sizeLabel : label}
                  value={options[key]}
                  display={describeOption(key, options[key], unit)}
                  {...{ min, max, step }}
                  onChange={(value) => setOption({ [key]: value })}
                />
              );
            })}
            {EFFECT_INFO[effect].hasEmojiStyle && (
              <div className="sm:col-span-2">
                <span className="mb-1.5 block text-sm text-slate-300">Path</span>
                <div role="group" aria-label="Emoji path" className="flex flex-wrap gap-2">
                  {EMOJI_PATHS.map((name) => (
                    <button
                      key={name}
                      type="button"
                      aria-pressed={options.emoji_path === name}
                      onClick={() => setOption({ emoji_path: name })}
                      className={chipClass(options.emoji_path === name)}
                    >
                      {EMOJI_PATH_INFO[name].label}
                    </button>
                  ))}
                </div>
                <span className="mt-1 block text-xs text-muted">{EMOJI_PATH_INFO[options.emoji_path].description}.</span>
              </div>
            )}
            {EFFECT_INFO[effect].hasRainStyle && (
              <>
                <div className="sm:col-span-2">
                  <span className="mb-1.5 block text-sm text-slate-300">Symbols</span>
                  <div role="group" aria-label="Rain symbols" className="flex flex-wrap gap-2">
                    {RAIN_SYMBOL_SETS.map((name) => (
                      <button
                        key={name}
                        type="button"
                        aria-pressed={options.rain_symbols === name}
                        onClick={() => setOption({ rain_symbols: name })}
                        className={chipClass(options.rain_symbols === name)}
                      >
                        {RAIN_SYMBOLS[name].label}
                        <span className="font-mono text-xs font-normal text-muted">{RAIN_SYMBOLS[name].sample}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="sm:col-span-2">
                  <span className="mb-1.5 block text-sm text-slate-300">Rain color</span>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                    {/* Picking any color leaves rainbow mode, since that's clearly what was meant. */}
                    <div role="group" aria-label="Rain color quick picks" className="flex flex-wrap gap-2">
                      {RAIN_COLOR_SWATCHES.map(({ name, hex }) => {
                        const selected = !options.rain_rainbow && options.rain_color.toLowerCase() === hex;
                        return (
                          <button
                            key={hex}
                            type="button"
                            title={name}
                            aria-label={name}
                            aria-pressed={selected}
                            onClick={() => setOption({ rain_color: hex, rain_rainbow: false })}
                            style={{ backgroundColor: hex }}
                            className={`size-7 rounded-full border border-white/20 transition ${
                              selected ? "ring-2 ring-cyan-400 ring-offset-2 ring-offset-surface" : "hover:scale-110"
                            }`}
                          />
                        );
                      })}
                    </div>
                    <input
                      type="color"
                      aria-label="Custom rain color"
                      className="h-8 w-12 cursor-pointer rounded-lg border border-line bg-canvas p-1"
                      value={options.rain_color}
                      onChange={(e) => setOption({ rain_color: e.target.value, rain_rainbow: false })}
                    />
                    <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        className="size-4 accent-cyan-400"
                        checked={options.rain_rainbow}
                        onChange={(e) => setOption({ rain_rainbow: e.target.checked })}
                      />
                      Rainbow
                    </label>
                  </div>
                </div>
              </>
            )}
            <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300 sm:col-span-2">
              <input
                type="checkbox"
                className="size-4 accent-cyan-400"
                checked={options.glow}
                onChange={(e) => setOption({ glow: e.target.checked })}
              />
              Neon glow <span className="text-xs text-muted">(a bright halo)</span>
            </label>
            {EFFECT_INFO[effect].hasSloganStyle && (
              <>
                <div className="sm:col-span-2">
                  <span className="mb-1.5 block text-sm text-slate-300">Letters</span>
                  <div role="group" aria-label="Slogan style" className="flex flex-wrap gap-2">
                    {SLOGAN_STYLES.map((name) => (
                      <button
                        key={name}
                        type="button"
                        aria-pressed={options.slogan_style === name}
                        onClick={() => setOption({ slogan_style: name })}
                        className={chipClass(options.slogan_style === name)}
                      >
                        {SLOGAN_STYLE_INFO[name].label}
                      </button>
                    ))}
                  </div>
                  <span className="mt-1 block text-xs text-muted">{SLOGAN_STYLE_INFO[options.slogan_style].description}.</span>
                </div>

                <div className="sm:col-span-2">
                  <span className="mb-1.5 block text-sm text-slate-300">Color</span>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                    <div role="group" aria-label="Slogan color quick picks" className="flex flex-wrap gap-2">
                      {SLOGAN_COLOR_SWATCHES.map(({ name, hex }) => {
                        const selected = options.slogan_color.toLowerCase() === hex;
                        return (
                          <button
                            key={hex}
                            type="button"
                            title={name}
                            aria-label={name}
                            aria-pressed={selected}
                            onClick={() => setOption({ slogan_color: hex })}
                            style={{ backgroundColor: hex }}
                            className={`size-7 rounded-full border border-white/20 transition ${
                              selected ? "ring-2 ring-cyan-400 ring-offset-2 ring-offset-surface" : "hover:scale-110"
                            }`}
                          />
                        );
                      })}
                    </div>
                    <input
                      type="color"
                      aria-label="Custom slogan color"
                      className="h-8 w-12 cursor-pointer rounded-lg border border-line bg-canvas p-1"
                      value={options.slogan_color}
                      onChange={(e) => setOption({ slogan_color: e.target.value })}
                    />
                  </div>
                </div>

                <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300 sm:col-span-2">
                  <input
                    type="checkbox"
                    className="size-4 accent-cyan-400"
                    checked={options.slogan_alternate}
                    onChange={(e) => setOption({ slogan_alternate: e.target.checked })}
                  />
                  Every other row goes the other way
                </label>
              </>
            )}
            {EFFECT_INFO[effect].hasLogoColor && (
              <div className="flex flex-wrap items-center gap-x-4 gap-y-2 sm:col-span-2">
                <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    className="size-4 accent-cyan-400"
                    checked={options.color_change}
                    onChange={(e) => setOption({ color_change: e.target.checked })}
                  />
                  Change color on every bounce
                </label>
                {/* A fixed color only matters while the color isn't changing. */}
                {!options.color_change && (
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    Logo color
                    <input
                      type="color"
                      className="h-8 w-12 cursor-pointer rounded-lg border border-line bg-canvas p-1"
                      value={options.color}
                      onChange={(e) => setOption({ color: e.target.value })}
                    />
                  </label>
                )}
              </div>
            )}
            {EFFECT_INFO[effect].hasLogoColor && (
              <p className="text-xs text-muted sm:col-span-2">
                Land a logo in a corner for a sparkle burst. Near misses count if they are close enough.
              </p>
            )}
            {options.brightness > 60 && (
              <p className="text-xs text-amber-300/90 sm:col-span-2">
                A bright effect behind text can make a card harder to read. Check the preview.
              </p>
            )}
          </fieldset>
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

/** What a slider's current value reads as: the direction gets an arrow, and the spin gets its turning direction. */
function describeOption(key: keyof typeof EFFECT_OPTION_RANGES, value: number, unit: string): ReactNode {
  if (key === "emoji_angle") {
    return (
      <span className="inline-flex items-center gap-1">
        <ArrowRight aria-hidden className="size-3.5" style={{ transform: `rotate(${value}deg)` }} />
        {value}
        {unit}
      </span>
    );
  }
  if (key === "emoji_spin") return value === 0 ? "none" : `${value > 0 ? "↻" : "↺"} ${Math.abs(value)}`;
  return `${value}${unit}`;
}

interface RangeFieldProps {
  label: string;
  value: number;
  /** The value as shown to people, e.g. "40%". */
  display: ReactNode;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

/** A labelled slider with its current value next to the label. */
function RangeField({ label, value, display, min, max, step, onChange }: RangeFieldProps) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="mb-1 flex items-baseline justify-between text-sm text-slate-300">
        {label}
        <output htmlFor={id} className="font-mono text-xs text-cyan-300">
          {display}
        </output>
      </label>
      <input
        id={id}
        type="range"
        className="block w-full cursor-pointer accent-cyan-400"
        {...{ min, max, step, value }}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
