import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import {
  BRANCH_THICKNESS,
  MIN_GAP_SECONDS,
  newStrike,
  secondsToNextStrike,
  strikeBrightness,
  STRIKE_SECONDS,
  THICKNESS_PER_SIZE,
  type Point,
  type Strike,
} from "../../utils/lightningBolt";
import { DEFAULT_EFFECT_OPTIONS, HEX_COLOR } from "../../utils/theme";

const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of jumping ahead
// Waiting up to 9 seconds for the first strike would look like the effect is broken, so a strike is never further away than this
// after a setting changes, or after the card scrolls into view.
const AFTER_CHANGE_SECONDS = 0.6;
const AFTER_SCROLL_IN_SECONDS = 1.5;
const FLASH_STRENGTH = 0.28; // how opaque the sky's flash is at its brightest; kept soft so it never blinds
const CORE = "#ffffff"; // the middle of a bolt is white-hot whatever color its glow is

/** Draws every point joined by straight lines; the paths of one stroke call are all part of one path. */
function trace(c: CanvasRenderingContext2D, paths: Point[][]) {
  c.beginPath();
  for (const path of paths) {
    path.forEach((point, index) => (index === 0 ? c.moveTo(point.x, point.y) : c.lineTo(point.x, point.y)));
  }
}

/**
 * Lightning striking down their parent, drawn on a canvas: a jagged bolt with forks flashes in at a random spot, may
 * flicker back once, and fades; the sky around it lights up in the bolt's color. Every bolt is made up on the spot, so
 * no two strikes are alike. How bolts are shaped and timed lives in `utils/lightningBolt.ts`.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function LightningStorm({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't cut a strike short or make the next one come early.
  const strikes = useRef<Strike[]>([]);
  const wait = useRef(AFTER_CHANGE_SECONDS); // seconds until the next strike
  const sinceLast = useRef(MIN_GAP_SECONDS); // seconds since the last one started; strikes are never closer than MIN_GAP_SECONDS
  const { size, glow, lightning_color: colorOption, lightning_strikes: rate, lightning_forks: forks, lightning_flash: flash } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // It comes from the server, but fall back rather than draw with something unexpected.
    const color = HEX_COLOR.test(colorOption) ? colorOption : DEFAULT_EFFECT_OPTIONS.lightning_color;
    const thickness = size * THICKNESS_PER_SIZE;
    let width = 0;
    let height = 0;
    let dpr = 1;
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    /** The sky around a strike lights up: a wash of the bolt's color, brightest where the bolt starts. */
    const paintFlash = (strike: Strike, level: number) => {
      const x = strike.bolt.main[0]?.x ?? width / 2;
      const wash = ctx.createRadialGradient(x, 0, 0, x, 0, Math.max(width, height) * 1.2);
      wash.addColorStop(0, color);
      wash.addColorStop(1, `${color}00`); // the same color, fully clear, so the edge doesn't turn gray
      ctx.globalAlpha = level * FLASH_STRENGTH;
      ctx.fillStyle = wash;
      ctx.fillRect(0, 0, width, height);
    };

    /** Three strokes over each other, widest and dimmest first, so the bolt has a glowing edge and a white-hot core. */
    const paintBolt = ({ bolt }: Strike, level: number) => {
      const layers = glow
        ? [
            { scale: 6, alpha: 0.14, stroke: color },
            { scale: 2.8, alpha: 0.4, stroke: color },
            { scale: 1, alpha: 1, stroke: CORE },
          ]
        : [
            { scale: 2.4, alpha: 0.3, stroke: color },
            { scale: 1, alpha: 1, stroke: CORE },
          ];
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      for (const { scale, alpha, stroke } of layers) {
        ctx.globalAlpha = alpha * level;
        ctx.strokeStyle = stroke;
        // With the glow on, the core also throws a halo. A shadow's blur is measured in device pixels whatever the transform, hence the `dpr`.
        if (glow && scale === 1) {
          ctx.shadowColor = color;
          ctx.shadowBlur = Math.max(6, thickness * 5) * dpr;
        }
        trace(ctx, [bolt.main]);
        ctx.lineWidth = thickness * scale;
        ctx.stroke();
        trace(ctx, bolt.branches);
        ctx.lineWidth = thickness * scale * BRANCH_THICKNESS;
        ctx.stroke();
      }
      ctx.shadowBlur = 0;
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      for (const strike of strikes.current) {
        const level = strikeBrightness(strike);
        if (level <= 0) continue;
        if (flash) paintFlash(strike, level);
        paintBolt(strike, level);
      }
      ctx.globalAlpha = 1;
    };

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // People who prefer reduced motion get one bolt, frozen mid-flash.
      if (reduceMotion) strikes.current = [newStrike({ width, height }, forks)];
      draw(); // resizing clears a canvas, so paint right away
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      wait.current -= seconds;
      sinceLast.current += seconds;
      if (wait.current <= 0 && sinceLast.current >= MIN_GAP_SECONDS) {
        strikes.current.push(newStrike({ width, height }, forks));
        wait.current = secondsToNextStrike(rate);
        sinceLast.current = 0;
      }
      for (const strike of strikes.current) strike.age += seconds;
      strikes.current = strikes.current.filter((strike) => strike.age < STRIKE_SECONDS);
      draw();
    };
    const start = () => {
      if (frame || reduceMotion) return;
      wait.current = Math.min(wait.current, AFTER_SCROLL_IN_SECONDS);
      frame = requestAnimationFrame(tick);
    };
    const stop = () => {
      cancelAnimationFrame(frame);
      frame = 0;
      lastFrame = 0;
    };

    // A changed setting shows up in a moment. (Strikes still keep MIN_GAP_SECONDS apart, so dragging a slider can't make them flash faster.)
    wait.current = Math.min(wait.current, AFTER_CHANGE_SECONDS);

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
  }, [size, glow, colorOption, rate, forks, flash]);

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
