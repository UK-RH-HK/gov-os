"""The owner-accepted known-red list, as a ratchet, and the named load-sensitive quarantine (DEC-757 items 2 and 4).

The path map's ``accepted_reds`` (entries ``{test, decision, reason, fixed_by}``) and ``load_sensitive`` (entries
``{test, decision, reason}``). A test is a pytest node id relative to the project's root. An entry counts only
when its decision is an ACCEPTED owner entry of the register whose text names the test (its own name, with its
parameter set, as a whole word, and its file), and every commit of the history that added the entry carries
``Role: owner`` in its final trailer block. An entry that does not count covers nothing and is a finding.

``apply_accepted_reds`` is the ratchet's core, one public function: ``gov close`` judges its runs' reds by it, and
W2-19 reuses it for declared test commands (DEC-736). What git cannot answer is a ``GovError``: nothing passes.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from gov.close.history import PATH_MAP_REL, REGISTER_KEY, owner_decision, register_entries
from gov.close.repo import git, read_commits

ACCEPTED_REDS, LOAD_SENSITIVE = "accepted_reds", "load_sensitive"
FIELDS = {ACCEPTED_REDS: ("test", "decision", "reason", "fixed_by"), LOAD_SENSITIVE: ("test", "decision", "reason")}
REFUSED = {ACCEPTED_REDS: "ACCEPTED_RED_REFUSED", LOAD_SENSITIVE: "LOAD_SENSITIVE_REFUSED"}
RED_NOT_ACCEPTED, ACCEPTED_RED_PASSES = "RED_NOT_ACCEPTED", "ACCEPTED_RED_PASSES"
PASSED, SKIPPED, FAILED, NOT_RUN = "passed", "skipped", "failed", "not run"


def red(outcome) -> bool:
    """Whether a result is a red: ``failed``, ``error``, or anything else that is neither a pass nor a skip."""
    return outcome not in (PASSED, SKIPPED)


def covers(entry_test: str, test: str) -> bool:
    """Whether a ``load_sensitive`` entry names the node id ``test``: the id itself, or ``file::function`` for
    every parameter set of that function."""
    return test == entry_test or test.startswith(entry_test + "[")


def _path_map_at(root: Path, sha: str) -> dict:
    """The path map a commit holds; ``{}`` where it holds none (or none git can show) or no mapping."""
    try:
        loaded = yaml.safe_load(git(root, "show", f"{sha}:{PATH_MAP_REL}", ok=(0, 128))) or {}
    except yaml.YAMLError:
        loaded = {}
    return loaded if isinstance(loaded, dict) else {}


def _held(path_map: dict, key: str) -> set[tuple]:
    entries = path_map.get(key)
    return {(e.get("test"), e.get("decision")) for e in entries if isinstance(e, dict)} \
        if isinstance(entries, list) else set()


def counted_entries(root, key: str, commit: str = "HEAD") -> tuple[list[dict], list[dict]]:
    """``(counted, findings)`` of the project's path map's list ``key``: the entries that count, and for each
    other one a finding ``{code, test, message}`` that names it, why, and the commit that added it without the
    owner's role."""
    root = Path(root)
    try:
        path_map = yaml.safe_load((root / PATH_MAP_REL).read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        path_map = {}
    entries = path_map.get(key) if isinstance(path_map, dict) else None
    if not entries:
        return [], []
    register = register_entries(root, path_map.get(REGISTER_KEY))
    # R-3: the commits that added an entry hold it while none of their parents does.
    maps: dict[str, set] = {}

    def holds(sha: str, entry: tuple) -> bool:
        if sha not in maps:
            maps[sha] = _held(_path_map_at(root, sha), key)
        return entry in maps[sha]

    changed = [(sha, git(root, "rev-list", "--parents", "-n", "1", sha).split()[1:])
               for sha in git(root, "rev-list", "--full-history", commit, "--", PATH_MAP_REL).split()]
    counted, findings = [], []
    for entry in entries if isinstance(entries, list) else [entries]:
        test, decision = (entry.get("test"), entry.get("decision")) if isinstance(entry, dict) else (entry, None)
        why = _refused_because(root, key, entry, register, changed, holds, commit)
        if why:
            findings.append({"code": REFUSED[key], "test": str(test),
                             "message": f"the {key} entry {test} ({decision}) is refused: {why}; it covers nothing"})
        else:
            counted.append(entry)
    return counted, findings


def _refused_because(root: Path, key: str, entry, register, changed, holds, commit: str) -> str | None:
    """Why an entry does not count (R-2, R-3), or None."""
    if not isinstance(entry, dict) or not all(isinstance(entry.get(f), str) and entry[f].strip()
                                              for f in FIELDS[key]):
        return f"it does not give each of {', '.join(FIELDS[key])}"
    test, decision = entry["test"], entry["decision"]
    why, text = owner_decision(decision, register)
    if why:
        return why
    file, _, name = test.rpartition("::")
    if not name or not file or file.split("::")[0] not in text or \
            not re.search(rf"(?<!\w){re.escape(name)}(?![\w\[])", text):
        return f"{decision} does not name the test {test}"
    added = [sha for sha, parents in changed
             if holds(sha, (test, decision)) and not any(holds(p, (test, decision)) for p in parents)]
    if not added:
        return f"no commit of the history of {commit} adds it"
    not_owner = [c["sha"][:12] for c in read_commits(root, "--no-walk", *added)
                 if c["trailers"].get("Role") != ["owner"]]
    if not_owner:
        return f"commit {', '.join(not_owner)} added it without Role: owner in its final trailer block"
    return None


def apply_accepted_reds(root, results: dict, commit: str = "HEAD") -> dict:
    """The ratchet (DEC-757 item 2) on a run's ``results`` (a test id to ``passed``, ``failed``, ``error`` or
    ``skipped``): ``{"ok", "accepted_reds", "findings"}``. A red that a counted entry lists by its exact id is
    covered and reported ``failed``; a listed test the run did not run is reported ``not run`` and refuses
    nothing; a listed test that passes refuses until its entry is removed; any other red refuses, and so does
    an entry that does not count."""
    counted, findings = counted_entries(root, ACCEPTED_REDS, commit)
    listed = {entry["test"]: entry for entry in counted}
    reports = []
    for test, entry in listed.items():
        outcome = results.get(test)
        result = NOT_RUN if outcome in (None, SKIPPED) else PASSED if outcome == PASSED else FAILED
        reports.append({**{field: entry[field] for field in FIELDS[ACCEPTED_REDS]}, "result": result})
        if result == PASSED:
            findings.append({"code": ACCEPTED_RED_PASSES, "test": test,
                             "message": f"the listed red {test} ({entry['decision']}) passes: remove its entry "
                                        f"from {ACCEPTED_REDS}"})
    for test, outcome in sorted(results.items()):
        if red(outcome) and test not in listed:
            findings.append({"code": RED_NOT_ACCEPTED, "test": test,
                             "message": f"{test} is red ({outcome}) and {ACCEPTED_REDS} does not list it"})
    return {"ok": not findings, ACCEPTED_REDS: reports, "findings": findings}
