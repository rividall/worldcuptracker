export default function Stat({
  label,
  value,
  strong,
}: {
  label: string;
  value: string | number;
  strong?: boolean;
}) {
  return (
    <div className="stat">
      <span className={`stat-value${strong ? " strong" : ""}`}>{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}
