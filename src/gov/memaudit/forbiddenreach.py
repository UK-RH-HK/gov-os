"""``forbidden-reach``: whether the forbidden sources an audit's misses cited are now outside default memory (DAEO-ma4q,
fix FR-1; DEC-1254 E-02).

Of each judged row marked ``forbidden_cited``, the sources are the paths of the final answer's citations that are in the
question's ``forbidden`` list, each once a row. Each is resolved against the repository's current path map (the working
tree's file): outside when git no longer tracks it, or a namespace holding it states a ``stale_class`` or
``lexical_policy: not indexed``; otherwise inside. One line of counts is printed, never a path, a question or an id;
nothing is written.
"""

from __future__ import annotations

from collections import Counter

import yaml

from gov.config.loader import PROJECT_DIR, read_yaml
from gov.memaudit import judge, layout, matcher
from gov.memaudit.common import UsageError, git, toplevel, z_list
from gov.retrieval import lexical

DESCRIPTION = ("Of the forbidden sources an audit's misses cited, how many the repository's current path map keeps out "
               "of default memory, and by which namespace. Prints one line of counts; writes nothing.")
VALID = ("answer", "search_again", "not_found")  # an attempt the judge takes as an answer; the last one is final
UNTRACKED, UNMAPPED = "untracked", "unmapped"


def add_arguments(sp) -> None:
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the audit's name, memory-audit-<8 digits>")
    sp.add_argument("--repo", metavar="DIR", help="the repository whose path map is read (default: the top level)")


def _cited(row: dict, question) -> set[str]:
    """The paths the row's final answer cites that the question's file names as forbidden."""
    final = next((a for a in reversed(row.get("attempts") or []) if a.get("verdict") in VALID), {})
    cited = {c.get("path") for c in final.get("citations") or [] if isinstance(c, dict)}
    try:
        named = yaml.safe_load(question.read_text(encoding="utf-8"))["forbidden"]
        return {path for path in named if isinstance(path, str) and path in cited}
    except (OSError, UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError):
        return set()


def _stale_classifier():
    """D3's ``classifier`` (``gov.retrieval.stale``), or None on a tree that has no such module."""
    try:
        from gov.retrieval.stale import classifier
    except ModuleNotFoundError as exc:
        if exc.name != "gov.retrieval.stale":
            raise
        return None
    return classifier


def holders(repo, paths) -> dict[str, tuple[str, bool]]:
    """``path -> (holder, outside)`` for each of ``paths``. The holder of a tracked file that is outside is the first
    namespace in the map's order that takes it out."""
    place = repo / PROJECT_DIR / "path-map.yaml"
    document = read_yaml(place, "CONFIG_INVALID", f"{PROJECT_DIR}/path-map.yaml") if place.is_file() else None
    spaces = document.get("namespaces") if isinstance(document, dict) else None
    spaces = spaces if isinstance(spaces, dict) else {}
    tracked = set(z_list(git(repo, "ls-files", "-z")))
    not_indexed = lexical.kept_out(repo, paths)
    classifier = _stale_classifier()
    classed = classifier(repo) if classifier else None
    order = list(spaces)
    found = {}
    for path in paths:
        holding = [name for name, entry in spaces.items()
                   if isinstance(entry, dict) and isinstance(entry.get("paths"), list)
                   and any(isinstance(p, str) and lexical._pattern(p).fullmatch(path) for p in entry["paths"])]
        if classifier:
            stale = (classed(path) or (None,))[0] if classed else None
        else:
            stale = next((name for name in holding if spaces[name].get("stale_class")), None)
        excluding = [name for name in (stale, not_indexed.get(path)) if name is not None]
        if path not in tracked:
            found[path] = UNTRACKED, True
        elif excluding:
            found[path] = min(excluding, key=order.index), True
        else:
            found[path] = (holding[0] if holding else UNMAPPED), False
    return found


def from_args(args, emit) -> str:
    """The exit word: ``ok``, or ``refused`` with the one line ``REACH-NOAUDIT``, ``REACH-NOROWS`` or ``REACH-NOSET``."""
    p = layout.paths(args.sets_root, args.audit)
    repo = toplevel(args.repo)
    if layout.inside(repo, p["root"]):
        raise UsageError("flag inside the sets root")
    if not p["run"].is_dir():
        emit("REACH-NOAUDIT")
        return "refused"
    rows = judge.rows_of(p["run"] / "reader")
    if not rows:
        emit("REACH-NOROWS")
        return "refused"
    cited = []  # a source once a row
    for qid, row in rows.items():
        if row.get("forbidden_cited") is not True:
            continue
        sources = _cited(row, p["hidden"] / f"{qid}.yaml")
        if not sources:  # the set cannot explain the mark: no partial count
            emit("REACH-NOSET")
            return "refused"
        cited += sorted(sources)
    held = holders(repo, sorted(set(cited)))
    outside = sum(held[path][1] for path in cited)
    counts = Counter(str(held[path][0]) for path in cited)
    by_holder = "; " + ", ".join(f"{name}: {n}" for name, n in sorted(counts.items())) if counts else ""
    emit(f"FORBIDDEN-REACH {len(cited)} cited, {outside} outside, {len(cited) - outside} inside{by_holder}")
    return "ok"
