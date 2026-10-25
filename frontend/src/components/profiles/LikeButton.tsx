import { Heart, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createSwipe, getSwipe, removeSwipe } from "../../services/api";
import type { SwipeDecision } from "../../types/profile";

interface LikeButtonProps {
  profileId: string;
  name: string;
}

/**
 * Like / Unlike someone from their profile page. It's the same like as Discover's ❤:
 * liked people show up on the Match page, and unliking puts them back on Discover.
 */
export default function LikeButton({ profileId, name }: LikeButtonProps) {
  // undefined = still asking the server; null = never liked or passed
  const [action, setAction] = useState<SwipeDecision | null | undefined>(undefined);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setAction(undefined);
    setMessage(null);
    setError(null);
    getSwipe(profileId, controller.signal)
      .then((swipe) => setAction(swipe.action))
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setAction(null); // still let them try to like
      });
    return () => controller.abort();
  }, [profileId]);

  const liked = action === "like";

  const toggle = () => {
    setSaving(true);
    setError(null);
    setMessage(null);
    const save = liked
      ? removeSwipe(profileId).then(() => {
          setAction(null);
          setMessage(`Unliked. ${name} is back on Discover.`);
        })
      : createSwipe(profileId, "like").then((result) => {
          setAction("like");
          setMessage(result.match ? `${result.match.score}% similar to you.` : "Liked!");
        });
    save
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Couldn't save, try again."))
      .finally(() => setSaving(false));
  };

  if (action === undefined) {
    return (
      <span className="inline-flex items-center gap-2 px-4 py-2 text-sm text-muted">
        <Loader2 className="size-4 animate-spin" aria-hidden />
      </span>
    );
  }

  return (
    <div className="flex flex-col items-center gap-1.5 sm:items-end">
      <button
        type="button"
        onClick={toggle}
        disabled={saving}
        aria-pressed={liked}
        aria-label={liked ? `Unlike ${name}` : `Like ${name}`}
        className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-60 ${
          liked
            ? "border border-rose-500/50 bg-rose-500/15 text-rose-200 hover:bg-rose-500/25"
            : "bg-rose-600 text-white hover:bg-rose-500"
        }`}
      >
        <Heart className={`size-4 ${liked ? "fill-current" : ""}`} aria-hidden />
        {liked ? "Liked" : "Like"}
      </button>
      {message && (
        <p className="text-xs text-slate-300">
          {message}{" "}
          {liked && (
            <Link to="/match" className="text-cyan-300 hover:underline">
              See your matches
            </Link>
          )}
        </p>
      )}
      {error && <p className="text-xs text-rose-300">{error}</p>}
    </div>
  );
}
