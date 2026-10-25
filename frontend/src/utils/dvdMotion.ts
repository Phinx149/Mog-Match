// The bouncing logo's movement rules, kept apart from the canvas drawing so they are easy to read
// (and to check without a browser). Positions are the logo's top-left corner in pixels.

export interface Logo {
  x: number;
  y: number;
  dx: 1 | -1;
  dy: 1 | -1;
  /** Index into the color palette; only used while colors change on each bounce. */
  color: number;
}

export interface Bounds {
  /** Furthest x / y the logo's top-left corner may reach (the box size minus the logo size). */
  maxX: number;
  maxY: number;
  /** A wall hit this close to a corner, heading into it, counts as a corner hit. */
  reach: number;
}

export type Hit = "corner" | "wall" | null;

/**
 * Moves a logo by `moveX` / `moveY` pixels along its direction and bounces it off the walls.
 *
 * A pixel-perfect corner hit almost never happens by chance, so a bounce that lands within `reach`
 * of a corner counts too: the logo is nudged into the corner and bounces back on both axes.
 * Returns what it hit, so the caller can change color or throw sparkles.
 */
export function moveLogo(logo: Logo, moveX: number, moveY: number, { maxX, maxY, reach }: Bounds): Hit {
  logo.x += logo.dx * moveX;
  logo.y += logo.dy * moveY;

  // `max > 0`: in a box smaller than the logo there is nowhere to bounce.
  let hitX = maxX > 0 && (logo.x <= 0 || logo.x >= maxX);
  let hitY = maxY > 0 && (logo.y <= 0 || logo.y >= maxY);

  // Hit one wall while still heading for the other one, and only just short of it: that's a corner.
  if (hitX && !hitY && maxY > 0) {
    hitY = (logo.dy === -1 && logo.y < reach) || (logo.dy === 1 && logo.y > maxY - reach);
  } else if (hitY && !hitX && maxX > 0) {
    hitX = (logo.dx === -1 && logo.x < reach) || (logo.dx === 1 && logo.x > maxX - reach);
  }

  if (hitX) {
    logo.x = logo.x < maxX / 2 ? 0 : maxX; // also pulls a logo that overshot the wall back inside
    logo.dx = logo.x === 0 ? 1 : -1;
  }
  if (hitY) {
    logo.y = logo.y < maxY / 2 ? 0 : maxY;
    logo.dy = logo.y === 0 ? 1 : -1;
  }
  return hitX && hitY ? "corner" : hitX || hitY ? "wall" : null;
}
