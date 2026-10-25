import type {
  ChartMood,
  ChartPalette,
  EffectOptions,
  EmojiPath,
  MoneyKind,
  ProfileTheme,
  RainSymbols,
  SloganStyle,
  ThemeEffect,
} from "../types/profile";

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
  emojis: ["🚀", "✨", "🔥", "💻", "🦄", "🍕"],
  emoji_count: 14,
  emoji_angle: 45,
  emoji_path: "straight",
  emoji_spin: 2,
  slogans: ["NEVER SKIP LEG DAY", "ONE MORE REP", "LIGHT WEIGHT BABY", "DO YOU EVEN LIFT?", "MOGGED"],
  slogan_color: "#ff4d2e",
  slogan_style: "mixed",
  slogan_tilt: -8,
  slogan_alternate: true,
  chart_volatility: 6,
  chart_mood: "choppy",
  chart_palette: "classic",
  chart_ticker: "MOG",
  chart_label: true,
  money_kind: "bills",
  money_count: 30,
  money_wind: 5,
  money_weight: 5,
};

/** The theme of a profile that hasn't customized anything. */
export const DEFAULT_THEME: ProfileTheme = { background: null, effect: null, effect_options: DEFAULT_EFFECT_OPTIONS };

/** The sliders' limits; the backend enforces the same ones (EFFECT_OPTION_RANGES). */
export const EFFECT_OPTION_RANGES = {
  brightness: { label: "Brightness", min: 10, max: 100, step: 5, unit: "%" },
  size: { label: "Text size", min: 10, max: 48, step: 2, unit: "px" },
  speed: { label: "Speed", min: 1, max: 10, step: 1, unit: "" },
  count: { label: "Logos", min: 1, max: 10, step: 1, unit: "" },
  emoji_count: { label: "How many", min: 3, max: 60, step: 1, unit: "" },
  emoji_angle: { label: "Direction", min: 0, max: 359, step: 15, unit: "°" },
  emoji_spin: { label: "Spin", min: -10, max: 10, step: 1, unit: "" },
  slogan_tilt: { label: "Tilt", min: -45, max: 45, step: 5, unit: "°" },
  chart_volatility: { label: "Volatility", min: 1, max: 10, step: 1, unit: "" },
  money_count: { label: "How much", min: 5, max: 80, step: 5, unit: "" },
  money_wind: { label: "Wind", min: 0, max: 10, step: 1, unit: "" },
  money_weight: { label: "Coin weight", min: 1, max: 10, step: 1, unit: "" },
} as const;

/** How many emoji a profile may list. Keep in sync with MAX_EMOJIS in the backend. */
export const MAX_EMOJIS = 12;

/** One-click emoji lists for the edit form. */
export const EMOJI_PACKS: readonly { name: string; emojis: string[] }[] = [
  { name: "Dev", emojis: ["💻", "🐛", "☕", "🔥", "⚡", "🚀"] },
  { name: "Party", emojis: ["🎉", "🥳", "🎈", "🎊", "✨", "🍾"] },
  { name: "Space", emojis: ["🚀", "🌙", "⭐", "🪐", "👽", "☄️"] },
  { name: "Snacks", emojis: ["🍕", "🌮", "🍔", "🍩", "🍟", "🧋"] },
  { name: "Critters", emojis: ["🦄", "🐱", "🐸", "🦊", "🐙", "🐧"] },
  { name: "Spooky", emojis: ["👻", "🎃", "🦇", "💀", "🕸️", "🧛"] },
  { name: "Chill", emojis: ["🌸", "🍃", "☁️", "🌈", "🌙", "🦋"] },
];

const packEmojis = (name: string): string[] => EMOJI_PACKS.find((pack) => pack.name === name)?.emojis ?? DEFAULT_EFFECT_OPTIONS.emojis;

/** How many slogans a profile may list, and the longest one. Keep in sync with MAX_SLOGANS and MAX_SLOGAN_LENGTH in the backend. */
export const MAX_SLOGANS = 8;
export const MAX_SLOGAN_LENGTH = 40;

/** One-click slogan lists for the edit form. */
export const SLOGAN_PACKS: readonly { name: string; slogans: string[] }[] = [
  {
    name: "Gym Bro",
    slogans: ["NEVER SKIP LEG DAY", "ONE MORE REP", "LIGHT WEIGHT BABY", "DO YOU EVEN LIFT?", "NO PAIN NO GAINS", "HYDRATE OR DIEDRATE"],
  },
  {
    name: "Dev Gym",
    slogans: ["DEADLIFT THE BACKLOG", "SQUATS > STANDUPS", "GIT PUSH --FORCE", "SHIP IT THEN LIFT IT", "CODE EAT LIFT REPEAT", "PR APPROVED"],
  },
  {
    name: "Mog",
    slogans: ["MOGGED", "GIGAMOGGER ENERGY", "MOG OR BE MOGGED", "NO ONE MOGS LIKE ME", "SENIOR MOGGER"],
  },
  {
    name: "Hype",
    slogans: ["LET'S GOOO", "STAY HARD", "BUILT DIFFERENT", "NO DAYS OFF", "WE'RE ALL GONNA MAKE IT"],
  },
];

const packSlogans = (name: string): string[] => SLOGAN_PACKS.find((pack) => pack.name === name)?.slogans ?? DEFAULT_EFFECT_OPTIONS.slogans;

/** The ways the slogans can be drawn, as the edit form words them. */
export const SLOGAN_STYLE_INFO: Record<SloganStyle, { label: string; description: string }> = {
  solid: { label: "Solid", description: "Every row is filled in" },
  outline: { label: "Outline", description: "Every row is just an outline, which is lighter behind your text" },
  mixed: { label: "Mixed", description: "Filled and outlined rows take turns" },
};

/** Quick picks for the slogan color. */
export const SLOGAN_COLOR_SWATCHES = [
  { name: "Hot orange", hex: "#ff4d2e" },
  { name: "Gold", hex: "#ffd60a" },
  { name: "Lime", hex: "#a3ff12" },
  { name: "Cyan", hex: "#22d3ee" },
  { name: "Blue", hex: "#3b82f6" },
  { name: "Violet", hex: "#a78bfa" },
  { name: "Magenta", hex: "#ff2bd6" },
  { name: "White", hex: "#ffffff" },
] as const;

/** How the chart's mood is worded in the edit form. */
export const CHART_MOOD_INFO: Record<ChartMood, { label: string; description: string }> = {
  bull: { label: "Bull run", description: "Mostly climbing, with the odd crash" },
  bear: { label: "Bear market", description: "Mostly sliding, with the odd rally" },
  choppy: { label: "Choppy", description: "Anything can happen" },
};

/** The candle colors (and how the edit form names them). Green up and red down is the Western habit; East Asian markets swap them. */
export const CHART_PALETTE_INFO: Record<ChartPalette, { label: string; up: string; down: string }> = {
  classic: { label: "Green / red", up: "#22c55e", down: "#ef4444" },
  swapped: { label: "Red / green", up: "#ef4444", down: "#22c55e" },
  neon: { label: "Cyan / magenta", up: "#22e5ff", down: "#ff2bd6" },
  mono: { label: "Light / dim", up: "#e2e8f0", down: "#64748b" },
};

/** What can rain down, as the edit form words it. */
export const MONEY_KIND_INFO: Record<MoneyKind, { label: string; description: string }> = {
  bills: { label: "Bills", description: "Green bills, flipping over as they fall" },
  coins: { label: "Coins", description: "Gold and silver coins, spinning as they fall" },
  mixed: { label: "Both", description: "Bills and coins together" },
};

/** The ways the emoji can travel, as the edit form words them. */
export const EMOJI_PATH_INFO: Record<EmojiPath, { label: string; description: string }> = {
  straight: { label: "Straight", description: "Drift one way and come back around the other side" },
  wave: { label: "Wave", description: "Drift one way while wobbling side to side" },
  bounce: { label: "Bounce", description: "Ricochet off the edges, starting in the chosen direction" },
};

// Emoji are told apart from other text by Unicode properties, so letters, digits and punctuation are left out.
const EMOJI_PICTOGRAPH = /\p{Extended_Pictographic}|\p{Regional_Indicator}/u;

/**
 * The emoji in a typed or pasted string, one entry per emoji, in order and without repeats.
 * A flag, a skin tone or a joined emoji like 👩‍💻 counts as one, which is why this splits by
 * "grapheme" (what people see as one character) and not by JavaScript's own characters.
 */
export function parseEmojis(text: string): string[] {
  const pieces =
    typeof Intl.Segmenter === "function"
      ? Array.from(new Intl.Segmenter().segment(text), ({ segment }) => segment)
      : Array.from(text); // very old browsers: a flag or a joined emoji would split, but plain emoji still work
  return [...new Set(pieces.filter((piece) => EMOJI_PICTOGRAPH.test(piece)))];
}

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
  {
    label: string;
    tuneTitle: string;
    sizeLabel: string;
    sliders: (keyof typeof EFFECT_OPTION_RANGES)[];
    hasLogoColor: boolean;
    hasRainStyle: boolean;
    hasEmojiStyle: boolean;
    hasSloganStyle: boolean;
    hasMarketStyle: boolean;
    hasMoneyStyle: boolean;
  }
> = {
  matrix: {
    label: "Matrix rain",
    tuneTitle: "Tune the rain",
    sizeLabel: "Text size",
    sliders: ["brightness", "size", "speed"],
    hasLogoColor: false,
    hasRainStyle: true,
    hasEmojiStyle: false,
    hasSloganStyle: false,
    hasMarketStyle: false,
    hasMoneyStyle: false,
  },
  dvd: {
    label: "Bouncing DVD",
    tuneTitle: "Tune the logo",
    sizeLabel: "Logo size",
    sliders: ["brightness", "size", "speed", "count"],
    hasLogoColor: true,
    hasRainStyle: false,
    hasEmojiStyle: false,
    hasSloganStyle: false,
    hasMarketStyle: false,
    hasMoneyStyle: false,
  },
  emoji: {
    label: "Floating emoji",
    tuneTitle: "Tune the emoji",
    sizeLabel: "Emoji size",
    sliders: ["brightness", "size", "emoji_count", "speed", "emoji_angle", "emoji_spin"],
    hasLogoColor: false,
    hasRainStyle: false,
    hasEmojiStyle: true,
    hasSloganStyle: false,
    hasMarketStyle: false,
    hasMoneyStyle: false,
  },
  slogans: {
    label: "Scrolling slogans",
    tuneTitle: "Tune the slogans",
    sizeLabel: "Text size",
    sliders: ["brightness", "size", "speed", "slogan_tilt"],
    hasLogoColor: false,
    hasRainStyle: false,
    hasEmojiStyle: false,
    hasSloganStyle: true,
    hasMarketStyle: false,
    hasMoneyStyle: false,
  },
  market: {
    label: "Volatile market",
    tuneTitle: "Tune the market",
    sizeLabel: "Candle size",
    sliders: ["brightness", "size", "speed", "chart_volatility"],
    hasLogoColor: false,
    hasRainStyle: false,
    hasEmojiStyle: false,
    hasSloganStyle: false,
    hasMarketStyle: true,
    hasMoneyStyle: false,
  },
  money: {
    label: "Money rain",
    tuneTitle: "Tune the money",
    sizeLabel: "Cash size",
    sliders: ["brightness", "size", "money_count", "speed", "money_wind", "money_weight"],
    hasLogoColor: false,
    hasRainStyle: false,
    hasEmojiStyle: false,
    hasSloganStyle: false,
    hasMarketStyle: false,
    hasMoneyStyle: true,
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
  {
    name: "Party Rain",
    description: "Confetti emoji, swaying down",
    theme: {
      background: "#1e0a2e",
      effect: "emoji",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 60,
        size: 26,
        speed: 4,
        emojis: packEmojis("Party"),
        emoji_count: 24,
        emoji_angle: 90,
        emoji_path: "wave",
        emoji_spin: 3,
      },
    },
  },
  {
    name: "Space Drift",
    description: "Planets and rockets sailing by, slowly turning",
    theme: {
      background: "#050816",
      effect: "emoji",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 60,
        size: 30,
        speed: 3,
        emojis: packEmojis("Space"),
        emoji_count: 14,
        emoji_angle: 20,
        emoji_path: "straight",
        emoji_spin: 2,
      },
    },
  },
  {
    name: "Snack Pinball",
    description: "Food ricocheting around, spinning fast",
    theme: {
      background: "#1a0b05",
      effect: "emoji",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 60,
        size: 32,
        speed: 5,
        emojis: packEmojis("Snacks"),
        emoji_count: 10,
        emoji_angle: 35,
        emoji_path: "bounce",
        emoji_spin: -6,
      },
    },
  },
  {
    name: "Gym Bro",
    description: "Gym slogans scrolling past",
    theme: {
      background: "#140808",
      effect: "slogans",
      effect_options: { ...DEFAULT_EFFECT_OPTIONS, brightness: 32, size: 18, speed: 4, slogans: packSlogans("Gym Bro") },
    },
  },
  {
    name: "Dev Gym",
    description: "Lifting meets shipping, outlined in gold",
    theme: {
      background: "#050816",
      effect: "slogans",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 40,
        size: 16,
        speed: 4,
        slogans: packSlogans("Dev Gym"),
        slogan_color: "#ffd60a",
        slogan_style: "outline",
        slogan_tilt: 6,
      },
    },
  },
  {
    name: "Mogged",
    description: "Big, glowing, and not sorry",
    theme: {
      background: "#0a0a12",
      effect: "slogans",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 35,
        size: 22,
        speed: 5,
        glow: true,
        slogans: packSlogans("Mog"),
        slogan_color: "#a78bfa",
        slogan_tilt: -14,
      },
    },
  },
  {
    name: "Wall Street",
    description: "A jumpy green and red chart",
    theme: {
      background: "#060b14",
      effect: "market",
      effect_options: { ...DEFAULT_EFFECT_OPTIONS, brightness: 50, size: 16, speed: 4, chart_volatility: 6 },
    },
  },
  {
    name: "To The Moon",
    description: "A neon bull run, mostly up",
    theme: {
      background: "#05060f",
      effect: "market",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 55,
        size: 18,
        speed: 5,
        glow: true,
        chart_volatility: 8,
        chart_mood: "bull",
        chart_palette: "neon",
        chart_ticker: "MOON",
      },
    },
  },
  {
    name: "Bear Market",
    description: "Red candles and bad news",
    theme: {
      background: "#12070a",
      effect: "market",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 50,
        size: 16,
        speed: 4,
        chart_volatility: 7,
        chart_mood: "bear",
        chart_ticker: "REKT",
      },
    },
  },
  {
    name: "Make It Rain",
    description: "Green bills fluttering down on a breeze",
    theme: {
      background: "#04150b",
      effect: "money",
      effect_options: { ...DEFAULT_EFFECT_OPTIONS, brightness: 60, size: 16, speed: 4, money_count: 30, money_wind: 5 },
    },
  },
  {
    name: "Gold Rush",
    description: "Gold and silver coins, glinting",
    theme: {
      background: "#140e03",
      effect: "money",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 65,
        size: 18,
        speed: 5,
        glow: true,
        money_kind: "coins",
        money_count: 24,
        money_wind: 2,
      },
    },
  },
  {
    name: "Cash Storm",
    description: "Bills and coins whipped around by a gale",
    theme: {
      background: "#030f0a",
      effect: "money",
      effect_options: {
        ...DEFAULT_EFFECT_OPTIONS,
        brightness: 65,
        size: 16,
        speed: 5,
        money_kind: "mixed",
        money_count: 50,
        money_wind: 10,
      },
    },
  },
];

export function sameList(a: readonly string[], b: readonly string[]): boolean {
  return a.length === b.length && a.every((item, i) => item === b[i]);
}

/** Options are numbers, strings and booleans, except the emoji list, which has to be compared item by item. */
function sameOption(a: EffectOptions[keyof EffectOptions], b: EffectOptions[keyof EffectOptions]): boolean {
  return Array.isArray(a) && Array.isArray(b) ? sameList(a, b) : a === b;
}

export function sameTheme(a: ProfileTheme, b: ProfileTheme): boolean {
  const keys = Object.keys(DEFAULT_EFFECT_OPTIONS) as (keyof EffectOptions)[];
  return (
    a.background?.toLowerCase() === b.background?.toLowerCase() &&
    a.effect === b.effect &&
    keys.every((key) => sameOption(a.effect_options[key], b.effect_options[key]))
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
