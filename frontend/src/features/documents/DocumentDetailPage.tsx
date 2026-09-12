import { ArrowLeft, FileText, Layers } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useGetDocumentChunksQuery, useGetDocumentQuery } from "../../api/documentApi";
import { AppLayout } from "../../components/AppLayout";
import { ChunkScatterPlot } from "./ChunkScatterPlot";
import { StatusBadge } from "./StatusBadge";

const POLL_MS = 4000;

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [pollingInterval, setPollingInterval] = useState<number>(POLL_MS);

  const { data: document, isLoading } = useGetDocumentQuery(id!, { pollingInterval });

  // Intentionally an effect - synchronizes RTK Query's own polling timer (an
  // external system) with the document's last known status, same reasoning
  // as DocumentsList.
  useEffect(() => {
    if (!document) return;
    const pending = document.status === "queued" || document.status === "processing";
    setPollingInterval(pending ? POLL_MS : 0);
  }, [document]);

  const isIndexed = document?.status === "indexed";
  const { data: chunks, isLoading: chunksLoading } = useGetDocumentChunksQuery(id!, {
    skip: !isIndexed,
  });

  return (
    <AppLayout>
      <Link
        to="/documents"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900"
      >
        <ArrowLeft className="size-4" />
        All documents
      </Link>

      {isLoading && <p className="text-sm text-slate-500">Loading…</p>}

      {document && (
        <>
          <div className="mb-6 flex items-start justify-between rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center gap-3">
              <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                <FileText className="size-5" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900">{document.filename}</h1>
                <p className="text-xs text-slate-500">
                  {formatSize(document.size_bytes)} · {document.content_type} ·{" "}
                  {new Date(document.created_at).toLocaleString()}
                </p>
              </div>
            </div>
            <StatusBadge status={document.status} />
          </div>

          <div className="animate-fade-in-up rounded-xl bg-white shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center gap-2 border-b border-slate-200 px-6 py-4">
              <Layers className="size-4 text-slate-400" />
              <h2 className="text-sm font-semibold text-slate-900">
                Indexed chunks {chunks ? `(${chunks.length})` : ""}
              </h2>
            </div>

            {!isIndexed && (
              <p className="px-6 py-10 text-center text-sm text-slate-500">
                {document.status === "failed"
                  ? "Ingestion failed for this document - no chunks were indexed."
                  : "Waiting for ingestion to finish before chunks are available."}
              </p>
            )}

            {isIndexed && chunksLoading && (
              <p className="px-6 py-10 text-center text-sm text-slate-500">Loading chunks…</p>
            )}

            {isIndexed && chunks && chunks.length === 0 && (
              <p className="px-6 py-10 text-center text-sm text-slate-500">
                No chunks were produced for this document (it may have been empty).
              </p>
            )}

            {isIndexed && chunks && chunks.length > 0 && (
              <div className="p-4">
                <p className="mb-2 px-2 text-xs text-slate-400">
                  Each point is one indexed chunk, positioned by a 2D projection of its embedding
                  vector. Hover a point to read its text.
                </p>
                <ChunkScatterPlot points={chunks} />
              </div>
            )}
          </div>
        </>
      )}
    </AppLayout>
  );
}
