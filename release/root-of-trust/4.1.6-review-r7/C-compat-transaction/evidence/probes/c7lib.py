#!/usr/bin/env python3
"""AR-0021 (independent compatibility/transaction review C of RoT-1 revision 7, d07d200) probe library.

Independence. `state_r7` is encoded by AR-0021 from the revision-7 text at d07d200:
  `18` §9 (state table, precedence sentence), §9.1 (closed entry sets, `.gitattributes` member), §9.2 (root discovery and
  working-directory refusal), §5.1 (honoured journals: per-project record lists the TX for this project_trust_id, repository
  path and locally recorded repository identity; untracked; foreign-artefact scan scope excluding completed `done/` archives
  this machine registered), `26` §2 (layout), `20` §9 (record identity).
It does not import or copy reviewer C's `c6lib.state_r6`, the architect's `crashmig7.state_r7` or any pack instrument.
Where the text admits more than one reading, every reading is computed and reported (`readings`), never resolved silently:
  ABSENT/type    "no occupation entries" = no entry of the occupation TYPE at an occupation path; "legacy entries" exactly the
                 two the row names (governance/framework.lock file, governance/kernel directory)
  ABSENT/path    any entry at an occupation path blocks ABSENT
  LMI/narrow     "moved and legacy entries coexist": legacy entries are the two the ABSENT row names
  LMI/broad      legacy entries also include the legacy-named directories (governance/project, governance/generated,
                 spec/audits/GOVERNANCE-ADOPTION, .governance-runtime/update)

Hygiene. Child processes get a constructed environment (PATH, HOME, XDG_*, GOV_KERNEL_CACHE in scratch; no other GOV_* unless
a probe sets it as the object of the test). Git runs with GIT_CONFIG_NOSYSTEM=1, a scratch GIT_CONFIG_GLOBAL,
GIT_OPTIONAL_LOCKS=0 and core.hooksPath=/dev/null. Whole-tree maps record every entry (type, mode, size, SHA-256, link count).
"""
import hashlib, json, os, re, shutil, stat, subprocess, time

SCR = os.environ.get("AR21_SCRATCH", "")
WT = os.environ.get("AR21_WT", "")          # the review worktree (read-only; git show at legacy commits)
EXPORT = os.environ.get("AR21_EXPORT", "")  # git archive of d07d200 (pack text read from here)
VERSIONS = ("4.1.2", "4.1.3", "4.1.4", "4.1.5")
BINS = {v: os.path.join(SCR, "bin", "gov-" + v) for v in VERSIONS}
REL = {v: os.path.join(SCR, "releases", v) for v in VERSIONS}
CLEANPATH = "/usr/bin:/bin"

SENTINEL = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
FORMAT_OBJ = {"layout": "legacy-path-occupation-v1", "minimum_reader": "4.1.6", "trust_format": "rot-1"}
GITATTR = b"* -text\n"
OCC = {"governance/kernel": "file", "governance/project": "file", "governance/generated": "file",
       "governance/framework.lock": "dir", "spec/audits/GOVERNANCE-ADOPTION": "file", ".governance-runtime/migration": "file"}
OCC_DIR_SENTINEL = "ROT-1-TRUST-FORMAT"
TRUST_TOP = {"FORMAT": "file", "framework.lock": "file", "kernel": "dir", "release.dsse.json": "file", "development.json": "file",
             "registration.dsse.json": "file", "lineage": "dir", "state": "dir", "root": "dir", "profiles": "dir", ".gitattributes": "file"}
STMT_DIRS = ("state", "root", "lineage", "profiles")
TX = ".governance-runtime/trust-tx"
LEGACY_NAMED_DIRS = ("governance/project", "governance/generated", "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/update")
MOVED_NAMES = ("governance/overlay", "governance/views", "spec/audits/ADOPTION", ".governance-runtime/legacy-quarantine")
MARK1, MARK2 = "AR0021RESTRICTEDMARKER", "AR0021CUSTOMERMARKER"
CLASS_PATTERNS = ("product/restricted-plan.md", "product/customers/**")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            c = f.read(1 << 16)
            if not c:
                break
            h.update(c)
    return h.hexdigest()


def kind(p):
    try:
        m = os.lstat(p).st_mode
    except (FileNotFoundError, NotADirectoryError):
        return "absent"
    except OSError:
        return "oserror"
    if stat.S_ISLNK(m):
        return "link"
    if stat.S_ISDIR(m):
        return "dir"
    if stat.S_ISREG(m):
        return "file"
    return "special"


def env_child(home, cache, extra=None):
    os.makedirs(home, exist_ok=True)
    e = {"PATH": CLEANPATH, "HOME": home, "LANG": "C.UTF-8", "USER": "ar21", "LOGNAME": "ar21",
         "XDG_CACHE_HOME": os.path.join(home, ".cache"), "XDG_CONFIG_HOME": os.path.join(home, ".config"),
         "XDG_STATE_HOME": os.path.join(home, ".local", "state"), "XDG_DATA_HOME": os.path.join(home, ".local", "share"),
         "GOV_KERNEL_CACHE": cache, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.path.join(home, ".gitconfig"),
         "GIT_AUTHOR_NAME": "ar21", "GIT_AUTHOR_EMAIL": "ar21@example.invalid", "GIT_COMMITTER_NAME": "ar21",
         "GIT_COMMITTER_EMAIL": "ar21@example.invalid", "PYTHONDONTWRITEBYTECODE": "1"}
    if extra:
        e.update(extra)
    for k in e:
        assert not k.startswith("GOV_") or k == "GOV_KERNEL_CACHE" or (extra and k in extra), k
    return e


def git(cwd, *args, home=None, check=True, env_extra=None, cfg=()):
    home = home or os.path.join(SCR, "githome")
    os.makedirs(home, exist_ok=True)
    e = {"PATH": CLEANPATH, "HOME": home, "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.path.join(home, ".gitconfig"),
         "GIT_OPTIONAL_LOCKS": "0", "GIT_AUTHOR_NAME": "ar21", "GIT_AUTHOR_EMAIL": "ar21@example.invalid", "GIT_COMMITTER_NAME": "ar21",
         "GIT_COMMITTER_EMAIL": "ar21@example.invalid", "GIT_AUTHOR_DATE": "2026-09-14T00:00:00Z", "GIT_COMMITTER_DATE": "2026-09-14T00:00:00Z"}
    if env_extra:
        e.update(env_extra)
    pre = ["git", "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null", "-c", "advice.detachedHead=false", "-c", "protocol.file.allow=always"]
    for c in cfg:
        pre += ["-c", c]
    r = subprocess.run(pre + list(args), cwd=cwd, env=e, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError("git %s @%s rc=%d: %s" % (" ".join(args), cwd, r.returncode, r.stderr[-400:]))
    return r


def gov(binary, argv, env, cwd, root=None, timeout=240):
    cmd = [binary, "--json"] + (["--root", root] if root is not None else []) + list(argv)
    t = time.time()
    try:
        r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        out, rc = r.stdout, r.returncode
        err = r.stderr
    except subprocess.TimeoutExpired:
        out, rc, err = "", -999, "TIMEOUT"
    try:
        d = json.loads(out)
        d = d if isinstance(d, dict) else {"value": d}
    except Exception:
        d = {"raw": out[-300:], "stderr": err[-300:]}
    d["_rc"] = rc
    d["_s"] = round(time.time() - t, 2)
    return d


def ecode(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def res(d):
    r = d.get("result")
    return r if isinstance(r, dict) else {}


# ---------------------------------------------------------------------------------------------------------- whole-tree maps
def entry(p):
    try:
        st = os.lstat(p)
    except OSError as e:
        return "error:%s" % (e.strerror or e.errno)
    m = stat.S_IMODE(st.st_mode)
    if stat.S_ISLNK(st.st_mode):
        return "l:" + os.readlink(p)
    if stat.S_ISDIR(st.st_mode):
        return "d:%o" % m
    if stat.S_ISREG(st.st_mode):
        try:
            return "f:%o:%d:%s:%d" % (m, st.st_size, fsha(p), st.st_nlink)
        except OSError as e:
            return "f-unreadable:%s" % (e.strerror or e.errno)
    return "s:%o" % stat.S_IFMT(st.st_mode)


def tmap(base):
    if not os.path.lexists(base):
        return {}
    if not stat.S_ISDIR(os.lstat(base).st_mode):
        return {".": entry(base)}
    out = {}
    for dp, dns, fns in os.walk(base, followlinks=False, onerror=lambda e: out.__setitem__("<walk-error>:" + str(getattr(e, "filename", ""))[-120:], "error:%s" % e.strerror)):
        for n in dns + fns:
            p = os.path.join(dp, n)
            try:
                out[os.path.relpath(p, base)] = entry(p)
            except FileNotFoundError:
                out[os.path.relpath(p, base)] = "vanished"
    return out


def dmap(m):
    return sha(json.dumps(m, sort_keys=True).encode())


def changed(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def part(paths):
    out = {}
    for p in paths:
        if p == ".git" or p.startswith(".git/"):
            k = "git"
        elif p == "governance/trust" or p.startswith("governance/trust/"):
            k = "pps_trust"
        elif p in OCC or p.startswith("governance/framework.lock/"):
            k = "pps_occupation"
        elif p == TX or p.startswith(TX + "/"):
            k = "pps_txarea"
        elif p == "governance/overlay" or p.startswith("governance/overlay/"):
            k = "overlay"
        elif p == "governance/views" or p.startswith("governance/views/"):
            k = "views"
        elif p.startswith("governance/"):
            k = "governance_other"
        elif p == ".gitignore" or p.endswith("/.gitignore"):
            k = "gitignore"
        elif p.startswith(".governance-runtime/"):
            k = "runtime_other"
        else:
            k = "project_other"
        out[k] = out.get(k, 0) + 1
    return out


# ---------------------------------------------------------------------------------------------------------- revision-7 predicate
def lock_ptid(root):
    try:
        return json.load(open(os.path.join(root, "governance/trust/framework.lock"))).get("project_trust_id")
    except Exception:
        return None


def lock_files(root):
    try:
        d = json.load(open(os.path.join(root, "governance/trust/framework.lock")))
        return {k: v.split(":", 1)[1] for k, v in d["kernel"]["files"].items()}
    except Exception:
        return None


def kernel_files(kd):
    out, others, dirs = {}, [], set()
    for dp, dns, fns in os.walk(kd, followlinks=False):
        for n in dns + fns:
            p = os.path.join(dp, n)
            k = kind(p)
            rel = os.path.relpath(p, kd)
            if k == "file":
                try:
                    out[rel] = fsha(p)
                except OSError:
                    others.append(rel)
            elif k == "dir":
                dirs.add(rel)
            else:
                others.append(rel)
    return out, others, dirs


def nested_legacy(root):
    inside, elsewhere = [], []
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel = os.path.relpath(dp, root)
        if rel == ".git" or rel.startswith(".git/"):
            dns[:] = []
            continue
        if "governance" in dns:
            g = os.path.join(dp, "governance")
            grel = os.path.relpath(g, root)
            if grel != "governance" and (kind(os.path.join(g, "framework.lock")) == "file" or kind(os.path.join(g, "kernel", "KERNEL_MANIFEST.json")) == "file"):
                (inside if grel.startswith("governance/") else elsewhere).append(grel)
    return sorted(inside), sorted(elsewhere)


def tracked(root, path):
    if kind(os.path.join(root, ".git")) == "absent":
        return set()
    r = git(root, "ls-files", "--", path, check=False)
    return set(r.stdout.split())


def journals(root, record, repo_identity):
    """`18` §5.1 (revision 7): honoured only if the per-project record lists <TX> as open for this project_trust_id, repository path
    and locally recorded repository identity, and the journal is untracked. Scan scope: trust-tx/<TX>/ directories; a completed
    done/<TX> archive this machine registered is not reported."""
    base = os.path.join(root, TX)
    honoured, foreign, done_unreg = [], [], []
    if kind(base) != "dir":
        return honoured, foreign, done_unreg
    tr = tracked(root, TX)
    real = os.path.realpath(root)
    for n in sorted(os.listdir(base)):
        d = os.path.join(base, n)
        if n == "done" and kind(d) == "dir":
            for m in sorted(os.listdir(d)):
                if kind(os.path.join(d, m, "journal.json")) == "file" and not (record and m in record.get("done_tx", ())):
                    done_unreg.append(TX + "/done/" + m)
            continue
        if n == "abandoned":
            continue
        j = os.path.join(d, "journal.json")
        if kind(j) != "file":
            continue
        rel = os.path.relpath(j, root)
        ok = (record is not None and n in record.get("open_tx", ()) and record.get("project_trust_id") == record.get("tx_ptid", {}).get(n, record.get("project_trust_id"))
              and real in record.get("paths", ()) and record.get("identity") == repo_identity and rel not in tr)
        (honoured if ok else foreign).append(rel)
    return honoured, foreign, done_unreg


def journal_phase(root, rel):
    try:
        return json.load(open(os.path.join(root, rel))).get("phase")
    except Exception:
        return None


def state_r7(root, record=None, repo_identity=None, rcs=None):
    g = lambda p: os.path.join(root, p)
    t = g("governance/trust")
    occ_kind = {p: kind(g(p)) for p in OCC}
    occ_typed = {p: occ_kind[p] == OCC[p] for p in OCC}
    trust_present = kind(t) == "dir"
    legacy2 = kind(g("governance/framework.lock")) == "file" or kind(g("governance/kernel")) == "dir"
    legacy_named = [p for p in LEGACY_NAMED_DIRS if kind(g(p)) == "dir"]
    moved = [p for p in MOVED_NAMES if kind(g(p)) == "dir"]
    overlay_or_views = kind(g("governance/overlay")) != "absent" or kind(g("governance/views")) != "absent"
    inside, elsewhere = nested_legacy(root)
    honoured, foreign, done_unreg = journals(root, record, repo_identity)
    reports = []
    if elsewhere:
        reports.append(["NESTED_LEGACY_PROJECT", elsewhere])
    if foreign:
        reports.append(["FOREIGN_TRANSACTION_ARTEFACT", foreign])
    if done_unreg:
        reports.append(["DONE_ARCHIVE_NOT_REGISTERED", done_unreg])
    # complete-row conditions
    reasons = []
    if not (trust_present and kind(os.path.join(t, "FORMAT")) == "file" and kind(os.path.join(t, "framework.lock")) == "file"
            and kind(os.path.join(t, "kernel")) == "dir" and (kind(os.path.join(t, "release.dsse.json")) == "file" or kind(os.path.join(t, "development.json")) == "file")):
        reasons.append("trust_components")
    if not all(occ_typed.values()):
        reasons.append("occupation")
    if legacy2:
        reasons.append("legacy_and_rot1_mixed")
    fmt_bad = False
    if trust_present:
        if kind(os.path.join(t, "FORMAT")) == "file":
            try:
                fmt_bad = json.loads(open(os.path.join(t, "FORMAT"), "rb").read()) != FORMAT_OBJ
            except Exception:
                fmt_bad = True
        for dp, dns, fns in os.walk(t, followlinks=False):
            if any(kind(os.path.join(dp, n)) == "link" for n in dns + fns):
                reasons.append("foreign_trust_entry(symlink)")
                break
        for n in os.listdir(t):
            if TRUST_TOP.get(n) != kind(os.path.join(t, n)):
                reasons.append("foreign_trust_entry(%s)" % n)
        ga = os.path.join(t, ".gitattributes")
        if kind(ga) != "file":
            reasons.append("trust_components(.gitattributes)")
        elif open(ga, "rb").read() != GITATTR:
            reasons.append("foreign_trust_entry(.gitattributes_content)")
        if kind(os.path.join(t, "kernel")) == "dir":
            files, others, dirs = kernel_files(os.path.join(t, "kernel"))
            lf = lock_files(root)
            need = set()
            for f in (lf or {}):
                parts = f.split("/")
                for i in range(1, len(parts)):
                    need.add("/".join(parts[:i]))
            if lf is None or others or files != lf or (dirs - need):
                reasons.append("kernel_content_mismatch")
            for dp, dns, fns in os.walk(os.path.join(t, "kernel")):
                for n in fns:
                    try:
                        if os.lstat(os.path.join(dp, n)).st_nlink != 1:
                            reasons.append("link_count(VU-12)")
                            break
                    except FileNotFoundError:
                        pass
        for sd in STMT_DIRS:
            d = os.path.join(t, sd)
            if kind(d) == "dir" and any(kind(os.path.join(d, n)) != "file" or not n.endswith(".dsse.json") for n in os.listdir(d)):
                reasons.append("foreign_trust_entry(%s/)" % sd)
    fl = g("governance/framework.lock")
    if kind(fl) == "dir" and (sorted(os.listdir(fl)) != [OCC_DIR_SENTINEL] or kind(os.path.join(fl, OCC_DIR_SENTINEL)) != "file"):
        reasons.append("foreign_occupation_entry")
    if inside:
        reasons.append("nested_legacy_install")
    reasons = sorted(set(reasons))
    rows = set()
    if fmt_bad:
        rows.add("FORMAT_UNSUPPORTED")
    if honoured:
        rows.add("IN_TRANSACTION")
    lmi_journal = any(str(journal_phase(root, j) or "").startswith(("layout-", "exchange-intent")) for j in honoured)
    lmi_narrow = bool(moved) and legacy2
    lmi_broad = bool(moved) and (legacy2 or bool(legacy_named))
    readings = {}
    base_absent = not trust_present and not legacy2 and not overlay_or_views
    readings["ABSENT/type"] = base_absent and not any(occ_typed.values())
    readings["ABSENT/path"] = base_absent and all(v == "absent" for v in occ_kind.values())
    readings["LMI/narrow"] = lmi_narrow or lmi_journal
    readings["LMI/broad"] = lmi_broad or lmi_journal
    legacy_row = legacy2 and not trust_present
    complete_row = not reasons and not honoured and not fmt_bad
    order = ["FORMAT_UNSUPPORTED", "IN_TRANSACTION", "LAYOUT_MIGRATION_INCOMPLETE", "ABSENT", "LEGACY", "COMPLETE", "PARTIAL"]

    def headline(absent_key, lmi_key):
        r = set(rows)
        if readings[lmi_key]:
            r.add("LAYOUT_MIGRATION_INCOMPLETE")
        if readings[absent_key]:
            r.add("ABSENT")
        if legacy_row:
            r.add("LEGACY")
        if complete_row:
            r.add("COMPLETE")
        if not r:
            r.add("PARTIAL")
        return sorted(r, key=order.index)[0], sorted(r, key=order.index)
    by_reading = {}
    for ak in ("ABSENT/type", "ABSENT/path"):
        for lk in ("LMI/narrow", "LMI/broad"):
            by_reading["%s+%s" % (ak, lk)] = headline(ak, lk)[0]
    state, matched = headline("ABSENT/path", "LMI/narrow")
    out = {"state": state, "rows": matched, "by_reading": by_reading, "readings": readings, "reasons": reasons, "reports": reports,
           "honoured": honoured, "foreign": foreign, "legacy_named_dirs": legacy_named, "moved_names": moved,
           "overlay_or_views": overlay_or_views, "nested_under_governance": inside}
    if rcs is not None:
        out["kernel_tampered"] = kernel_tampered(root, rcs)
    return out


def kernel_tampered(root, rcs):
    k = os.path.join(root, "governance/trust/kernel")
    if kind(k) != "dir":
        return True
    files, others, _ = kernel_files(k)
    return files != rcs or bool(others)


def states_allowing(state):
    """`18` §9 'Allowed' column (revision 7), for the RoT-1 commands this review asks about."""
    return {"ABSENT": ["init"], "LEGACY": ["update --apply (layout migration)"], "IN_TRANSACTION": ["recover"],
            "LAYOUT_MIGRATION_INCOMPLETE": ["recover"], "PARTIAL": ["kernel reinstall", "update --apply", "recover", "init --force"],
            "COMPLETE": ["per verdict"], "FORMAT_UNSUPPORTED": []}.get(state, [])


def rinit9_refuses(root):
    """`09`/`26` R-INIT-9 as written: refuses only when governance/overlay or governance/views exists."""
    return kind(os.path.join(root, "governance/overlay")) != "absent" or kind(os.path.join(root, "governance/views")) != "absent"


PPS_CWD = ("governance/trust", "governance/framework.lock", TX)


def discover_r7(start):
    start = os.path.realpath(start)
    cur, root = start, None
    while True:
        if kind(os.path.join(cur, "governance/trust/FORMAT")) == "file":
            root = cur
            break
        nx = os.path.dirname(cur)
        if nx == cur:
            break
        cur = nx
    if root is None:
        return {"root": None, "refuse": False}
    rel = os.path.relpath(start, root)
    return {"root": root, "refuse": rel in OCC or any(rel == p or rel.startswith(p + "/") for p in PPS_CWD)}


def classifications(root):
    import yaml
    found = {}
    for ov in ("governance/overlay", "governance/project"):
        p = os.path.join(root, ov, "DATA_SENSITIVITY.yaml")
        if kind(p) == "file":
            try:
                d = yaml.safe_load(open(p)) or {}
                pats = {c.get("pattern") for c in (d.get("classifications") or []) if isinstance(c, dict)}
                found[ov] = set(CLASS_PATTERNS) <= pats
            except Exception:
                found[ov] = False
    return found


def scrub(s):
    for a, b in ((SCR, "<ar21>"), (WT, "<wt>"), (EXPORT, "<export>")):
        if a:
            s = s.replace(a, b)
    return s


def dump(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write(scrub(json.dumps(obj, indent=1, sort_keys=True, default=lambda o: sorted(o) if isinstance(o, set) else str(o))))
