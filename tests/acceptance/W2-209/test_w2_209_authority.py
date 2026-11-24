"""S3: G0, the owner's standing yes (``governance/project/release-authority.yaml``).

The file as committed in this repository says ``on`` (the owner turned it on, DEC-1223, DEC-1226, DEC-1235), with the
owner's trailer on its last commit; the planted repositories below state their own authority file and do not read it.
In the planted source, ``gov release 0.1.2 --patch`` is refused
at G0 when the file is absent, unreadable, anything but ``on``, names no decision, or was last committed without a
``Decided-by: owner...`` trailer, or is ``on`` only in the working tree; G0 is read before anything else. When G0
passes, the answer names a later gate (here G2: no suite record given). README, "S3".
"""

import pytest
import yaml

import w2_209_support as support


def test_s3_the_authority_file_committed_here_is_on_with_the_decision_and_bake_hours():
    """Repository-state kind: reads this repository's own committed file."""
    path = support.REPO_ROOT / support.AUTHORITY_REL
    assert path.is_file(), f"{support.AUTHORITY_REL} is not in this repository"
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"{support.AUTHORITY_REL} is not a map: {text!r}"
    assert "patch_releases: on" in text and data.get("patch_releases") is True, \
        f"the committed file does not say patch_releases: on: {text!r}"
    assert data.get("decision") == support.DECISION, f"the decision is not {support.DECISION}: {data}"
    assert data.get("bake_hours") == 4, f"bake_hours is not 4: {data}"
    tracked = support.git(support.REPO_ROOT, "ls-files", "--", support.AUTHORITY_REL).strip()
    assert tracked == support.AUTHORITY_REL, f"{support.AUTHORITY_REL} is not committed"
    assert not support.git(support.REPO_ROOT, "status", "--porcelain", "--", support.AUTHORITY_REL).strip(), \
        f"{support.AUTHORITY_REL} differs from its last commit"
    last = support.git(support.REPO_ROOT, "log", "-1", "--format=%(trailers:key=Decided-by,valueonly)",
                       "--", support.AUTHORITY_REL)
    assert last.strip().startswith("owner"), f"the last commit of {support.AUTHORITY_REL} has no Decided-by: owner: {last!r}"


def _plant(repo, state):
    no_trailer = (("Class", "C"), ("Role", "orchestrator"))
    if state == "absent":
        support.commit(repo, {support.AUTHORITY_REL: None}, "Remove the authority file", (("Class", "C"),))
    elif state == "off":
        pass  # as make_case(authority_on=False) planted it: off, with the owner's trailer; independent of this repository
    elif state == "maybe":
        support.turn_authority_on(repo, text=support.authority("maybe"))
    elif state == "on_without_trailer":
        support.turn_authority_on(repo, trailers=no_trailer)
    elif state == "on_decided_by_orchestrator":
        support.turn_authority_on(repo, trailers=no_trailer + (("Decided-by", "orchestrator (standing, DEC-1223)"),))
    elif state == "on_uncommitted":
        support.write(repo, {support.AUTHORITY_REL: support.authority("on")})  # the last commit has the trailer
    elif state == "unreadable":
        support.turn_authority_on(repo, text="patch_releases: [on\ndecision: DEC-1223\n")
    elif state == "no_decision":
        support.turn_authority_on(repo, text=support.authority("on", decision=None))
    elif state == "on":
        support.turn_authority_on(repo)
    else:
        raise ValueError(state)


REFUSED_STATES = ("absent", "off", "maybe", "on_without_trailer", "on_decided_by_orchestrator", "on_uncommitted",
                  "unreadable", "no_decision")


@pytest.mark.parametrize("state", REFUSED_STATES)
def test_s3_the_cut_is_refused_at_g0(base, tmp_path, home, state):
    repo = support.make_case(base, tmp_path / "repo", "clean", authority_on=False)
    _plant(repo, state)
    before = support.snapshot(repo)
    run = support.release(repo, home.path, support.X)
    support.assert_gate(support.refusal(run), "G0", state)
    assert not support.difference(before, support.snapshot(repo)), f"{state}: a refused cut changed the repository"


def test_s3_an_authority_file_on_and_committed_with_the_owner_trailer_passes_g0(base, tmp_path, home):
    repo = support.make_case(base, tmp_path / "repo", "clean", authority_on=False)
    _plant(repo, "on")
    run = support.release(repo, home.path, support.X)  # no --suite: G2 is the first red
    support.assert_gate(support.refusal(run), "G2", "G0 green, no suite record")


def test_s3_g0_is_read_first_whatever_the_later_gates_say(base, tmp_path, home):
    """The authority file off; G1 red (a contract change), G2 red (no record), G3 red (no kept run), G4 red (the
    tag exists and the tree is dirty): the answer is G0."""
    repo = support.make_case(base, tmp_path / "repo", "contract", authority_on=False)
    support.git(repo, "tag", f"v{support.X}", base.n_commit)
    support.write(repo, {"untracked.txt": "a dirty tree\n"})
    before = support.snapshot(repo)
    run = support.release(repo, home.path, support.X)
    support.assert_gate(support.refusal(run), "G0", "every gate red")
    assert not support.difference(before, support.snapshot(repo)), "a refused cut changed the repository"
