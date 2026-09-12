import { ChevronLeft, ChevronRight, FileText, Inbox, Search, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useListDocumentsQuery } from "../../api/documentApi";
import { StatusBadge } from "./StatusBadge";
import { useDebouncedValue } from "./useDebouncedValue";

const PAGE_SIZE = 10;
const POLL_MS = 4000;

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function DocumentsList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 300);

  // Ingestion happens async in a separate worker - poll while anything on
  // this page is still queued/processing, so status updates without a
  // manual refresh; stop once nothing's pending so this doesn't hit the API
  // forever on an idle screen. Starts polling (rather than off) so the very
  // first fetch's result is itself picked up promptly.
  const [pollingInterval, setPollingInterval] = useState<number>(POLL_MS);

  const { data, isLoading, isFetching } = useListDocumentsQuery(
    { page, page_size: PAGE_SIZE, search: debouncedSearch || undefined },
    { pollingInterval },
  );

  // Intentionally an effect, not derived-during-render: this synchronizes
  // RTK Query's own polling timer (an external system) with its last
  // result, not just local UI state.
  useEffect(() => {
    if (!data) return;
    const hasPending = data.data.some((d) => d.status === "queued" || d.status === "processing");
    setPollingInterval(hasPending ? POLL_MS : 0);
  }, [data]);

  function handleSearchChange(value: string) {
    setSearch(value);
    setPage(1);
  }

  const totalPages = data?.meta.total_pages ?? 1;

  return (
    <div className="animate-fade-in-up rounded-xl bg-white shadow-sm ring-1 ring-slate-200">
      <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-6 py-4">
        <h2 className="text-sm font-semibold text-slate-900">All documents</h2>
        <div className="flex items-center gap-3">
          {isFetching && (
            <span className="flex items-center gap-1.5 text-xs text-slate-400">
              <RefreshCw className="size-3.5 animate-spin" />
              Refreshing…
            </span>
          )}
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search by filename"
              className="w-48 rounded-lg border border-slate-300 py-1.5 pl-8 pr-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
            />
          </div>
        </div>
      </div>

      {isLoading && <p className="px-6 py-10 text-center text-sm text-slate-500">Loading…</p>}

      {!isLoading && data?.data.length === 0 && (
        <div className="flex flex-col items-center gap-2 px-6 py-12 text-center">
          <Inbox className="size-8 text-slate-300" />
          <p className="text-sm text-slate-500">
            {debouncedSearch ? `No documents match "${debouncedSearch}".` : "No documents uploaded yet."}
          </p>
        </div>
      )}

      {!isLoading && data && data.data.length > 0 && (
        <ul className="divide-y divide-slate-100">
          {data.data.map((doc) => (
            <li key={doc.id}>
              <Link
                to={`/documents/${doc.id}`}
                className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-slate-50"
              >
                <div className="flex items-center gap-3">
                  <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                    <FileText className="size-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">{doc.filename}</p>
                    <p className="text-xs text-slate-500">
                      {formatSize(doc.size_bytes)} · {new Date(doc.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <StatusBadge status={doc.status} />
              </Link>
            </li>
          ))}
        </ul>
      )}

      {!isLoading && data && data.meta.total_items > 0 && (
        <div className="flex items-center justify-between border-t border-slate-200 px-6 py-3">
          <p className="text-xs text-slate-500">
            Page {data.meta.page} of {totalPages} · {data.meta.total_items} total
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="size-4" />
              Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
              <ChevronRight className="size-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
