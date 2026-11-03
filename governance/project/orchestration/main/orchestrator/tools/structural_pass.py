"""One cheap structural pass on a tree's head (R1-21, DEC-1052): a notice to the CTO, never a refusal.

    python3 structural_pass.py <repo> [<base>] [--timeout <s>]

Runs, each in a process of its own, all at once, each within a time bound (default 50 s), in <repo> with
PYTHONPATH=<repo>/src (no GIT_* variable inherited), the declared checks `gov check`'s runner runs for these families:
schema (core-schema), graph (core-graph), claims (core-claims), mutation (core-mutation), authority (core-authority),
pathmap (core-pathmap), audit (audit-reproducibility: the audit validator on docs/audit/) and skills (every declaration
that runs the skill validator). Each command is the tree's own declaration
(template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml) when it is a
`python3 -m gov.<module> ...` command, else the built-in one below. Portability (adapter-portability, R1-10) runs only
when the change <base>..HEAD touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when
<base> does not resolve; with no <base> it is left out.

Prints one line per family, `<family>: ok`, `<family>: ok (not applicable: ...)`, `<family>: skipped (...)` or
`<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`. Exit 0
whatever the checks find; 2 only when it could not run at all (no such folder, not a git work tree, bad arguments).

After a landing: tools/land.py calls it on the new head (base: the head before the queue run) and puts its lines in
the landing's log, plus one inbox item when a family is not ok.

After the CTO's record commits (tickets, the register, the path map), in the main tree, by hand (<base>: the commit
before them; HEAD~1 after one commit):

    python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS HEAD~1

Measured on the main tree (2026-11-03): see the CTO lane's R1-21 return. Later replaced by T-2's `--families`.
"""
import argparse
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CHECKS_DIRS = ("template/governance/kernel/checks", "governance/kernel/checks")  # gov.cli.checks.CHECKS_DIRS
# (family, declaration ids, built-in command for each id): today's declarations, used where the tree has none
FAMILIES = (
    ("schema", {"core-schema": "python3 -m gov.check.schema"}),
    ("graph", {"core-graph": "python3 -m gov.check.graph"}),
    ("claims", {"core-claims": "python3 -m gov.check.claims"}),
    ("mutation", {"core-mutation": "python3 -m gov.check.mutation"}),
    ("authority", {"core-authority": "python3 -m gov.check.authority"}),
    ("pathmap", {"core-pathmap": "python3 -m gov.check.pathmap"}),
    ("audit", {"audit-reproducibility": "python3 -m gov.check.audit_validator docs/audit/"}),
    ("skills", {  # every declaration whose command runs the skill validator (found in the tree, else these)
        "skill-regression-a": "python3 -m gov.check.skill_validator --both-layouts "
                              + " ".join(f"template/governance/kernel/skills/{s}"
                                         for s in ("discovery", "planning", "test-design", "change")),
        "skill-regression-b1": "python3 -m gov.check.skill_validator --both-layouts "
                               + " ".join(f"template/governance/kernel/skills/{s}"
                                          for s in ("retrieval", "audit", "checkpoint", "adopt")),
        "skill-regression-orchestration": "python3 -m gov.check.skill_validator --both-layouts "
                                          "template/governance/kernel/skills/orchestration"}),
)
PORTABILITY = ("portability", {"adapter-portability": "python3 -m gov.adapters.portability"})
PORTABILITY_PATHS = tuple(f"template/governance/kernel/{d}/" for d in ("roles", "skills", "hooks")) + (".rulesync/",)
SHOWN = 3  # findings shown on a family's line
WIDTH = 160  # characters of each one


class CannotRun(Exception):
    pass


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, timeout=60)


def declared(repo):
    """{id: command} of the tree's own `python3 -m gov.` declarations (a yaml that cannot be read is left out)."""
    try:
        import yaml
    except ImportError:
        return {}
    found = {}
    for d in CHECKS_DIRS:
        for f in sorted((repo / d).glob("*.yaml")) if (repo / d).is_dir() else ():
            try:
                raw = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(raw, dict) and isinstance(raw.get("command"), str) and \
                    re.match(r"python3 -m gov\.[\w.]+(\s|$)", raw["command"].strip()):
                found.setdefault(str(raw.get("id", f.stem)), raw["command"].strip())
    return found


def plan(repo, with_portability):
    """[(family, [(id, command), ...]), ...]: the tree's declarations where it has them, else the built-in ones."""
    decl = declared(repo)
    out = []
    for family, builtin in FAMILIES + ((PORTABILITY,) if with_portability else ()):
        if family == "skills":
            ids = sorted(i for i, c in decl.items() if "gov.check.skill_validator" in c) or sorted(builtin)
        else:
            ids = list(builtin)
        out.append((family, [(i, decl.get(i) or builtin[i]) for i in ids]))
    return out


def run_one(repo, command, bound):
    """(exit code or None past the bound, stdout, stderr) of one declared command, in its own process group."""
    argv = [sys.executable, "-P", *shlex.split(command)[1:]]  # python3 -> this interpreter; -P: no cwd on the path
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["PYTHONPATH"] = str(repo / "src")
    p = subprocess.Popen(argv, cwd=str(repo), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = p.communicate(timeout=bound)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)  # the check and whatever it started (check-jsonschema, rulesync)
        except ProcessLookupError:
            pass
        p.communicate()
        return None, "", ""


def short(text):
    text = " ".join(str(text).split())
    return text if len(text) <= WIDTH else text[:WIDTH - 3] + "..."


def judge(check_id, rc, out, err, bound):
    """(ok, text) for one check: ok, 'not applicable: <why>', or what it found."""
    if rc is None:
        return False, [f"{check_id} did not end within {bound:g} s"]
    parsed = None
    try:
        parsed = json.loads(out) if out.strip() else None
    except json.JSONDecodeError:
        pass
    if rc == 0:
        return True, []
    if rc == 2 and isinstance(parsed, dict) and parsed.get("not_applicable") is True:
        return True, [f"not applicable: {parsed.get('reason', '')}"]
    if parsed is None and re.search(r"^(ModuleNotFoundError|ImportError|SyntaxError|\w+Error)\b", err, re.M):
        last = [l for l in err.strip().splitlines() if l.strip()][-1]
        return False, [f"{check_id} could not run: {last}"]
    findings = None
    if isinstance(parsed, list):
        findings = parsed
    elif isinstance(parsed, dict) and isinstance(parsed.get("findings"), list) and parsed["findings"]:
        findings = parsed["findings"]
    elif isinstance(parsed, dict) and parsed.get("unmeasured"):
        return False, [f"{check_id} unmeasured: {parsed.get('reason', '')}"]
    if findings:
        return False, [f.get("message") or json.dumps(f) if isinstance(f, dict) else str(f) for f in findings]
    first = (out.strip() or err.strip() or "no output").splitlines()[0]
    return False, [f"{check_id} exit {rc}: {first}"]


def family_line(family, results):
    """One line: ok, ok (not applicable ...), or NOTICE <n> finding(s): <first ones> (+k more)."""
    found = [t for ok, texts in results if not ok for t in texts]
    if not found:
        notes = [t for _, texts in results for t in texts]
        return True, f"{family}: ok" + (f" ({short('; '.join(notes))})" if notes else "")
    shown = " | ".join(short(t) for t in found[:SHOWN])
    more = f" (+{len(found) - SHOWN} more)" if len(found) > SHOWN else ""
    return False, f"{family}: NOTICE {len(found)} finding{'s' if len(found) != 1 else ''}: {shown}{more}"


def touches_kernel(repo, base):
    """(run portability?, why) for the change base..HEAD."""
    if base is None:
        return False, "no base given"
    r = git(repo, "rev-parse", "--verify", "-q", base + "^{commit}")
    if r.returncode or not r.stdout.strip():
        return True, f"the base {base} does not resolve: run"
    b = r.stdout.strip()
    d = git(repo, "diff", "--name-only", f"{b}..HEAD")
    if d.returncode:
        return True, f"the change since {b[:12]} cannot be read: run"
    hits = [f for f in d.stdout.splitlines() if f.startswith(PORTABILITY_PATHS)]
    if hits:
        return True, f"{len(hits)} kernel role, skill, hook or .rulesync path(s) changed since {b[:12]}"
    return False, f"no change under template/governance/kernel/{{roles,skills,hooks}}/ or .rulesync/ since {b[:12]}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repo")
    ap.add_argument("base", nargs="?")
    ap.add_argument("--timeout", type=float, default=50.0, help="each check's bound in seconds (default 50)")
    a = ap.parse_args(argv)
    start = time.monotonic()
    repo = Path(a.repo).resolve()
    if not repo.is_dir():
        raise CannotRun(f"no folder {repo}")
    top = git(repo, "rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.strip()).resolve() != repo:
        raise CannotRun(f"{repo} is not the top of a git work tree")
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if not head:
        raise CannotRun(f"{repo} has no HEAD commit")
    with_port, port_why = touches_kernel(repo, a.base)
    families = plan(repo, with_port)
    bound = a.timeout
    jobs = [(fam, cid, cmd) for fam, checks in families for cid, cmd in checks]
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = [pool.submit(run_one, repo, cmd, bound) for _, _, cmd in jobs]
        answers = [f.result() for f in futures]
    by_family = {}
    for (fam, cid, _), (rc, out, err) in zip(jobs, answers):
        by_family.setdefault(fam, []).append(judge(cid, rc, out, err, bound))
    notices, n = [], 0
    for fam, _ in families:
        ok, line = family_line(fam, by_family[fam])
        n += 1
        if not ok:
            notices.append(fam)
        if fam == "portability":
            line += f" [{port_why}]"
        print(line, flush=True)
    if not with_port:
        print(f"portability: skipped ({port_why})", flush=True)
    dirty = [l for l in git(repo, "status", "--porcelain", "--untracked-files=no").stdout.splitlines() if l]
    took = f"{time.monotonic() - start:.1f} s"
    at = f"structural pass at {head[:12]}" + (f" (the work tree differs from it at {len(dirty)} tracked path(s): "
                                              f"the working files were read)" if dirty else "")
    if notices:
        print(f"{at}: NOTICE in {', '.join(notices)} ({n - len(notices)} of {n} families ok), {took}; a notice, "
              f"not a refusal", flush=True)
    else:
        print(f"{at}: all {n} families ok, {took}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CannotRun as e:
        print(f"structural pass could not run: {e}", flush=True)
        sys.exit(2)
