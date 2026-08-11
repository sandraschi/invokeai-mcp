import type { ReactNode } from "react";

export function MockBadge({ text = "MOCK" }: { text?: string }) {
  return (
    <span
      className="rounded border border-rose-500/50 bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-rose-400"
      data-testid="mock-badge"
    >
      {text}
    </span>
  );
}

export function MockBanner() {
  return (
    <div
      className="mb-4 rounded-lg border border-dashed border-rose-500/40 bg-rose-500/5 px-4 py-2 text-xs text-rose-300"
      data-testid="mock-data-banner"
    >
      [MOCK] Sample data - connect InvokeAI to see live content. Complete
      onboarding (docs/ONBOARDING.md) and this clears automatically.
    </div>
  );
}

export function KpiCard({
  label,
  value,
  icon,
  testid,
  accent = "text-amber-400",
}: {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  testid: string;
  accent?: string;
}) {
  return (
    <div
      className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur"
      data-testid={testid}
    >
      <div className="flex items-center gap-2 text-xs text-slate-500">
        {icon}
        {label}
      </div>
      <div className={`mt-1.5 text-2xl font-bold ${accent}`}>{value}</div>
    </div>
  );
}

export function SectionCard({
  title,
  children,
  testid,
  actions,
}: {
  title: string;
  children: ReactNode;
  testid?: string;
  actions?: ReactNode;
}) {
  return (
    <div
      className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur"
      data-testid={testid}
    >
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-200">{title}</h2>
        {actions}
      </div>
      {children}
    </div>
  );
}

export function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${
        ok
          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
          : "border-red-500/40 bg-red-500/10 text-red-300"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-emerald-400" : "bg-red-400"}`}
      />
      {label}
    </span>
  );
}

export function PageHeader({
  title,
  subtitle,
}: { title: string; subtitle?: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-slate-100">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  hint,
}: { icon: ReactNode; title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-12 text-center">
      <div className="mb-2 text-slate-600">{icon}</div>
      <div className="text-sm font-medium text-slate-400">{title}</div>
      {hint && (
        <div className="mt-1 max-w-sm text-xs text-slate-600">{hint}</div>
      )}
    </div>
  );
}

export function Spinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-6 text-sm text-slate-500">
      <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-amber-400" />
      {label}
    </div>
  );
}
