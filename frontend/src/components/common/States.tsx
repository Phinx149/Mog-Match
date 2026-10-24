import { AlertTriangle, Loader2 } from "lucide-react";
import type { ReactNode } from "react";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-muted">
      <Loader2 className="size-5 animate-spin" aria-hidden />
      {label}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="mx-auto my-10 max-w-md rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-center">
      <AlertTriangle className="mx-auto mb-3 size-6 text-rose-400" aria-hidden />
      <p className="text-sm text-rose-200">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg border border-rose-400/40 px-4 py-1.5 text-sm text-rose-100 hover:bg-rose-500/20"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="mx-auto my-10 max-w-md rounded-2xl border border-dashed border-line p-8 text-center">
      <p className="font-medium text-slate-200">{title}</p>
      {children && <div className="mt-2 text-sm text-muted">{children}</div>}
    </div>
  );
}
