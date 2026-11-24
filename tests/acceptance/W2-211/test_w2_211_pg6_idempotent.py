"""PG-6: the same sheet twice, a skip then a fuller sheet, a changed mind."""
from __future__ import annotations

import re

import w2_211_support as S


def _sheet(case, picks_by_id):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, [(pid, *picks_by_id.get(pid, ("skip", None))) for pid in cards])


def test_second_paste_changes_nothing_exits_zero_and_names_the_entries(case, env):
    repo = case[0]
    sheet = _sheet(case, {"DP-0042": ("b", "n"), "DP-0043": ("a", None)})
    assert S.answer(repo, env, sheet).code == 0
    snap, head = S.snapshot(repo), S.head(repo, env)
    text = (repo / S.REGISTER).read_text(encoding="utf-8")
    again = S.answer(repo, env, sheet)
    assert again.code == 0, again.both[-500:]
    assert re.search(r"DP-0042 already recorded as DEC-1251", again.out), again.out
    assert re.search(r"DP-0043 already recorded as DEC-1252", again.out), again.out
    assert S.snapshot(repo) == snap and S.head(repo, env) == head
    assert (repo / S.REGISTER).read_text(encoding="utf-8") == text


def test_a_skip_writes_nothing_and_a_fuller_sheet_answers_only_what_is_open(case, env):
    repo = case[0]
    start = S.head(repo, env)
    first = _sheet(case, {"DP-0042": ("a", None), "DP-0043": ("skip", None)})
    assert S.answer(repo, env, first).code == 0
    assert S.git("rev-list", "--count", f"{start}..HEAD", cwd=repo, env=env) == "1"
    reg = (repo / S.REGISTER).read_text(encoding="utf-8")
    assert len([k for k, _ in S.entries(reg) if int(k[4:]) > 1250]) == 1, "the skips wrote entries"
    assert re.search(r'(?m)^status: "?PROPOSED"?\s*$', (repo / S.PKG_DIR / "DP-0043.md").read_text(encoding="utf-8"))
    mid = S.head(repo, env)
    fuller = _sheet(case, {"DP-0042": ("a", None), "DP-0043": ("b", "later"), "DP-0044": ("a", None)})
    run = S.answer(repo, env, fuller)
    assert run.code == 0, run.both[-500:]
    assert S.git("rev-list", "--count", f"{mid}..HEAD", cwd=repo, env=env) == "1"
    ents = S.entries((repo / S.REGISTER).read_text(encoding="utf-8"))
    new = [k for k, _ in ents if int(k[4:]) > 1250]
    assert new == ["DEC-1251", "DEC-1252", "DEC-1253"], new
    body = "\n".join(t for _k, t in ents)
    for pid in ("DP-0042", "DP-0043", "DP-0044"):
        assert len(re.findall(rf"answer {pid}\b", body)) == 1, f"{pid} answered twice"
    assert "DP-0042 already recorded as DEC-1251" in run.out
    for pid in ("DP-0043", "DP-0044"):
        assert re.search(rf'(?m)^status: "?ACCEPTED"?\s*$', (repo / S.PKG_DIR / f"{pid}.md").read_text(encoding="utf-8"))


def test_another_option_for_an_answered_package_is_refused(case, env):
    repo = case[0]
    assert S.answer(repo, env, _sheet(case, {"DP-0042": ("a", None)})).code == 0
    snap, head = S.snapshot(repo), S.head(repo, env)
    run = S.answer(repo, env, _sheet(case, {"DP-0042": ("b", None)}))
    assert run.code == 1 and "ANSWER_CONFLICT" in run.both, run.both[-500:]
    assert S.snapshot(repo) == snap and S.head(repo, env) == head
