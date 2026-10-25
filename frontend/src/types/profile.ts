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
export const THEME_EFFECTS = ["matrix"] as const;
export type ThemeEffect = (typeof THEME_EFFECTS)[number];

/** Cosmetic look of a profile's card and page. A `null` option means the default look. */
export interface ProfileTheme {
  /** Card background as `#rrggbb`. */
  background: string | null;
  /** Animation drawn behind the card's content. */
  effect: ThemeEffect | null;
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
  /** Replaces the whole theme; send `{ background: null, effect: null }` to go back to the default. */
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
