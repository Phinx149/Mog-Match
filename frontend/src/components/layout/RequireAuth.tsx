import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { LoadingState } from "../common/States";

/** Wraps the logged-in part of the app: sends you to /login (and back here afterwards) if needed. */
export default function RequireAuth() {
  const { user, checking } = useAuth();
  const location = useLocation();

  if (checking) return <LoadingState label="Checking who you are…" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  // Keyed by user: if the logged-in user changes, every page reloads its data for the new user.
  return <Outlet key={user.id} />;
}
