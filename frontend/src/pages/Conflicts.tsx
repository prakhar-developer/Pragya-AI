import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import {
  AlertTriangle,
  CheckCircle2,
  FileDown,
  Loader2,
  ShieldCheck,
  X,
  Wrench,
} from "lucide-react";
import {
  useConflicts,
  useGenerateWorkOrder,
  useResolveConflict,
} from "../hooks/useConflicts";
import type { Conflict } from "../services/types";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { CardSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { Button } from "../components/ui/Button";
import { formatINR, formatDate, severityLabel } from "../lib/utils";

const FILTERS = [
  { key: undefined, label: "All" },
  { key: "open", label: "Open" },
  { key: "resolved", label: "Resolved" },
];

function severityStyle(sev: number) {
  if (sev >= 4) return "bg-rose-50 text-rose-700 border-rose-100";
  if (sev >= 3) return "bg-amber-50 text-amber-700 border-amber-100";
  return "bg-teal-50 text-teal-700 border-teal-100";
}

function ConflictCard({
  conflict,
  onGenerate,
  onResolve,
  generating,
  resolving,
}: {
  conflict: Conflict;
  onGenerate: (c: Conflict) => void;
  onResolve: (c: Conflict) => void;
  generating: boolean;
  resolving: boolean;
}) {
  const resolved = conflict.status === "resolved";
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-border bg-card p-5 shadow-sm"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-rose-50 text-rose-700">
            <AlertTriangle size={17} />
          </span>
          {conflict.equipment_tag && (
            <span className="font-mono text-xs text-muted">
              {conflict.equipment_tag}
            </span>
          )}
        </div>
        <span
          className={`rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-medium ${severityStyle(
            conflict.severity
          )}`}
        >
          {severityLabel(conflict.severity)}
        </span>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-body">
        {conflict.description}
      </p>

      {conflict.recommended_action && (
        <p className="mt-2 text-xs text-muted">
          <span className="font-medium text-teal-700">Action: </span>
          {conflict.recommended_action}
        </p>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
        {conflict.financial_exposure_inr != null && (
          <span className="font-mono font-semibold text-rose-700">
            {formatINR(conflict.financial_exposure_inr)}
          </span>
        )}
        {conflict.deadline && <span>Due {formatDate(conflict.deadline)}</span>}
        {conflict.regulatory_reference && (
          <span className="font-mono">{conflict.regulatory_reference}</span>
        )}
      </div>

      <div className="mt-4 flex items-center gap-2 border-t border-border pt-4">
        {resolved ? (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-medium text-teal-700">
            <CheckCircle2 size={14} /> Resolved{" "}
            {conflict.resolved_at ? `· ${formatDate(conflict.resolved_at)}` : ""}
          </span>
        ) : (
          <Button
            variant="secondary"
            onClick={() => onResolve(conflict)}
            disabled={resolving}
            className="px-3 py-1.5 text-xs"
          >
            {resolving ? (
              <Loader2 size={13} className="animate-spin" />
            ) : (
              <ShieldCheck size={13} />
            )}
            Resolve
          </Button>
        )}
        <Button
          variant="ghost"
          onClick={() => onGenerate(conflict)}
          disabled={generating}
          className="px-3 py-1.5 text-xs"
        >
          {generating ? (
            <Loader2 size={13} className="animate-spin" />
          ) : (
            <FileDown size={13} />
          )}
          Work order
        </Button>
      </div>
    </motion.div>
  );
}

function WorkOrderModal({
  conflict,
  onClose,
  onConfirm,
  generating,
}: {
  conflict: Conflict;
  onClose: () => void;
  onConfirm: () => void;
  generating: boolean;
}) {
  const rows: [string, string][] = [
    ["Description", conflict.description],
    ["Equipment tag", conflict.equipment_tag ?? "—"],
    ["Recommended action", conflict.recommended_action ?? "—"],
    ["Responsible role", conflict.responsible_role ?? "shift_supervisor"],
    ["Deadline", formatDate(conflict.deadline)],
    ["Regulatory reference", conflict.regulatory_reference ?? "—"],
    ["Financial exposure", formatINR(conflict.financial_exposure_inr)],
  ];
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="relative w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-card"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-50 text-violet-700">
              <Wrench size={17} />
            </span>
            <div>
              <h2 className="text-base font-semibold text-body">
                Pre-filled work order
              </h2>
              <p className="text-xs text-muted">Review before generating PDF</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted hover:bg-background"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-4 divide-y divide-border rounded-xl border border-border">
          {rows.map(([k, v]) => (
            <div key={k} className="flex gap-3 px-3.5 py-2.5">
              <span className="w-40 shrink-0 text-xs font-medium text-muted">
                {k}
              </span>
              <span className="flex-1 text-sm text-body">{v}</span>
            </div>
          ))}
        </div>

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onConfirm} disabled={generating}>
            {generating ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <FileDown size={15} />
            )}
            Generate PDF
          </Button>
        </div>
      </motion.div>
    </div>
  );
}

export function Conflicts() {
  const [status, setStatus] = useState<string | undefined>(undefined);
  const [modal, setModal] = useState<Conflict | null>(null);
  const { data, isLoading, isError, refetch } = useConflicts(status);
  const resolve = useResolveConflict();
  const generate = useGenerateWorkOrder();

  const handleResolve = (c: Conflict) => {
    resolve.mutate(c.id, {
      onSuccess: () => toast.success("Conflict resolved"),
      onError: () => toast.error("Could not resolve conflict"),
    });
  };

  const handleGenerate = (c: Conflict) => {
    generate.mutate(c.id, {
      onSuccess: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `work_order_${c.id}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success("Work order generated");
        setModal(null);
      },
      onError: () => toast.error("Could not generate work order"),
    });
  };

  return (
    <PageContainer>
      <PageHeader
        title="Conflicts"
        subtitle="Cross-agent conflicts detected across maintenance and compliance reasoning."
        actions={
          <div className="flex rounded-xl border border-border bg-card p-1">
            {FILTERS.map((f) => (
              <button
                key={f.label}
                onClick={() => setStatus(f.key)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  status === f.key
                    ? "bg-violet-50 text-violet-700"
                    : "text-muted hover:text-body"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        }
      />

      <div className="mt-6">
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : isError ? (
          <ErrorState
            message="Failed to load conflicts from the backend."
            onRetry={() => refetch()}
          />
        ) : !data || data.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            title="No conflicts found"
            message="No cross-agent conflicts match this filter. Run a Copilot query to surface new ones."
          />
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <AnimatePresence>
              {data.map((c) => (
                <ConflictCard
                  key={c.id}
                  conflict={c}
                  onGenerate={setModal}
                  onResolve={handleResolve}
                  generating={
                    generate.isPending && generate.variables === c.id
                  }
                  resolving={resolve.isPending && resolve.variables === c.id}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      <AnimatePresence>
        {modal && (
          <WorkOrderModal
            conflict={modal}
            onClose={() => setModal(null)}
            onConfirm={() => handleGenerate(modal)}
            generating={generate.isPending}
          />
        )}
      </AnimatePresence>
    </PageContainer>
  );
}
