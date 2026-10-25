import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { DEFAULT_EFFECT_OPTIONS, HEX_COLOR } from "../../utils/theme";
import {
  buildTape,
  fieldSize,
  isLeftward,
  isOutlined,
  rowNumbers,
  tapeX,
  type Tape,
} from "../../utils/sloganMarquee";

const FONT_PER_SIZE = 1.5; // size 10-48 is the letters' scale (like the rain's); the slogans' font is 1.5 times that
const ROW_HEIGHT = 1.55; // times the font size
const SPEED = 0.6; // font heights per second, per step of the speed setting (the default, 4, is an easy read)
const FILLED_ALPHA = 0.8; // filled rows are the heavy ones behind small text, so they are eased back a little
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting

interface Row {
  /** How far this row has scrolled, in pixels. */
  offset: number;
  /** 0.8-1.2: this row's share of the speed, so rows drift apart instead of moving in lockstep. */
  pace: number;
}

/**
 * Slogans scrolling past in rows like a marquee, drawn on a canvas: rows lean at a set tilt, take turns
 * being filled or outlined, and (optionally) take turns going the other way. The whole field is drawn
 * rotated, so the text stays level within it. The parent must be `relative`; ThemeScope takes care of that.
 */
export default function ScrollingSlogans({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't reshuffle where every row is.
  const rows = useRef(new Map<number, Row>());
  const {
    size,
    speed,
    glow,
    slogan_color: colorOption,
    slogan_style: style,
    slogan_tilt: tiltDegrees,
    slogan_alternate: alternate,
  } = options;
  // The list is joined into one string so a new-but-identical array (each profile fetch makes one) doesn't restart the effect.
  // A slogan never contains a line break (the server tidies them to spaces), so it is a safe separator.
  const sloganKey = options.slogans.join("\n");

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const slogans = sloganKey ? sloganKey.split("\n") : DEFAULT_EFFECT_OPTIONS.slogans;
    const fontPx = size * FONT_PER_SIZE;
    const font = `italic 900 ${fontPx}px Impact, "Arial Black", Haettenschweiler, sans-serif`;
    const rowHeight = fontPx * ROW_HEIGHT;
    const pxPerSecond = speed * SPEED * fontPx;
    const tilt = (tiltDegrees * Math.PI) / 180;
    // The color is only used on a canvas, but still refuse anything that isn't a plain #rrggbb.
    const color = HEX_COLOR.test(colorOption) ? colorOption : DEFAULT_EFFECT_OPTIONS.slogan_color;
    let width = 0;
    let height = 0;
    let field = { x: 0, y: 0 };
    let rowList: number[] = [];
    let tapes = new Map<number, Tape>();
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    /** Works out which rows the box needs and what each one says; redone whenever the box or the text changes size. */
    const layout = () => {
      field = fieldSize(width, height, tilt);
      rowList = rowNumbers(field.y, rowHeight);
      ctx.font = font;
      const measure = (text: string) => ctx.measureText(text).width;
      tapes = new Map(rowList.map((row) => [row, buildTape(slogans, row, field.x, measure)]));
      for (const row of rowList) {
        if (!rows.current.has(row)) rows.current.set(row, { offset: Math.random() * 2000, pace: 0.8 + Math.random() * 0.4 });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.save();
      // Rotate the whole field about the middle of the box, then draw level rows in it.
      ctx.translate(width / 2, height / 2);
      ctx.rotate(tilt);
      ctx.font = font;
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";
      ctx.lineWidth = Math.max(1.2, fontPx * 0.05);
      ctx.fillStyle = color;
      ctx.strokeStyle = color;
      if (glow) {
        ctx.shadowColor = color;
        ctx.shadowBlur = fontPx * 0.3;
      }
      for (const row of rowList) {
        const tape = tapes.get(row);
        const state = rows.current.get(row);
        if (!tape || !state) continue;
        const x = tapeX(state.offset, tape.width, field.x, isLeftward(row, alternate));
        const y = row * rowHeight;
        const outlined = isOutlined(style, row);
        ctx.globalAlpha = outlined ? 1 : FILLED_ALPHA;
        const paint = (at: number) => (outlined ? ctx.strokeText(tape.text, at, y) : ctx.fillText(tape.text, at, y));
        paint(x);
        paint(x + tape.width);
      }
      ctx.restore();
    };

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      layout();
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      for (const row of rows.current.values()) row.offset += pxPerSecond * row.pace * seconds;
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
  }, [sloganKey, size, speed, glow, colorOption, style, tiltDegrees, alternate]);

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
