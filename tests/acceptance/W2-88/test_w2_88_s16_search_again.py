"""S16 (success-16), the ticket's "S15 Search again once in the adopted repository"; I7, B-1.1 and B-1.3 (P-W2-88-B-1, DEC-1157
(3), (12)): adoption copies, unchanged, the kernel's retrieval skill (W2-142), the discovery skill's line (W2-142) and T-0's and
T-8's "Search again once" line (W2-128). Nothing is re-worded per repository.

The copy step is A9's (the interface of run 4): stage A9 copies, byte for byte, into the adopted repository every file of Gov OS's
``template/governance/kernel/skills/retrieval/`` and ``.../discovery/`` to ``.claude/skills/retrieval/`` and ``.claude/skills/discovery/``
(same relative names), T-0 (``templates/brief.md``) and T-8 (``templates/role-cto.md``) to ``governance/kernel/templates/``, and Gov OS's
``governance/project/retrieval.yaml`` to ``governance/project/retrieval.yaml`` only when the repository tracks none (its own is kept and
judged, B-1.4). The copies are committed in A9's own record commit; they are in place before the build and the queries run; A9's record
holds ``installed: [{path, sha256, from}]`` for each file written and ``kept: [{path, sha256}]`` for a repository's own ``retrieval.yaml``;
a refused A9 leaves no copy in the tree.

A string test for "search again once", "own, different words", "not found" and "two searches" on the sources adoption copies and on the
copies a planted adoption holds. The sources: the kernel's retrieval skill, and the brief template that carries T-0's line and the CTO role
template (T-8's carrier): this head holds the lines in the retrieval skill, ``brief.md`` and ``role-cto.md`` (the source cases are green
here and stay green; they go red for W2-142 and W2-128 (``waits_on``) if the lines leave). The discovery skill's line is W2-142's S2
("searches once more in its own words before treating the question as unanswered"), merged and decided; it is not one of the four
phrases, and the case on the copied discovery skill asks that the copy hold it, unchanged (green on this head).
"""

from __future__ import annotations

import hashlib
import re

import pytest

import w2_88_support as W

PHRASES = ("search again once", "own, different words", "not found", "two searches")
KERNEL = W.REPO_ROOT / W.KERNEL_REL
SOURCES = {"the retrieval skill": KERNEL / "skills/retrieval/SKILL.md", "T-0's brief template": KERNEL / "templates/brief.md",
           "T-8's role template (CTO)": KERNEL / "templates/role-cto.md"}
COPIES = {"the retrieval skill": ".claude/skills/retrieval/SKILL.md", "T-0's brief template": "governance/kernel/templates/brief.md",
          "T-8's role template (CTO)": "governance/kernel/templates/role-cto.md"}
PLAN = W.copy_plan()                       # (path in the adopted repository, path in Gov OS), read from Gov OS's own files
DISCOVERY_COPY = ".claude/skills/discovery/SKILL.md"
DISCOVERY_LINE = "searches once more in its own words before treating the question as unanswered"   # W2-142 S2, as Gov OS ships it


def holds(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text.lower())
    return [p for p in PHRASES if p not in flat]


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_s16_guard_the_source_adoption_copies_holds_the_four_phrases(name):
    missing = holds(SOURCES[name].read_text(encoding="utf-8"))
    assert not missing, f"{name} lacks {missing} (W2-142 / W2-128's line is not on this head)"


def test_s16_the_copy_plan_names_every_file_of_the_two_skills_and_both_templates():
    """The suite's own reading of the interface (green: it judges Gov OS's files): the plan holds both skills' files and T-0, T-8."""
    paths = [p for p, _ in PLAN]
    for needed in (".claude/skills/retrieval/SKILL.md", ".claude/skills/discovery/SKILL.md", "governance/kernel/templates/brief.md",
                   "governance/kernel/templates/role-cto.md"):
        assert needed in paths, f"{needed} is not in the copy plan {paths}"
    assert all((W.REPO_ROOT / source).is_file() for _, source in PLAN)


def installed_of(record: dict) -> dict:
    """A9's ``installed`` as ``{path: entry}`` (each entry ``{path, sha256, from}``)."""
    items = record.get("installed")
    assert isinstance(items, list) and items, f"A9's record holds no `installed` list: {items!r}"
    assert all(isinstance(i, dict) and {"path", "sha256", "from"} <= set(i) for i in items), f"an `installed` item lacks path, sha256 or from: {items!r}"
    return {i["path"]: i for i in items}


@pytest.mark.parametrize("target,source", PLAN, ids=[p for p, _ in PLAN])
def test_s16_a_planted_adoption_holds_the_kernels_file_byte_for_byte_and_lists_it_installed(worlds, target, source):
    nine = worlds.a9("default")
    record = nine.record()
    copy = nine.project / target
    assert copy.is_file(), f"the adopted repository holds no {target}: stage A9 copies the kernel's {source} there (B-1.1, B-1.3)"
    original = (W.REPO_ROOT / source).read_bytes()
    assert copy.read_bytes() == original, f"{target} is not Gov OS's {source}, byte for byte"
    entry = installed_of(record).get(target)
    assert entry, f"A9's `installed` does not list {target}: {sorted(installed_of(record))}"
    assert entry["sha256"] == hashlib.sha256(original).hexdigest(), f"installed[{target}].sha256 is not the file's digest"
    assert entry["from"] == source, f"installed[{target}].from is {entry['from']!r}, Gov OS's file is {source}"


def test_s16_the_copies_are_committed_in_a9s_own_record_commit_and_the_tree_is_clean(worlds):
    nine = worlds.a9("default")
    nine.need_a9()
    record_path = nine.run.result.get("record")
    assert isinstance(record_path, str), f"A9 names no record: {nine.run.describe()}"
    assert W.git(nine.project, "status", "--porcelain") == "", "A9 left the tree dirty: a copy is written and not committed"
    changed = set(W.git(nine.project, "show", "--name-only", "--format=", "HEAD").split())
    wanted = {target for target, _ in PLAN}
    assert record_path in changed, f"HEAD (A9's commit) does not hold the record {record_path}: {sorted(changed)}"
    assert wanted <= changed, f"the copies are not in A9's own record commit (one commit); missing from HEAD: {sorted(wanted - changed)}"
    tracked = set(W.git(nine.project, "ls-files").splitlines())
    assert wanted <= tracked, f"copies untracked after A9: {sorted(wanted - tracked)}"


def test_s16_the_copies_are_in_place_before_the_build_runs(worlds):
    """B-1.1: the files are in place before the build and the scale and measure queries run: the child sees them at the entry of
    ``gov.rebuild.command.run`` (A9's build)."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "fork-copies-first")
    wanted = [target for target, _ in PLAN]
    run, done = W.run_a9_child(adoption, adoption.box.base / "copies-out", watch=wanted)
    W.assert_offered(run, "A9")
    seen = W.stderr_json(done, "copies-at-build:")
    assert seen is not None, f"the plant did not take: A9 did not call gov.rebuild.command.run in this process\n{run.describe()}"
    assert sorted(seen) == sorted(wanted), f"files absent when the build began: {sorted(set(wanted) - set(seen))}"


@pytest.mark.parametrize("name", sorted(COPIES))
def test_s16_a_planted_adoption_holds_the_four_phrases_in_the_copy(worlds, name):
    nine = worlds.a9("default")
    nine.need_a9()
    copy = nine.project / COPIES[name]
    assert copy.is_file(), f"the planted adoption holds no {COPIES[name]} ({name}): no stage copies it (B-1.1, B-1.3)"
    assert copy.read_bytes() == SOURCES[name].read_bytes(), f"{COPIES[name]} is not {name} as Gov OS ships it, byte for byte"
    assert not holds(copy.read_text(encoding="utf-8")), f"{COPIES[name]} lacks one of {PHRASES}"


def test_s16_a_planted_adoption_holds_the_discovery_skills_search_again_line(worlds):
    """W2-142's S2 (DAEO-qskx, closed and merged), copied unchanged: the discovery skill's line as Gov OS ships it ("the practitioner
    searches once more in its own words before treating the question as unanswered", the retrieval skill's step 7; DEC-1092 (1)) is in
    the planted adoption's copy, which is Gov OS's discovery skill byte for byte. The four phrases are the retrieval skill's and T-0's,
    not this skill's; the KPI asks only that this line be copied unchanged. Green on the head (the copy step is built and the line
    is in Gov OS's skill); red if the copy is absent, differs from Gov OS's skill, or the skill's line is gone."""
    nine = worlds.a9("default")
    nine.need_a9()
    copy = nine.project / DISCOVERY_COPY
    assert copy.is_file(), f"the planted adoption holds no {DISCOVERY_COPY}: no stage copies the discovery skill (B-1.1)"
    assert copy.read_bytes() == (KERNEL / "skills/discovery/SKILL.md").read_bytes(), f"{DISCOVERY_COPY} is not Gov OS's discovery skill"
    flat = re.sub(r"\s+", " ", copy.read_text(encoding="utf-8").lower())
    assert DISCOVERY_LINE in flat, f"the copied discovery skill lacks W2-142's S2 line ({DISCOVERY_LINE!r})"


# ---- B-1.3: retrieval.yaml, installed only where the repository tracks none -----------------------------------------

def test_s16_a_repository_with_no_retrieval_yaml_gets_gov_oss_s_and_a9_is_ok_with_no_decision(worlds):
    """B-1.3 (and B-1.4): no tracked ``retrieval.yaml``: Gov OS's own is installed byte for byte, listed in ``installed`` with its
    ``from``, ``kept`` is empty, and the standard is judged on the installed copy: no pool departure, so A9 is ok with no ``--decision``."""
    nine = worlds.a9("no-retrieval", plant_options={"no_retrieval": True})
    nine.need_chain()                  # the plant tracks no retrieval.yaml: A0..A8 must reach A8 without it
    record = nine.record()
    path = nine.project / W.RETRIEVAL_REL
    assert path.is_file(), f"no {W.RETRIEVAL_REL} was installed in a repository that tracks none"
    assert path.read_bytes() == W.RETRIEVAL_SRC.read_bytes(), f"the installed {W.RETRIEVAL_REL} is not Gov OS's, byte for byte"
    entry = installed_of(record).get(W.RETRIEVAL_REL)
    assert entry, f"`installed` does not list {W.RETRIEVAL_REL}: {sorted(installed_of(record))}"
    assert entry["sha256"] == W.sha256_file(W.RETRIEVAL_SRC) and entry["from"] == W.RETRIEVAL_REL, entry
    assert record.get("kept") == [], f"`kept` is {record.get('kept')!r}: the repository kept no retrieval.yaml of its own"
    standard = record["standard"]
    assert standard["departures"] == [], f"a fresh adoption with no retrieval.yaml departs from the standard: {standard['departures']}"
    assert standard["retrieval_yaml_sha256"] == W.sha256_file(W.RETRIEVAL_SRC), "the standard is not judged on the installed copy"
    assert W.git(nine.project, "show", f"HEAD:{W.RETRIEVAL_REL}").encode() == W.RETRIEVAL_SRC.read_bytes(), "the copy is not committed"


def test_s16_a_repositorys_own_tracked_retrieval_yaml_is_kept_unchanged_and_listed(worlds):
    """B-1.3: a repository's own tracked ``retrieval.yaml`` is kept as it is (bytes unchanged), listed in ``kept`` with its sha256,
    not in ``installed``, and judged (here it holds the standard's settings, so no departure)."""
    own = W.RETRIEVAL_SRC.read_text(encoding="utf-8") + "# the repository's own comment, kept as it is\n"
    nine = worlds.a9("own-retrieval", retrieval=own)
    record = nine.record()
    path = nine.project / W.RETRIEVAL_REL
    assert path.read_bytes() == own.encode("utf-8"), "the repository's own retrieval.yaml was changed"
    wanted = hashlib.sha256(own.encode("utf-8")).hexdigest()
    kept = record.get("kept")
    assert isinstance(kept, list) and [k.get("path") for k in kept] == [W.RETRIEVAL_REL], f"`kept` is {kept!r}"
    assert kept[0].get("sha256") == wanted, f"kept[0].sha256 is {kept[0].get('sha256')!r}, the file's digest is {wanted}"
    assert W.RETRIEVAL_REL not in installed_of(record), "a repository's own retrieval.yaml is listed as installed"
    assert record["standard"]["retrieval_yaml_sha256"] == wanted and record["standard"]["departures"] == []


def test_s16_the_default_planted_adoption_keeps_its_tracked_retrieval_yaml(worlds):
    """The planted harbour tracks a retrieval.yaml (a copy of Gov OS's): it is the repository's own, so it is kept, never installed."""
    nine = worlds.a9("default")
    record = nine.record()
    wanted = W.sha256_file(W.RETRIEVAL_SRC)
    assert [k.get("path") for k in (record.get("kept") or [])] == [W.RETRIEVAL_REL], f"`kept` is {record.get('kept')!r}"
    assert record["kept"][0].get("sha256") == wanted
    assert W.RETRIEVAL_REL not in installed_of(record)


def test_s16_a_refused_a9_leaves_no_copy_in_the_tree(worlds):
    """B-1.1: a refusal of A9 writes nothing in the repository's tree: a departure with no decision is refused, and no skill,
    template or retrieval copy is left, the tree is clean and HEAD is where it was."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "fork-refused-copies", W.retrieval_variant("pool-depth"))
    head = W.head(adoption.project)
    run = adoption.a9(adoption.box.base / "refused-out")
    W.assert_refused(run, "STANDARD_DEPARTURE", "A9 with a pool departure and no decision id")
    leftovers = [target for target, _ in PLAN if (adoption.project / target).exists()]
    assert not leftovers, f"a refused A9 left copies in the tree: {leftovers}"
    assert not (adoption.project / ".claude").exists(), "a refused A9 left a .claude/ folder"
    assert W.git(adoption.project, "status", "--porcelain") == "", "a refused A9 left the tree dirty"
    assert W.head(adoption.project) == head, "a refused A9 committed"
