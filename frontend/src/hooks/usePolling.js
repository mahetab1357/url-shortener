import { useEffect, useRef, useState } from "react";

/**
 * Polls `fetchFn` every `intervalMs` and exposes the latest result.
 *
 * Polling vs WebSockets: a WebSocket connection would need server-side
 * connection-lifecycle management and (if this service ever ran more than
 * one instance) a pub/sub layer to fan a click-out to all connected
 * dashboards. For a counter that updates a few times a minute, that's a
 * lot of infrastructure for a property that's fine being a few seconds
 * stale - so plain polling.
 */
export function usePolling(fetchFn, { intervalMs = 5000, enabled = true } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const fetchFnRef = useRef(fetchFn);
  fetchFnRef.current = fetchFn;

  useEffect(() => {
    if (!enabled) {
      return;
    }
    let cancelled = false;

    async function tick() {
      try {
        const result = await fetchFnRef.current();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      }
    }

    tick();
    const id = setInterval(tick, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [intervalMs, enabled]);

  return { data, error };
}
