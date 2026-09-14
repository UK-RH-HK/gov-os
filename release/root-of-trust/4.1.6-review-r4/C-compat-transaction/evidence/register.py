#!/usr/bin/env python3
"""AR-0007: derive each legacy binary's full command register from its own CLI (`--help` recursion), independently of the
architect's P3r3 parser. Output: {version: {sha256, version_string, groups[], leaves[{path, usage, positionals[], options[]}]}}.
A leaf is a command with no subcommands. Positionals come from the `Arguments:` section and the usage line; options from
`Options:` (global options --root/--json/--session/--role/--help/--version are excluded). An option is required when it
appears in the usage line outside brackets.
Usage: register.py <scratch-dir> > registers.json
"""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import BINS, VERSIONS, child_env, scrub  # noqa

GLOBAL = {"--root", "--json", "--session", "--role", "--help", "--version"}


def helptext(binary, path, env):
    r = subprocess.run([binary, *path, "--help"], capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
    return r.stdout if r.stdout.strip() else r.stderr


def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^(Usage|Commands|Arguments|Options):\s*(.*)$", line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(2)] if m.group(2) else []
        elif cur:
            out[cur].append(line)
    return out


def parse(text):
    s = sections(text)
    usage = " ".join(x.strip() for x in s.get("Usage", []) if x.strip())
    subs = []
    for line in s.get("Commands", []):
        m = re.match(r"^  ([a-z0-9][a-z0-9-]*)\b", line)
        if m and m.group(1) != "help":
            subs.append(m.group(1))
    pos = []
    for line in s.get("Arguments", []):
        m = re.match(r"^\s+([<\[])([A-Za-z0-9_]+)[>\]](\.\.\.)?", line)
        if m:
            pos.append({"name": m.group(2), "required": m.group(1) == "<", "multiple": bool(m.group(3))})
    # required options: tokens "--x <V>" in the usage line that are not inside [...]
    depth, outside = 0, []
    for ch in usage:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0:
            outside.append(ch)
    outside = "".join(outside)
    opts = []
    for line in s.get("Options", []):
        m = re.match(r"^\s+(?:-([A-Za-z]), )?--([a-z0-9-]+)(?:[ =]<([A-Za-z0-9_]+)>(\.\.\.)?)?", line)
        if not m or "--" + m.group(2) in GLOBAL:
            continue
        long = "--" + m.group(2)
        opts.append({"long": long, "value": m.group(3), "required": bool(re.search(r"(^|\s)%s(\s|$)" % re.escape(long), outside))})
    return usage, subs, pos, opts


def register(binary, env):
    groups, leaves = [], []

    def walk(path):
        usage, subs, pos, opts = parse(helptext(binary, path, env))
        if subs:
            groups.append({"path": path, "subcommands": subs})
            for x in subs:
                walk(path + [x])
        else:
            leaves.append({"path": path, "usage": usage, "positionals": pos, "options": opts})
    walk([])
    return {"groups": groups, "leaves": leaves}


if __name__ == "__main__":
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S, exist_ok=True)
    env = child_env(S, "register")
    out = {}
    for v in VERSIONS:
        b = BINS[v]
        reg = register(b, env)
        out[v] = {"sha256": hashlib.sha256(open(b, "rb").read()).hexdigest(),
                  "version_string": subprocess.run([b, "--version"], capture_output=True, text=True, env=env).stdout.strip(),
                  "leaf_count": len(reg["leaves"]), "group_count": len(reg["groups"]), **reg}
    print(scrub(json.dumps(out, indent=1), S))
