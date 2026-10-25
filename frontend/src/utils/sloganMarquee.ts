// The scrolling slogans' layout rules, kept apart from the canvas drawing so they are easy to read
// (and to check without a browser). The slogans are drawn in rows on a field that is tilted as a whole;
// everything here works in the field's own coordinates, where rows are level and x = 0 is the middle.

import type { SloganStyle } from "../types/profile";

/** What sits between two slogans on a row. */
export const SEPARATOR = "  ✦  ";
const MAX_REPEATS = 200; // however tiny the text, a row's string never gets longer than this many copies

export interface Tape {
  text: string;
  /** How wide `text` is when drawn. */
  width: number;
}

/** The size of the tilted field that has to be covered so no corner of the box is left bare. */
export function fieldSize(width: number, height: number, tiltRadians: number): { x: number; y: number } {
  const cos = Math.abs(Math.cos(tiltRadians));
  const sin = Math.abs(Math.sin(tiltRadians));
  return { x: width * cos + height * sin, y: width * sin + height * cos };
}

/** Row numbers that cover a field `fieldHeight` tall, with row 0 in the middle. */
export function rowNumbers(fieldHeight: number, rowHeight: number): number[] {
  const reach = Math.ceil(fieldHeight / 2 / rowHeight);
  return Array.from({ length: reach * 2 + 1 }, (_, i) => i - reach);
}

/** The row's text: every slogan in order, starting from a different one on each row so neighbors read differently. */
export function buildTape(slogans: readonly string[], row: number, minWidth: number, measure: (text: string) => number): Tape {
  const start = ((row % slogans.length) + slogans.length) % slogans.length;
  const once = slogans.map((_, i) => slogans[(start + i) % slogans.length]).join(SEPARATOR) + SEPARATOR;
  const onceWidth = measure(once);
  // Repeated until it is at least as wide as the field, so two copies side by side can always fill it.
  const repeats = onceWidth > 0 ? Math.min(MAX_REPEATS, Math.max(1, Math.ceil(minWidth / onceWidth))) : 1;
  const text = once.repeat(repeats);
  return { text, width: measure(text) };
}

/**
 * The x to draw a row's text at, `shift` pixels into its scroll. Draw it again at x + `tapeWidth`: the two
 * copies cover the whole field, and shifting forever just wraps around, so the scroll never has a seam.
 * (This needs `tapeWidth` to be at least `fieldWidth`, which `buildTape` makes sure of.)
 */
export function tapeX(shift: number, tapeWidth: number, fieldWidth: number, leftward: boolean): number {
  const into = ((shift % tapeWidth) + tapeWidth) % tapeWidth;
  return leftward ? -fieldWidth / 2 - into : -fieldWidth / 2 - tapeWidth + into;
}

/** Without "alternate", every row scrolls left; with it, odd rows go the other way. */
export const isLeftward = (row: number, alternate: boolean): boolean => !alternate || row % 2 === 0;

/** Whether a row is drawn as an outline. In the mixed style, odd rows are. */
export const isOutlined = (style: SloganStyle, row: number): boolean =>
  style === "outline" || (style === "mixed" && row % 2 !== 0);
