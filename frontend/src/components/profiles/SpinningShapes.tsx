import { useEffect, useRef } from "react";
import type { EffectOptions } from "../../types/profile";
import { DEFAULT_EFFECT_OPTIONS, HEX_COLOR } from "../../utils/theme";
import { anglesAt, buildShape, newSpinner, perspective, rotate, slots, type Shape, type Spinner, type Vec3 } from "../../utils/wireShapes";

const MAX_FRAME_SECONDS = 0.1; // after a pause (hidden tab), move by at most this much instead of jumping ahead
const RADIUS_PER_SIZE = 3; // the size setting, 10-48, is a shape radius of 30-144 pixels...
const MAX_RADIUS_FRACTION = 0.38; // ...but never more than this much of the card's shorter side, so a shape isn't cut off by the edges
const CLOCK_PER_SPEED = 0.18; // seconds of turning per second, per point of speed: the default speed, 4, turns about once in 9 seconds
const BOB_FRACTION = 0.05; // how far a shape drifts up and down, as a fraction of the card's height
const DEPTH_BANDS = 4; // lines are grouped by how near they are, so each group is drawn in one go instead of line by line
const GLOW_BANDS = 2; // only the nearest groups throw a halo, which is where it shows and keeps the glow cheap

/**
 * Wireframe shapes turning in 3D, drawn on a canvas: a cube, torus or globe made of lines, tumbling as it goes and
 * squashed onto the screen with perspective, so near lines are bigger, thicker and brighter than far ones. There is no
 * 3D library; the points and the turning are plain math in `utils/wireShapes.ts`, and this draws the lines.
 * The parent must be `relative`; ThemeScope takes care of that.
 */
export default function SpinningShapes({ options }: { options: EffectOptions }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Kept across effect re-runs so dragging a slider doesn't make the shapes jump to another angle.
  const spinners = useRef<Spinner[]>([]);
  const clock = useRef(0); // how long the shapes have been turning; it runs faster at higher speeds, so changing the speed never jerks them
  const { size, speed, glow, shape_kind: kind, shape_count: count, shape_color: colorOption } = options;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // It comes from the server, but fall back rather than draw with something unexpected.
    const color = HEX_COLOR.test(colorOption) ? colorOption : DEFAULT_EFFECT_OPTIONS.shape_color;
    const shape: Shape = buildShape(kind);
    // Scratch space reused by every shape on every frame: where each point is after turning, and where it lands on the screen.
    const points: Vec3[] = [];
    const xs: number[] = [];
    const ys: number[] = [];
    const bands: number[][] = Array.from({ length: DEPTH_BANDS }, () => []); // per depth band, the edges (indexes into shape.edges) in it
    let width = 0;
    let height = 0;
    let dpr = 1;
    let frame = 0; // requestAnimationFrame id; 0 = not running
    let lastFrame = 0;

    const paintShape = (spinner: Spinner, place: { x: number; y: number }) => {
      const radius = Math.min(size * RADIUS_PER_SIZE, Math.min(width, height) * MAX_RADIUS_FRACTION);
      const line = Math.max(1, radius * 0.022);
      const centerX = place.x * width;
      const centerY = (place.y + Math.sin(clock.current * 0.5 + spinner.bob) * BOB_FRACTION) * height;

      rotate(shape, anglesAt(spinner, clock.current), points);
      points.forEach(([x, y, z], i) => {
        const scale = perspective(z) * radius;
        xs[i] = centerX + x * scale;
        ys[i] = centerY + y * scale;
      });

      // z runs from -1 (far side) to 1 (near side). Sort each line into a band by how near its middle is.
      for (const band of bands) band.length = 0;
      shape.edges.forEach(([a, b], edge) => {
        const depth = (points[a]![2] + points[b]![2]) / 2;
        bands[Math.min(DEPTH_BANDS - 1, Math.floor(((depth + 1) / 2) * DEPTH_BANDS))]!.push(edge);
      });

      ctx.strokeStyle = color;
      ctx.lineCap = "round";
      bands.forEach((band, index) => {
        const nearness = (index + 0.5) / DEPTH_BANDS; // 0 = far, 1 = near
        ctx.globalAlpha = 0.12 + 0.88 * nearness ** 1.5;
        ctx.lineWidth = line * (0.6 + 0.8 * nearness);
        // A shadow's blur is measured in device pixels whatever the transform, hence the `dpr`.
        const halo = glow && index >= DEPTH_BANDS - GLOW_BANDS;
        ctx.shadowColor = color;
        ctx.shadowBlur = halo ? Math.max(6, radius * 0.18) * dpr : 0;
        ctx.beginPath();
        for (const edge of band) {
          const [a, b] = shape.edges[edge]!;
          ctx.moveTo(xs[a]!, ys[a]!);
          ctx.lineTo(xs[b]!, ys[b]!);
        }
        ctx.stroke();
      });
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      const places = slots(spinners.current.length);
      spinners.current.forEach((spinner, i) => paintShape(spinner, places[i]!));
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
    };

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw(); // resizing clears a canvas, so paint right away (also the still picture for reduced motion)
    };

    // Add or drop shapes to match the count; the first few keep their angles.
    const list = spinners.current;
    while (list.length < count) list.push(newSpinner());
    list.length = count;

    const tick = (now: number) => {
      frame = requestAnimationFrame(tick);
      const seconds = Math.min((now - (lastFrame || now)) / 1000, MAX_FRAME_SECONDS);
      lastFrame = now;
      clock.current += seconds * speed * CLOCK_PER_SPEED;
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
  }, [size, speed, glow, kind, count, colorOption]);

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
