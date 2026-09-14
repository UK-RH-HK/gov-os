#!/usr/bin/env python3
"""AR-0007 (independent compatibility/transaction review C of RoT-1 revision 4) probe library.

Independent of the architect's P3r3/LR2 harnesses and of review r3's C/D probes (no code copied).
Hygiene: scratch only; every child environment has GOV_* removed; HOME, XDG_* and GOV_KERNEL_CACHE point into scratch;
Git runs with GIT_CONFIG_NOSYSTEM=1 and GIT_OPTIONAL_LOCKS=0 so that observing Git state does not rewrite the index.

Whole-tree snapshots record EVERY entry under the project root, including `.governance-runtime/` and `.git/`, with entry
type, permission bits, size and SHA-256 (files) or target (links). Nothing is excluded by name; results are reported per
partition (work tree / runtime / git) so no write is hidden by a named-path choice.
"""
import hashlib, json, os, shutil, stat, subprocess, time

SCRATCHPAD = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad"
WT = os.environ.get("AR7_WT", SCRATCHPAD + "/wt/review-r4-c")
LEG = os.environ.get("AR7_LEGACY_BIN", SCRATCHPAD + "/legacy-bin")
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
MARK = "AR0007RESTRICTEDMARKER"
CLEANPATH = "/usr/bin:/bin:/usr/local/bin"
VERSIONS = ("4.1.2", "4.1.3", "4.1.4", "4.1.5")
BINS = {v: os.path.join(LEG, f"gov-{v}") for v in VERSIONS}
REL = {v: os.path.join(WT, "release", "releases", v) for v in VERSIONS}
FORMAT_BYTES = b'{"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}'
# 26 §2 / 08 §2 occupation entries and their required types
OCCUPATION = {"governance/kernel": "file", "governance/project": "file", "governance/generated": "file",
              "governance/framework.lock": "dir", "spec/audits/GOVERNANCE-ADOPTION": "file",
              ".governance-runtime/migration": "file"}
TRUST_TOP_ALLOWED = {"FORMAT", "framework.lock", "kernel", "release.dsse.json", "lineage", "state", "root", "profiles",
                     "development.json"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def child_env(scratch, tag, extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    home = os.path.join(scratch, "homes", tag)
    os.makedirs(home, exist_ok=True)
    env.update({"PATH": CLEANPATH, "HOME": home, "GOV_KERNEL_CACHE": os.path.join(scratch, "caches", tag),
                "XDG_CACHE_HOME": os.path.join(home, ".cache"), "XDG_CONFIG_HOME": os.path.join(home, ".config"),
                "XDG_STATE_HOME": os.path.join(home, ".local", "state"), "XDG_DATA_HOME": os.path.join(home, ".local", "share"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "ar7", "GIT_AUTHOR_EMAIL": "ar7@x",
                "GIT_COMMITTER_NAME": "ar7", "GIT_COMMITTER_EMAIL": "ar7@x", "PYTHONDONTWRITEBYTECODE": "1",
                "AR7_MARKER": os.path.join(scratch, "markers", tag)})
    os.makedirs(os.path.join(scratch, "markers"), exist_ok=True)
    for k in list(env):
        if k.startswith("GOV_") and k != "GOV_KERNEL_CACHE":
            del env[k]
    if extra:
        env.update(extra)
    return env


def git_env(home):
    return {"PATH": CLEANPATH, "HOME": home, "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0"}


def git(cwd, *a, check=True, home=None):
    r = subprocess.run(["git", "-c", "user.name=ar7", "-c", "user.email=ar7@x", "-c", "init.defaultBranch=main",
                        "-c", "advice.detachedHead=false", *a], cwd=cwd, capture_output=True, text=True,
                       env=git_env(home or cwd))
    if check and r.returncode:
        raise RuntimeError(f"git {a} in {cwd}: rc={r.returncode} {r.stderr[-400:]}")
    return r


def gov(binary, argv, env, cwd, root=None, session=True, timeout=240):
    cmd = [binary, "--json"]
    if root is not None:
        cmd += ["--root", root]
    if session:
        cmd += ["--session", "S-ar7", "--role", "orchestrator"]
    cmd += list(argv)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err, rc = "TIMEOUT", -999
    try:
        d = json.loads(out)
        if not isinstance(d, dict):
            d = {"value": d}
    except Exception:
        d = {"raw": (out or "")[-400:], "stderr": (err or "")[-400:]}
    d["_rc"], d["_secs"] = rc, round(time.time() - t0, 2)
    return d


def code(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def result(d):
    r = d.get("result")
    return r if isinstance(r, dict) else {}


def entry(p):
    st = os.lstat(p)
    m = stat.S_IMODE(st.st_mode)
    if stat.S_ISLNK(st.st_mode):
        return f"l:{os.readlink(p)}"
    if stat.S_ISDIR(st.st_mode):
        return f"d:{m:o}"
    if stat.S_ISREG(st.st_mode):
        with open(p, "rb") as f:
            return f"f:{m:o}:{st.st_size}:{sha(f.read())}"
    return f"s:{stat.S_IFMT(st.st_mode):o}:{m:o}"


def tree_map(base):
    """Every entry under base (no exclusions), relpath -> type/mode/size/digest. Symlinks are recorded, never followed."""
    m = {}
    if not os.path.lexists(base):
        return {"<absent>": ""}
    if not stat.S_ISDIR(os.lstat(base).st_mode):
        return {".": entry(base)}
    for dp, dns, fns in os.walk(base, followlinks=False):
        dns.sort()
        for n in sorted(dns + fns):
            p = os.path.join(dp, n)
            try:
                m[os.path.relpath(p, base)] = entry(p)
            except FileNotFoundError:
                m[os.path.relpath(p, base)] = "vanished"
    return m


def partition(m):
    work, rt, g = {}, {}, {}
    for k, v in m.items():
        top = k.split(os.sep, 1)[0]
        if top == ".git":
            if k == os.path.join(".git", "index"):
                continue  # index stat refresh is recorded through git_state()['index_entries'] instead
            g[k] = v
        elif top == ".governance-runtime":
            rt[k] = v
        else:
            work[k] = v
    return {"work": work, "runtime": rt, "git_files": g}


def digest(m):
    return sha(json.dumps(m, sort_keys=True).encode())[:20]


def git_state(root, home=None):
    if not os.path.isdir(os.path.join(root, ".git")):
        return {"no_git": True}
    def g(*a):
        return git(root, *a, check=False, home=home).stdout
    return {"head": g("rev-parse", "HEAD").strip(), "refs": sha(g("for-each-ref", "--format=%(refname) %(objectname)").encode())[:16],
            "index_entries": sha(g("ls-files", "-s").encode())[:16], "stash": g("stash", "list").strip()}


def snap(root, home=None, cache=None):
    s = partition(tree_map(root))
    s["git"] = git_state(root)
    if home:
        s["home"] = tree_map(home)
    if cache:
        s["cache"] = tree_map(cache)
    return s


def changed(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def compare(before, after):
    out = {}
    for part in ("work", "runtime", "git_files"):
        c = changed(before[part], after[part])
        out[part + "_changed"] = bool(c)
        out[part + "_paths"] = c[:40]
        out[part + "_n"] = len(c)
    out["git_state_changed"] = before["git"] != after["git"]
    if "home" in before:
        c = changed(before["home"], after["home"])
        out["home_paths"] = c[:20]
    return out


def kind(p):
    if os.path.islink(p):
        return "link"
    if os.path.isdir(p):
        return "dir"
    if os.path.isfile(p):
        return "file"
    if os.path.lexists(p):
        return "special"
    return "absent"


def installation_state(root, vts_open_tx=False):
    """`18` §9 of revision 4, evaluated literally on a tree (entry types by lstat, never by name).
    Returns the state plus diagnostics that §9 as written does NOT examine (reported separately, never used for the state)."""
    occ = {p: kind(os.path.join(root, p)) for p in OCCUPATION}
    t = os.path.join(root, "governance", "trust")
    trust_present = kind(t) == "dir"
    fmt_ok = None
    if trust_present and kind(os.path.join(t, "FORMAT")) == "file":
        fmt_ok = open(os.path.join(t, "FORMAT"), "rb").read() == FORMAT_BYTES
    trust_complete = trust_present and kind(os.path.join(t, "FORMAT")) == "file" and kind(os.path.join(t, "framework.lock")) == "file" \
        and kind(os.path.join(t, "kernel")) == "dir" and (kind(os.path.join(t, "release.dsse.json")) == "file" or kind(os.path.join(t, "development.json")) == "file")
    legacy_entries = occ["governance/framework.lock"] == "file" or occ["governance/kernel"] == "dir"
    wrong = {p: occ[p] for p, ty in OCCUPATION.items() if occ[p] != ty}
    if trust_present and fmt_ok is False:
        state = "FORMAT_UNSUPPORTED"
    elif not trust_present and all(v == "absent" for v in occ.values()):
        state = "ABSENT"
    elif legacy_entries and not trust_present:
        state = "LEGACY"
    elif vts_open_tx:
        state = "IN_TRANSACTION"
    elif trust_complete and not wrong:
        state = "COMPLETE"
    else:
        state = "PARTIAL"
    diag = {}
    if trust_present:
        diag["unlisted_trust_top_entries"] = sorted(set(os.listdir(t)) - TRUST_TOP_ALLOWED)
    fl = os.path.join(root, "governance", "framework.lock")
    if kind(fl) == "dir":
        diag["occupation_dir_extra_entries"] = sorted(set(os.listdir(fl)) - {"ROT-1-TRUST-FORMAT"})
    nested = []
    for dp, dns, fns in os.walk(root):
        rel = os.path.relpath(dp, root)
        if rel.split(os.sep)[0] == ".git":
            dns[:] = []
            continue
        if rel != "." and os.path.basename(dp) == "governance" and ("framework.lock" in fns or "framework.lock" in dns):
            if os.path.relpath(os.path.dirname(dp), root) != ".":
                nested.append(os.path.relpath(os.path.join(dp, "framework.lock"), root))
    diag["nested_legacy_project_locks"] = sorted(nested)
    return {"state": state, "occupation": occ, "occupation_wrong": wrong, "legacy_entries": legacy_entries,
            "trust_present": trust_present, "trust_complete": trust_complete, "diagnostics_not_in_18_s9": diag}


def overlay_classifies(root, pattern="product/restricted-plan.md", overlay="governance/overlay"):
    import yaml
    p = os.path.join(root, overlay, "DATA_SENSITIVITY.yaml")
    try:
        d = yaml.safe_load(open(p)) or {}
        return any(isinstance(c, dict) and c.get("pattern") == pattern for c in (d.get("classifications") or []))
    except Exception:
        return None


def legacy_harm(binary, env, cwd, root=None):
    """Legacy view after a probe: does the legacy binary regard the project as a verified install, and does it index and
    serve the restricted marker file?"""
    kt = gov(binary, ["kernel", "trust"], env, cwd, root)
    rb = gov(binary, ["rebuild-memory"], env, cwd, root)
    mq = gov(binary, ["memory", "query", MARK], env, cwd, root)
    hits = [h.get("path") for h in (result(mq).get("hits") or []) if isinstance(h, dict)]
    return {"kernel_trust_ok": kt.get("ok"), "kernel_trust_code": code(kt), "verified": result(kt).get("verified"),
            "rebuild_ok": rb.get("ok"), "rebuild_code": code(rb), "query_ok": mq.get("ok"), "query_code": code(mq),
            "restricted_hits": [h for h in hits if h and "restricted" in h]}


def copy_tree(src, dst):
    shutil.copytree(src, dst, symlinks=True)
    return dst


def aside(scratch, src, tag):
    d = os.path.join(scratch, "aside", tag, os.path.relpath(src, "/").replace("/", "__"))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.move(src, d)
    return d


def scrub(text, scratch):
    return text.replace(scratch, "<scratch>").replace(WT, "<wt>").replace(LEG, "<legacy-bin>")
