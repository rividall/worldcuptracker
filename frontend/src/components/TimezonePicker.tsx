import { TIME_ZONES } from "@/lib/time";
import { useTimeZone } from "@/lib/timezone";

export default function TimezonePicker() {
  const { zoneId, setZoneId } = useTimeZone();
  return (
    <select
      className="tz-picker"
      value={zoneId}
      onChange={(e) => setZoneId(e.target.value)}
      aria-label="Display timezone"
    >
      {TIME_ZONES.map((z) => (
        <option key={z.id} value={z.id}>
          {z.label}
        </option>
      ))}
    </select>
  );
}
