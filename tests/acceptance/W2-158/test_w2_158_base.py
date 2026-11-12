"""S4 (a ``<base>``: portability when the change touches the kernel's roles, skills, hooks or ``.rulesync/``, or when the
base does not resolve; the tree's own ``gov links --since <base>`` after the others; both left out, named, without a
base).

Planted histories: a base commit holding the declarations, then a commit that touches one path. The tree's own ``gov
links`` is a stand-in ``src/gov/cli/main.py`` (with ``src/gov/__init__.py``, ``src/gov/cli/__init__.py`` and
``src/gov/links/__init__.py``) that records its call, writes ``.gov-runtime/links/mark`` and answers as the real
command's first line says (L7).
"""

from __future__ import annotations

import os

import pytest

import w2_158_support as support
from w2_158_support import BOUND, OUTPUT_ORDER, SLACK_S, assert_shape

KERNEL_PATHS = [
    "template/governance/kernel/skills/x/SKILL.md",
    "template/governance/kernel/roles/some-role.md",
    "template/governance/kernel/hooks/pre-tool.sh",
    ".rulesync/rules/a.md",
]
OTHER_PATHS = [
    "docs/readme.md",
    "src/other.py",
    "template/governance/kernel/roles-old/a.md",     # next to a kernel folder, not under it
    "template/governance/kernel/checks/extra.txt",   # the kernel, but not roles, skills or hooks
    ".rulesync-old/a.md",
]


def planted(tree, *, portability: str = "ok", links: str | None = None) -> str:
    """Eight families and portability declared as markers (quick), the base commit; returns the base's full sha."""
    tree.declare_all("ok", delay=0.5)
    tree.declare_family("portability", portability, delay=0.5)
    if links is not None:
        tree.plant_links(links)
    return tree.commit("the base")


@pytest.mark.parametrize("touched", KERNEL_PATHS)
def test_s4_a_change_under_the_kernels_roles_skills_hooks_or_rulesync_runs_portability(tree, touched):
    """Base, then a commit touching one kernel path: the portability marker runs (the line reads ``portability: ok``),
    exit 0, one line per family as always."""
    base = planted(tree)
    tree.commit("touch", files={touched: "changed\n"})
    outcome = tree.structural(base)
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("portability")] == "portability: ok", lines
    assert tree.ran("adapter-portability"), tree.started()


@pytest.mark.parametrize("touched", OTHER_PATHS)
def test_s4_a_change_elsewhere_skips_portability_naming_why(tree, touched):
    """Base, then a commit touching only another path: ``portability: skipped (no such change)`` and the portability
    marker never started (the other eight did)."""
    base = planted(tree)
    tree.commit("touch", files={touched: "changed\n"})
    outcome = tree.structural(base)
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("portability")] == "portability: skipped (no such change)", lines
    assert not tree.ran("adapter-portability"), "portability ran with no kernel change"
    assert len(tree.started()) == 8, tree.started()


def test_s4_a_kernel_change_in_an_earlier_commit_of_the_range_counts(tree):
    """The range is ``<base>..HEAD`` as a whole: a kernel path touched by the first of two commits after the base, the
    second touching another path, still runs portability."""
    base = planted(tree)
    tree.commit("kernel", files={"template/governance/kernel/skills/y/SKILL.md": "a\n"})
    tree.commit("elsewhere", files={"docs/b.md": "b\n"})
    assert tree.structural(base).family("portability") == "portability: ok"


def test_s4_a_change_before_the_base_does_not_count(tree):
    """A kernel change in a commit before the base is not in ``<base>..HEAD``: portability is skipped."""
    tree.commit("kernel first", files={"template/governance/kernel/hooks/h.sh": "a\n"})
    base = planted(tree)
    tree.commit("elsewhere", files={"docs/b.md": "b\n"})
    assert tree.structural(base).family("portability") == "portability: skipped (no such change)"
    assert not tree.ran("adapter-portability")


def test_s4_a_base_may_be_any_git_revision(tree):
    """``HEAD~1`` as the base: the kernel change of the last commit runs portability."""
    planted(tree)
    tree.commit("kernel", files={"template/governance/kernel/roles/r.md": "a\n"})
    outcome = tree.structural("HEAD~1")
    assert outcome.family("portability") == "portability: ok", outcome.text()


def test_s4_a_base_that_does_not_resolve_runs_portability(tree):
    """A base that names no commit: portability runs (its marker started, the line reads ok), exit 0."""
    planted(tree)
    outcome = tree.structural("no-such-revision-w2158")
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("portability")] == "portability: ok", lines
    assert tree.ran("adapter-portability")


def test_s4_without_a_base_portability_and_links_are_left_out_and_named(tree):
    """No ``<base>``: ``portability: skipped (no base given)`` and ``links: skipped (no base given)``; neither the
    portability marker nor the stand-in ``gov links`` was started, even with a kernel change at HEAD and links present."""
    planted(tree, links="clean")
    tree.commit("kernel", files={"template/governance/kernel/skills/x/SKILL.md": "a\n"})
    outcome = tree.structural()
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("portability")] == "portability: skipped (no base given)", lines
    assert lines[OUTPUT_ORDER.index("links")] == "links: skipped (no base given)", lines
    assert not tree.ran("adapter-portability") and not tree.ran("links"), tree.started()
    assert not (tree.tree / ".gov-runtime" / "links" / "mark").exists()


# --- links ------------------------------------------------------------------------------------------------------------

def test_s4_links_with_nothing_new_reads_ok_with_the_standing_count_and_ran_after_the_others(tree):
    """A tree with ``src/gov/links/`` whose own ``gov links --since <base>`` answers ``0 new ..., 4 standing`` (exit 0):
    ``links: ok (0 new since <base>, 4 standing)``; it was started as ``python3 -m gov.cli.main links --since <base>`` in
    the tree with ``PYTHONPATH=<tree>/src`` after every other check (portability included) had ended; it wrote the mark."""
    base = planted(tree, links="clean")
    tree.commit("kernel", files={"template/governance/kernel/skills/x/SKILL.md": "a\n"})
    outcome = tree.structural(base)
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("links")] == f"links: ok (0 new since {base}, 4 standing)", lines
    record = tree.record("links")
    assert record is not None, f"the tree's own gov links never ran\n{outcome.text()}"
    assert record["argv"] == ["links", "--since", base], record["argv"]
    assert record["cwd"] == os.path.realpath(tree.tree), record
    assert record["pythonpath"] == str(tree.tree / "src"), record
    assert record["dontwritebytecode"] == "1" and record["git_vars"] == [], record
    names = [n for n in tree.started() if n != "links"]
    assert len(names) == 9, f"expected the eight families and portability to have started: {names}"
    latest_end = max(tree.record(name, "end")["end"] for name in names)
    assert record["start"] >= latest_end, "gov links started before the other checks had ended"
    assert (tree.tree / ".gov-runtime" / "links" / "mark").is_file(), "the mark the stand-in writes is not there"


def test_s4_links_with_new_findings_is_a_notice_with_the_first_findings_and_exit_0(tree):
    """The stand-in answers ``2 new since <base>, 4 standing`` plus two finding lines, exit 1: the line starts
    ``links: NOTICE 2 new`` and holds the first finding line; the pass exits 0 and the last line names links."""
    base = planted(tree, links="new")
    outcome = tree.structural(base)
    lines = assert_shape(outcome, tree, notices=("links",))
    line = lines[OUTPUT_ORDER.index("links")]
    assert line.startswith("links: NOTICE 2 new"), line
    assert "UNLINKED_ID DAEO-aaaa1111 in .tickets/x.md (role engineer)" in line, line
    assert outcome.code == 0


def test_s4_a_links_that_cannot_run_is_a_notice_with_its_last_line(tree):
    """The stand-in ends with exit 2 and its reason on standard error (an unknown revision), or exits 0 with a first line of
    another form: ``links: NOTICE gov links could not run (exit <code>): <its last line>``; the pass exits 0."""
    base = planted(tree, links="badrev")
    refused = tree.structural(base)
    line = refused.family("links")
    assert line.startswith("links: NOTICE gov links could not run (exit 2): "), f"{line!r}\n{refused.text()}"
    assert "names no commit" in line, line
    (tree.marks / "links.mode").write_text("weird")
    odd = tree.structural(base)
    assert odd.family("links") == "links: NOTICE gov links could not run (exit 0): something else entirely", odd.text()


def test_s4_a_links_past_the_bound_is_not_measured(tree):
    """The stand-in sleeps past ``--timeout 2``: ``links: NOTICE not measured: ...``, never ok, exit 0, the run ends
    within two bounds + slack (the families' bound, then links')."""
    base = planted(tree, links="sleep")
    outcome = tree.structural(base)
    line = outcome.family("links")
    assert line.startswith("links: NOTICE") and "not measured" in line, f"{line!r}\n{outcome.text()}"
    assert outcome.elapsed < 2 * BOUND + SLACK_S, f"{outcome.elapsed:.1f} s"
    record = tree.record("links")
    assert record is not None and support.wait_gone(record["pid"]), "the links process outlived the bound"


def test_s4_a_tree_without_src_gov_links_reads_skipped_naming_why(tree):
    """A base given and no ``src/gov/links/`` in the tree: ``links: skipped (no gov links in this tree)``; the gov of
    this repository is not used in its place (a mark would show)."""
    base = planted(tree)   # no links planted
    tree.commit("elsewhere", files={"docs/b.md": "b\n"})
    outcome = tree.structural(base)
    lines = assert_shape(outcome, tree)
    assert lines[OUTPUT_ORDER.index("links")] == "links: skipped (no gov links in this tree)", lines
    assert not (tree.tree / ".gov-runtime" / "links" / "mark").exists()
