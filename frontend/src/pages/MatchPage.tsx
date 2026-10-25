import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States";
import Navbar from "../components/layout/Navbar";
import MatchCard from "../components/match/MatchCard";
import { getMyMatches, removeSwipe } from "../services/api";
import type { MatchedProfile } from "../types/profile";

/** Mog Match: everyone I liked, ranked by how similar their profile is to mine. */
export default function MatchPage() {
  const [matches, setMatches] = useState<MatchedProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    getMyMatches(controller.signal)
      .then(({ matches }) => setMatches(matches))
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Failed to load matches.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [reloadKey]);

  const [notice, setNotice] = useState<string | null>(null);

  const refresh = () => setReloadKey((key) => key + 1);

  const unlike = (profile: MatchedProfile) => {
    const before = matches;
    setMatches((current) => current.filter((m) => m.id !== profile.id)); // feels instant
    setNotice(null);
    removeSwipe(profile.id)
      .then(() => setNotice(`Unliked ${profile.full_name}. They're back on Discover.`))
      .catch((err: unknown) => {
        setMatches(before); // not saved, so put the card back
        setNotice(err instanceof Error ? err.message : "Couldn't unlike, try again.");
      });
  };

  return (
    <>
      <Navbar>
        <h1 className="truncate text-sm font-semibold text-slate-200">Mog Match</h1>
        <button
          type="button"
          onClick={refresh}
          title="Recalculate matches"
          aria-label="Refresh"
          className="ml-auto shrink-0 rounded-full border border-line bg-surface p-2 text-muted transition-colors hover:border-cyan-500/50 hover:text-cyan-200"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
        </button>
      </Navbar>

      <main className="mx-auto max-w-3xl px-4 py-6">
        <p className="mb-5 text-sm text-muted">
          Everyone you liked, ranked by how much their profile overlaps with yours: tech stack, interests, goals and
          more.
        </p>
        {notice && <p className="mb-4 text-sm text-violet-200">{notice}</p>}

        {error ? (
          <ErrorState message={error} onRetry={refresh} />
        ) : loading && matches.length === 0 ? (
          <LoadingState label="Comparing profiles…" />
        ) : matches.length === 0 ? (
          <EmptyState title="No matches yet">
            <Link to="/discover" className="text-cyan-300 hover:underline">
              Like someone on Discover
            </Link>{" "}
            and they'll show up here with their match score.
          </EmptyState>
        ) : (
          <ol className={`flex flex-col gap-4 transition-opacity ${loading ? "opacity-60" : ""}`}>
            {matches.map((profile, index) => (
              <li key={profile.id}>
                <MatchCard profile={profile} rank={index + 1} onUnlike={unlike} />
              </li>
            ))}
          </ol>
        )}
      </main>
    </>
  );
}
