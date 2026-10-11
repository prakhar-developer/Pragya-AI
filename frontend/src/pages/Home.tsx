import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  ChevronDown,
  FileSearch,
  GitMerge,
  MessagesSquare,
  Sparkles,
  TrendingDown,
  Clock,
  ShieldCheck,
} from "lucide-react";
import { InfiniteGrid } from "../components/ui/infinite-grid";
import { useCountUp } from "../hooks/useCountUp";

function StatCard({
  target,
  suffix,
  label,
  decimals = 0,
}: {
  target: number;
  suffix: string;
  label: string;
  decimals?: number;
}) {
  const value = useCountUp(target);
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="font-mono text-3xl font-semibold text-violet-700">
        {value.toFixed(decimals)}
        {suffix}
      </div>
      <div className="mt-2 text-sm text-muted">{label}</div>
    </div>
  );
}

const STEPS = [
  {
    icon: FileSearch,
    title: "Ingest & extract",
    body: "Regulations, permits, work orders and expert notes are parsed into a connected knowledge graph.",
  },
  {
    icon: GitMerge,
    title: "Reason across agents",
    body: "Copilot, maintenance and compliance agents assess each query in parallel and surface conflicts.",
  },
  {
    icon: ShieldCheck,
    title: "Synthesize & act",
    body: "A single arbitrated recommendation with financial exposure, citations and ready-to-run work orders.",
  },
];

const METRICS = [
  { icon: TrendingDown, value: "35%", label: "Fewer unplanned shutdowns" },
  { icon: Clock, value: "18–22%", label: "Faster decision cycles" },
  { icon: ShieldCheck, value: "25%", label: "Higher compliance coverage" },
];

export function Home() {
  return (
    <div>
      <section className="relative overflow-hidden">
        <InfiniteGrid />
        <div className="relative mx-auto max-w-5xl px-4 pb-20 pt-24 text-center sm:px-6 lg:pt-32">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mx-auto inline-flex items-center gap-2 rounded-full border border-violet-100 bg-violet-50 px-3 py-1 font-mono text-xs text-violet-700"
          >
            <Sparkles size={13} />
            Industrial Knowledge Reasoning Engine
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            className="mt-6 text-4xl font-semibold tracking-tight text-body sm:text-6xl"
          >
            Industrial Knowledge.{" "}
            <span className="text-violet-700">Connected.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.12 }}
            className="mx-auto mt-5 max-w-2xl text-lg text-muted"
          >
            PRAGYA AI unifies regulations, maintenance history and expert
            knowledge into one reasoning engine — so refinery teams decide
            faster, safer and with full traceability.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.18 }}
            className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Link
              to="/copilot"
              className="inline-flex items-center gap-2 rounded-xl bg-violet px-5 py-3 text-sm font-medium text-white shadow-sm transition-colors hover:bg-violet-800"
            >
              <MessagesSquare size={17} />
              Ask the Copilot
            </Link>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-5 py-3 text-sm font-medium text-body transition-colors hover:bg-background"
            >
              View Dashboard
              <ArrowRight size={17} />
            </Link>
          </motion.div>

          <div className="mx-auto mt-16 grid max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard target={35} suffix="%" label="Fewer unplanned shutdowns" />
            <StatCard target={22} suffix="%" label="Faster decision cycles" />
            <StatCard target={25} suffix="%" label="Higher compliance coverage" />
          </div>

          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.8, repeat: Infinity }}
            className="mt-16 flex justify-center text-muted"
          >
            <ChevronDown size={22} />
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-semibold tracking-tight text-body">
          How PRAGYA AI works
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-5 md:grid-cols-3">
          {STEPS.map(({ icon: Icon, title, body }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="rounded-2xl border border-border bg-card p-6 shadow-sm"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-violet-50 text-violet-700">
                <Icon size={20} />
              </span>
              <div className="mt-4 font-mono text-xs text-muted">
                STEP {i + 1}
              </div>
              <h3 className="mt-1 text-lg font-semibold text-body">{title}</h3>
              <p className="mt-2 text-sm text-muted">{body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="border-t border-border bg-card">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-10 sm:grid-cols-3 sm:px-6">
          {METRICS.map(({ icon: Icon, value, label }) => (
            <div key={label} className="flex items-center gap-4">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-50 text-teal-700">
                <Icon size={22} />
              </span>
              <div>
                <div className="font-mono text-2xl font-semibold text-body">
                  {value}
                </div>
                <div className="text-sm text-muted">{label}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-border bg-slate-50/70 py-6 text-center text-xs text-muted">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 sm:flex-row sm:px-6">
          <p>
            PRAGYA AI &copy; {new Date().getFullYear()} &mdash; Engineered by{" "}
            <a
              href="https://github.com/prakhar-developer"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-slate-800 hover:text-teal-600 underline underline-offset-2"
            >
              Prakhar Srivastava
            </a>
          </p>
          <div className="flex items-center gap-4 text-xs font-medium">
            <a
              href="https://github.com/prakhar-developer"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-teal-600 transition-colors"
            >
              GitHub
            </a>
            <span>&bull;</span>
            <a
              href="https://www.linkedin.com/in/prakhar--developer/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-teal-600 transition-colors"
            >
              LinkedIn
            </a>
            <span>&bull;</span>
            <a
              href="https://prakhar-developer.web.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-teal-600 transition-colors"
            >
              Portfolio
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
