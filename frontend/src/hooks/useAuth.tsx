import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { getSession, LOGGED_OUT_EVENT, logIn as apiLogIn, logOut as apiLogOut, signUp as apiSignUp } from "../services/api";
import type { SessionUser } from "../types/auth";

interface AuthState {
  /** The logged-in user, or null. */
  user: SessionUser | null;
  /** True until we've asked the server who we are. */
  checking: boolean;
  logIn: (username: string, password: string) => Promise<void>;
  /** Creates an account and logs it in. */
  signUp: (fullName: string, username: string, password: string) => Promise<void>;
  logOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

/** Asks the API "who am I?" once on load and shares the answer with every page. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getSession()
      .then((session) => setUser(session.user))
      .catch(() => setUser(null)) // API offline: the login page shows the real error when you try
      .finally(() => setChecking(false));

    // All normal tabs share one login cookie. If another tab logged in as someone else, this tab
    // must notice, or it would show one name while the API answers as another. Re-check on focus.
    const recheck = () => {
      getSession()
        .then((session) => setUser((current) => (current?.id === session.user?.id ? current : session.user)))
        .catch(() => {});
    };
    // Any API call that comes back 401 means the session ended (e.g. after `flask seed --reset`).
    const onLoggedOut = () => setUser(null);
    window.addEventListener("focus", recheck);
    window.addEventListener(LOGGED_OUT_EVENT, onLoggedOut);
    return () => {
      window.removeEventListener("focus", recheck);
      window.removeEventListener(LOGGED_OUT_EVENT, onLoggedOut);
    };
  }, []);

  const logIn = useCallback(async (username: string, password: string) => {
    setUser((await apiLogIn(username, password)).user);
  }, []);

  const signUp = useCallback(async (fullName: string, username: string, password: string) => {
    setUser((await apiSignUp(fullName, username, password)).user);
  }, []);

  const logOut = useCallback(async () => {
    await apiLogOut();
    setUser(null);
  }, []);

  return <AuthContext.Provider value={{ user, checking, logIn, signUp, logOut }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth must be used inside <AuthProvider>");
  return auth;
}
