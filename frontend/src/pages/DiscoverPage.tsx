import { Heart, RefreshCw, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States";
import FilterBar from "../components/discover/FilterBar";
import SearchBar from "../components/discover/SearchBar";
import Navbar from "../components/layout/Navbar";
import ProfileCard from "../components/profiles/ProfileCard";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { getFilterOptions, listProfiles } from "../services/api";
import type { FilterOptions, Profile, SwipeDecision } from "../types/profile";

const NO_OPTIONS: FilterOptions = { skills: [], looking_for: [] };

export default function DiscoverPage() {
  const [search, setSearch] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedLookingFor, setSelectedLookingFor] = useState<string[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>(NO_OPTIONS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  // Likes/passes live only in memory for this milestone; persistence comes with matching.
  const [decisions, setDecisions] = useState<Record<string, { name: string; decision: SwipeDecision }>>({});

  const debouncedSearch = useDebouncedValue(search, 300);

  // The filter menu offers every valid skill, so it doesn't depend on which profiles are on screen.
  // A failure here is non-fatal (the menu just says nothing is available); Refresh retries it.
  useEffect(() => {
    const controller = new AbortController();
    getFilterOptions(controller.signal)
      .then(setFilterOptions)
      .catch(() => {});
    return () => controller.abort();
  }, [reloadKey]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    listProfiles({ q: debouncedSearch, skills: selectedSkills, looking_for: selectedLookingFor }, controller.signal)
      .then(({ profiles }) => setProfiles(profiles))
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Failed to load profiles.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [debouncedSearch, selectedSkills, selectedLookingFor, reloadKey]);

  const remaining = useMemo(() => profiles.filter((p) => !decisions[p.id]), [profiles, decisions]);
  const liked = Object.values(decisions).filter((d) => d.decision === "like");
  const passedCount = Object.keys(decisions).length - liked.length;

  const decide = (profile: Profile, decision: SwipeDecision) =>
    setDecisions((current) => ({ ...current, [profile.id]: { name: profile.full_name, decision } }));

  const refresh = () => {
    setDecisions({});
    setReloadKey((key) => key + 1);
  };

  return (
    <>
      <Navbar>
        <SearchBar value={search} onChange={setSearch} />
        <button
          type="button"
          onClick={refresh}
          title="Refresh and reset likes/passes"
          aria-label="Refresh"
          className="shrink-0 rounded-full border border-line bg-surface p-2 text-muted transition-colors hover:border-cyan-500/50 hover:text-cyan-200"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
        </button>
      </Navbar>

      <main className="mx-auto max-w-3xl px-4 py-6">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <FilterBar
            options={filterOptions}
            skills={selectedSkills}
            lookingFor={selectedLookingFor}
            onSkillsChange={setSelectedSkills}
            onLookingForChange={setSelectedLookingFor}
          />
          <p className="flex shrink-0 items-center gap-3 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <Heart className="size-3.5 text-violet-300" aria-hidden /> {liked.length} liked
            </span>
            <span className="inline-flex items-center gap-1">
              <X className="size-3.5" aria-hidden /> {passedCount} passed
            </span>
          </p>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={refresh} />
        ) : loading && profiles.length === 0 ? (
          <LoadingState label="Finding developers…" />
        ) : remaining.length === 0 ? (
          <EmptyState title={profiles.length ? "You've seen everyone here" : "No developers match"}>
            {profiles.length ? (
              <>
                {liked.length > 0 && <p className="mb-2">You liked {liked.map((d) => d.name).join(", ")}.</p>}
                <button type="button" onClick={refresh} className="text-cyan-300 hover:underline">
                  Refresh to start over
                </button>
              </>
            ) : (
              "Try removing a filter or changing your search."
            )}
          </EmptyState>
        ) : (
          <ul className={`flex flex-col gap-4 transition-opacity ${loading ? "opacity-60" : ""}`}>
            {remaining.map((profile) => (
              <li key={profile.id}>
                <ProfileCard
                  profile={profile}
                  activeSkills={selectedSkills}
                  activeLookingFor={selectedLookingFor}
                  onDecide={decide}
                />
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  );
}
