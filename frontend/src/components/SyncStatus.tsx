import { getLastSync } from "@/api/worldcup";
import { usePolling } from "@/hooks/usePolling";

function relativeTime(iso: string): string {
  const minutes = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  return `${hours} h ago`;
}

export default function SyncStatus() {
  const { data } = usePolling(getLastSync, 60_000);

  if (!data || !data.last_sync_at) return null;
  return (
    <span className="sync-status" title={data.detail ?? undefined}>
      {data.status === "error" ? "⚠ last sync failed · " : ""}
      Updated {relativeTime(data.last_sync_at)}
    </span>
  );
}
