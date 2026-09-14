#!/usr/bin/env python3
"""AR-0017: each legacy binary's full command register, derived twice and cross-checked.

(1) From the binary itself: `gov --help` recursion (clap help), parsing `Commands:`, `Arguments:` and `Options:`.
(2) From the binary's own source: `cli/src/main.rs` at its release commit (`git show`), parsing the clap derive enums
    (compact single-line enums of 4.1.2/4.1.3 and multi-line enums of 4.1.4/4.1.5; `#[arg(long)]`, `#[arg(long = "x")]`,
    `default_value`, `#[command(subcommand)]`, positional fields).
Output: registers6.json {version: {leaves: [{path, positionals:[{name, required}], options:[{long, value, required}]}], ...},
cross-check}. Written by AR-0017; not derived from P3r3, ST5, review r4 C or review r5 C instruments.
Usage: register6.py <out.json>
"""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c6lib as L  # noqa

COMMITS = {"4.1.2": "8ad06be", "4.1.3": "26ab5b6", "4.1.4": "47d8394", "4.1.5": "da9c851"}
GLOBAL = {"--root", "--json", "--session", "--role", "--help", "--version", "-h", "-V"}


# ------------------------------------------------------------------------------------------------ help recursion
def help_text(v, path):
    env = L.child_env(os.path.join(L.SCR, "homes", "help"), os.path.join(L.SCR, "caches", "help"))
    r = subprocess.run([L.BINS[v]] + list(path) + ["--help"], env=env, cwd=os.path.join(L.SCR, "homes", "help"),
                       capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    return r.stdout


def sections(txt):
    out, cur = {}, None
    for line in txt.splitlines():
        m = re.match(r"^([A-Z][A-Za-z ]+):\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if cur and line.startswith("  "):
            out[cur].append(line)
    return out


def help_register(v):
    leaves = []

    def walk(path):
        s = sections(help_text(v, path))
        cmds = []
        for l in s.get("Commands", []):
            m = re.match(r"^  (\S+)\s", l + " ")
            if m and m.group(1) != "help" and not l.startswith("   "):
                cmds.append(m.group(1))
        if cmds:
            for c in cmds:
                walk(path + [c])
            return
        pos = []
        for l in s.get("Arguments", []):
            m = re.match(r"^\s+(<([A-Z_0-9]+)>|\[([A-Z_0-9]+)\])", l)
            if m:
                pos.append({"name": m.group(2) or m.group(3), "required": bool(m.group(2))})
        opts = []
        for l in s.get("Options", []):
            m = re.match(r"^\s+(?:-\w, )?(--[a-z0-9-]+)(?: <([A-Z_0-9]+)>)?", l)
            if m and m.group(1) not in GLOBAL:
                opts.append({"long": m.group(1), "value": m.group(2), "required": False})
        usage = help_text(v, path).splitlines()[0:6]
        u = " ".join(x for x in usage if x.startswith("Usage:"))
        for o in opts:
            if re.search(r"(?<!\[)%s(?: <[A-Z_0-9]+>)?(?!\])" % re.escape(o["long"]), u) and "[" + o["long"] not in u:
                o["required"] = True
        leaves.append({"path": path, "positionals": pos, "options": opts})
    walk([])
    return sorted(leaves, key=lambda x: x["path"])


# ------------------------------------------------------------------------------------------------ source parser
def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", l) for l in src.splitlines())


def block(src, start):
    """Return the text between the brace at `start` and its match."""
    depth, i = 0, start
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1:i]
        i += 1
    raise ValueError("unbalanced")


def split_top(s):
    parts, depth, cur, ang = [], 0, "", 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth -= 1
        elif ch == "<":
            ang += 1
        elif ch == ">" and ang:
            ang -= 1
        elif ch == '"':
            j = s.index('"', i + 1)
            cur += s[i:j + 1]
            i = j + 1
            continue
        if ch == "," and depth == 0 and ang == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def kebab(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def attrs_and_rest(s):
    attrs = []
    s = s.strip()
    while s.startswith("#["):
        depth, i = 0, 1
        while True:
            if s[i] == "[":
                depth += 1
            elif s[i] == "]":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        attrs.append(s[2:i])
        s = s[i + 1:].strip()
    return attrs, s


def source_register(v):
    src = strip_comments(subprocess.run(["git", "show", COMMITS[v] + ":cli/src/main.rs"], cwd=L.WT, capture_output=True, text=True, check=True).stdout)
    enums = {}
    for m in re.finditer(r"enum\s+(\w+)\s*\{", src):
        enums[m.group(1)] = block(src, m.end() - 1)

    def variants(ename):
        out = []
        for part in split_top(enums[ename]):
            attrs, rest = attrs_and_rest(part)
            m = re.match(r"(\w+)\s*(\{(.*)\})?\s*$", rest, re.S)
            if not m:
                continue
            out.append((m.group(1), attrs, split_top(m.group(3)) if m.group(3) is not None else []))
        return out

    leaves = []

    def walk(ename, path):
        for vname, vattrs, fields in variants(ename):
            name = kebab(vname)
            for a in vattrs:
                mm = re.search(r'name\s*=\s*"([^"]+)"', a)
                if mm and a.startswith("command"):
                    name = mm.group(1)
            sub, pos, opts = None, [], []
            for f in fields:
                fattrs, frest = attrs_and_rest(f)
                mm = re.match(r"(\w+)\s*:\s*(.+)$", frest, re.S)
                if not mm:
                    continue
                fname, ftype = mm.group(1), mm.group(2).strip()
                joined = " ".join(fattrs)
                if "subcommand" in joined:
                    sub = ftype
                    continue
                argattr = [a for a in fattrs if a.startswith("arg(")]
                a0 = argattr[0] if argattr else ""
                has_long = bool(re.search(r"\blong\b", a0))
                default = "default_value" in a0
                if has_long:
                    lm = re.search(r'long\s*=\s*"([^"]+)"', a0)
                    long = "--" + (lm.group(1) if lm else fname.replace("_", "-"))
                    is_flag = ftype == "bool"
                    required = not (is_flag or ftype.startswith("Option<") or ftype.startswith("Vec<") or default)
                    opts.append({"long": long, "value": None if is_flag else fname.upper(), "required": required})
                else:
                    required = not (ftype.startswith("Option<") or ftype.startswith("Vec<") or default)
                    pos.append({"name": fname.upper(), "required": required})
            if sub:
                walk(sub, path + [name])
            else:
                leaves.append({"path": path + [name], "positionals": pos, "options": opts})
    walk("Cmd", [])
    return sorted(leaves, key=lambda x: x["path"])


def main():
    out = {}
    for v in L.VERSIONS:
        h, s = help_register(v), source_register(v)
        hp = {tuple(x["path"]): x for x in h}
        sp = {tuple(x["path"]): x for x in s}
        opt_diff = []
        for p in set(hp) & set(sp):
            ho = {(o["long"], o["value"] is None) for o in hp[p]["options"]}
            so = {(o["long"], o["value"] is None) for o in sp[p]["options"]}
            hpos = [x["required"] for x in hp[p]["positionals"]]
            spos = [x["required"] for x in sp[p]["positionals"]]
            hreq = {o["long"] for o in hp[p]["options"] if o["required"]}
            sreq = {o["long"] for o in sp[p]["options"] if o["required"]}
            if ho != so or hpos != spos or hreq != sreq:
                opt_diff.append({"path": list(p), "help_opts": sorted(ho), "source_opts": sorted(so), "help_pos": hpos, "source_pos": spos,
                                 "help_required": sorted(hreq), "source_required": sorted(sreq)})
        out[v] = {"binary_sha256": L.sha_file(L.BINS[v]), "commit": COMMITS[v], "leaves": h,
                  "leaf_count_help": len(h), "leaf_count_source": len(s),
                  "option_count_help": sum(len(x["options"]) for x in h), "option_count_source": sum(len(x["options"]) for x in s),
                  "positional_count_help": sum(len(x["positionals"]) for x in h),
                  "in_help_not_source": sorted(" ".join(p) for p in set(hp) - set(sp)),
                  "in_source_not_help": sorted(" ".join(p) for p in set(sp) - set(hp)),
                  "option_or_positional_differences": opt_diff,
                  "cwd_rooted_non_install_families": sorted({" ".join(x["path"][:2]) for x in h if x["path"][0] == "init" or x["path"][:2] in (["adopt", "baseline"], ["migrate", "baseline"])})}
    L.dump(out, sys.argv[1])
    print(json.dumps({v: {k: out[v][k] for k in ("leaf_count_help", "leaf_count_source", "option_count_help", "option_count_source",
                                                  "in_help_not_source", "in_source_not_help")} | {"diffs": len(out[v]["option_or_positional_differences"])} for v in out}, indent=1))


if __name__ == "__main__":
    main()
