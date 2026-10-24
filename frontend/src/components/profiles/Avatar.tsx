import { useState } from "react";

const SIZES = {
  md: "size-14 text-lg",
  lg: "size-20 text-2xl",
  xl: "size-32 text-4xl sm:size-36",
};

interface AvatarProps {
  name: string;
  url: string | null;
  size?: keyof typeof SIZES;
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]!.toUpperCase())
    .join("");
}

export default function Avatar({ name, url, size = "md" }: AvatarProps) {
  const [broken, setBroken] = useState(false);
  const base = `${SIZES[size]} shrink-0 rounded-full ring-2 ring-violet-500/40`;

  if (url && !broken) {
    return <img src={url} alt={name} onError={() => setBroken(true)} className={`${base} object-cover`} />;
  }
  return (
    <div
      aria-label={name}
      className={`${base} flex items-center justify-center bg-gradient-to-br from-violet-600 to-cyan-500 font-semibold text-white`}
    >
      {initials(name) || "?"}
    </div>
  );
}
