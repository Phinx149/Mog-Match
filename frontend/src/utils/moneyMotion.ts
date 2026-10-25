// The money rain's movement rules, kept apart from the canvas drawing so they are easy to read
// (and to check without a browser). Positions are the center of a bill or coin, in pixels.

import type { MoneyKind } from "../types/profile";

const TAU = Math.PI * 2;
const MIN_SCALE = 0.6; // the smallest a piece gets, next to the biggest at 1
const MIN_SQUASH = 0.06; // a piece turned edge-on stays a hairline instead of vanishing
const EDGE_SHADE = 0.6; // how dark a piece turned edge-on is drawn, next to 1 when it faces the viewer
const WIND_PX_PER_STEP = 28; // sideways speed of a full gust per point of the wind setting (wind 10 peaks near 280 px/s)
const LEAN_PER_PX_S = 0.0015; // radians a bill tips into the wind per px/s of sideways speed
const OFFSCREEN_PER_SIZE = 2; // a piece is hidden once its center is this many sizes past an edge

/** Drawn sizes, as multiples of the size setting. A bill is long and thin like a real one (about 2.35 to 1). */
export const BILL_LENGTH_PER_SIZE = 3;
export const BILL_ASPECT = 2.35;
export const COIN_DIAMETER_PER_SIZE = 1.5;

/**
 * How a kind of money behaves in the air. `weight` is how little the wind moves it, `fall` its fall speed next to
 * a bill's, `tumble` how fast it turns over (a fast spin is what makes a thing look light), and `windTumble` how
 * much of the wind setting is added on top of that.
 */
export interface Feel {
  weight: number;
  fall: number;
  flutter: number;
  rock: number;
  response: number;
  tumble: number;
  windTumble: number;
}

const BILL: Feel = { weight: 0.8, fall: 1, flutter: 45, rock: 0.5, response: 2.2, tumble: 1, windTumble: 1 };
const COIN_ROCK = 0.12;

/**
 * How a coin behaves for a weight setting of 1-10 (5 is the default). Heavier coins fall faster, turn over slower
 * and are pushed less by the wind; at 1 a coin falls and is blown about like a bill, though it still turns more calmly.
 * Each line is straight from 1 to 10, passing through the values that felt right at 5.
 */
export function coinFeel(weight: number): Feel {
  return {
    weight: 0.6 + 0.2 * weight, // 0.8 (as light as a bill) to 2.6
    fall: 0.9 + 0.09 * weight, // 0.99 to 1.8
    flutter: 10,
    rock: COIN_ROCK,
    response: 1.2,
    tumble: 1.25 - 0.09 * weight, // 1.16 to 0.35
    windTumble: 0.55 - 0.05 * weight, // 0.5 to 0.05
  };
}

export interface Cash {
  coin: boolean;
  /** Which look this one has (taken modulo how many there are: two greens, or gold and silver). */
  variant: number;
  x: number;
  y: number;
  /** Sideways speed in px/s. It eases toward what the wind asks for, so a gust shoves a piece instead of teleporting it. */
  vx: number;
  /** 0.6-1: how big this one is next to the others. Small ones also fall slower, which reads as depth. */
  scale: number;
  /** Where in its tumble it is, in radians: it is |cos| of its full width (coin) or height (bill) across, and the sign says which face shows. */
  flip: number;
  /** 1.5-3.5: radians of tumble per second, before the wind speeds it up. */
  flipRate: number;
  /** Where in its flutter it is, in radians: it sways side to side and rocks as this advances. */
  sway: number;
  /** 1.5-3: radians of flutter per second. */
  swayRate: number;
  /** The tilt it rocks around, in radians. */
  lean: number;
}

export interface Box {
  width: number;
  height: number;
  /** The size setting, which decides how far past an edge a piece is hidden. */
  size: number;
}

export interface Weather {
  seconds: number;
  /** Seconds since the rain started; the gusts are a function of it. */
  time: number;
  /** Fall speed of the biggest bill, in px/s. */
  fall: number;
  /** The wind setting, 0-10. */
  wind: number;
  /** How coins behave, from `coinFeel` (worked out once, not for every coin on every frame). */
  coin: Feel;
}

/** What a piece is drawn like right now. */
export interface Pose {
  /** Rotation in radians. */
  angle: number;
  /** 0.06-1: the fraction of its width (coin) or height (bill) it shows. */
  squash: number;
  /** Whether the back side is showing. */
  back: boolean;
  /** 0.6-1: 1 facing the viewer, darker the closer to edge-on. */
  shade: number;
}

/** Bills, coins, or every other one in turn. */
export function isCoin(index: number, kind: MoneyKind): boolean {
  return kind === "coins" || (kind === "mixed" && index % 2 === 1);
}

/** A piece at a random spot in the box, mid-tumble. */
export function newCash(index: number, kind: MoneyKind, { width, height }: Box): Cash {
  return {
    coin: isCoin(index, kind),
    variant: Math.floor(Math.random() * 2),
    x: Math.random() * width,
    y: Math.random() * height,
    vx: 0,
    scale: MIN_SCALE + Math.random() * (1 - MIN_SCALE),
    flip: Math.random() * TAU,
    flipRate: 1.5 + Math.random() * 2,
    sway: Math.random() * TAU,
    swayRate: 1.5 + Math.random() * 1.5,
    lean: (Math.random() - 0.5) * 0.6,
  };
}

/**
 * The wind at one spot: -1 is a full gust to the left, 1 a full gust to the right, and it changes smoothly.
 * Three waves of unrelated speeds never quite line up again, so it doesn't loop. Shifting the clock by
 * position makes a gust sweep across the screen from left to right, instead of shoving everything at once.
 */
export function gust(time: number, x: number, y: number): number {
  const t = time - x * 0.004 + y * 0.002;
  return (0.55 * Math.sin(t * 0.7) + 0.3 * Math.sin(t * 1.9 + 1.7) + 0.35 * Math.sin(t * 0.23 + 4)) / 1.2;
}

/** How strongly the air is rising at one spot, 0-1. It comes in bursts (two waves multiplied) and holds falling pieces up. */
export function updraft(time: number, x: number): number {
  const t = time - x * 0.003;
  return Math.max(0, Math.sin(t * 0.37 + 2) * Math.sin(t * 0.91));
}

/** Moves one piece for one frame: it falls, flutters, tumbles, and gets blown around. Leaving a side wraps to the other; leaving the bottom starts over at the top. */
export function moveCash(piece: Cash, { seconds, time, fall, wind, coin }: Weather, { width, height, size }: Box): void {
  const feel = piece.coin ? coin : BILL;
  const strength = wind / 10;

  // Sideways: the gust pushes (lighter pieces harder), and the piece's own flutter adds a wobble on top.
  const push = (gust(time, piece.x, piece.y) * wind * WIND_PX_PER_STEP) / feel.weight;
  const wobble = Math.sin(piece.sway) * feel.flutter * piece.scale;
  piece.vx += (push + wobble - piece.vx) * Math.min(1, feel.response * seconds);

  // Down: a face-on piece catches the air and hangs, an edge-on one slips through it, and an updraft can hold it up or even lift it.
  const slip = 1.2 - 0.4 * Math.abs(Math.cos(piece.flip));
  const lift = (updraft(time, piece.x) * strength) / feel.weight;
  const vy = fall * feel.fall * piece.scale * slip * (1 - lift);

  piece.x += piece.vx * seconds;
  piece.y += vy * seconds;
  // The wind also tumbles them faster (light bills much more than heavy coins).
  piece.flip = (piece.flip + piece.flipRate * feel.tumble * (1 + strength * feel.windTumble) * seconds) % TAU;
  piece.sway = (piece.sway + piece.swayRate * seconds) % TAU;

  const margin = size * OFFSCREEN_PER_SIZE;
  const span = width + 2 * margin;
  piece.x = ((((piece.x + margin) % span) + span) % span) - margin;
  if (piece.y > height + margin) {
    // Fell out of the bottom: come back in from above, somewhere new, a little later than the others so they don't arrive in a row.
    piece.x = Math.random() * width;
    piece.y = -margin - Math.random() * margin;
  } else if (piece.y < -margin) {
    piece.y = -margin; // lifted out of the top: wait there until it falls back
  }
}

/** How to draw a piece right now. */
export function pose(piece: Cash): Pose {
  const turn = Math.cos(piece.flip);
  const rock = piece.coin ? COIN_ROCK : BILL.rock;
  return {
    angle: piece.lean + Math.sin(piece.sway) * rock + piece.vx * LEAN_PER_PX_S,
    squash: Math.max(MIN_SQUASH, Math.abs(turn)),
    back: turn < 0,
    shade: EDGE_SHADE + (1 - EDGE_SHADE) * Math.abs(turn),
  };
}
