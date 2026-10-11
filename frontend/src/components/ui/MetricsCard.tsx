import type { LucideIcon } from "lucide-react";
import { cn } from "../../lib/utils";

interface MetricsCardProps {
  label: string;
  value: string;
  icon?: LucideIcon;
  accent?: "violet" | "teal" | "rose" | "amber";
  sub?: string;
  className?: string;
}

const ACCENT: Record<string, { bg: string; text: string }> = {
  violet: { bg: "bg-violet-50", text: "text-violet-700" },
  teal: { bg: "bg-teal-50", text: "text-teal-700" },
  rose: { bg: "bg-rose-50", text: "text-rose-700" },
  amber: { bg: "bg-amber-50", text: "text-amber-700" },
};

export function MetricsCard({
  label,
  value,
  icon: Icon,
  accent = "violet",
  sub,
  className,
}: MetricsCardProps) {
  const a = ACCENT[accent];
  return (
    <div
      className={cn(
        "rounded-2xl border border-border bg-card p-5 shadow-sm",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <span className="text-sm font-medium text-muted">{label}</span>
        {Icon && (
          <span
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-xl",
              a.bg,
              a.text
            )}
          >
            <Icon size={18} />
          </span>
        )}
      </div>
      <div className="mt-3 font-mono text-2xl font-semibold tracking-tight text-body">
        {value}
      </div>
      {sub && <div className="mt-1 text-xs text-muted">{sub}</div>}
    </div>
  );
}
