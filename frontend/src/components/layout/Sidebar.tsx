import { NavLink } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { cn } from "../../lib/utils";
import { NAV_ITEMS } from "./navItems";

import { useQuery } from "@tanstack/react-query";
import { getSystemStatus } from "../../services/api";

export function Sidebar() {
  const { data: status } = useQuery({
    queryKey: ["systemStatus"],
    queryFn: getSystemStatus,
    refetchInterval: 15000,
    retry: 1,
  });

  const isLive = status?.mode === "live";

  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 shrink-0 flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2.5 px-6 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet text-white shadow-sm">
          <Sparkles size={18} />
        </div>
        <div className="leading-tight">
          <div className="font-semibold tracking-tight text-body">PRAGYA AI</div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-muted">
            Knowledge Engine
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-violet-50 text-violet-700"
                  : "text-muted hover:bg-background hover:text-body"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={18}
                  className={cn(isActive ? "text-violet-700" : "text-muted")}
                />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border px-4 py-3.5 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                status ? "bg-teal-600 animate-pulse-soft" : "bg-amber-500"
              )}
            />
            <span className="font-mono text-xs font-medium text-body">
              {isLive ? "Live Cloud Mode" : "Resilient Demo Mode"}
            </span>
          </div>
          <span className="rounded bg-slate-200/70 px-1.5 py-0.5 font-mono text-[9px] text-muted uppercase">
            v1.0
          </span>
        </div>

        <div className="mt-2.5 grid grid-cols-3 gap-1 text-[10px] font-mono">
          <div
            className={cn(
              "rounded px-1.5 py-1 text-center font-medium",
              status?.services.knowledge_graph.connected
                ? "bg-teal-50 text-teal-700 border border-teal-100"
                : "bg-slate-100 text-slate-600"
            )}
            title="Neo4j Aura Knowledge Graph"
          >
            Neo4j
          </div>
          <div
            className={cn(
              "rounded px-1.5 py-1 text-center font-medium",
              status?.services.vector_store.connected
                ? "bg-teal-50 text-teal-700 border border-teal-100"
                : "bg-slate-100 text-slate-600"
            )}
            title="Supabase Vector Store"
          >
            pgvector
          </div>
          <div
            className={cn(
              "rounded px-1.5 py-1 text-center font-medium",
              status?.services.reasoning_llm.connected
                ? "bg-teal-50 text-teal-700 border border-teal-100"
                : "bg-slate-100 text-slate-600"
            )}
            title="Groq Llama-3.3 Reasoning"
          >
            Groq
          </div>
        </div>

        <div className="mt-2.5 border-t border-slate-100 pt-2 text-[10px] text-slate-500 flex items-center justify-between">
          <span>Architect:</span>
          <a
            href="https://github.com/prakhar-developer"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-slate-700 hover:text-teal-600 transition-colors"
          >
            Prakhar Srivastava
          </a>
        </div>
      </div>
    </aside>
  );
}
