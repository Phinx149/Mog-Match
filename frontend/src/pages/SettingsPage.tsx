import { Bell, Lock, Palette } from "lucide-react";
import Navbar from "../components/layout/Navbar";

const PLACEHOLDERS = [
  { icon: Bell, title: "Notifications", text: "Match and message alerts — coming with matching." },
  { icon: Lock, title: "Account & privacy", text: "Sign-in and visibility controls — coming with authentication." },
  { icon: Palette, title: "Appearance", text: "Dark mode is the only mode. For now." },
];

export default function SettingsPage() {
  return (
    <>
      <Navbar />
      <main className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        {PLACEHOLDERS.map(({ icon: Icon, title, text }) => (
          <section key={title} className="flex items-start gap-4 rounded-2xl border border-line bg-surface p-5">
            <Icon className="mt-0.5 size-5 text-violet-300" aria-hidden />
            <div>
              <h2 className="font-medium">{title}</h2>
              <p className="mt-1 text-sm text-muted">{text}</p>
            </div>
          </section>
        ))}
      </main>
    </>
  );
}
