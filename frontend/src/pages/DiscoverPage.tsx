import { Heart, RefreshCw, Sparkles, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States";
import FilterBar from "../components/discover/FilterBar";
import SearchBar from "../components/discover/SearchBar";
import MogFilter from "../components/mog/MogFilter";
import Navbar from "../components/layout/Navbar";
import ProfileCard from "../components/profiles/ProfileCard";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { clearSwipes, createSwipe, getFilterOptions, listProfiles } from "../services/api";
import type { FilterOptions, MogMatch, MogTier, Profile, SwipeDecision } from "../types/profile";

const NO_OPTIONS: FilterOptions = { skills: [], skill_aliases: {}, looking_for: [] };

export default function DiscoverPage() {
  const [search, setSearch] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedLookingFor, setSelectedLookingFor] = useState<string[]>([]);
  const [minTier, setMinTier] = useState<MogTier | "">("");
  const [sortByMog, setSortByMog] = useState(false);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>(NO_OPTIONS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  // Hides a card the moment you swipe. Swipes are saved on the server, which leaves them out of
  // the list from then on; this map just avoids waiting for a reload.
  const [decisions, setDecisions] = useState<Record<string, { name: string; decision: SwipeDecision }>>({});
  const [lastMatch, setLastMatch] = useState<{ name: string; match: MogMatch } | null>(null);
  const [swipeError, setSwipeError] = useState<string | null>(null);

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
    listProfiles(
      {
        q: debouncedSearch,
        skills: selectedSkills,
        looking_for: selectedLookingFor,
        min_tier: minTier || undefined,
        sort: sortByMog ? "mog" : undefined,
      },
      controller.signal,
    )
      .then(({ profiles }) => setProfiles(profiles))
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Failed to load profiles.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [debouncedSearch, selectedSkills, selectedLookingFor, minTier, sortByMog, reloadKey]);

  const remaining = useMemo(() => profiles.filter((p) => !decisions[p.id]), [profiles, decisions]);
  const liked = Object.values(decisions).filter((d) => d.decision === "like");
  const passedCount = Object.keys(decisions).length - liked.length;
  const filtersActive = Boolean(
    debouncedSearch.trim() || selectedSkills.length || selectedLookingFor.length || minTier,
  );

  const decide = (profile: Profile, decision: SwipeDecision) => {
    setSwipeError(null);
    setDecisions((current) => ({ ...current, [profile.id]: { name: profile.full_name, decision } }));
    createSwipe(profile.id, decision)
      .then(({ match }) => {
        if (match) setLastMatch({ name: profile.full_name, match });
      })
      .catch((err: unknown) => {
        // Not saved: put the card back so the swipe isn't silently lost.
        setDecisions((current) => {
          const next = { ...current };
          delete next[profile.id];
          return next;
        });
        setSwipeError(err instanceof Error ? err.message : "Couldn't save that swipe.");
      });
  };

  const refresh = () => setReloadKey((key) => key + 1);

  /** Deletes every like/pass on the server, which also empties the Match page. */
  const startOver = () => {
    clearSwipes()
      .then(() => {
        setDecisions({});
        setLastMatch(null);
        refresh();
      })
      .catch((err: unknown) => setSwipeError(err instanceof Error ? err.message : "Couldn't start over."));
  };

  return (
    <>
      <Navbar>
        <SearchBar value={search} onChange={setSearch} />
        <button
          type="button"
          onClick={refresh}
          title="Refresh"
          aria-label="Refresh"
          className="shrink-0 rounded-full border border-line bg-surface p-2 text-muted transition-colors hover:border-cyan-500/50 hover:text-cyan-200"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
        </button>
      </Navbar>

      <main className="mx-auto max-w-3xl px-4 py-6">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-2">
            <FilterBar
              options={filterOptions}
              skills={selectedSkills}
              lookingFor={selectedLookingFor}
              onSkillsChange={setSelectedSkills}
              onLookingForChange={setSelectedLookingFor}
            />
            <MogFilter
              minTier={minTier}
              sortByMog={sortByMog}
              onMinTierChange={setMinTier}
              onSortByMogChange={setSortByMog}
            />
          </div>
          <p className="flex shrink-0 items-center gap-3 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <Heart className="size-3.5 text-violet-300" aria-hidden /> {liked.length} liked
            </span>
            <span className="inline-flex items-center gap-1">
              <X className="size-3.5" aria-hidden /> {passedCount} passed
            </span>
          </p>
        </div>

        {lastMatch && (
          <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl border border-violet-500/30 bg-violet-500/10 px-4 py-2.5 text-sm text-violet-100">
            <Sparkles className="size-4 shrink-0 text-violet-300" aria-hidden />
            <span>
              Liked {lastMatch.name}: <strong className="font-mono">{lastMatch.match.score}%</strong> match,{" "}
              <span className="italic">{lastMatch.match.label.toLowerCase()}</span>.
            </span>
            <Link to="/match" className="ml-auto text-cyan-300 hover:underline">
              See your matches
            </Link>
          </p>
        )}
        {swipeError && <p className="mb-4 text-sm text-rose-300">{swipeError}</p>}

        {error ? (
          <ErrorState message={error} onRetry={refresh} />
        ) : loading && profiles.length === 0 ? (
          <LoadingState label="Finding developers…" />
        ) : remaining.length === 0 ? (
          <EmptyState title={filtersActive && !profiles.length ? "No developers match" : "You've seen everyone here"}>
            {filtersActive && !profiles.length && <p className="mb-2">Try removing a filter or changing your search.</p>}
            <p className="mb-2">Liked profiles are on your Match page; people you've swiped on don't come back.</p>
            <button type="button" onClick={startOver} className="text-cyan-300 hover:underline">
              Start over (clears your likes and matches)
            </button>
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
