import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Fetch on mount, then re-fetch every `interval` ms while the tab is visible.
 * Also re-fetches immediately when the tab becomes visible again.
 *
 * `interval` may be a number, or a function of the latest data — e.g. return a
 * short interval when a match is live and a long one otherwise. When the derived
 * interval changes, the timer resets to the new cadence.
 */
export function usePolling<T>(
  fetcher: () => Promise<T>,
  interval: number | ((data: T | null) => number),
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const intervalMs = typeof interval === "function" ? interval(data) : interval;

  const refresh = useCallback(async () => {
    try {
      const result = await fetcherRef.current();
      setData(result);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(() => {
      if (document.visibilityState === "visible") refresh();
    }, intervalMs);
    const onVisible = () => {
      if (document.visibilityState === "visible") refresh();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [refresh, intervalMs]);

  return { data, error, loading, refresh };
}
