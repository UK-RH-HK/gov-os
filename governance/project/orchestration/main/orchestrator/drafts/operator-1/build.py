#!/usr/bin/env python3
"""ACT-OPERATOR-1: build the guard's rule 2d into both hooks it may land on, and its block into the path map.

    python3 build.py <main tree>

Writes, beside this file:
  pretooluse.pre.candidate.py    the live hook before ACT-GUARD-CALLLOG-1 (d5be03dbb48e) plus rule 2d
  pretooluse.post.candidate.py   ACT-GUARD-CALLLOG-1's candidate (a7981319f877) plus rule 2d (its answer carries the
                                 call log's rule id "2d")
  path-map.candidate.yaml        the live map plus the write_refused block, after session_hidden
  pretooluse.pre.diff, pretooluse.post.diff, path-map.patch   the review diffs
The same three insertions go into either hook; build.py refuses a base whose anchors are not each found once.
"""
import difflib
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = sys.argv[1] if len(sys.argv) > 1 else "/home/usain/Dynamic-Agentic-Engineering-OS"
PRE = os.path.join(MAIN, ".claude/hooks/pretooluse.py")
POST = os.path.join(MAIN, ".gov-runtime/scratch/orchestrator/drafts/guard-calllog/pretooluse.candidate.py")
MAP = os.path.join(MAIN, "governance/project/path-map.yaml")
WANT = {"pre": "d5be03dbb48ed6b9a3b60364afc39c61db11cac65a1b93c0889f5999aa6ef74c",
        "post": "a7981319f877846d6a62a6768ca036a5014dc7d9f8aadd09e54e61af8251d7d0"}

DOC_ANCHOR = "     the CTO's tools included, is untouched. No block, no check;\n"
DOC_ADD = """  2d (ACT-OPERATOR-1, DEC-1106 (3), DEC-1108 (5)). no writes, by any session this guard judges, into a folder
     outside every tree that the main tree's path-map.yaml write_refused: names, but for the folders directly under
     it that its entry keeps open: the operator agent's folder ~/gov-os-operator (its install and commit freeze, its
     frozen ACTs, log and wall; the CTO writes only queue/) and the guard's call log ~/.gov-os/guard-calls. A file
     tool by the path it names, links followed; a Bash line by the writes the guard resolves (one it cannot work out
     is let through, as for rules 1 and 5; deletions there are already the catastrophic rule's). The operator agent's
     walled session runs outside this guard. No block, no check;
"""
CODE_ANCHOR = "_CLASSES = []\n"
CODE_ADD = '''WRITE_BLOCK = "write_refused"  # ACT-OPERATOR-1 (2d)
WRITE_REFUSAL = ("the call writes into {root}, which no session writes (ACT-OPERATOR-1, path-map.yaml write_refused: "
                 "{why})")


def write_rules(main):
    """ACT-OPERATOR-1 (2d): the main tree's write_refused block (a branch cannot weaken it): a list of entries, each a
    root outside every tree (a real path; not / or HOME), the names directly under it that stay writable (except),
    and why. [] with no block. A block not of that shape raises (fail closed)."""
    try:
        with open(os.path.join(main, PATH_MAP), encoding="utf-8") as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return []
    at = [i for i, line in enumerate(lines) if re.match(WRITE_BLOCK + r"\\s*:", line)]
    if not at:
        return []
    if len(at) > 1:
        raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\\t", "#", "\\n", "\\r")), len(lines))
    from gov.guard.heldout import load_yaml_unique
    data = load_yaml_unique("".join(lines[at[0]:end]))
    block = data.get(WRITE_BLOCK) if isinstance(data, dict) else None
    if not isinstance(block, list) or not block:
        raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK} is not a list of entries")
    out = []
    for e in block:
        top = os.path.expanduser(e.get("root")) if isinstance(e, dict) and isinstance(e.get("root"), str) else ""
        keep = e.get("except") if isinstance(e, dict) else None
        why = e.get("why") if isinstance(e, dict) else None
        if (not os.path.isabs(top) or os.path.realpath(top) in ("/", HOME)
                or not isinstance(keep, list)
                or not all(isinstance(k, str) and k and "/" not in k and k not in (".", "..") for k in keep)
                or not isinstance(why, str) or not why):
            raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK}: an entry is not a root, its open folders and why")
        real = os.path.realpath(top)
        # an open folder by its own name under the real root, never followed: a link there to the rest of the
        # root resolves outside it and stays refused
        out.append((real, [os.path.join(real, k) for k in keep], why))
    return out


def write_refusal(entries, tool, tin, command, cwd):
    """Why this call writes into an entry's root outside its open folders, or "". A file tool by the path it names,
    real (links followed); a Bash line by the writes the guard resolves, the shell's own and its inline code's."""
    targets = []
    if tool in WRITE_TOOLS:
        targets = [tin.get("file_path") or tin.get("notebook_path")]
    elif command is not None:
        shell, code = bash_writes_of(command, cwd)
        targets = shell + code
    for t in targets:
        if not isinstance(t, str) or not t:
            continue
        full = os.path.realpath(os.path.join(cwd or "/", os.path.expanduser(t)))
        for top, keep, why in entries:
            if inside(full, top) and not any(inside(full, k) for k in keep):
                return WRITE_REFUSAL.format(root=top, why=why)
    return ""


'''
CALL_ANCHOR = "    # G-14 (DEC-1052), role separation: what the main tree's path map's role_paths: denies the session's role and\n"
CALL_ADD = '''    # ACT-OPERATOR-1 (2d): folders outside every tree that no session writes (the operator agent's folder but its
    # queue/, the guard's call log), every role, by the writes the guard resolves. Read only for a write tool or Bash.
    if tool in WRITE_TOOLS or command is not None:
        rules_w = write_rules(main)
        if rules_w:
            why = write_refusal(rules_w, tool, tin, command, cwd)
            if why:
                answer("deny", why{RULE})

'''

MAP_ANCHOR = "# The retrieval authority order (DEC-952 item 1, W2-87)"
MAP_ADD = """# write_refused (ACT-OPERATOR-1, rule 2d; DEC-1106 (3), DEC-1104 (2), DEC-1108 (5)): folders outside every tree that no
# session the guard judges writes into, every role: a file tool by the path it names (links followed), a Bash line by
# the writes the guard resolves. `except` names the folders directly under the root that stay writable. The operator
# agent's walled session runs outside this guard. Read from the main tree's copy only.
write_refused:
  - root: "~/gov-os-operator"
    except: [queue]
    why: "the operator agent's folder (its install and commit freeze, its frozen ACTs, log and wall); the CTO writes only queue/ (DEC-1106 (3), OPERATOR-AGENT-1 §1)"
  - root: "~/.gov-os/guard-calls"
    except: []
    why: "the guard's call log, which no session rewrites (DEC-1108 (5))"
"""


def sha(b):
    return hashlib.sha256(b).hexdigest()


def once(text, anchor, what):
    n = text.count(anchor)
    if n != 1:
        sys.exit(f"build.py: the {what} anchor is found {n} times, not once")


def build_hook(src, kind):
    raw = open(src, "rb").read()
    if sha(raw) != WANT[kind]:
        sys.exit(f"build.py: the {kind} base {src} hashes {sha(raw)[:12]}, not {WANT[kind][:12]}")
    text = raw.decode("utf-8")
    for a, w in ((DOC_ANCHOR, "docstring"), (CODE_ANCHOR, "code"), (CALL_ANCHOR, "call")):
        once(text, a, w)
    text = text.replace(DOC_ANCHOR, DOC_ANCHOR + DOC_ADD)
    text = text.replace(CODE_ANCHOR, CODE_ADD + CODE_ANCHOR)
    text = text.replace(CALL_ANCHOR, CALL_ADD.replace("{RULE}", ', "2d"' if kind == "post" else "") + CALL_ANCHOR)
    return raw.decode("utf-8"), text


def write(name, text):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{sha(text.encode())[:12]}  {name}")


def diff(a, b, an, bn):
    return "".join(difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True), an, bn))


for kind, src in (("pre", PRE), ("post", POST)):
    old, new = build_hook(src, kind)
    write(f"pretooluse.{kind}.candidate.py", new)
    write(f"pretooluse.{kind}.diff", diff(old, new, f"a/.claude/hooks/pretooluse.py ({WANT[kind][:12]})",
                                          "b/.claude/hooks/pretooluse.py (+ rule 2d)"))
old = open(MAP, encoding="utf-8").read()
once(old, MAP_ANCHOR, "map")
if "\nwrite_refused:" in old:
    sys.exit("build.py: the live map already has write_refused")
new = old.replace(MAP_ANCHOR, MAP_ADD + MAP_ANCHOR)
print(f"{sha(old.encode())[:12]}  (the live map, the base)")
write("path-map.candidate.yaml", new)
write("path-map.patch", diff(old, new, "a/governance/project/path-map.yaml", "b/governance/project/path-map.yaml"))
