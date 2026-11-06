"""``gov links [--since <rev> | --all] [--json] [--propose-marks | --propose-sources]`` (W2-129, DEC-1073 (5)(b)).

A notice, never a gate: no close, landing, launch, claim, readiness check or hook calls it. It reads ``HEAD``
(``gov.links.check``) and writes nothing but its mark, ``.gov-runtime/links/mark``: the full sha of the head it
judged, alone. The range is ``<rev>..HEAD`` from ``--since``, else from the mark; with neither it refuses, naming
``--since`` (``--all`` with neither judges the whole history: every finding is new).

Its output: the line ``gov links: N new since <rev>, M standing (...)``, then one line per new finding (and, with
``--all``, per standing finding); ``--json`` gives the same in gov's envelope. Its exit code is 0 with no new finding,
1 with new findings and 2 when it cannot run (named). ``--propose-marks`` and ``--propose-sources`` print a patch
for ``git apply`` instead, write nothing (not the mark) and end with 0.
"""

from __future__ import annotations

CLASS = "read"
HELP = "link integrity: unlinked and contradicted records, with the role that fixes each (a notice)"
CHILD_EXIT_CODE = True  # 0, 1 or 2, as the run's own outcome; gov prints no envelope of its own

EXIT_CLEAN, EXIT_NEW, EXIT_CANNOT = 0, 1, 2


def add_arguments(parser) -> None:
    rangeful = parser.add_mutually_exclusive_group()
    rangeful.add_argument("--since", metavar="<rev>", help="judge <rev>..HEAD (default: the mark)")
    rangeful.add_argument("--all", action="store_true", help="list the standing findings too")
    patches = parser.add_mutually_exclusive_group()
    patches.add_argument("--propose-marks", action="store_true",
                         help="print a patch adding each UNMARKED_CHANGE's mark to its entry's status line")
    patches.add_argument("--propose-sources", action="store_true",
                         help="print a patch adding each UNLINKED_ID to its ticket's sources:")


def _cannot(args, code: str, message: str, details: dict | None = None) -> int:
    import json
    import sys

    if args.json:
        print(json.dumps({"ok": False, "command": "links", "result": {}, "session": args.session,
                          "error": {"code": code, "message": message, "details": details or {}}}))
    else:
        print(f"gov links: {code}: {message}", file=sys.stderr)
    return EXIT_CANNOT


def _toplevel(root):
    import subprocess
    from pathlib import Path

    from gov.util.gitenv import git_env
    try:
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True,
                              text=True, env=git_env(root, pinned=True))
    except OSError:
        return None
    return Path(done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else None


def _commit(root, rev: str) -> str | None:
    from gov.cli.errors import GovError
    from gov.store import loader
    try:
        return loader._git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}").decode().strip() or None
    except GovError:
        return None


def run(root, args, config):
    import json
    from collections import Counter
    from pathlib import Path

    from gov.cli.errors import GovError
    from gov.links import check, patch

    top = _toplevel(Path(root))
    if top is None or not Path(root).is_dir():
        return _cannot(args, "LINKS_NOT_A_WORK_TREE", f"{root} is not a git work tree", {"root": str(root)})
    root = top
    head = _commit(root, "HEAD")
    if head is None:
        return _cannot(args, "LINKS_NO_HEAD", f"{root} has no commit to judge", {"root": str(root)})
    proposing = args.propose_marks or args.propose_sources
    mark_path = root / check.MARK_REL
    base, since = None, None
    if args.since:
        base = _commit(root, args.since)
        if base is None:
            return _cannot(args, "LINKS_BAD_REV", f"--since {args.since} names no commit", {"rev": args.since})
        since = args.since
    elif mark_path.is_file():
        marked = mark_path.read_text(encoding="utf-8").strip()
        base = _commit(root, marked) if marked else None
        if base is None:
            return _cannot(args, "LINKS_MARK_UNKNOWN", f"the mark {check.MARK_REL} names no commit of this "
                           "repository; give the range with --since <rev>", {"mark": marked})
        since = marked
    elif not (args.all or proposing):
        return _cannot(args, "LINKS_NO_RANGE", f"no mark yet ({check.MARK_REL}): give the range with --since <rev> "
                       "(or list every finding with --all)", {"mark": check.MARK_REL})
    try:
        repo = check._Repo(root)
        range_ = check.touched(repo, base)
        found, in_range = check.findings(repo, None if range_ is None else range_["commits"])
    except GovError as error:
        return _cannot(args, error.code, error.message, error.details)
    if proposing:
        if args.propose_marks:
            lines = {entry["id"]: repo.status_line(entry) for entry in repo.entries}
            print(patch.marks(repo.register_path, repo.register_text, found, lines) if repo.register_path else "",
                  end="")
        else:
            print(patch.sources(repo.files, found), end="")
        return EXIT_CLEAN
    for finding in found:
        finding["new"] = check.is_new(finding, repo, range_)
    new = [finding for finding in found if finding["new"]]
    standing = [finding for finding in found if not finding["new"]]
    by = Counter((finding["code"], finding["role"]) for finding in standing)
    breakdown = ", ".join(f"{code} {role} {count}" for (code, role), count in
                          sorted(by.items(), key=lambda item: (check.CODES.index(item[0][0]), item[0][1])))
    gone = check.not_applicable(repo)
    counts = f"records {len(repo.fronts) + len(repo.entries)}, register {len(repo.entries)} entries, commits {in_range}"
    label = since if since is not None else "root"
    first = (f"gov links: {len(new)} new since {label}, {len(standing)} standing ("
             + (f"{breakdown}; " if breakdown else "") + counts
             + (f"; not applicable: {', '.join(gone)}" if gone else "") + ")")
    listed = new + (standing if args.all else [])
    mark_path.parent.mkdir(parents=True, exist_ok=True)
    mark_path.write_text(head, encoding="utf-8")
    if args.json:
        standing_by: dict = {}
        for (code, role), count in by.items():
            standing_by.setdefault(code, {})[role] = count
        result = {"summary": first, "since": label, "base": base, "head": head, "new": len(new),
                  "standing": len(standing), "standing_by": standing_by,
                  "counts": {"records": len(repo.fronts) + len(repo.entries), "register_entries": len(repo.entries),
                             "commits": in_range},
                  "not_applicable": gone, "mark": check.MARK_REL, "findings": listed}
        print(json.dumps({"ok": True, "command": "links", "result": result, "session": args.session}))
    else:
        print(first)
        for finding in listed:
            print(check.render(finding))
    return EXIT_NEW if new else EXIT_CLEAN
