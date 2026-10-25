import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import { useAuth } from "../hooks/useAuth";
import { ApiError, changePassword, updateMyProfile } from "../services/api";
import { APPEARANCES, getAppearance, setAppearance } from "../utils/appearance";

const buttonClass = "self-start rounded-lg bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-500 disabled:opacity-60";

function errorMessage(error: unknown) {
  if (error instanceof ApiError && Object.keys(error.fields).length) return Object.values(error.fields).join(" ");
  return error instanceof Error ? error.message : "Couldn't save changes. Try again.";
}

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.full_name ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [nameError, setNameError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [nameSaved, setNameSaved] = useState(false);
  const [passwordSaved, setPasswordSaved] = useState(false);
  const [appearance, setCurrentAppearance] = useState(getAppearance);

  useEffect(() => { setName(user?.full_name ?? ""); }, [user?.id, user?.full_name]);

  async function saveName(event: FormEvent) {
    event.preventDefault();
    if (!user || savingName) return;
    setSavingName(true);
    setNameError("");
    setNameSaved(false);
    try {
      const profile = await updateMyProfile({ full_name: name.trim() });
      updateUser({ id: profile.id, full_name: profile.full_name, username: profile.username, avatar_url: profile.avatar_url });
      setName(profile.full_name);
      setNameSaved(true);
    } catch (error) {
      setNameError(errorMessage(error));
    } finally {
      setSavingName(false);
    }
  }

  async function savePassword(event: FormEvent) {
    event.preventDefault();
    if (savingPassword) return;
    setPasswordError("");
    setPasswordSaved(false);
    if (newPassword !== confirmation) {
      setPasswordError("New passwords don't match.");
      return;
    }
    setSavingPassword(true);
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmation("");
      setPasswordSaved(true);
    } catch (error) {
      setPasswordError(errorMessage(error));
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="mx-auto flex max-w-3xl flex-col gap-5 px-4 py-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <section aria-labelledby="appearance-heading" className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-5">
          <div>
            <h2 id="appearance-heading" className="font-semibold">Appearance</h2>
            <p className="mt-1 text-sm text-muted">Pick a color scheme for the whole site. It applies right away and is remembered on this device.</p>
          </div>
          <div role="radiogroup" aria-labelledby="appearance-heading" className="grid gap-3 sm:grid-cols-2">
            {APPEARANCES.map(({ id, label, description, preview }) => (
              <label key={id}
                className="flex cursor-pointer flex-col gap-3 rounded-xl border border-line p-3 transition-colors hover:border-violet-500/60 has-checked:border-violet-400 has-checked:bg-violet-500/10 has-focus-visible:ring-2 has-focus-visible:ring-violet-400">
                <input type="radio" name="appearance" value={id} className="sr-only" checked={appearance === id}
                  onChange={() => { setAppearance(id); setCurrentAppearance(id); }} />
                {/* A tiny mock page in this appearance's own colors, so you can see it before picking. */}
                <span aria-hidden="true" className="flex h-16 items-center gap-2 rounded-lg border px-3"
                  style={{ backgroundColor: preview.canvas, borderColor: preview.line }}>
                  <span className="h-8 w-14 rounded-md border" style={{ backgroundColor: preview.surface, borderColor: preview.line }} />
                  <span className="flex flex-col gap-1.5">
                    <span className="h-2 w-16 rounded-full" style={{ backgroundColor: preview.accent }} />
                    <span className="h-2 w-10 rounded-full" style={{ backgroundColor: preview.accentAlt }} />
                  </span>
                </span>
                <span>
                  <span className="block text-sm font-semibold">{label}{appearance === id && <span aria-hidden="true" className="ml-2 text-xs font-normal text-muted">Current</span>}</span>
                  <span className="block text-sm text-muted">{description}</span>
                </span>
              </label>
            ))}
          </div>
        </section>
        <form onSubmit={saveName} aria-labelledby="display-name-heading" className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-5">
          <div>
            <h2 id="display-name-heading" className="font-semibold">Display name</h2>
            <p className="mt-1 text-sm text-muted">Shown on your profile and to other developers.</p>
            <p className="mt-2 text-sm">Current display name: <strong>{user?.full_name}</strong></p>
          </div>
          <label className="flex flex-col gap-1.5 text-sm">
            Display name
            <input className="field" autoComplete="name" required maxLength={120} value={name} disabled={savingName}
              onChange={(event) => { setName(event.target.value); setNameSaved(false); setNameError(""); }} />
          </label>
          {nameError && <p role="alert" className="text-sm text-rose-300">{nameError}</p>}
          {nameSaved && <p role="status" className="text-sm text-emerald-300">Display name saved. <Link to="/profile" className="underline">View your profile</Link></p>}
          <button className={buttonClass} disabled={savingName || !name.trim() || name.trim() === user?.full_name}>
            {savingName ? "Saving…" : "Save display name"}
          </button>
        </form>
        <form onSubmit={savePassword} aria-labelledby="password-heading" className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-5">
          <div>
            <h2 id="password-heading" className="font-semibold">Change password</h2>
            <p className="mt-1 text-sm text-muted">Use 8–128 characters. Your new password takes effect when saved.</p>
          </div>
          <input type="text" name="username" autoComplete="username" value={user?.username ?? ""} readOnly hidden />
          <fieldset disabled={savingPassword} className="flex flex-col gap-4">
            <label className="flex flex-col gap-1.5 text-sm">
              Current password
              <input className="field" type="password" autoComplete="current-password" required value={currentPassword}
                onChange={(event) => { setCurrentPassword(event.target.value); setPasswordSaved(false); setPasswordError(""); }} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              New password
              <input className="field" type="password" autoComplete="new-password" required minLength={8} maxLength={128} value={newPassword}
                onChange={(event) => { setNewPassword(event.target.value); setPasswordSaved(false); setPasswordError(""); }} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              Confirm new password
              <input className="field" type="password" autoComplete="new-password" required minLength={8} maxLength={128} value={confirmation}
                onChange={(event) => { setConfirmation(event.target.value); setPasswordSaved(false); setPasswordError(""); }} />
            </label>
          </fieldset>
          {passwordError && <p role="alert" className="text-sm text-rose-300">{passwordError}</p>}
          {passwordSaved && <p role="status" className="text-sm text-emerald-300">Password changed. Use your new password next time you log in.</p>}
          <button className={buttonClass} disabled={savingPassword}>
            {savingPassword ? "Saving…" : "Save password"}
          </button>
        </form>
      </main>
    </>
  );
}
