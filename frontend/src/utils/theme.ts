import type { EffectOptions, ProfileTheme } from "../types/profile";

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
export const DEFAULT_EFFECT_OPTIONS: EffectOptions = { brightness: 40, size: 14, speed: 4, glow: false };

/** The theme of a profile that hasn't customized anything. */
export const DEFAULT_THEME: ProfileTheme = { background: null, effect: null, effect_options: DEFAULT_EFFECT_OPTIONS };

/** The sliders' limits; the backend enforces the same ones (EFFECT_OPTION_RANGES). */
export const EFFECT_OPTION_RANGES = {
  brightness: { label: "Brightness", min: 10, max: 100, step: 5, unit: "%" },
  size: { label: "Text size", min: 10, max: 48, step: 2, unit: "px" },
  speed: { label: "Speed", min: 1, max: 10, step: 1, unit: "" },
} as const;

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
      effect_options: { brightness: 90, size: 28, speed: 7, glow: true },
    },
  },
];

export function sameTheme(a: ProfileTheme, b: ProfileTheme): boolean {
  const [x, y] = [a.effect_options, b.effect_options];
  return (
    a.background?.toLowerCase() === b.background?.toLowerCase() &&
    a.effect === b.effect &&
    x.brightness === y.brightness &&
    x.size === y.size &&
    x.speed === y.speed &&
    x.glow === y.glow
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
