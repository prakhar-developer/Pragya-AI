import { useEffect, useRef, useState } from "react";

interface InfiniteGridProps {
  cellSize?: number;
  className?: string;
}

export function InfiniteGrid({
  cellSize = 48,
  className = "",
}: InfiniteGridProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: -1000, y: -1000 });
  const [active, setActive] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      setActive(true);
    };
    const onLeave = () => setActive(false);
    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  const baseLines =
    "linear-gradient(to right, rgba(109,40,217,0.04) 1px, transparent 1px)," +
    "linear-gradient(to bottom, rgba(109,40,217,0.04) 1px, transparent 1px)";
  const revealLines =
    "linear-gradient(to right, rgba(109,40,217,0.15) 1px, transparent 1px)," +
    "linear-gradient(to bottom, rgba(109,40,217,0.15) 1px, transparent 1px)";

  return (
    <div
      ref={ref}
      className={`pointer-events-auto absolute inset-0 overflow-hidden ${className}`}
      aria-hidden
    >
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: baseLines,
          backgroundSize: `${cellSize}px ${cellSize}px`,
        }}
      />
      <div
        className="absolute inset-0 transition-opacity duration-300"
        style={{
          backgroundImage: revealLines,
          backgroundSize: `${cellSize}px ${cellSize}px`,
          opacity: active ? 1 : 0,
          WebkitMaskImage: `radial-gradient(220px circle at ${pos.x}px ${pos.y}px, black 0%, transparent 70%)`,
          maskImage: `radial-gradient(220px circle at ${pos.x}px ${pos.y}px, black 0%, transparent 70%)`,
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background" />
    </div>
  );
}
