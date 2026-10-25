import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { HEX_COLOR } from "../../utils/theme";
import { moveLogo, type Logo } from "../../utils/dvdMotion";

// Logos change color on every wall hit, cycling through these (the sparkles use them too).
const COLORS = ["#ff3b30", "#ffcc00", "#34c759", "#00c7ff", "#7c5cff", "#ff2d95", "#ffffff"];
const PX_PER_SPEED = 30; // speed 1-10 -> 30-300 px per second (the default, 4, is a lazy screensaver drift)
const SLOPE = 0.75; // vertical speed relative to horizontal, so the path doesn't just trace a diagonal square
const FONT_PER_SIZE = 2; // size 10-48 is the letters' scale (like the rain's); the logo's font is twice that
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting
const CORNER_REACH = 0.3; // times the font size: how close to a corner a wall hit must be to count as a corner hit
const SPARKS = 56; // per corner hit
const MIN_BURST_SCALE = 30; // px; the burst is sized from the logo but never smaller than this, so it always reads as an event

interface Spark {
  x: number;
  y: number;
  vx: number;
  vy: number;
  age: number; // seconds so far
  life: number; // seconds it lasts
  radius: number;
  color: string;
}

interface Flash {
  x: number;
  y: number;
  age: number;
}
const FLASH_SECONDS = 0.5;

const randomColor = () => Math.floor(Math.random() * COLORS.length);

/** A 4-pointed sparkle centered on (x, y). */
function star(ctx: CanvasRenderingContext2D, x: number, y: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x, y - r);
  ctx.quadraticCurveTo(x, y, x + r, y); // each curve dips into the center, which makes the points
  ctx.quadraticCurveTo(x, y, x, y + r);
  ctx.quadraticCurveTo(x, y, x - r, y);
  ctx.quadraticCurveTo(x, y, x, y - r);
  ctx.fill();
}

/**
 * "DVD" logos bouncing around their parent like an old screensaver, drawn on a canvas. A logo that
 * lands in a corner sets off a burst of sparkles. The logo is drawn from text and shapes, not an
 * image, so it scales and recolors freely. The parent must be `relative`; ThemeScope takes care of that.
 */
export default function BouncingDvd({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't make the logos jump somewhere else.
  const logos = useRef<Logo[]>([]);
  const { size, speed, glow, count, color_change: changeColor, color } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const fontSize = size * FONT_PER_SIZE;
    const font = `italic 900 ${fontSize}px "Arial Black", Impact, sans-serif`;
    ctx.font = font;
    const logoWidth = ctx.measureText("DVD").width;
    const logoHeight = fontSize * 1.45; // the letters, then the disc under them
    const pxPerSecond = speed * PX_PER_SPEED;
    const burstScale = Math.max(fontSize, MIN_BURST_SCALE);
    // The color is only used on a canvas, but still refuse anything that isn't a plain #rrggbb.
    const fixedColor = HEX_COLOR.test(color) ? color : "#ffffff";
    let width = 0;
    let height = 0;
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;
    let sparks: Spark[] = [];
    let flashes: Flash[] = [];

    const bounds = () => ({
      maxX: Math.max(0, width - logoWidth),
      maxY: Math.max(0, height - logoHeight),
      reach: fontSize * CORNER_REACH,
    });

    const drawLogo = (logo: Logo) => {
      const fill = changeColor ? (COLORS[logo.color] ?? fixedColor) : fixedColor;
      ctx.fillStyle = fill;
      ctx.shadowColor = fill;
      ctx.shadowBlur = glow ? fontSize * 0.4 : 0;
      ctx.font = font;
      ctx.textBaseline = "top";
      ctx.fillText("DVD", logo.x, logo.y);

      // The disc: a flat ring under the letters.
      const cx = logo.x + logoWidth / 2;
      const cy = logo.y + fontSize * 1.2;
      const rx = logoWidth / 2;
      const ry = fontSize * 0.2;
      ctx.beginPath();
      ctx.moveTo(cx + rx, cy); // moveTo first, or the second ellipse would be joined to the first by a line
      ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
      ctx.moveTo(cx + rx * 0.5, cy);
      ctx.ellipse(cx, cy, rx * 0.5, ry * 0.5, 0, 0, Math.PI * 2);
      ctx.fill("evenodd"); // the inner ellipse becomes the hole
    };

    const drawBurst = () => {
      ctx.shadowBlur = 0;
      ctx.globalCompositeOperation = "lighter"; // overlapping light adds up, so the burst glows
      for (const flash of flashes) {
        const fade = 1 - flash.age / FLASH_SECONDS;
        const radius = burstScale * (2 + (1 - fade) * 3);
        const glowing = ctx.createRadialGradient(flash.x, flash.y, 0, flash.x, flash.y, radius);
        glowing.addColorStop(0, `rgba(255, 255, 255, ${0.7 * fade})`);
        glowing.addColorStop(1, "rgba(255, 255, 255, 0)");
        ctx.fillStyle = glowing;
        ctx.fillRect(flash.x - radius, flash.y - radius, radius * 2, radius * 2);
      }
      for (const spark of sparks) {
        const fade = 1 - spark.age / spark.life;
        ctx.globalAlpha = fade;
        ctx.fillStyle = spark.color;
        star(ctx, spark.x, spark.y, spark.radius * (0.4 + 0.6 * fade)); // shrinks as it dies
      }
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = "source-over";
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      logos.current.forEach(drawLogo);
      drawBurst();
    };

    /** Sparkles fly out of the corner the logo just hit, into the box. */
    const burst = (logo: Logo) => {
      const cornerX = logo.dx === 1 ? 0 : width; // the logo has already turned around, so dx tells which corner
      const cornerY = logo.dy === 1 ? 0 : height;
      const inward = Math.atan2(logo.dy, logo.dx);
      flashes.push({ x: cornerX, y: cornerY, age: 0 });
      for (let i = 0; i < SPARKS; i++) {
        const angle = inward + (Math.random() - 0.5) * Math.PI * 0.9;
        const velocity = burstScale * (3 + Math.random() * 7);
        sparks.push({
          x: cornerX,
          y: cornerY,
          vx: Math.cos(angle) * velocity,
          vy: Math.sin(angle) * velocity,
          age: 0,
          life: 0.8 + Math.random() * 0.8,
          radius: burstScale * (0.2 + Math.random() * 0.25),
          color: COLORS[randomColor()] ?? "#ffffff",
        });
      }
    };

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Add or drop logos to match the count, then pull every one back inside in case the box shrank.
      const { maxX, maxY } = bounds();
      const list = logos.current;
      while (list.length < count) {
        list.push({
          x: Math.random() * maxX,
          y: Math.random() * maxY,
          dx: Math.random() < 0.5 ? 1 : -1,
          dy: Math.random() < 0.5 ? 1 : -1,
          color: randomColor(),
        });
      }
      list.length = count;
      for (const logo of list) {
        logo.x = Math.min(logo.x, maxX);
        logo.y = Math.min(logo.y, maxY);
      }
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;

      for (const logo of logos.current) {
        const hit = moveLogo(logo, pxPerSecond * seconds, pxPerSecond * SLOPE * seconds, bounds());
        if (!hit) continue;
        // Pick a different color than the one it had (an offset of 1 to N-1 around the palette).
        logo.color = (logo.color + 1 + Math.floor(Math.random() * (COLORS.length - 1))) % COLORS.length;
        if (hit === "corner") burst(logo);
      }

      const drag = Math.pow(0.12, seconds); // sparks slow down quickly, like embers
      for (const spark of sparks) {
        spark.age += seconds;
        spark.x += spark.vx * seconds;
        spark.y += spark.vy * seconds;
        spark.vx *= drag;
        spark.vy *= drag;
      }
      for (const flash of flashes) flash.age += seconds;
      sparks = sparks.filter((spark) => spark.age < spark.life);
      flashes = flashes.filter((flash) => flash.age < FLASH_SECONDS);
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
  }, [size, speed, glow, count, changeColor, color]);

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
