import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { DEFAULT_TIME_ZONE_ID, TIME_ZONES, kickoffFormatter, zoneForId } from "@/lib/time";

const STORAGE_KEY = "worldcup.timezone";

type TimeZoneContextValue = {
  zoneId: string;
  zone: string | undefined;
  setZoneId: (id: string) => void;
};

const TimeZoneContext = createContext<TimeZoneContextValue | null>(null);

function initialZoneId(): string {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && TIME_ZONES.some((z) => z.id === saved)) return saved;
  } catch {
    /* localStorage unavailable (private mode etc.) — fall back to default */
  }
  return DEFAULT_TIME_ZONE_ID;
}

export function TimeZoneProvider({ children }: { children: ReactNode }) {
  const [zoneId, setZoneId] = useState<string>(initialZoneId);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, zoneId);
    } catch {
      /* ignore persistence failure */
    }
  }, [zoneId]);

  const value = useMemo(() => ({ zoneId, zone: zoneForId(zoneId), setZoneId }), [zoneId]);
  return <TimeZoneContext.Provider value={value}>{children}</TimeZoneContext.Provider>;
}

export function useTimeZone(): TimeZoneContextValue {
  const ctx = useContext(TimeZoneContext);
  if (!ctx) throw new Error("useTimeZone must be used within <TimeZoneProvider>");
  return ctx;
}

// Memoized kickoff formatter for the currently selected zone. Pass a STABLE
// options object (a module-level const) so the memo key stays stable per render.
export function useKickoffFormatter(options: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
  const { zone } = useTimeZone();
  return useMemo(() => kickoffFormatter(zone, options), [zone, options]);
}
