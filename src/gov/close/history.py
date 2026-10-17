"""What of a project's history the trailer gates judge (DEC-482, DEC-704, DEC-734): the trailers base, the
commits an owner's decision accepted as history, the merges in DEC-436's merge form, and a move of the base.

``gov close``'s trailer gate and the product-traceability check both read it, so the two judge one history.
What git cannot answer is a ``GovError`` (``gov.close.repo.git``): nothing is judged, and nothing passes.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from gov.close.repo import git

BASE_KEY = "trailers_base"  # DEC-482: a commit id, full or abbreviated; only the commits after it are judged
ACCEPTED_KEY = "accepted_history"  # DEC-734: a list of {commit, decision}
REGISTER_KEY = "decision_register"  # DEC-479
MOVE_KEY = "trailers_base_move"
MOVED_COUNT = "commits_out_of_judgement"  # W2-M266
REFUSED = "ACCEPTED_HISTORY_REFUSED"
PATH_MAP_REL = "governance/project/path-map.yaml"
COMMIT_ID = re.compile(r"[0-9a-fA-F]{4,64}")
_ENTRY = re.compile(r"#{2,6} +([A-Z]+-\d+)\b")  # DEC-473's heading of a register entry
_HEADING = re.compile(r"#{1,6} ")
_STATUS = re.compile(r"- \*\*Status:\*\*\s*(.*)")  # the entry's own status line, never a quote of one
_OWNER_ACCEPTED = re.compile(r"ACCEPTED \(owner[,;)\s]")  # the word owner alone, not owner-delegated or owner's
_UNDONE = re.compile(r"\b(superseded|revoked)\b", re.IGNORECASE)
_NAMED_ID = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{8,64}(?![0-9a-fA-F])")


def commit_of(root: Path, given) -> str | None:
    """The full id of the commit ``given`` names by its id, full or abbreviated; None for anything else (a
    branch or a tag named in hex digits included)."""
    if not isinstance(given, str) or not COMMIT_ID.fullmatch(given):
        return None
    commit = git(root, "rev-parse", "--verify", "--quiet", given + "^{commit}", ok=(0, 1)).strip()
    return commit if commit.startswith(given.lower()) else None


def trailers_base(root: Path, path_map: dict) -> tuple[str | None, set[str] | None]:
    """The base the path map records, as a full id, and the commits after it (DEC-482, DEC-479: the path map as
    the project holds it now); ``(None, None)`` with none: the whole history is judged. ``ValueError`` where
    the value is not the id, full or abbreviated, of one commit that ``HEAD`` descends from."""
    if BASE_KEY not in path_map:
        return None, None
    base = path_map[BASE_KEY]
    commit = commit_of(root, base)
    if commit and git(root, "merge-base", "--is-ancestor", commit, "HEAD", ok=(0, 1), code=True) == 0:
        return commit, set(git(root, "rev-list", f"{commit}..HEAD").split())
    raise ValueError(f"the base commit {base!r} recorded under '{BASE_KEY}' is not one commit of the project "
                     "that HEAD descends from: no commit is judged")


def adds_nothing(root: Path, sha: str) -> bool:
    """Whether ``sha`` is a merge with nothing of its own (DEC-436's merge form, W2-M165): its tree is the tree
    git's own merge of its two parents gives without a conflict. A merge whose parents conflict, or of more
    than two parents, has a resolution of its own."""
    parents = git(root, "rev-list", "--parents", "-n", "1", sha).split()[1:]
    if len(parents) != 2:
        return False
    # Exit code 1 is git's answer "the parents conflict", and the conflicted paths follow the tree; any other
    # failure is an error.
    merged = git(root, "merge-tree", "--write-tree", "--no-messages", "--name-only", *parents, ok=(0, 1)).split()
    return len(merged) == 1 and merged[0] == git(root, "rev-parse", f"{sha}^{{tree}}").strip()


def differing(root: Path, older: str, newer: str) -> list[str]:
    """The paths whose content at ``newer`` is not their content at ``older``."""
    return [p for p in git(root, "-c", "core.quotePath=false", "diff-tree", "-r", "-z", "--no-renames",
                           "--name-only", older, newer).split("\0") if p]


def register_entries(root: Path, rel) -> dict[str, list[str]] | str:
    """The entries of the register the path map names, by id, each its text from its heading to the next; the
    reason as text where there is no register to read."""
    if not isinstance(rel, str) or not rel:
        return f"the path map names no decision register ('{REGISTER_KEY}')"
    try:
        text = (root / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return f"the decision register {rel} cannot be read ({e})"
    entries: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        heading = _ENTRY.match(line)
        if heading:
            current = [line]
            entries.setdefault(heading.group(1), []).append(current)
        elif _HEADING.match(line):
            current = None
        elif current is not None:
            current.append(line)
    return {key: ["\n".join(lines) for lines in found] for key, found in entries.items()}


def _refused_because(commit: str | None, decision, register) -> str | None:
    """Why an entry is not accepted history (DEC-734), or None: its decision is one entry of the register whose
    own status line is ACCEPTED by the owner (not delegated), not undone after it, and whose text names the
    commit by an id of at least eight characters that the commit's id begins with."""
    if not commit:
        return "it names no commit of the project"
    if isinstance(register, str):
        return register
    texts = register.get(decision, []) if isinstance(decision, str) else []
    if len(texts) != 1:
        return f"the register holds {'no entry' if not texts else f'{len(texts)} entries'} {decision}"
    status = next((m.group(1).strip() for m in map(_STATUS.match, texts[0].splitlines()) if m), "no status")
    if not status.startswith("ACCEPTED"):
        return f"{decision} is not accepted (its status: {status})"
    if not _OWNER_ACCEPTED.match(status):
        return f"{decision} is accepted, but not by the owner: not the owner's decision (its status: {status})"
    undone = _UNDONE.search(status)
    if undone:
        return f"{decision} was accepted by the owner, then {undone.group(1).lower()} (its status: {status})"
    if not any(commit.startswith(named.lower()) for named in _NAMED_ID.findall(texts[0])):
        return f"{decision} does not name the commit {commit[:12]}"
    return None


def accepted_history(root: Path, path_map: dict) -> tuple[dict[str, str], list[dict]]:
    """``(accepted, refused)`` of the path map's accepted history (DEC-734): each accepted commit's full id with
    its decision, and a finding for each other entry, whose commit stays judged."""
    entries = path_map.get(ACCEPTED_KEY) or []
    register = register_entries(root, path_map.get(REGISTER_KEY)) if entries else {}
    accepted, refused = {}, []
    for entry in entries if isinstance(entries, list) else [entries]:
        given, decision = (entry.get("commit"), entry.get("decision")) if isinstance(entry, dict) else (entry, None)
        commit = commit_of(root, str(given)) if given is not None else None
        why = _refused_because(commit, decision, register)
        if why:
            refused.append({"code": REFUSED, "commit": str(given), "decision": str(decision),
                            "message": f"the accepted-history entry {given} ({decision}) is refused: {why}; "
                                       "its commit stays judged"})
        else:
            accepted[commit] = decision
    return accepted, refused


def base_move(root: Path, base: str | None) -> dict | None:
    """The last move of the base to ``base`` (W2-M266): the base the path map recorded before it, or None for
    none, and the number of commits the move took out of judgement. None where no earlier path map of
    ``HEAD``'s history recorded another base (a base never recorded, or recorded with the path map itself)."""
    if base is None:
        return None
    for sha in git(root, "log", "--topo-order", "--format=%H", "HEAD", "--", PATH_MAP_REL).split():
        try:
            earlier = yaml.safe_load(git(root, "show", f"{sha}:{PATH_MAP_REL}", ok=(0, 128))) or {}
        except yaml.YAMLError:
            earlier = {}
        given = earlier.get(BASE_KEY) if isinstance(earlier, dict) else None
        old = commit_of(root, str(given)) if given is not None else None
        if old != base:
            break
    else:
        return None
    if given is not None and old is None:
        count = "not measured: the earlier base is no commit of the project"
    else:
        count = int(git(root, "rev-list", "--count", f"{old}..{base}" if old else base).strip())
    return {"from": old if old else given, "to": base, MOVED_COUNT: count}


def judged_history(root: Path, path_map: dict) -> dict:
    """What the trailer gates judge: ``after`` (the commits after the base, or None), ``accepted`` (full id to
    decision), ``refused`` (the findings of refused entries) and ``report``, what the output states: the base
    used (``None`` for none), the accepted history as a list of ``{commit, decision}``, and a move of the
    base. ``ValueError`` where the base is no commit of the project (``trailers_base``)."""
    base, after = trailers_base(root, path_map)
    accepted, refused = accepted_history(root, path_map)
    report = {BASE_KEY: base, ACCEPTED_KEY: [{"commit": c, "decision": d} for c, d in accepted.items()]}
    move = base_move(root, base)
    if move:
        report[MOVE_KEY] = move
    return {"after": after, "accepted": accepted, "refused": refused, "report": report}
