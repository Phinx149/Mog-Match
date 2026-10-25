import type { EffectOptions, ProfileTheme, RainSymbols, ThemeEffect } from "../types/profile";

// Helpers for profile themes. The backend is the authority on what's allowed
// (backend/app/services/profile_service.py `_clean_theme`); these let the edit form warn
// before saving and let ThemeScope refuse anything that isn't a plain #rrggbb color.

export const HEX_COLOR = /^#[0-9a-f]{6}$/i;

/** The card color when a profile hasn't picked one (`--color-surface` in index.css). */
export const DEFAULT_BACKGROUND = "#131724";

/** WCAG relative luminance, 0 (black) to 1 (white). Keep in sync with MAX_BACKGROUND_LUMINANCE in the backend. */
const MAX_BACKGROUND_LUMINANCE = 0.05;

/** Quick picks for the edit form. All are dark enough to pass `isDarkEnough`. */
export const BACKGROUND_SWATCHES = [
  { name: "Slate", hex: "#0f172a" },
  { name: "Navy", hex: "#172554" },
  { name: "Indigo", hex: "#312e81" },
  { name: "Violet", hex: "#4c1d95" },
  { name: "Plum", hex: "#4a044e" },
  { name: "Rose", hex: "#4c0519" },
  { name: "Rust", hex: "#431407" },
  { name: "Forest", hex: "#052e16" },
  { name: "Teal", hex: "#042f2e" },
  { name: "Ocean", hex: "#083344" },
] as const;

/** What the server uses for options a profile hasn't set. Keep in sync with DEFAULT_EFFECT_OPTIONS in the backend. */
export const DEFAULT_EFFECT_OPTIONS: EffectOptions = {
  brightness: 40,
  size: 14,
  speed: 4,
  glow: false,
  count: 1,
  color_change: true,
  color: "#ffffff",
  rain_color: "#22ff66",
  rain_rainbow: false,
  rain_symbols: "katakana",
};

/** The theme of a profile that hasn't customized anything. */
export const DEFAULT_THEME: ProfileTheme = { background: null, effect: null, effect_options: DEFAULT_EFFECT_OPTIONS };

/** The sliders' limits; the backend enforces the same ones (EFFECT_OPTION_RANGES). */
export const EFFECT_OPTION_RANGES = {
  brightness: { label: "Brightness", min: 10, max: 100, step: 5, unit: "%" },
  size: { label: "Text size", min: 10, max: 48, step: 2, unit: "px" },
  speed: { label: "Speed", min: 1, max: 10, step: 1, unit: "" },
  count: { label: "Logos", min: 1, max: 10, step: 1, unit: "" },
} as const;

/** The characters each symbol set draws, and its name in the edit form. */
export const RAIN_SYMBOLS: Record<RainSymbols, { label: string; sample: string; glyphs: string }> = {
  // Half-width katakana and digits, like the film.
  katakana: { label: "Katakana", sample: "ｱｶｻﾅ", glyphs: "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789" },
  binary: { label: "Binary", sample: "0110", glyphs: "01" },
  code: { label: "Code", sample: "{</>", glyphs: "{}[]()<>/\\|;:=+-*&%#!?$@~^_.," },
  // Everything at once: katakana, letters, digits, symbols, Greek, math and block characters.
  chaos: {
    label: "Chaos",
    sample: "Σ#ﾊ▓",
    glyphs:
      "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ" +
      "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
      "{}[]()<>/\\|;:=+-*&%#!?$@~^_" +
      "ΣΔΩΨΞΦΠλμπ∑∞≠≈√∫∂∇⊕⊗¬∀∃" +
      "░▒▓█▄▀■□▲▼◆○●",
  },
};

/** Quick picks for the rain's color: the classic green first. */
export const RAIN_COLOR_SWATCHES = [
  { name: "Classic green", hex: "#22ff66" },
  { name: "Cyan", hex: "#22d3ee" },
  { name: "Blue", hex: "#3b82f6" },
  { name: "Violet", hex: "#a78bfa" },
  { name: "Magenta", hex: "#ff2bd6" },
  { name: "Red", hex: "#ff3b3b" },
  { name: "Amber", hex: "#ffb020" },
  { name: "White", hex: "#ffffff" },
] as const;

/** What the edit form shows for each effect: its wording, and which of the tuning options it reads. */
export const EFFECT_INFO: Record<
  ThemeEffect,
  { label: string; tuneTitle: string; sizeLabel: string; sliders: (keyof typeof EFFECT_OPTION_RANGES)[]; hasLogoColor: boolean; hasRainStyle: boolean }
> = {
  matrix: {
    label: "Matrix rain",
    tuneTitle: "Tune the rain",
    sizeLabel: "Text size",
    sliders: ["brightness", "size", "speed"],
    hasLogoColor: false,
    hasRainStyle: true,
  },
  dvd: {
    label: "Bouncing DVD",
    tuneTitle: "Tune the logo",
    sizeLabel: "Logo size",
    sliders: ["brightness", "size", "speed", "count"],
    hasLogoColor: true,
    hasRainStyle: false,
  },
};

/** One-click looks for the edit form: each sets the whole theme at once. */
export const THEME_PRESETS: readonly { name: string; description: string; theme: ProfileTheme }[] = [
  {
    name: "Hacker",
    description: "Dark green with subtle falling code",
    theme: { background: "#03110a", effect: "matrix", effect_options: DEFAULT_EFFECT_OPTIONS },
  },
  {
    name: "Neon Hacker",
    description: "Big, bright, glowing code",
    theme: {
      background: "#010a03",
      effect: "matrix",
      effect_options: { ...DEFAULT_EFFECT_OPTIONS, brightness: 90, size: 28, speed: 7, glow: true },
    },
  },
  {
    name: "Cyber Chaos",
    description: "Rainbow chaos symbols, glowing",
    theme: {
      background: "#0a0212",
      effect: "matrix",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 80,
        size: 20,
        speed: 6,
        glow: true,
        rain_rainbow: true,
        rain_symbols: "chaos",
      },
    },
  },
  {
    name: "Screensaver",
    description: "A DVD logo bouncing on black",
    theme: {
      background: "#000000",
      effect: "dvd",
      effect_options: { ...DEFAULT_EFFECT_OPTIONS, brightness: 100 },
    },
  },
];

export function sameTheme(a: ProfileTheme, b: ProfileTheme): boolean {
  const keys = Object.keys(DEFAULT_EFFECT_OPTIONS) as (keyof EffectOptions)[];
  return (
    a.background?.toLowerCase() === b.background?.toLowerCase() &&
    a.effect === b.effect &&
    keys.every((key) => a.effect_options[key] === b.effect_options[key])
  );
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const channel = parseInt(hex.slice(i, i + 2), 16) / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r! + 0.7152 * g! + 0.0722 * b!;
}

/** The UI's text is light, so a card background must be dark enough to keep it readable. */
export function isDarkEnough(hex: string): boolean {
  return HEX_COLOR.test(hex) && relativeLuminance(hex) <= MAX_BACKGROUND_LUMINANCE;
}
