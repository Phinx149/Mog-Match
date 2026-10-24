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
  location?: string;
}

export interface HealthResponse {
  status: string;
  database: string;
}

export const EXPERIENCE_LEVELS = ["Student", "Junior", "Mid-level", "Senior", "Lead"] as const;

export type SwipeDecision = "like" | "pass";
