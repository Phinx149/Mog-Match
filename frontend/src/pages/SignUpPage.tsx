import { UserPlus } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";

// Same rules as the backend (auth_service.validate_sign_up, profile_service.USERNAME_PATTERN), so most
// mistakes are caught before the request. The server checks again, and also knows if a username is taken.
const USERNAME_PATTERN = /^[A-Za-z0-9_-]{3,40}$/;
const MIN_PASSWORD_LENGTH = 8;

type Field = "full_name" | "username" | "password" | "confirm";
type FieldErrors = Partial<Record<Field, string>>;

function check(fullName: string, username: string, password: string, confirm: string): FieldErrors {
  const errors: FieldErrors = {};
  if (!fullName.trim()) errors.full_name = "This field is required.";
  if (!username.trim()) errors.username = "This field is required.";
  else if (!USERNAME_PATTERN.test(username.trim())) errors.username = "Use 3-40 letters, numbers, underscores or hyphens.";
  if (!password) errors.password = "This field is required.";
  else if (password.length < MIN_PASSWORD_LENGTH) errors.password = `Use at least ${MIN_PASSWORD_LENGTH} characters.`;
  // There is no password reset yet, so catch typos now rather than lock someone out of their new account.
  if (password && confirm !== password) errors.confirm = "Passwords don't match.";
  return errors;
}

export default function SignUpPage() {
  const { user, signUp } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  // Someone who is already logged in goes back where they came from, or Discover.
  const from = (location.state as { from?: string } | null)?.from ?? "/discover";

  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [error, setError] = useState<string | null>(null);

  // `submitting` stays true after a successful sign-up, so this doesn't fire (and send us to Discover)
  // in the moment between "logged in" and navigating to the new profile below.
  if (user && !submitting) return <Navigate to={from} replace />;

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const problems = check(fullName, username, password, confirm);
    setFieldErrors(problems);
    setError(null);
    if (Object.keys(problems).length > 0) return;

    setSubmitting(true);
    signUp(fullName.trim(), username.trim(), password)
      // A new profile is nearly empty, so the next step is filling it in.
      .then(() => navigate("/profile/edit", { replace: true }))
      .catch((err: unknown) => {
        // The server's per-field messages (e.g. "That username is already taken.") go under the fields;
        // anything else (API offline, …) goes above the button.
        const fields = err instanceof ApiError ? err.fields : {};
        const serverErrors: FieldErrors = { full_name: fields.full_name, username: fields.username, password: fields.password };
        if (Object.values(serverErrors).some(Boolean)) {
          setFieldErrors(serverErrors);
        } else {
          setError(err instanceof Error ? err.message : "Couldn't create your account, try again.");
        }
        setSubmitting(false);
      });
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-4 py-10">
      <p className="mb-8 text-center font-mono text-3xl font-bold tracking-tight">
        <span className="text-violet-400">mog</span>
        <span className="text-cyan-400">match</span>
      </p>

      <form onSubmit={submit} noValidate className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-6">
        <h1 className="text-xl font-semibold">Create your account</h1>

        <label className="flex flex-col gap-1.5 text-sm">
          Full name
          <input
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            autoComplete="name"
            autoFocus
            maxLength={120}
            placeholder="Jordan Lee"
            aria-invalid={!!fieldErrors.full_name}
            className="field"
          />
          {fieldErrors.full_name && <span className="text-xs text-rose-300">{fieldErrors.full_name}</span>}
        </label>

        <label className="flex flex-col gap-1.5 text-sm">
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            maxLength={40}
            placeholder="jordan-dev"
            aria-invalid={!!fieldErrors.username}
            className="field font-mono"
          />
          {fieldErrors.username && <span className="text-xs text-rose-300">{fieldErrors.username}</span>}
        </label>

        <label className="flex flex-col gap-1.5 text-sm">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="new-password"
            maxLength={128}
            aria-invalid={!!fieldErrors.password}
            className="field"
          />
          {fieldErrors.password ? (
            <span className="text-xs text-rose-300">{fieldErrors.password}</span>
          ) : (
            <span className="text-xs text-muted">At least {MIN_PASSWORD_LENGTH} characters.</span>
          )}
        </label>

        <label className="flex flex-col gap-1.5 text-sm">
          Confirm password
          <input
            type="password"
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
            autoComplete="new-password"
            maxLength={128}
            aria-invalid={!!fieldErrors.confirm}
            className="field"
          />
          {fieldErrors.confirm && <span className="text-xs text-rose-300">{fieldErrors.confirm}</span>}
        </label>

        {error && <p className="text-sm text-rose-300">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-60"
        >
          <UserPlus className="size-4" aria-hidden />
          {submitting ? "Creating account…" : "Sign up"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" state={location.state} className="font-medium text-violet-300 hover:text-violet-200">
          Log in
        </Link>
      </p>
    </main>
  );
}
