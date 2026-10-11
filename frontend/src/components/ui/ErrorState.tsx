import { AlertCircle, RotateCw } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "Something went wrong while loading data.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-rose-100 bg-rose-50 px-6 py-14 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-rose-700">
        <AlertCircle size={26} />
      </span>
      <h3 className="mt-4 text-base font-semibold text-rose-700">
        Unable to load
      </h3>
      <p className="mt-1 max-w-sm text-sm text-rose-700/80">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-5 inline-flex items-center gap-2 rounded-xl bg-rose-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-rose-600"
        >
          <RotateCw size={15} />
          Retry
        </button>
      )}
    </div>
  );
}
