/** Look shared by the theme picker's preset, effect and emoji-pack buttons. */
export function chipClass(selected: boolean): string {
  return `inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
    selected
      ? "border-cyan-400 bg-cyan-400/10 text-cyan-200"
      : "border-line text-slate-200 hover:border-cyan-500/50 hover:text-cyan-200"
  }`;
}
