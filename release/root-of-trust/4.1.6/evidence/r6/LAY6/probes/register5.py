#!/usr/bin/env python3
"""AR-0013: derive each legacy binary's full command register (a) from its own CLI by `--help` recursion and (b) from its
own source (`cli/src/main.rs` clap derive enums at the binary's release commit), and cross-check the two.

Written independently of the architect's P3r3 parser and of review r4 C's register.py (neither imported nor copied).
Leaf = a command path with no subcommands. Options are parsed from `Options:`; positionals from `Arguments:`; an option is
"required" when its long form appears in the usage line outside square brackets. Global options are excluded.

Usage: register5.py <scratch-dir> > registers5.json
"""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c5lib as L  # noqa

COMMITS = {"4.1.2": "8ad06be", "4.1.3": "26ab5b6", "4.1.4": "47d8394", "4.1.5": "da9c851"}
GLOBAL = {"--root", "--json", "--session", "--role", "--help", "--version", "-h", "-V"}


def help_of(binary, path, env):
    r = subprocess.run([binary, *path, "--help"], capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
    return (r.stdout or "") + ("\n" + r.stderr if not r.stdout.strip() else "")


def parse_help(text):
    sec, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][a-z]+):\s*(.*)$", line)
        if m and m.group(1) in ("Usage", "Commands", "Arguments", "Options"):
            cur = m.group(1)
            sec[cur] = [m.group(2)] if m.group(2) else []
            continue
        if cur:
            sec[cur].append(line)
    usage = " ".join(s.strip() for s in sec.get("Usage", []) if s.strip())
    subs = []
    for line in sec.get("Commands", []):
        m = re.match(r"^\s{2,}([a-z0-9][a-z0-9-]*)(\s|$)", line)
        if m and m.group(1) != "help":
            subs.append(m.group(1))
    pos = []
    for line in sec.get("Arguments", []):
        m = re.match(r"^\s+(<|\[)([A-Za-z0-9_]+)(>|\])(\.\.\.)?", line)
        if m:
            pos.append({"name": m.group(2), "required": m.group(1) == "<"})
    outside, depth = [], 0
    for ch in usage:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0:
            outside.append(ch)
    outside = "".join(outside)
    opts = []
    for line in sec.get("Options", []):
        m = re.match(r"^\s+(?:-[A-Za-z], )?(--[a-z0-9-]+)(?:[ =]<([A-Za-z0-9_]+)>)?", line)
        if not m or m.group(1) in GLOBAL:
            continue
        opts.append({"long": m.group(1), "value": m.group(2),
                     "required": re.search(r"(^|\s)%s(\s|$)" % re.escape(m.group(1)), outside) is not None})
    return usage, subs, pos, opts


def walk(binary, env):
    leaves, groups = [], []

    def rec(path):
        usage, subs, pos, opts = parse_help(help_of(binary, path, env))
        if subs:
            groups.append({"path": path, "subs": subs})
            for s in subs:
                rec(path + [s])
        else:
            leaves.append({"path": path, "usage": usage, "positionals": pos, "options": opts})
    rec([])
    return leaves, groups


def kebab(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def source_register(commit):
    """Parse `enum Cmd` and every `enum *Cmd` of cli/src/main.rs: variant names -> kebab names; a variant carrying
    `#[command(subcommand)]` (or a field typed `XCmd`) points at that enum."""
    src = subprocess.run(["git", "show", f"{commit}:cli/src/main.rs"], cwd=L.WT, capture_output=True, text=True).stdout
    enums = {}
    for m in re.finditer(r"enum (\w+)\s*\{", src):
        name = m.group(1)
        i, depth = m.end(), 1
        while depth and i < len(src):
            depth += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        body = src[m.end(): i - 1]
        # top-level variants: identifiers at brace depth 0 of the body followed by '{', ',', '(' or end
        variants, d, j, tok = [], 0, 0, ""
        clean = re.sub(r"///[^\n]*|//[^\n]*", "", body)
        clean = re.sub(r"#\[[^\]]*\]", "", clean)
        k = 0
        while k < len(clean):
            ch = clean[k]
            if ch in "{(":
                if d == 0 and tok.strip():
                    variants.append((tok.strip(), clean[k:]))
                    tok = ""
                d += 1
            elif ch in "})":
                d -= 1
            elif ch == "," and d == 0:
                if tok.strip():
                    variants.append((tok.strip(), ""))
                tok = ""
            elif d == 0:
                tok += ch
            k += 1
        if tok.strip():
            variants.append((tok.strip(), ""))
        enums[name] = [v for v in variants if re.match(r"^[A-Z]\w*$", v[0])]
    out = []

    def expand(enum, prefix):
        for vname, rest in enums.get(enum, []):
            # find the variant's own field block text in the original enum body to see if it holds a *Cmd type
            sub = None
            mm = re.match(r"^\{([^{}]*)\}", rest) or re.match(r"^\(([^()]*)\)", rest)
            if mm:
                t = re.search(r":\s*(\w+Cmd)\b", mm.group(1)) or re.search(r"^\s*(\w+Cmd)\s*$", mm.group(1))
                if t and t.group(1) in enums:
                    sub = t.group(1)
            if sub:
                expand(sub, prefix + [kebab(vname)])
            else:
                out.append(prefix + [kebab(vname)])
    expand("Cmd", [])
    return sorted(out), sorted(enums)


def main():
    S = os.path.abspath(sys.argv[1])
    home = os.path.join(S, "register-home")
    env = L.child_env(home, os.path.join(S, "register-cache"))
    res = {}
    for v in L.VERSIONS:
        b = L.BINS[v]
        leaves, groups = walk(b, env)
        help_paths = sorted([x["path"] for x in leaves])
        src_paths, enum_names = source_register(COMMITS[v])
        res[v] = {"sha256": L.sha_file(b), "commit": COMMITS[v],
                  "version_string": subprocess.run([b, "--version"], capture_output=True, text=True, env=env).stdout.strip(),
                  "leaf_count_help": len(leaves), "group_count_help": len(groups), "leaf_count_source": len(src_paths),
                  "in_help_not_source": [p for p in help_paths if p not in src_paths],
                  "in_source_not_help": [p for p in src_paths if p not in help_paths],
                  "source_enums": enum_names, "groups": groups, "leaves": leaves}
    print(L.scrub(json.dumps(res, indent=1)))


if __name__ == "__main__":
    main()
