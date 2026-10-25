// The floating emoji's movement rules, kept apart from the canvas drawing so they are easy to read
// (and to check without a browser). Positions are the center of an emoji, in pixels.

import type { EmojiPath } from "../types/profile";

const TAU = Math.PI * 2;
const MIN_SCALE = 0.6; // the smallest an emoji gets, next to the biggest at 1
const WAVE_PX_PER_RADIAN = 30; // distance travelled per radian of wobble, so a wave keeps its shape at any speed
const SPIN_RADIANS = TAU / 10; // a spin setting of 10 is one full turn per second
const GLYPH_HALF_PER_SIZE = 0.6; // an emoji is a bit wider than its font size; this is half of that

/** Each emoji is drawn on a square this many times its size, which leaves room for the glow and for turning. */
export const CELL_PER_SIZE = 2.4;

/** How far a wave-path emoji strays to each side of its line. */
export const waveAmplitude = (size: number) => Math.max(20, size * 1.5);

export interface Floater {
  /** Which emoji this one shows: an index into the list (taken modulo its length, so a shorter list is fine). */
  emoji: number;
  x: number;
  y: number;
  /** Unit direction of travel. Bouncing flips its signs. */
  dx: number;
  dy: number;
  /** 0.6-1: how big this one is next to the others. Small ones also move slower, which reads as depth. */
  scale: number;
  /** Current rotation in radians. */
  rotation: number;
  /** 0.5-1.5: this one's share of the spin setting, so they don't all turn in step. */
  turn: number;
  /** How far along the wave this one is, in radians. Only the wave path draws it. */
  wave: number;
}

export interface Box {
  width: number;
  height: number;
  /** The emoji size setting, which decides how far past an edge an emoji is hidden, or how close it may get when bouncing. */
  size: number;
}

export interface Motion {
  seconds: number;
  /** Speed of the biggest emoji. */
  pxPerSecond: number;
  /** The spin setting, -10 to 10. */
  spin: number;
  path: EmojiPath;
}

/** Points a floater along `degrees`: 0 is right and 90 is down, like a rotation on the screen. */
export function aim(floater: Floater, degrees: number): void {
  const radians = (degrees * Math.PI) / 180;
  floater.dx = Math.cos(radians);
  floater.dy = Math.sin(radians);
}

/** A floater at a random spot in the box. */
export function newFloater(emoji: number, { width, height }: Box, degrees: number): Floater {
  const floater: Floater = {
    emoji,
    x: Math.random() * width,
    y: Math.random() * height,
    dx: 1,
    dy: 0,
    scale: MIN_SCALE + Math.random() * (1 - MIN_SCALE),
    rotation: Math.random() * TAU,
    turn: 0.5 + Math.random(),
    wave: Math.random() * TAU,
  };
  aim(floater, degrees);
  return floater;
}

/** Wraps `value` into [-margin, size + margin), so leaving one side means coming back in on the other. */
function wrap(value: number, size: number, margin: number): number {
  const span = size + 2 * margin;
  return ((((value + margin) % span) + span) % span) - margin;
}

/** Moves and turns a floater for one frame. Straight and wave paths wrap around the edges; bounce reflects off them. */
export function moveFloater(floater: Floater, { seconds, pxPerSecond, spin, path }: Motion, { width, height, size }: Box): void {
  const distance = pxPerSecond * floater.scale * seconds;
  floater.x += floater.dx * distance;
  floater.y += floater.dy * distance;
  floater.wave += distance / WAVE_PX_PER_RADIAN;
  floater.rotation = (floater.rotation + floater.turn * spin * SPIN_RADIANS * seconds) % TAU;

  if (path === "bounce") {
    // The edge is where the emoji itself stops, not its padding. In a box too small for it, it sits in the middle.
    const inset = size * GLYPH_HALF_PER_SIZE * floater.scale;
    const lowX = Math.min(inset, width / 2);
    const lowY = Math.min(inset, height / 2);
    if (floater.x < lowX) {
      floater.x = lowX;
      floater.dx = Math.abs(floater.dx);
    } else if (floater.x > width - lowX) {
      floater.x = width - lowX;
      floater.dx = -Math.abs(floater.dx);
    }
    if (floater.y < lowY) {
      floater.y = lowY;
      floater.dy = Math.abs(floater.dy);
    } else if (floater.y > height - lowY) {
      floater.y = height - lowY;
      floater.dy = -Math.abs(floater.dy);
    }
    return;
  }

  // Far enough out that the whole padded square (and the wave's swing) is hidden before it jumps to the other side.
  const margin = (size * CELL_PER_SIZE) / 2 + (path === "wave" ? waveAmplitude(size) : 0);
  floater.x = wrap(floater.x, width, margin);
  floater.y = wrap(floater.y, height, margin);
}

/** How far to the side of its line a wave-path floater is drawn: perpendicular to where it's heading. */
export function waveOffset(floater: Floater, amplitude: number): { x: number; y: number } {
  const swing = Math.sin(floater.wave) * amplitude;
  return { x: -floater.dy * swing, y: floater.dx * swing };
}
