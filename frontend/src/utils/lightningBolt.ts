// The lightning's rules (what a bolt looks like, when it strikes and how it fades), kept apart from
// the canvas drawing so they are easy to read. Positions are pixels in the card.

export interface Point {
  x: number;
  y: number;
}

export interface Box {
  width: number;
  height: number;
}

/** One bolt: the main channel from the top of the card, and the branches that fork off it. */
export interface Bolt {
  main: Point[];
  branches: Point[][];
}

export interface Strike {
  bolt: Bolt;
  /** Seconds since it struck. */
  age: number;
  /** Whether it flickers back for a second flash along the same path, as real lightning often does. */
  restrikes: boolean;
}

/**
 * Flashing safety: a strike flashes at most twice (the strike and its restrike, within a fifth of a second), and
 * two strikes start at least MIN_GAP_SECONDS apart, so nobody sees more than two flashes in any one second.
 * That stays under the limit of three that accessibility guidelines set for flashing content.
 */
export const MIN_GAP_SECONDS = 1.2;

const FIRST_FLASH_END = 0.07; // seconds the strike stays at full brightness
const RESTRIKE_START = 0.13; // it dips between these two...
const RESTRIKE_END = 0.21; // ...then flares back up for a moment
const FADE_SECONDS = 0.5;
/** How long a strike lasts in all; after this it is gone. */
export const STRIKE_SECONDS = RESTRIKE_END + FADE_SECONDS;

/** How thick the bolt's core is, per point of the size setting (size 14 is about 2px). */
export const THICKNESS_PER_SIZE = 0.15;
/** A branch is this fraction as thick as the main bolt. */
export const BRANCH_THICKNESS = 0.5;

/**
 * Splits every segment in two and pushes the new point sideways, `rounds` times, with smaller pushes each round.
 * This "midpoint displacement" is what gives a bolt its jagged look at every scale: big kinks first, then small ones.
 */
function jag(from: Point, to: Point, rounds: number, roughness: number): Point[] {
  let points = [from, to];
  let push = Math.hypot(to.x - from.x, to.y - from.y) * roughness; // the biggest sideways push this round
  for (let round = 0; round < rounds; round++) {
    const next: Point[] = [from];
    let a = from;
    for (const b of points.slice(1)) {
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const length = Math.hypot(dx, dy) || 1;
      const offset = (Math.random() * 2 - 1) * push;
      // (-dy, dx) is the direction at a right angle to the segment.
      next.push({ x: (a.x + b.x) / 2 - (dy / length) * offset, y: (a.y + b.y) / 2 + (dx / length) * offset }, b);
      a = b;
    }
    points = next;
    push *= 0.55;
  }
  return points;
}

/** A bolt from near the top edge to somewhere in the lower part of the box, with `forks` branches leaning left or right. */
export function newBolt({ width, height }: Box, forks: number): Bolt {
  const startX = width * (0.1 + Math.random() * 0.8);
  const start = { x: startX, y: -4 }; // just above the edge, so it enters from outside the card
  const endX = Math.min(Math.max(startX + (Math.random() - 0.5) * width * 0.35, 0), width);
  const end = { x: endX, y: height * (0.65 + Math.random() * 0.4) }; // the lower part of the card, sometimes past it
  const main = jag(start, end, 6, 0.16);

  const branches: Point[][] = [];
  for (let i = 0; i < forks; i++) {
    // Fork off somewhere along the upper-middle of the bolt, heading down and out to one side.
    const from = main[Math.floor(main.length * (0.1 + Math.random() * 0.7))] ?? start;
    const side = Math.random() < 0.5 ? -1 : 1;
    const angle = Math.PI / 2 + side * (0.3 + Math.random() * 0.7); // radians; PI / 2 is straight down
    const length = height * (0.1 + Math.random() * 0.25);
    const to = { x: from.x + Math.cos(angle) * length, y: from.y + Math.sin(angle) * length };
    branches.push(jag(from, to, 4, 0.2));
  }
  return { main, branches };
}

export function newStrike(box: Box, forks: number): Strike {
  return { bolt: newBolt(box, forks), age: 0, restrikes: Math.random() < 0.6 };
}

/**
 * Seconds to wait before the next strike. Strikes 1 is about every 7 seconds and 10 about every 1.5, always varied
 * (so cards on screen together don't flash in step) and never under MIN_GAP_SECONDS.
 */
export function secondsToNextStrike(strikes: number): number {
  const average = 7.5 - 0.65 * (strikes - 1);
  return Math.max(MIN_GAP_SECONDS, average * (0.6 + Math.random() * 0.8));
}

/** How bright a strike is `age` seconds after it struck, 0-1: a full-bright flash, an optional flicker back, then a quick fade. */
export function strikeBrightness({ age, restrikes }: Pick<Strike, "age" | "restrikes">): number {
  const fade = (since: number, from: number) => from * Math.max(0, 1 - since / FADE_SECONDS) ** 2;
  if (age < FIRST_FLASH_END) return 1;
  if (!restrikes) return fade(age - FIRST_FLASH_END, 1);
  if (age < RESTRIKE_START) return 0.2;
  if (age < RESTRIKE_END) return 0.9;
  return fade(age - RESTRIKE_END, 0.9);
}
