import { Loader2 } from "lucide-react";
import type { ReactNode } from "react";

export function SubmitButton({
  loading,
  children,
  className = "",
}: {
  loading: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <button
      type="submit"
      disabled={loading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 disabled:active:scale-100 ${className}`}
    >
      {loading && <Loader2 className="size-4 animate-spin" />}
      {children}
    </button>
  );
}
