import type { FilterOptions } from "../types/profile";

// Lets the edit form flag an unknown skill or technology the moment it is added. The backend is the
// authority (backend/app/services/tech_catalog.py `normalize_technology`): lookups ignore case, spaces,
// dots, hyphens and underscores, so "nodejs", "Node JS" and "node.js" are all the same technology.

/** Comparison key. Keep in sync with `_key` in tech_catalog.py. */
const toKey = (name: string) => name.trim().toLowerCase().replace(/[\s._-]+/g, "");

/** Every spelling the backend accepts, as comparison keys. */
export function knownTechnologyKeys({ skills, skill_aliases }: Pick<FilterOptions, "skills" | "skill_aliases">): Set<string> {
  return new Set([...skills, ...Object.keys(skill_aliases)].map(toKey));
}

/** An error message naming the names that aren't known technologies, or undefined if they all are.
 *  Worded like the backend's, so the message doesn't change when you save. */
export function unknownTechnologyError(values: string[], known: Set<string>, noun: "skill" | "technology"): string | undefined {
  const unknown = values.filter((value) => !known.has(toKey(value)));
  if (!unknown.length) return undefined;
  return `Unknown ${noun}: ${unknown.slice(0, 3).join(", ")}${unknown.length > 3 ? "…" : ""}. Use a known language, framework or dev tool.`;
}
