import { ArrowLeft, CheckCircle2, Loader2, Plus, RotateCcw, Save, Trash2 } from "lucide-react";
import { cloneElement, useEffect, useId, useState, type FormEvent, type ReactElement, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { ErrorState, LoadingState } from "../components/common/States";
import TagInput from "../components/forms/TagInput";
import ToggleChips from "../components/forms/ToggleChips";
import Navbar from "../components/layout/Navbar";
import ThemePicker from "../components/profiles/ThemePicker";
import { ApiError, getFilterOptions, getMyProfile, updateMyProfile } from "../services/api";
import { EXPERIENCE_LEVELS, type Profile, type ProfileTheme, type ProfileUpdate } from "../types/profile";
import { DEFAULT_THEME, sameTheme } from "../utils/theme";

type LinkDraft = { label: string; url: string };
type ProjectDraft = { title: string; description: string; project_url: string; technologies: string[] };

interface FormState {
  full_name: string;
  username: string;
  avatar_url: string;
  location: string;
  education: string;
  bio: string;
  favorite_ide: string;
  experience_level: string;
  skills: string[];
  interests: string[];
  favorite_ai_agents: string[];
  looking_for: string[];
  theme: ProfileTheme;
  links: LinkDraft[];
  projects: ProjectDraft[];
}

type SaveStatus = { kind: "idle" } | { kind: "saving" } | { kind: "saved" } | { kind: "error"; message: string };

function toForm(p: Profile, lookingForOptions: string[]): FormState {
  return {
    full_name: p.full_name,
    username: p.username,
    avatar_url: p.avatar_url ?? "",
    location: p.location ?? "",
    education: p.education ?? "",
    bio: p.bio,
    favorite_ide: p.favorite_ide ?? "",
    experience_level: p.experience_level ?? "",
    skills: p.skills,
    interests: p.interests,
    favorite_ai_agents: p.favorite_ai_agents,
    // Keep only values on the allowed list; older free-text entries would be rejected on save.
    looking_for: lookingForOptions.filter((option) =>
      p.looking_for.some((value) => value.toLowerCase() === option.toLowerCase()),
    ),
    theme: p.theme,
    links: p.links.map(({ label, url }) => ({ label, url })),
    projects: p.projects.map(({ title, description, project_url, technologies }) => ({
      title,
      description,
      project_url: project_url ?? "",
      technologies,
    })),
  };
}

const orNull = (value: string) => (value.trim() ? value.trim() : null);

function toUpdate(form: FormState): ProfileUpdate {
  return {
    full_name: form.full_name,
    username: form.username,
    avatar_url: orNull(form.avatar_url),
    location: orNull(form.location),
    education: orNull(form.education),
    bio: form.bio,
    favorite_ide: orNull(form.favorite_ide),
    experience_level: orNull(form.experience_level),
    skills: form.skills,
    interests: form.interests,
    favorite_ai_agents: form.favorite_ai_agents,
    looking_for: form.looking_for,
    theme: form.theme,
    links: form.links,
    projects: form.projects.map((project) => ({ ...project, project_url: orNull(project.project_url) })),
  };
}

export default function EditProfilePage() {
  const [form, setForm] = useState<FormState | null>(null);
  const [lookingForOptions, setLookingForOptions] = useState<string[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [status, setStatus] = useState<SaveStatus>({ kind: "idle" });
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!photo) { setPhotoPreview(null); return; }
    const url = URL.createObjectURL(photo);
    setPhotoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [photo]);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([getMyProfile(controller.signal), getFilterOptions(controller.signal)])
      .then(([profile, options]) => {
        setLookingForOptions(options.looking_for);
        setForm(toForm(profile, options.looking_for));
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setLoadError(err instanceof Error ? err.message : "Failed to load your profile.");
      });
    return () => controller.abort();
  }, []);

  if (loadError) return <ErrorState message={loadError} onRetry={() => window.location.reload()} />;
  if (!form) return <LoadingState label="Loading your profile…" />;

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => (current ? { ...current, [key]: value } : current));
    if (status.kind === "saved") setStatus({ kind: "idle" });
  };

  const updateLink = (index: number, patch: Partial<LinkDraft>) =>
    update("links", form.links.map((link, i) => (i === index ? { ...link, ...patch } : link)));
  const updateProject = (index: number, patch: Partial<ProjectDraft>) =>
    update("projects", form.projects.map((project, i) => (i === index ? { ...project, ...patch } : project)));
  // The picker previews instantly, so drop the server's old complaints about the theme as soon as it changes.
  const updateTheme = (theme: ProfileTheme) => {
    update("theme", theme);
    setFieldErrors((current) => {
      const next = { ...current };
      for (const key of Object.keys(next)) if (key.startsWith("theme.")) delete next[key];
      return next;
    });
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setStatus({ kind: "saving" });
    setFieldErrors({});
    try {
      const saved = await updateMyProfile(toUpdate(form), photo);
      setForm(toForm(saved, lookingForOptions)); // reflect server-side cleanup and allowed categories
      setPhoto(null);
      setStatus({ kind: "saved" });
    } catch (err) {
      if (err instanceof ApiError) setFieldErrors(err.fields);
      setStatus({ kind: "error", message: err instanceof Error ? err.message : "Save failed." });
    }
  };

  const err = (key: string) => fieldErrors[key];
  // The sliders can't send a bad value, so a server complaint about one option is shown as a single line.
  const firstEffectOptionError = Object.entries(fieldErrors).find(([key]) => key.startsWith("theme.effect_options."))?.[1];
  const saving = status.kind === "saving";

  return (
    <>
      <Navbar>
        <Link to="/profile" className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-slate-200">
          <ArrowLeft className="size-4" aria-hidden /> Back to profile
        </Link>
      </Navbar>

      <form onSubmit={onSubmit} className="mx-auto flex max-w-3xl flex-col gap-5 px-4 py-6" noValidate>
        <h1 className="text-2xl font-bold">Edit Profile</h1>

        <Card title="Basics">
          <Field label="Profile photo" error={err("photo")} hint="JPEG, PNG or WebP, up to 5 MB. Saved when you save your profile.">
            <input className="field cursor-pointer" type="file" accept="image/jpeg,image/png,image/webp" disabled={saving} onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />
          </Field>
          {(photoPreview || form.avatar_url) && <img src={photoPreview || form.avatar_url} alt="Profile photo preview" className="size-24 rounded-full object-cover" />}
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Full name" error={err("full_name")}>
              <input className="field" value={form.full_name} maxLength={120} required onChange={(e) => update("full_name", e.target.value)} />
            </Field>
            <Field label="Username" error={err("username")} hint="3–40 letters, numbers, _ or -">
              <input className="field font-mono" value={form.username} maxLength={40} required onChange={(e) => update("username", e.target.value)} />
            </Field>
            <Field label="Location" error={err("location")}>
              <input className="field" value={form.location} maxLength={120} placeholder="City, Country" onChange={(e) => update("location", e.target.value)} />
            </Field>
            <Field label="Education" error={err("education")}>
              <input className="field" value={form.education} maxLength={200} placeholder="School, degree, year" onChange={(e) => update("education", e.target.value)} />
            </Field>
            <Field label="Avatar URL" error={err("avatar_url")} hint="Used when no profile photo has been uploaded.">
              <input className="field" type="url" value={form.avatar_url} maxLength={500} placeholder="https://…" onChange={(e) => update("avatar_url", e.target.value)} />
            </Field>
            <Field label="Experience level" error={err("experience_level")}>
              <select className="field" value={form.experience_level} onChange={(e) => update("experience_level", e.target.value)}>
                <option value="">Not specified</option>
                {EXPERIENCE_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <Field label="About" error={err("bio")}>
            <textarea className="field min-h-28" value={form.bio} maxLength={2000} placeholder="What do you build? What are you looking for?" onChange={(e) => update("bio", e.target.value)} />
          </Field>
        </Card>

        <Card title="Skills & interests">
          <TagInput label="Technical skills (languages, frameworks, specialties)" error={err("skills")} values={form.skills} onChange={(v) => update("skills", v)} placeholder="Rust, React, Frontend…" maxTags={30} />

          <TagInput label="Interests" variant="interest" error={err("interests")} values={form.interests} onChange={(v) => update("interests", v)} placeholder="AI, Gaming, Startups…" maxTags={30} />

          <div>
            <span className="mb-1.5 block text-sm font-medium text-slate-300">Looking for</span>
            <ToggleChips label="Looking for" error={err("looking_for")} options={lookingForOptions} selected={form.looking_for} onChange={(v) => update("looking_for", v)} />
          </div>
        </Card>

        <Card title="Setup">
          <Field label="Favorite IDE" error={err("favorite_ide")}>
            <input className="field" value={form.favorite_ide} maxLength={80} placeholder="VS Code, Neovim…" onChange={(e) => update("favorite_ide", e.target.value)} />
          </Field>
          <TagInput label="Favorite AI coding agents" variant="neutral" error={err("favorite_ai_agents")} values={form.favorite_ai_agents} onChange={(v) => update("favorite_ai_agents", v)} placeholder="Claude Code, Codex…" maxTags={10} />

        </Card>

        <Card
          title="Links"
          action={
            <AddButton onClick={() => update("links", [...form.links, { label: "", url: "" }])} disabled={form.links.length >= 10}>
              Add link
            </AddButton>
          }
        >
          {form.links.length === 0 && <p className="text-sm text-muted">No links yet — add GitHub, LinkedIn, or a portfolio.</p>}
          {form.links.map((link, index) => (
            <div key={index} className="grid gap-2 sm:grid-cols-[10rem_1fr_auto] sm:items-start">
              <Field label="Label" error={err(`links[${index}].label`)} compact>
                <input className="field" value={link.label} maxLength={40} placeholder="GitHub" onChange={(e) => updateLink(index, { label: e.target.value })} />
              </Field>
              <Field label="URL" error={err(`links[${index}].url`)} compact>
                <input className="field" type="url" value={link.url} maxLength={500} placeholder="https://github.com/you" onChange={(e) => updateLink(index, { url: e.target.value })} />
              </Field>
              <RemoveButton label="Remove link" onClick={() => update("links", form.links.filter((_, i) => i !== index))} />
            </div>
          ))}
        </Card>

        <Card
          title="Projects"
          action={
            <AddButton
              onClick={() => update("projects", [...form.projects, { title: "", description: "", project_url: "", technologies: [] }])}
              disabled={form.projects.length >= 20}
            >
              Add project
            </AddButton>
          }
        >
          {form.projects.length === 0 && <p className="text-sm text-muted">No projects yet.</p>}
          {form.projects.map((project, index) => (
            <div key={index} className="flex flex-col gap-3 rounded-xl border border-line bg-surface-raised p-4">
              <div className="flex items-start gap-2">
                <div className="grid flex-1 gap-3 sm:grid-cols-2">
                  <Field label="Title" error={err(`projects[${index}].title`)} compact>
                    <input className="field" value={project.title} maxLength={120} onChange={(e) => updateProject(index, { title: e.target.value })} />
                  </Field>
                  <Field label="Project URL" error={err(`projects[${index}].project_url`)} compact>
                    <input className="field" type="url" value={project.project_url} maxLength={500} placeholder="https://…" onChange={(e) => updateProject(index, { project_url: e.target.value })} />
                  </Field>
                </div>
                <RemoveButton label="Remove project" onClick={() => update("projects", form.projects.filter((_, i) => i !== index))} />
              </div>
              <Field label="Description" error={err(`projects[${index}].description`)} compact>
                <textarea className="field min-h-20" value={project.description} maxLength={2000} onChange={(e) => updateProject(index, { description: e.target.value })} />
              </Field>
              <TagInput label="Technologies" variant="neutral" error={err(`projects[${index}].technologies`)} values={project.technologies} onChange={(v) => updateProject(index, { technologies: v })} placeholder="React, Flask…" maxTags={20} />

            </div>
          ))}
        </Card>

        <Card
          title="Appearance"
          // Always rendered (disabled at the default) so the header keeps the same height; a button
          // that only appears with a custom theme would make this card jump taller.
          action={
            <button
              type="button"
              onClick={() => updateTheme(DEFAULT_THEME)}
              disabled={sameTheme(form.theme, DEFAULT_THEME)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-xs text-slate-200 transition-colors enabled:hover:border-cyan-500/50 enabled:hover:text-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RotateCcw className="size-3.5" aria-hidden />
              Reset to default
            </button>
          }
        >
          <ThemePicker
            theme={form.theme}
            onChange={updateTheme}
            error={err("theme.background")}
            effectError={err("theme.effect") ?? err("theme.effect_options") ?? firstEffectOptionError}
            preview={{
              name: form.full_name,
              username: form.username,
              avatarUrl: photoPreview || form.avatar_url || null,
              skills: form.skills,
            }}
          />
        </Card>

        <div className="flex flex-col gap-3 rounded-2xl border border-line bg-surface/95 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm" aria-live="polite">
            {status.kind === "saved" && (
              <span className="inline-flex items-center gap-1.5 text-emerald-300">
                <CheckCircle2 className="size-4" aria-hidden /> Profile saved.{" "}
                <Link to="/profile" className="underline underline-offset-2">
                  View profile
                </Link>
              </span>
            )}
            {status.kind === "error" && (
              <span className="text-rose-300">
                {status.message}
                {Object.keys(fieldErrors).length > 0 && " Check the highlighted fields."}
              </span>
            )}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Save className="size-4" aria-hidden />}
            {saving ? "Saving…" : "Save"}
          </button>
        </div>
      </form>
    </>
  );
}

function Card({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-wide text-violet-300 uppercase">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function Field({ label, error, hint, compact, children }: { label: string; error?: string; hint?: string; compact?: boolean; children: ReactElement<{ id?: string; "aria-invalid"?: boolean; "aria-describedby"?: string }> }) {
  const id = useId();
  return (
    <div className="min-w-0">
      <label htmlFor={id} className={`mb-1.5 block font-medium text-slate-300 ${compact ? "text-xs" : "text-sm"}`}>{label}</label>
      <div className={error ? "[&_.field]:border-rose-500" : ""}>{cloneElement(children, { id, "aria-invalid": !!error, "aria-describedby": error || hint ? `${id}-help` : undefined })}</div>
      <div id={`${id}-help`}>
      {hint && !error && <span className="mt-1 block text-xs text-muted">{hint}</span>}
      <FieldError message={error} />
      </div>
    </div>
  );
}

function FieldError({ message }: { message?: string }) {
  return message ? <span className="mt-1 block text-xs text-rose-300">{message}</span> : null;
}

function AddButton({ onClick, disabled, children }: { onClick: () => void; disabled?: boolean; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-xs text-slate-200 transition-colors hover:border-cyan-500/50 hover:text-cyan-200 disabled:opacity-50"
    >
      <Plus className="size-3.5" aria-hidden />
      {children}
    </button>
  );
}

function RemoveButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className="mt-6 self-start rounded-lg border border-line p-2 text-muted transition-colors hover:border-rose-500/50 hover:text-rose-300"
    >
      <Trash2 className="size-4" aria-hidden />
    </button>
  );
}
