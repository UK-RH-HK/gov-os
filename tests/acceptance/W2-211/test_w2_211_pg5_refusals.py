"""PG-5: each refusal code from a good sheet with one change; the tree and HEAD are the same after."""
from __future__ import annotations

import json

import pytest

import w2_211_support as S


def _picks(cards):
    by_id = {"DP-0042": ("b", "ok"), "DP-0043": ("a", None), "DP-0044": ("a", None), "DP-0045": ("b", None)}
    return [(pid, *by_id[pid]) for pid in cards]


def _good(case):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards))


def _replace_line(sheet, prefix, new):
    return "\n".join(new if ln.startswith(prefix) else ln for ln in sheet.split("\n"))


def _edit_package(repo, env, pid, fn, msg):
    p = repo / S.PKG_DIR / f"{pid}.md"
    p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")
    S.commit(repo, env, msg)


def c_role(case, env):
    return _good(case), "engineer"


def c_format_first_line(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards), first="GOV-ANSWERS 2"), None


def c_format_count(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards), count=3), None


def c_format_duplicate(case, env):
    repo, batch, digest, cards = case
    picks = _picks(cards)
    picks[1] = (picks[0][0], "a", None)
    return S.sheet_text(batch, digest, picks), None


def c_format_long_note(case, env):
    repo, batch, digest, cards = case
    picks = _picks(cards)
    picks[0] = (picks[0][0], picks[0][1], "x" * 401)
    return S.sheet_text(batch, digest, picks), None


def c_format_no_end(case, env):
    return _good(case).replace("END\n", ""), None


def c_format_order(case, env):
    lines = _good(case).split("\n")
    lines[1], lines[2] = lines[2], lines[1]
    return "\n".join(lines), None


def c_batch_unknown(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text("B-19990101-9", digest, _picks(cards)), None


def c_batch_edited_manifest(case, env):
    repo, batch, digest, cards = case
    f = repo / S.BATCH_DIR / f"{batch}.manifest.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    prefix = "sha256:" if str(data["hash"]).startswith("sha256:") else ""
    data["hash"] = prefix + "0" * 64
    f.write_text(json.dumps(data), encoding="utf-8")
    S.commit(repo, env, "hand-edited manifest")
    return _good(case), None


def c_hash(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, ("0" if digest[0] != "0" else "1") + digest[1:], _picks(cards)), None


def c_unknown_id(case, env):
    repo, batch, digest, cards = case
    picks = _picks(cards)
    picks[2] = ("DP-0777", "a", None)
    return S.sheet_text(batch, digest, picks), None


def c_wrong_order(case, env):
    repo, batch, digest, cards = case
    picks = _picks(cards)
    picks[0], picks[1] = picks[1], picks[0]
    return S.sheet_text(batch, digest, picks), None


def c_missing_card(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards)[:-1]), None


def c_option(case, env):
    repo, batch, digest, cards = case
    picks = [(pid, "c" if pid == "DP-0045" else letter, n) for pid, letter, n in _picks(cards)]
    return S.sheet_text(batch, digest, picks), None


def c_withdrawn(case, env):
    repo, batch, digest, cards = case
    S.write(repo / S.PKG_DIR / "DP-0099.md", S.package_text("DP-0099", replaces="DP-0042"))
    S.commit(repo, env, "re-ask")
    return _good(case), None


def c_stale_changed(case, env):
    repo, batch, digest, cards = case
    _edit_package(repo, env, "DP-0043", lambda t: t.replace("the old way is slow", "the old way is fast"), "edit")
    return _good(case), None


def c_stale_declined(case, env):
    repo, batch, digest, cards = case
    _edit_package(repo, env, "DP-0044", lambda t: t.replace('"PROPOSED"', '"DECLINED"'), "declined")
    return _good(case), None


def c_date_before(case, env):
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards), answered="2000-01-01T00:00:00Z"), None


def c_date_future(case, env):
    from datetime import timedelta
    repo, batch, digest, cards = case
    return S.sheet_text(batch, digest, _picks(cards), answered=S.now_stamp(timedelta(days=3))), None


def c_dirty_register(case, env):
    repo = case[0]
    with open(repo / S.REGISTER, "a", encoding="utf-8") as fh:
        fh.write("\nuncommitted\n")
    return _good(case), None


def c_dirty_package(case, env):
    repo = case[0]
    with open(repo / S.PKG_DIR / "DP-0042.md", "a", encoding="utf-8") as fh:
        fh.write("\nuncommitted\n")
    return _good(case), None


def c_register_unreadable(case, env):
    repo = case[0]
    S.write(repo / S.REGISTER, "nothing here that is an entry\n")
    S.commit(repo, env, "broken register")
    return _good(case), None


CASES = [
    ("ANSWER_ROLE", c_role), ("ANSWER_FORMAT", c_format_first_line), ("ANSWER_FORMAT", c_format_count),
    ("ANSWER_FORMAT", c_format_duplicate), ("ANSWER_FORMAT", c_format_long_note), ("ANSWER_FORMAT", c_format_no_end),
    ("ANSWER_FORMAT", c_format_order), ("ANSWER_BATCH", c_batch_unknown), ("ANSWER_BATCH", c_batch_edited_manifest),
    ("ANSWER_HASH", c_hash), ("ANSWER_UNKNOWN_ID", c_unknown_id), ("ANSWER_UNKNOWN_ID", c_wrong_order),
    ("ANSWER_UNKNOWN_ID", c_missing_card), ("ANSWER_OPTION", c_option), ("ANSWER_WITHDRAWN", c_withdrawn),
    ("ANSWER_STALE", c_stale_changed), ("ANSWER_STALE", c_stale_declined), ("ANSWER_DATE", c_date_before),
    ("ANSWER_DATE", c_date_future), ("ANSWER_DIRTY", c_dirty_register), ("ANSWER_DIRTY", c_dirty_package),
    ("REGISTER_UNREADABLE", c_register_unreadable),
]


@pytest.mark.parametrize("code,make", CASES, ids=[f"{c}-{m.__name__[2:]}" for c, m in CASES])
def test_refusal_carries_its_code_and_changes_nothing(case, env, code, make):
    repo = case[0]
    sheet, role = make(case, env)
    run_env = S.make_env(S.make_home(repo.parent / "h2"), role=role) if role else env
    before, head = S.snapshot(repo), S.head(repo, env)
    status = S.git("status", "--porcelain", cwd=repo, env=env)
    run = S.answer(repo, run_env, sheet)
    assert run.code == 1, f"expected exit 1, got {run.code}: {run.both[-500:]}"
    assert code in run.both, f"expected {code}: {run.both[-500:]}"
    assert S.snapshot(repo) == before, "a refusal changed a file"
    assert S.head(repo, env) == head, "a refusal made a commit"
    assert S.git("status", "--porcelain", cwd=repo, env=env) == status


def test_withdrawn_names_the_newer_package(case, env):
    sheet, _ = c_withdrawn(case, env)
    run = S.answer(case[0], env, sheet)
    assert "ANSWER_WITHDRAWN" in run.both and "DP-0099" in run.both, run.both[-500:]
