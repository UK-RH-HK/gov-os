#!/usr/bin/env python3
"""ACT-PERMISSIONS-2 (the owner, 2026-11-06): two additional directories and three Read deny rules in a settings file.

    python3 apply.py <settings.local.json>           apply (a backup beside it first)
    python3 apply.py <settings.local.json> --check   print what is present and missing; change nothing
    python3 apply.py <settings.local.json> --undo    restore the backup this script made

- ``permissions.additionalDirectories`` gains the measure clones and the worktrees (reads there stop prompting);
  ``~/gov-os-eval`` is NOT added, so its reads keep prompting (the owner's last check).
- ``permissions.deny`` gains Read rules for the three hidden folders of the sets root, which the guard does not
  cover outside the repository. A deny rule wins over every allow, the user-level ``Read(*)`` included.
- Nothing is removed; ``allow``, ``ask`` and every other key are left exactly as they are. Twice changes nothing.

``--runs``, ``--worktrees`` and ``--eval`` replace the three folders (the rehearsal's stand-ins only); the operator
passes none. Exit 0 on success; 1 on a failed check; 2 on a usage or file error.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

BACKUP_SUFFIX = ".pre-act-permissions-2"
HIDDEN = ("fixtures/evaluation/memory-retrieval/hidden/**", "fixtures/evaluation/memory-verdict/**",
          "fixtures/evaluation/memory-verdict-2/**")


def wanted(runs: str, worktrees: str, sets_root: str) -> tuple[list[str], list[str]]:
    """The directories and the deny rules. A rule's ``//`` prefix is an absolute path (Claude Code's form; a single
    ``/`` would be read from the settings file's project)."""
    dirs = [runs, worktrees]
    rules = [f"Read(/{sets_root.rstrip('/')}/{tail})" for tail in HIDDEN]
    return dirs, rules


def main(argv) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("settings")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--check", dest="mode", action="store_const", const="--check")
    group.add_argument("--undo", dest="mode", action="store_const", const="--undo")
    ap.add_argument("--runs", default="/home/usain/gov-os-runs")
    ap.add_argument("--worktrees", default="/home/usain/gov-os-worktrees")
    ap.add_argument("--eval", default="/home/usain/gov-os-eval")
    try:
        args = ap.parse_args(argv[1:])
    except SystemExit as stop:
        return 0 if stop.code == 0 else 2
    path = Path(args.settings)
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if args.mode == "--undo":
        if not backup.is_file():
            print(f"undo: no backup {backup}", file=sys.stderr)
            return 2
        shutil.copy2(backup, path)
        print(f"undo: {path} restored from {backup.name}")
        return 0
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        print(f"cannot read {path}: {error}", file=sys.stderr)
        return 2
    dirs, rules = wanted(args.runs, args.worktrees, args.eval)
    perms = data.setdefault("permissions", {})
    have_dirs, have_deny = perms.get("additionalDirectories", []), perms.get("deny", [])
    miss_dirs = [d for d in dirs if d not in have_dirs]
    miss_rules = [r for r in rules if r not in have_deny]
    if args.mode == "--check":
        print(f"check: directories {len(dirs) - len(miss_dirs)} of {len(dirs)}; deny rules {len(rules) - len(miss_rules)}"
              f" of {len(rules)}; missing: {miss_dirs + miss_rules or 'none'}")
        print(f"check: additionalDirectories {perms.get('additionalDirectories', [])}; deny {perms.get('deny', [])}; "
              f"ask {perms.get('ask', [])}")
        evals = [d for d in perms.get("additionalDirectories", []) if d.rstrip("/").endswith("gov-os-eval")]
        if evals:
            print(f"check: STOP: the sets root is an additional directory: {evals}")
            return 1
        return 0 if not (miss_dirs or miss_rules) else 1
    if not backup.exists():
        shutil.copy2(path, backup)
    before = json.loads(json.dumps(data))
    perms.setdefault("additionalDirectories", []).extend(miss_dirs)
    perms.setdefault("deny", []).extend(miss_rules)
    text = json.dumps(data, indent=2) + "\n"
    json.loads(text)
    path.write_text(text)
    after = json.loads(path.read_text())
    unchanged = {k: v for k, v in after.items() if k != "permissions"} == {k: v for k, v in before.items() if k != "permissions"} \
        and after["permissions"].get("allow") == before["permissions"].get("allow") \
        and after["permissions"].get("ask") == before["permissions"].get("ask")
    if not unchanged:
        shutil.copy2(backup, path)
        print("STOP: allow, ask or another key changed; restored from the backup", file=sys.stderr)
        return 1
    print(f"applied: {len(miss_dirs)} director(ies) and {len(miss_rules)} deny rule(s) added; backup {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
