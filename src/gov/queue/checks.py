"""The queue's checks of a work branch before any run (W2-115b success 5 and 6), on ``<base>..<tip>``.

- **G-1, who wrote the acceptance tests** (MR-3, DEC-1050 (12)), ported from the landing tool's
  ``acceptance_authors``: a non-merge commit that changes a path under one of the acceptance places counts; a
  two-parent merge counts when its result there differs from git's own merge of its parents (``--remerge-diff``),
  an octopus merge when it differs from its first parent. A counted commit passes only with at least one ``Role:``
  trailer, each of them ``independent-test-designer`` or ``owner``.
- **The path notice** (audit 7 C-6): every path a non-merge commit changes outside the ticket's ``allowed_paths``
  and its own record places is listed; it never refuses.
- **The new ticket notice** (W2-201 fix X4, DEC-1219 (5)): each ticket file ``.tickets/<id>.md`` the branch adds (a
  path new at the tip, not an edit of one at the base) is a feature when it holds KPIs (a ``kpis.success`` line with
  its verify) and a spec (a body after its front matter); one that lacks either, or whose front matter cannot be
  read, is named in one ``NEW_TICKET_NOT_FEATURE`` notice; it never refuses.
- **The acceptance tests are there** (W2-202 A3): a ticket judged on its tests has an acceptance folder that holds a
  test and a README whose KPI map the runner of ``gov accept`` reads; else it is refused before any run.
"""

from __future__ import annotations

import subprocess
from fnmatch import fnmatch
from pathlib import Path

from gov.util.gitenv import git_env

TEST_ROLES = ("independent-test-designer", "owner")
ACCEPTANCE = "tests/acceptance/"
NO_ACCEPTANCE_TESTS = "NO_ACCEPTANCE_TESTS"
NEW_TICKET_NOT_FEATURE = "NEW_TICKET_NOT_FEATURE"
TICKETS = ".tickets/"
NO_KPIS, NO_SPEC, UNREADABLE = ("no kpis.success line with a verify", "no spec (the ticket's body is empty)",
                                "front matter unreadable")


def _git(root: Path, *args: str, ok: bool = False) -> str | None:
    done = subprocess.run(["git", "-c", "core.quotePath=false", "-C", str(root), *args], capture_output=True,
                          text=True, env=git_env(root))
    if done.returncode and ok:
        return None
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {' '.join(done.stderr.split())[:200]}")
    return done.stdout


def _under(path: str, places: list[str]) -> bool:
    return any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") for p in places if p.strip("/"))


def test_authors(root: Path, base: str, tip: str, places: list[str]) -> list[dict]:
    """The commits of ``base..tip`` that change ``places`` without the role that may: ``{"commit", "roles",
    "subject"}`` each. ``RuntimeError`` where git cannot read them (the caller refuses: fails closed)."""
    places = [p for p in places if p and p.strip("/")]
    touched = _git(root, "rev-list", "--full-history", "--no-merges", f"{base}..{tip}", "--", *places).split()
    for merge in _git(root, "rev-list", "--merges", f"{base}..{tip}").split():
        if len(_git(root, "rev-list", "--parents", "-n", "1", merge).split()) == 3:
            names = _git(root, "log", "-1", "--remerge-diff", "--format=", "--name-only", merge).splitlines()
        else:
            names = _git(root, "diff", "--name-only", f"{merge}^1", merge).splitlines()
        if any(_under(n, places) for n in names):
            touched.append(merge)
    bad = []
    for commit in touched:
        roles, _, subject = _git(root, "log", "-1", "--format=%(trailers:key=Role,valueonly,separator=%x1f)%x00%s",
                                 commit).rstrip("\n").partition("\x00")
        roles = [r.strip() for r in roles.split("\x1f") if r.strip()]
        if not roles or any(r not in TEST_ROLES for r in roles):
            bad.append({"commit": commit, "roles": roles, "subject": subject[:120]})
    return bad


def record_places(ticket: str, acceptance: str | None) -> list[str]:
    """A ticket's own record places: its ticket file, close record, checkpoints and acceptance suite."""
    own = [f".tickets/{ticket}.md", f"docs/close/{ticket}/", f"docs/checkpoints/{ticket}/"]
    return own + ([acceptance] if acceptance and acceptance.strip("/") else [])


def path_notices(root: Path, base: str, tip: str, allowed: list[str], own: list[str]) -> list[dict]:
    """``{"commit", "path"}`` for each path a non-merge commit of ``base..tip`` changes outside ``allowed`` (the
    ``allowed_paths`` grammar) and outside ``own`` (record places: a file, or a folder ending ``/``)."""
    from gov.close.select import match

    notices = []
    for commit in _git(root, "rev-list", "--no-merges", "--reverse", f"{base}..{tip}").split():
        names = _git(root, "diff-tree", "-z", "--no-commit-id", "--name-only", "-r", "--no-renames", "--root",
                     commit).split("\0")
        for path in sorted(filter(None, names)):
            if any(match(path, p) for p in allowed) or _under(path, own):
                continue
            notices.append({"commit": commit, "path": path})
    return notices


def _verified(line) -> bool:
    """A ``kpis.success`` line with its verify: the mapping form's non-blank ``verify``, or the string form's
    ``Verify:``."""
    if isinstance(line, dict):
        return isinstance(line.get("verify"), str) and bool(line["verify"].strip())
    return isinstance(line, str) and "Verify:" in line


def _missing(text: str) -> list[str]:
    """What a ticket file's text lacks to be a feature: its KPIs, its spec, or a front matter that can be read."""
    from gov.util.frontmatter import FrontmatterError, parse

    try:
        front = parse(text)
    except FrontmatterError:
        front = None
    if front is None:
        return [UNREADABLE]
    kpis = front.get("kpis")
    success = kpis.get("success") if isinstance(kpis, dict) else None
    lines = text.split("\n")
    body = "\n".join(lines[lines.index("---", 1) + 1:])
    return ([] if isinstance(success, list) and any(map(_verified, success)) else [NO_KPIS]) + \
        ([] if body.strip() else [NO_SPEC])


def ticket_notices(root: Path, base: str, tip: str) -> list[dict]:
    """``{"id", "code", "notice"}`` for each ticket file ``.tickets/<id>.md`` that ``tip`` adds against ``base`` (a
    path ``base`` does not hold) and that, read at ``tip``, is not a feature (``_missing``). ``RuntimeError`` where
    git cannot read them (the caller says so and lands anyway)."""
    names = _git(root, "diff", "-z", "--no-renames", "--name-only", "--diff-filter=A", base, tip, "--", TICKETS)
    notices = []
    for path in sorted(filter(None, names.split("\0"))):
        name = path[len(TICKETS):]
        if not path.startswith(TICKETS) or "/" in name or not name.endswith(".md") or name == ".md":
            continue
        ticket = " ".join(name[:-len(".md")].split())  # one line, whatever the file's name
        missing = _missing(_git(root, "show", f"{tip}:{path}"))
        if missing:
            notices.append({"id": ticket, "code": NEW_TICKET_NOT_FEATURE,
                            "notice": f"{NEW_TICKET_NOT_FEATURE} {ticket}: {'; '.join(missing)}"})
    return notices


def holds_tests(root: Path, rev: str, folder: str) -> bool:
    """Whether ``folder`` holds a test file (``test_*.py``, at any depth) at ``rev``."""
    names = _git(root, "ls-tree", "-r", "-z", "--name-only", rev, "--", folder.strip("/") + "/").split("\0")
    return any(fnmatch(name.rsplit("/", 1)[-1], "test_*.py") for name in names if name)


def acceptance_refusal(root: Path, revs: list[str], folder: str | None) -> tuple[str, str] | None:
    """Why a ticket cannot be judged on its acceptance tests, as ``(code, reason)``; None where it can. ``folder``
    is the path its ticket file declares; it is read at the first of ``revs`` (the branch tip, then the base) where
    it holds a test. No test at any of them is ``NO_ACCEPTANCE_TESTS``; a README the runner of ``gov accept`` would
    refuse is the runner's own code (``ACCEPT_NO_MAP``, ``ACCEPT_MAP_UNREADABLE``): fail closed, before any run."""
    from gov.accept import runner

    if not folder or not folder.strip("/"):
        return NO_ACCEPTANCE_TESTS, "its ticket file declares no acceptance folder (acceptance_tests.path)"
    folder = folder.strip("/")
    held = next((rev for rev in revs if holds_tests(root, rev, folder)), None)
    if held is None:
        return NO_ACCEPTANCE_TESTS, f"its acceptance folder {folder}/ holds no test"
    readme = _git(root, "show", f"{held}:{folder}/README.md", ok=True)
    try:
        mapping = runner.parse_map(readme) if readme is not None else {}
    except runner.Unreadable:
        return "ACCEPT_MAP_UNREADABLE", f"the README of {folder}/ has a KPI map the runner of gov accept cannot read"
    if not mapping:
        return "ACCEPT_NO_MAP", f"the README of {folder}/ maps no KPI line, so gov accept cannot judge its tests"
    return None
