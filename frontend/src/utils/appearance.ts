// The site-wide color scheme the user picks in Settings (not to be confused with a *profile* theme,
// which only restyles one profile's cards: see utils/theme.ts). The choice lives in this browser's
// localStorage and shows up as `data-appearance` on <html>; the matching colors are in index.css.
// index.html applies the saved choice before the first paint, so keep STORAGE_KEY in sync there.

export type Appearance = "default" | "hacker";

const STORAGE_KEY = "mogmatch-appearance";

/** What Settings shows for each appearance. `preview` is fixed hex (not CSS variables) so each card shows its own colors whichever one is active. */
export const APPEARANCES: readonly {
  id: Appearance;
  label: string;
  description: string;
  preview: { canvas: string; surface: string; line: string; accent: string; accentAlt: string };
}[] = [
  {
    id: "default",
    label: "Default",
    description: "Dark navy with violet accents",
    preview: { canvas: "#0b0d14", surface: "#131724", line: "#262d42", accent: "#8b5cf6", accentAlt: "#22d3ee" },
  },
  {
    id: "hacker",
    label: "Hacker",
    description: "Pure black with terminal-green accents",
    preview: { canvas: "#000000", surface: "#08100b", line: "#153823", accent: "#1fe86f", accentAlt: "#2ee8b0" },
  },
];

/** The appearance currently applied to the page. */
export function getAppearance(): Appearance {
  const applied = document.documentElement.dataset.appearance;
  return APPEARANCES.find((appearance) => appearance.id === applied)?.id ?? "default";
}

/** Switches the whole site right now and remembers the choice for next time. */
export function setAppearance(appearance: Appearance) {
  document.documentElement.dataset.appearance = appearance;
  try {
    localStorage.setItem(STORAGE_KEY, appearance);
  } catch {
    // Storage can be blocked (private windows, strict settings). The switch still works until the page is reloaded.
  }
}
