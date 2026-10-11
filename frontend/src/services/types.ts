export type DocumentType =
  | "regulation"
  | "work_order"
  | "permit"
  | "procedure"
  | "expert_tacit"
  | string;

export interface DocumentRecord {
  id: string;
  filename: string;
  document_type: DocumentType;
  summary: string;
  created_at: string | null;
}

export interface ExtractedEntities {
  equipment_tags: string[];
  permit_ids: string[];
  dates: string[];
  procedure_refs: string[];
  regulation_clauses: string[];
  personnel: string[];
  state_transitions: Array<{
    tag: string;
    from_state: string;
    to_state: string;
    timestamp: string;
  }>;
  document_type: string;
  summary: string;
}

export interface UploadResponse {
  doc_id: string;
  filename: string;
  chunk_count: number;
  entities: ExtractedEntities;
}

export interface BatchUploadItem {
  filename: string;
  status: "success" | "failed";
  doc_id?: string | null;
  chunk_count: number;
  reason?: string | null;
}

export interface BatchUploadResponse {
  total_files: number;
  succeeded: number;
  failed: number;
  total_chunks: number;
  results: BatchUploadItem[];
}

export interface Conflict {
  id: string;
  conflict_code?: string;
  description: string;
  equipment_tag?: string;
  recommended_action?: string;
  responsible_role?: string;
  deadline?: string;
  regulatory_reference?: string;
  financial_exposure_inr?: number;
  severity: number;
  status: string;
  detected_at?: string;
  resolved_at?: string | null;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string | null;
  criticality: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface GraphExport {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface StateHistoryEntry {
  recorded_at?: string;
  timestamp?: string;
  state?: string;
  [key: string]: unknown;
}

export interface NodeDetail {
  tag: string;
  type: string | null;
  criticality: string;
  state_history: StateHistoryEntry[];
  neighbours: Array<{ rel: string; entity: Record<string, unknown> }>;
}

export interface ExpertContribution {
  id?: string;
  contributor_name: string;
  contributor_role: string;
  years_experience: number;
  text: string;
  entities_found: string[];
  verification_status?: string;
  created_at?: string;
}

export interface ExpertContributionInput {
  contributor_name: string;
  contributor_role: string;
  years_experience: number;
  text: string;
}

export interface ExpertContributeResponse {
  contribution: ExpertContribution;
  entities_found: string[];
}

export interface BenchmarkResult {
  id?: number;
  query_id: string;
  question: string;
  ground_truth?: string;
  category?: string;
  answer?: string;
  latency_seconds?: number;
  ran_at?: string;
}

export interface SynthesisResult {
  primary_recommendation: string;
  conflicts: Array<{
    agents_involved?: string[];
    description?: string;
    resolution?: string;
  }>;
  financial_exposure_inr: number;
  action_stubs: string[];
  severity?: number;
  urgency?: number;
  confidence?: number;
  composite_score?: number;
}

export interface SystemStatusResponse {
  status: string;
  app_name: string;
  mode: string;
  timestamp: string;
  services: {
    knowledge_graph: {
      name: string;
      connected: boolean;
      node_count: number;
    };
    vector_store: {
      name: string;
      connected: boolean;
      document_count: number;
      conflict_count: number;
    };
    reasoning_llm: {
      name: string;
      connected: boolean;
      model: string;
    };
    agents: Array<{
      name: string;
      status: string;
    }>;
  };
}
