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
  links: ProfileLink[];
  projects: Project[];
  created_at: string;
  updated_at: string;
  mog: MogScore;
}

export type MatchComponent =
  | "skills"
  | "interests"
  | "looking_for"
  | "experience"
  | "ai_agents"
  | "ide"
  | "location";

/** Mirrors backend/app/services/mog_match.py `compute_match`: how similar a profile is to mine. */
export interface MogMatch {
  score: number;
  label: string;
  breakdown: Record<MatchComponent, number>;
  max_breakdown: Record<MatchComponent, number>;
  /** What both profiles have, in the other person's spelling. */
  shared: { skills: string[]; interests: string[]; looking_for: string[]; ai_agents: string[] };
}

export interface MatchedProfile extends Profile {
  match: MogMatch;
}

/** POST /api/swipes. A like comes back with its Mog Match score; a pass has `match: null`. */
export interface SwipeResult {
  target_id: string;
  action: SwipeDecision;
  match: MogMatch | null;
}

/** GET /api/profiles/me/matches: everyone I liked, most similar first. */
export interface MatchListResponse {
  matches: MatchedProfile[];
  count: number;
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
