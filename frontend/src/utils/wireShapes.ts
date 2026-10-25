// The spinning shapes' geometry and math (what each shape is made of, how it turns and how it is squashed onto the
// screen), kept apart from the canvas drawing so they are easy to read. Every shape fits inside a ball of radius 1
// around its middle; the component scales that to pixels.

import type { ShapeKind } from "../types/profile";

export type Vec3 = [number, number, number];

/** A shape is dots in space (`vertices`) and which pairs of them are joined by a line (`edges`, as indexes into `vertices`). */
export interface Shape {
  vertices: Vec3[];
  edges: [number, number][];
}

/** How far the camera is from the middle of a shape, in shape radii. Nearer looks more dramatic, further looks flatter. */
export const CAMERA_DISTANCE = 3.5;

/** Scales a list of points so the furthest is exactly 1 from the middle. */
function fitToUnitBall(vertices: Vec3[]): Vec3[] {
  const furthest = Math.max(...vertices.map(([x, y, z]) => Math.hypot(x, y, z)));
  return vertices.map(([x, y, z]) => [x / furthest, y / furthest, z / furthest]);
}

/** Eight corners, and a line between every two that differ in just one direction. */
function cube(): Shape {
  const vertices: Vec3[] = [];
  for (let i = 0; i < 8; i++) vertices.push([i & 1 ? 1 : -1, i & 2 ? 1 : -1, i & 4 ? 1 : -1]);
  const edges: [number, number][] = [];
  for (let a = 0; a < 8; a++) {
    for (let b = a + 1; b < 8; b++) {
      const differing = a ^ b; // the bits (directions) in which the two corners differ
      if (differing === 1 || differing === 2 || differing === 4) edges.push([a, b]);
    }
  }
  return { vertices: fitToUnitBall(vertices), edges };
}

/** A donut: `around` points along the big ring, each the start of a small ring of `tube` points. */
function torus(around = 28, tube = 12, ringRadius = 1, tubeRadius = 0.4): Shape {
  const vertices: Vec3[] = [];
  const at = (u: number, v: number) => (u % around) * tube + (v % tube); // wraps, so the last joins up with the first
  for (let u = 0; u < around; u++) {
    for (let v = 0; v < tube; v++) {
      const big = (u / around) * Math.PI * 2;
      const small = (v / tube) * Math.PI * 2;
      const out = ringRadius + tubeRadius * Math.cos(small);
      vertices.push([out * Math.cos(big), tubeRadius * Math.sin(small), out * Math.sin(big)]);
    }
  }
  const edges: [number, number][] = [];
  for (let u = 0; u < around; u++) {
    for (let v = 0; v < tube; v++) {
      edges.push([at(u, v), at(u + 1, v)]); // along the big ring
      edges.push([at(u, v), at(u, v + 1)]); // around the tube
    }
  }
  return { vertices: fitToUnitBall(vertices), edges };
}

/** A globe: rings of latitude between two poles, joined by lines of longitude. */
function sphere(rings = 7, meridians = 16): Shape {
  const vertices: Vec3[] = [[0, 1, 0]]; // north pole
  for (let r = 1; r <= rings; r++) {
    const latitude = Math.PI * (r / (rings + 1)); // 0 at the north pole, PI at the south
    for (let m = 0; m < meridians; m++) {
      const longitude = (m / meridians) * Math.PI * 2;
      vertices.push([Math.sin(latitude) * Math.cos(longitude), Math.cos(latitude), Math.sin(latitude) * Math.sin(longitude)]);
    }
  }
  vertices.push([0, -1, 0]); // south pole
  const south = vertices.length - 1;
  const at = (ring: number, meridian: number) => 1 + (ring - 1) * meridians + (meridian % meridians);

  const edges: [number, number][] = [];
  for (let m = 0; m < meridians; m++) {
    edges.push([0, at(1, m)]);
    for (let r = 1; r < rings; r++) edges.push([at(r, m), at(r + 1, m)]);
    edges.push([at(rings, m), south]);
  }
  for (let r = 1; r <= rings; r++) {
    for (let m = 0; m < meridians; m++) edges.push([at(r, m), at(r, m + 1)]);
  }
  return { vertices: fitToUnitBall(vertices), edges };
}

const BUILDERS: Record<ShapeKind, () => Shape> = { cube, torus, sphere };
const built = new Map<ShapeKind, Shape>();

/** The shape's points and lines. Built once and shared, so nobody should change them. */
export function buildShape(kind: ShapeKind): Shape {
  let shape = built.get(kind);
  if (!shape) {
    shape = BUILDERS[kind]();
    built.set(kind, shape);
  }
  return shape;
}

/**
 * Turns every point of `shape` by the three angles (radians, around the x, y and z axes in that order) and writes the
 * result into `out`, which is reused from frame to frame instead of making a new list every time.
 */
export function rotate(shape: Shape, [ax, ay, az]: Vec3, out: Vec3[]): void {
  const [sx, cx, sy, cy, sz, cz] = [Math.sin(ax), Math.cos(ax), Math.sin(ay), Math.cos(ay), Math.sin(az), Math.cos(az)];
  shape.vertices.forEach(([x, y, z], i) => {
    const y1 = y * cx - z * sx; // around x
    const z1 = y * sx + z * cx;
    const x2 = x * cy + z1 * sy; // around y
    const z2 = -x * sy + z1 * cy;
    const point = (out[i] ??= [0, 0, 0]);
    point[0] = x2 * cz - y1 * sz; // around z
    point[1] = x2 * sz + y1 * cz;
    point[2] = z2;
  });
}

/** How much bigger a point looks when it is `z` toward the camera (negative: away from it). 1 in the middle. */
export function perspective(z: number): number {
  return CAMERA_DISTANCE / (CAMERA_DISTANCE - z);
}

/** One shape's own way of tumbling, so shapes on screen together don't turn in step. */
export interface Spinner {
  /** Where it starts, as angles. */
  start: Vec3;
  /** How fast it turns around each axis, in radians per unit of the clock. Mostly around y, so it spins more than it tumbles. */
  turn: Vec3;
  /** Where in its slow up-and-down drift it starts. */
  bob: number;
}

const between = (low: number, high: number) => low + Math.random() * (high - low);
const either = () => (Math.random() < 0.5 ? -1 : 1);

export function newSpinner(): Spinner {
  return {
    start: [between(0, Math.PI * 2), between(0, Math.PI * 2), between(0, Math.PI * 2)],
    turn: [either() * between(0.3, 0.6), either() * between(0.8, 1.2), either() * between(0.1, 0.3)],
    bob: between(0, Math.PI * 2),
  };
}

/** The angles a spinner has reached once the clock has run for `clock`. */
export function anglesAt({ start, turn }: Spinner, clock: number): Vec3 {
  return [start[0] + turn[0] * clock, start[1] + turn[1] * clock, start[2] + turn[2] * clock];
}

/**
 * Where each of `count` shapes sits in a box, as fractions of its width and height (0-1). One shape sits right of
 * center, in the room beside a card's name and photo; several spread evenly across.
 */
export function slots(count: number): { x: number; y: number }[] {
  if (count === 1) return [{ x: 0.72, y: 0.5 }];
  return Array.from({ length: count }, (_, i) => ({ x: 0.12 + (0.76 * i) / (count - 1), y: i % 2 === 0 ? 0.42 : 0.58 }));
}
