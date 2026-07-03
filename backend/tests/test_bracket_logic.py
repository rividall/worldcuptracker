"""Unit tests for bracket position/feed derivation (pure logic, no DB)."""

from types import SimpleNamespace

from app.services.bracket import build_positions


def _match(id, stage, winner=None, home=None, away=None):
    return SimpleNamespace(
        id=id, stage=stage, winner_team_id=winner, home_team_id=home, away_team_id=away
    )


def test_final_is_position_zero():
    final = _match(10, "FINAL")
    positions, feeds = build_positions([final])
    assert positions[10] == 0
    assert feeds[10] is None


def test_winner_link_beats_id_order():
    # Two semis feed the final. By ID order, match 1 would be slot 0 —
    # but its winner (team 99) plays as AWAY in the final's... no wait,
    # the final has teams 99 and 42; semi 2's winner 42 is also in the final.
    # Semi 1 (winner 99) and semi 2 (winner 42) both link; slots by parent order.
    final = _match(10, "FINAL", home=42, away=99)
    semi1 = _match(1, "SEMI_FINALS", winner=99)
    semi2 = _match(2, "SEMI_FINALS", winner=42)
    positions, feeds = build_positions([final, semi1, semi2])
    assert feeds[1] == 10
    assert feeds[2] == 10
    assert {positions[1], positions[2]} == {0, 1}
    # Linked children of the same parent are ordered by ID.
    assert positions[1] == 0
    assert positions[2] == 1


def test_unlinked_children_fill_free_slots_in_id_order():
    final = _match(10, "FINAL")  # no teams yet
    semi1 = _match(1, "SEMI_FINALS")  # unresolved
    semi2 = _match(2, "SEMI_FINALS")  # unresolved
    positions, feeds = build_positions([final, semi1, semi2])
    assert positions[1] == 0
    assert positions[2] == 1
    assert feeds[1] == 10
    assert feeds[2] == 10


def test_mixed_linked_and_unlinked():
    # QF pair feeding two semis; only one QF resolved.
    final = _match(100, "FINAL")
    semi_a = _match(51, "SEMI_FINALS", home=7)  # team 7 qualified here
    semi_b = _match(52, "SEMI_FINALS")
    qf1 = _match(1, "QUARTER_FINALS", winner=7)  # links to semi_a
    qf2 = _match(2, "QUARTER_FINALS")
    qf3 = _match(3, "QUARTER_FINALS")
    qf4 = _match(4, "QUARTER_FINALS")
    positions, feeds = build_positions([final, semi_a, semi_b, qf1, qf2, qf3, qf4])

    # semi_a and semi_b get slots 0/1 by ID order (both unlinked to final).
    assert positions[51] == 0 and positions[52] == 1
    # qf1 linked to semi_a → one of slots 0,1
    assert feeds[1] == 51
    assert positions[1] in (0, 1)
    # remaining QFs fill the other three slots in ID order
    taken = {positions[m] for m in (1, 2, 3, 4)}
    assert taken == {0, 1, 2, 3}


def test_full_wc_shape():
    # 16 + 8 + 4 + 2 + 1 with no links: everything positioned, all slots unique.
    matches = []
    mid = 0
    for stage, count in [
        ("LAST_32", 16),
        ("LAST_16", 8),
        ("QUARTER_FINALS", 4),
        ("SEMI_FINALS", 2),
        ("FINAL", 1),
    ]:
        for _ in range(count):
            mid += 1
            matches.append(_match(mid, stage))
    positions, feeds = build_positions(matches)
    assert len(positions) == 31
    l32 = [m for m in matches if m.stage == "LAST_32"]
    assert sorted(positions[m.id] for m in l32) == list(range(16))
    # every non-final match feeds something
    final_id = matches[-1].id
    assert all(feeds[m.id] is not None for m in matches if m.id != final_id)
