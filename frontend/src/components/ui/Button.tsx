import { cn } from "../../lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-violet text-white hover:bg-violet-800 disabled:bg-violet-200",
  secondary:
    "bg-teal text-white hover:bg-teal-600 disabled:bg-teal-100 disabled:text-teal-700",
  ghost:
    "bg-transparent text-body hover:bg-background border border-border",
  danger: "bg-rose-700 text-white hover:bg-rose-600 disabled:bg-rose-100",
};

export function Button({
  variant = "primary",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-colors disabled:cursor-not-allowed",
        VARIANTS[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
