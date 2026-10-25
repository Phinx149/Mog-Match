// The light cycles' rules (where they ride, when they turn and how long their trails are), kept apart from
// the canvas drawing so they are easy to read. Everything here is measured in grid cells, not pixels.

export interface Point {
  x: number;
  y: number;
}

/** The grid is `cols` by `rows` cells, so its crossings run from (0, 0) to (cols, rows). Cycles ride the lines between them. */
export interface Grid {
  cols: number;
  rows: number;
}

/** The four ways to ride, clockwise from east. Turning right is the next one in the list, turning left the one before it. */
const HEADINGS: readonly Point[] = [
  { x: 1, y: 0 },
  { x: 0, y: 1 },
  { x: -1, y: 0 },
  { x: 0, y: -1 },
];

export interface Cycle {
  /**
   * The trail from its tail to its head: the corners it has turned at, then the head last. Every stretch between two
   * points is straight along a grid line, and every corner is on a crossing.
   */
  path: Point[];
  /** An index into HEADINGS. */
  heading: number;
  /** Whole cells ridden since the last turn. */
  run: number;
}

const MIN_RUN = 2; // cells between turns at the least, so a trail never zigzags on the spot
const TURN_CHANCE = 0.25; // the chance of turning at each crossing after that (so runs average about 5 cells; edges cut some short)
const EPSILON = 1e-9; // adding up fractions of a cell drifts a little; this keeps a head that is "almost" on a crossing from skipping it

const pick = <T>(items: T[]): T | undefined => items[Math.floor(Math.random() * items.length)];

/** Whether one more cell in this heading from the crossing `at` still lands on the grid. */
function canRide({ cols, rows }: Grid, at: Point, heading: number): boolean {
  const step = HEADINGS[heading]!;
  const x = at.x + step.x;
  const y = at.y + step.y;
  return x >= 0 && x <= cols && y >= 0 && y <= rows;
}

/** Straight on, or a quarter-turn to the left or right. A cycle never turns back on itself, and never leaves the grid. */
function chooseHeading(cycle: Cycle, grid: Grid, at: Point): number {
  const ahead = canRide(grid, at, cycle.heading);
  if (ahead && (cycle.run < MIN_RUN || Math.random() > TURN_CHANCE)) return cycle.heading;
  // Blocked by the edge, or it felt like turning: either way, to a side that is still on the grid.
  const sideways = [(cycle.heading + 3) % 4, (cycle.heading + 1) % 4].filter((heading) => canRide(grid, at, heading));
  return pick(sideways) ?? cycle.heading;
}

/** How long a trail is, in cells. Every stretch is straight along an axis, so its length is just how far it goes in x plus y. */
export function trailLength(path: Point[]): number {
  let total = 0;
  for (let i = 1; i < path.length; i++) total += Math.abs(path[i]!.x - path[i - 1]!.x) + Math.abs(path[i]!.y - path[i - 1]!.y);
  return total;
}

/** Pulls the tail in until the trail is no longer than `tailCells`. */
function trim(path: Point[], tailCells: number): void {
  let excess = trailLength(path) - tailCells;
  while (excess > 0 && path.length > 1) {
    const tail = path[0]!;
    const next = path[1]!;
    const length = Math.abs(next.x - tail.x) + Math.abs(next.y - tail.y);
    if (length <= excess) {
      path.shift(); // that whole stretch is gone, so the corner after it is the new tail
      excess -= length;
    } else {
      tail.x += Math.sign(next.x - tail.x) * excess;
      tail.y += Math.sign(next.y - tail.y) * excess;
      break;
    }
  }
}

/** Rides `cells` further, turning at crossings along the way, and keeps the trail to `tailCells` long. */
export function advance(cycle: Cycle, grid: Grid, cells: number, tailCells: number): void {
  let left = cells;
  while (left > 0) {
    const head = cycle.path[cycle.path.length - 1]!;
    const step = HEADINGS[cycle.heading]!;
    const along = step.x !== 0 ? head.x : head.y; // the head's place on the line it is riding
    const direction = step.x + step.y; // 1 or -1
    const crossing = direction > 0 ? Math.floor(along + EPSILON) + 1 : Math.ceil(along - EPSILON) - 1; // the next whole number ahead
    const toCrossing = Math.abs(crossing - along);
    if (left < toCrossing) {
      head.x += step.x * left;
      head.y += step.y * left;
      break;
    }
    // Reach the crossing exactly, then decide where to go from there with whatever distance is left.
    if (step.x !== 0) head.x = crossing;
    else head.y = crossing;
    left -= toCrossing;
    cycle.run += 1;
    const heading = chooseHeading(cycle, grid, head);
    if (heading !== cycle.heading) {
      cycle.path.push({ x: head.x, y: head.y }); // the old head stays where it is as the corner
      cycle.heading = heading;
      cycle.run = 0;
    }
  }
  trim(cycle.path, tailCells);
}

/** A cycle at a random crossing, already a while into its ride so it starts with a full trail that has a bend or two in it. */
export function newCycle(grid: Grid, tailCells: number): Cycle {
  const head = { x: Math.floor(Math.random() * (grid.cols + 1)), y: Math.floor(Math.random() * (grid.rows + 1)) };
  const open = HEADINGS.map((_, heading) => heading).filter((heading) => canRide(grid, head, heading));
  const cycle: Cycle = { path: [head], heading: pick(open) ?? 0, run: 0 };
  advance(cycle, grid, tailCells * (1 + Math.random()), tailCells);
  return cycle;
}
