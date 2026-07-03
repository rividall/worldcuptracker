import { TIME_ZONES } from "@/lib/time";
import { useTimeZone } from "@/lib/timezone";

export default function TimezonePicker() {
  const { zoneId, setZoneId } = useTimeZone();
  return (
    <label className="tz-picker">
      <span className="tz-picker-label">Timezone</span>
      <select
        className="tz-picker-select"
        value={zoneId}
        onChange={(e) => setZoneId(e.target.value)}
      >
        {TIME_ZONES.map((z) => (
          <option key={z.id} value={z.id}>
            {z.label}
          </option>
        ))}
      </select>
    </label>
  );
}
