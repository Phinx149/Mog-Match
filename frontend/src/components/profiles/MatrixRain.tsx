import { useEffect, useRef } from "react";

// Half-width katakana and digits, like the film.
const GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789";
const FONT_SIZE = 14; // px; also the column width and row height
const FRAME_MS = 60; // ~16 fps: a slow, steady fall, and cheap when Discover shows many cards
const FADE = 0.12; // how much of the older letters is erased each frame; lower = longer trails
const STATIC_STEPS = 40; // frames pre-drawn for people who prefer reduced motion

/**
 * Falling green code, drawn on a canvas that fills its parent. It is generated, not an image:
 * it fits any card size, never repeats or shows a seam, and costs no download.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let width = 0;
    let height = 0;
    let drops: number[] = []; // the row each column's falling letter is on
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastDraw = 0;

    const step = () => {
      // Erase part of what is already there instead of repainting a background, so the canvas
      // stays transparent and the trails fade out over whatever color sits behind it.
      ctx.globalCompositeOperation = "destination-out";
      ctx.fillStyle = `rgba(0, 0, 0, ${FADE})`;
      ctx.fillRect(0, 0, width, height);
      ctx.globalCompositeOperation = "source-over";

      ctx.fillStyle = "#22ff66";
      ctx.font = `${FONT_SIZE}px monospace`;
      drops.forEach((row, column) => {
        const letter = GLYPHS.charAt(Math.floor(Math.random() * GLYPHS.length));
        ctx.fillText(letter, column * FONT_SIZE, row * FONT_SIZE);
        // Once past the bottom, restart from the top at random so the columns drift out of sync.
        drops[column] = row * FONT_SIZE > height && Math.random() > 0.96 ? 0 : row + 1;
      });
    };

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2); // 2x is plenty for text this dim
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Start each column somewhere random so the rain is already falling on first paint.
      const rows = height / FONT_SIZE;
      drops = Array.from({ length: Math.ceil(width / FONT_SIZE) }, () => Math.floor(Math.random() * rows));
      if (reduceMotion) for (let i = 0; i < STATIC_STEPS; i++) step(); // one still picture, no animation
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      if (now - lastDraw < FRAME_MS) return;
      lastDraw = now;
      step();
    };
    const start = () => {
      if (!frame && !reduceMotion) frame = requestAnimationFrame(tick);
    };
    const stop = () => {
      cancelAnimationFrame(frame);
      frame = 0;
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
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      // -z-10 puts it behind the content (ThemeScope isolates the stacking); dim enough that text stays readable.
      className="pointer-events-none absolute inset-0 -z-10 size-full rounded-[inherit] opacity-40"
    />
  );
}
