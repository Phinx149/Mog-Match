import { ArrowLeft, Bot, Code2, Search, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States";
import Navbar from "../components/layout/Navbar";
import MogScoreCard from "../components/mog/MogScoreCard";
import ProfileHeader from "../components/profiles/ProfileHeader";
import ProjectCard from "../components/profiles/ProjectCard";
import SkillBadge from "../components/profiles/SkillBadge";
import { ApiError, getMyProfile, getProfile } from "../services/api";
import type { Profile } from "../types/profile";

export default function ProfilePage() {
  const { id } = useParams();
  const isMe = !id;
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setProfile(null);
    setError(null);
    (id ? getProfile(id, controller.signal) : getMyProfile(controller.signal))
      .then(setProfile)
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof ApiError && err.status === 404 ? "This profile doesn't exist." : String((err as Error).message));
      });
    return () => controller.abort();
  }, [id, reloadKey]);

  const retry = useCallback(() => setReloadKey((key) => key + 1), []);

  return (
    <>
      <Navbar>
        {!isMe && (
          <Link to="/discover" className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-slate-200">
            <ArrowLeft className="size-4" aria-hidden /> Back to Discover
          </Link>
        )}
      </Navbar>

      <main className="mx-auto flex max-w-3xl flex-col gap-5 px-4 py-6">
        {error ? (
          <ErrorState message={error} onRetry={retry} />
        ) : !profile ? (
          <LoadingState label="Loading profile…" />
        ) : (
          <>
            <ProfileHeader profile={profile} editable={isMe} />

            <MogScoreCard mog={profile.mog} showTips={isMe} />

            <Section title="About">
              {profile.bio ? (
                <p className="leading-relaxed whitespace-pre-line text-slate-300">{profile.bio}</p>
              ) : (
                <p className="text-muted">No bio yet.</p>
              )}
              <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
                <Fact icon={<Sparkles className="size-4" />} label="Experience" value={profile.experience_level} />
                <Fact icon={<Code2 className="size-4" />} label="Favorite IDE" value={profile.favorite_ide} />
                <Fact
                  icon={<Bot className="size-4" />}
                  label="AI agents"
                  value={profile.favorite_ai_agents.join(", ") || null}
                />
              </dl>
              {profile.looking_for.length > 0 && (
                <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
                  <span className="inline-flex items-center gap-1.5 text-muted">
                    <Search className="size-4" aria-hidden /> Looking for
                  </span>
                  {profile.looking_for.map((item) => (
                    <SkillBadge key={item} label={item} variant="neutral" />
                  ))}
                </div>
              )}
            </Section>

            <Section title="Technical Skills">
              <TagList values={profile.skills} variant="skill" empty="No skills listed yet." />
            </Section>

            <Section title="Projects">
              {profile.projects.length ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  {profile.projects.map((project) => (
                    <ProjectCard key={project.id} project={project} />
                  ))}
                </div>
              ) : (
                <EmptyState title="No projects yet">{isMe && "Add one from Edit Profile."}</EmptyState>
              )}
            </Section>

            <Section title="Interests">
              <TagList values={profile.interests} variant="interest" empty="No interests listed yet." />
            </Section>
          </>
        )}
      </main>
    </>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-line bg-surface p-6">
      <h2 className="mb-4 text-sm font-semibold tracking-wide text-violet-300 uppercase">{title}</h2>
      {children}
    </section>
  );
}

function Fact({ icon, label, value }: { icon: ReactNode; label: string; value: string | null }) {
  return (
    <div className="rounded-xl border border-line bg-surface-raised p-3">
      <dt className="flex items-center gap-1.5 text-xs text-muted">
        {icon}
        {label}
      </dt>
      <dd className="mt-1 text-slate-200">{value || "—"}</dd>
    </div>
  );
}

function TagList({ values, variant, empty }: { values: string[]; variant: "skill" | "interest"; empty: string }) {
  if (!values.length) return <p className="text-sm text-muted">{empty}</p>;
  return (
    <div className="flex flex-wrap gap-2">
      {values.map((value) => (
        <SkillBadge key={value} label={value} variant={variant} />
      ))}
    </div>
  );
}
