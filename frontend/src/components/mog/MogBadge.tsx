import type { MogScore } from "../../types/profile";

/** Compact "👑 91" pill for cards. The tier and roast show on hover. */
export default function MogBadge({ mog }: { mog: MogScore }) {
  return (
    <span
      title={`${mog.tier}: ${mog.roast}`}
      className="inline-flex shrink-0 items-center gap-1 rounded-full border border-amber-400/30 bg-amber-400/10 px-2.5 py-0.5 font-mono text-xs font-semibold text-amber-200"
    >
      <span aria-hidden>{mog.emoji}</span>
      {mog.score}
      <span className="sr-only">Mog Score, {mog.tier}</span>
    </span>
  );
}
