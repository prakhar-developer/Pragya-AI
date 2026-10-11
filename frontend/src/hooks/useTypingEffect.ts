import { useEffect, useRef, useState } from "react";

/** Reveals `text` progressively for a typing effect. Returns the visible slice and
 *  whether typing has finished. Re-runs whenever the source text changes. */
export function useTypingEffect(text: string, charsPerTick = 3, tickMs = 16) {
  const [visible, setVisible] = useState("");
  const [done, setDone] = useState(false);
  const timerRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    if (!text) {
      setVisible("");
      setDone(false);
      return;
    }
    setVisible("");
    setDone(false);
    let index = 0;
    const step = () => {
      index = Math.min(index + charsPerTick, text.length);
      setVisible(text.slice(0, index));
      if (index >= text.length) {
        setDone(true);
        return;
      }
      timerRef.current = window.setTimeout(step, tickMs);
    };
    timerRef.current = window.setTimeout(step, tickMs);
    return () => window.clearTimeout(timerRef.current);
  }, [text, charsPerTick, tickMs]);

  return { visible, done };
}
