import type {
  FilterOptions,
  HealthResponse,
  MatchListResponse,
  Profile,
  ProfileFilters,
  ProfileListResponse,
  ProfileUpdate,
  SwipeDecision,
  SwipeResult,
} from "../types/profile";

const API_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:5001").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  fields: Record<string, string>;

  constructor(message: string, status: number, fields: Record<string, string> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fields = fields;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...init.headers },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(`Can't reach the API at ${API_URL}. Is the Flask server running?`, 0);
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error?.message ?? `Request failed (${response.status})`;
    throw new ApiError(message, response.status, body?.error?.fields ?? {});
  }
  return body as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

export function listProfiles(filters: ProfileFilters = {}, signal?: AbortSignal) {
  const params = new URLSearchParams();
  if (filters.q?.trim()) params.set("q", filters.q.trim());
  if (filters.skills?.length) params.set("skills", filters.skills.join(","));
  if (filters.interests?.length) params.set("interests", filters.interests.join(","));
  if (filters.looking_for?.length) params.set("looking_for", filters.looking_for.join(","));
  if (filters.location?.trim()) params.set("location", filters.location.trim());
  if (filters.min_tier) params.set("min_tier", filters.min_tier);
  if (filters.sort) params.set("sort", filters.sort);
  const query = params.toString();
  return request<ProfileListResponse>(`/api/profiles${query ? `?${query}` : ""}`, { signal });
}

export function getFilterOptions(signal?: AbortSignal) {
  return request<FilterOptions>("/api/profiles/filter-options", { signal });
}

export function getProfile(id: string, signal?: AbortSignal) {
  return request<Profile>(`/api/profiles/${encodeURIComponent(id)}`, { signal });
}

export function getMyProfile(signal?: AbortSignal) {
  return request<Profile>("/api/profiles/me", { signal });
}

export function getMyMatches(signal?: AbortSignal) {
  return request<MatchListResponse>("/api/profiles/me/matches", { signal });
}

export function createSwipe(targetId: string, action: SwipeDecision) {
  return request<SwipeResult>("/api/swipes", {
    method: "POST",
    body: JSON.stringify({ target_id: targetId, action }),
  });
}

/** Forget all my likes/passes (and so all my matches). */
export function clearSwipes() {
  return request<{ removed: number }>("/api/swipes", { method: "DELETE" });
}

export function updateMyProfile(update: ProfileUpdate, photo?: File | null) {
  const body = new FormData();
  body.append("profile", JSON.stringify(update));
  if (photo) body.append("photo", photo);
  return request<Profile>("/api/profiles/me", {
    method: "PATCH",
    body: photo ? body : JSON.stringify(update),
  });
}
