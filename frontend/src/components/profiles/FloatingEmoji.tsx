import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { DEFAULT_EFFECT_OPTIONS } from "../../utils/theme";
import {
  aim,
  CELL_PER_SIZE,
  moveFloater,
  newFloater,
  waveAmplitude,
  waveOffset,
  type Floater,
} from "../../utils/emojiMotion";

const PX_PER_SPEED = 20; // speed 1-10 -> 20-200 px per second (the default, 4, is a slow drift)
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting
const EMOJI_FONT = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
const GLOW = "rgba(255, 255, 255, 0.9)";

/**
 * Emoji floating around their parent, drawn on a canvas: they drift in the chosen direction, optionally
 * wobbling or bouncing off the edges, and each one slowly spins. Every emoji is painted once onto a small
 * hidden canvas (a "sprite") and then stamped on each frame, so many of them stay cheap.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function FloatingEmoji({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't make the emoji jump somewhere else.
  const floaters = useRef<Floater[]>([]);
  const { size, speed, glow, emoji_count: count, emoji_angle: angle, emoji_path: path, emoji_spin: spin } = options;
  // The list is joined into one string so a new-but-identical array (each profile fetch makes one) doesn't restart the effect.
  // An emoji never contains a space, so it is a safe separator.
  const emojiKey = options.emojis.join(" ");

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const emojis = emojiKey ? emojiKey.split(" ") : DEFAULT_EFFECT_OPTIONS.emojis;
    const cell = size * CELL_PER_SIZE; // the square each emoji is drawn on, in CSS pixels
    const amplitude = waveAmplitude(size);
    const pxPerSecond = speed * PX_PER_SPEED;
    let width = 0;
    let height = 0;
    let dpr = 0;
    let sprites: HTMLCanvasElement[] = [];
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    const box = () => ({ width, height, size });

    /** One canvas per emoji, painted at the screen's pixel density so it stays sharp. */
    const buildSprites = () =>
      emojis.map((emoji) => {
        const sprite = document.createElement("canvas");
        sprite.width = sprite.height = Math.ceil(cell * dpr);
        const spriteCtx = sprite.getContext("2d");
        if (spriteCtx) {
          spriteCtx.font = `${size * dpr}px ${EMOJI_FONT}`;
          spriteCtx.textAlign = "center";
          spriteCtx.textBaseline = "middle";
          if (glow) {
            // Baked in here, once, rather than blurred again on every frame.
            spriteCtx.shadowColor = GLOW;
            spriteCtx.shadowBlur = size * dpr * 0.35;
          }
          spriteCtx.fillText(emoji, sprite.width / 2, sprite.height / 2);
        }
        return sprite;
      });

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      for (const floater of floaters.current) {
        const sprite = sprites[floater.emoji % sprites.length];
        if (!sprite) continue;
        const side = cell * floater.scale;
        const sway = path === "wave" ? waveOffset(floater, amplitude) : { x: 0, y: 0 };
        // Position and turn in one step: the matrix is "rotate by r, then move to (x, y)", times the pixel density.
        const cos = Math.cos(floater.rotation) * dpr;
        const sin = Math.sin(floater.rotation) * dpr;
        ctx.setTransform(cos, sin, -sin, cos, (floater.x + sway.x) * dpr, (floater.y + sway.y) * dpr);
        ctx.drawImage(sprite, -side / 2, -side / 2, side, side);
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const resize = () => {
      const nextDpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * nextDpr);
      canvas.height = Math.round(height * nextDpr);
      if (nextDpr !== dpr || !sprites.length) {
        dpr = nextDpr;
        sprites = buildSprites();
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Add or drop emoji to match the count; the first few keep their places.
      const list = floaters.current;
      const before = list.length;
      while (list.length < count) list.push(newFloater(list.length, box(), angle));
      list.length = count;
      // Small ones first, so bigger ones are drawn over them.
      if (list.length !== before) list.sort((a, b) => a.scale - b.scale);
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      const motion = { seconds, pxPerSecond, spin, path };
      for (const floater of floaters.current) moveFloater(floater, motion, box());
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

    // A changed direction applies to the emoji already floating, not just new ones.
    for (const floater of floaters.current) aim(floater, angle);

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
  }, [emojiKey, size, speed, glow, count, angle, path, spin]);

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
