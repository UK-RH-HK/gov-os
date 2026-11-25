"""The release rule (W2-209, RELEASE-ON-BEHALF "What a patch release is"; DEC-1223 RB-7; DEC-1235 (2)).

A release is a **patch release** when five rules hold, each read by code from the last release N to the release
commit C, never by judgement:

- P1 version: ``pyproject.toml`` at C is N's version with only the last number raised and no pre-release part;
- P2 owner's text: no path changed under ``docs/contract``, ``docs/charter`` or ``docs/emergency-2/EMERGENCY-2.md``;
- P3 no feature: no ticket closed at C that was not closed at N, and every non-merge commit N..C that touches
  ``src/gov`` or ``template`` carries a ``Fix:`` trailer with a ``Task:`` ticket closed at N, or ``Class: C``;
- P4 no new command: the command names the CLI knows are the same at N and at C;
- P5 no new record kind: no file added to or removed from ``template/governance/kernel/schemas``.

A range that fails a rule is **approved** (DEC-1235 (2)) when the version at C is a plain semantic version above N's,
something in the range needs approval and each such item names the owner's approving decision: a ticket closed since
N by its front matter's ``approved_by``; a commit P3 rejects, one that changes a P2 path and one that adds or removes
a command module or a kit schema by its ``Approved-by:`` trailer or its ``Task:`` ticket's ``approved_by``. A P2, P4
or P5 change no non-merge commit accounts for has no name. A decision counts only when the register at C holds it with
a Status beginning ``ACCEPTED (owner``.

Anything else is a **bigger** release, which only the owner builds (``gov release``, DEC-772). ``evaluate`` reads git
objects only and writes nothing. A rule whose input cannot be read fails (it never passes), and such a range is never
approved.
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

import yaml

from gov.decisions.basis import REGISTER_DEFAULT, _fields, parse_entries
from gov.release import RELEASES_REL, SEMVER, ReleaseError, _blobs

RULES = ("P1", "P2", "P3", "P4", "P5")
P2_PATHS = ("docs/contract", "docs/charter", "docs/emergency-2/EMERGENCY-2.md")
SCHEMAS = "template/governance/kernel/schemas"
CODE_PATHS = ("src/gov", "template")
_TRAILER = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):[ \t]*(.*?)[ \t]*$")
_DECISION = re.compile(r"DEC-\d+")
OWNERS = "ACCEPTED (owner"
UNREADABLE = "cannot be read: "


class NoRelease(ReleaseError):
    """No release N to read the range from."""


def _run(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, encoding="utf-8", errors="replace")
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


def _under(path: str, roots: tuple) -> bool:
    return any(path == root or path.startswith(root + "/") for root in roots)


def _changed(repo: Path, n_commit: str, c: str, *paths: str) -> list[tuple[str, str]]:
    """``(status, path)`` of every path under ``paths`` that differs between N and C (a rename as D and A)."""
    parts = _run(repo, "diff", "--name-status", "--no-renames", "-z", n_commit, c, "--", *paths).split("\0")
    return list(zip(parts[0::2], parts[1::2]))


def _p2(repo: Path, n_commit: str, c: str) -> dict:
    names = [path for _, path in _changed(repo, n_commit, c, *P2_PATHS)]
    if names:
        return {"pass": False, "detail": f"changed since the last release: {', '.join(names[:20])}"
                                         f"{' and more' if len(names) > 20 else ''}"}
    return {"pass": True, "detail": "no path of the Contract, the Charter or EMERGENCY-2 changed"}


def _tickets(repo: Path, commit: str) -> list[dict]:
    """The tickets at ``commit`` that have front matter: ``{"fields": its top-level lines, "data": its bytes}``."""
    found = []
    for rel, data in _blobs(repo, commit, ".tickets").items():
        if rel.count("/") != 1 or not rel.endswith(".md"):
            continue
        text = data.decode("utf-8", "replace")
        if not text.startswith("---"):
            continue
        fields = {}
        for line in text.split("\n---", 1)[0].splitlines()[1:]:
            key, sep, value = line.partition(":")
            if sep and key and not key[0].isspace():
                fields.setdefault(key.strip(), value.strip().strip("'\""))
        found.append({"fields": fields, "data": data})
    return found


def _names(fields: dict) -> set[str]:
    """The names a ``Task:`` trailer may give a ticket."""
    return {fields[k] for k in ("id", "wbs_id", "external-ref") if fields.get(k)}


def closed_tickets(repo: Path, commit: str) -> dict[str, set[str]]:
    """The tickets closed at ``commit``: ``{id: {the names a Task: trailer may give it}}``."""
    return {t["fields"]["id"]: _names(t["fields"]) for t in _tickets(repo, commit)
            if t["fields"].get("status") == "closed" and t["fields"].get("id")}


def _history(repo: Path, n_commit: str, c: str) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """Every non-merge commit N..C, oldest first, as ``(sha, message, [(status, path)])``, from one ``git log``."""
    log = _run(repo, "-c", "log.showRoot=true", "log", "--no-merges", "--reverse", "--no-renames", "--name-status",
               "-z", "--format=%x1e%H%x1f%B%x1f", f"{n_commit}..{c}")
    found = []
    for entry in log.split("\x1e")[1:]:
        sha, _, rest = entry.partition("\x1f")
        message, sep, names = rest.rpartition("\x1f")
        if not sep or not re.fullmatch(r"[0-9a-f]{40,64}", sha):
            raise ReleaseError(f"the log of {n_commit[:12]}..{c[:12]} cannot be parsed")
        parts = [part for part in names.lstrip("\0\n").split("\0") if part]
        found.append((sha, message, list(zip(parts[0::2], parts[1::2]))))
    return found


def _tasks(found: dict) -> list[str]:
    """The ticket each ``Task:`` trailer names (its first word)."""
    return [task.split()[0] for task in found.get("Task", []) if task.split()]


def _rejected(message: str, changed: list, known: set[str]) -> bool:
    """Whether P3 rejects a commit: it touches the code, is no ``Class: C`` chore and no fix under a ticket in ``known``."""
    if not any(_under(path, CODE_PATHS) for _, path in changed):
        return False
    found = trailers(message)
    if (found.get("Class") or [""])[-1].split()[:1] == ["C"]:
        return False
    return not (found.get("Fix") and any(task in known for task in _tasks(found)))


def _p3(repo: Path, n_commit: str, c: str) -> dict:
    before, now = closed_tickets(repo, n_commit), closed_tickets(repo, c)
    newly = sorted(set(now) - set(before))
    known = set().union(*before.values()) if before else set()
    problems = [f"ticket {ticket} closed since the last release" for ticket in newly]
    for sha, message, changed in reversed(_history(repo, n_commit, c)):
        if _rejected(message, changed, known):
            subject = message.strip().splitlines()[0][:60] if message.strip() else ""
            line = f"{sha[:12]} {subject}".strip()
            problems.append(f"commit {line}: no Fix: with a Task: ticket closed at the last release, no Class: C")
    if problems:
        return {"pass": False, "detail": "; ".join(problems[:20]) + (" and more" if len(problems) > 20 else "")}
    return {"pass": True, "detail": "no ticket closed; every code commit is a fix or a Class: C chore"}


def _command_name(rel: str) -> str | None:
    """The command a module path gives the CLI: ``src/gov/<folder>/command.py`` or ``src/gov/cli/commands/<name>.py``."""
    match = (re.fullmatch(r"src/gov/([^/]+)/command\.py", rel)
             or re.fullmatch(r"src/gov/cli/commands/(?!__init__\.py)([^/]+)\.py", rel))
    return match.group(1).replace("_", "-") if match else None


def commands_at(repo: Path, commit: str) -> set[str]:
    """The command names the CLI knows at ``commit``, read from git objects: ``src/gov/<folder>/command.py`` (the
    folder, ``_`` read as ``-``) and ``src/gov/cli/commands/<name>.py``."""
    listed = _run(repo, "ls-tree", "-r", "--name-only", commit, "--", "src/gov").splitlines()
    return {name for name in map(_command_name, listed) if name}


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
    for status, rel in _changed(repo, n_commit, c, SCHEMAS):
        if status in ("A", "D"):
            changed.append(f"{rel.rsplit('/', 1)[-1]} {'added' if status == 'A' else 'removed'}")
    if changed:
        return {"pass": False, "detail": f"kit schemas changed in number: {', '.join(changed)}"}
    return {"pass": True, "detail": "no kit schema added or removed"}


def _register(repo: Path, commit: str) -> dict[str, list[list[str]]]:
    """The register at ``commit``: ``{decision id: [the Status texts of each of its entries]}``."""
    data = _blobs(repo, commit, REGISTER_DEFAULT).get(REGISTER_DEFAULT)
    if data is None:
        raise ReleaseError(f"{REGISTER_DEFAULT} is not at {commit[:12]}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ReleaseError(f"{REGISTER_DEFAULT} at {commit[:12]} is not UTF-8") from None
    found: dict[str, list[list[str]]] = {}
    for entry in parse_entries(text):
        found.setdefault(entry["id"], []).append(
            [value.strip() for label, value in _fields(entry["lines"]) if label == "status"])
    return found


def _name(values: list, register: dict) -> tuple[list[str], list[str]]:
    """One name of approving decisions (a ticket's ``approved_by`` or one trailer): the ids it gives and why it does not
    count (nothing when every one of them is the owner's)."""
    ids, lacks = [], []
    for value in values:
        if not isinstance(value, str) or not _DECISION.fullmatch(value):
            lacks.append(f"{value!r} is not a decision id")
            continue
        ids.append(value)
        entries = register.get(value)
        if not entries:
            lacks.append(f"{value} is not in the register at the release commit")
        elif not all(texts and all(text.startswith(OWNERS) for text in texts) for texts in entries):
            said = next((text for texts in entries for text in texts if not text.startswith(OWNERS)), "without a Status")
            lacks.append(f"{value} is not accepted by the owner (its Status: {said[:60]})")
    return ids, lacks


def _ticket_name(ticket: dict, register: dict) -> tuple[list[str], list[str]] | None:
    """The name in a ticket's front matter (``approved_by``), None without one."""
    label = ticket["fields"].get("id") or "a ticket"
    try:
        text = ticket["data"].decode("utf-8")
        front, closing, _ = text[3:].partition("\n---")
        record = yaml.safe_load(front) if closing else None
    except (UnicodeDecodeError, ValueError, yaml.YAMLError):
        record = None
    if not isinstance(record, dict):
        return [], [f"the front matter of {label} cannot be read"]
    value = record.get("approved_by")
    if value is None or value == []:
        return None
    return _name(value if isinstance(value, list) else [value], register)


def _item(item: str, names: list, covered: bool, missing: str) -> dict:
    decisions = list(dict.fromkeys(found for ids, _ in names for found in ids))
    reasons = list(dict.fromkeys(why for _, lacks in names for why in lacks))
    return {"item": item, "decisions": decisions, "ok": covered,
            "lacks": None if covered else "; ".join(reasons) or missing}


def approvals(repo: Path, n_commit: str, c: str) -> list[dict]:
    """Every item of the range N..C that needs the owner's approval, as ``{"item", "decisions", "ok", "lacks"}``."""
    tickets, register = _tickets(repo, c), _register(repo, c)
    before, now = closed_tickets(repo, n_commit), closed_tickets(repo, c)
    known = set().union(*before.values()) if before else set()
    items = []
    for ticket in sorted(set(now) - set(before)):
        names = [_ticket_name(t, register) for t in tickets if t["fields"].get("id") == ticket]
        covered = all(name is not None and not name[1] for name in names)
        items.append(_item(f"ticket {ticket}", [name for name in names if name], covered,
                           "names no approving decision (approved_by in its front matter)"))
    history = _history(repo, n_commit, c)
    for sha, message, changed in history:
        needs = (_rejected(message, changed, known)
                 or any(_under(path, P2_PATHS) for _, path in changed)
                 or any(status in ("A", "D") and (_command_name(path) or _under(path, (SCHEMAS,)))
                        for status, path in changed))
        if not needs:
            continue
        found = trailers(message)
        names = [_name([part.strip() for part in value.split(",")], register) for value in found.get("Approved-by", [])]
        for task in _tasks(found):
            names += [name for t in tickets if task in _names(t["fields"]) and (name := _ticket_name(t, register))]
        items.append(_item(f"commit {sha[:12]}", names, any(not lacks for _, lacks in names),
                           "names no approving decision (an Approved-by: trailer, or approved_by in its Task: ticket)"))
    return items + [_item(item, [], False, "no non-merge commit of the range accounts for it, so no decision covers it")
                    for item in _unaccounted(repo, n_commit, c, history)]


def _unaccounted(repo: Path, n_commit: str, c: str, history: list) -> list[str]:
    """The P2, P4 and P5 changes between N and C that no non-merge commit of the range made (a merge's own change)."""
    made = {(status, path) for _, _, changed in history for status, path in changed}
    touched = {path for _, path in made}
    found = [f"path {path}" for _, path in _changed(repo, n_commit, c, *P2_PATHS) if path not in touched]
    old, new = commands_at(repo, n_commit), commands_at(repo, c)
    for status, names in (("A", new - old), ("D", old - new)):
        accounted = {_command_name(path) for done, path in made if done == status}
        found += [f"command {name}" for name in sorted(names - accounted)]
    return found + [f"schema {path}" for status, path in _changed(repo, n_commit, c, SCHEMAS)
                    if status in ("A", "D") and (status, path) not in made]


def _raised(repo: Path, n: str, c: str) -> bool:
    """Whether the version at C is a semantic version with no pre-release or build part, above N's."""
    found = _pyproject_version(repo, c)
    match = SEMVER.fullmatch(found) if found is not None else None
    if not match or match.group(4) or match.group(5):
        return False
    return _version_tuple(found) > _version_tuple(n)


def evaluate(repo: Path, version: str, commit: str | None = None) -> dict:
    """The rule from the last release N to ``commit`` (default HEAD) as ``{"version", "kind", "from", "commit",
    "rules": {"P1": {"pass", "detail"}, ...}, "failed": [...]}``, with ``approvals`` where a rule fails. Raises
    ``NoRelease`` without an N. Writes nothing."""
    repo = Path(repo)
    c = _run(repo, "rev-parse", "--verify", f"{commit or 'HEAD'}^{{commit}}").strip()
    n, n_commit = last_release(repo, c)
    checks = {"P1": _p1, "P2": _p2, "P3": _p3, "P4": _p4, "P5": _p5}
    rules = {}
    for name in RULES:
        try:
            rules[name] = checks[name](repo, n, c) if name == "P1" else checks[name](repo, n_commit, c)
        except ReleaseError as exc:  # an input that cannot be read is a failure, never a pass
            rules[name] = {"pass": False, "detail": f"{UNREADABLE}{exc}"}
    failed = [name for name in RULES if not rules[name]["pass"]]
    result = {"version": version, "kind": "patch", "from": n, "commit": c, "rules": rules, "failed": failed}
    if not failed:
        return result
    unread = any(rule["detail"].startswith(UNREADABLE) for rule in rules.values())
    try:
        items = approvals(repo, n_commit, c)
    except ReleaseError as exc:
        items = [_item("the range", [], False, f"{UNREADABLE}{exc}")]
    approved = not unread and bool(items) and all(item["ok"] for item in items) and _raised(repo, n, c)
    return {**result, "kind": "approved" if approved else "bigger", "approvals": items}


def bigger_reason(result: dict) -> str:
    """Why a range is bigger: each failed rule with its detail, then each item that lacks the owner's decision."""
    said = [f"{rule}: {result['rules'][rule]['detail']}" for rule in result["failed"]]
    said += [f"{item['item']} lacks the owner's approval: {item['lacks']}" for item in result["approvals"]
             if not item["ok"]]
    return "; ".join(said)


def bigger_details(result: dict) -> dict:
    return {key: result[key] for key in ("kind", "from", "commit", "rules", "failed", "approvals")}


def kind_record(result: dict) -> dict:
    """The ``kind.json`` of a release: the result without its ``failed`` list; ``approvals`` for an approved one."""
    keys = ("version", "kind", "from", "commit", "rules")
    keys += ("approvals",) if result["kind"] == "approved" else ()
    return {key: result[key] for key in keys}


def changes(repo: Path, n: str, commit: str) -> tuple[list[str], list[str]]:
    """The fixes and the chores of the range ``v<n>..commit`` in plain words: the ``Fix:`` value of every non-merge
    commit that has one, and the subject of every other non-merge commit with ``Class: C``."""
    log = _run(Path(repo), "log", "--no-merges", "--reverse", "--format=%B%x1e", f"v{n}..{commit}")
    fixes, chores = [], []
    for message in log.split("\x1e"):
        if not message.strip():
            continue
        found = trailers(message)
        if found.get("Fix"):
            fixes += [value for value in found["Fix"] if value]
        elif (found.get("Class") or [""])[-1].split()[:1] == ["C"]:
            chores.append(message.strip().splitlines()[0])
    return fixes, chores


def count_fixes(repo: Path, n: str, commit: str) -> int:
    """The number of non-merge commits of ``v<n>..commit`` that carry a ``Fix:`` trailer."""
    log = _run(Path(repo), "log", "--no-merges", "--format=%B%x1e", f"v{n}..{commit}")
    return sum(1 for message in log.split("\x1e") if trailers(message).get("Fix"))


def dumps(value) -> str:
    return json.dumps(value, indent=2) + "\n"
