-- PRAGYA AI - Supabase schema
-- Run in the Supabase SQL editor. Enables pgvector, creates all tables,
-- an HNSW index on chunk embeddings, and the match_document_chunks RPC.

create extension if not exists vector;

create table if not exists documents (
    id uuid primary key,
    filename text not null,
    document_type text default '',
    summary text default '',
    created_at timestamptz not null default now()
);

create table if not exists document_chunks (
    id bigint generated always as identity primary key,
    content text not null,
    embedding vector(384),
    chunk_index integer not null default 0,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists conflicts (
    id uuid primary key default gen_random_uuid(),
    conflict_code text,
    description text not null,
    equipment_tag text,
    recommended_action text,
    responsible_role text default 'shift_supervisor',
    deadline text,
    regulatory_reference text,
    financial_exposure_inr numeric default 0,
    severity numeric not null default 0,
    status text not null default 'open',
    detected_at timestamptz not null default now(),
    resolved_at timestamptz
);

create table if not exists work_orders (
    id uuid primary key default gen_random_uuid(),
    work_order_id text unique not null,
    equipment_tag text,
    line text,
    task text,
    scheduled_start timestamptz,
    status text default 'planned',
    created_at timestamptz not null default now()
);

create table if not exists permits (
    id uuid primary key default gen_random_uuid(),
    permit_id text unique not null,
    permit_type text,
    line text,
    valid_from timestamptz,
    valid_to timestamptz,
    status text default 'active',
    created_at timestamptz not null default now()
);

create table if not exists chat_sessions (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now()
);

create table if not exists chat_messages (
    id bigint generated always as identity primary key,
    session_id text not null,
    role text not null,
    content text not null,
    created_at timestamptz not null default now()
);

create table if not exists expert_contributions (
    id uuid primary key default gen_random_uuid(),
    contributor_name text not null,
    contributor_role text,
    years_experience integer default 0,
    text text not null,
    entities_found jsonb default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists benchmark_results (
    id bigint generated always as identity primary key,
    query_id text unique not null,
    question text not null,
    ground_truth text,
    category text,
    answer text,
    latency_seconds numeric,
    ran_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists document_chunks_embedding_hnsw
    on document_chunks
    using hnsw (embedding vector_cosine_ops);

create index if not exists conflicts_severity_detected_idx
    on conflicts (severity desc, detected_at desc);

create or replace function match_document_chunks(
    query_embedding vector(384),
    match_count int default 8,
    filter jsonb default '{}'::jsonb
)
returns table (
    id bigint,
    content text,
    chunk_index integer,
    metadata jsonb,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        dc.id,
        dc.content,
        dc.chunk_index,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) as similarity
    from document_chunks dc
    where dc.metadata @> filter
    order by dc.embedding <=> query_embedding
    limit match_count;
end;
$$;
