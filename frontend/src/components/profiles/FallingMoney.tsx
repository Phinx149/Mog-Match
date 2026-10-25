import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import {
  BILL_ASPECT,
  BILL_LENGTH_PER_SIZE,
  COIN_DIAMETER_PER_SIZE,
  coinFeel,
  isCoin,
  moveCash,
  newCash,
  pose,
  type Cash,
} from "../../utils/moneyMotion";

const FALL_PX_PER_SPEED = 20; // speed 1-10 -> 20-200 px per second (the default, 4, is a steady shower)
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting
const TAU = Math.PI * 2;
const FONT = '"Arial Black", Impact, system-ui, sans-serif';
const BILL_GLOW = "rgba(120, 255, 150, 0.9)";
const COIN_GLOW = "rgba(255, 215, 90, 0.9)";

// Two looks for each kind, so a shower isn't a row of clones. The first is the green of a real dollar bill.
const BILL_TONES = [
  { face: "#85bb65", back: "#5f9448", line: "#3d6b2b", medallion: "#a9d68d", ink: "#2a4d1c" },
  { face: "#4aa36a", back: "#2f7a4d", line: "#1d5638", medallion: "#7fcf9b", ink: "#123d27" },
];
const COIN_TONES = [
  { rim: "#b8860b", face: "#f6c945", shine: "#fff0b0", ink: "#8a5a00" }, // gold
  { rim: "#6b7685", face: "#d4dae2", shine: "#ffffff", ink: "#4d5866" }, // silver
];

type BillTone = (typeof BILL_TONES)[number];
type CoinTone = (typeof COIN_TONES)[number];

/** One kind of piece, painted once for each side. `width` and `height` are in CSS pixels and include the room around it for the glow. */
interface Look {
  front: HTMLCanvasElement;
  back: HTMLCanvasElement;
  width: number;
  height: number;
}

/** A bill: a rounded rectangle with a border, a medallion and a dollar sign (the back has no sign and is darker). */
function paintBill(c: CanvasRenderingContext2D, w: number, h: number, tone: BillTone, side: "front" | "back", glow: boolean, glowBlur: number) {
  const inset = h * 0.1;
  c.fillStyle = side === "front" ? tone.face : tone.back;
  if (glow) {
    // The halo goes on the outline only; the details drawn over it would each get their own and turn muddy.
    c.shadowColor = BILL_GLOW;
    c.shadowBlur = glowBlur;
  }
  c.beginPath();
  c.roundRect(0, 0, w, h, h * 0.1);
  c.fill();
  c.shadowColor = "transparent";
  c.shadowBlur = 0;

  c.strokeStyle = tone.line;
  c.lineWidth = Math.max(1, h * 0.05);
  c.beginPath();
  c.roundRect(inset, inset, w - 2 * inset, h - 2 * inset, h * 0.06);
  c.stroke();

  c.fillStyle = tone.medallion;
  c.beginPath();
  c.ellipse(w / 2, h / 2, h * 0.3, h * 0.3, 0, 0, TAU);
  c.fill();
  c.stroke();

  if (side === "front") {
    c.fillStyle = tone.ink;
    c.font = `900 ${h * 0.4}px ${FONT}`;
    c.textAlign = "center";
    c.textBaseline = "middle";
    c.fillText("$", w / 2, h / 2 + h * 0.02);
    // Small corner marks, like the numerals on a real bill.
    const corner = inset * 1.8;
    for (const x of [corner, w - corner]) {
      for (const y of [corner, h - corner]) {
        c.beginPath();
        c.arc(x, y, h * 0.035, 0, TAU);
        c.fill();
      }
    }
  }
}

/** A coin: a rim, a shiny face, an inner ring and a dollar sign. Both sides look the same. */
function paintCoin(c: CanvasRenderingContext2D, d: number, tone: CoinTone, glow: boolean, glowBlur: number) {
  const radius = d / 2;
  c.fillStyle = tone.rim;
  if (glow) {
    c.shadowColor = COIN_GLOW;
    c.shadowBlur = glowBlur;
  }
  c.beginPath();
  c.arc(radius, radius, radius, 0, TAU);
  c.fill();
  c.shadowColor = "transparent";
  c.shadowBlur = 0;

  const shine = c.createRadialGradient(d * 0.38, d * 0.34, d * 0.04, radius, radius, radius);
  shine.addColorStop(0, tone.shine);
  shine.addColorStop(1, tone.face);
  c.fillStyle = shine;
  c.beginPath();
  c.arc(radius, radius, radius * 0.88, 0, TAU);
  c.fill();

  c.strokeStyle = tone.rim;
  c.lineWidth = Math.max(1, d * 0.04);
  c.beginPath();
  c.arc(radius, radius, radius * 0.7, 0, TAU);
  c.stroke();

  c.fillStyle = tone.ink;
  c.font = `900 ${d * 0.5}px ${FONT}`;
  c.textAlign = "center";
  c.textBaseline = "middle";
  c.fillText("$", radius, radius + d * 0.02);
}

/**
 * Cash raining down their parent, drawn on a canvas: green bills (or gold and silver coins) that flutter,
 * tumble end over end, and get blown sideways by gusts of wind that sweep across, with the odd updraft
 * that holds them in the air. Each look is painted once onto a small hidden canvas (a "sprite") and then
 * stamped on each frame, so many of them stay cheap. How things move lives in `utils/moneyMotion.ts`.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function FallingMoney({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't make the cash jump somewhere else, or the wind change course.
  const pieces = useRef<Cash[]>([]);
  const clock = useRef(Math.random() * 60); // seconds of weather so far; random, so two cards on screen don't gust in step
  const { size, speed, glow, money_kind: kind, money_count: count, money_wind: wind, money_weight: coinWeight } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const billLength = size * BILL_LENGTH_PER_SIZE;
    const billHeight = billLength / BILL_ASPECT;
    const coinDiameter = size * COIN_DIAMETER_PER_SIZE;
    const coin = coinFeel(coinWeight);
    const room = glow ? size * 0.5 : 2; // CSS pixels around a piece inside its sprite, for the halo
    let width = 0;
    let height = 0;
    let dpr = 0;
    let billLooks: Look[] = [];
    let coinLooks: Look[] = [];
    let built = false; // whether the looks above have been painted yet
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    const box = () => ({ width, height, size });

    /** A sprite `w` by `h` (plus room), painted at the screen's pixel density so it stays sharp. */
    const makeSprite = (w: number, h: number, paint: (c: CanvasRenderingContext2D) => void): HTMLCanvasElement => {
      const sprite = document.createElement("canvas");
      sprite.width = Math.ceil((w + 2 * room) * dpr);
      sprite.height = Math.ceil((h + 2 * room) * dpr);
      const c = sprite.getContext("2d");
      if (c) {
        c.scale(dpr, dpr);
        c.translate(room, room);
        paint(c);
      }
      return sprite;
    };

    const buildLooks = () => {
      // A shadow's blur is measured in device pixels whatever the transform, hence the `dpr`.
      const glowBlur = size * 0.35 * dpr;
      billLooks =
        kind === "coins"
          ? []
          : BILL_TONES.map((tone) => ({
              front: makeSprite(billLength, billHeight, (c) => paintBill(c, billLength, billHeight, tone, "front", glow, glowBlur)),
              back: makeSprite(billLength, billHeight, (c) => paintBill(c, billLength, billHeight, tone, "back", glow, glowBlur)),
              width: billLength + 2 * room,
              height: billHeight + 2 * room,
            }));
      coinLooks =
        kind === "bills"
          ? []
          : COIN_TONES.map((tone) => {
              const sprite = makeSprite(coinDiameter, coinDiameter, (c) => paintCoin(c, coinDiameter, tone, glow, glowBlur));
              return { front: sprite, back: sprite, width: coinDiameter + 2 * room, height: coinDiameter + 2 * room };
            });
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      for (const piece of pieces.current) {
        const looks = piece.coin ? coinLooks : billLooks;
        const look = looks[piece.variant % looks.length];
        if (!look) continue;
        const { angle, squash, back, shade } = pose(piece);
        const w = look.width * piece.scale;
        const h = look.height * piece.scale;
        // Position and turn in one step: the matrix is "rotate by the angle, then move to (x, y)", times the pixel density.
        const cos = Math.cos(angle) * dpr;
        const sin = Math.sin(angle) * dpr;
        ctx.setTransform(cos, sin, -sin, cos, piece.x * dpr, piece.y * dpr);
        // Turning over squashes a bill's height (it spins on its long edge) and a coin's width (it spins on its diameter).
        if (piece.coin) ctx.scale(squash, 1);
        else ctx.scale(1, squash);
        ctx.globalAlpha = shade * piece.scale; // edge-on and far-away pieces are dimmer
        ctx.drawImage(back ? look.back : look.front, -w / 2, -h / 2, w, h);
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

      // Add or drop pieces to match the count; the first few keep their places.
      const list = pieces.current;
      const before = list.length;
      while (list.length < count) list.push(newCash(list.length, kind, box()));
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
      const weather = { seconds, time: clock.current, fall: speed * FALL_PX_PER_SPEED, wind, coin };
      for (const piece of pieces.current) moveCash(piece, weather, box());
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

    // A changed kind applies to the cash already falling, not just new pieces.
    pieces.current.forEach((piece, index) => {
      piece.coin = isCoin(index, kind);
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
  }, [size, speed, glow, kind, count, wind, coinWeight]);

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
