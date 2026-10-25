import { ArrowRight, ChevronDown, SlidersHorizontal } from "lucide-react";
import { useId, useState, type ReactNode } from "react";
import {
  CHART_MOODS,
  CHART_PALETTES,
  EMOJI_PATHS,
  MONEY_KINDS,
  RAIN_SYMBOL_SETS,
  SLOGAN_STYLES,
  SNOW_KINDS,
  THEME_EFFECTS,
  type EffectOptions,
  type ProfileTheme,
  type ThemeEffect,
} from "../../types/profile";
import {
  BACKGROUND_SWATCHES,
  CHART_MOOD_INFO,
  CHART_PALETTE_INFO,
  DEFAULT_BACKGROUND,
  EFFECT_INFO,
  EMOJI_PATH_INFO,
  EFFECT_OPTION_RANGES,
  isDarkEnough,
  LIGHTNING_COLOR_SWATCHES,
  MONEY_KIND_INFO,
  RAIN_COLOR_SWATCHES,
  RAIN_SYMBOLS,
  sameTheme,
  SLOGAN_COLOR_SWATCHES,
  SLOGAN_STYLE_INFO,
  SNOW_KIND_INFO,
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

/** Controlled picker for a profile's look: a background color, an animated effect (with its presets and tuning), and a live preview. */
export default function ThemePicker({ theme, onChange, error, effectError, preview }: ThemePickerProps) {
  const inputId = useId();
  const [tuneOpen, setTuneOpen] = useState(false);
  const { background, effect, effect_options: options } = theme;
  // Presets live with the effect they use, so only that effect's are offered.
  const presets = effect ? THEME_PRESETS.filter((preset) => preset.theme.effect === effect) : [];
  const setOption = (patch: Partial<EffectOptions>) => onChange({ ...theme, effect_options: { ...options, ...patch } });
  // Warn right away; the server re-checks on save and is the one that actually enforces it.
  const message =
    background !== null && !isDarkEnough(background)
      ? "That color is too light for the text. Pick a darker one."
      : error;

  return (
    <>
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
          <div className="mt-3 rounded-lg border border-line">
            <button
              type="button"
              aria-expanded={tuneOpen}
              onClick={() => setTuneOpen((open) => !open)}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-200 transition-colors hover:text-cyan-200"
            >
              <SlidersHorizontal className="size-4 text-cyan-300" aria-hidden />
              {EFFECT_INFO[effect].tuneTitle}
              <span className="text-xs font-normal text-muted">
                {presets.length} {presets.length === 1 ? "preset" : "presets"} and settings
              </span>
              <ChevronDown className={`ml-auto size-4 text-muted transition-transform ${tuneOpen ? "rotate-180" : ""}`} aria-hidden />
            </button>

            {tuneOpen && (
              <fieldset className="grid gap-3 border-t border-line p-3 sm:grid-cols-2">
                <legend className="sr-only">{EFFECT_INFO[effect].tuneTitle}</legend>
                <div className="sm:col-span-2">
                  <span className="mb-1.5 block text-sm text-slate-300">Presets</span>
                  <div role="group" aria-label={`${EFFECT_INFO[effect].label} presets`} className="flex flex-wrap gap-2">
                    {presets.map((preset) => {
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
                {EFFECT_INFO[effect].sliders
                  // Weight is only about coins, so it has no use while bills are all that falls.
                  .filter((key) => key !== "money_weight" || options.money_kind !== "bills")
                  .map((key) => {
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
                {EFFECT_INFO[effect].hasMoneyStyle && (
                  <div className="sm:col-span-2">
                    <span className="mb-1.5 block text-sm text-slate-300">Cash</span>
                    <div role="group" aria-label="Kind of cash" className="flex flex-wrap gap-2">
                      {MONEY_KINDS.map((name) => (
                        <button
                          key={name}
                          type="button"
                          aria-pressed={options.money_kind === name}
                          onClick={() => setOption({ money_kind: name })}
                          className={chipClass(options.money_kind === name)}
                        >
                          {MONEY_KIND_INFO[name].label}
                        </button>
                      ))}
                    </div>
                    <span className="mt-1 block text-xs text-muted">{MONEY_KIND_INFO[options.money_kind].description}.</span>
                  </div>
                )}
                {EFFECT_INFO[effect].hasSnowStyle && (
                  <div className="sm:col-span-2">
                    <span className="mb-1.5 block text-sm text-slate-300">Flakes</span>
                    <div role="group" aria-label="Kind of snowflake" className="flex flex-wrap gap-2">
                      {SNOW_KINDS.map((name) => (
                        <button
                          key={name}
                          type="button"
                          aria-pressed={options.snow_kind === name}
                          onClick={() => setOption({ snow_kind: name })}
                          className={chipClass(options.snow_kind === name)}
                        >
                          {SNOW_KIND_INFO[name].label}
                        </button>
                      ))}
                    </div>
                    <span className="mt-1 block text-xs text-muted">{SNOW_KIND_INFO[options.snow_kind].description}.</span>
                  </div>
                )}
                {EFFECT_INFO[effect].hasLightningStyle && (
                  <>
                    <div className="sm:col-span-2">
                      <span className="mb-1.5 block text-sm text-slate-300">Bolt color</span>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                        <div role="group" aria-label="Bolt color quick picks" className="flex flex-wrap gap-2">
                          {LIGHTNING_COLOR_SWATCHES.map(({ name, hex }) => {
                            const selected = options.lightning_color.toLowerCase() === hex;
                            return (
                              <button
                                key={hex}
                                type="button"
                                title={name}
                                aria-label={name}
                                aria-pressed={selected}
                                onClick={() => setOption({ lightning_color: hex })}
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
                          aria-label="Custom bolt color"
                          className="h-8 w-12 cursor-pointer rounded-lg border border-line bg-canvas p-1"
                          value={options.lightning_color}
                          onChange={(e) => setOption({ lightning_color: e.target.value })}
                        />
                      </div>
                      <span className="mt-1 block text-xs text-muted">The glow around each bolt. The bolt itself is always white-hot.</span>
                    </div>

                    <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300 sm:col-span-2">
                      <input
                        type="checkbox"
                        className="size-4 accent-cyan-400"
                        checked={options.lightning_flash}
                        onChange={(e) => setOption({ lightning_flash: e.target.checked })}
                      />
                      Light up the sky <span className="text-xs text-muted">(a soft flash of color with each strike)</span>
                    </label>
                    <p className="text-xs text-muted sm:col-span-2">
                      Strikes are always at least a second apart and flash at most twice, so the storm never strobes.
                    </p>
                  </>
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
                {EFFECT_INFO[effect].hasMarketStyle && (
                  <>
                    <div className="sm:col-span-2">
                      <span className="mb-1.5 block text-sm text-slate-300">Market mood</span>
                      <div role="group" aria-label="Market mood" className="flex flex-wrap gap-2">
                        {CHART_MOODS.map((name) => (
                          <button
                            key={name}
                            type="button"
                            aria-pressed={options.chart_mood === name}
                            onClick={() => setOption({ chart_mood: name })}
                            className={chipClass(options.chart_mood === name)}
                          >
                            {CHART_MOOD_INFO[name].label}
                          </button>
                        ))}
                      </div>
                      <span className="mt-1 block text-xs text-muted">{CHART_MOOD_INFO[options.chart_mood].description}.</span>
                    </div>

                    <div className="sm:col-span-2">
                      <span className="mb-1.5 block text-sm text-slate-300">Candle colors</span>
                      <div role="group" aria-label="Candle colors" className="flex flex-wrap gap-2">
                        {CHART_PALETTES.map((name) => (
                          <button
                            key={name}
                            type="button"
                            aria-pressed={options.chart_palette === name}
                            onClick={() => setOption({ chart_palette: name })}
                            className={chipClass(options.chart_palette === name)}
                          >
                            <span aria-hidden className="flex gap-0.5">
                              <span className="size-3 rounded-sm" style={{ backgroundColor: CHART_PALETTE_INFO[name].up }} />
                              <span className="size-3 rounded-sm" style={{ backgroundColor: CHART_PALETTE_INFO[name].down }} />
                            </span>
                            {CHART_PALETTE_INFO[name].label}
                          </button>
                        ))}
                      </div>
                      {options.chart_palette === "swapped" && (
                        <span className="mt-1 block text-xs text-muted">Red up and green down, the way East Asian markets show it.</span>
                      )}
                    </div>

                    <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300 sm:col-span-2">
                      <input
                        type="checkbox"
                        className="size-4 accent-cyan-400"
                        checked={options.chart_label}
                        onChange={(e) => setOption({ chart_label: e.target.checked })}
                      />
                      Show the ticker and price <span className="text-xs text-muted">(and the price tag on the right)</span>
                    </label>
                    {options.chart_label && (
                      <TickerField value={options.chart_ticker} onChange={(chart_ticker) => setOption({ chart_ticker })} />
                    )}
                    <p className="text-xs text-muted sm:col-span-2">
                      Everything on the chart is made up, and it is not financial advice. Pumps and crashes throw up popups now and then.
                    </p>
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

/** The made-up stock's symbol. Typing is cleaned as it goes (letters and numbers, uppercase), and it can't be left empty. */
function TickerField({ value, onChange }: { value: string; onChange: (ticker: string) => void }) {
  const id = useId();
  // Kept separately so the box can be emptied while retyping; only a non-empty symbol is passed up.
  const [draft, setDraft] = useState(value);
  return (
    <div className="sm:col-span-2">
      <label htmlFor={id} className="mb-1 block text-sm text-slate-300">
        Ticker symbol
      </label>
      <input
        id={id}
        type="text"
        className="field w-40 font-mono uppercase"
        value={draft}
        maxLength={8}
        spellCheck={false}
        autoComplete="off"
        onChange={(e) => {
          const ticker = e.target.value.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
          setDraft(ticker);
          if (ticker) onChange(ticker);
        }}
        onBlur={() => setDraft(value)}
      />
      <span className="mt-1 block text-xs text-muted">Up to 8 letters or numbers, like MOG or GIGA42.</span>
    </div>
  );
}

/** What a slider's current value reads as: the direction gets an arrow, and the spin and snow wind get their turning or blowing direction. */
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
  if (key === "money_wind") return value === 0 ? "calm" : value;
  if (key === "lightning_forks") return value === 0 ? "none" : value;
  if (key === "snow_wind") return value === 0 ? "calm" : `${value < 0 ? "←" : "→"} ${Math.abs(value)}`;
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
