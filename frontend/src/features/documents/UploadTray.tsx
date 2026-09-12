import { CheckCircle2, File as FileIcon, Loader2, X, XCircle } from "lucide-react";
import type { ReactNode } from "react";

import type { UploadItem, UploadStatus } from "./useUploadTray";

const STATUS_ICON: Record<UploadStatus, ReactNode> = {
  uploading: <Loader2 className="size-4 shrink-0 animate-spin text-indigo-500" />,
  success: <CheckCircle2 className="size-4 shrink-0 text-green-600" />,
  error: <XCircle className="size-4 shrink-0 text-red-600" />,
};

function trayHeading(items: UploadItem[]): string {
  const uploading = items.filter((i) => i.status === "uploading").length;
  if (uploading > 0) return `Uploading ${uploading} item(s)…`;

  const failed = items.filter((i) => i.status === "error").length;
  if (failed > 0) return `${failed} of ${items.length} failed`;

  return "Uploads complete";
}

export function UploadTray({
  items,
  onDismiss,
}: {
  items: UploadItem[];
  onDismiss: (id: string) => void;
}) {
  if (items.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 w-80 animate-fade-in-up overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-slate-200">
      <div className="border-b border-slate-200 px-4 py-3">
        <p className="text-sm font-semibold text-slate-900">{trayHeading(items)}</p>
      </div>
      <ul className="max-h-64 divide-y divide-slate-100 overflow-y-auto">
        {items.map((item) => (
          <li key={item.id} className="flex flex-col gap-1 px-4 py-2.5">
            <div className="flex items-center gap-2">
              <FileIcon className="size-4 shrink-0 text-slate-400" />
              <span className="flex-1 truncate text-sm text-slate-700">{item.filename}</span>
              {STATUS_ICON[item.status]}
              {item.status !== "uploading" && (
                <button
                  onClick={() => onDismiss(item.id)}
                  className="text-slate-300 hover:text-slate-500"
                  aria-label="Dismiss"
                >
                  <X className="size-3.5" />
                </button>
              )}
            </div>
            {item.status === "error" && item.error && (
              <p className="pl-6 text-xs text-red-600">{item.error}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
