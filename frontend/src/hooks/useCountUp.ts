import { useEffect, useRef, useState } from "react";

export function useCountUp(target: number, duration = 1400, start = true) {
  const [value, setValue] = useState(0);
  const frame = useRef<number>(0);

  useEffect(() => {
    if (!start) return;
    let startTime: number | null = null;
    const tick = (t: number) => {
      if (startTime === null) startTime = t;
      const progress = Math.min((t - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(target * eased);
      if (progress < 1) frame.current = requestAnimationFrame(tick);
    };
    frame.current = requestAnimationFrame(tick);
    return () => {
      if (frame.current) cancelAnimationFrame(frame.current);
    };
  }, [target, duration, start]);

  return value;
}
