import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { advance, createMarket, type Market, type MarketEvent, type MarketSettings } from "../../utils/marketSim";
import { CHART_PALETTE_INFO, DEFAULT_EFFECT_OPTIONS } from "../../utils/theme";

const HISTORY_CANDLES = 300; // the chart starts full; this is more than any card is wide
const PITCH = 1.7; // distance between candles, in candle widths
const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of teleporting
const AXIS_EASE = 3; // per second: how quickly the price axis follows the candles, so it glides instead of jumping
const POPUP_SECONDS = 1.8;
const FLASH_SECONDS = 0.7;
const FLASH_STRENGTH = 0.14;
const MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace';
const POPUP_FONT = 'italic 900 {px}px Impact, "Arial Black", sans-serif';

const POPUPS = {
  pump: ["🚀 TO THE MOON", "STONKS ONLY GO UP", "DIAMOND HANDS 💎", "GIGA PUMP 📈", "BUY BUY BUY", "WAGMI"],
  crash: ["💥 REKT", "BUY THE DIP", "THIS IS FINE 🔥", "CIRCUIT BREAKER ⛔", "PAPER HANDS 🧻", "NGMI"],
};

interface Popup {
  text: string;
  x: number;
  y: number;
  color: string;
  age: number;
}

const pick = <T,>(items: T[]): T => items[Math.floor(Math.random() * items.length)] as T;
const money = (price: number) => price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/**
 * A made-up stock market drawn as a candlestick chart, scrolling past: green and red candles form
 * live, with volume bars underneath, a price tag, and now and then a pump or a crash that tints the
 * chart and throws up a popup. The price comes from `utils/marketSim.ts`; this file only draws it.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function VolatileMarket({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't throw the chart away.
  const market = useRef<Market | null>(null);
  const settings = useRef<MarketSettings>({ volatility: options.chart_volatility, mood: options.chart_mood });
  const { size, speed, glow, chart_palette: paletteName, chart_ticker: tickerOption, chart_label: showLabel } = options;

  // The market itself reads these every frame, so changing them doesn't restart anything: the chart just starts behaving differently.
  useEffect(() => {
    settings.current = { volatility: options.chart_volatility, mood: options.chart_mood };
  }, [options.chart_volatility, options.chart_mood]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const { up, down } = CHART_PALETTE_INFO[paletteName] ?? CHART_PALETTE_INFO.classic;
    // Drawn on a canvas only, but still refuse anything that isn't a short run of letters and numbers.
    const ticker = /^[A-Z0-9]{1,8}$/.test(tickerOption) ? tickerOption : DEFAULT_EFFECT_OPTIONS.chart_ticker;
    const candleW = Math.max(3, size * 0.5);
    const pitch = candleW * PITCH;
    const candleSeconds = 2.4 - 0.2 * speed; // speed 1-10 -> 2.2 down to 0.4 seconds per candle
    const labelPx = Math.min(Math.max(size * 1.1, 12), 26);
    const popupPx = Math.min(Math.max(size * 1.4, 16), 36);
    let width = 0;
    let height = 0;
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;
    let popups: Popup[] = [];
    let flash = { color: up, age: FLASH_SECONDS }; // age >= FLASH_SECONDS means no flash
    const axis = { low: 0, high: 1, ready: false };

    // Where things go: the candles in the top part, the volume bars along the bottom, a margin on the right for the price tag.
    const area = () => {
      const bottom = height * 0.76;
      // With the headline on, the candles start below it, so the price tag never runs into it.
      const top = showLabel ? Math.min(Math.max(height * 0.1, labelPx * 2 + 8), bottom * 0.5) : height * 0.1;
      return { right: width * 0.88, top, bottom, volumeTop: height * 0.82, volumeBottom: height * 0.98 };
    };
    const priceY = (price: number) => {
      const { top, bottom } = area();
      return bottom - ((price - axis.low) / (axis.high - axis.low)) * (bottom - top);
    };

    const draw = (seconds: number) => {
      ctx.clearRect(0, 0, width, height);
      const m = market.current;
      if (!m || width < 40 || height < 40) return;
      const { right, top, bottom, volumeTop, volumeBottom } = area();
      const shown = Math.ceil(right / pitch) + 2; // how many candles back still have any part on screen

      // The axis follows the candles that are on screen (with some room above and below).
      let low = m.live.low;
      let high = m.live.high;
      let busiest = m.live.volume;
      for (let k = 1; k <= shown; k++) {
        const candle = m.candles[m.candles.length - k];
        if (!candle) break;
        low = Math.min(low, candle.low);
        high = Math.max(high, candle.high);
        busiest = Math.max(busiest, candle.volume);
      }
      const room = (high - low) * 0.12 || high * 0.01;
      const ease = axis.ready ? 1 - Math.exp(-AXIS_EASE * seconds) : 1;
      axis.low += (low - room - axis.low) * ease;
      axis.high += (high + room - axis.high) * ease;
      axis.ready = true;

      // Faint grid.
      ctx.strokeStyle = "rgba(255, 255, 255, 0.07)";
      ctx.lineWidth = 1;
      for (let i = 0; i <= 3; i++) {
        const y = top + ((bottom - top) * i) / 3;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Candle k steps back from the live one sits k pitches to its left, and everything slides left as the live one forms.
      const candleAt = (k: number) => (k === 0 ? m.live : m.candles[m.candles.length - k]);
      const xAt = (k: number) => right - (m.progress + k) * pitch;
      const bar = (k: number, fill: string, paint: (x: number, candle: NonNullable<ReturnType<typeof candleAt>>) => void) => {
        const candle = candleAt(k);
        if (!candle) return;
        ctx.fillStyle = fill;
        paint(xAt(k), candle);
      };
      const colorOf = (candle: { open: number; close: number }) => (candle.close >= candle.open ? up : down);

      // Volume bars, behind everything else.
      ctx.globalAlpha = 0.3;
      for (let k = 0; k <= shown; k++) {
        const candle = candleAt(k);
        if (!candle) break;
        bar(k, colorOf(candle), (x, c) => {
          const h = (c.volume / busiest) * (volumeBottom - volumeTop);
          ctx.fillRect(x - candleW / 2, volumeBottom - h, candleW, h);
        });
      }
      ctx.globalAlpha = 1;

      // The candles: a thin wick from the lowest to the highest price, and a body from open to close.
      ctx.lineWidth = Math.max(1, candleW * 0.15);
      for (let k = shown; k >= 0; k--) {
        const candle = candleAt(k);
        if (!candle) continue;
        const color = colorOf(candle);
        if (glow) {
          ctx.shadowColor = color;
          ctx.shadowBlur = candleW * 0.9;
        }
        ctx.strokeStyle = color;
        const x = xAt(k);
        ctx.beginPath();
        ctx.moveTo(x, priceY(candle.high));
        ctx.lineTo(x, priceY(candle.low));
        ctx.stroke();
        bar(k, color, (cx, c) => {
          const openY = priceY(c.open);
          const closeY = priceY(c.close);
          ctx.fillRect(cx - candleW / 2, Math.min(openY, closeY), candleW, Math.max(1.5, Math.abs(openY - closeY)));
        });
      }
      ctx.shadowBlur = 0;

      const price = m.live.close;
      const color = colorOf(m.live);
      const first = m.candles[m.candles.length - shown] ?? m.candles[0];
      const change = first ? price / first.open - 1 : 0;
      const changeColor = change >= 0 ? up : down;

      if (showLabel) {
        // The dashed line at the current price, with its tag on the right edge.
        const y = Math.min(bottom, Math.max(top, priceY(price)));
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = color;
        ctx.globalAlpha = 0.5;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
        ctx.font = `700 ${labelPx * 0.8}px ${MONO}`;
        ctx.textBaseline = "middle";
        ctx.textAlign = "center";
        const tag = money(price);
        const tagWidth = ctx.measureText(tag).width + 10;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.roundRect(width - tagWidth - 4, y - labelPx * 0.55, tagWidth, labelPx * 1.1, 4);
        ctx.fill();
        ctx.fillStyle = "#06080f";
        ctx.fillText(tag, width - tagWidth / 2 - 4, y + 0.5);

        // The headline: symbol, price, and how far it has moved over what's on screen.
        ctx.font = `800 ${labelPx}px ${MONO}`;
        ctx.textAlign = "right";
        ctx.textBaseline = "alphabetic";
        const arrow = change >= 0 ? "▲" : "▼";
        const text = `${arrow} ${(Math.abs(change) * 100).toFixed(2)}%`;
        ctx.fillStyle = changeColor;
        ctx.fillText(text, width - 12, 10 + labelPx);
        const textWidth = ctx.measureText(text + "  ").width;
        ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
        ctx.fillText(`$${ticker}`, width - 12 - textWidth, 10 + labelPx);
      }

      // A pump or crash tints the whole chart for a moment...
      if (flash.age < FLASH_SECONDS) {
        ctx.globalAlpha = FLASH_STRENGTH * (1 - flash.age / FLASH_SECONDS);
        ctx.fillStyle = flash.color;
        ctx.fillRect(0, 0, width, height);
        ctx.globalAlpha = 1;
      }

      // ...and a popup rises from where it happened.
      ctx.font = POPUP_FONT.replace("{px}", String(popupPx));
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";
      ctx.lineWidth = Math.max(3, popupPx * 0.18);
      for (const popup of popups) {
        const t = popup.age / POPUP_SECONDS;
        const half = ctx.measureText(popup.text).width / 2 + 8;
        const x = Math.min(width - half, Math.max(half, popup.x)); // keep it on the card
        const rise = 1 - (1 - Math.min(1, t * 1.5)) ** 3;
        ctx.globalAlpha = t < 0.6 ? 1 : Math.max(0, 1 - (t - 0.6) / 0.4);
        if (glow) {
          ctx.shadowColor = popup.color;
          ctx.shadowBlur = popupPx * 0.4;
        }
        ctx.strokeStyle = "rgba(0, 0, 0, 0.65)";
        ctx.strokeText(popup.text, x, popup.y - 30 * rise);
        ctx.fillStyle = popup.color;
        ctx.fillText(popup.text, x, popup.y - 30 * rise);
        ctx.shadowBlur = 0;
      }
      ctx.globalAlpha = 1;
    };

    const onEvent = (event: MarketEvent) => {
      const m = market.current;
      if (!m) return;
      const color = event.kind === "pump" ? up : down;
      flash = { color, age: 0 };
      popups.push({
        text: pick(POPUPS[event.kind]),
        x: area().right - m.progress * pitch - 20,
        y: Math.min(area().bottom, Math.max(area().top + popupPx, priceY(m.live.close))),
        color,
        age: 0,
      });
    };

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      market.current ??= createMarket(settings.current, HISTORY_CANDLES, Math.random);
      draw(0); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      const m = market.current;
      if (m) for (const event of advance(m, seconds / candleSeconds, settings.current, Math.random)) onEvent(event);
      for (const popup of popups) popup.age += seconds;
      popups = popups.filter((popup) => popup.age < POPUP_SECONDS);
      flash.age += seconds;
      draw(seconds);
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
  }, [size, speed, glow, paletteName, tickerOption, showLabel]);

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
