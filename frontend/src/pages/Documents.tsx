import { useRef, useState } from "react";
import toast from "react-hot-toast";
import {
  UploadCloud,
  FileText,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { useDocuments, useUploadDocuments } from "../hooks/useDocuments";
import type { BatchUploadResponse } from "../services/types";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { RowSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { formatDate } from "../lib/utils";

function docTypeStyle(type: string) {
  const map: Record<string, string> = {
    regulation: "bg-violet-50 text-violet-700",
    work_order: "bg-teal-50 text-teal-700",
    permit: "bg-amber-50 text-amber-700",
    procedure: "bg-slate-100 text-body",
    expert_tacit: "bg-rose-50 text-rose-700",
  };
  return map[type] ?? "bg-slate-100 text-body";
}

export function Documents() {
  const [dragging, setDragging] = useState(false);
  const [summary, setSummary] = useState<BatchUploadResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { data, isLoading, isError, refetch } = useDocuments();
  const upload = useUploadDocuments();

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const files = Array.from(fileList);
    const label =
      files.length === 1 ? files[0].name : `${files.length} files`;
    const toastId = toast.loading(`Uploading ${label}…`);
    upload.mutate(files, {
      onSuccess: (res) => {
        setSummary(res);
        if (res.failed === 0) {
          toast.success(
            `Ingested ${res.succeeded} file(s) · ${res.total_chunks} chunks`,
            { id: toastId }
          );
        } else {
          toast.error(
            `${res.succeeded} succeeded, ${res.failed} failed`,
            { id: toastId }
          );
        }
      },
      onError: () => toast.error("Upload failed", { id: toastId }),
    });
  };

  const handleIngestSample = () => {
    const sampleText = `OISD-GDN-105 AMENDMENT 2026:
Mandatory simultaneous operations (SIMOPS) protocol on heavy distillate units.
Hot work permits (PTW) are strictly invalid during open flange mechanical intervention on adjacent hydrocarbon lines.
Equipment: Pump-7A, Line-4, PSV-220.
Requirement: Continuous gas sniff test with explosive limits under 1% LEL before mechanical permit sign-off.`;
    const blob = new Blob([sampleText], { type: "text/plain" });
    const sampleFile = new File([blob], "OISD-GDN-105-SIMOPS-Amendment-2026.txt", { type: "text/plain" });
    handleFiles([sampleFile] as unknown as FileList);
  };

  return (
    <PageContainer>
      <PageHeader
        title="Documents"
        subtitle="Ingest regulations, permits, work orders and operational notes into the knowledge base."
        actions={
          <button
            onClick={handleIngestSample}
            disabled={upload.isPending}
            className="inline-flex items-center gap-1.5 rounded-xl border border-violet-200 bg-violet-50 px-3.5 py-1.5 text-xs font-medium text-violet-700 hover:bg-violet-100 transition-colors"
          >
            <FileText size={13} />
            + Ingest Sample OISD Amendment
          </button>
        }
      />

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors ${
          dragging
            ? "border-violet-300 bg-violet-50"
            : "border-border bg-card hover:border-violet-200"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.xlsx,.txt,.md,.csv,.log,image/*"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-50 text-violet-700">
          {upload.isPending ? (
            <Loader2 size={26} className="animate-spin" />
          ) : (
            <UploadCloud size={26} />
          )}
        </span>
        <p className="mt-4 text-sm font-medium text-body">
          {upload.isPending
            ? `Processing documents… ${upload.progress}%`
            : "Drag & drop documents, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-muted">
          Multiple files supported — PDF, images and text parsed, embedded and
          linked automatically
        </p>

        {upload.isPending && (
          <div className="mt-4 h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-violet-100">
            <div
              className="h-full rounded-full bg-violet transition-[width] duration-200"
              style={{ width: `${upload.progress}%` }}
            />
          </div>
        )}
      </div>

      {summary && (
        <div className="mt-4 rounded-2xl border border-border bg-card p-4">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm">
            <span className="font-medium text-body">
              {summary.total_files} file(s)
            </span>
            <span className="text-teal-700">
              {summary.succeeded} succeeded
            </span>
            {summary.failed > 0 && (
              <span className="text-rose-700">{summary.failed} failed</span>
            )}
            <span className="text-muted">
              {summary.total_chunks} chunks created
            </span>
          </div>
          <ul className="mt-3 space-y-1.5">
            {summary.results.map((r, i) => (
              <li key={i} className="flex items-center gap-2 text-xs">
                {r.status === "success" ? (
                  <CheckCircle2 size={14} className="shrink-0 text-teal-700" />
                ) : (
                  <XCircle size={14} className="shrink-0 text-rose-700" />
                )}
                <span className="font-mono text-body">{r.filename}</span>
                {r.status === "success" ? (
                  <span className="text-muted">· {r.chunk_count} chunks</span>
                ) : (
                  <span className="text-rose-700/80">· {r.reason}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8">
        <h2 className="mb-3 text-sm font-semibold text-body">
          Ingested documents
        </h2>
        {isLoading ? (
          <div className="rounded-2xl border border-border bg-card">
            {Array.from({ length: 5 }).map((_, i) => (
              <RowSkeleton key={i} />
            ))}
          </div>
        ) : isError ? (
          <ErrorState
            message="Failed to load documents."
            onRetry={() => refetch()}
          />
        ) : !data || data.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents yet"
            message="Upload your first document above to start building the knowledge base."
          />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-background/60">
                <tr className="text-xs font-medium text-muted">
                  <th className="px-4 py-3">Filename</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="hidden px-4 py-3 md:table-cell">Summary</th>
                  <th className="px-4 py-3">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.map((doc) => (
                  <tr key={doc.id} className="hover:bg-background/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText size={15} className="text-muted" />
                        <span className="font-mono text-xs text-body">
                          {doc.filename}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-lg px-2 py-0.5 font-mono text-[11px] ${docTypeStyle(
                          doc.document_type
                        )}`}
                      >
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="hidden max-w-md px-4 py-3 text-xs text-muted md:table-cell">
                      <span className="line-clamp-2">{doc.summary}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted">
                      {formatDate(doc.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
