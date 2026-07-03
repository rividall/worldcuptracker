// All match kickoff times are displayed in Spain time (Europe/Madrid),
// regardless of where the viewer is. Times are stored as UTC in the DB
// (see CLAUDE.md); we pin the *display* zone here so everyone sees the same
// Spanish clock time. `timeZoneName: "short"` is included by callers so the
// zone (e.g. "GMT+2") is shown — otherwise a viewer abroad would misread a
// Spanish kickoff as their own local time.
export const MATCH_TIME_ZONE = "Europe/Madrid";

// Build a formatter in Spain's zone. Locale stays the viewer's default so
// month/weekday names follow the browser language; only the zone is pinned.
export function madridFormat(options: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
  return new Intl.DateTimeFormat(undefined, { ...options, timeZone: MATCH_TIME_ZONE });
}
