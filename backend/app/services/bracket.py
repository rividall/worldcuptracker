"""Bracket structure derivation.

football-data.org exposes no bracket adjacency and match IDs are NOT in
bracket order (see docs/research/football-data-analysis.md §5). Strategy:

1. Link by winner: a finished match whose winner appears in a later-round
   match feeds that match. Exact; coverage grows as rounds resolve.
2. Positions assigned top-down from the FINAL (position 0): parent at
   position p expects children at 2p and 2p+1. Linked children take their
   slots; unlinked children fill remaining slots in ID order.

Pure functions over Match-like objects (needs: id, stage, winner_team_id,
home_team_id, away_team_id) so this is unit-testable without a DB.
"""

ROUND_ORDER = ["LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"]

# Fixed 2026 bracket slot order, by football-data match id.
#
# Winner-linking (below) reconstructs adjacency only for rounds that have been
# PLAYED. For rounds still to come, football-data leaves the teams null and
# exposes no adjacency, so we fall back to ordering by match id — which assumes
# id order == bracket order. That assumption holds for every round EXCEPT the
# quarter-finals and the round-of-16 that feed them: football-data numbers the
# two middle quarters into the wrong halves. Verified against the official 2026
# bracket on 2026-07-03 — the Brazil/Mexico quarter (QF 537384) and the
# Spain·Portugal/USA·Belgium quarter (QF 537385) are transposed, which would let
# Brazil meet Spain/France before the final. Pinning the true slot order for
# just these two rounds puts Brazil & Argentina in one half and Spain & France
# in the other. Every other round (R32, semis, final) is already id-ordered.
BRACKET_ORDER: dict[str, list[int]] = {
    # R16 slots 0..7. Middle two pairs swapped vs. id order:
    #   377,378 (Brazil/Mexico quarter) trade places with 379,380 (Spain quarter).
    "LAST_16": [537375, 537376, 537379, 537380, 537377, 537378, 537381, 537382],
    # QF slots 0..3: 537384 and 537385 swapped vs. id order.
    "QUARTER_FINALS": [537383, 537385, 537384, 537386],
}


def _bracket_key(match) -> int:
    """Slot order for a match: the fixed template when known, else match id."""
    order = BRACKET_ORDER.get(match.stage)
    if order and match.id in order:
        return order.index(match.id)
    return match.id


def build_positions(matches: list) -> tuple[dict[int, int], dict[int, int | None]]:
    """Return (positions, feeds_into) keyed by match id.

    positions: index of each knockout match within its round, bracket order.
    feeds_into: match id of the next-round match this one feeds (or None).
    """
    rounds = {
        stage: sorted((m for m in matches if m.stage == stage), key=_bracket_key)
        for stage in ROUND_ORDER
    }

    positions: dict[int, int] = {}
    feeds_into: dict[int, int | None] = {}

    # Final sits at position 0.
    for match in rounds["FINAL"]:
        positions[match.id] = 0
        feeds_into[match.id] = None

    # Walk down: assign child positions from parent positions.
    for round_index in range(len(ROUND_ORDER) - 1, 0, -1):
        parents = rounds[ROUND_ORDER[round_index]]
        children = rounds[ROUND_ORDER[round_index - 1]]
        slot_count = 2 * len(parents)
        taken: set[int] = set()
        unlinked: list = []

        # Pass 1: children linked to a parent by winner.
        parent_children: dict[int, list] = {p.id: [] for p in parents}
        for child in children:
            parent = _find_parent(child, parents)
            if parent is not None:
                parent_children[parent.id].append(child)
            else:
                unlinked.append(child)

        for parent in parents:
            base = 2 * positions[parent.id]
            for offset, child in enumerate(sorted(parent_children[parent.id], key=lambda m: m.id)[:2]):
                positions[child.id] = base + offset
                feeds_into[child.id] = parent.id
                taken.add(base + offset)

        # Pass 2: unlinked children fill remaining slots in ID order.
        free_slots = [s for s in range(slot_count) if s not in taken]
        for child, slot in zip(unlinked, free_slots):
            positions[child.id] = slot
            # Feed target implied by geometry: parent at slot // 2.
            parent = next((p for p in parents if positions[p.id] == slot // 2), None)
            feeds_into[child.id] = parent.id if parent else None

    return positions, feeds_into


def _find_parent(child, parents):
    if child.winner_team_id is None:
        return None
    for parent in parents:
        if child.winner_team_id in (parent.home_team_id, parent.away_team_id):
            return parent
    return None
