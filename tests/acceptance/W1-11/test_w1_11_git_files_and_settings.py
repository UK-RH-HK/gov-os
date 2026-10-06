"""KPI success 2 [CAP-01.b, CAP-21.a], batch 6: the approval fact is read from the repository's real commits,
whatever a file under ``.git/`` or a git setting makes git report. Added after implementation, from two behaviours
a review described (DEC-136, DEC-413): in each the check returned no finding.

- **A file under ``.git/`` that changes the parents git reports changes nothing** (as a replace ref changes
  nothing, DEC-387). The merge rule (DEC-398) judges a merge against the merge base of its parents. A grafts
  file, a shallow file written by hand and a commit-graph file each make git name other parents for a commit
  than the commit itself names, and so another merge base. No object is added, removed or rewritten.
- **A git setting changes nothing.** The fact is the text ``Role: owner`` in the final trailer block of the
  commit's own message (DEC-360, DEC-182). ``trailer.separators`` and ``trailer.<name>.key`` make git print
  another line of the message as a ``Role`` trailer; the setting may lie in the repository's ``.git/config`` or
  in the ``.gitconfig`` of the ``HOME`` the check runs with.

Every case runs the check without loading the store, as the replace ref case does: what ``gov.store.load`` reads
with such a file or setting in place is not this ticket's.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)
NOTES = "# Notes\n\nNo frontmatter here.\n"


# --------------------------------------------------------------------------
# A file under `.git/` that changes the parents git reports
# --------------------------------------------------------------------------

def two_children(project, merged_by):
    """The owner's commit A adds the decision ACTIVE. D, a child of A, demotes it to PROPOSED. K, another child of
    A, by an agent, edits the body and keeps ACTIVE. M, a merge by ``merged_by`` with the parents D and K, keeps
    K's file and is HEAD. The merge base of D and K is A, so D changed the status since the merge base and M is
    the change that sets the decision ACTIVE again: its own trailer is the fact."""
    project.put(support.CLEAN, who=OWNER)
    a = project.put({PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    d = project.put({PATH: decision(ADR, "PROPOSED")}, who=AGENT)
    support.git(project.root, "checkout", "-q", "-b", "work", a)
    k = project.put({PATH: decision(ADR, "ACTIVE", body="Another body.")}, who=AGENT)
    project.switch("main")
    m = project.merge_with("work", who=merged_by, take={PATH: k})
    assert support.real_parents(project.root, d) == [a] and support.real_parents(project.root, k) == [a]
    assert_the_merge_is_head(project, m, d, k, base=a)
    return {"A": a, "D": d, "K": k, "M": m}


def through_a_side_line(project, merged_by):
    """As ``two_children``, with a second way from D down to the first commit, for a file that hides one parent.

    The owner's first commit P holds the decision PROPOSED; the owner's A, its child, sets it ACTIVE. S is a child
    of P and N a child of A, each an agent's note. D is an agent's merge of N and S that demotes the decision to
    PROPOSED. K, a child of A, by an agent, edits the body and keeps ACTIVE. M, a merge by ``merged_by`` with the
    parents D and K, keeps K's file and is HEAD. The merge base of D and K is A. Were N cut off from A, the only
    commit D and K would still share is P, which holds the decision PROPOSED as D does."""
    p = project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")}, who=OWNER)
    project.switch("side", new=True)
    s = project.put({"notes/side.md": NOTES}, who=AGENT)
    project.switch("main")
    a = project.put({PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    project.switch("work", new=True)
    k = project.put({PATH: decision(ADR, "ACTIVE", body="Another body.")}, who=AGENT)
    project.switch("main")
    n = project.put({"notes/main.md": NOTES}, who=AGENT)
    d = project.merge_with("side", who=AGENT, files={PATH: decision(ADR, "PROPOSED")})
    m = project.merge_with("work", who=merged_by, take={PATH: k})
    assert support.real_parents(project.root, n) == [a] and support.real_parents(project.root, d) == [n, s]
    assert_the_merge_is_head(project, m, d, k, base=a)
    return {"P": p, "A": a, "N": n, "D": d, "K": k, "M": m}


def assert_the_merge_is_head(project, m, d, k, base):
    root = project.root
    assert support.git(root, "rev-parse", "HEAD").strip() == m, "the fixture's merge is not HEAD"
    assert support.real_parents(root, m) == [d, k], "the fixture's merge has other parents"
    assert support.merge_bases(root, d, k) == [base], "the fixture's merge has another merge base"
    assert support.git(root, "rev-parse", f"{m}:{PATH}") == support.git(root, "rev-parse", f"{k}:{PATH}"), \
        "the fixture's merge does not keep the file of K"


def a_shallow_file(project, commits):
    """`.git/shallow`, written by hand, names N: git reports N with no parent. No object is missing."""
    path = support.write_shallow(project.root, commits["N"])
    assert support.parents_of(project.root, commits["N"]) == [], "the fixture's shallow file is not in effect"
    return path


def a_commit_graph(project, commits):
    """`.git/objects/info/commit-graph` names P, not A, as the parent of N."""
    path = support.write_commit_graph(project.root, commits["N"], commits["P"])
    without = support.git(project.root, "-c", "core.commitGraph=false", "merge-base", "--all", commits["D"],
                          commits["K"]).split()
    assert without == [commits["A"]], "the fixture's merge base without the commit-graph is not A"
    return path


def test_a_grafts_file_does_not_turn_a_flagged_agent_merge_into_a_pass(api, project):
    """One line in `.git/info/grafts` gives K the parent D. Git then reports D as the merge base of D and K, and D
    holds the decision as D does: nothing seems to have changed since. The commits say otherwise."""
    commits = two_children(project, merged_by=AGENT)
    support.assert_flagged(api.check_only(project.root), support.ACTIVE_UNAPPROVED, [ADR], [PATH])

    grafts = support.write_grafts(project.root, commits["K"], [commits["D"]])
    assert grafts.read_text(encoding="ascii") == f"{commits['K']} {commits['D']}\n"
    assert support.parents_of(project.root, commits["K"]) == [commits["D"]], "the fixture's graft is not in effect"
    assert support.merge_bases(project.root, commits["D"], commits["K"]) == [commits["D"]]
    assert support.real_parents(project.root, commits["K"]) == [commits["A"]], "the fixture's commit K was rewritten"
    assert support.git(project.root, "rev-parse", "HEAD").strip() == commits["M"]

    support.assert_flagged(api.check_only(project.root), support.ACTIVE_UNAPPROVED, [ADR], [PATH])


@pytest.mark.parametrize("hide", [a_shallow_file, a_commit_graph], ids=["a shallow file written by hand",
                                                                        "a commit-graph that names another parent"])
def test_a_file_that_hides_a_parent_does_not_turn_a_flagged_agent_merge_into_a_pass(api, project, hide):
    """The file cuts N off from A. Git then reports P as the merge base of D and K, and P holds the decision
    PROPOSED as D does: nothing seems to have changed since. The check gives the finding or raises `GovError`
    (a history it cannot trust, as DEC-387 accepts for a shallow clone); it never passes."""
    commits = through_a_side_line(project, merged_by=AGENT)
    support.assert_flagged(api.check_only(project.root), support.ACTIVE_UNAPPROVED, [ADR], [PATH])

    assert hide(project, commits).is_file()
    assert support.merge_bases(project.root, commits["D"], commits["K"]) == [commits["P"]], \
        "the fixture's file does not change the merge base git reports"
    assert support.real_parents(project.root, commits["N"]) == [commits["A"]], "the fixture's commit N was rewritten"
    assert support.git(project.root, "rev-parse", "HEAD").strip() == commits["M"]
    assert support.absent_objects(project.root) == [], "the fixture's repository lacks an object"

    kind, result = support.outcome(api, project.root)
    if kind == "findings":
        support.assert_flagged(result, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_an_owner_merge_passes_with_a_grafts_file_in_place(api, project):
    """The control: the same history, the merge by the owner. Its own `Role: owner` trailer is the fact, with or
    without the grafts file: a grafts file is no finding and no error."""
    commits = two_children(project, merged_by=OWNER)
    support.write_grafts(project.root, commits["K"], [commits["D"]])
    assert support.merge_bases(project.root, commits["D"], commits["K"]) == [commits["D"]], \
        "the fixture's graft is not in effect"
    assert api.check_only(project.root) == []


def test_an_owner_merge_passes_with_a_commit_graph_git_wrote(api, project):
    """The control: the same history, the merge by the owner, and the commit-graph file as git itself writes it
    (`git gc` writes one in an ordinary repository). Such a file is no finding and no error."""
    commits = through_a_side_line(project, merged_by=OWNER)
    assert support.write_commit_graph(project.root).is_file()
    assert support.merge_bases(project.root, commits["D"], commits["K"]) == [commits["A"]]
    assert api.check_only(project.root) == []


# --------------------------------------------------------------------------
# A git setting that changes how a commit's trailers are printed
# --------------------------------------------------------------------------

SEPARATORS = ("Role# owner", "trailer.separators", ":#")  # `#` separates a trailer's key from its value too
KEY_ALIAS = ("Approved: owner", "trailer.approved.key", "Role")  # an `Approved` trailer is printed as `Role`
ROLE_AS_GIT_PRINTS_IT = "--format=%(trailers:key=Role,valueonly,unfold)"


def an_agent_adds_the_decision(project, last_line):
    """An agent's commit adds the decision ACTIVE; ``last_line`` is the last line of its message, in the final
    trailer block. The commit is dated after 2026-10-03, so only that block is read (DEC-182)."""
    project.put(support.CLEAN, who=OWNER)
    project.write(PATH, decision(ADR, "ACTIVE"))
    commit = project.commit(f"Add a decision\n\nTask: PROJ-aaaa\n{last_line}", who=AGENT, trailers=())
    message = support.git(project.root, "log", "-1", "--format=%B", commit)
    assert message.rstrip("\n").splitlines()[-1] == last_line, "the fixture's message does not end with the line"
    assert "role:" not in message.lower(), "the fixture's message holds a `Role:` line"
    assert support.git(project.root, "log", "-1", ROLE_AS_GIT_PRINTS_IT, commit).strip() == "", \
        "git prints a Role trailer for the fixture's commit before any setting"
    return commit


def set_in_the_repository(project, home, key, value):
    """`git config <key> <value>` in the repository: the setting lands in `.git/config`."""
    support.git(project.root, "config", key, value)
    assert support.git(project.root, "config", "--local", "--get", key).rstrip("\n") == value


def set_for_the_user(project, home, key, value):
    """The setting lies in the `.gitconfig` of the ``HOME`` the check runs with; `.git/config` is untouched."""
    section, name = key.rsplit(".", 1)
    section, _, sub = section.partition(".")
    head = f'[{section} "{sub}"]' if sub else f"[{section}]"
    (home / ".gitconfig").write_text(f'{head}\n\t{name} = "{value}"\n', encoding="utf-8")
    assert support.git(project.root, "config", "--local", "--get", key, check=False) == ""


@pytest.mark.parametrize("line, key, value, where", [
    (*SEPARATORS, set_in_the_repository),
    (*SEPARATORS, set_for_the_user),
    (*KEY_ALIAS, set_in_the_repository),
], ids=["trailer.separators in the repository", "trailer.separators in the user's configuration",
        "trailer.<name>.key in the repository"])
def test_a_git_setting_does_not_make_another_line_the_owner_trailer(tmp_path, project, line, key, value, where):
    """With the setting git prints `owner` as the commit's `Role` trailer. The message holds no `Role: owner`."""
    commit = an_agent_adds_the_decision(project, line)
    api = support.Api(tmp_path / "api")  # this case's own HOME for the check, empty so far
    home = api.workdir / "home"
    support.assert_flagged(api.check_only(project.root), support.ACTIVE_UNAPPROVED, [ADR], [PATH])

    where(project, home, key, value)
    assert support.git_as_user(project.root, home, "log", "-1", ROLE_AS_GIT_PRINTS_IT, commit).strip() == "owner", \
        "the fixture's setting is not in effect"
    assert "role:" not in support.git(project.root, "cat-file", "commit", commit).lower(), \
        "the fixture's commit was rewritten"

    support.assert_flagged(api.check_only(project.root), support.ACTIVE_UNAPPROVED, [ADR], [PATH])


@pytest.mark.parametrize("line, key, value", [SEPARATORS, KEY_ALIAS],
                         ids=["trailer.separators", "trailer.<name>.key"])
def test_the_owner_trailer_still_approves_with_the_setting_in_place(api, project, line, key, value):
    """The control: the owner's commit adds the decision ACTIVE with the trailer `Role: owner`, and the setting
    lies in the repository. The setting is no finding and no error."""
    project.put(support.CLEAN, who=OWNER)
    commit = project.put({PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    assert support.git(project.root, "log", "-1", "--format=%B", commit).rstrip("\n").splitlines()[-1] == "Role: owner"
    set_in_the_repository(project, None, key, value)
    assert api.check_only(project.root) == []
