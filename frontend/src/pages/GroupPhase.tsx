import { useEffect, useRef, useState } from "react";
import { anyLive, IDLE_POLL_MS, LIVE_POLL_MS } from "@/api/types";
import { getGroups } from "@/api/worldcup";
import GroupCard from "@/components/GroupCard";
import { usePolling } from "@/hooks/usePolling";

export default function GroupPhase() {
  const { data: groups, error, loading } = usePolling(getGroups, (data) =>
    data?.some((g) => anyLive(g.matches)) ? LIVE_POLL_MS : IDLE_POLL_MS,
  );
  const [active, setActive] = useState(0);
  const trackRef = useRef<HTMLDivElement>(null);

  const scrollTo = (index: number) => {
    const track = trackRef.current;
    if (!track || !groups) return;
    const clamped = Math.max(0, Math.min(groups.length - 1, index));
    track.scrollTo({ left: clamped * track.clientWidth, behavior: "smooth" });
  };

  // Track which card is snapped.
  const onScroll = () => {
    const track = trackRef.current;
    if (!track) return;
    setActive(Math.round(track.scrollLeft / track.clientWidth));
  };

  // Arrow keys on desktop.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowLeft") scrollTo(active - 1);
      if (event.key === "ArrowRight") scrollTo(active + 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (loading) return <p className="state-msg">Loading groups…</p>;
  if (error) return <p className="state-msg error">Couldn't load groups: {error}</p>;
  if (!groups || groups.length === 0)
    return <p className="state-msg">No group data yet — first sync pending.</p>;

  return (
    <div className="group-phase">
      <div className="carousel" ref={trackRef} onScroll={onScroll}>
        {groups.map((group) => (
          <div className="carousel-item" key={group.name}>
            <GroupCard group={group} />
          </div>
        ))}
      </div>
      <div className="carousel-nav">
        <button
          className="nav-btn"
          onClick={() => scrollTo(active - 1)}
          disabled={active === 0}
          aria-label="Previous group"
        >
          ‹
        </button>
        <div className="dots" role="tablist" aria-label="Groups">
          {groups.map((group, index) => (
            <button
              key={group.name}
              className={`dot${index === active ? " active" : ""}`}
              onClick={() => scrollTo(index)}
              aria-label={`Group ${group.name}`}
            >
              {group.name}
            </button>
          ))}
        </div>
        <button
          className="nav-btn"
          onClick={() => scrollTo(active + 1)}
          disabled={active === groups.length - 1}
          aria-label="Next group"
        >
          ›
        </button>
      </div>
    </div>
  );
}
