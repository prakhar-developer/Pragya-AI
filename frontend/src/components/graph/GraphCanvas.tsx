import { useEffect, useMemo, useRef, useState } from "react";
import * as d3 from "d3";
import { motion } from "framer-motion";
import { X, Share2, Circle } from "lucide-react";
import type { GraphExport, NodeDetail } from "../../services/types";

interface SimNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  type: string | null;
  criticality: string;
}

interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  relationship: string;
}

const CRIT_COLOR: Record<string, string> = {
  process_critical: "#9F1239",
  safety_critical: "#B45309",
  utility: "#0F766E",
  unknown: "#64748B",
};

function critColor(c: string) {
  return CRIT_COLOR[c] ?? "#6D28D9";
}

interface Props {
  data: GraphExport;
  onSelect: (tag: string) => void;
  selected: string | null;
}

export function GraphCanvas({ data, onSelect, selected }: Props) {
  const ref = useRef<SVGSVGElement>(null);
  const [dims, setDims] = useState({ w: 800, h: 560 });

  const { nodes, links } = useMemo(() => {
    const nodes: SimNode[] = data.nodes.map((n) => ({ ...n }));
    const ids = new Set(nodes.map((n) => n.id));
    const links: SimLink[] = data.edges
      .filter((e) => ids.has(e.source) && ids.has(e.target))
      .map((e) => ({
        source: e.source,
        target: e.target,
        relationship: e.relationship,
      }));
    return { nodes, links };
  }, [data]);

  useEffect(() => {
    const el = ref.current?.parentElement;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      setDims({ w: el.clientWidth, h: Math.max(480, el.clientHeight) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    if (!nodes.length) return;

    const { w, h } = dims;
    const container = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on("zoom", (event) => container.attr("transform", event.transform));
    svg.call(zoom as never);

    const sim = d3
      .forceSimulation<SimNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<SimNode, SimLink>(links)
          .id((d) => d.id)
          .distance(90)
      )
      .force("charge", d3.forceManyBody().strength(-260))
      .force("center", d3.forceCenter(w / 2, h / 2))
      .force("collide", d3.forceCollide(28));

    const link = container
      .append("g")
      .attr("stroke", "#E2E8F0")
      .attr("stroke-width", 1.5)
      .selectAll("line")
      .data(links)
      .join("line");

    const node = container
      .append("g")
      .selectAll<SVGGElement, SimNode>("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .on("click", (_e, d) => onSelect(d.id));

    node
      .append("circle")
      .attr("r", (d) => (d.id === selected ? 16 : 12))
      .attr("fill", (d) => critColor(d.criticality))
      .attr("stroke", (d) => (d.id === selected ? "#6D28D9" : "#FFFFFF"))
      .attr("stroke-width", (d) => (d.id === selected ? 3 : 2));

    node
      .append("text")
      .text((d) => d.label)
      .attr("x", 18)
      .attr("y", 4)
      .attr("font-size", "11px")
      .attr("font-family", "'JetBrains Mono', monospace")
      .attr("fill", "#1E293B");

    node.call(
      d3
        .drag<SVGGElement, SimNode>()
        .on("start", (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as never
    );

    sim.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0);
      node.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      sim.stop();
    };
  }, [nodes, links, dims, selected, onSelect]);

  return <svg ref={ref} width={dims.w} height={dims.h} className="block" />;
}

export function GraphLegend() {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {Object.entries(CRIT_COLOR).map(([k, color]) => (
        <span key={k} className="flex items-center gap-1.5 text-xs text-muted">
          <Circle size={10} fill={color} stroke={color} />
          {k.replace(/_/g, " ")}
        </span>
      ))}
    </div>
  );
}

export function NodeDetailPanel({
  detail,
  onClose,
  loading,
}: {
  detail: NodeDetail | undefined;
  onClose: () => void;
  loading: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      className="w-full rounded-2xl border border-border bg-card p-5 shadow-sm lg:w-80"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-50 text-violet-700">
            <Share2 size={16} />
          </span>
          <span className="font-mono text-sm font-semibold text-body">
            {detail?.tag ?? "…"}
          </span>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-muted hover:bg-background"
        >
          <X size={16} />
        </button>
      </div>

      {loading ? (
        <p className="mt-4 text-sm text-muted">Loading node…</p>
      ) : detail ? (
        <div className="mt-4 space-y-4">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-lg bg-background px-2.5 py-1 font-mono text-[11px] text-body">
              {detail.type ?? "unknown"}
            </span>
            <span
              className="rounded-lg px-2.5 py-1 font-mono text-[11px] text-white"
              style={{ background: critColor(detail.criticality) }}
            >
              {detail.criticality.replace(/_/g, " ")}
            </span>
          </div>

          <div>
            <div className="font-mono text-[11px] uppercase tracking-wide text-muted">
              State history
            </div>
            {detail.state_history.length === 0 ? (
              <p className="mt-1 text-xs text-muted">No recorded transitions.</p>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {detail.state_history.slice(0, 8).map((s, i) => (
                  <li
                    key={i}
                    className="rounded-lg border border-border bg-background px-2.5 py-1.5 font-mono text-[11px] text-body"
                  >
                    {String(s.state ?? s.to_state ?? JSON.stringify(s))}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <div className="font-mono text-[11px] uppercase tracking-wide text-muted">
              Neighbours ({detail.neighbours.length})
            </div>
            <ul className="mt-2 space-y-1.5">
              {detail.neighbours.slice(0, 10).map((n, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs"
                >
                  <span className="font-mono text-body">
                    {String(
                      (n.entity as Record<string, unknown>).tag ?? "entity"
                    )}
                  </span>
                  <span className="font-mono text-[10px] text-muted">
                    {n.rel}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <p className="mt-4 text-sm text-muted">Node not found.</p>
      )}
    </motion.div>
  );
}
