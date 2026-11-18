"""S4: `gov decisions basis` refuses a new rule without a basis line that names an incident."""

from __future__ import annotations

import re

import w2_198_support as s
from w2_198_support import dec

OLD = dec(1, "Standing practice: leads check merges", "- **Decision:** leads check every merge.")
OLD_EDITED = dec(1, "Standing practice: leads check merges", "- **Decision:** leads check every merge and tag.")
NEW = [
    dec(2, "Every lead runs the merge check before landing", "- **Decision:** the lead runs the merge check.",
        "- **Basis:** the incident of 2026-11-03,", "  when a lead landed a branch whose tests never ran."),
    dec(3, "A gate on bundle size", "- **Decision:** a gate refuses bundles over 1 GiB.",
        "- **Basis:** docs/incidents/lost-branch.md"),
    dec(4, "Role separation rules for reviewers", "- **Decision:** reviewers never write code.",
        "- **Basis:** question 1 (role separation)"),
    dec(5, "Standing review of the weekly digest", "- **Decision:** the digest is read each Monday.", dash="–"),
    dec(6, "Checked links in every record", "- **Decision:** every link is followed once.",
        "- **Basis:** see docs/incidents/missing-record.md", dash="-"),
    dec(7, "Rename the release folder", "- **Decision:** the release folder is renamed to releases."),
    dec(8, "The practice notes move to the wiki", "- **Adds:** no rule", "- **Decision:** the notes move."),
    dec(9, "Move the archive", "- **Decision:** the archive moves to docs/archive.",
        "- **Basis:** the rule of tidy folders", "- **Governing sources:** the standing practice of DEC-1"),
]
FAILING = {"DEC-4": "basis names no incident", "DEC-5": "no basis line", "DEC-6": "basis names no incident"}
NEW_IDS = {f"DEC-{n}" for n in range(2, 10)}
RULES = {"DEC-2", "DEC-3", "DEC-4", "DEC-5", "DEC-6"}
PASSING_LATER = [
    dec(10, "Gate the landing on the merge queue", "- **Decision:** the landing waits for the queue.",
        "- **Basis:** on 2026-11-10 two leads landed the same branch twice in one hour."),
    dec(11, "Rename the digest", "- **Decision:** the digest is renamed."),
]
REGISTER = "docs/DECISION_REGISTER.md"


def _repo(tmp_path, env):
    """A, B (adds DEC-2 to DEC-9, edits DEC-1), C (adds DEC-10, DEC-11). Returns (repo, A, B, C)."""
    repo = tmp_path / "proj"
    repo.mkdir()
    s.git("init", "-q", cwd=repo, env=env)
    a = s.commit(repo, env, "register", {REGISTER: s.REGISTER_HEAD + OLD,
                                         "docs/incidents/lost-branch.md": "# A branch was lost\n"})
    b = s.commit(repo, env, "new entries", {REGISTER: s.REGISTER_HEAD + OLD_EDITED + "".join(NEW)})
    c = s.commit(repo, env, "more entries", {REGISTER: s.REGISTER_HEAD + OLD_EDITED + "".join(NEW + PASSING_LATER)})
    return repo, a, b, c


def _verdicts(run) -> dict:
    result = run.envelope()["result"]
    return {item["id"]: item for item in result["entries"]}


def _fails(item) -> bool:
    return str(item["verdict"]).lower().startswith("fail")


def test_s4_the_range_names_exactly_the_new_rule_entries_without_an_incident(tmp_path, env):
    repo, a, b, _ = _repo(tmp_path, env)
    run = s.gov(["decisions", "basis", "--range", f"{a}..{b}", "--json"], env=env, cwd=repo)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    entries = _verdicts(run)
    assert set(entries) == NEW_IDS, f"entries {sorted(entries)}"
    assert {i for i, item in entries.items() if _fails(item)} == set(FAILING)
    for ident, reason in FAILING.items():
        assert reason in str(entries[ident]["reason"]), (ident, entries[ident])
    assert {i for i, item in entries.items() if item["rule"]} == RULES
    for ident in NEW_IDS - set(FAILING):
        assert str(entries[ident]["verdict"]).lower().startswith("pass"), entries[ident]


def test_s4_text_form_is_one_line_an_entry_naming_each_failure_and_its_reason(tmp_path, env):
    repo, a, b, _ = _repo(tmp_path, env)
    run = s.gov(["decisions", "basis", "--range", f"{a}..{b}"], env=env, cwd=repo)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    assert "BASIS_MISSING" in run.both
    lines = run.text_lines()
    for ident in NEW_IDS:
        mine = [line for line in lines if re.search(rf"{ident}(?!\d)", line)]
        assert len(mine) == 1, f"{ident}: {len(mine)} lines: {mine}"
        if ident in FAILING:
            assert FAILING[ident] in mine[0], mine[0]
        else:
            assert "no basis line" not in mine[0] and "names no incident" not in mine[0], mine[0]
    assert not any(re.search(r"DEC-1(?!\d)", line) for line in lines), "DEC-1, not new in the range, is named"


def test_s4_a_range_of_passing_entries_exits_0_and_the_default_is_head(tmp_path, env):
    repo, _, b, c = _repo(tmp_path, env)
    ranged = s.gov(["decisions", "basis", "--range", f"{b}..{c}", "--json"], env=env, cwd=repo)
    assert ranged.code == 0, f"exit {ranged.code}, not 0: {ranged.both[-600:]}"
    assert set(_verdicts(ranged)) == {"DEC-10", "DEC-11"}
    default = s.gov(["decisions", "basis", "--json"], env=env, cwd=repo)
    assert default.code == 0, f"exit {default.code}, not 0: {default.both[-600:]}"
    assert set(_verdicts(default)) == {"DEC-10", "DEC-11"}


def test_s4_an_uncommitted_edit_to_the_register_changes_no_answer(tmp_path, env):
    repo, a, b, c = _repo(tmp_path, env)
    runs = [["decisions", "basis", "--range", f"{a}..{b}", "--json"],
            ["decisions", "basis", "--range", f"{b}..{c}", "--json"]]
    before = [s.gov(args, env=env, cwd=repo) for args in runs]
    assert [r.code for r in before] == [1, 0], [r.both[-300:] for r in before]
    text = (repo / REGISTER).read_text(encoding="utf-8")
    text = text.replace("- **Basis:** question 1 (role separation)\n", "- **Basis:** on 2026-11-01 a lead lost "
                        "a whole day of work to a stale branch.\n")
    text += dec(99, "A new gate on pushes", "- **Decision:** pushes are gated.")
    (repo / REGISTER).write_text(text, encoding="utf-8")
    after = [s.gov(args, env=env, cwd=repo) for args in runs]
    for one, two in zip(before, after):
        assert two.code == one.code
        assert two.envelope()["result"]["entries"] == one.envelope()["result"]["entries"]


def test_s4_register_option_reads_another_file(tmp_path, env):
    repo = tmp_path / "proj"
    repo.mkdir()
    s.git("init", "-q", cwd=repo, env=env)
    other = "governance/RULES_REGISTER.md"
    s.commit(repo, env, "registers", {REGISTER: s.REGISTER_HEAD, other: s.REGISTER_HEAD})
    s.commit(repo, env, "entries", {
        REGISTER: s.REGISTER_HEAD + PASSING_LATER[0],
        other: s.REGISTER_HEAD + dec(30, "Standing rule on reviews", "- **Decision:** reviews are read twice."),
    })
    default = s.gov(["decisions", "basis", "--json"], env=env, cwd=repo)
    assert default.code == 0, f"exit {default.code}, not 0: {default.both[-600:]}"
    assert set(_verdicts(default)) == {"DEC-10"}
    run = s.gov(["decisions", "basis", "--register", other, "--json"], env=env, cwd=repo)
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    entries = _verdicts(run)
    assert set(entries) == {"DEC-30"} and "no basis line" in str(entries["DEC-30"]["reason"])
