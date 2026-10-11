import { useMemo } from "react";
import {
  FileText,
  AlertTriangle,
  Share2,
  Gauge,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { useDocuments } from "../hooks/useDocuments";
import { useConflicts } from "../hooks/useConflicts";
import { useGraph } from "../hooks/useGraph";
import { useBenchmarks } from "../hooks/useBenchmarks";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { MetricsCard } from "../components/ui/MetricsCard";
import { CardSkeleton, RowSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { formatINR, formatDate } from "../lib/utils";

export function Dashboard() {
  const documents = useDocuments();
  const conflicts = useConflicts();
  const graph = useGraph();
  const benchmarks = useBenchmarks();

  const loading =
    documents.isLoading ||
    conflicts.isLoading ||
    graph.isLoading ||
    benchmarks.isLoading;

  const openConflicts = useMemo(
    () => (conflicts.data ?? []).filter((c) => c.status !== "resolved"),
    [conflicts.data]
  );

  const totalExposure = useMemo(
    () =>
      openConflicts.reduce(
        (sum, c) => sum + (c.financial_exposure_inr ?? 0),
        0
      ),
    [openConflicts]
  );

  const avgLatency = useMemo(() => {
    const runs = (benchmarks.data ?? []).filter(
      (b) => b.latency_seconds != null
    );
    if (!runs.length) return null;
    return (
      runs.reduce((s, b) => s + (b.latency_seconds ?? 0), 0) / runs.length
    );
  }, [benchmarks.data]);

  return (
    <PageContainer>
      <PageHeader
        title="Dashboard"
        subtitle="Live operational overview across knowledge, conflicts and benchmarks."
      />

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
        ) : (
          <>
            <MetricsCard
              label="Documents ingested"
              value={String(documents.data?.length ?? 0)}
              icon={FileText}
              accent="violet"
              sub="in knowledge base"
            />
            <MetricsCard
              label="Open conflicts"
              value={String(openConflicts.length)}
              icon={AlertTriangle}
              accent="rose"
              sub={`${conflicts.data?.length ?? 0} total detected`}
            />
            <MetricsCard
              label="Graph entities"
              value={String(graph.data?.nodes.length ?? 0)}
              icon={Share2}
              accent="teal"
              sub={`${graph.data?.edges.length ?? 0} relationships`}
            />
            <MetricsCard
              label="Financial exposure"
              value={formatINR(totalExposure)}
              icon={Gauge}
              accent="amber"
              sub="across open conflicts"
            />
          </>
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-rose-700" />
            <h2 className="text-sm font-semibold text-body">
              Recent conflicts
            </h2>
          </div>
          <div className="mt-3">
            {conflicts.isLoading ? (
              <div>
                {Array.from({ length: 3 }).map((_, i) => (
                  <RowSkeleton key={i} />
                ))}
              </div>
            ) : openConflicts.length === 0 ? (
              <EmptyState
                icon={CheckCircle2}
                title="All clear"
                message="No open conflicts right now."
              />
            ) : (
              <ul className="divide-y divide-border">
                {openConflicts.slice(0, 6).map((c) => (
                  <li
                    key={c.id}
                    className="flex items-start justify-between gap-3 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm text-body">
                        {c.description}
                      </p>
                      {c.equipment_tag && (
                        <span className="font-mono text-xs text-muted">
                          {c.equipment_tag}
                        </span>
                      )}
                    </div>
                    <span className="shrink-0 font-mono text-xs font-semibold text-rose-700">
                      {formatINR(c.financial_exposure_inr)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge size={16} className="text-violet-700" />
              <h2 className="text-sm font-semibold text-body">
                Benchmark results
              </h2>
            </div>
            {avgLatency != null && (
              <span className="inline-flex items-center gap-1 font-mono text-xs text-muted">
                <Clock size={12} /> {avgLatency.toFixed(1)}s avg
              </span>
            )}
          </div>
          <div className="mt-3">
            {benchmarks.isLoading ? (
              <div>
                {Array.from({ length: 3 }).map((_, i) => (
                  <RowSkeleton key={i} />
                ))}
              </div>
            ) : !benchmarks.data || benchmarks.data.length === 0 ? (
              <EmptyState
                icon={Gauge}
                title="No benchmark runs"
                message="Run the benchmark suite from the backend to populate results."
              />
            ) : (
              <ul className="divide-y divide-border">
                {benchmarks.data.slice(0, 6).map((b, i) => (
                  <li
                    key={b.id ?? b.query_id ?? i}
                    className="flex items-start justify-between gap-3 py-3"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-violet-700">
                          {b.query_id}
                        </span>
                        {b.category && (
                          <span className="rounded bg-background px-1.5 py-0.5 text-[10px] text-muted">
                            {b.category}
                          </span>
                        )}
                      </div>
                      <p className="mt-0.5 truncate text-sm text-body">
                        {b.question}
                      </p>
                    </div>
                    {b.latency_seconds != null && (
                      <span className="shrink-0 font-mono text-xs text-muted">
                        {b.latency_seconds.toFixed(1)}s
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <h2 className="mb-3 text-sm font-semibold text-body">
          Recently ingested documents
        </h2>
        {documents.isLoading ? (
          <div>
            {Array.from({ length: 4 }).map((_, i) => (
              <RowSkeleton key={i} />
            ))}
          </div>
        ) : !documents.data || documents.data.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents"
            message="Upload documents to populate the knowledge base."
          />
        ) : (
          <ul className="divide-y divide-border">
            {documents.data.slice(0, 6).map((d) => (
              <li
                key={d.id}
                className="flex items-center justify-between gap-3 py-3"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <FileText size={15} className="shrink-0 text-muted" />
                  <span className="truncate font-mono text-xs text-body">
                    {d.filename}
                  </span>
                  <span className="shrink-0 rounded bg-background px-1.5 py-0.5 font-mono text-[10px] text-muted">
                    {d.document_type}
                  </span>
                </div>
                <span className="shrink-0 text-xs text-muted">
                  {formatDate(d.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </PageContainer>
  );
}
