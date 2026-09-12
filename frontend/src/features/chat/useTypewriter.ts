import { useEffect, useState } from "react";

const CHARS_PER_TICK = 4;
const TICK_MS = 12;

/** Backend returns the full mock answer in one shot (no real streaming LLM
 * yet - see app/core/llm.py) - this simulates a streaming feel on the
 * frontend by revealing it progressively. `active` gates it so only the
 * newest message animates; older ones render their full text immediately. */
export function useTypewriter(text: string, active: boolean): string {
  const [revealed, setRevealed] = useState(active ? "" : text);

  useEffect(() => {
    if (!active) {
      setRevealed(text);
      return;
    }

    setRevealed("");
    let position = 0;
    const interval = setInterval(() => {
      position += CHARS_PER_TICK;
      setRevealed(text.slice(0, position));
      if (position >= text.length) clearInterval(interval);
    }, TICK_MS);

    return () => clearInterval(interval);
  }, [text, active]);

  return revealed;
}
