import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react";

import type { DocumentStatus } from "../../api/types";

const CONFIG: Record<DocumentStatus, { style: string; icon: typeof Clock; spin?: boolean }> = {
  queued: { style: "bg-slate-100 text-slate-600", icon: Clock },
  processing: { style: "bg-amber-100 text-amber-700", icon: Loader2, spin: true },
  indexed: { style: "bg-green-100 text-green-700", icon: CheckCircle2 },
  failed: { style: "bg-red-100 text-red-700", icon: XCircle },
};

export function StatusBadge({ status }: { status: DocumentStatus }) {
  const { style, icon: Icon, spin } = CONFIG[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${style}`}>
      <Icon className={`size-3.5 ${spin ? "animate-spin" : ""}`} />
      {status}
    </span>
  );
}
