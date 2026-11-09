#!/usr/bin/env python3
"""The operator agent's classifier (OPERATOR-AGENT-1 §2 and §3, DEC-1104 (2)): the code's vote on an ACT's class.

    python3 act_class.py <bundle dir>

Reads <bundle dir>/manifest.json (every touched file with its before and after sha256, every command) and the
bundle's files (before/<root>/<path>, after/<root>/<path>, apply.sh), with class-rules.yaml beside this file, and
prints one JSON object: {"class": "a"|"b"|"O", "files": [...], "hits": [...], "why": "..."}.

- Each touched file takes the class of the first rule-table row that names it; an unknown path is (O).
- A list-shaped file is parsed before and after, and is (a) only when the only differences are the ones its row
  allows (items added to a named refusal or coupling list, lines removed from an opt-in list); a file that cannot be
  parsed, or that the bundle does not hold as hashed, is never (a).
- apply.sh, the manifest's `commands` and its checks' cmds are scanned: sudo, git push, git tag, history prunes, rm
  outside the project and Windows-side steps raise the class to (O); installs and network calls to non-local hosts to
  (b).
- The ACT's class is the highest among its files and its hits. Fails closed: a manifest it cannot read is (O).
Standalone: the standard library and PyYAML.
"""
import json
import os
import re
import shlex
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RANK = {"a": 0, "b": 1, "O": 2}
LIVE_REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0", "[::1]"}


def top(*classes):
    vs = [c if c in RANK else "O" for c in classes] or ["a"]
    return max(vs, key=RANK.get)


# ------------------------------------------------------------------------------------------------------------- rules
def load_rules(path=None):
    with open(path or os.path.join(HERE, "class-rules.yaml"), encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    if not isinstance(rules, dict) or not isinstance(rules.get("rows"), list) or not rules["rows"]:
        raise ValueError("class-rules.yaml holds no rows")
    for r in rules["rows"]:
        if not isinstance(r, dict) or not isinstance(r.get("match"), list):
            raise ValueError(f"a malformed row in class-rules.yaml: {r!r}")
        if "class" not in r and "list" not in r:
            raise ValueError(f"row {r.get('id')} has neither class nor list")
    return rules


_GLOB_CACHE = {}


def glob_re(pattern):
    """allowed_paths' reading: ** any characters including /, * any characters but /, the rest literal."""
    rx = _GLOB_CACHE.get(pattern)
    if rx is None:
        out, i = [], 0
        while i < len(pattern):
            if pattern.startswith("**", i):
                out.append(".*")
                i += 2
            elif pattern[i] == "*":
                out.append("[^/]*")
                i += 1
            else:
                out.append(re.escape(pattern[i]))
                i += 1
        rx = _GLOB_CACHE[pattern] = re.compile("^" + "".join(out) + "$")
    return rx


def row_for(rules, root, path):
    for r in rules["rows"]:
        for m in r["match"]:
            if m.get("root") == root and glob_re(str(m.get("path"))).match(path):
                return r
    return None


# ------------------------------------------------------------------------------------------------- list-shaped files
def strip_jsonc(text):
    """JSON with comments: // and /* */ outside strings removed, trailing commas dropped."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                raise ValueError("an unclosed comment")
            i = j + 2
        else:
            out.append(c)
            i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def parse(kind, data):
    text = data.decode("utf-8")
    if kind == "yaml":
        doc = yaml.safe_load(text)
    elif kind == "json":
        doc = json.loads(text)
    elif kind == "jsonc":
        doc = json.loads(strip_jsonc(text))
    else:
        raise ValueError(f"unknown list kind {kind}")
    if not isinstance(doc, dict):
        raise ValueError("the file is not a mapping")
    return doc


def spec_match(path, specs):
    for s in specs or []:
        parts = s.split(".")
        if len(parts) == len(path) and all(p == "*" and q != "[]" or p == q for p, q in zip(parts, path)):
            return True
    return False


def subsequence(old, new):
    it = iter(new)
    return all(any(o == x for x in it) for o in old)


def compare(old, new, path, lst):
    """True when new differs from old only as the row's `list` allows."""
    if spec_match(path, lst.get("only_added")):
        return isinstance(old, list) and isinstance(new, list) and subsequence(old, new)
    if spec_match(path, lst.get("free")):
        return True
    if spec_match(path, lst.get("only_added_deny")):
        if not isinstance(old, dict) or not isinstance(new, dict):
            return False
        return all(k in new and new[k] == v for k, v in old.items()) and \
            all(v == "deny" for k, v in new.items() if k not in old)
    if isinstance(old, dict) and isinstance(new, dict):
        for k, v in old.items():
            if k not in new or not compare(v, new[k], path + [str(k)], lst):
                return False
        extra = [k for k in new if k not in old]
        if extra:
            if not spec_match(path, lst.get("new_entries")):
                return False
            need = (lst.get("new_entry_needs") or {}).get(".".join(path))
            for k in extra:
                if need and not (isinstance(new[k], dict) and new[k].get(need)):
                    return False
        return True
    if isinstance(old, list) and isinstance(new, list) and spec_match(path, lst.get("appendable")):
        return len(new) >= len(old) and all(compare(o, n, path + ["[]"], lst) for o, n in zip(old, new))
    return old == new


def list_class(row, before, after):
    """(class, why) for a list-shaped file, given its bytes before and after (None: absent or not held)."""
    lst, other = row["list"], row.get("else", "b")
    if before is None or after is None:
        return other, "created, deleted or not held in the bundle as hashed: never (a)"
    kind = lst.get("kind")
    try:
        if kind == "lines_removed":
            o, n = before.decode("utf-8").splitlines(), after.decode("utf-8").splitlines()
            return ("a", "lines only removed") if subsequence(n, o) else (other, "lines added or changed")
        o, n = parse(kind, before), parse(kind, after)
    except (ValueError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return other, f"cannot be parsed ({exc.__class__.__name__}): never (a)"
    for k in lst.get("ratchet") or []:
        if o.get(k) != n.get(k):
            return row.get("ratchet_class", "O"), f"a change to {k}, read only from the owner's commits"
    if compare(o, n, [], lst):
        return "a", "only the additions the row allows"
    return other, "a change the row does not allow as (a)"


# ------------------------------------------------------------------------------------------------------ script hits
WRAPPERS = {"env", "nohup", "setsid", "timeout", "nice", "ionice", "exec", "command", "time", "stdbuf", "taskset",
            "flock", "xargs", "builtin", "chrt"}
INSTALLERS = {"pip", "pip3", "pipx", "uv", "npm", "yarn", "pnpm", "apt", "apt-get", "dnf", "yum", "brew", "cargo",
              "gem", "go", "conda", "mamba", "snap", "flatpak", "dpkg", "rpm", "poetry"}
NETWORK = {"curl", "wget", "aria2c", "ssh", "scp", "sftp", "ftp", "nc", "ncat", "telnet", "http", "https"}
WINDOWS = {"powershell.exe", "pwsh.exe", "pwsh", "cmd.exe", "schtasks.exe", "schtasks", "wsl.exe", "reg.exe",
           "explorer.exe", "wscript.exe", "cscript.exe"}


def url_host(tok):
    m = re.search(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://(\[[^\]]+\]|[^/:@\s]+@)?(\[[^\]]+\]|[^/:\s'\"]+)", tok)
    if not m:
        return None
    return m.group(2).lower()


def is_local(host):
    return host in LOCAL_HOSTS or host.endswith(".localhost")


def rm_outside(arg, repo=LIVE_REPO):
    a = arg.strip("'\"")
    if not a or a.startswith("-"):
        return False
    if a.startswith(("$TMPDIR", "${TMPDIR", "$TMP/", "${TMP}", "$tmp", "${tmp")):
        return False
    if a.startswith(("~", "$HOME", "${HOME")):
        return True
    if a.startswith("$"):
        return False                       # a variable the scan cannot place: left to the dry run's changed set
    if a.startswith("/"):
        p = os.path.normpath(a)
        return not (p.startswith(("/tmp/", "/var/tmp/")) or p in ("/tmp", "/dev/null") or
                    p == repo or p.startswith(repo + "/"))
    return a == ".." or a.startswith("../") or "/../" in a


def segments(line):
    """The simple commands of one shell line, as token lists; None when the line cannot be tokenised."""
    line = line.replace("`", " ; ").replace("$(", " ; ( ")
    try:
        lex = shlex.shlex(line, posix=True, punctuation_chars=";&|()<>")
        lex.whitespace_split = True
        lex.commenters = "#"
        toks = list(lex)
    except ValueError:
        return None
    segs, cur = [], []
    for t in toks:
        if t and all(c in ";&|()<>" for c in t):
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        segs.append(cur)
    return segs


def strip_wrappers(toks):
    i = 0
    while i < len(toks):
        t = toks[i]
        b = os.path.basename(t)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            i += 1
        elif b in ("sudo", "doas"):
            return toks[i:]
        elif b in WRAPPERS:
            i += 1
            while i < len(toks) and (toks[i].startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i])
                                     or (b in ("timeout",) and re.match(r"^\d+[smhd]?$", toks[i]))
                                     or (b == "nice" and re.match(r"^-?\d+$", toks[i]))
                                     or (b == "taskset" and re.match(r"^[0-9,-]+$", toks[i]))
                                     or (b == "env" and toks[i - 1] == "-u")):
                if toks[i] in ("-n", "-c", "-u", "-k", "-s", "--kill-after", "--signal") and i + 1 < len(toks):
                    i += 1
                i += 1
            if b == "flock" and i < len(toks):
                i += 1                     # flock <lock file> <command>
        else:
            break
    return toks[i:]


def git_sub(toks):
    i = 1
    while i < len(toks):
        t = toks[i]
        if t in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            i += 2
        elif t.startswith("-"):
            i += 1
        else:
            return t, toks[i + 1:]
    return None, []


def scan_segment(toks, out, depth=0):
    toks = strip_wrappers(toks)
    if not toks:
        return
    cmd = os.path.basename(toks[0])
    args = toks[1:]
    joined = " ".join(toks)
    if "/mnt/c/" in joined or ".wslconfig" in joined or cmd.lower() in WINDOWS:
        out.append(("windows", joined))
    if cmd in ("sudo", "doas"):
        out.append(("sudo", joined))
        scan_segment(args, out, depth)
        return
    if cmd in ("bash", "sh", "zsh", "dash") and "-c" in args and depth < 3:
        k = args.index("-c")
        if k + 1 < len(args):
            scan_text(args[k + 1], out, depth + 1)
        return
    if cmd.startswith("python") and "-c" in args:
        for a in args:
            h = url_host(a)
            if h and not is_local(h):
                out.append(("network", joined))
        if re.search(r"\bpip\b.*\binstall\b", joined):
            out.append(("install", joined))
    if cmd.startswith("python") and "-m" in args:
        k = args.index("-m")
        mod = args[k + 1] if k + 1 < len(args) else ""
        if mod in ("pip", "pipx") and "install" in args[k + 2:]:
            out.append(("install", joined))
        if mod in ("http.server",):
            out.append(("network", joined))
    if cmd == "git":
        sub, rest = git_sub(toks)
        if sub == "push":
            out.append(("push", joined))
        elif sub == "tag":
            out.append(("tag", joined))
        elif sub in ("filter-branch", "filter-repo", "replace"):
            out.append(("history", joined))
        elif sub == "reflog" and "expire" in rest:
            out.append(("history", joined))
        elif sub == "gc" and any(a.startswith("--prune") for a in rest):
            out.append(("history", joined))
        elif sub == "update-ref" and "-d" in rest:
            out.append(("history", joined))
        elif sub == "branch" and ("-D" in rest or "--delete" in rest and "--force" in rest):
            out.append(("history", joined))
        elif sub in ("fetch", "pull", "ls-remote"):
            if any(not a.startswith(("-", "/", ".", "~")) for a in rest) or not rest:
                out.append(("network", joined))
        elif sub == "clone":
            for a in rest:
                h = url_host(a)
                if (h and not is_local(h)) or re.match(r"^[\w.-]+@[\w.-]+:", a):
                    out.append(("network", joined))
        return
    if cmd in INSTALLERS:
        subs = [a for a in args if not a.startswith("-")]
        if cmd in ("dpkg", "rpm") and any(a in ("-i", "--install", "-U") for a in args):
            out.append(("install", joined))
        elif subs and subs[0] in ("install", "i", "add", "ci", "get", "sync", "upgrade"):
            out.append(("install", joined))
        elif cmd == "uv" and len(subs) > 1 and subs[0] in ("pip", "tool") and subs[1] in ("install", "sync"):
            out.append(("install", joined))
        return
    if cmd in ("npx", "uvx", "pipx"):
        out.append(("install", joined))
        return
    if cmd in NETWORK:
        hosts = [url_host(a) for a in args]
        hosts = [h for h in hosts if h]
        if cmd in ("curl", "wget", "aria2c", "http", "https"):
            if not hosts or any(not is_local(h) for h in hosts):
                out.append(("network", joined))
        else:
            out.append(("network", joined))
        return
    if cmd == "rsync" and any(re.match(r"^[\w.-]+(@[\w.-]+)?:", a) for a in args):
        out.append(("network", joined))
    if cmd in ("rm", "rmdir", "shred", "unlink"):
        if any(rm_outside(a) for a in args):
            out.append(("rm-outside", joined))
    if cmd == "find" and ("-delete" in args or ("-exec" in args and any(os.path.basename(a) == "rm" for a in args))):
        roots = [a for a in args if not a.startswith("-")][:1]
        if any(rm_outside(r) for r in roots):
            out.append(("rm-outside", joined))


def scan_text(text, out, depth=0):
    if not isinstance(text, str):
        return
    logical = re.sub(r"\\\n", " ", text)
    for line in logical.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        segs = segments(line)
        if segs is None:                   # fail closed: the raw line, by word
            for kind, rx in (("sudo", r"(^|[\s;&|(`])sudo\s"), ("push", r"\bgit\b.*\bpush\b"),
                             ("tag", r"\bgit\b\s+(-C\s+\S+\s+)?tag\b"), ("install", r"\b(pip3?|npm|apt(-get)?)\s+install\b"),
                             ("windows", r"powershell\.exe|/mnt/c/|cmd\.exe"), ("history", r"filter-branch|reflog expire")):
                if re.search(rx, line):
                    out.append((kind, line.strip()))
            if re.search(r"\b(curl|wget)\b", line):
                hosts = [url_host(t) for t in line.split()]
                if not any(hosts) or any(h and not is_local(h) for h in hosts):
                    out.append(("network", line.strip()))
            continue
        for seg in segs:
            scan_segment(seg, out, depth)


# -------------------------------------------------------------------------------------------------------- classify
def held(bundle, side, root, path, want):
    """The bytes of before/ or after/ in the bundle when they hash as the manifest says; else None."""
    if want is None:
        return None
    full = os.path.join(bundle, side, root, path)
    if not os.path.isfile(full) or os.path.islink(full):
        return None
    with open(full, "rb") as f:
        data = f.read()
    import hashlib
    return data if hashlib.sha256(data).hexdigest() == want else None


def classify_manifest(manifest, bundle=None, rules=None):
    rules = rules or load_rules()
    files, hits, why = [], [], []
    touched = manifest.get("touched")
    if not isinstance(touched, list):
        raise ValueError("the manifest's touched list is missing")
    for t in touched:
        if not isinstance(t, dict):
            raise ValueError("a touched entry is not an object")
        root, path = t.get("root"), t.get("path")
        if root not in ("repo", "home", "crontab") or not isinstance(path, str) or not path or path.startswith("/") \
                or ".." in path.split("/"):
            files.append({"root": root, "path": path, "class": "O", "row": None, "why": "not a touched file's form"})
            continue
        row = row_for(rules, root, path)
        if row is None:
            files.append({"root": root, "path": path, "class": "O", "row": None, "why": "a path no rule names"})
            continue
        if "list" in row:
            before = held(bundle, "before", root, path, t.get("before")) if bundle else None
            after = held(bundle, "after", root, path, t.get("after")) if bundle else None
            if t.get("before") is not None and t.get("before") == t.get("after"):
                cls, w = "a", "unchanged"
            else:
                cls, w = list_class(row, before, after)
        else:
            cls, w = row["class"], row.get("why", "")
        files.append({"root": root, "path": path, "class": cls, "row": row.get("id"), "why": w})
    texts = []
    if bundle and os.path.isfile(os.path.join(bundle, "apply.sh")):
        with open(os.path.join(bundle, "apply.sh"), encoding="utf-8", errors="replace") as f:
            texts.append(f.read())
    cmds = manifest.get("commands") or []
    if not isinstance(cmds, list):
        raise ValueError("the manifest's commands are not a list")
    texts += [c for c in cmds if isinstance(c, str)]
    for c in manifest.get("checks") or []:
        if isinstance(c, dict) and isinstance(c.get("cmd"), str):
            texts.append(c["cmd"])
    raw = []
    for t in texts:
        scan_text(t, raw)
    hit_class = rules.get("hits") or {}
    seen = set()
    for kind, line in raw:
        if (kind, line) in seen:
            continue
        seen.add((kind, line))
        hits.append({"kind": kind, "class": hit_class.get(kind, "O"), "line": line[:200]})
    cls = top(*([f["class"] for f in files] + [h["class"] for h in hits] or ["a"]))
    for f in files:
        if f["class"] == cls:
            why.append(f"{f['root']}:{f['path']} ({f['row']}: {f['why']})")
    for h in hits:
        if h["class"] == cls:
            why.append(f"script hit {h['kind']}: {h['line'][:80]}")
    return {"class": cls, "files": files, "hits": hits, "why": "; ".join(why) or "nothing that governs agents"}


def classify(bundle, rules=None):
    """The code's vote for a bundle folder. Fails closed: anything unreadable is (O)."""
    try:
        with open(os.path.join(bundle, "manifest.json"), "rb") as f:
            manifest = json.loads(f.read().decode("utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("the manifest is not an object")
        return classify_manifest(manifest, bundle, rules)
    except Exception as exc:  # fail closed
        return {"class": "O", "files": [], "hits": [], "why": f"the bundle cannot be classified ({exc}): (O)"}


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: act_class.py <bundle dir>\n")
        print(json.dumps({"class": "O", "files": [], "hits": [], "why": "usage"}))
        return 2
    print(json.dumps(classify(argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
