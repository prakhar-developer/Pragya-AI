import { API_BASE } from "./api";
import type { SynthesisResult } from "./types";

export type StreamEventType =
  | "node_start"
  | "node_end"
  | "synthesis"
  | "done"
  | "error";

export interface StreamCallbacks {
  onNodeStart?: (agent: string) => void;
  onNodeEnd?: (agent: string, output: Record<string, unknown>) => void;
  onSynthesis?: (synthesis: SynthesisResult) => void;
  onDone?: () => void;
  onError?: (message: string) => void;
}

export async function streamQuery(
  query: string,
  sessionId: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/v1/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: sessionId }),
      signal,
    });
  } catch (err) {
    if ((err as Error).name === "AbortError") return;
    callbacks.onError?.((err as Error).message);
    return;
  }

  if (!response.ok || !response.body) {
    callbacks.onError?.(`Request failed (${response.status})`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const dispatch = (type: string, data: Record<string, unknown>) => {
    switch (type) {
      case "node_start":
        callbacks.onNodeStart?.(String(data.agent ?? ""));
        break;
      case "node_end":
        callbacks.onNodeEnd?.(
          String(data.agent ?? ""),
          (data.output as Record<string, unknown>) ?? {}
        );
        break;
      case "synthesis":
        callbacks.onSynthesis?.(data as unknown as SynthesisResult);
        break;
      case "done":
        callbacks.onDone?.();
        break;
      case "error":
        callbacks.onError?.(String(data.message ?? "Stream error"));
        break;
    }
  };

  const handleBlock = (block: string) => {
    let eventType = "message";
    const dataLines: string[] = [];
    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) eventType = line.slice(6).trim();
      else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
    }
    if (!dataLines.length) return;
    const raw = dataLines.join("\n");
    let parsed: Record<string, unknown> = {};
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = { message: raw };
    }
    dispatch(eventType, parsed);
  };

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let sep: number;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const block = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        if (block.trim()) handleBlock(block);
      }
    }
    if (buffer.trim()) handleBlock(buffer);
  } catch (err) {
    if ((err as Error).name !== "AbortError") {
      callbacks.onError?.((err as Error).message);
    }
  }
}
