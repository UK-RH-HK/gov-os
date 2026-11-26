"""UR-4: three planted repositories (helpers, a resumed session, a session across midnight) give exact rows."""

from __future__ import annotations

import w2_207_support as s

D1, D2 = "2026-11-24", "2026-11-25"


def plant(env):
    m = env.msg
    alpha, beta, gamma = env.repo("alpha"), env.repo("beta"), env.repo("gamma")
    env.launch(alpha, "A1", "engineer")
    a1 = [
        m(alpha, "A1", "a1", s.ts(D1, "10:00:00"), "m-a", 1, 5, 100, 10),   # streaming chunk, superseded
        m(alpha, "A1", "a1", s.ts(D1, "10:00:01"), "m-a", 2, 50, 1000, 100),  # the last line of a1 counts
        "this line is not json {",
        {"type": "assistant", "sessionId": "A1", "cwd": str(alpha), "timestamp": s.ts(D1, "10:01:00"),
         "message": {"id": "nou", "role": "assistant", "model": "m-a"}},      # no usage
        "also not json",
        m(alpha, "A1", "a2", s.ts(D1, "23:59:59"), "m-a", 3, 30, 0, 0),
        m(alpha, "A1", "a3", s.ts(D2, "00:00:01"), "m-a", 4, 40, 200, 0),
        m(alpha, "A1", "a4", s.ts(D2, "08:00:00"), "m-a", 5, 10, 0, 0),
    ]
    env.transcript(alpha, "A1", a1)
    # the resumed session: a second file repeating the history, then one new message
    resumed = [x for x in a1 if not isinstance(x, str)] + [
        m(alpha, "A1", "a5", s.ts(D1, "12:00:00"), "m-a", 6, 6, 6, 6)]
    resumed.pop(0)  # without the superseded chunk; the same last line of a1 remains
    env.transcript(alpha, "A1", resumed, file="A1-resumed")
    env.transcript(alpha, "A1", [
        m(alpha, "A1", "h1", s.ts(D1, "11:00:00"), "m-b", 10, 100, 1000, 100, True),
        m(alpha, "A1", "h2", s.ts(D1, "11:01:00"), "m-a", 1, 1, 1, 1, True),
    ], helper="h1", agent_type="reviewer")

    env.cto("B1")
    env.transcript(beta, "B1", [m(beta, "B1", "b1", s.ts(D1, "09:00:00"), "m-a", 1, 2, 3, 4)])
    env.transcript(beta, "B1", [m(beta, "B1", "bh", s.ts(D1, "09:10:00"), "m-a", 2, 2, 2, 2, True)],
                   helper="h2", agent_type="engineer")
    env.transcript(beta, "B2", [m(beta, "B2", "b2", s.ts(D1, "09:30:00"), "m-b", 100, 200, 300, 400)])

    for sess in ("G1", "G2"):  # the same message id in two sessions counts in each
        env.launch(gamma, sess, "qa")
        env.transcript(gamma, sess, [m(gamma, sess, "mg", s.ts(D1, "01:00:00"), "m-a", 1000, 0, 0, 0)])
    return alpha, beta, gamma


def tok(t):
    return (t["input"], t["output"], t["cache_read"], t["cache_creation"])


def test_ur4_day_one_rows_and_totals_by_hand(env):
    alpha, beta, gamma = plant(env)
    r = env.daily(D1)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = env.record(D1)
    assert rec["skipped_lines"] == 3  # two non-JSON lines and one assistant line with no usage
    assert "3" in r.stdout
    rows = {(x["session"], x["model"]): x for x in rec["rows"]}
    assert set(rows) == {("A1", "m-a"), ("A1/agent-h1", "m-b"), ("A1/agent-h1", "m-a"),
                         ("B1", "m-a"), ("B1/agent-h2", "m-a"), ("B2", "m-b"), ("G1", "m-a"), ("G2", "m-a")}

    # A1 on day 1: a1 once (last line), a2, a5, the resumed copy counted once; a3 and a4 belong to day 2
    a = rows[("A1", "m-a")]
    assert (a["repository"], a["role"]) == (str(alpha), "engineer")
    assert tok(a) == (11, 86, 1006, 106) and a["context_peak"] == 1102 and a["cost_usd"] == 0.003366

    hb, ha = rows[("A1/agent-h1", "m-b")], rows[("A1/agent-h1", "m-a")]
    assert (hb["role"], hb["repository"]) == ("reviewer", str(alpha))
    assert tok(hb) == (10, 100, 1000, 100) and hb["context_peak"] == 1110 and hb["cost_usd"] == 0.00102
    assert tok(ha) == (1, 1, 1, 1) and ha["context_peak"] == 3 and ha["cost_usd"] == 0.000036

    b1, bh, b2 = rows[("B1", "m-a")], rows[("B1/agent-h2", "m-a")], rows[("B2", "m-b")]
    assert (b1["role"], b1["cost_usd"], b1["context_peak"]) == ("cto", 0.000073, 8)
    assert (bh["role"], bh["cost_usd"], bh["context_peak"]) == ("engineer", 0.000072, 6)
    assert b2["role"] == "unknown" and "unknown" in b2["role_source"]
    assert (b2["cost_usd"], b2["context_peak"]) == (0.00155, 800)
    for g in ("G1", "G2"):
        assert tok(rows[(g, "m-a")]) == (1000, 0, 0, 0) and rows[(g, "m-a")]["cost_usd"] == 0.01

    t = rec["totals"]
    A, B, G = str(alpha), str(beta), str(gamma)
    assert tok(t["by_repository"][A]) == (22, 187, 2007, 207) and abs(t["by_repository"][A]["cost_usd"] - 0.004422) < 1e-6
    assert tok(t["by_repository"][B]) == (103, 204, 305, 406) and abs(t["by_repository"][B]["cost_usd"] - 0.001695) < 1e-6
    assert tok(t["by_repository"][G]) == (2000, 0, 0, 0) and abs(t["by_repository"][G]["cost_usd"] - 0.02) < 1e-6
    assert tok(t["by_role"]["engineer"]) == (13, 88, 1008, 108) and abs(t["by_role"]["engineer"]["cost_usd"] - 0.003438) < 1e-6
    assert tok(t["by_role"]["reviewer"]) == (11, 101, 1001, 101)
    assert tok(t["by_role"]["qa"]) == (2000, 0, 0, 0)
    assert tok(t["by_model"]["m-b"]) == (110, 300, 1300, 500) and abs(t["by_model"]["m-b"]["cost_usd"] - 0.00257) < 1e-6
    assert tok(t["by_model"]["m-a"])[0] == 2015 and abs(t["by_model"]["m-a"]["cost_usd"] - 0.023547) < 1e-6
    assert tok(t["by_repository_role"][f"{A}|engineer"]) == (11, 86, 1006, 106)
    s.assert_totals_match(rec)


def test_ur4_the_session_spanning_midnight_has_only_its_own_day_in_each_record(env):
    alpha, _b, _g = plant(env)
    assert env.daily(D1).returncode == 0
    assert env.daily(D2).returncode == 0
    rec = env.record(D2)
    assert rec["date"] == D2
    assert len(rec["rows"]) == 1  # the resumed file's repeats of a3 and a4 are counted once
    a = rec["rows"][0]
    assert (a["session"], a["repository"], a["role"], a["model"]) == ("A1", str(alpha), "engineer", "m-a")
    assert tok(a) == (9, 50, 200, 0) and a["context_peak"] == 204 and a["cost_usd"] == 0.00129
    s.assert_totals_match(rec)
    assert len(env.record(D1)["rows"]) == 8


def test_ur4_a_transcript_of_only_bad_lines_is_skipped_and_counted_never_fatal(env):
    repo = env.repo("alpha")
    env.launch(repo, "S1", "engineer")
    env.transcript(repo, "S1", [
        "{broken", "", "[]", {"type": "assistant", "cwd": str(repo), "timestamp": s.ts(D1), "message": {"id": "q"}},
        env.msg(repo, "S1", "ok", s.ts(D1), "m-a", 1, 1, 1, 1),
    ])
    r = env.daily(D1)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = env.record(D1)
    assert rec["skipped_lines"] >= 2
    assert [x["session"] for x in rec["rows"]] == ["S1"] and rec["rows"][0]["cost_usd"] == 0.000036
