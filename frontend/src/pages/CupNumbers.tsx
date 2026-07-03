import type { Scorer, StatMatch, StatTeam } from "@/api/types";
import { getCupNumbers } from "@/api/worldcup";
import Stat from "@/components/Stat";
import { usePolling } from "@/hooks/usePolling";

const POLL_MS = 15 * 60 * 1000;

function matchLine(sm: StatMatch): string {
  const m = sm.match;
  const home = m.home_team?.tla ?? "TBD";
  const away = m.away_team?.tla ?? "TBD";
  return `${home} ${m.score.home}–${m.score.away} ${away}`;
}

function TeamSuper({ label, stat, unit }: { label: string; stat: StatTeam | null; unit: string }) {
  if (!stat) return null;
  return (
    <div className="super-card">
      <span className="super-label">{label}</span>
      <span className="super-team">
        {stat.team.crest_url && <img src={stat.team.crest_url} alt="" className="crest-sm" />}
        {stat.team.name}
      </span>
      <span className="super-value">
        {stat.value} <small>{unit}</small>
      </span>
    </div>
  );
}

function MatchSuper({ label, stat, unit }: { label: string; stat: StatMatch | null; unit: string }) {
  if (!stat) return null;
  return (
    <div className="super-card">
      <span className="super-label">{label}</span>
      <span className="super-team">{matchLine(stat)}</span>
      <span className="super-value">
        {stat.value} <small>{unit}</small>
      </span>
    </div>
  );
}

function Leaderboard({
  title,
  rows,
  metric,
}: {
  title: string;
  rows: Scorer[];
  metric: "goals" | "assists";
}) {
  return (
    <section>
      <h3 className="section-label">{title}</h3>
      {rows.length === 0 ? (
        <p className="muted-note">Nothing here yet.</p>
      ) : (
        <table className="scorer-table">
          <thead>
            <tr>
              <th className="s-rank">#</th>
              <th className="s-name">Player</th>
              <th>G</th>
              <th>A</th>
              <th>MP</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s, i) => (
              <tr key={s.player_id}>
                <td className="s-rank">{i + 1}</td>
                <td className="s-name">
                  <span className="s-namewrap">
                    <span>{s.player_name}</span>
                    {s.team_crest && (
                      <img src={s.team_crest} alt={s.team_tla ?? ""} className="s-flag" />
                    )}
                  </span>
                </td>
                <td className={metric === "goals" ? "s-goals" : ""}>{s.goals}</td>
                <td className={metric === "assists" ? "s-goals" : ""}>{s.assists ?? "–"}</td>
                <td>{s.played_matches ?? "–"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default function CupNumbers() {
  const { data, error, loading } = usePolling(getCupNumbers, POLL_MS);

  if (loading) return <p className="state-msg">Loading numbers…</p>;
  if (error) return <p className="state-msg error">Couldn't load numbers: {error}</p>;
  if (!data) return <p className="state-msg">No data yet — first sync pending.</p>;

  const t = data.totals;
  const s = data.superlatives;

  return (
    <div className="cup-numbers">
      <div className="stat-grid">
        <Stat label="Goals" value={t.goals} strong />
        <Stat label="Goals / match" value={t.goals_per_match.toFixed(2)} />
        <Stat label="Matches" value={`${t.matches_played}/${t.matches_total}`} />
        <Stat label="Clean sheets" value={t.clean_sheets} />
        <Stat label="Shootouts" value={t.shootouts} />
        <Stat label="Extra time" value={t.extra_time} />
      </div>

      <h3 className="section-label">Superlatives</h3>
      <div className="super-grid">
        <TeamSuper label="Best attack" stat={s.best_attack} unit="goals" />
        <TeamSuper label="Best defense" stat={s.best_defense} unit="conceded" />
        <TeamSuper label="Most clean sheets" stat={s.most_clean_sheets} unit="clean" />
        <MatchSuper label="Biggest win" stat={s.biggest_win} unit="margin" />
        <MatchSuper label="Highest scoring" stat={s.highest_scoring} unit="goals" />
      </div>

      <Leaderboard title="Top scorers" rows={data.top_scorers} metric="goals" />
      <Leaderboard title="Top assists" rows={data.top_assisters} metric="assists" />
    </div>
  );
}
