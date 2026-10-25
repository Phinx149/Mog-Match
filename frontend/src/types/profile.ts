// Mirrors the JSON returned by backend/app/services/profile_service.py `to_dict`.

export interface ProfileLink {
  id: string;
  label: string;
  url: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  project_url: string | null;
  technologies: string[];
}

export type MogComponent =
  | "esoteric"
  | "breadth"
  | "links"
  | "projects"
  | "descriptions"
  | "completeness"
  | "experience"
  | "bio";

/** Mirrors backend/app/services/mog_score.py `compute_mog_score`. */
export interface MogScore {
  score: number;
  tier: MogTier;
  emoji: string;
  roast: string;
  breakdown: Record<MogComponent, number>;
  max_breakdown: Record<MogComponent, number>;
  tips: string[];
}

/** Lowest tier first. */
export const MOG_TIERS = ["Hello World", "Junior Mogger", "Mid Mogger", "Senior Mogger", "Gigamogger"] as const;
export type MogTier = (typeof MOG_TIERS)[number];

/** Animated card backgrounds. Keep in sync with THEME_EFFECTS in backend/app/services/profile_service.py. */
export const THEME_EFFECTS = ["matrix", "dvd", "emoji", "slogans"] as const;
export type ThemeEffect = (typeof THEME_EFFECTS)[number];

/** What the matrix rain is made of. Keep in sync with RAIN_SYMBOL_SETS in the backend. */
export const RAIN_SYMBOL_SETS = ["katakana", "binary", "code", "chaos"] as const;
export type RainSymbols = (typeof RAIN_SYMBOL_SETS)[number];

/** How the floating emoji travel. Keep in sync with EMOJI_PATHS in the backend. */
export const EMOJI_PATHS = ["straight", "wave", "bounce"] as const;
export type EmojiPath = (typeof EMOJI_PATHS)[number];

/** How the scrolling slogans are drawn: filled letters, outlined letters, or rows taking turns. Keep in sync with SLOGAN_STYLES in the backend. */
export const SLOGAN_STYLES = ["solid", "outline", "mixed"] as const;
export type SloganStyle = (typeof SLOGAN_STYLES)[number];

/** How the animated effect looks, shared by every effect. The server fills in defaults, so every field is always present. */
export interface EffectOptions {
  /** How opaque the effect is, 10-100 (%). */
  brightness: number;
  /** Letter size (rain), logo size (DVD), emoji size or text size (slogans), 10-48. */
  size: number;
  /** How fast it moves, 1-10. */
  speed: number;
  /** Neon halo (and bold letters for the rain). */
  glow: boolean;
  /** How many bouncing logos (DVD only), 1-10. */
  count: number;
  /** Whether a logo takes a new color each time it bounces (DVD only). */
  color_change: boolean;
  /** The logo's color as `#rrggbb` when it doesn't change color (DVD only). */
  color: string;
  /** The rain's color as `#rrggbb` (matrix only). */
  rain_color: string;
  /** Every column of the rain gets its own hue, drifting over time, instead of `rain_color` (matrix only). */
  rain_rainbow: boolean;
  /** Which characters fall (matrix only). */
  rain_symbols: RainSymbols;
  /** The emoji that float around, 1-12 (emoji only). */
  emojis: string[];
  /** How many emoji float around at once, 3-60 (emoji only). */
  emoji_count: number;
  /** Direction of travel in degrees, 0-359: 0 is right and 90 is down (emoji only). */
  emoji_angle: number;
  /** Straight line, a wobbling wave, or bouncing off the edges (emoji only). */
  emoji_path: EmojiPath;
  /** How fast each emoji turns, -10 to 10: negative is counter-clockwise, 0 is no spin (emoji only). */
  emoji_spin: number;
  /** The slogans that scroll by, 1-8 of up to 40 characters (slogans only). */
  slogans: string[];
  /** The letters' color as `#rrggbb` (slogans only). */
  slogan_color: string;
  /** Filled letters, outlined letters, or rows taking turns (slogans only). */
  slogan_style: SloganStyle;
  /** How far the rows lean, -45 to 45 degrees: negative leans up to the right (slogans only). */
  slogan_tilt: number;
  /** Every other row scrolls the opposite way (slogans only). */
  slogan_alternate: boolean;
}

/** Cosmetic look of a profile's card and page. A `null` background or effect means the default look. */
export interface ProfileTheme {
  /** Card background as `#rrggbb`. */
  background: string | null;
  /** Animation drawn behind the card's content. */
  effect: ThemeEffect | null;
  /** Tuning for `effect`; kept even while the effect is off. */
  effect_options: EffectOptions;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name: string;
  username: string;
  avatar_url: string | null;
  location: string | null;
  education: string | null;
  bio: string;
  favorite_ide: string | null;
  favorite_ai_agents: string[];
  skills: string[];
  interests: string[];
  experience_level: string | null;
  looking_for: string[];
  theme: ProfileTheme;
  links: ProfileLink[];
  projects: Project[];
  created_at: string;
  updated_at: string;
  mog: MogScore;
}

export interface ProfileListResponse {
  profiles: Profile[];
  count: number;
}

/** Body for PATCH /api/profiles/me. Links and projects replace the existing lists. */
export interface ProfileUpdate {
  full_name?: string;
  username?: string;
  avatar_url?: string | null;
  location?: string | null;
  education?: string | null;
  bio?: string;
  favorite_ide?: string | null;
  favorite_ai_agents?: string[];
  skills?: string[];
  interests?: string[];
  experience_level?: string | null;
  looking_for?: string[];
  /** Replaces the whole theme; send `DEFAULT_THEME` (utils/theme.ts) to go back to the default. */
  theme?: ProfileTheme;
  links?: Omit<ProfileLink, "id">[];
  projects?: Omit<Project, "id">[];
}

export interface ProfileFilters {
  q?: string;
  skills?: string[];
  interests?: string[];
  looking_for?: string[];
  location?: string;
  min_tier?: MogTier;
  sort?: "mog";
}

/** Every allowed value for the list fields (GET /api/profiles/filter-options). */
export interface FilterOptions {
  /** Every skill a profile is allowed to list. */
  skills: string[];
  /** Every "looking for" option a profile can pick. */
  looking_for: string[];
}

export interface HealthResponse {
  status: string;
  database: string;
}

export const EXPERIENCE_LEVELS = ["Student", "Junior", "Mid-level", "Senior", "Lead"] as const;

export type SwipeDecision = "like" | "pass";
