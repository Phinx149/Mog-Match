import { LogIn } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const { user, logIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  // Go back to the page that sent us here, or Discover.
  const from = (location.state as { from?: string } | null)?.from ?? "/discover";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (user) return <Navigate to={from} replace />;

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    logIn(username, password)
      .then(() => navigate(from, { replace: true }))
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Couldn't log in, try again.");
        setSubmitting(false);
      });
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-4 py-10">
      <p className="mb-8 text-center font-mono text-3xl font-bold tracking-tight">
        <span className="text-violet-400">mog</span>
        <span className="text-cyan-400">match</span>
      </p>

      <form onSubmit={submit} className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-6">
        <h1 className="text-xl font-semibold">Log in</h1>

        <label className="flex flex-col gap-1.5 text-sm">
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            autoFocus
            placeholder="jordan-dev"
            className="field"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            className="field"
          />
        </label>

        {error && <p className="text-sm text-rose-300">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-60"
        >
          <LogIn className="size-4" aria-hidden />
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>

      <p className="mt-4 text-center text-xs text-muted">
        Demo accounts: any seeded username (e.g. <span className="font-mono">jordan-dev</span>,{" "}
        <span className="font-mono">samfullstack</span>). The shared password is{" "}
        <span className="font-mono">SEED_PASSWORD</span> in <span className="font-mono">backend/.env.example</span>.
      </p>
    </main>
  );
}
