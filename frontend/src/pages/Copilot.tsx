import { useMemo, useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Loader2,
  CheckCircle2,
  Cpu,
  AlertTriangle,
  Quote,
  Sparkles,
  RotateCw,
} from "lucide-react";
import { usePragyaQuery } from "../hooks/useQuery";
import type { AgentStep } from "../hooks/useQuery";
import { useTypingEffect } from "../hooks/useTypingEffect";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { EmptyState } from "../components/ui/EmptyState";
import { formatINR } from "../lib/utils";

const AGENT_LABELS: Record<string, string> = {
  routing: "Routing",
  copilot: "Copilot",
  maintenance: "Maintenance",
  compliance: "Compliance",
  synthesis: "Synthesis & Arbitration",
};

const SAMPLE_QUERIES = [
  "Can we perform welding on Line-4 this Saturday during Pump-7A overhaul?",
  "What is the minimum safe distance mandated by OISD-STD-118 between floating roof tanks?",
  "Check Pump-7A bearing temperature anomaly and assess degradation risk",
  "Is relief valve PSV-220 overdue for statutory OISD-STD-132 inspection?",
  "Are there conflicting operations between compressor K-301 maintenance and active permits?",
];

function agentLabel(agent: string) {
  return AGENT_LABELS[agent] ?? agent.replace(/_/g, " ");
}

function StepRow({ step }: { step: AgentStep }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-3 rounded-xl border border-border bg-card px-3.5 py-2.5"
    >
      <span
        className={
          step.status === "running"
            ? "text-violet-700"
            : "text-teal-700"
        }
      >
        {step.status === "running" ? (
          <Loader2 size={16} className="animate-spin" />
        ) : (
          <CheckCircle2 size={16} />
        )}
      </span>
      <span className="flex-1 text-sm font-medium text-body">
        {agentLabel(step.agent)}
      </span>
      <span className="font-mono text-[11px] uppercase tracking-wide text-muted">
        {step.status}
      </span>
    </motion.div>
  );
}

export function Copilot() {
  const [input, setInput] = useState("");
  const [lastQuery, setLastQuery] = useState("");
  const { steps, synthesis, isStreaming, error, run } = usePragyaQuery();
  const sessionId = useMemo(
    () => `web-${Math.floor(performance.now())}`,
    []
  );
  const scrollRef = useRef<HTMLDivElement>(null);

  const { visible: typedRecommendation, done: typingDone } = useTypingEffect(
    synthesis?.primary_recommendation ?? ""
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [steps.length, synthesis, typedRecommendation]);

  const submit = (q: string) => {
    const query = q.trim();
    if (!query || isStreaming) return;
    setLastQuery(query);
    setInput("");
    run(query, sessionId);
  };

  const citations = useMemo(() => {
    const set = new Set<string>();
    steps.forEach((s) => {
      const c = (s.output?.citations as string[]) ?? [];
      c.forEach((x) => set.add(String(x)));
    });
    synthesis?.conflicts?.forEach((c) => {
      if (c.description) set.add(c.description);
    });
    return Array.from(set);
  }, [steps, synthesis]);

  // Sources/citations are only revealed once the answer has finished typing.
  const showCitations = typingDone && citations.length > 0;

  const hasActivity = steps.length > 0 || synthesis || isStreaming || error;

  return (
    <PageContainer>
      <PageHeader
        title="Reasoning Copilot"
        subtitle="Ask across regulations, maintenance history and expert knowledge. Agents reason in parallel."
      />

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div
            ref={scrollRef}
            className="max-h-[calc(100vh-22rem)] min-h-[24rem] overflow-y-auto rounded-2xl border border-border bg-card p-5 shadow-sm"
          >
            {!hasActivity && (
              <div className="flex h-full flex-col justify-center">
                <EmptyState
                  icon={Sparkles}
                  title="Ask PRAGYA AI anything"
                  message="Pose an operational question and watch the agents reason toward a single arbitrated recommendation."
                />
                <div className="mt-6 space-y-2">
                  {SAMPLE_QUERIES.map((q) => (
                    <button
                      key={q}
                      onClick={() => submit(q)}
                      className="w-full rounded-xl border border-border bg-background px-4 py-3 text-left text-sm text-body transition-colors hover:border-violet-200 hover:bg-violet-50"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {lastQuery && (
              <div className="mb-4 flex justify-end">
                <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-violet px-4 py-2.5 text-sm text-white">
                  {lastQuery}
                </div>
              </div>
            )}

            {steps.length > 0 && (
              <div className="mb-4 space-y-2">
                <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wide text-muted">
                  <Cpu size={13} /> Agent pipeline
                </div>
                <AnimatePresence>
                  {steps.map((s, i) => (
                    <StepRow key={`${s.agent}-${i}`} step={s} />
                  ))}
                </AnimatePresence>
              </div>
            )}

            {error && (
              <div className="flex items-start gap-3 rounded-xl border border-rose-100 bg-rose-50 px-4 py-3">
                <AlertTriangle size={18} className="mt-0.5 text-rose-700" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-rose-700">
                    Query failed
                  </p>
                  <p className="mt-0.5 text-sm text-rose-700/80">{error}</p>
                </div>
                <button
                  onClick={() => submit(lastQuery)}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-rose-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-rose-600"
                >
                  <RotateCw size={13} /> Retry
                </button>
              </div>
            )}

            {synthesis && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl border border-violet-100 bg-violet-50/50 p-5"
              >
                <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wide text-violet-700">
                  <Sparkles size={13} /> Recommendation
                </div>
                <p className="mt-2 text-sm leading-relaxed text-body">
                  {typedRecommendation}
                  {!typingDone && (
                    <span className="ml-0.5 inline-block h-4 w-[2px] animate-pulse bg-violet-400 align-middle" />
                  )}
                </p>

                {typingDone && synthesis.financial_exposure_inr > 0 && (
                  <div className="mt-4 inline-flex items-center gap-2 rounded-xl bg-card px-3 py-2 shadow-sm">
                    <span className="text-xs text-muted">
                      Financial exposure
                    </span>
                    <span className="font-mono text-sm font-semibold text-rose-700">
                      {formatINR(synthesis.financial_exposure_inr)}
                    </span>
                  </div>
                )}

                {typingDone && synthesis.conflicts?.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-semibold text-rose-700">
                      Conflicts detected
                    </div>
                    {synthesis.conflicts.map((c, i) => (
                      <div
                        key={i}
                        className="rounded-xl border border-rose-100 bg-card p-3"
                      >
                        <p className="text-sm text-body">{c.description}</p>
                        {c.resolution && (
                          <p className="mt-1 text-xs text-muted">
                            <span className="font-medium text-teal-700">
                              Resolution:{" "}
                            </span>
                            {c.resolution}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {typingDone && synthesis.action_stubs?.length > 0 && (
                  <div className="mt-4">
                    <div className="text-xs font-semibold text-body">
                      Suggested actions
                    </div>
                    <ul className="mt-2 space-y-1.5">
                      {synthesis.action_stubs.map((a, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-sm text-body"
                        >
                          <CheckCircle2
                            size={15}
                            className="mt-0.5 shrink-0 text-teal-700"
                          />
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              submit(input);
            }}
            className="mt-4 flex items-center gap-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about equipment, permits, compliance…"
              className="flex-1 rounded-xl border border-border bg-card px-4 py-3 text-sm text-body outline-none transition-colors placeholder:text-muted focus:border-violet-300"
            />
            <button
              type="submit"
              disabled={isStreaming || !input.trim()}
              className="inline-flex items-center gap-2 rounded-xl bg-violet px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-violet-800 disabled:cursor-not-allowed disabled:bg-violet-200"
            >
              {isStreaming ? (
                <Loader2 size={17} className="animate-spin" />
              ) : (
                <Send size={17} />
              )}
              Ask
            </button>
          </form>
        </div>

        <aside className="lg:col-span-1">
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wide text-muted">
              <Quote size={13} /> Citations
            </div>
            {!showCitations ? (
              <p className="mt-3 text-sm text-muted">
                Sources cited by the agents will appear here once the answer is
                complete.
              </p>
            ) : (
              <ul className="mt-3 space-y-2">
                {citations.map((c, i) => (
                  <li
                    key={i}
                    className="rounded-xl border border-border bg-background px-3 py-2 font-mono text-xs text-body"
                  >
                    {c}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>
    </PageContainer>
  );
}
