// Kickoff times are stored as UTC in the DB and rendered in a zone the viewer
// picks (header timezone picker, persisted in localStorage). This module is the
// single source of truth for the available zones and how a kickoff formatter is
// built. Changing the zone only affects display, never storage.

export type TimeZoneChoice = {
  id: string; // persisted value
  label: string; // shown in the picker
  zone: string | undefined; // IANA zone; undefined = the viewer's own device zone
};

// Default is Spain (tournament reference zone); Chile added per request.
export const TIME_ZONES: TimeZoneChoice[] = [
  { id: "spain", label: "Spain", zone: "Europe/Madrid" },
  { id: "chile", label: "Chile", zone: "America/Santiago" },
  { id: "local", label: "My timezone", zone: undefined },
];

export const DEFAULT_TIME_ZONE_ID = "spain";

export function zoneForId(id: string): string | undefined {
  return (TIME_ZONES.find((z) => z.id === id) ?? TIME_ZONES[0]).zone;
}

// Build a kickoff formatter in the given zone. Locale stays the viewer's default
// so month/weekday names follow the browser language; pass `timeZoneName` in
// options so the zone (e.g. GMT+2) is shown — important now that the displayed
// time may not match the viewer's own clock.
export function kickoffFormatter(
  zone: string | undefined,
  options: Intl.DateTimeFormatOptions,
): Intl.DateTimeFormat {
  return new Intl.DateTimeFormat(undefined, { ...options, timeZone: zone });
}
