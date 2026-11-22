"""The patch rule of a release (W2-209, RELEASE-ON-BEHALF "What a patch release is"; DEC-1223 RB-7).

A release is a **patch release** when five rules hold, each read by code from the last release N to the release
commit C, never by judgement:

- P1 version: ``pyproject.toml`` at C is N's version with only the last number raised and no pre-release part;
- P2 owner's text: no path changed under ``docs/contract``, ``docs/charter`` or ``docs/emergency-2/EMERGENCY-2.md``;
- P3 no feature: no ticket closed at C that was not closed at N, and every non-merge commit N..C that touches
  ``src/gov`` or ``template`` carries a ``Fix:`` trailer with a ``Task:`` ticket closed at N, or ``Class: Q``, or
  ``Class: C``;
- P4 no new command: the command names the CLI knows are the same at N and at C;
- P5 no new record kind: no file added to or removed from ``template/governance/kernel/schemas``.

Anything else is a **bigger** release, which only the owner builds (``gov release``, DEC-772). ``evaluate`` reads git
objects only and writes nothing. A rule whose input cannot be read fails (it never passes).
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

from gov.release import RELEASES_REL, SEMVER, ReleaseError, _blobs

RULES = ("P1", "P2", "P3", "P4", "P5")
P2_PATHS = ("docs/contract", "docs/charter", "docs/emergency-2/EMERGENCY-2.md")
SCHEMAS = "template/governance/kernel/schemas"
CODE_PATHS = ("src/gov", "template")
_TRAILER = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):[ \t]*(.*?)[ \t]*$")


class NoRelease(ReleaseError):
    """No release N to read the range from."""


def _run(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if done.returncode:
        raise ReleaseError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def trailers(message: str) -> dict[str, list[str]]:
    """The trailers of a commit message: the ``Key: value`` lines of its last paragraph (a message of one paragraph
    has its subject skipped), by key, in order. A line in the body's prose is no trailer."""
    paragraphs = [p for p in re.split(r"\n[ \t]*\n", message.strip("\n")) if p.strip()]
    if not paragraphs:
        return {}
    lines = paragraphs[-1].splitlines()
    if len(paragraphs) == 1:
        lines = lines[1:]
    found: dict[str, list[str]] = {}
    for line in lines:
        match = _TRAILER.match(line)
        if match:
            found.setdefault(match.group(1), []).append(match.group(2))
    return found


def _version_tuple(version: str):
    match = SEMVER.fullmatch(version)
    return tuple(int(part) for part in match.groups()[:3]) if match else None


def last_release(repo: Path, commit: str) -> tuple[str, str]:
    """N: the highest version ``V`` (MAJOR.MINOR.PATCH, no pre-release) with a tag ``v<V>`` whose record
    ``docs/releases/<V>/manifest.json`` is at ``commit``; its version and the commit its tag names."""
    found = []
    for tag in _run(repo, "for-each-ref", "--format=%(refname:strip=2)", "refs/tags").split():
        match = SEMVER.fullmatch(tag[1:]) if tag.startswith("v") else None
        if not match or match.group(4) or match.group(5):
            continue
        version = tag[1:]
        record = subprocess.run(["git", "-C", str(repo), "cat-file", "-e",
                                 f"{commit}:{RELEASES_REL}/{version}/manifest.json"], capture_output=True)
        if record.returncode:
            continue
        at = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}"],
                            capture_output=True, text=True)
        if at.returncode or not at.stdout.strip():
            continue
        found.append((_version_tuple(version), version, at.stdout.strip()))
    if not found:
        raise NoRelease(f"no release to read the range from: no tag v<version> with a record under "
                        f"{RELEASES_REL}/ at {commit[:12]}")
    _, version, at = max(found)
    return version, at


def _pyproject_version(repo: Path, commit: str) -> str | None:
    try:
        text = _blobs(repo, commit, "pyproject.toml")["pyproject.toml"].decode("utf-8")
        value = tomllib.loads(text)["project"]["version"]
    except (ReleaseError, KeyError, ValueError, UnicodeDecodeError, TypeError):
        return None
    return value if isinstance(value, str) else None


def _p1(repo: Path, n: str, c: str) -> dict:
    found = _pyproject_version(repo, c)
    if found is None:
        return {"pass": False, "detail": "pyproject.toml at the release commit declares no readable project version"}
    match, old = SEMVER.fullmatch(found), _version_tuple(n)
    if not match:
        return {"pass": False, "detail": f"version {found} is not a semantic version"}
    if match.group(4) or match.group(5):
        return {"pass": False, "detail": f"version {found} has a pre-release or build part"}
    now = tuple(int(p) for p in match.groups()[:3])
    if now[:2] != old[:2] or now[2] <= old[2]:
        return {"pass": False, "detail": f"version {found} is not {n} with only the last number raised"}
    return {"pass": True, "detail": f"version {found} is {n} with the last number raised"}


def _p2(repo: Path, n_commit: str, c: str) -> dict:
    names = [line for line in _run(repo, "diff", "--name-only", "--no-renames", n_commit, c, "--", *P2_PATHS).splitlines()
             if line]
    if names:
        return {"pass": False, "detail": f"changed since the last release: {', '.join(names[:20])}"
                                         f"{' and more' if len(names) > 20 else ''}"}
    return {"pass": True, "detail": "no path of the Contract, the Charter or EMERGENCY-2 changed"}


def closed_tickets(repo: Path, commit: str) -> dict[str, set[str]]:
    """The tickets closed at ``commit``: ``{id: {the names a Task: trailer may give it}}``."""
    try:
        blobs = _blobs(repo, commit, ".tickets")
    except ReleaseError:
        return {}
    closed = {}
    for rel, data in blobs.items():
        if rel.count("/") != 1 or not rel.endswith(".md"):
            continue
        text = data.decode("utf-8", "replace")
        if not text.startswith("---"):
            continue
        front = text.split("\n---", 1)[0].splitlines()[1:]
        fields = {}
        for line in front:
            key, sep, value = line.partition(":")
            if sep and key and not key[0].isspace():
                fields.setdefault(key.strip(), value.strip().strip("'\""))
        if fields.get("status") == "closed" and fields.get("id"):
            closed[fields["id"]] = {fields[k] for k in ("id", "wbs_id", "external-ref") if fields.get(k)}
    return closed


def _p3(repo: Path, n_commit: str, c: str) -> dict:
    before, now = closed_tickets(repo, n_commit), closed_tickets(repo, c)
    newly = sorted(set(now) - set(before))
    known = set().union(*before.values()) if before else set()
    bad = []
    log = _run(repo, "log", "--no-merges", "--full-history", "--format=%H%x1f%B%x1e", f"{n_commit}..{c}", "--",
               *CODE_PATHS)
    for entry in log.split("\x1e"):
        sha, _, message = entry.strip("\n").partition("\x1f")
        if not sha.strip():
            continue
        found = trailers(message)
        klass = (found.get("Class") or [""])[-1].split()[:1]
        if klass and klass[0] in ("Q", "C"):
            continue
        if found.get("Fix") and any(task.split()[:1] and task.split()[0] in known for task in found.get("Task", [])):
            continue
        bad.append(f"{sha.strip()[:12]} {message.strip().splitlines()[0][:60] if message.strip() else ''}".strip())
    problems = [f"ticket {ticket} closed since the last release" for ticket in newly]
    problems += [f"commit {line}: no Fix: with a Task: ticket closed at the last release, no Class: Q, no Class: C"
                 for line in bad]
    if problems:
        return {"pass": False, "detail": "; ".join(problems[:20]) + (" and more" if len(problems) > 20 else "")}
    return {"pass": True, "detail": "no ticket closed; every code commit is a fix or a chore"}


def commands_at(repo: Path, commit: str) -> set[str]:
    """The command names the CLI knows at ``commit``, read from git objects: ``src/gov/<folder>/command.py`` (the
    folder, ``_`` read as ``-``) and ``src/gov/cli/commands/<name>.py``."""
    names = set()
    for rel in _run(repo, "ls-tree", "-r", "--name-only", commit, "--", "src/gov").splitlines():
        match = re.fullmatch(r"src/gov/([^/]+)/command\.py", rel)
        if match:
            names.add(match.group(1).replace("_", "-"))
            continue
        match = re.fullmatch(r"src/gov/cli/commands/([^/]+)\.py", rel)
        if match and match.group(1) != "__init__":
            names.add(match.group(1).replace("_", "-"))
    return names


def _p4(repo: Path, n_commit: str, c: str) -> dict:
    before, now = commands_at(repo, n_commit), commands_at(repo, c)
    added, removed = sorted(now - before), sorted(before - now)
    if added or removed:
        said = [f"added: {', '.join(added)}"] if added else []
        said += [f"removed: {', '.join(removed)}"] if removed else []
        return {"pass": False, "detail": "the commands differ (" + "; ".join(said) + ")"}
    return {"pass": True, "detail": f"the same {len(now)} commands"}


def _p5(repo: Path, n_commit: str, c: str) -> dict:
    changed = []
    for line in _run(repo, "diff", "--name-status", "--no-renames", n_commit, c, "--", SCHEMAS).splitlines():
        status, _, rel = line.partition("\t")
        if status in ("A", "D"):
            changed.append(f"{rel.rsplit('/', 1)[-1]} {'added' if status == 'A' else 'removed'}")
    if changed:
        return {"pass": False, "detail": f"kit schemas changed in number: {', '.join(changed)}"}
    return {"pass": True, "detail": "no kit schema added or removed"}


def evaluate(repo: Path, version: str, commit: str | None = None) -> dict:
    """The rule from the last release N to ``commit`` (default HEAD) as ``{"version", "kind", "from", "commit",
    "rules": {"P1": {"pass", "detail"}, ...}, "failed": [...]}``. Raises ``NoRelease`` without an N. Writes nothing."""
    repo = Path(repo)
    c = _run(repo, "rev-parse", "--verify", f"{commit or 'HEAD'}^{{commit}}").strip()
    n, n_commit = last_release(repo, c)
    checks = {"P1": _p1, "P2": _p2, "P3": _p3, "P4": _p4, "P5": _p5}
    rules = {}
    for name in RULES:
        try:
            rules[name] = checks[name](repo, n, c) if name == "P1" else checks[name](repo, n_commit, c)
        except ReleaseError as exc:  # an input that cannot be read is a failure, never a pass
            rules[name] = {"pass": False, "detail": f"cannot be read: {exc}"}
    failed = [name for name in RULES if not rules[name]["pass"]]
    return {"version": version, "kind": "bigger" if failed else "patch", "from": n, "commit": c, "rules": rules,
            "failed": failed}


def kind_record(result: dict) -> dict:
    """The ``kind.json`` of a release: the result without its ``failed`` list."""
    return {key: result[key] for key in ("version", "kind", "from", "commit", "rules")}


def changes(repo: Path, n: str, commit: str) -> tuple[list[str], list[str]]:
    """The fixes and the chores of the range ``v<n>..commit`` in plain words: the ``Fix:`` value of every non-merge
    commit that has one, and the subject of every other non-merge commit with ``Class: Q`` or ``Class: C``."""
    log = _run(Path(repo), "log", "--no-merges", "--reverse", "--format=%B%x1e", f"v{n}..{commit}")
    fixes, chores = [], []
    for message in log.split("\x1e"):
        if not message.strip():
            continue
        found = trailers(message)
        if found.get("Fix"):
            fixes += [value for value in found["Fix"] if value]
        elif (found.get("Class") or [""])[-1].split()[:1] in (["Q"], ["C"]):
            chores.append(message.strip().splitlines()[0])
    return fixes, chores


def count_fixes(repo: Path, n: str, commit: str) -> int:
    """The number of non-merge commits of ``v<n>..commit`` that carry a ``Fix:`` trailer."""
    log = _run(Path(repo), "log", "--no-merges", "--format=%B%x1e", f"v{n}..{commit}")
    return sum(1 for message in log.split("\x1e") if trailers(message).get("Fix"))


def dumps(value) -> str:
    return json.dumps(value, indent=2) + "\n"
