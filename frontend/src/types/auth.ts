// Mirrors backend/app/services/auth_service.py (session_dict).

export interface SessionUser {
  id: string;
  full_name: string;
  username: string;
  avatar_url: string | null;
}

/** GET /api/auth/session, POST /api/auth/login, /signup and /logout. `user` is null when logged out. */
export interface SessionResponse {
  user: SessionUser | null;
}
