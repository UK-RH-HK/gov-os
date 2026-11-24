"""PG-4: ``gov decisions answer`` on a valid sheet: entries, packages, stored sheet, one commit, nothing new for
``gov decisions basis`` and ``gov links``."""
from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest

import w2_211_support as S

NOTE = 'only for the first week | "then" ask me again é☕'


def _picks(cards):
    by_id = {"DP-0042": ("b", NOTE), "DP-0043": ("a", None), "DP-0044": ("skip", None), "DP-0045": ("b", None)}
    return [(pid, *by_id[pid]) for pid in cards]


@pytest.fixture
def done(case, env):
    repo, batch, digest, cards = case
    before_head = S.head(repo, env)
    before = S.snapshot(repo)
    sheet = S.sheet_text(batch, digest, _picks(cards))
    run = S.answer(repo, env, sheet)
    assert run.code == 0, f"answer failed ({run.code}): {run.both[-800:]}"
    return {"repo": repo, "batch": batch, "digest": digest, "cards": cards, "sheet": sheet, "run": run,
            "before_head": before_head, "before": before, "env": env}


def _new_entries(d):
    text = (d["repo"] / S.REGISTER).read_text(encoding="utf-8")
    return dict(S.entries(text))


def test_one_entry_per_pick_in_the_form_with_consecutive_ids(done):
    ents = _new_entries(done)
    new = [k for k in ents if int(k.split("-")[1]) > 1250]
    assert new == ["DEC-1251", "DEC-1252", "DEC-1253"], f"ids must be the next free, consecutive, in sheet order: {new}"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    batch = done["batch"]
    cards = [c for c in done["cards"] if c != "DP-0044"]
    heads = {"DP-0042": "Question DP-0042: Change it", "DP-0043": "Question DP-0043: Keep it",
             "DP-0045": "Question DP-0045: No"}
    for dec, pid in zip(new, cards):
        e = ents[dec]
        assert e.startswith(f"### {dec} — {heads[pid]}\n"), e.splitlines()[0]
        status = re.search(r"(?m)^- \*\*Status:\*\* (.*)$", e).group(1)
        assert status.startswith(f"ACCEPTED (owner, {date}, on the decisions page {batch}, answer {pid}"), status
        assert re.search(r"(?m)^- \*\*Decision:\*\* ", e) and re.search(r"(?m)^- \*\*Basis:\*\* ", e)
        assert re.search(r"(?m)^- \*\*Governing sources:\*\* ", e)
        basis = re.search(r"(?m)^- \*\*Basis:\*\* (.*)$", e).group(1)
        assert batch in basis and f"What was found for {pid}" in basis, basis
        assert "docs/spec.md" in e and pid in re.search(r"(?m)^- \*\*Governing sources:\*\* (.*)$", e).group(1)
    e42 = ents[new[0]]
    assert "(b) Change it" in e42 and "Change it goes ahead and the next step starts" in e42
    assert f'"{NOTE}"' in e42, "the owner's note must be carried verbatim, in quotes"
    assert "**Under:** DEC-1225" in e42 and "**Changes:** DEC-1230" in e42
    assert "owner's note" not in ents[new[1]].lower() and "**Changes:**" not in ents[new[1]]
    assert "**Under:**" not in ents[new[1]]
    # earlier entries untouched
    before = dict(S.entries(done["before"][S.REGISTER].decode("utf-8")))
    assert all(ents[k] == v for k, v in before.items())


def test_status_lines_read_as_the_owners_decision(done):
    from gov.close.history import owner_decision, register_entries
    reg = register_entries(done["repo"], S.REGISTER)
    for dec in ("DEC-1251", "DEC-1252", "DEC-1253"):
        why, _text = owner_decision(dec, reg)
        assert why is None, f"{dec}: {why}"


def test_packages_accepted_skip_untouched_and_sheet_stored(done):
    repo, batch = done["repo"], done["batch"]
    for pid, dec, letter in (("DP-0042", "DEC-1251", "b"), ("DP-0043", "DEC-1252", "a"), ("DP-0045", "DEC-1253", "b")):
        text = (repo / S.PKG_DIR / f"{pid}.md").read_text(encoding="utf-8")
        assert re.search(r'(?m)^status: "?ACCEPTED"?\s*$', text), f"{pid} stays PROPOSED"
        assert dec in text and batch in text and re.search(rf"\b{letter}\b", text.split("## Answer", 1)[1]), text[-400:]
    key = f"{S.PKG_DIR}/DP-0044.md"
    assert (repo / key).read_bytes() == done["before"][key], "a skip changed its package"
    assert re.search(r'(?m)^status: "?PROPOSED"?\s*$', (repo / key).read_text(encoding="utf-8"))
    sheets = list((repo / S.BATCH_DIR).glob(f"{batch}.sheet-*.txt"))
    assert len(sheets) == 1, [s.name for s in sheets]
    assert sheets[0].read_text(encoding="utf-8") == done["sheet"]
    assert re.fullmatch(rf"{re.escape(batch)}\.sheet-[0-9a-f]{{8}}\.txt", sheets[0].name), sheets[0].name


def test_one_commit_with_the_trailers_and_nothing_left_behind(done):
    repo, env, batch = done["repo"], done["env"], done["batch"]
    assert S.git("rev-list", "--count", f"{done['before_head']}..HEAD", cwd=repo, env=env) == "1"
    subject = S.git("log", "-1", "--format=%s", cwd=repo, env=env)
    assert subject.startswith(f"DEC-1251 to DEC-1253 (page {batch}): "), subject
    trailers = S.git("log", "-1", "--format=%(trailers:only,unfold)", cwd=repo, env=env)
    for line in ("Task: decision-record", "Role: orchestrator", f"Decided-by: owner (page {batch})"):
        assert line in trailers.splitlines(), f"missing trailer {line!r}: {trailers!r}"
    assert S.git("status", "--porcelain", cwd=repo, env=env) == "", "nothing may be left unstaged or staged"
    changed = set(S.git("show", "--name-only", "--format=", "HEAD", cwd=repo, env=env).splitlines())
    assert S.REGISTER in changed and f"{S.PKG_DIR}/DP-0044.md" not in changed
    assert {f"{S.PKG_DIR}/DP-004{n}.md" for n in (2, 3, 5)} <= changed
    assert len(changed) == 5, changed


def test_output_names_each_answer_the_skip_and_the_notes(done):
    out = done["run"].out
    assert re.search(r"DP-0042 -> DEC-1251 \(b\)", out) and re.search(r"DP-0043 -> DEC-1252 \(a\)", out)
    assert re.search(r"DP-0045 -> DEC-1253 \(b\)", out)
    assert re.search(r"skipped: .*DP-0044", out), out
    assert "notes for the CTO" in out and "ask me again" in out
    assert re.search(r"still open in this batch: .*DP-0044", out), out


def test_basis_and_links_find_nothing_new(done):
    repo, env = done["repo"], done["env"]
    basis = S.gov(["decisions", "basis", "--range", "HEAD^..HEAD", "--root", repo], env=env, cwd=repo)
    assert basis.code == 0, basis.both[-600:]
    assert "fail" not in basis.out and basis.out.count("DEC-125") >= 3, basis.out
    links = S.gov(["links", "--since", "HEAD~1", "--root", repo], env=env, cwd=repo)
    assert links.code in (0, 1), links.both[-400:]
    for dec in ("DEC-1251", "DEC-1252", "DEC-1253"):
        assert dec not in links.both, f"links finds something in {dec}: {links.both[-600:]}"
