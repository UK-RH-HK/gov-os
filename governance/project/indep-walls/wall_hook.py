#!/usr/bin/env python3
"""The wall hook (ACT-INDEP-WALLS-1, DEC-1101 (2)): the PreToolUse guard of one independent session's walled folder.

Run as `python3 -I <wall>/.claude/wall_hook.py <wall> <tree>` from the wall's own settings (<tree>: the wall's plain
tree of the repository, kept outside the sets root, ACT-INDEP-WALLS-1 §1). It is the inverse of the
repository's guard (DEC-820: reads open, writes closed): here reads AND writes are closed to the wall.
  - Tools: Read, Grep, Glob (reads), Write, Edit, MultiEdit (writes), TodoWrite (no file). Every other tool is refused:
    Bash and every shell, WebFetch, WebSearch, Task/Agent (no subagents), NotebookEdit, Skill, any MCP tool, and any
    tool this file does not name.
  - Reads: only paths whose real path (links followed) is inside the wall or its tree. A Grep or Glob with no path
    searches the session's folder, which must be the wall.
  - Writes: only into <wall>/out/ (real path of the folder, the last name not a link), never the wall's .claude/,
    its brief, seed, manifest or input, never the tree.
  - Fails closed: an event it cannot read, a wall that is not a folder, or any error refuses (exit 2).
It reads nothing but the event; it opens no file. The repository's guard is not loaded here (ACT-INDEP-WALLS-1 §1).
"""
import json
import os
import sys

READS = ("Read", "Grep", "Glob")
WRITES = ("Write", "Edit", "MultiEdit")
FREE = ("TodoWrite",)
GLOB_CHARS = "*?[{"


def deny(why):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                        "permissionDecisionReason": "wall: " + why}}))
    sys.exit(0)


def inside(path, folder):
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def main():
    if len(sys.argv) != 3:
        raise RuntimeError("usage: wall_hook.py <wall> <tree>")
    wall, tree = os.path.realpath(sys.argv[1]), os.path.realpath(sys.argv[2])
    home = os.path.realpath(os.path.expanduser("~"))
    for f in (wall, tree):
        if not os.path.isdir(f) or f in ("/", home) or inside(home, f):
            raise RuntimeError("the wall or its tree is not a folder of its own")
    readable = lambda p: inside(p, wall) or inside(p, tree)
    out = os.path.join(wall, "out")
    data = json.loads(sys.stdin.read())
    tool = data.get("tool_name")
    tin = data.get("tool_input")
    cwd = data.get("cwd")
    if not isinstance(tool, str) or not isinstance(tin, dict):
        raise RuntimeError("an event without a tool name or input")
    if not isinstance(cwd, str) or not inside(os.path.realpath(cwd), wall):
        deny("the session's folder is not its wall")
    cwd = os.path.realpath(cwd)

    def real(p):
        return os.path.realpath(os.path.join(cwd, os.path.expanduser(p)))

    if tool in FREE:
        sys.exit(0)
    if tool in READS:
        for k in ("file_path", "path", "notebook_path"):
            v = tin.get(k)
            if v is None:
                continue
            if not isinstance(v, str) or not v or "\x00" in v:
                deny(f"{tool}'s {k} is not a path")
            if not readable(real(v)):
                deny(f"{tool} reaches outside the wall ({v})")
        if tool == "Glob":
            pat = tin.get("pattern")
            if not isinstance(pat, str) or not pat or "\x00" in pat:
                deny("Glob's pattern is not a pattern")
            parts = pat.split("/")
            n = next((i for i, p in enumerate(parts) if any(c in p for c in GLOB_CHARS)), len(parts))
            head = "/".join(parts[:n]) or "."
            if ".." in parts[n:]:
                deny("Glob's pattern climbs out after a wildcard")
            base = real(tin.get("path")) if isinstance(tin.get("path"), str) and tin.get("path") else cwd
            if not readable(os.path.realpath(os.path.join(base, os.path.expanduser(head)))):
                deny(f"Glob reaches outside the wall ({pat})")
        if tool == "Read" and not isinstance(tin.get("file_path"), str):
            deny("Read names no file")
        sys.exit(0)
    if tool in WRITES:
        v = tin.get("file_path")
        if not isinstance(v, str) or not v or "\x00" in v:
            deny(f"{tool} names no file")
        full = os.path.join(cwd, os.path.expanduser(v))
        folder = os.path.realpath(os.path.dirname(os.path.normpath(full)))
        name = os.path.basename(os.path.normpath(full))
        if os.path.islink(os.path.join(folder, name)):
            deny(f"{tool} writes through a link ({v})")
        if not inside(os.path.join(folder, name), out) or os.path.join(folder, name) == out:
            deny(f"{tool} writes outside the wall's out/ ({v})")
        sys.exit(0)
    deny(f"the tool {tool} is not open to a walled session")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        sys.stderr.write(f"wall hook: could not decide: {exc}; refused\n")
        sys.exit(2)
