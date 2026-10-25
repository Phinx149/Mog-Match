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
import type { SessionResponse } from "../types/auth";
import type { InboxResponse, Invite } from "../types/invite";

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

/** Fired when the API says we're not logged in (e.g. the session ended), so the app can show the login page. */
export const LOGGED_OUT_EVENT = "mogmatch:logged-out";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      credentials: "include", // send the login cookie to the API (it's on another port)
      headers: { ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...init.headers },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(`Can't reach the API at ${API_URL}. Is the Flask server running?`, 0);
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error?.message ?? `Request failed (${response.status})`;
    // A wrong password is also a 401, but that's the login form's error to show, not a logout.
    if (response.status === 401 && path !== "/api/auth/login") {
      window.dispatchEvent(new Event(LOGGED_OUT_EVENT));
    }
    throw new ApiError(message, response.status, body?.error?.fields ?? {});
  }
  return body as T;
}

export function getSession(signal?: AbortSignal) {
  return request<SessionResponse>("/api/auth/session", { signal });
}

export function logIn(username: string, password: string) {
  return request<SessionResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function logOut() {
  return request<SessionResponse>("/api/auth/logout", { method: "POST" });
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

/** Unlike one person: they leave my matches and come back to Discover. */
export function removeSwipe(targetId: string) {
  return request<{ removed: boolean }>(`/api/swipes/${encodeURIComponent(targetId)}`, { method: "DELETE" });
}

/** Forget all my likes/passes (and so all my matches). */
export function clearSwipes() {
  return request<{ removed: number }>("/api/swipes", { method: "DELETE" });
}

/** Fired after I answer an invite, so the nav badge can re-count without a page change. */
export const INVITES_CHANGED_EVENT = "mogmatch:invites-changed";

export function getInbox(signal?: AbortSignal) {
  return request<InboxResponse>("/api/invites/inbox", { signal });
}

/** Invite someone I liked. `message` is optional. */
export function sendInvite(recipientId: string, message?: string) {
  return request<Invite>("/api/invites", {
    method: "POST",
    body: JSON.stringify({ recipient_id: recipientId, ...(message?.trim() ? { message } : {}) }),
  });
}

/** Accept or decline an invite sent to me. */
export async function respondToInvite(inviteId: string, status: "accepted" | "declined") {
  const invite = await request<Invite>(`/api/invites/${encodeURIComponent(inviteId)}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  window.dispatchEvent(new Event(INVITES_CHANGED_EVENT));
  return invite;
}

/** Take back an invite I sent that hasn't been answered yet. */
export function cancelInvite(inviteId: string) {
  return request<{ removed: boolean }>(`/api/invites/${encodeURIComponent(inviteId)}`, { method: "DELETE" });
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
