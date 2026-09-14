#!/usr/bin/env python3
"""AR-0003 independent probe library. Scratch only; strips GOV_* from children; GOV_KERNEL_CACHE/HOME into scratch."""
import hashlib, json, os, shutil, subprocess, sys, time

LEG = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin"
REPO = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r3-c"
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project"
MARK = "AR0003RESTRICTEDMARKER"
CLEANPATH = "/usr/bin:/bin:/usr/local/bin"
BINS = {v: os.path.join(LEG, f"gov-{v}") for v in ("4.1.2", "4.1.3", "4.1.4", "4.1.5")}


def child_env(scratch, tag):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    home = os.path.join(scratch, "homes", tag)
    os.makedirs(home, exist_ok=True)
    env["PATH"] = CLEANPATH
    env["HOME"] = home
    env["GOV_KERNEL_CACHE"] = os.path.join(scratch, "caches", tag)
    env["XDG_CACHE_HOME"] = os.path.join(home, ".cache")
    env["XDG_CONFIG_HOME"] = os.path.join(home, ".config")
    env["XDG_STATE_HOME"] = os.path.join(home, ".local/state")
    for k in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"): env[k] = "ar3"
    for k in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"): env[k] = "ar3@x"
    return env


def git(root, *a, check=True):
    return subprocess.run(["git", "-c", "user.name=ar3", "-c", "user.email=ar3@x",
                           "-c", "init.defaultBranch=main", *a], cwd=root, check=check,
                          capture_output=True, text=True, env={"PATH": CLEANPATH, "HOME": root})


def gov(binary, root, args, env, timeout=180):
    try:
        r = subprocess.run([binary, "--json", "--root", root, "--session", "S-ar3", "--role", "orchestrator", *args],
                           env=env, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, cwd=root)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = "", "TIMEOUT", -999
    try:
        d = json.loads(out)
    except Exception:
        d = {"raw": (out or "")[-300:], "stderr": (err or "")[-200:]}
    d["_rc"] = rc
    return d


def code(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


EXCL = {".git", ".governance-runtime"}


def file_map(root, exclude_runtime=True):
    """Whole-tree map: relpath -> type+digest. Records entry TYPE (file/dir/link) so type-flips are visible."""
    m = {}
    excl = EXCL if exclude_runtime else {".git"}
    for dp, dns, fns in os.walk(root):
        rel = os.path.relpath(dp, root)
        if rel == ".":
            dns[:] = sorted(d for d in dns if d not in excl)
        else:
            dns.sort()
        for d in list(dns):
            p = os.path.join(dp, d)
            r = os.path.relpath(p, root)
            m[r + "/"] = "link:" + os.readlink(p) if os.path.islink(p) else "dir"
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            r = os.path.relpath(p, root)
            if os.path.islink(p):
                m[r] = "link:" + os.readlink(p)
            elif os.path.isfile(p):
                m[r] = "f:" + hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
            else:
                m[r] = "special"
    return m


def digest(m):
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:16]


def git_state(root):
    def g(*a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True,
                              env={"PATH": CLEANPATH, "HOME": root}).stdout
    return {"head": g("rev-parse", "HEAD").strip(),
            "index": hashlib.sha256(g("ls-files", "-s").encode()).hexdigest()[:16],
            "status": g("status", "--porcelain").strip(),
            "stash": g("stash", "list").strip()}


def changed(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
