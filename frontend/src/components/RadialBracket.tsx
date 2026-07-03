import type { Bracket, BracketMatch, Team } from "@/api/types";
import { isLive } from "@/api/types";

/**
 * Radial knockout bracket: 32 team slots on the outer ring, one ring per
 * round advancing inward, trophy/champion at the center. Pure SVG, polar
 * coordinates computed from each match's bracket `position`.
 */

const SIZE = 1000;
const CENTER = SIZE / 2;
const TEAM_RING_RADIUS = 452;
const ROUND_RADII = [368, 290, 212, 134, 0]; // LAST_32 … FINAL (center)
const TEAM_NODE_RADIUS = 26;
const MATCH_NODE_RADII = [21, 23, 25, 28, 46];

function polar(radius: number, slots: number, position: number): [number, number] {
  const angle = ((-90 + ((position + 0.5) * 360) / slots) * Math.PI) / 180;
  return [CENTER + radius * Math.cos(angle), CENTER + radius * Math.sin(angle)];
}

function Crest({
  team,
  x,
  y,
  r,
  clipId,
  dim,
}: {
  team: Team | null;
  x: number;
  y: number;
  r: number;
  clipId: string;
  dim?: boolean;
}) {
  return (
    <g className={dim ? "node dim" : "node"}>
      <clipPath id={clipId}>
        <circle cx={x} cy={y} r={r - 2} />
      </clipPath>
      <circle cx={x} cy={y} r={r} className="node-bg" />
      {team?.crest_url ? (
        <image
          href={team.crest_url}
          x={x - r + 2}
          y={y - r + 2}
          width={2 * (r - 2)}
          height={2 * (r - 2)}
          clipPath={`url(#${clipId})`}
          preserveAspectRatio="xMidYMid slice"
        />
      ) : (
        <text x={x} y={y + 4} className="node-tbd">
          {team?.tla ?? "·"}
        </text>
      )}
    </g>
  );
}

interface Props {
  bracket: Bracket;
  onSelect: (match: BracketMatch) => void;
}

export default function RadialBracket({ bracket, onSelect }: Props) {
  const rounds = bracket.rounds; // LAST_32 … FINAL, matches sorted by position
  const teamById = new Map<number, Team>();
  for (const round of rounds) {
    for (const match of round.matches) {
      if (match.home_team) teamById.set(match.home_team.id, match.home_team);
      if (match.away_team) teamById.set(match.away_team.id, match.away_team);
    }
  }
  const positionOf = new Map<number, [number, number]>();
  rounds.forEach((round, ri) => {
    const slots = round.matches.length || 1;
    for (const match of round.matches) {
      positionOf.set(match.id, polar(ROUND_RADII[ri], slots, match.position));
    }
  });

  const final = rounds[4]?.matches[0];
  const champion = bracket.champion_team_id
    ? (teamById.get(bracket.champion_team_id) ?? null)
    : null;

  const connectors: React.ReactElement[] = [];
  const nodes: React.ReactElement[] = [];

  rounds.forEach((round, ri) => {
    const slots = round.matches.length || 1;
    round.matches.forEach((match) => {
      const [x, y] = polar(ROUND_RADII[ri], slots, match.position);

      // Outer ring: team slots + connectors into the LAST_32 match node.
      if (ri === 0) {
        ([
          [match.home_team, 2 * match.position],
          [match.away_team, 2 * match.position + 1],
        ] as const).forEach(([team, slot], side) => {
          const [tx, ty] = polar(TEAM_RING_RADIUS, 32, slot);
          const won = team !== null && match.winner_team_id === team.id;
          const lost =
            match.status === "FINISHED" && team !== null && match.winner_team_id !== team.id;
          connectors.push(
            <line
              key={`t${match.id}-${side}`}
              x1={tx}
              y1={ty}
              x2={x}
              y2={y}
              className={won ? "link won" : "link"}
            />
          );
          nodes.push(
            <g
              key={`team-${match.id}-${side}`}
              onClick={() => onSelect(match)}
              className="clickable"
            >
              <Crest
                team={team}
                x={tx}
                y={ty}
                r={TEAM_NODE_RADIUS}
                clipId={`clip-t${match.id}-${side}`}
                dim={lost}
              />
            </g>
          );
        });
      }

      // Connector to the next round inward.
      if (match.feeds_into_match_id !== null) {
        const parent = positionOf.get(match.feeds_into_match_id);
        if (parent) {
          connectors.push(
            <line
              key={`m${match.id}`}
              x1={x}
              y1={y}
              x2={parent[0]}
              y2={parent[1]}
              className={match.winner_team_id !== null ? "link won" : "link"}
            />
          );
        }
      }

      // The match node itself (final rendered separately at the center).
      if (ri < 4) {
        const winner = match.winner_team_id ? (teamById.get(match.winner_team_id) ?? null) : null;
        nodes.push(
          <g key={`match-${match.id}`} onClick={() => onSelect(match)} className="clickable">
            {isLive(match) && (
              <circle cx={x} cy={y} r={MATCH_NODE_RADII[ri] + 6} className="pulse" />
            )}
            <Crest
              team={winner}
              x={x}
              y={y}
              r={MATCH_NODE_RADII[ri]}
              clipId={`clip-m${match.id}`}
            />
          </g>
        );
      }
    });
  });

  return (
    <svg
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      className="radial-bracket"
      role="img"
      aria-label="World Cup knockout bracket"
    >
      <defs>
        <radialGradient id="trophy-glow">
          <stop offset="0%" stopColor="var(--gold)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--gold)" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={CENTER} cy={CENTER} r={150} fill="url(#trophy-glow)" />
      {connectors}
      {nodes}
      {/* Center: champion crest once decided, trophy until then. */}
      <g
        className="clickable"
        onClick={() => final && onSelect(final)}
        aria-label="Final"
      >
        {final && isLive(final) && (
          <circle cx={CENTER} cy={CENTER} r={MATCH_NODE_RADII[4] + 8} className="pulse" />
        )}
        {champion ? (
          <Crest
            team={champion}
            x={CENTER}
            y={CENTER}
            r={MATCH_NODE_RADII[4]}
            clipId="clip-champion"
          />
        ) : (
          <text x={CENTER} y={CENTER + 18} className="trophy">
            🏆
          </text>
        )}
      </g>
    </svg>
  );
}
