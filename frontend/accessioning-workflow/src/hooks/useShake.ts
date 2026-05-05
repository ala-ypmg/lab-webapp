import { useState, useEffect } from 'react';

/**
 * Returns 'shake-error' whenever active is true, re-triggering the animation
 * each time `version` changes (even if active was already true).
 */
export function useShake(active: boolean, version: number): string {
  const [shaking, setShaking] = useState(false);

  useEffect(() => {
    if (!active) {
      setShaking(false);
      return;
    }
    // Drop the class first so the animation restarts cleanly on re-trigger.
    setShaking(false);
    const outer = requestAnimationFrame(() => {
      const inner = requestAnimationFrame(() => setShaking(true));
      return () => cancelAnimationFrame(inner);
    });
    return () => cancelAnimationFrame(outer);
  }, [active, version]);

  // Remove class after the animation duration so it can fire again next time.
  useEffect(() => {
    if (!shaking) return;
    const timer = setTimeout(() => setShaking(false), 400);
    return () => clearTimeout(timer);
  }, [shaking]);

  return shaking ? 'shake-error' : '';
}
