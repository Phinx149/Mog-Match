import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { advance, newCycle, type Cycle, type Grid, type Point } from "../../utils/lightCycles";
import { DEFAULT_EFFECT_OPTIONS, HEX_COLOR } from "../../utils/theme";

const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of jumping ahead
const CELL_PER_SIZE = 2; // the size setting, 10-48, is a grid cell of 20-96 pixels
const MIN_CELLS = 2; // fewest columns and rows, so there is always somewhere to turn
const LINE_PER_CELL = 0.07; // how thick a trail is, as a fraction of a cell (but never under MIN_LINE pixels)
const MIN_LINE = 1.5;
const CELLS_PER_SECOND = { base: 1.5, perSpeed: 0.9 }; // speed 1-10 is 2.4-10.5 cells a second (the default, 4, is 5)
const CELLS_PER_TAIL = { base: 2, perStep: 2.5 }; // trail length 1-10 is 4.5-27 cells
const GRID_ALPHA = 0.14;
const CORE = "#ffffff"; // the middle of a trail and its head are white-hot whatever color the cycle is

/** A color with an opacity, as the 8-digit hex a canvas understands. `color` must be a plain `#rrggbb`. */
const withAlpha = (color: string, alpha: number) => `${color}${Math.round(Math.min(Math.max(alpha, 0), 1) * 255).toString(16).padStart(2, "0")}`;

/**
 * Light cycles riding a grid, drawn on a canvas: glowing trails that run straight along the grid lines and turn
 * only at crossings, always by a quarter-turn, each with a white-hot head and a tail that fades away. How they
 * ride and turn lives in `utils/lightCycles.ts`; this draws them.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function LightCycles({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't send the cycles somewhere else.
  const cycles = useRef<Cycle[]>([]);
  const gridOf = useRef<Grid>({ cols: 0, rows: 0 }); // the grid those cycles ride; they are made again if it changes shape
  const { size, speed, glow, tron_color: colorOption, tron_cycles: count, tron_tail: tail, tron_grid: showGrid } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // It comes from the server, but fall back rather than draw with something unexpected.
    const color = HEX_COLOR.test(colorOption) ? colorOption : DEFAULT_EFFECT_OPTIONS.tron_color;
    const cell = size * CELL_PER_SIZE; // pixels
    const line = Math.max(MIN_LINE, cell * LINE_PER_CELL); // pixels
    const cellsPerSecond = CELLS_PER_SECOND.base + speed * CELLS_PER_SECOND.perSpeed;
    const tailCells = CELLS_PER_TAIL.base + tail * CELLS_PER_TAIL.perStep;
    let width = 0;
    let height = 0;
    let dpr = 1;
    let grid: Grid = { cols: MIN_CELLS, rows: MIN_CELLS };
    let originX = 0; // where the grid's (0, 0) is in pixels: the grid is centered, so the spare room is split evenly
    let originY = 0;
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    const toPixels = ({ x, y }: Point): Point => ({ x: originX + x * cell, y: originY + y * cell });

    /** Faint lines in the cycles' color, continuing the grid out to the card's edges (the cycles stay in from them). */
    const paintGrid = () => {
      ctx.strokeStyle = withAlpha(color, GRID_ALPHA);
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = originX % cell; x <= width; x += cell) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
      }
      for (let y = originY % cell; y <= height; y += cell) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
      }
      ctx.stroke();
    };

    /**
     * A trail is drawn a stretch at a time, each a straight line with its own gradient from how bright the trail is
     * where the stretch starts to how bright it is where it ends: brightest at the head, gone at the tail. The layers go
     * widest and dimmest first, so the trail has a soft halo (with the glow on), its color, and a thin white-hot core.
     */
    const paintTrail = ({ path }: Cycle) => {
      // How far each point is from the head along the trail, in cells.
      const fromHead = new Array<number>(path.length).fill(0);
      for (let i = path.length - 2; i >= 0; i--) {
        fromHead[i] = fromHead[i + 1]! + Math.abs(path[i + 1]!.x - path[i]!.x) + Math.abs(path[i + 1]!.y - path[i]!.y);
      }
      const brightness = (cells: number) => Math.max(0, 1 - cells / tailCells) ** 1.5;
      const layers = [
        ...(glow ? [{ scale: 4, alpha: 0.16, stroke: color }] : []),
        { scale: 1, alpha: 0.9, stroke: color },
        { scale: 0.35, alpha: 0.9, stroke: CORE },
      ];
      ctx.lineCap = "square"; // reaches a half-width past each end, so two stretches meet in a clean corner
      for (const { scale, alpha, stroke } of layers) {
        // With the glow on, the colored line also throws a halo. A shadow's blur is measured in device pixels whatever the transform, hence the `dpr`.
        if (glow && scale === 1) {
          ctx.shadowColor = color;
          ctx.shadowBlur = line * 4 * dpr;
        }
        ctx.lineWidth = line * scale;
        for (let i = 0; i + 1 < path.length; i++) {
          const from = toPixels(path[i]!);
          const to = toPixels(path[i + 1]!);
          if (from.x === to.x && from.y === to.y) continue; // a corner the head has only just turned at
          const fade = ctx.createLinearGradient(from.x, from.y, to.x, to.y);
          fade.addColorStop(0, withAlpha(stroke, alpha * brightness(fromHead[i]!)));
          fade.addColorStop(1, withAlpha(stroke, alpha * brightness(fromHead[i + 1]!)));
          ctx.strokeStyle = fade;
          ctx.beginPath();
          ctx.moveTo(from.x, from.y);
          ctx.lineTo(to.x, to.y);
          ctx.stroke();
        }
        ctx.shadowBlur = 0;
      }
      // The head: a small white square, with a halo in the cycle's color when the glow is on.
      const head = toPixels(path[path.length - 1]!);
      const half = line * 0.9;
      if (glow) {
        ctx.shadowColor = color;
        ctx.shadowBlur = line * 6 * dpr;
      }
      ctx.fillStyle = CORE;
      ctx.fillRect(head.x - half, head.y - half, half * 2, half * 2);
      ctx.shadowBlur = 0;
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      if (showGrid) paintGrid();
      for (const cycle of cycles.current) paintTrail(cycle);
    };

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // One cell fewer than fit, so the outermost lines are at least half a cell in from the edge and a trail is never cut off by it.
      grid = { cols: Math.max(MIN_CELLS, Math.floor(width / cell) - 1), rows: Math.max(MIN_CELLS, Math.floor(height / cell) - 1) };
      originX = (width - grid.cols * cell) / 2;
      originY = (height - grid.rows * cell) / 2;

      // Cycles are placed on the grid, so a grid of another shape needs new ones. Otherwise keep what is riding,
      // and just add or drop cycles to match the count.
      const list = cycles.current;
      if (grid.cols !== gridOf.current.cols || grid.rows !== gridOf.current.rows) list.length = 0;
      gridOf.current = grid;
      while (list.length < count) list.push(newCycle(grid, tailCells));
      list.length = count;
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      for (const cycle of cycles.current) advance(cycle, grid, seconds * cellsPerSecond, tailCells);
      draw();
    };
    const start = () => {
      if (!frame && !reduceMotion) frame = requestAnimationFrame(tick);
    };
    const stop = () => {
      cancelAnimationFrame(frame);
      frame = 0;
      lastFrame = 0;
    };

    // Only animate while on screen: Discover can list many themed cards, most scrolled out of view.
    const resizeObserver = new ResizeObserver(resize);
    const visibilityObserver = new IntersectionObserver(([entry]) => (entry?.isIntersecting ? start() : stop()));
    resizeObserver.observe(canvas);
    visibilityObserver.observe(canvas);
    return () => {
      stop();
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
    };
  }, [size, speed, glow, colorOption, count, tail, showGrid]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      style={{ opacity: options.brightness / 100 }}
      // -z-10 puts it behind the content (ThemeScope isolates the stacking).
      className="pointer-events-none absolute inset-0 -z-10 size-full rounded-[inherit]"
    />
  );
}
