#!/usr/bin/env python3
"""AR-0017 (independent compatibility/transaction review C of RoT-1 revision 6, 4106885) probe library.

Independence. The installation-state predicate `state_r6` is encoded by AR-0017 from the text of `18` §9 (table), §9.1
(closed entry sets, revision-6 `.gitattributes` member), §9.2 (root discovery and working-directory refusal, revision-6
transaction area) and §5.1 (honoured journals) at 4106885. It does not import or copy the architect's LAY6 `c5lib`, review
r5 C's `c5lib.state_r5`, ST5 or LR2. Where the table's rows overlap (ABSENT / LEGACY / IN_TRANSACTION) the predicate returns
every matching row, so an ambiguity in the text is visible rather than resolved by the instrument.

Hygiene. Every child process receives a constructed environment (never the parent's): PATH, HOME, XDG_* and
GOV_KERNEL_CACHE inside scratch; no other GOV_* variable unless a probe sets it explicitly as the object of the test. Git
runs with GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL inside scratch, GIT_OPTIONAL_LOCKS=0, core.hooksPath=/dev/null.
Snapshots record every entry under the project root (work tree, .governance-runtime, .git), the child HOME and the kernel
cache by type, mode, size and SHA-256. `restore_slot` (entry-by-entry restore from a pristine copy, each path asserted
inside the slot) is provided but the reported matrix run did not use it: `matrix6.py` removes each per-row scratch copy with
`shutil.rmtree` after its digests are recorded (scratch paths only; disclosed in evidence/README.md).
"""
import hashlib, json, os, shutil, stat, subprocess, time

SCR = os.environ.get("AR17_SCRATCH", "")
WT = os.environ.get("AR17_WT", "")
VERSIONS = ("4.1.2", "4.1.3", "4.1.4", "4.1.5")
BINS = {v: os.path.join(SCR, "bin", "gov-" + v) for v in VERSIONS}
REL = {v: os.path.join(SCR, "releases", v) for v in VERSIONS}
PACK = os.path.join(WT, "release", "root-of-trust", "4.1.6")
CLEANPATH = "/usr/bin:/bin"

# ---- revision-6 layout constants, from 08 §2, 26 §2, 18 §8/§9.1 at 4106885 ----------------------------------------------
SENTINEL = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
FORMAT_OBJ = {"layout": "legacy-path-occupation-v1", "minimum_reader": "4.1.6", "trust_format": "rot-1"}
FORMAT_BYTES = json.dumps(FORMAT_OBJ, sort_keys=True, separators=(",", ":")).encode()
GITATTR_BYTES = b"* -text\n"          # 18 §9.1 item 1 (26 §2 writes `* -text`; §9.1 fixes the trailing newline)
OCCUPATION = {"governance/kernel": "file", "governance/project": "file", "governance/generated": "file",
              "governance/framework.lock": "dir", "spec/audits/GOVERNANCE-ADOPTION": "file",
              ".governance-runtime/migration": "file"}
OCC_DIR_SENTINEL = "ROT-1-TRUST-FORMAT"
TRUST_ALLOWED = {"FORMAT": "file", "framework.lock": "file", "kernel": "dir", "release.dsse.json": "file",
                 "development.json": "file", "registration.dsse.json": "file", "lineage": "dir", "state": "dir",
                 "root": "dir", "profiles": "dir", ".gitattributes": "file"}
STATEMENT_DIRS = ("state", "root", "lineage", "profiles")
TXAREA = ".governance-runtime/trust-tx"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def kind(p):
    try:
        st = os.lstat(p)
    except (FileNotFoundError, NotADirectoryError):
        return "absent"
    if stat.S_ISLNK(st.st_mode):
        return "link"
    if stat.S_ISDIR(st.st_mode):
        return "dir"
    if stat.S_ISREG(st.st_mode):
        return "file"
    return "special"


# ---- processes ------------------------------------------------------------------------------------------------------------
def child_env(home, cache, extra=None):
    os.makedirs(home, exist_ok=True)
    env = {"PATH": CLEANPATH, "HOME": home, "LANG": "C.UTF-8", "USER": "ar17", "LOGNAME": "ar17",
           "XDG_CACHE_HOME": os.path.join(home, ".cache"), "XDG_CONFIG_HOME": os.path.join(home, ".config"),
           "XDG_STATE_HOME": os.path.join(home, ".local", "state"), "XDG_DATA_HOME": os.path.join(home, ".local", "share"),
           "GOV_KERNEL_CACHE": cache, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.path.join(home, ".gitconfig-ar17"),
           "GIT_AUTHOR_NAME": "ar17", "GIT_AUTHOR_EMAIL": "ar17@example.invalid", "GIT_COMMITTER_NAME": "ar17",
           "GIT_COMMITTER_EMAIL": "ar17@example.invalid", "PYTHONDONTWRITEBYTECODE": "1"}
    if extra:
        env.update(extra)
    assert all(not k.startswith("GOV_") or k == "GOV_KERNEL_CACHE" or (extra and k in extra) for k in env)
    return env


def git_env(home, extra=None):
    os.makedirs(home, exist_ok=True)
    e = {"PATH": CLEANPATH, "HOME": home, "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.path.join(home, ".gitconfig"), "GIT_OPTIONAL_LOCKS": "0",
         "GIT_AUTHOR_NAME": "ar17", "GIT_AUTHOR_EMAIL": "ar17@example.invalid", "GIT_COMMITTER_NAME": "ar17",
         "GIT_COMMITTER_EMAIL": "ar17@example.invalid", "GIT_AUTHOR_DATE": "2026-09-14T00:00:00Z",
         "GIT_COMMITTER_DATE": "2026-09-14T00:00:00Z"}
    if extra:
        e.update(extra)
    return e


def git(cwd, *a, check=True, home=None, extra_env=None, cfg=()):
    env = git_env(home or os.path.join(SCR, "githome"), extra_env)
    pre = ["git", "-c", "init.defaultBranch=main", "-c", "advice.detachedHead=false", "-c", "core.hooksPath=/dev/null"]
    for c in cfg:
        pre += ["-c", c]
    r = subprocess.run(pre + list(a), cwd=cwd, capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError("git %s in %s rc=%s %s" % (a, cwd, r.returncode, r.stderr[-500:]))
    return r


def gov(binary, argv, env, cwd, root=None, timeout=240, json_flag=True, globals_=()):
    cmd = [binary] + (["--json"] if json_flag else [])
    if root is not None:
        cmd += ["--root", root]
    cmd += list(globals_) + list(argv)
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
    d["_rc"], d["_secs"] = rc, round(time.time() - t0, 3)
    return d


def errcode(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def result(d):
    r = d.get("result")
    return r if isinstance(r, dict) else {}


# ---- whole-tree snapshots -------------------------------------------------------------------------------------------------
def entry(p):
    st = os.lstat(p)
    m = stat.S_IMODE(st.st_mode)
    if stat.S_ISLNK(st.st_mode):
        return "l:" + os.readlink(p)
    if stat.S_ISDIR(st.st_mode):
        return "d:%o" % m
    if stat.S_ISREG(st.st_mode):
        return "f:%o:%d:%s:%d" % (m, st.st_size, sha_file(p), st.st_nlink)
    return "s:%o:%o" % (stat.S_IFMT(st.st_mode), m)


def tree_map(base):
    """Every entry under base, no exclusions; symlinks recorded, never followed."""
    if not os.path.lexists(base):
        return {}
    if not stat.S_ISDIR(os.lstat(base).st_mode):
        return {".": entry(base)}
    m = {}
    for dp, dns, fns in os.walk(base, followlinks=False):
        dns.sort()
        for n in sorted(dns + fns):
            p = os.path.join(dp, n)
            try:
                m[os.path.relpath(p, base)] = entry(p)
            except FileNotFoundError:
                m[os.path.relpath(p, base)] = "vanished"
    return m


def digest_map(m):
    return sha(json.dumps(m, sort_keys=True).encode())


def diff(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def partition(paths):
    out = {}
    for p in paths:
        top = p.split("/", 1)[0]
        if top == ".git":
            k = "git"
        elif p == "governance/trust" or p.startswith("governance/trust/"):
            k = "pps_trust"
        elif p in OCCUPATION or p.startswith("governance/framework.lock/"):
            k = "pps_occupation"
        elif p == TXAREA or p.startswith(TXAREA + "/"):
            k = "pps_txarea"
        elif p.startswith("governance/overlay/") or p == "governance/overlay":
            k = "overlay"
        elif p.startswith("governance/views/") or p == "governance/views":
            k = "views"
        elif p.startswith("governance/"):
            k = "governance_other"
        elif top == ".governance-runtime":
            k = "runtime_other"
        else:
            k = "project_other"
        out[k] = out.get(k, 0) + 1
    return out


# ---- slot restore without recursive/forced deletes ------------------------------------------------------------------------
def restore_slot(slot, pristine_dir, pristine_map, after_map):
    """Restore `slot` to the pristine tree using only the entries the diff names. Returns True when a whole-tree digest of
    the slot equals the pristine digest afterwards."""
    slot = os.path.realpath(slot)
    changed = diff(pristine_map, after_map)
    added = sorted((k for k in changed if k not in pristine_map), key=lambda k: -k.count("/"))
    for k in added:                                   # deepest first
        p = os.path.join(slot, k)
        assert os.path.realpath(os.path.dirname(p)).startswith(slot), p
        kk = kind(p)
        try:
            if kk == "dir":
                os.rmdir(p)
            elif kk != "absent":
                os.unlink(p)
        except OSError:
            return False
    # entries that changed or vanished: recreate from pristine, parents first
    for k in sorted((k for k in changed if k in pristine_map), key=lambda k: k.count("/")):
        src, dst = os.path.join(pristine_dir, k), os.path.join(slot, k)
        assert os.path.realpath(os.path.dirname(dst)).startswith(slot), dst
        pk, dk = kind(src), kind(dst)
        try:
            if pk == "dir":
                if dk not in ("dir", "absent"):
                    os.unlink(dst)
                if kind(dst) == "absent":
                    os.mkdir(dst)
                shutil.copystat(src, dst)
            elif pk == "file":
                if dk == "dir":
                    return False
                if dk == "link":
                    os.unlink(dst)
                shutil.copy2(src, dst)
            elif pk == "link":
                if dk != "absent":
                    if dk == "dir":
                        return False
                    os.unlink(dst)
                os.symlink(os.readlink(src), dst)
        except OSError:
            return False
    return digest_map(tree_map(slot)) == digest_map(pristine_map)


def move_to_trash(p, trash):
    os.makedirs(trash, exist_ok=True)
    n = 0
    while os.path.lexists(os.path.join(trash, "%s-%d" % (os.path.basename(p), n))):
        n += 1
    os.rename(p, os.path.join(trash, "%s-%d" % (os.path.basename(p), n)))


# ---- revision-6 predicates (text of 18 §9, §9.1, §9.2, §5.1) ----------------------------------------------------------------
def kernel_file_map(kdir):
    out = {}
    for dp, dns, fns in os.walk(kdir, followlinks=False):
        for n in dns + fns:
            p = os.path.join(dp, n)
            k = kind(p)
            rel = os.path.relpath(p, kdir)
            out[rel] = (k, sha_file(p) if k == "file" else (os.readlink(p) if k == "link" else None))
    return out


def lock_file_map(root):
    try:
        d = json.load(open(os.path.join(root, "governance", "trust", "framework.lock")))
        return {k: v.split(":", 1)[1] for k, v in d["kernel"]["files"].items()}
    except Exception:
        return None


def legacy_markers(root):
    """§9.1 item 5: a directory named `governance` holding `framework.lock` as a regular file or `kernel/KERNEL_MANIFEST.json`,
    other than the project's root layout. Returns (under project governance/, elsewhere)."""
    inside, elsewhere = [], []
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel = os.path.relpath(dp, root)
        if rel == ".git" or rel.startswith(".git/"):
            dns[:] = []
            continue
        if "governance" in dns:
            g = os.path.join(dp, "governance")
            grel = os.path.relpath(g, root)
            if grel != "governance" and (kind(os.path.join(g, "framework.lock")) == "file"
                                         or kind(os.path.join(g, "kernel", "KERNEL_MANIFEST.json")) == "file"):
                (inside if grel.startswith("governance/") else elsewhere).append(grel)
    return sorted(inside), sorted(elsewhere)


def journals(root, vts_open=()):
    base = os.path.join(root, TXAREA)
    honoured, foreign = [], []
    if kind(base) != "dir":
        return honoured, foreign
    tracked = set()
    if kind(os.path.join(root, ".git")) == "dir":
        tracked = set(git(root, "ls-files", TXAREA, check=False).stdout.split())
    for dp, dns, fns in os.walk(base, followlinks=False):
        if "journal.json" in fns:
            j = os.path.relpath(os.path.join(dp, "journal.json"), root)
            tx = os.path.basename(dp)
            (honoured if (tx in vts_open and j not in tracked and os.path.dirname(os.path.dirname(j)) == TXAREA) else foreign).append(j)
    return sorted(honoured), sorted(foreign)


def state_r6(root, vts_open=(), rcs=None):
    t = os.path.join(root, "governance", "trust")
    occ = {p: kind(os.path.join(root, p)) for p in OCCUPATION}
    trust_present = kind(t) == "dir"
    legacy_layout = occ["governance/framework.lock"] == "file" or occ["governance/kernel"] == "dir"
    inside, elsewhere = legacy_markers(root)
    honoured, foreign = journals(root, vts_open)
    reports = []
    if elsewhere:
        reports.append(["NESTED_LEGACY_PROJECT", elsewhere])
    if foreign:
        reports.append(["FOREIGN_TRANSACTION_ARTEFACT", foreign])
    rows = []
    if trust_present and kind(os.path.join(t, "FORMAT")) == "file":
        try:
            fobj = json.loads(open(os.path.join(t, "FORMAT"), "rb").read())
        except Exception:
            fobj = None
        if fobj != FORMAT_OBJ:
            rows.append("FORMAT_UNSUPPORTED")
    if not trust_present and all(v == "absent" for v in occ.values()) and not legacy_layout:
        rows.append("ABSENT")
    if legacy_layout and not trust_present:
        rows.append("LEGACY")
    if honoured:
        rows.append("IN_TRANSACTION")
    reasons = []
    if not (trust_present and kind(os.path.join(t, "FORMAT")) == "file" and kind(os.path.join(t, "framework.lock")) == "file"
            and kind(os.path.join(t, "kernel")) == "dir"
            and (kind(os.path.join(t, "release.dsse.json")) == "file" or kind(os.path.join(t, "development.json")) == "file")):
        reasons.append("trust_components")
    if any(occ[p] != OCCUPATION[p] for p in OCCUPATION):
        reasons.append("occupation")
    if legacy_layout:
        reasons.append("legacy_and_rot1_mixed")
    if trust_present:
        for dp, dns, fns in os.walk(t, followlinks=False):
            if any(kind(os.path.join(dp, n)) == "link" for n in dns + fns):
                reasons.append("foreign_trust_entry(symlink)")
                break
        for n in os.listdir(t):
            if TRUST_ALLOWED.get(n) != kind(os.path.join(t, n)):
                reasons.append("foreign_trust_entry(%s)" % n)
        ga = os.path.join(t, ".gitattributes")
        if kind(ga) != "file":
            reasons.append("trust_components(.gitattributes)")
        elif open(ga, "rb").read() != GITATTR_BYTES:
            reasons.append("foreign_trust_entry(.gitattributes_content)")
        fm = lock_file_map(root)
        if kind(os.path.join(t, "kernel")) == "dir":
            cur = kernel_file_map(os.path.join(t, "kernel"))
            files = {k: v[1] for k, v in cur.items() if v[0] == "file"}
            others = [k for k, v in cur.items() if v[0] not in ("file", "dir")]
            needed_dirs = set()
            for f in (fm or {}):
                parts = f.split("/")
                for i in range(1, len(parts)):
                    needed_dirs.add("/".join(parts[:i]))
            extra_dirs = {k for k, v in cur.items() if v[0] == "dir"} - needed_dirs
            if fm is None or others or files != fm or extra_dirs:
                reasons.append("kernel_content_mismatch")
        for sd in STATEMENT_DIRS:
            d = os.path.join(t, sd)
            if kind(d) == "dir" and any(kind(os.path.join(d, n)) != "file" or not n.endswith(".dsse.json") for n in os.listdir(d)):
                reasons.append("foreign_trust_entry(%s/)" % sd)
    fl = os.path.join(root, "governance", "framework.lock")
    if kind(fl) == "dir" and (os.listdir(fl) != [OCC_DIR_SENTINEL] or kind(os.path.join(fl, OCC_DIR_SENTINEL)) != "file"):
        reasons.append("foreign_occupation_entry")
    if inside:
        reasons.append("nested_legacy_install")
    reasons = sorted(set(reasons))
    if not reasons and not honoured:
        rows.append("COMPLETE")
    if not rows:
        rows.append("PARTIAL")
    # stated precedence used for the headline: FORMAT_UNSUPPORTED > IN_TRANSACTION > ABSENT > LEGACY > COMPLETE > PARTIAL
    order = ["FORMAT_UNSUPPORTED", "IN_TRANSACTION", "ABSENT", "LEGACY", "COMPLETE", "PARTIAL"]
    state = sorted(rows, key=order.index)[0]
    out = {"state": state, "rows_matched": sorted(rows, key=order.index), "reasons": reasons if state in ("PARTIAL",) else ([] if state == "COMPLETE" else reasons),
           "reports": reports, "nested_under_governance": inside}
    if rcs is not None:
        out["kernel_tampered"] = kernel_tampered(root, rcs)
    return out


def kernel_tampered(root, rcs):
    """18 §6.1 steps 4-5 against RCS(D) (the builder's release content set, never the unsigned lock)."""
    k = os.path.join(root, "governance", "trust", "kernel")
    if kind(k) != "dir":
        return True
    cur = kernel_file_map(k)
    return {a: b[1] for a, b in cur.items() if b[0] == "file"} != rcs or any(b[0] not in ("file", "dir") for b in cur.values())


PPS_CWD = ("governance/trust", "governance/framework.lock", TXAREA)


def discover_r6(start):
    """18 §9.2 items 1-3 as written at 4106885."""
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
        return {"root": None, "refuse": False}
    rel = os.path.relpath(start, root)
    refuse = rel in OCCUPATION or any(rel == p or rel.startswith(p + "/") for p in PPS_CWD)
    between = []
    if rel != ".":
        parts = rel.split("/")
        for i in range(len(parts)):
            g = os.path.join(root, *parts[: i + 1], "governance")
            if kind(os.path.join(g, "framework.lock")) == "file" or kind(os.path.join(g, "kernel", "KERNEL_MANIFEST.json")) == "file":
                between.append(os.path.relpath(g, root))
    return {"root_rel": os.path.relpath(root, start), "refuse": refuse, "legacy_markers_between": between}


def classifications(root, patterns=("product/restricted-plan.md", "product/customers/**")):
    import yaml
    for ov in ("governance/overlay", "governance/project"):
        p = os.path.join(root, ov, "DATA_SENSITIVITY.yaml")
        if kind(p) == "file":
            try:
                d = yaml.safe_load(open(p)) or {}
                pats = {c.get("pattern") for c in (d.get("classifications") or []) if isinstance(c, dict)}
                return set(patterns) <= pats
            except Exception:
                return False
    return None


def scrub(text):
    for a, b in ((SCR, "<ar17>"), (WT, "<wt>")):
        if a:
            text = text.replace(a, b)
    return text


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(scrub(json.dumps(obj, indent=1, sort_keys=True, default=str)))
