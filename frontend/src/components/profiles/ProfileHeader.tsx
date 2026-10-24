import { GraduationCap, Link as LinkIcon, MapPin, Pencil } from "lucide-react";
import { Link } from "react-router-dom";
import type { Profile } from "../../types/profile";
import Avatar from "./Avatar";

interface ProfileHeaderProps {
  profile: Profile;
  editable?: boolean;
}

export default function ProfileHeader({ profile, editable }: ProfileHeaderProps) {
  return (
    <section className="relative overflow-hidden rounded-2xl border border-line bg-surface p-6 sm:p-8">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-r from-violet-600/25 via-fuchsia-500/10 to-cyan-500/25" />

      <div className="relative flex flex-col items-center gap-5 text-center sm:flex-row sm:items-end sm:text-left">
        <Avatar name={profile.full_name} url={profile.avatar_url} size="xl" />

        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold sm:text-3xl">{profile.full_name}</h1>
          <p className="font-mono text-sm text-cyan-300">@{profile.username}</p>

          <ul className="mt-3 flex flex-col gap-1.5 text-sm text-slate-300 sm:flex-row sm:flex-wrap sm:gap-x-5">
            {profile.location && (
              <li className="flex items-center justify-center gap-1.5 sm:justify-start">
                <MapPin className="size-4 text-muted" aria-hidden />
                {profile.location}
              </li>
            )}
            {profile.education && (
              <li className="flex items-center justify-center gap-1.5 sm:justify-start">
                <GraduationCap className="size-4 text-muted" aria-hidden />
                {profile.education}
              </li>
            )}
          </ul>

          {profile.links.length > 0 && (
            <ul className="mt-3 flex flex-wrap justify-center gap-2 sm:justify-start">
              {profile.links.map((link) => (
                <li key={link.id}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface-raised px-3 py-1 text-xs text-slate-200 transition-colors hover:border-cyan-500/50 hover:text-cyan-200"
                  >
                    <LinkIcon className="size-3" aria-hidden />
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>

        {editable && (
          <Link
            to="/profile/edit"
            className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-500"
          >
            <Pencil className="size-4" aria-hidden />
            Edit Profile
          </Link>
        )}
      </div>
    </section>
  );
}
