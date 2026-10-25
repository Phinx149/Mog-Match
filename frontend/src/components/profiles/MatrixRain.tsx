import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { DEFAULT_EFFECT_OPTIONS, HEX_COLOR, RAIN_SYMBOLS } from "../../utils/theme";

const STEPS_PER_SPEED = 4; // speed 1-10 -> 4-40 rows fallen per second (the default, 4, is the original slow fall)
const MAX_STEPS_PER_FRAME = 3; // catch-up limit, e.g. right after the tab was in the background
const HUE_PER_COLUMN = 9; // degrees: neighboring columns differ a little, so the rainbow reads as a smooth sweep
const HUE_PER_STEP = 2; // degrees the whole rainbow drifts each step
const FADE = 0.12; // how much of the older letters is erased each step; lower = longer trails
const STATIC_STEPS = 40; // steps pre-drawn for people who prefer reduced motion

/**
 * Falling code (green unless it's tuned otherwise), drawn on a canvas that fills its parent. It is generated, not an image:
 * it fits any card size, never repeats or shows a seam, and costs no download.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function MatrixRain({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { size, speed, glow, rain_rainbow: rainbow } = options;
  const rainColor = options.rain_color;
  const symbolSet = options.rain_symbols;

  // Brightness is just the canvas opacity (below), so changing it never restarts the animation.
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const stepMs = 1000 / (speed * STEPS_PER_SPEED);
    // Both come from the server, but fall back rather than draw with something unexpected.
    const glyphs = (RAIN_SYMBOLS[symbolSet] ?? RAIN_SYMBOLS.katakana).glyphs;
    const color = HEX_COLOR.test(rainColor) ? rainColor : DEFAULT_EFFECT_OPTIONS.rain_color;
    let width = 0;
    let height = 0;
    let drops: number[] = []; // the row each column's falling letter is on
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastStep = 0;
    let steps = 0; // how many steps have been drawn; moves the rainbow along

    const step = () => {
      // Erase part of what is already there instead of repainting a background, so the canvas
      // stays transparent and the trails fade out over whatever color sits behind it.
      ctx.shadowBlur = 0; // a leftover glow would be "erased" as well, smearing the fade
      ctx.globalCompositeOperation = "destination-out";
      ctx.fillStyle = `rgba(0, 0, 0, ${FADE})`;
      ctx.fillRect(0, 0, width, height);
      ctx.globalCompositeOperation = "source-over";

      ctx.font = `${glow ? "bold " : ""}${size}px monospace`;
      drops.forEach((row, column) => {
        const letter = glyphs.charAt(Math.floor(Math.random() * glyphs.length));
        // A letter keeps the color it was drawn in while it fades, so the rainbow leaves colored trails.
        const fill = rainbow ? `hsl(${(column * HUE_PER_COLUMN + steps * HUE_PER_STEP) % 360} 100% 60%)` : color;
        ctx.fillStyle = fill;
        if (glow) {
          ctx.shadowColor = fill;
          ctx.shadowBlur = size * 0.7;
        }
        ctx.fillText(letter, column * size, row * size);
        // Once past the bottom, restart from the top at random so the columns drift out of sync.
        drops[column] = row * size > height && Math.random() > 0.96 ? 0 : row + 1;
      });
      steps++;
    };

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2); // 2x is plenty for text this dim
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Start each column somewhere random so the rain is already falling on first paint.
      const rows = height / size;
      drops = Array.from({ length: Math.ceil(width / size) }, () => Math.floor(Math.random() * rows));
      if (reduceMotion) for (let i = 0; i < STATIC_STEPS; i++) step(); // one still picture, no animation
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      if (!lastStep) lastStep = now;
      // Screens refresh every ~16 ms, so at high speeds more than one step can be due per frame.
      const due = Math.floor((now - lastStep) / stepMs);
      if (due < 1) return;
      lastStep += due * stepMs;
      for (let i = 0; i < Math.min(due, MAX_STEPS_PER_FRAME); i++) step();
    };
    const start = () => {
      if (!frame && !reduceMotion) frame = requestAnimationFrame(tick);
    };
    const stop = () => {
      cancelAnimationFrame(frame);
      frame = 0;
      lastStep = 0;
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
  }, [size, speed, glow, rainbow, rainColor, symbolSet]);

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
