import type { Group, Match } from "@/api/types";
import { isLive } from "@/api/types";
import LiveBadge from "@/components/LiveBadge";
import { useKickoffFormatter } from "@/lib/timezone";

const KICKOFF_OPTS: Intl.DateTimeFormatOptions = {
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZoneName: "short",
};

function MatchRow({ match, kickoffFormat }: { match: Match; kickoffFormat: Intl.DateTimeFormat }) {
  const played = match.score.home !== null;
  return (
    <li className={`match-row${isLive(match) ? " is-live" : ""}`}>
      <span className="match-team home">
        {match.home_team?.crest_url && (
          <img src={match.home_team.crest_url} alt="" className="crest-sm" />
        )}
        {match.home_team?.tla ?? "TBD"}
      </span>
      {played ? (
        <span className="match-score">
          {match.score.home}–{match.score.away}
          {match.score.duration === "PENALTY_SHOOTOUT" && (
            <small className="pens">
              {" "}
              ({match.score.penalties_home}–{match.score.penalties_away} p)
            </small>
          )}
        </span>
      ) : (
        <span className="match-time">{kickoffFormat.format(new Date(match.utc_date))}</span>
      )}
      <span className="match-team away">
        {match.away_team?.tla ?? "TBD"}
        {match.away_team?.crest_url && (
          <img src={match.away_team.crest_url} alt="" className="crest-sm" />
        )}
      </span>
      {isLive(match) && <LiveBadge />}
    </li>
  );
}

export default function GroupCard({ group }: { group: Group }) {
  const kickoffFormat = useKickoffFormatter(KICKOFF_OPTS);
  return (
    <article className="group-card" aria-label={`Group ${group.name}`}>
      <h2>Group {group.name}</h2>
      <table className="standings">
        <thead>
          <tr>
            <th className="pos">#</th>
            <th className="team">Team</th>
            <th>P</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>GD</th>
            <th className="pts">Pts</th>
          </tr>
        </thead>
        <tbody>
          {group.standings.map((row) => (
            <tr key={row.team.id} className={row.position <= 2 ? "qualified" : ""}>
              <td className="pos">{row.position}</td>
              <td className="team">
                {row.team.crest_url && <img src={row.team.crest_url} alt="" className="crest-sm" />}
                <span className="team-name">{row.team.name}</span>
              </td>
              <td>{row.played}</td>
              <td>{row.won}</td>
              <td>{row.drawn}</td>
              <td>{row.lost}</td>
              <td>{row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}</td>
              <td className="pts">{row.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ul className="match-list">
        {group.matches.map((match) => (
          <MatchRow key={match.id} match={match} kickoffFormat={kickoffFormat} />
        ))}
      </ul>
    </article>
  );
}
