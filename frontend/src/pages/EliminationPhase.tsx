import { useState } from "react";
import type { BracketMatch, Match } from "@/api/types";
import { isLive } from "@/api/types";
import { getBracket } from "@/api/worldcup";
import LiveBadge from "@/components/LiveBadge";
import RadialBracket from "@/components/RadialBracket";
import { useKickoffFormatter } from "@/lib/timezone";
import { usePolling } from "@/hooks/usePolling";

const POLL_MS = 15 * 60 * 1000;

const STAGE_LABELS: Record<string, string> = {
  LAST_32: "Round of 32",
  LAST_16: "Round of 16",
  QUARTER_FINALS: "Quarter-final",
  SEMI_FINALS: "Semi-final",
  THIRD_PLACE: "Third place",
  FINAL: "Final",
};

const KICKOFF_OPTS: Intl.DateTimeFormatOptions = {
  weekday: "short",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZoneName: "short",
};

function MatchDetail({ match, onClose }: { match: Match; onClose: () => void }) {
  const played = match.score.home !== null;
  const kickoffFormat = useKickoffFormatter(KICKOFF_OPTS);
  return (
    <div className="match-detail" role="dialog" aria-label="Match details">
      <header>
        <span className="stage-label">{STAGE_LABELS[match.stage] ?? match.stage}</span>
        {isLive(match) && <LiveBadge />}
        <button className="close-btn" onClick={onClose} aria-label="Close">
          ×
        </button>
      </header>
      <div className="detail-teams">
        <span className="detail-team">
          {match.home_team?.crest_url && <img src={match.home_team.crest_url} alt="" />}
          {match.home_team?.name ?? "TBD"}
        </span>
        <span className="detail-score">
          {played ? `${match.score.home}–${match.score.away}` : "vs"}
        </span>
        <span className="detail-team">
          {match.away_team?.crest_url && <img src={match.away_team.crest_url} alt="" />}
          {match.away_team?.name ?? "TBD"}
        </span>
      </div>
      {match.score.duration === "PENALTY_SHOOTOUT" && (
        <p className="detail-note">
          After penalties: {match.score.penalties_home}–{match.score.penalties_away}
        </p>
      )}
      {match.score.duration === "EXTRA_TIME" && <p className="detail-note">After extra time</p>}
      <p className="detail-kickoff">{kickoffFormat.format(new Date(match.utc_date))}</p>
    </div>
  );
}

export default function EliminationPhase() {
  const { data: bracket, error, loading } = usePolling(getBracket, POLL_MS);
  const [selected, setSelected] = useState<BracketMatch | Match | null>(null);

  if (loading) return <p className="state-msg">Loading bracket…</p>;
  if (error) return <p className="state-msg error">Couldn't load bracket: {error}</p>;
  if (!bracket || bracket.rounds.every((round) => round.matches.length === 0))
    return <p className="state-msg">No knockout data yet — first sync pending.</p>;

  return (
    <div className="elimination-phase">
      <RadialBracket bracket={bracket} onSelect={setSelected} />
      {bracket.third_place && (
        <button className="third-place" onClick={() => setSelected(bracket.third_place)}>
          <span className="stage-label">Third place</span>
          <span>
            {bracket.third_place.home_team?.tla ?? "TBD"}{" "}
            {bracket.third_place.score.home !== null
              ? `${bracket.third_place.score.home}–${bracket.third_place.score.away}`
              : "vs"}{" "}
            {bracket.third_place.away_team?.tla ?? "TBD"}
          </span>
        </button>
      )}
      {selected && <MatchDetail match={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
