#!/usr/bin/env python3
"""P2-AR-0022 (integration builder) — P2-HO-0019 step 4, last bullet: run the WS-2 health scheduler under concurrency
against a COLD embedded-kernel cache and confirm the integrated tree does not trip the `kernel::embedded_kernel_dir`
race WS-2 found (IP-WS02-15; its root-cause fix is round 2, WS-8).

Integration evidence only (Contract v3 O3). Every scenario runs on an isolated simulated machine: private HOME,
XDG_STATE_HOME and XDG_CACHE_HOME under the scratch directory, no GOV_* variable inherited, no GOV_CANONICAL_ROOT (so
the embedded payload is what `init` and every embedded-baseline substitution use). The cache the concurrent runs see is
a fresh, empty XDG_CACHE_HOME ("cold"). After the concurrent runs the cache is compared, byte for byte, with the payload
this binary embeds (reconstructed from the worktree exactly as runtime/build.rs selects it), and a later `gov init`
that materialises nothing (it reuses that cache) must succeed and verify.

Scenarios:
  U-trusted    unprovisioned machine, trusted installed kernel; sandboxed checks (context_reproducibility,
               memory_retrieval_regression, recovery_rebuild, skill scenarios) evaluate kernel trust for copies of the
               project at other paths (WS-8's per-project installation record is keyed by path).
  U-untrusted  unprovisioned machine, installed kernel edited after install (untrusted: the embedded baseline is
               substituted, which is the path that materialises the cache) — WS-2's own S-J scenario, integrated.
  P-trusted    provisioned machine (throw-away root from the alpha-r test-material keys, via WS-8's probe helpers),
               kernel installed from a signed release: live kernel anchored by this machine's per-project record,
               sandbox copies at other paths anchored (or not) by the verified-release ledger.
  P-untrusted  as P-trusted, then a mutually consistent payload + KERNEL_MANIFEST.json + framework.lock rewrite
               (BC-P2-35): the live kernel is untrusted on a provisioned machine.
Each scenario runs TRIALS (default 5) trials, each against a new empty cache: 4 concurrent processes (3 x `gov health
run --no-cache --no-persist`, 1 x `gov doctor`); each health run itself runs its checks on a worker pool with
sandboxed state-writing checks, and doctor runs its check groups on threads.

Usage: GOV=<gov> P2AR0022_SCRATCH=<dir> python3 cold_cache_scheduler.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.environ.get("GOV", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("P2AR0022_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0022-cc-")
os.makedirs(SCR, exist_ok=True)
os.environ["PROBE_TMP"] = SCR
os.environ["GOV"] = GOV
RESULTS = []


def check(name, ok, what, detail=None):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name} {'PASS' if ok else 'FAIL'} {what}", flush=True)
    if detail is not None:
        print("      detail:", json.dumps(detail, sort_keys=True, default=str)[:2000], flush=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def expected_payload():
    """The embedded payload, reconstructed as runtime/build.rs selects it: framework/** (README.md dropped),
    migrations/** and tools/** (README.md kept)."""
    out = {}
    for base, prefix in (("framework", ""), ("migrations", "migrations"), ("tools", "tools")):
        root = os.path.join(WT, base)
        for d, _, fs in os.walk(root):
            for f in fs:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                rel = f"{prefix}/{rel}" if prefix else rel
                if rel.endswith("README.md") and not (rel.startswith("migrations") or rel.startswith("tools")):
                    continue
                out[rel] = sha(open(p, "rb").read())
    return out


EXPECTED = expected_payload()


def cache_report(cache_home):
    kernels = os.path.join(cache_home, "gov", "kernels")
    rep = {"kernels_dir_exists": os.path.isdir(kernels), "entries": [], "staging_leftovers": []}
    if not os.path.isdir(kernels):
        return rep
    for name in sorted(os.listdir(kernels)):
        d = os.path.join(kernels, name)
        if name.startswith(".staging-"):
            rep["staging_leftovers"].append(name)
            continue
        files = {}
        for dd, _, fs in os.walk(d):
            for f in fs:
                p = os.path.join(dd, f)
                files[os.path.relpath(p, d).replace(os.sep, "/")] = sha(open(p, "rb").read())
        complete = files.pop(".complete", None) is not None
        missing = sorted(set(EXPECTED) - set(files))
        extra = sorted(set(files) - set(EXPECTED))
        differ = sorted(r for r in set(files) & set(EXPECTED) if files[r] != EXPECTED[r])
        rep["entries"].append({"dir": name, "files": len(files), "expected_files": len(EXPECTED), "complete_marker": complete,
                               "missing": missing[:10], "n_missing": len(missing), "extra": extra[:10],
                               "differing": differ[:10], "n_differing": len(differ)})
    return rep


def cache_ok(rep):
    """A cache is sound when every entry marked complete holds exactly the embedded payload."""
    return all(e["n_missing"] == 0 and not e["extra"] and e["n_differing"] == 0
               for e in rep["entries"] if e["complete_marker"])


class Machine:
    def __init__(self, name):
        self.dir = tempfile.mkdtemp(prefix=f"{name}-", dir=SCR)
        self.home = os.path.join(self.dir, "home")
        os.makedirs(self.home)
        self.state = os.path.join(self.dir, "state")
        self.cache = os.path.join(self.dir, "cache-install")

    def env(self, cache=None):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
        e.update({"HOME": self.home, "XDG_STATE_HOME": self.state, "XDG_CACHE_HOME": cache or self.cache,
                  "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
                  "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
        return e

    def argv(self, root, args, role="orchestrator"):
        return [GOV, "--json", "--root", root, "--session", "S-cc", "--role", role, *args]

    def run(self, root, *args, cache=None, role="orchestrator"):
        p = subprocess.run(self.argv(root, args, role), capture_output=True, text=True, env=self.env(cache))
        try:
            return json.loads(p.stdout)
        except Exception:
            return {"ok": False, "error": {"code": "NON_JSON", "message": (p.stdout + p.stderr)[-500:]}}

    def concurrent(self, root, cache, argvs):
        procs = [subprocess.Popen(self.argv(root, a), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  env=self.env(cache)) for a in argvs]
        outs = []
        for a, p in zip(argvs, procs):
            so, se = p.communicate()
            try:
                v = json.loads(so)
            except Exception:
                v = {"ok": False, "error": {"code": "NON_JSON", "message": (so + se)[-300:]}}
            outs.append({"cmd": " ".join(a), "exit": p.returncode, "ok": v.get("ok"),
                         "error": (v.get("error") or {}).get("code"),
                         "verdict": (v.get("result") or {}).get("verdict") if isinstance(v.get("result"), dict) else None,
                         "threads": ((v.get("result") or {}).get("parallelism") or {}) if isinstance(v.get("result"), dict) else None})
        return outs

    def repo(self, name):
        d = os.path.join(self.dir, name)
        shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), d)
        e = self.env()
        for a in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "fixture"]):
            subprocess.run(["git", *a], cwd=d, env=e, capture_output=True)
        return d


RUNS = [["health", "run", "--no-cache", "--no-persist"]] * 3 + [["doctor"]]
print(f"# gov={GOV} sha256={sha(open(GOV, 'rb').read())}")
print(f"# worktree HEAD={subprocess.run(['git', '-C', WT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
print(f"# embedded payload (reconstructed): {len(EXPECTED)} files")


TRIALS = int(os.environ.get("TRIALS", "5"))


def scenario(tag, m, proj, prepare_untrusted=None):
    if prepare_untrusted:
        prepare_untrusted(proj)
    kt = m.run(proj, "kernel", "trust")
    trusted = (kt.get("result") or {}).get("verified")
    reps, materialised, last = [], 0, None
    for n in range(TRIALS):
        cold = os.path.join(m.dir, f"cache-cold-{tag}-{n}")
        assert not os.path.exists(cold)
        outs = m.concurrent(proj, cold, RUNS)
        rep = cache_report(cold)
        materialised += 1 if rep["entries"] else 0
        reps.append({"trial": n, "runs": [(o["cmd"], o["ok"], o["error"]) for o in outs], "cache": rep})
        last = cold
        if n == 0:
            print(f"# {tag}: kernel trust verified={trusted}; trial 0 concurrent runs: {json.dumps(outs, default=str)[:1500]}")
    check(f"{tag}.runs-complete", all(r[2] in (None, "UNHEALTHY") for t in reps for r in t["runs"]),
          f"in {TRIALS} cold-cache trials every concurrent run returned a JSON result (a verdict, possibly UNHEALTHY), never an internal failure",
          [t["runs"] for t in reps])
    check(f"{tag}.cache-sound", all(cache_ok(t["cache"]) and not t["cache"]["staging_leftovers"] for t in reps),
          f"in {TRIALS} cold-cache trials every cache entry marked complete is byte-identical to the embedded payload; no staging leftovers "
          f"(cache materialised during the concurrent runs in {materialised}/{TRIALS} trials)",
          [t["cache"] for t in reps][:2])
    # a later embedded init reuses the cache the concurrent runs left behind: on a fresh UNPROVISIONED machine sharing
    # that per-user cache (a provisioned machine refuses the unsigned embedded payload, SRR_RELEASE_UNVERIFIED, which
    # says nothing about the cache)
    u = Machine(f"{tag}-consumer")
    fresh = u.repo(f"fresh-{tag}")
    i = u.run(fresh, "init", "--name", f"f{tag}", "--alias", f"f-{tag.lower()}", "--skip-index", cache=last)
    kv = u.run(fresh, "kernel", "verify", cache=last)
    check(f"{tag}.later-init", i.get("ok") and (kv.get("result") or {}).get("ok") is True,
          "a later embedded `gov init` using that cache (fresh unprovisioned machine) succeeds and its kernel verifies",
          {"init": i.get("ok") or (i.get("error") or {}).get("code"), "kernel_verify_ok": (kv.get("result") or {}).get("ok"),
           "after": cache_report(last)})
    return trusted


# ---- U: unprovisioned machine, kernel installed from the embedded payload
m = Machine("U")
proj = m.repo("proj")
r = m.run(proj, "init", "--name", "cc", "--alias", "cc-u")
assert r.get("ok"), r
t = scenario("U-trusted", m, proj)
print(f"# U-trusted: live kernel trusted={t}")


def touch_kernel(p):
    with open(os.path.join(p, "governance/kernel/schemas/task.schema.json"), "a") as f:
        f.write("\n")


m2 = Machine("U2")
proj2 = m2.repo("proj")
r = m2.run(proj2, "init", "--name", "cc", "--alias", "cc-u2")
assert r.get("ok"), r
t = scenario("U-untrusted", m2, proj2, prepare_untrusted=touch_kernel)
check("U-untrusted.precondition", t is False, "the edited installed kernel is untrusted (embedded baseline substituted)", t)

# ---- P: provisioned machine (test-material keys; WS-8 probe helpers, read-only reuse)
sys.path.insert(0, os.path.join(WT, "release", "capability-baseline", "repair-1", "ws08", "evidence"))
import ws08_common as C  # noqa: E402

for tag, untrusted in (("P-trusted", False), ("P-untrusted", True)):
    sb = C.Sandbox(tag)
    C.provision(sb)
    rel = C.Releases(sb)
    k = rel.sign(rel.build(f"rel-{tag}"), sequence=20)
    mm = Machine(tag)
    # the provisioned machine is the Sandbox's (its HOME carries the state root); reuse its environment
    mm.home = sb.home
    mm.state = sb.env.get("XDG_STATE_HOME", os.path.join(sb.home, ".local", "state"))
    base_env = dict(sb.env)

    def env(cache=None, _b=base_env):
        e = dict(_b)
        e["XDG_CACHE_HOME"] = cache or os.path.join(sb.dir, "cache-install")
        return e
    mm.env = env
    pj = mm.repo("proj")
    r = mm.run(pj, "init", "--source", k, "--name", "cc", "--alias", f"cc-{tag.lower()}", "--skip-index")
    check(f"{tag}.install", r.get("ok"), "authentic release installed on the provisioned machine",
          r.get("ok") or r.get("error"))
    prep = (lambda p: C.consistent_rewrite(p, "policies/SECURITY_POLICY.yaml", "never_index_classes: [secret, restricted]",
                                           "never_index_classes: []")) if untrusted else None
    t = scenario(tag, mm, pj, prepare_untrusted=prep)
    check(f"{tag}.precondition", t is (not untrusted), f"live kernel trusted={not untrusted} as intended", t)

print("\nSUMMARY checks=%d pass=%d fail=%d failed=%s" % (len(RESULTS), sum(1 for _, o in RESULTS if o),
                                                         sum(1 for _, o in RESULTS if not o), [n for n, o in RESULTS if not o]))
