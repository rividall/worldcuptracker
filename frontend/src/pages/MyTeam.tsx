import { useEffect, useMemo, useState } from "react";
import type { Match, TeamDetail, TeamListItem } from "@/api/types";
import { anyLive, FINISHED_STATUS, IDLE_POLL_MS, isLive, LIVE_POLL_MS } from "@/api/types";
import { getTeam, getTeams } from "@/api/worldcup";
import LiveBadge from "@/components/LiveBadge";
import Stat from "@/components/Stat";
import { useKickoffFormatter } from "@/lib/timezone";
import { usePolling } from "@/hooks/usePolling";

const STORAGE_KEY = "worldcup.myteam";

const STAGE_LABELS: Record<string, string> = {
  GROUP_STAGE: "Group",
  LAST_32: "Round of 32",
  LAST_16: "Round of 16",
  QUARTER_FINALS: "Quarter-final",
  SEMI_FINALS: "Semi-final",
  THIRD_PLACE: "Third place",
  FINAL: "Final",
};

// The round a team advances to after winning at each stage — used to show the
// next round even before the feed assigns the team to that match.
const NEXT_STAGE: Record<string, string> = {
  GROUP_STAGE: "LAST_32",
  LAST_32: "LAST_16",
  LAST_16: "QUARTER_FINALS",
  QUARTER_FINALS: "SEMI_FINALS",
  SEMI_FINALS: "FINAL",
};

const KICKOFF_OPTS: Intl.DateTimeFormatOptions = {
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZoneName: "short",
};

type Result = "W" | "D" | "L";

function resultFor(match: Match, teamId: number): Result | null {
  if (match.status !== FINISHED_STATUS) return null;
  if (match.winner_team_id == null) return "D"; // group-stage draw
  return match.winner_team_id === teamId ? "W" : "L";
}

function goalsFor(match: Match, teamId: number): { for: number; against: number } | null {
  if (match.score.home == null || match.score.away == null) return null;
  const home = match.home_team?.id === teamId;
  return home
    ? { for: match.score.home, against: match.score.away }
    : { for: match.score.away, against: match.score.home };
}

function opponent(match: Match, teamId: number) {
  return match.home_team?.id === teamId ? match.away_team : match.home_team;
}

function summarize(matches: Match[], teamId: number) {
  let played = 0,
    won = 0,
    drawn = 0,
    lost = 0,
    gf = 0,
    ga = 0,
    clean = 0;
  for (const m of matches) {
    const r = resultFor(m, teamId);
    if (!r) continue;
    played++;
    if (r === "W") won++;
    else if (r === "D") drawn++;
    else lost++;
    const g = goalsFor(m, teamId);
    if (g) {
      gf += g.for;
      ga += g.against;
      if (g.against === 0) clean++;
    }
  }
  return { played, won, drawn, lost, gf, ga, gd: gf - ga, clean };
}

function teamStatus(detail: TeamDetail): { label: string; tone: string } {
  const id = detail.team.id;
  const finished = detail.matches.filter((m) => m.status === FINISHED_STATUS);
  const upcoming = detail.matches.filter((m) => m.status !== FINISHED_STATUS);

  const final = finished.find((m) => m.stage === "FINAL");
  if (final && final.winner_team_id === id) return { label: "🏆 Champions", tone: "champ" };

  // Still in it → show the round of their next match (green).
  if (upcoming.length) {
    const next = upcoming[0]; // earliest upcoming; detail.matches is chronological
    return { label: STAGE_LABELS[next.stage] ?? next.stage, tone: "in" };
  }

  const last = finished[finished.length - 1];
  if (last) {
    if (last.stage !== "GROUP_STAGE") {
      // Knockout: a LOSS eliminates them. A win means they advanced — the next
      // match just isn't assigned in the data yet (the slot is still TBD), so
      // show the round they're headed to.
      if (resultFor(last, id) === "L") return { label: `Out · ${STAGE_LABELS[last.stage]}`, tone: "out" };
      const next = NEXT_STAGE[last.stage];
      return { label: next ? STAGE_LABELS[next] : "🏆 Champions", tone: "in" };
    }
    if (detail.standing && detail.standing.position <= 2)
      return { label: STAGE_LABELS[NEXT_STAGE.GROUP_STAGE], tone: "in" };
    return { label: "Out · Group stage", tone: "out" };
  }
  return { label: "Group stage", tone: "neutral" };
}

function TeamMatchRow({
  match,
  teamId,
  kickoffFormat,
}: {
  match: Match;
  teamId: number;
  kickoffFormat: Intl.DateTimeFormat;
}) {
  const opp = opponent(match, teamId);
  const g = goalsFor(match, teamId);
  const r = resultFor(match, teamId);
  const home = match.home_team?.id === teamId;
  const shootout = match.score.duration === "PENALTY_SHOOTOUT";
  return (
    <li className={`tmatch${isLive(match) ? " is-live" : ""}`}>
      <span className="tmatch-stage">{STAGE_LABELS[match.stage] ?? match.stage}</span>
      <span className="tmatch-opp">
        <span className="tmatch-ha">{home ? "vs" : "@"}</span>
        {opp?.crest_url && <img src={opp.crest_url} alt="" className="crest-sm" />}
        {opp?.name ?? "TBD"}
      </span>
      {g ? (
        <span className="tmatch-score">
          {g.for}–{g.against}
          {shootout && (
            <small className="pens">
              {" "}
              ({match.score.penalties_home}–{match.score.penalties_away}p)
            </small>
          )}
        </span>
      ) : (
        <span className="tmatch-time">{kickoffFormat.format(new Date(match.utc_date))}</span>
      )}
      {r && <span className={`result-chip ${r.toLowerCase()}`}>{r}</span>}
      {isLive(match) && <LiveBadge />}
    </li>
  );
}

function TeamDetailView({ detail }: { detail: TeamDetail }) {
  const kickoffFormat = useKickoffFormatter(KICKOFF_OPTS);
  const id = detail.team.id;
  const status = teamStatus(detail);
  const stats = summarize(detail.matches, id);
  const form = detail.matches
    .filter((m) => m.status === FINISHED_STATUS)
    .slice(-5)
    .map((m) => resultFor(m, id)!);
  const next = detail.matches.find((m) => m.status !== FINISHED_STATUS);

  return (
    <div className="team-detail">
      <header className="team-header">
        {detail.team.crest_url && <img src={detail.team.crest_url} alt="" className="team-crest" />}
        <div className="team-id">
          <h2>{detail.team.name}</h2>
          <div className="team-meta">
            {detail.group_name && <span>Group {detail.group_name}</span>}
            <span className={`team-status ${status.tone}`}>{status.label}</span>
          </div>
        </div>
      </header>

      {next && (
        <p className="next-match">
          Next: {opponent(next, id)?.name ?? "TBD"} · {STAGE_LABELS[next.stage] ?? next.stage} ·{" "}
          {kickoffFormat.format(new Date(next.utc_date))}
        </p>
      )}

      <div className="stat-grid">
        {detail.standing && <Stat label="Points" value={detail.standing.points} strong />}
        <Stat label="Played" value={stats.played} />
        <Stat label="W-D-L" value={`${stats.won}-${stats.drawn}-${stats.lost}`} />
        <Stat label="GF" value={stats.gf} />
        <Stat label="GA" value={stats.ga} />
        <Stat label="GD" value={stats.gd > 0 ? `+${stats.gd}` : stats.gd} />
        <Stat label="Clean sheets" value={stats.clean} />
      </div>

      {form.length > 0 && (
        <div className="form-row" aria-label="Recent form">
          <span className="section-label">Form</span>
          {form.map((r, i) => (
            <span key={i} className={`form-pill ${r.toLowerCase()}`}>
              {r}
            </span>
          ))}
        </div>
      )}

      <section>
        <h3 className="section-label">Matches</h3>
        <ul className="team-matches">
          {/* Latest first. Derived stats/form/status above still use the
              chronological `detail.matches`; only the display order flips. */}
          {[...detail.matches].reverse().map((m) => (
            <TeamMatchRow key={m.id} match={m} teamId={id} kickoffFormat={kickoffFormat} />
          ))}
        </ul>
      </section>

      <section>
        <h3 className="section-label">Scorers & assists</h3>
        {detail.scorers.length === 0 ? (
          <p className="muted-note">No goals recorded for this team yet.</p>
        ) : (
          <table className="scorer-table">
            <thead>
              <tr>
                <th className="s-name">Player</th>
                <th>G</th>
                <th>A</th>
                <th>Pens</th>
                <th>MP</th>
              </tr>
            </thead>
            <tbody>
              {detail.scorers.map((s) => (
                <tr key={s.player_id}>
                  <td className="s-name">{s.player_name}</td>
                  <td className="s-goals">{s.goals}</td>
                  <td>{s.assists ?? "–"}</td>
                  <td>{s.penalties ?? "–"}</td>
                  <td>{s.played_matches ?? "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <p className="muted-note">Tournament totals · assists are provided where available.</p>
      </section>
    </div>
  );
}

// Group the picker options by group letter (A–L), then teams alphabetically.
function groupedTeams(teams: TeamListItem[]): [string, TeamListItem[]][] {
  const byGroup = new Map<string, TeamListItem[]>();
  for (const t of teams) {
    const key = t.group_name ?? "Other";
    (byGroup.get(key) ?? byGroup.set(key, []).get(key)!).push(t);
  }
  return [...byGroup.entries()].sort(([a], [b]) => a.localeCompare(b));
}

export default function MyTeam() {
  const { data: teams } = usePolling(getTeams, IDLE_POLL_MS);
  const [teamId, setTeamId] = useState<number | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? Number(saved) : null;
    } catch {
      return null;
    }
  });

  const [detail, setDetail] = useState<TeamDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState(false);

  useEffect(() => {
    if (teamId == null) return;
    try {
      localStorage.setItem(STORAGE_KEY, String(teamId));
    } catch {
      /* ignore */
    }
  }, [teamId]);

  useEffect(() => {
    if (teamId == null) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    setError(null);
    const load = () =>
      getTeam(teamId)
        .then((d) => {
          if (!cancelled) {
            setDetail(d);
            setError(null);
            setLive(anyLive(d.matches)); // speed up polling while this team is live
          }
        })
        .catch((e) => {
          if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load team");
        });
    load();
    const timer = setInterval(() => {
      if (document.visibilityState === "visible") load();
    }, live ? LIVE_POLL_MS : IDLE_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [teamId, live]);

  const groups = useMemo(() => (teams ? groupedTeams(teams) : []), [teams]);
  const shown = detail && detail.team.id === teamId ? detail : null;

  return (
    <div className="myteam">
      <label className="team-picker">
        <span className="section-label">My team</span>
        <select
          className="team-picker-select"
          value={teamId ?? ""}
          onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Choose a team…</option>
          {groups.map(([group, list]) => (
            <optgroup key={group} label={group === "Other" ? "Other" : `Group ${group}`}>
              {list.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </label>

      {teamId == null && <p className="state-msg">Pick a team above to follow it.</p>}
      {teamId != null && error && <p className="state-msg error">Couldn't load team: {error}</p>}
      {teamId != null && !shown && !error && <p className="state-msg">Loading team…</p>}
      {shown && <TeamDetailView detail={shown} />}
    </div>
  );
}
