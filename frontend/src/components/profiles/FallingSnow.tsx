import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import {
  CRYSTAL_DIAMETER_PER_SIZE,
  DOT_DIAMETER_PER_SIZE,
  isCrystal,
  moveFlake,
  newFlake,
  type Flake,
} from "../../utils/snowMotion";

const FALL_PX_PER_SPEED = 15; // speed 1-10 -> 15-150 px per second (the default, 4, is a gentle fall)
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting
const TAU = Math.PI * 2;
const SNOW = "#f4f9ff"; // white with a hint of blue, like snow in shade
const GLOW = "rgba(170, 215, 255, 0.95)";

/**
 * Where along an arm each pair of side branches sits (0 is the center, 1 the tip) and how long they are, as a
 * fraction of the arm. Each entry is one crystal drawing, so a fall of crystals isn't a field of clones.
 */
const CRYSTAL_DRAWINGS = [
  [
    { at: 0.4, length: 0.3 },
    { at: 0.7, length: 0.2 },
  ],
  [{ at: 0.55, length: 0.38 }],
];

/** One kind of flake, painted once. `side` is the sprite's width and height in CSS pixels, including the room around it for the glow. */
interface Look {
  sprite: HTMLCanvasElement;
  side: number;
}

/** A soft flake: a white ball that fades out toward its edge. */
function paintDot(c: CanvasRenderingContext2D, d: number, glow: boolean, glowBlur: number) {
  const radius = d / 2;
  const ball = c.createRadialGradient(radius, radius, 0, radius, radius, radius);
  ball.addColorStop(0, "rgba(255, 255, 255, 1)");
  ball.addColorStop(0.55, "rgba(255, 255, 255, 0.85)");
  ball.addColorStop(1, "rgba(255, 255, 255, 0)");
  if (glow) {
    c.shadowColor = GLOW;
    c.shadowBlur = glowBlur;
  }
  c.fillStyle = ball;
  c.beginPath();
  c.arc(radius, radius, radius, 0, TAU);
  c.fill();
}

/** A crystal: six arms, each with a pair of branches leaning outward at 60 degrees (or two pairs, depending on the drawing). */
function paintCrystal(c: CanvasRenderingContext2D, d: number, drawing: number, glow: boolean, glowBlur: number) {
  const radius = d / 2;
  const arm = radius * 0.92;
  c.strokeStyle = SNOW;
  c.lineWidth = Math.max(1, d * 0.07);
  c.lineCap = "round";
  if (glow) {
    c.shadowColor = GLOW;
    c.shadowBlur = glowBlur;
  }
  // The whole crystal is one path, so a halo is drawn once around all of it instead of once per stroke.
  c.beginPath();
  for (let k = 0; k < 6; k++) {
    const angle = (k * TAU) / 6;
    const dx = Math.cos(angle);
    const dy = Math.sin(angle);
    c.moveTo(radius, radius);
    c.lineTo(radius + dx * arm, radius + dy * arm);
    for (const { at, length } of CRYSTAL_DRAWINGS[drawing] ?? []) {
      const bx = radius + dx * arm * at;
      const by = radius + dy * arm * at;
      for (const lean of [-Math.PI / 3, Math.PI / 3]) {
        c.moveTo(bx, by);
        c.lineTo(bx + Math.cos(angle + lean) * arm * length, by + Math.sin(angle + lean) * arm * length);
      }
    }
  }
  c.stroke();
}

/**
 * Snow falling down their parent, drawn on a canvas: soft round flakes and/or six-armed crystals that drift
 * down, wobble as they go, and get blown sideways by a wind that surges and eases off. Nearer flakes are bigger,
 * faster and brighter than far ones. Each look is painted once onto a small hidden canvas (a "sprite") and then
 * stamped on each frame, so many flakes stay cheap. How things move lives in `utils/snowMotion.ts`.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function FallingSnow({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't make the flakes jump somewhere else, or the wind change course.
  const flakes = useRef<Flake[]>([]);
  const clock = useRef(Math.random() * 60); // seconds of weather so far; random, so two cards on screen don't surge in step
  const { size, speed, glow, snow_kind: kind, snow_count: count, snow_wind: wind } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const dotDiameter = size * DOT_DIAMETER_PER_SIZE;
    const crystalDiameter = size * CRYSTAL_DIAMETER_PER_SIZE;
    const room = glow ? size * 0.5 : 2; // CSS pixels around a flake inside its sprite, for the halo
    let width = 0;
    let height = 0;
    let dpr = 0;
    let dotLook: Look | null = null;
    let crystalLooks: Look[] = [];
    let built = false; // whether the looks above have been painted yet
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    const box = () => ({ width, height, size });

    /** A sprite `d` across (plus room), painted at the screen's pixel density so it stays sharp. */
    const makeLook = (d: number, paint: (c: CanvasRenderingContext2D) => void): Look => {
      const side = d + 2 * room;
      const sprite = document.createElement("canvas");
      sprite.width = sprite.height = Math.ceil(side * dpr);
      const c = sprite.getContext("2d");
      if (c) {
        c.scale(dpr, dpr);
        c.translate(room, room);
        paint(c);
      }
      return { sprite, side };
    };

    const buildLooks = () => {
      // A shadow's blur is measured in device pixels whatever the transform, hence the `dpr`.
      const glowBlur = size * 0.35 * dpr;
      dotLook = kind === "crystals" ? null : makeLook(dotDiameter, (c) => paintDot(c, dotDiameter, glow, glowBlur));
      crystalLooks =
        kind === "dots"
          ? []
          : CRYSTAL_DRAWINGS.map((_, drawing) =>
              makeLook(crystalDiameter, (c) => paintCrystal(c, crystalDiameter, drawing, glow, glowBlur)),
            );
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      for (const flake of flakes.current) {
        const look = flake.crystal ? crystalLooks[flake.variant % crystalLooks.length] : dotLook;
        if (!look) continue;
        const side = look.side * flake.scale;
        // Position and turn in one step: the matrix is "rotate by the turn, then move to (x, y)", times the pixel density.
        const cos = Math.cos(flake.turn) * dpr;
        const sin = Math.sin(flake.turn) * dpr;
        ctx.setTransform(cos, sin, -sin, cos, flake.x * dpr, flake.y * dpr);
        ctx.globalAlpha = flake.scale; // far-away flakes are fainter
        ctx.drawImage(look.sprite, -side / 2, -side / 2, side, side);
      }
      ctx.globalAlpha = 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const resize = () => {
      const nextDpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * nextDpr);
      canvas.height = Math.round(height * nextDpr);
      if (nextDpr !== dpr || !built) {
        dpr = nextDpr;
        buildLooks();
        built = true;
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Add or drop flakes to match the count; the first few keep their places.
      const list = flakes.current;
      const before = list.length;
      while (list.length < count) list.push(newFlake(list.length, kind, box()));
      list.length = count;
      // Small (far away) ones first, so bigger ones are drawn over them.
      if (list.length !== before) list.sort((a, b) => a.scale - b.scale);
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      clock.current += seconds;
      const weather = { seconds, time: clock.current, fall: speed * FALL_PX_PER_SPEED, wind };
      for (const flake of flakes.current) moveFlake(flake, weather, box());
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

    // A changed kind applies to the flakes already falling, not just new ones.
    flakes.current.forEach((flake, index) => {
      flake.crystal = isCrystal(index, kind);
    });

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
  }, [size, speed, glow, kind, count, wind]);

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
