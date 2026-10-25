import type { ComponentType, CSSProperties, ReactNode } from "react";
import type { EffectOptions, ProfileTheme, ThemeEffect } from "../../types/profile";
import { DEFAULT_BACKGROUND, HEX_COLOR } from "../../utils/theme";
import BouncingDvd from "./BouncingDvd";
import FloatingEmoji from "./FloatingEmoji";
import MatrixRain from "./MatrixRain";

/** What to draw for each effect name. Adding an effect = a component here + its name in THEME_EFFECTS. */
const EFFECTS: Record<ThemeEffect, ComponentType<{ options: EffectOptions }>> = {
  matrix: MatrixRain,
  dvd: BouncingDvd,
  emoji: FloatingEmoji,
};

interface ThemeScopeProps {
  theme: ProfileTheme;
  className?: string;
  children: ReactNode;
}

/**
 * A `div` that applies a profile's theme to everything inside it. Only the card/page content
 * goes in here; app chrome (navbar, Like/Pass buttons) stays outside so it looks the same
 * on every profile. With no theme set it adds nothing, so the default look is untouched.
 */
export default function ThemeScope({ theme, className = "", children }: ThemeScopeProps) {
  // The color is put in a style attribute, so only a plain #rrggbb is ever allowed through,
  // even though the backend already validates it.
  const background = theme.background && HEX_COLOR.test(theme.background) ? theme.background : null;
  // An unknown name (say, from a newer server) just draws nothing.
  const Effect = theme.effect ? EFFECTS[theme.effect] : undefined;
  if (!background && !Effect) return <div className={className}>{children}</div>;

  return (
    <div
      // `isolate` makes this its own stacking context, so the effect's -z-10 canvas sits behind the
      // content but still in front of this element's own background.
      className={`profile-theme ${Effect ? "relative isolate" : ""} ${className}`}
      data-effect={theme.effect ?? undefined}
      style={{ "--profile-bg": background ?? DEFAULT_BACKGROUND } as CSSProperties}
    >
      {Effect && <Effect options={theme.effect_options} />}
      {children}
    </div>
  );
}
