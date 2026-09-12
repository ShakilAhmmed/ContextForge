import type { LucideIcon } from "lucide-react";
import { Sparkle } from "lucide-react";

export function PageHeader({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-6 flex items-center gap-4 overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div className="relative flex size-12 shrink-0 items-center justify-center">
        <span className="absolute inset-0 animate-ping rounded-xl bg-indigo-400/30" />
        <div className="relative flex size-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-sm">
          <Icon className="size-6" />
        </div>
        <Sparkle
          className="absolute -right-1 -top-1 size-3 animate-pulse text-amber-400"
          style={{ animationDelay: "0.3s" }}
          fill="currentColor"
        />
        <Sparkle
          className="absolute -bottom-1 -left-1 size-2.5 animate-pulse text-violet-400"
          style={{ animationDelay: "0.8s" }}
          fill="currentColor"
        />
      </div>
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
        {description && <p className="text-sm text-slate-500">{description}</p>}
      </div>
    </div>
  );
}
