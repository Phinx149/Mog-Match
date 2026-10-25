// The snowfall's movement rules, kept apart from the canvas drawing so they are easy to read
// (and to check without a browser). Positions are the center of a flake, in pixels.

import type { SnowKind } from "../types/profile";

const TAU = Math.PI * 2;
const MIN_SCALE = 0.4; // the smallest a flake gets, next to the biggest at 1
const WIND_PX_PER_STEP = 12; // sideways speed of the biggest flake per point of the wind setting (wind 10 is about 120 px/s)
const SWAY_PX_PER_S = 14; // how hard a biggest flake's own wobble pushes it sideways
const RESPONSE = 1.5; // how quickly sideways speed catches up with what the wind asks for, per second
const OFFSCREEN_PER_SIZE = 2; // a flake is hidden once its center is this many sizes past an edge

/** Drawn sizes, as multiples of the size setting. A crystal needs room for its arms; a soft flake looks right smaller. */
export const DOT_DIAMETER_PER_SIZE = 0.6;
export const CRYSTAL_DIAMETER_PER_SIZE = 1;

export interface Flake {
  crystal: boolean;
  /** Which crystal drawing this one has (taken modulo how many there are). */
  variant: number;
  x: number;
  y: number;
  /** Sideways speed in px/s. It eases toward what the wind asks for, so a gust shoves a flake instead of teleporting it. */
  vx: number;
  /** 0.4-1: how big this one is next to the others. Small ones also fall slower and are drawn fainter, which reads as depth. */
  scale: number;
  /** 0.85-1.15: how much faster or slower than the others this one falls, so they don't keep in step. */
  drift: number;
  /** Where in its wobble it is, in radians. */
  sway: number;
  /** 1-2.5: radians of wobble per second. */
  swayRate: number;
  /** How far a crystal has turned, in radians. */
  turn: number;
  /** -0.6 to 0.6: radians of turn per second (negative is counter-clockwise). */
  turnRate: number;
}

export interface Box {
  width: number;
  height: number;
  /** The size setting, which decides how far past an edge a flake is hidden. */
  size: number;
}

export interface Weather {
  seconds: number;
  /** Seconds since the snow started; the gusts are a function of it. */
  time: number;
  /** Fall speed of the biggest flake, in px/s. */
  fall: number;
  /** The wind setting, -10 to 10. */
  wind: number;
}

/** Soft flakes, crystals, or every other one in turn. */
export function isCrystal(index: number, kind: SnowKind): boolean {
  return kind === "crystals" || (kind === "mixed" && index % 2 === 1);
}

/** A flake at a random spot in the box. */
export function newFlake(index: number, kind: SnowKind, { width, height }: Box): Flake {
  return {
    crystal: isCrystal(index, kind),
    variant: Math.floor(Math.random() * 2),
    x: Math.random() * width,
    y: Math.random() * height,
    vx: 0,
    scale: MIN_SCALE + Math.random() * (1 - MIN_SCALE),
    drift: 0.85 + Math.random() * 0.3,
    sway: Math.random() * TAU,
    swayRate: 1 + Math.random() * 1.5,
    turn: Math.random() * TAU,
    turnRate: (Math.random() - 0.5) * 1.2,
  };
}

/**
 * How strongly the wind is blowing right now, as a multiple of the setting (0.6-1.4). It surges and eases off,
 * and shifting the clock by position makes each surge sweep across the screen instead of hitting everything at once.
 */
export function surge(time: number, x: number): number {
  return 1 + 0.4 * Math.sin(time * 0.6 - x * 0.003);
}

/** Moves one flake for one frame: it falls, wobbles, and gets blown sideways. Leaving a side wraps to the other; leaving the bottom starts over at the top. */
export function moveFlake(flake: Flake, { seconds, time, fall, wind }: Weather, { width, height, size }: Box): void {
  // Sideways: the wind pushes (nearer, bigger flakes faster), and the flake's own wobble adds a sway on top.
  const push = wind * WIND_PX_PER_STEP * surge(time, flake.x) * flake.scale;
  const wobble = Math.sin(flake.sway) * SWAY_PX_PER_S * flake.scale;
  flake.vx += (push + wobble - flake.vx) * Math.min(1, RESPONSE * seconds);

  flake.x += flake.vx * seconds;
  flake.y += fall * flake.scale * flake.drift * seconds;
  flake.sway = (flake.sway + flake.swayRate * seconds) % TAU;
  flake.turn = (flake.turn + flake.turnRate * seconds) % TAU;

  const margin = size * OFFSCREEN_PER_SIZE;
  const span = width + 2 * margin;
  flake.x = ((((flake.x + margin) % span) + span) % span) - margin;
  if (flake.y > height + margin) {
    // Fell out of the bottom: come back in from above, somewhere new, a little later than the others so they don't arrive in a row.
    flake.x = Math.random() * width;
    flake.y = -margin - Math.random() * margin;
  }
}
