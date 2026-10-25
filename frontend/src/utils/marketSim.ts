// The volatile market's price simulation, kept apart from the canvas drawing so it is easy to read
// (and to check without a browser). It makes up a stock: a price that wiggles all the time, grouped
// into candles, with now and then a pump or a crash. Nothing here is real, or a prediction of anything.

import type { ChartMood } from "../types/profile";

export interface Candle {
  open: number;
  high: number;
  low: number;
  close: number;
  /** Made-up units. A candle still forming has only the share of its volume it has traded so far. */
  volume: number;
}

export type Regime = "calm" | "pump" | "crash";

/** What `advance` reports, so the drawing can throw a popup at it. */
export interface MarketEvent {
  kind: "pump" | "crash";
}

export interface MarketSettings {
  /** 1-10. */
  volatility: number;
  mood: ChartMood;
}

export interface Market {
  /** Finished candles, oldest first. */
  candles: Candle[];
  /** The candle being formed right now. */
  live: Candle;
  /** 0-1: how much of the live candle's time has passed. */
  progress: number;
  regime: Regime;
  /** Candles left before the regime changes. */
  regimeLeft: number;
  /** The price that the market is pulled back toward, so it can't wander off to zero or infinity. */
  anchor: number;
  /** How much the live candle will have traded by the time it finishes. */
  volumeTarget: number;
}

type Rng = () => number; // like Math.random; passing another one makes the market repeatable

const BASE_SIGMA = 0.005; // a calm market's typical move per candle (0.5%)
const SIGMA_GROWTH = 1.3; // how much each step of "volatility" multiplies that
const REVERSION = 0.01; // per candle: how hard the price is pulled back toward the anchor
const MAX_CANDLES = 400;
const HISTORY_STEPS = 8; // a history candle is built from this many small moves, so its wicks look real

/** How each regime pushes the price: drift (in typical moves per candle), size of the swings, and trading volume. */
const REGIMES: Record<Regime, { drift: number; sigma: number; volume: number }> = {
  calm: { drift: 0, sigma: 1, volume: 1 },
  pump: { drift: 1.3, sigma: 1.4, volume: 2.5 },
  crash: { drift: -1.8, sigma: 1.8, volume: 3 },
};
/** The market's lean while it is calm, in typical moves per candle. */
const MOOD_DRIFT: Record<ChartMood, number> = { bull: 0.2, bear: -0.2, choppy: 0 };
/** Relative odds of a pump or a crash coming next. */
const EVENT_ODDS: Record<ChartMood, { pump: number; crash: number }> = {
  bull: { pump: 25, crash: 10 },
  bear: { pump: 10, crash: 25 },
  choppy: { pump: 15, crash: 15 },
};

/** The typical move of a calm candle, as a fraction of the price. */
export const candleSigma = (volatility: number): number => BASE_SIGMA * SIGMA_GROWTH ** (volatility - 1);

/** A standard normal number (Box-Muller). */
function gaussian(rng: Rng): number {
  return Math.sqrt(-2 * Math.log(1 - rng())) * Math.cos(2 * Math.PI * rng()); // 1 - rng() is never 0, so the log is fine
}

function chooseRegime(settings: MarketSettings, rng: Rng): { regime: Regime; length: number } {
  const { pump, crash } = EVENT_ODDS[settings.mood];
  // A wilder market has more going on, so less of it is calm.
  const calm = Math.max(10, 90 - 5 * settings.volatility);
  let roll = rng() * (calm + pump + crash);
  if ((roll -= pump) < 0) return { regime: "pump", length: 3 + Math.floor(rng() * 5) };
  if ((roll -= crash) < 0) return { regime: "crash", length: 3 + Math.floor(rng() * 5) };
  return { regime: "calm", length: 4 + Math.floor(rng() * 9) };
}

function openCandle(market: Market, rng: Rng): void {
  const price = market.live.close;
  market.live = { open: price, high: price, low: price, close: price, volume: 0 };
  market.progress = 0;
  market.volumeTarget = REGIMES[market.regime].volume * (0.5 + rng());
}

/** Moves the price along for a slice of the live candle (`step` is a share of one candle, 0-1). */
function move(market: Market, step: number, settings: MarketSettings, rng: Rng): void {
  const regime = REGIMES[market.regime];
  const sigma = candleSigma(settings.volatility);
  const live = market.live;
  const drift = (regime.drift + (market.regime === "calm" ? MOOD_DRIFT[settings.mood] : 0)) * sigma;
  const pull = -REVERSION * Math.log(live.close / market.anchor);
  const price = live.close * Math.exp((drift + pull) * step + sigma * regime.sigma * Math.sqrt(step) * gaussian(rng));
  live.close = price;
  live.high = Math.max(live.high, price);
  live.low = Math.min(live.low, price);
  market.progress += step;
  live.volume = market.volumeTarget * Math.min(1, market.progress);
}

function finishCandle(market: Market, settings: MarketSettings, rng: Rng, events: MarketEvent[]): void {
  market.live.volume = market.volumeTarget;
  market.candles.push(market.live);
  if (market.candles.length > MAX_CANDLES) market.candles.shift();

  if (--market.regimeLeft <= 0) {
    const next = chooseRegime(settings, rng);
    market.regime = next.regime;
    market.regimeLeft = next.length;
    if (next.regime !== "calm") events.push({ kind: next.regime });
  }
  openCandle(market, rng);
}

/**
 * Lets the market run for `candles` candles' worth of time (a frame is a small fraction of one; a long
 * pause may be several). Returns the pumps and crashes that started along the way.
 */
export function advance(market: Market, candles: number, settings: MarketSettings, rng: Rng): MarketEvent[] {
  const events: MarketEvent[] = [];
  let left = candles;
  while (left > 1e-9) {
    const step = Math.min(left, 1 - market.progress);
    move(market, step, settings, rng);
    left -= step;
    if (market.progress >= 1 - 1e-9) finishCandle(market, settings, rng, events);
  }
  return events;
}

/** A new market with `history` candles already behind it, so the first thing drawn is a full chart. */
export function createMarket(settings: MarketSettings, history: number, rng: Rng): Market {
  const price = 20 * Math.exp(rng() * Math.log(250)); // anywhere from 20 to 5000
  const market: Market = {
    candles: [],
    live: { open: price, high: price, low: price, close: price, volume: 0 },
    progress: 0,
    regime: "calm",
    regimeLeft: 4 + Math.floor(rng() * 9),
    anchor: price,
    volumeTarget: 1,
  };
  openCandle(market, rng);
  for (let i = 0; i < history * HISTORY_STEPS; i++) advance(market, 1 / HISTORY_STEPS, settings, rng);
  return market;
}
