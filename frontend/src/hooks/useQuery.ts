import { useCallback, useRef, useState } from "react";
import { streamQuery } from "../services/streaming";
import type { SynthesisResult } from "../services/types";

export interface AgentStep {
  agent: string;
  status: "running" | "done";
  output?: Record<string, unknown>;
}

export interface QueryState {
  steps: AgentStep[];
  synthesis: SynthesisResult | null;
  isStreaming: boolean;
  error: string | null;
}

const INITIAL: QueryState = {
  steps: [],
  synthesis: null,
  isStreaming: false,
  error: null,
};

export function usePragyaQuery() {
  const [state, setState] = useState<QueryState>(INITIAL);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(INITIAL);
  }, []);

  const run = useCallback((query: string, sessionId: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ steps: [], synthesis: null, isStreaming: true, error: null });

    streamQuery(
      query,
      sessionId,
      {
        onNodeStart: (agent) =>
          setState((s) => ({
            ...s,
            steps: [...s.steps, { agent, status: "running" }],
          })),
        onNodeEnd: (agent, output) =>
          setState((s) => ({
            ...s,
            steps: s.steps.map((st) =>
              st.agent === agent && st.status === "running"
                ? { ...st, status: "done", output }
                : st
            ),
          })),
        onSynthesis: (synthesis) =>
          setState((s) => ({ ...s, synthesis })),
        onDone: () => setState((s) => ({ ...s, isStreaming: false })),
        onError: (error) =>
          setState((s) => ({ ...s, isStreaming: false, error })),
      },
      controller.signal
    );
  }, []);

  return { ...state, run, reset };
}
