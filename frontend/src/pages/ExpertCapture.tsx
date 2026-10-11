import { useState } from "react";
import toast from "react-hot-toast";
import { motion } from "framer-motion";
import {
  UserRoundPen,
  Loader2,
  Send,
  Tags,
  MessageSquareQuote,
} from "lucide-react";
import {
  useExpertContributions,
  useSubmitContribution,
} from "../hooks/useExpert";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { CardSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { Button } from "../components/ui/Button";
import { formatDate } from "../lib/utils";

const EMPTY = {
  contributor_name: "",
  contributor_role: "",
  years_experience: 0,
  text: "",
};

export function ExpertCapture() {
  const [form, setForm] = useState(EMPTY);
  const submit = useSubmitContribution();
  const { data, isLoading, isError, refetch } = useExpertContributions();

  const canSubmit =
    form.contributor_name.trim() &&
    form.contributor_role.trim() &&
    form.text.trim().length > 10;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || submit.isPending) return;
    submit.mutate(form, {
      onSuccess: (res) => {
        toast.success(
          `Captured · ${res.entities_found.length} entities linked`
        );
        setForm(EMPTY);
      },
      onError: () => toast.error("Could not save contribution"),
    });
  };

  return (
    <PageContainer>
      <PageHeader
        title="Expert Capture"
        subtitle="Turn tacit operator knowledge into structured, searchable graph entities."
      />

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-5">
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-border bg-card p-5 shadow-sm lg:col-span-2"
        >
          <div className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-50 text-violet-700">
              <UserRoundPen size={17} />
            </span>
            <h2 className="text-sm font-semibold text-body">
              New contribution
            </h2>
          </div>

          <div className="mt-4 space-y-3">
            <div>
              <label className="text-xs font-medium text-muted">Name</label>
              <input
                value={form.contributor_name}
                onChange={(e) =>
                  setForm({ ...form, contributor_name: e.target.value })
                }
                className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-2 text-sm text-body outline-none focus:border-violet-300"
                placeholder="R. Sharma"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-muted">Role</label>
                <input
                  value={form.contributor_role}
                  onChange={(e) =>
                    setForm({ ...form, contributor_role: e.target.value })
                  }
                  className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-2 text-sm text-body outline-none focus:border-violet-300"
                  placeholder="Rotating equipment lead"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted">
                  Experience (yrs)
                </label>
                <input
                  type="number"
                  min={0}
                  value={form.years_experience || ""}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      years_experience: Number(e.target.value) || 0,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-2 font-mono text-sm text-body outline-none focus:border-violet-300"
                  placeholder="12"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-muted">
                Knowledge
              </label>
              <textarea
                value={form.text}
                onChange={(e) => setForm({ ...form, text: e.target.value })}
                rows={6}
                className="mt-1 w-full resize-none rounded-xl border border-border bg-background px-3 py-2 text-sm text-body outline-none focus:border-violet-300"
                placeholder="Describe the failure mode, workaround, or operational insight — reference equipment tags and procedures where possible."
              />
            </div>

            <Button
              type="submit"
              disabled={!canSubmit || submit.isPending}
              className="w-full"
            >
              {submit.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
              Capture knowledge
            </Button>
          </div>
        </form>

        <div className="lg:col-span-3">
          <h2 className="mb-3 text-sm font-semibold text-body">
            Recent contributions
          </h2>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : isError ? (
            <ErrorState
              message="Failed to load contributions."
              onRetry={() => refetch()}
            />
          ) : !data || data.length === 0 ? (
            <EmptyState
              icon={MessageSquareQuote}
              title="No contributions yet"
              message="Capture the first piece of expert knowledge using the form."
            />
          ) : (
            <div className="space-y-4">
              {data.map((c, i) => (
                <motion.div
                  key={c.id ?? i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl border border-border bg-card p-5 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-semibold text-body">
                        {c.contributor_name}
                      </span>
                      <span className="ml-2 text-xs text-muted">
                        {c.contributor_role} · {c.years_experience} yrs
                      </span>
                    </div>
                    {c.created_at && (
                      <span className="text-xs text-muted">
                        {formatDate(c.created_at)}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm leading-relaxed text-body">
                    {c.text}
                  </p>
                  {c.entities_found?.length > 0 && (
                    <div className="mt-3 flex flex-wrap items-center gap-1.5">
                      <Tags size={14} className="text-muted" />
                      {c.entities_found.map((t) => (
                        <span
                          key={t}
                          className="rounded-lg bg-violet-50 px-2 py-0.5 font-mono text-[11px] text-violet-700"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
