#!/usr/bin/env python3
"""AR-0013 (independent compatibility/transaction review C of RoT-1 revision 5, cdb4e14) probe library.

Independence: the installation-state predicate below is encoded from the text of `18` §9, §9.1 and §9.2 at cdb4e14. It does
not import or copy the architect's `evidence/r5/ST5-installation-state-r5.py` or review r4 C's `c4lib.installation_state`.
The legacy-binary runner and whole-tree snapshot follow the same hygiene rules as review r4 C (`c4lib.py`), re-written.

Hygiene: every child gets a constructed environment (never the parent's): PATH, HOME, XDG_* and GOV_KERNEL_CACHE in
scratch; no other GOV_* variable unless a probe sets one explicitly as the object of the test. Git runs with
GIT_CONFIG_NOSYSTEM=1, GIT_OPTIONAL_LOCKS=0. Whole-tree snapshots record every entry under the project root (work tree,
.governance-runtime, .git), the child HOME and the kernel cache, by type, mode, size and SHA-256. No forced deletes.
"""
import hashlib, json, os, shutil, stat, subprocess, time

sys_dont = True
SCRATCH = os.environ.get("AR13_SCRATCH", "")
WT = os.environ.get("AR13_WT", "")
LEG = os.environ.get("AR13_LEGACY_BIN", "")
VERSIONS = ("4.1.2", "4.1.3", "4.1.4", "4.1.5")
BINS = {v: os.path.join(LEG, f"gov-{v}") for v in VERSIONS}
REL = {v: os.path.join(WT, "release", "releases", v) for v in VERSIONS}
PACK = os.path.join(WT, "release", "root-of-trust", "4.1.6")
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
MARK = "AR0013RESTRICTEDMARKER"
CLEANPATH = "/usr/bin:/bin"
FORMAT_OBJ = {"layout": "legacy-path-occupation-v1", "minimum_reader": "4.1.6", "trust_format": "rot-1"}
FORMAT_BYTES = json.dumps(FORMAT_OBJ, sort_keys=True, separators=(",", ":")).encode()

# 26 §2 / 18 §8: occupation entries and exact types
OCCUPATION = {"governance/kernel": "file", "governance/project": "file", "governance/generated": "file",
              "governance/framework.lock": "dir", "spec/audits/GOVERNANCE-ADOPTION": "file",
              ".governance-runtime/migration": "file"}
# 18 §9.1 item 1
TRUST_TOP = {"FORMAT": "file", "framework.lock": "file", "kernel": "dir", "release.dsse.json": "file",
             "development.json": "file", "registration.dsse.json": "file", "lineage": "dir", "state": "dir",
             "root": "dir", "profiles": "dir"}
STATEMENT_DIRS = ("state", "root", "lineage", "profiles")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ processes
def child_env(home, cache, extra=None):
    os.makedirs(home, exist_ok=True)
    env = {"PATH": CLEANPATH, "HOME": home, "LANG": "C.UTF-8",
           "XDG_CACHE_HOME": os.path.join(home, ".cache"), "XDG_CONFIG_HOME": os.path.join(home, ".config"),
           "XDG_STATE_HOME": os.path.join(home, ".local", "state"), "XDG_DATA_HOME": os.path.join(home, ".local", "share"),
           "GOV_KERNEL_CACHE": cache, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "ar13", "GIT_AUTHOR_EMAIL": "ar13@x",
           "GIT_COMMITTER_NAME": "ar13", "GIT_COMMITTER_EMAIL": "ar13@x", "PYTHONDONTWRITEBYTECODE": "1",
           "AR13_MARKER": os.path.join(home, "MARKER")}
    if extra:
        env.update(extra)
    return env


def git_env(home):
    return {"PATH": CLEANPATH, "HOME": home, "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0", "LANG": "C.UTF-8"}


def git(cwd, *a, check=True, home=None, extra_env=None):
    env = git_env(home or os.path.join(SCRATCH, "githome"))
    os.makedirs(env["HOME"], exist_ok=True)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(["git", "-c", "user.name=ar13", "-c", "user.email=ar13@x", "-c", "init.defaultBranch=main",
                        "-c", "advice.detachedHead=false", "-c", "core.hooksPath=/dev/null", *a], cwd=cwd,
                       capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError(f"git {a} in {cwd}: rc={r.returncode} {r.stderr[-400:]}")
    return r


def gov(binary, argv, env, cwd, root=None, timeout=180, json_flag=True):
    cmd = [binary]
    if json_flag:
        cmd.append("--json")
    if root is not None:
        cmd += ["--root", root]
    cmd += ["--session", "S-ar13", "--role", "orchestrator"]
    cmd += list(argv)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err, rc = "TIMEOUT", -999
    try:
        d = json.loads(out)
        if not isinstance(d, dict):
            d = {"value": d}
    except Exception:
        d = {"raw": (out or "")[-300:], "stderr": (err or "")[-300:]}
    d["_rc"], d["_secs"] = rc, round(time.time() - t0, 2)
    return d


def code(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def result(d):
    r = d.get("result")
    return r if isinstance(r, dict) else {}


# ------------------------------------------------------------------------------------------------ snapshots
def entry(p):
    st = os.lstat(p)
    m = stat.S_IMODE(st.st_mode)
    if stat.S_ISLNK(st.st_mode):
        return f"l:{os.readlink(p)}"
    if stat.S_ISDIR(st.st_mode):
        return f"d:{m:o}"
    if stat.S_ISREG(st.st_mode):
        return f"f:{m:o}:{st.st_size}:{sha_file(p)}"
    return f"s:{stat.S_IFMT(st.st_mode):o}:{m:o}"


def tree_map(base):
    """Every entry under base, no exclusions; symlinks recorded, never followed."""
    m = {}
    if not os.path.lexists(base):
        return {}
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


def git_plumbing(root, home):
    if not os.path.isdir(os.path.join(root, ".git")):
        return {"no_git": True}
    g = lambda *a: git(root, *a, check=False, home=home).stdout
    return {"head": g("rev-parse", "HEAD").strip(), "refs": sha(g("for-each-ref", "--format=%(refname) %(objectname)").encode()),
            "index": sha(g("ls-files", "-s").encode()), "stash": g("stash", "list").strip()}


def snap(root, home=None, cache=None, githome=None):
    t = tree_map(root)
    s = {"work": {}, "runtime": {}, "git_files": {}, "git_index_raw": None}
    for k, v in t.items():
        top = k.split(os.sep, 1)[0]
        if top == ".git":
            if k == os.path.join(".git", "index"):
                s["git_index_raw"] = v
            else:
                s["git_files"][k] = v
        elif top == ".governance-runtime":
            s["runtime"][k] = v
        else:
            s["work"][k] = v
    s["git"] = git_plumbing(root, githome or os.path.join(SCRATCH, "githome"))
    s["home"] = tree_map(home) if home else {}
    s["cache"] = tree_map(cache) if cache else {}
    return s


def changed(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def compare(before, after):
    out = {}
    for part in ("work", "runtime", "git_files", "home", "cache"):
        c = changed(before[part], after[part])
        out[part] = c
    out["git_plumbing_changed"] = before["git"] != after["git"]
    out["git_index_stat_only"] = (before["git_index_raw"] != after["git_index_raw"]) and before["git"].get("index") == after["git"].get("index")
    return out


def digest_map(m):
    return sha(json.dumps(m, sort_keys=True).encode())


def kind(p):
    try:
        st = os.lstat(p)
    except FileNotFoundError:
        return "absent"
    except NotADirectoryError:
        return "absent"
    if stat.S_ISLNK(st.st_mode):
        return "link"
    if stat.S_ISDIR(st.st_mode):
        return "dir"
    if stat.S_ISREG(st.st_mode):
        return "file"
    return "special"


# ------------------------------------------------------------------------------------------------ RoT-1 predicates (text)
def kernel_file_map(kdir):
    """relpath -> ('file', sha) | ('link', target) | ('dir', None) | ('special', None) under the kernel dir."""
    out = {}
    for dp, dns, fns in os.walk(kdir, followlinks=False):
        for n in dns + fns:
            p = os.path.join(dp, n)
            k = kind(p)
            rel = os.path.relpath(p, kdir)
            if k == "file":
                out[rel] = ("file", sha_file(p))
            elif k == "dir":
                out[rel] = ("dir", None)
            elif k == "link":
                out[rel] = ("link", os.readlink(p))
            else:
                out[rel] = (k, None)
    return out


def read_lock_file_map(root):
    """Lock 3.0.0 (08 §3, revision 5): the release content set recorded as `kernel.files` {relpath: 'sha256:<hex>'}."""
    p = os.path.join(root, "governance", "trust", "framework.lock")
    try:
        d = json.load(open(p))
        files = d["kernel"]["files"]
        return {k: v.split(":", 1)[1] for k, v in files.items()}
    except Exception:
        return None


def format_supported(root):
    p = os.path.join(root, "governance", "trust", "FORMAT")
    try:
        d = json.loads(open(p, "rb").read())
    except Exception:
        return False
    return d.get("trust_format") == "rot-1" and d.get("layout") == "legacy-path-occupation-v1" and d.get("minimum_reader") in ("4.1.6",)


def legacy_markers(root):
    """18 §9.1 item 5: a directory named `governance` holding `framework.lock` as a regular file, or holding
    `kernel/KERNEL_MANIFEST.json`. Returns (under_project_governance[], elsewhere[]), relpaths of the `governance` dirs,
    excluding the project's own root `governance/` layout."""
    inside, elsewhere = [], []
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel = os.path.relpath(dp, root)
        if rel.split(os.sep, 1)[0] == ".git":
            dns[:] = []
            continue
        for n in list(dns) + [x for x in fns if False]:
            if n != "governance":
                continue
            g = os.path.join(dp, n)
            grel = os.path.relpath(g, root)
            if grel == "governance":
                continue
            is_marker = kind(os.path.join(g, "framework.lock")) == "file" or kind(os.path.join(g, "kernel", "KERNEL_MANIFEST.json")) == "file"
            if is_marker:
                (inside if grel.startswith("governance" + os.sep) else elsewhere).append(grel)
    return sorted(inside), sorted(elsewhere)


def symlinks_below(base):
    out = []
    for dp, dns, fns in os.walk(base, followlinks=False):
        for n in dns + fns:
            p = os.path.join(dp, n)
            if kind(p) == "link":
                out.append(os.path.relpath(p, base))
    return sorted(out)


def honoured_journals(root, vts_open_tx):
    """18 §5.1: honoured iff the VTS lists the TX open for this project AND the journal path is untracked."""
    base = os.path.join(root, ".governance-runtime", "trust-tx")
    out, foreign = [], []
    if kind(base) != "dir":
        return out, foreign
    tracked = set()
    if os.path.isdir(os.path.join(root, ".git")):
        tracked = set(git(root, "ls-files", ".governance-runtime/trust-tx", check=False).stdout.split())
    for n in sorted(os.listdir(base)):
        j = os.path.join(base, n, "journal.json")
        if kind(j) != "file":
            continue
        rel = os.path.relpath(j, root)
        if n in (vts_open_tx or []) and rel not in tracked:
            out.append(n)
        else:
            foreign.append(n)
    return out, foreign


def state_r5(root, vts_open_tx=None):
    """`18` §9 table + §9.1 closed entry sets, literally, by lstat types. Returns state, reasons, reports."""
    reasons, reports = [], []
    occ = {p: kind(os.path.join(root, p)) for p in OCCUPATION}
    t = os.path.join(root, "governance", "trust")
    trust_present = kind(t) == "dir"
    legacy_entries = occ["governance/framework.lock"] == "file" or occ["governance/kernel"] == "dir"
    inside, elsewhere = legacy_markers(root)
    if elsewhere:
        reports.append({"NESTED_LEGACY_PROJECT": elsewhere})
    honoured, foreign = honoured_journals(root, vts_open_tx)
    if foreign:
        reports.append({"FOREIGN_TRANSACTION_ARTEFACT": foreign})
    if trust_present and kind(os.path.join(t, "FORMAT")) == "file" and not format_supported(root):
        return {"state": "FORMAT_UNSUPPORTED", "reasons": ["format"], "reports": reports}
    if not trust_present and all(v == "absent" for v in occ.values()) and not legacy_entries:
        return {"state": "ABSENT", "reasons": [], "reports": reports}
    if legacy_entries and not trust_present:
        return {"state": "LEGACY", "reasons": [], "reports": reports}
    if honoured:
        return {"state": "IN_TRANSACTION", "reasons": ["honoured_journal"], "reports": reports, "tx": honoured}
    # COMPLETE prerequisites
    base_ok = trust_present and kind(os.path.join(t, "FORMAT")) == "file" and kind(os.path.join(t, "framework.lock")) == "file" \
        and kind(os.path.join(t, "kernel")) == "dir" and (kind(os.path.join(t, "release.dsse.json")) == "file" or kind(os.path.join(t, "development.json")) == "file")
    if not base_ok:
        reasons.append("trust_components")
    wrong = {p: v for p, v in occ.items() if v != OCCUPATION[p]}
    if wrong:
        reasons.append("occupation")
    if legacy_entries:
        reasons.append("legacy_and_rot1_mixed")
    if trust_present:
        # §9.1 preamble: no symbolic link anywhere below governance/trust/
        if symlinks_below(t):
            reasons.append("foreign_trust_entry(symlink)")
        # item 1
        for n in os.listdir(t):
            k = kind(os.path.join(t, n))
            if n not in TRUST_TOP or TRUST_TOP[n] != k:
                reasons.append("foreign_trust_entry")
                break
        # item 2: kernel path set equals the lock's file map, digests equal
        fm = read_lock_file_map(root)
        if kind(os.path.join(t, "kernel")) == "dir":
            cur = kernel_file_map(os.path.join(t, "kernel"))
            cur_files = {k: v[1] for k, v in cur.items() if v[0] == "file"}
            non_files = [k for k, v in cur.items() if v[0] not in ("file", "dir")]
            if fm is None or non_files or cur_files != fm:
                reasons.append("kernel_content_mismatch")
            # directories that contain no registered file are extra entries of the path set
            dirs = {k for k, v in cur.items() if v[0] == "dir"}
            needed = set()
            for f in (fm or {}):
                parts = f.split("/")
                for i in range(1, len(parts)):
                    needed.add("/".join(parts[:i]))
            if dirs - needed:
                reasons.append("kernel_content_mismatch(extra_dir)")
        # item 3
        for sd in STATEMENT_DIRS:
            d = os.path.join(t, sd)
            if kind(d) != "dir":
                continue
            for n in os.listdir(d):
                if kind(os.path.join(d, n)) != "file" or not n.endswith(".dsse.json"):
                    reasons.append("foreign_trust_entry(statement_dir)")
                    break
    # item 4
    fl = os.path.join(root, "governance", "framework.lock")
    if kind(fl) == "dir":
        ents = os.listdir(fl)
        if ents != ["ROT-1-TRUST-FORMAT"] or kind(os.path.join(fl, "ROT-1-TRUST-FORMAT")) != "file":
            reasons.append("foreign_occupation_entry")
    # item 5
    if inside:
        reasons.append("nested_legacy_install")
    reasons = sorted(set(reasons))
    return {"state": "PARTIAL" if reasons else "COMPLETE", "reasons": reasons, "reports": reports,
            "nested_under_governance": inside}


def kernel_tampered(root, rcs):
    """`18` §6.1 steps 4–5: the installed kernel tree must equal RCS(D) (from the signed release statement, modelled by the
    builder's reference map `rcs`, never by the unsigned lock)."""
    k = os.path.join(root, "governance", "trust", "kernel")
    if kind(k) != "dir":
        return True
    cur = kernel_file_map(k)
    files = {a: b[1] for a, b in cur.items() if b[0] == "file"}
    return files != rcs or any(b[0] not in ("file", "dir") for b in cur.values())


PPS_CWD_18_S9_2 = ("governance/trust", "governance/framework.lock")


def discover_r5(start):
    """`18` §9.2: nearest ancestor of the working directory holding governance/trust/FORMAT as a regular file; refusal when
    the resolved working directory is inside the PPS as §9.2 item 2 lists it; the markers between; and, separately, whether
    the directory is inside the PPS as `18` §8 defines it (adds the transaction area)."""
    start = os.path.realpath(start)
    cur, root = start, None
    while True:
        if kind(os.path.join(cur, "governance", "trust", "FORMAT")) == "file":
            root = cur
            break
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    if root is None:
        return {"root": None, "refuse_9_2": False, "inside_pps_18_8": False}
    rel = os.path.relpath(start, root)
    in92 = any(rel == p or rel.startswith(p + "/") for p in PPS_CWD_18_S9_2) or rel in OCCUPATION
    in88 = in92 or rel == ".governance-runtime/trust-tx" or rel.startswith(".governance-runtime/trust-tx/")
    between = []
    if rel != ".":
        parts = rel.split("/")
        for i in range(0, len(parts)):
            d = os.path.join(root, *parts[: i + 1]) if i >= 0 else root
            g = os.path.join(d, "governance")
            if kind(os.path.join(g, "framework.lock")) == "file" or kind(os.path.join(g, "kernel", "KERNEL_MANIFEST.json")) == "file":
                between.append(os.path.relpath(g, root))
    return {"root_rel_to_start": os.path.relpath(root, start), "refuse_9_2": in92, "inside_pps_18_8": in88,
            "legacy_markers_between": between}


# ------------------------------------------------------------------------------------------------ misc
def copy_tree(src, dst):
    shutil.copytree(src, dst, symlinks=True)
    return dst


def scrub(text):
    for a, b in ((SCRATCH, "<scratch>"), (WT, "<wt>"), (LEG, "<legacy-bin>")):
        if a:
            text = text.replace(a, b)
    return text


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(scrub(json.dumps(obj, indent=1, sort_keys=True, default=str)))
