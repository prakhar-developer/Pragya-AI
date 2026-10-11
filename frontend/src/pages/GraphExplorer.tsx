import { useState, useMemo } from "react";
import { Share2, Search } from "lucide-react";
import { useGraph, useNodeDetail } from "../hooks/useGraph";
import {
  GraphCanvas,
  GraphLegend,
  NodeDetailPanel,
} from "../components/graph/GraphCanvas";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";

const CRIT_FILTERS = [
  { key: "all", label: "All Nodes" },
  { key: "process_critical", label: "Process Critical" },
  { key: "safety_critical", label: "Safety Critical" },
  { key: "utility", label: "Utility" },
];

export function GraphExplorer() {
  const [selected, setSelected] = useState<string | null>("Pump-7A");
  const [critFilter, setCritFilter] = useState("all");
  const [search, setSearch] = useState("");
  const { data, isLoading, isError, refetch } = useGraph();
  const detail = useNodeDetail(selected);

  const filteredData = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    let nodes = data.nodes;

    if (critFilter !== "all") {
      nodes = nodes.filter((n) => n.criticality === critFilter);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      nodes = nodes.filter(
        (n) =>
          n.label.toLowerCase().includes(q) ||
          n.id.toLowerCase().includes(q) ||
          (n.type || "").toLowerCase().includes(q)
      );
    }

    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = data.edges.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );

    return { nodes, edges };
  }, [data, critFilter, search]);

  const stats = useMemo(() => {
    if (!data) return { total: 0, edges: 0, processCrit: 0, safetyCrit: 0 };
    return {
      total: data.nodes.length,
      edges: data.edges.length,
      processCrit: data.nodes.filter((n) => n.criticality === "process_critical").length,
      safetyCrit: data.nodes.filter((n) => n.criticality === "safety_critical").length,
    };
  }, [data]);

  return (
    <PageContainer>
      <PageHeader
        title="Knowledge Graph Explorer"
        subtitle="Explore connected industrial equipment, work orders, active permits, and regulatory compliance entities in real-time."
        actions={<GraphLegend />}
      />

      {/* Graph Stats Bar */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-3 shadow-sm">
          <div className="font-mono text-xs text-muted">Total Entities</div>
          <div className="mt-1 font-mono text-xl font-semibold text-body">{stats.total}</div>
        </div>
        <div className="rounded-xl border border-border bg-card p-3 shadow-sm">
          <div className="font-mono text-xs text-muted">Graph Relationships</div>
          <div className="mt-1 font-mono text-xl font-semibold text-body">{stats.edges}</div>
        </div>
        <div className="rounded-xl border border-border bg-card p-3 shadow-sm">
          <div className="font-mono text-xs text-rose-700">Process Critical</div>
          <div className="mt-1 font-mono text-xl font-semibold text-rose-700">{stats.processCrit}</div>
        </div>
        <div className="rounded-xl border border-border bg-card p-3 shadow-sm">
          <div className="font-mono text-xs text-amber-700">Safety Critical</div>
          <div className="mt-1 font-mono text-xl font-semibold text-amber-700">{stats.safetyCrit}</div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-1.5 rounded-xl border border-border bg-card p-1">
          {CRIT_FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setCritFilter(f.key)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                critFilter === f.key
                  ? "bg-violet-50 text-violet-700 font-semibold"
                  : "text-muted hover:text-body"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search size={14} className="absolute left-3 top-3 text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tags, equipment, permits…"
            className="w-full rounded-xl border border-border bg-card py-2 pl-9 pr-3 text-xs text-body outline-none focus:border-violet-300"
          />
        </div>
      </div>

      {/* Quick Tag Selector Chips */}
      {data && data.nodes.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-1.5">
          <span className="font-mono text-[11px] text-muted mr-1">Quick Inspect:</span>
          {data.nodes.slice(0, 8).map((node) => (
            <button
              key={node.id}
              onClick={() => setSelected(node.id)}
              className={`rounded-lg px-2.5 py-1 font-mono text-[11px] transition-colors border ${
                selected === node.id
                  ? "bg-violet text-white border-violet"
                  : "bg-card text-muted hover:text-body border-border hover:border-violet-200"
              }`}
            >
              {node.label}
            </button>
          ))}
        </div>
      )}

      {/* Main Canvas + Detail Area */}
      <div className="mt-4">
        {isLoading ? (
          <Skeleton className="h-[560px] w-full" />
        ) : isError ? (
          <ErrorState
            message="Failed to load the knowledge graph."
            onRetry={() => refetch()}
          />
        ) : !data || data.nodes.length === 0 ? (
          <EmptyState
            icon={Share2}
            title="Graph is empty"
            message="No entities have been ingested yet. Upload documents to build the knowledge graph."
          />
        ) : (
          <div className="flex flex-col gap-6 lg:flex-row">
            <div className="min-h-[500px] flex-1 overflow-hidden rounded-2xl border border-border bg-card shadow-sm relative">
              <GraphCanvas
                data={filteredData}
                selected={selected}
                onSelect={setSelected}
              />
            </div>
            {selected && (
              <NodeDetailPanel
                detail={detail.data}
                loading={detail.isLoading}
                onClose={() => setSelected(null)}
              />
            )}
          </div>
        )}
      </div>
    </PageContainer>
  );
}
