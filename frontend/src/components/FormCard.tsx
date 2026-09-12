import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function FormCard({
  title,
  description,
  icon: Icon,
  children,
  footer,
}: {
  title: string;
  description?: string;
  icon: LucideIcon;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-indigo-50 px-4">
      <div className="w-full max-w-sm animate-fade-in-up rounded-2xl bg-white p-8 shadow-lg shadow-slate-200/50 ring-1 ring-slate-200">
        <div className="mb-4 flex size-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm">
          <Icon className="size-5" />
        </div>
        <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
        {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
        <div className="mt-6">{children}</div>
        {footer && <div className="mt-6 text-sm text-slate-500">{footer}</div>}
      </div>
    </div>
  );
}
