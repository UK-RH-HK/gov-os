"""EL-2: a decision below its level is refused with DECISION_BELOW_LEVEL by ``gov decisions basis --range`` and
``answer`` runs the same check."""
from __future__ import annotations

import pytest

import w2_211_support as S

# (touches, reversible, inside, Decided-by, expected level, passes)
CASES = [
    ("spec", "yes", "repository", "CTO", "P1", False),
    ("spec", "yes", "repository", "orchestrator", "P1", False),
    ("spec", "yes", "repository", "lead", "P1", False),
    ("own-ticket", "no", "repository", "CTO", "P1", False),
    ("own-ticket", "yes", "outside", "lead", "P2", False),
    ("shared-code", "yes", "worktree", "lead", "P2", False),
    ("kernel-text", "yes", "worktree", "lead", "P2", False),
    ("spec", "yes", "repository", "owner (chat)", "P1", True),
    ("spec", "yes", "repository", "owner (page B-20261123-1)", "P1", True),
    ("shared-code", "yes", "repository", "owner (chat)", "P2", True),
    ("shared-code", "yes", "repository", "CTO", "P2", True),
    ("shared-code", "yes", "repository", "orchestrator", "P2", True),
    ("shared-code", "yes", "repository", "senior-engineer", "P2", True),
    ("own-ticket", "yes", "worktree", "lead", "P3", True),
    ("own-ticket", "yes", "worktree", "CTO", "P3", True),
]


def _entry(touches, rev, inside, who, extra=""):
    owner = who.startswith("owner")
    status = "ACCEPTED (owner, 2026-11-24, in the chat" if owner else f"ACCEPTED ({who}, 2026-11-24, in the ticket"
    lines = ["### DEC-1300 — A choice that is recorded",
             f"- **Status:** {status}; recorded by the CTO)"]
    if touches is not None:
        lines += [f"- **Touches:** {touches}", f"- **Reversible:** {rev}", f"- **Inside:** {inside}"]
    lines += ["- **Decision:** go ahead with the small change." + extra, "- **Adds:** no rule",
              "- **Basis:** the message of 2026-11-24; docs/spec.md", "- **Governing sources:** docs/spec.md", ""]
    return "\n".join(lines)


def _land(tmp_path, env, entry, who):
    repo = S.init_repo(tmp_path, env, "el2")
    reg = repo / S.REGISTER
    reg.write_text(reg.read_text(encoding="utf-8") + "\n" + entry, encoding="utf-8")
    S.commit(repo, env, f"DEC-1300: a choice\n\nTask: decision-record\nRole: orchestrator\nDecided-by: {who}")
    return repo


def _basis(repo, env):
    return S.gov(["decisions", "basis", "--range", "HEAD^..HEAD", "--root", repo], env=env, cwd=repo)


@pytest.mark.parametrize("touches,rev,inside,who,level,ok", CASES,
                         ids=[f"{t}-{r}-{i}-{w.split()[0]}" for t, r, i, w, _l, _o in CASES])
def test_the_range_check_judges_the_decider_against_the_level(tmp_path, env, touches, rev, inside, who, level, ok):
    repo = _land(tmp_path, env, _entry(touches, rev, inside, who), who)
    run = _basis(repo, env)
    computed = S.gov(["decisions", "level", "--touches", touches, "--reversible", rev, "--inside", inside,
                      "--root", repo], env=env, cwd=repo)
    assert f"level: {level}" in computed.out, f"`gov decisions level` must compute {level}: {computed.both[-300:]}"
    if ok:
        assert run.code == 0, f"a decider at or above the level must pass: {run.both[-500:]}"
        assert "DECISION_BELOW_LEVEL" not in run.both
    else:
        assert run.code != 0, "a decision below its level must be refused"
        assert "DECISION_BELOW_LEVEL" in run.both, run.both[-500:]
        assert level in run.both, f"the message must name the computed level {level}: {run.both[-500:]}"
        assert touches.split(",")[0] in run.both, f"the message must name the facts: {run.both[-500:]}"


def test_a_p2_call_written_inside_an_owners_decision_passes(tmp_path, env):
    extra = (" The CTO's calls inside it (P2, reversible, in the ticket's config): the floor defaults to 2 GB.")
    repo = _land(tmp_path, env, _entry("shared-code", "yes", "repository", "owner (chat)", extra), "owner (chat)")
    assert _basis(repo, env).code == 0
    computed = S.gov(["decisions", "level", "--touches", "shared-code", "--reversible", "yes", "--inside",
                      "repository", "--root", repo], env=env, cwd=repo)
    assert "level: P2" in computed.out, computed.both[-300:]


def test_an_entry_with_no_stated_facts_is_not_judged_and_is_listed(tmp_path, env):
    repo = _land(tmp_path, env, _entry(None, None, None, "lead"), "lead")
    run = _basis(repo, env)
    assert run.code == 0, run.both[-400:]
    assert "unstated" in run.both and "DEC-1300" in run.both, run.both[-400:]


def test_emergency_is_the_owners(tmp_path, env):
    repo = _land(tmp_path, env, _entry("own-ticket", "yes", "worktree", "CTO", "") + "- **Emergency:** yes\n", "CTO")
    run = _basis(repo, env)
    assert run.code != 0 and "DECISION_BELOW_LEVEL" in run.both and "emergency" in run.both, run.both[-400:]


def test_answer_runs_the_same_check_and_the_owner_passes_a_p1_package(case, env):
    """The sheet is the owner's decision, so a P1 package (touches spec) is written; the entry then passes the
    range check that every decision-record commit runs."""
    repo, batch, digest, cards = case
    picks = [(pid, "a", None) for pid in cards]
    run = S.answer(repo, env, S.sheet_text(batch, digest, picks))
    assert run.code == 0 and "DECISION_BELOW_LEVEL" not in run.both, run.both[-500:]
    check = _basis(repo, env)
    assert check.code == 0 and "DECISION_BELOW_LEVEL" not in check.both, check.both[-500:]
