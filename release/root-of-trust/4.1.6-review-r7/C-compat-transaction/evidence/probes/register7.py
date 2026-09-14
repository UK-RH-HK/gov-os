#!/usr/bin/env python3
"""AR-0021: each legacy binary's full command register, derived independently twice and cross-checked.

(H) From the binary: recursive `--help`. A node is a leaf when its help has no "Commands:" section. Required positionals and
    options come from the leaf's "Usage:" line (tokens outside [...] brackets); all options from "Options:"; positionals from
    "Arguments:".
(S) From the binary's source: `cli/src/main.rs` at the release commit (`git show`), tokenised; clap derive enums are walked from
    `Cmd`; a field with `#[command(subcommand)]` descends; `#[arg(long ...)]` fields are options (bool = flag; Option/Vec/default
    = optional); other fields are positionals.
(E) Environment variables each binary's source reads (`env::var("…")`, `var_os("…")`), and the commands whose root is the
    working directory without `require_installed` (source lines that use `current_dir()` as the root fallback).
Written by AR-0021; not copied from register6.py or any earlier instrument (their counts are compared afterwards, as claims).
Usage: register7.py <out.json>
"""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa

COMMITS = {"4.1.2": "8ad06be", "4.1.3": "26ab5b6", "4.1.4": "47d8394", "4.1.5": "da9c851"}
GLOBAL_OPTS = {"--root", "--json", "--session", "--role", "--help", "--version"}


def helptext(v, path):
    home = os.path.join(L.SCR, "homes", "help7")
    env = L.env_child(home, os.path.join(L.SCR, "caches", "help7"))
    r = subprocess.run([L.BINS[v]] + path + ["--help"], env=env, cwd=home, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    return r.stdout


def parse_help(txt):
    sec, cur = {"_usage": ""}, None
    for line in txt.splitlines():
        if line.startswith("Usage:"):
            sec["_usage"] = line[len("Usage:"):].strip()
            cur = None
            continue
        m = re.match(r"^(Commands|Arguments|Options):\s*$", line)
        if m:
            cur = m.group(1)
            sec[cur] = []
            continue
        if cur and re.match(r"^\s{2,}\S", line):
            if cur == "Commands" and not re.match(r"^\s{2}\S", line):
                continue          # wrapped description lines of a command list
            sec[cur].append(line.strip())
    return sec


def usage_required(usage):
    depth, toks, cur = 0, [], ""
    for ch in usage:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif depth == 0:
            cur += ch
    return cur.split()


def help_register(v):
    leaves = []

    def walk(path):
        sec = parse_help(helptext(v, path))
        subs = [l.split()[0] for l in sec.get("Commands", []) if l.split() and l.split()[0] != "help"]
        if subs:
            for s in subs:
                walk(path + [s])
            return
        req = usage_required(sec["_usage"])
        positionals = []
        for l in sec.get("Arguments", []):
            m = re.match(r"^(<[A-Z0-9_]+>|\[[A-Z0-9_]+\])(\.\.\.)?", l)
            if m:
                nm = m.group(1).strip("<>[]")
                positionals.append({"name": nm, "required": m.group(1).startswith("<")})
        options = []
        for l in sec.get("Options", []):
            m = re.match(r"^(?:-[A-Za-z], )?(--[a-z0-9][a-z0-9-]*)(?: <([A-Z0-9_]+)>)?", l)
            if not m or m.group(1) in GLOBAL_OPTS:
                continue
            options.append({"long": m.group(1), "value": m.group(2), "required": m.group(1) in req})
        leaves.append({"path": path, "positionals": positionals, "options": options})
    walk([])
    return sorted(leaves, key=lambda x: x["path"])


TOK = re.compile(r'"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_]*|#\[|::|->|=>|[{}()\[\]<>,:;=#!&*.?\-+/|@%^~]|\S')


def tokens(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    src = re.sub(r"//[^\n]*", " ", src)
    return TOK.findall(src)


def matching(toks, i, o, c):
    d = 0
    for j in range(i, len(toks)):
        if toks[j] == o:
            d += 1
        elif toks[j] == c:
            d -= 1
            if d == 0:
                return j
    raise ValueError("unbalanced")


def attr_groups(toks, i):
    """Collect #[ ... ] attributes starting at i; return (list of attribute token lists, next index)."""
    attrs = []
    while i < len(toks) and toks[i] == "#[":
        d, j = 1, i + 1
        while d:
            if toks[j] in ("[", "#["):
                d += 1
            elif toks[j] == "]":
                d -= 1
            j += 1
        attrs.append(toks[i + 1:j - 1])
        i = j
    return attrs, i


def split_commas(toks):
    out, cur, d = [], [], 0
    for t in toks:
        if t in ("{", "(", "[", "<", "#["):
            d += 1
        elif t in ("}", ")", "]", ">"):
            d -= 1
        if t == "," and d == 0:
            out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    return [x for x in out if x]


def source_register(v):
    src = subprocess.run(["git", "show", COMMITS[v] + ":cli/src/main.rs"], cwd=L.WT, capture_output=True, text=True, check=True).stdout
    toks = tokens(src)
    enums = {}
    for i, t in enumerate(toks):
        if t == "enum" and i + 2 < len(toks) and toks[i + 2] == "{":
            j = matching(toks, i + 2, "{", "}")
            enums[toks[i + 1]] = toks[i + 3:j]
    leaves = []

    def kebab(n):
        return re.sub(r"(?<!^)([A-Z])", r"-\1", n).lower()

    def walk(ename, path):
        for part in split_commas(enums[ename]):
            vattrs, k = attr_groups(part, 0)
            if k >= len(part):
                continue
            vname = part[k]
            name = kebab(vname)
            for a in vattrs:
                if a and a[0] == "command" and "name" in a:
                    idx = a.index("name")
                    if idx + 2 < len(a) and a[idx + 1] == "=":
                        name = a[idx + 2].strip('"')
            body = []
            if k + 1 < len(part) and part[k + 1] == "{":
                body = part[k + 2:matching(part, k + 1, "{", "}")]
            sub, pos, opts = None, [], []
            for f in split_commas(body):
                fattrs, m = attr_groups(f, 0)
                if m + 2 > len(f) or f[m + 1] != ":":
                    continue
                fname, ftype = f[m], f[m + 2:]
                flat = [x for a in fattrs for x in a]
                if "subcommand" in flat:
                    sub = ftype[0]
                    continue
                argt = [a for a in fattrs if a and a[0] == "arg"]
                at = argt[0] if argt else []
                optional = ftype[0] in ("Option", "Vec") or "default_value" in at or "default_value_t" in at
                if "long" in at:
                    li = at.index("long")
                    long = "--" + (at[li + 2].strip('"') if li + 2 < len(at) and at[li + 1] == "=" else fname.replace("_", "-"))
                    is_flag = ftype == ["bool"]
                    opts.append({"long": long, "value": None if is_flag else fname.upper(), "required": not (is_flag or optional)})
                else:
                    pos.append({"name": fname.upper(), "required": not optional})
            if sub:
                walk(sub, path + [name])
            else:
                leaves.append({"path": path + [name], "positionals": pos, "options": opts})
    walk("Cmd", [])
    return sorted(leaves, key=lambda x: x["path"]), src


def env_and_cwd(src, v):
    envs = sorted(set(re.findall(r'var(?:_os)?\("([A-Z][A-Z0-9_]+)"\)', src)))
    runtime_envs = sorted(set(re.findall(r'var(?:_os)?\("(GOV_[A-Z0-9_]+)"\)', subprocess.run(["git", "grep", "-h", "env::var", COMMITS[v], "--", "runtime/src", "cli/src"], cwd=L.WT, capture_output=True, text=True).stdout)))
    cwd_lines = [l.strip()[:160] for l in src.splitlines() if "current_dir()" in l]
    return {"cli_env": envs, "gov_env_all_sources": runtime_envs, "current_dir_lines": cwd_lines}


def main():
    out = {}
    for v in L.VERSIONS:
        h = help_register(v)
        s, src = source_register(v)
        hp = {tuple(x["path"]): x for x in h}
        sp = {tuple(x["path"]): x for x in s}
        diffs = []
        for p in sorted(set(hp) & set(sp)):
            ho = sorted((o["long"], o["value"] is None, o["required"]) for o in hp[p]["options"])
            so = sorted((o["long"], o["value"] is None, o["required"]) for o in sp[p]["options"])
            hpos = [x["required"] for x in hp[p]["positionals"]]
            spos = [x["required"] for x in sp[p]["positionals"]]
            if ho != so or hpos != spos:
                diffs.append({"path": list(p), "only_help": sorted(set(ho) - set(so)), "only_source": sorted(set(so) - set(ho)), "help_pos": hpos, "source_pos": spos})
        out[v] = {"commit": COMMITS[v], "binary_sha256": L.fsha(L.BINS[v]), "leaves": h, "source_leaves": s,
                  "counts": {"leaves_help": len(h), "leaves_source": len(s), "options_help": sum(len(x["options"]) for x in h),
                             "options_source": sum(len(x["options"]) for x in s), "positionals_help": sum(len(x["positionals"]) for x in h)},
                  "leaf_paths_only_help": sorted(" ".join(p) for p in set(hp) - set(sp)),
                  "leaf_paths_only_source": sorted(" ".join(p) for p in set(sp) - set(hp)), "option_differences": diffs, "env": env_and_cwd(src, v)}
    L.dump(out, sys.argv[1])
    print(json.dumps({v: dict(out[v]["counts"], only_help=out[v]["leaf_paths_only_help"], only_source=out[v]["leaf_paths_only_source"],
                              option_differences=len(out[v]["option_differences"]), gov_env=out[v]["env"]["gov_env_all_sources"]) for v in out}, indent=1))


if __name__ == "__main__":
    main()
