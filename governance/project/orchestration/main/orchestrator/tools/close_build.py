"""The build-phase close (owner, DEC-953 items 1 and 5): a ticket closes on the audit's 10 practices, nothing more.

    python3 close_build.py <W2 id> [<W2 id> ...] [--full] [--dry]

One W2 id: its own selection (scoped, or full when shared core changed). Several: one batch on the same head, one
full run for all of them (any red refuses the batch). Steps, stopping at the first failure:
  1. a clean clone of w2/integrate's head (the merged code) under ~/gov-os-runs/W2-00/close/<name>-<stamp>/;
  2. the clone's stores rebuilt (tests that read the repository's own state need them), under the rebuild lock;
  3. the one selection tool (select_tests.py, DEC-953 item 4) on each merge's own change;
  4. the selected tests in the close's form, under the verification lock: one parallel run, then the selected
     serial-only cases; every failing case re-run alone once (a pass alone is a flaky candidate, named);
  5. per ticket: a FULL ticket needs a passing independent review record in docs/probes/<id>/ (no staleness check);
     gitleaks on the merge's own change;
  6. per ticket: the close record governance/project/orchestration/closes/<W2>-<id>.md and `tk close <id>`; one
     commit each with Task: <id>, Implements: DEC-953, Role: orchestrator.
Logs: .gov-runtime/scratch/orchestrator/log/close-build/<name>-<stamp>/. Exit 0 closed; 3 tests red; 4 another step.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
RUNS = Path("/home/usain/gov-os-runs/W2-00/close")
VERIFY_LOCK = "/tmp/gov-os-verify.lock"
REBUILD_LOCK = "/tmp/gov-os-rebuild.lock"
WANTS_LOCK = "/tmp/gov-os-close-wants-lock"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(*args, cwd=ROOT):
    return sh(["git", "-C", str(cwd), *args]).stdout.strip()


def ticket_of(w2):
    for path in glob.glob(str(ROOT / ".tickets/*.md")):
        text = open(path, encoding="utf-8").read()
        head = text.split("\n---", 1)[0]
        if re.search(r"^wbs_id: " + re.escape(w2) + r"$", head, re.M):
            prof = re.search(r"^profile: (\S+)$", text, re.M)
            return os.path.basename(path)[:-3], (prof.group(1) if prof else "")
    sys.exit(f"no ticket for {w2}")


def merge_of(w2):
    """All of the ticket's merges into w2/integrate, newest first, comma-joined (select_tests.py's --merge)."""
    found = []
    for line in git("log", "--merges", "--first-parent", "w2/integrate", "--format=%H %s", "-600").splitlines():
        sha, subj = line.split(" ", 1)
        if re.search(r"Merge w2/" + re.escape(w2) + r"\b", subj):
            found.append(sha)
    return ",".join(found) or None


def failing(xml_paths):
    out = []
    for p in xml_paths:
        if not Path(p).is_file():
            continue
        for case in ET.parse(p).iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                file = case.get("file") or (case.get("classname", "").replace(".", "/") + ".py")
                out.append(f"{file}::{case.get('name')}")
    return list(dict.fromkeys(out))


def totals(xml_path):
    t = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    if Path(xml_path).is_file():
        r = ET.parse(xml_path).getroot()
        for s in ([r] if r.tag == "testsuite" else r.iter("testsuite")):
            for k in t:
                t[k] += int(s.get(k, 0))
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("w2", nargs="+")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--dry", action="store_true", help="run the tests, write nothing in the repository")
    a = ap.parse_args()
    items = []
    for w2 in a.w2:
        tid, profile = ticket_of(w2)
        merge = merge_of(w2)
        if not merge:
            sys.exit(f"no merge of w2/{w2} on w2/integrate")
        items.append({"w2": w2, "ticket": tid, "profile": profile, "merge": merge})
    name = "+".join(a.w2)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = ORCH / "log/close-build" / f"{name}-{stamp}"
    log.mkdir(parents=True)
    run = {"tickets": [i["w2"] for i in items], "started": time.strftime("%F %T")}

    def note(msg):
        line = time.strftime("%F %T ") + msg
        print(line, flush=True)
        with open(log / "close.txt", "a") as f:
            f.write(line + "\n")

    def stop(code, why):
        run["verdict"] = "REFUSED: " + why
        (log / "run.json").write_text(json.dumps(run, indent=1))
        note("CLOSE REFUSED: " + why)
        sys.exit(code)

    if sh(["bash", str(ORCH / "tools/disk_gate.sh")]).returncode:
        stop(4, "disk gate shut")
    t0 = time.time()
    clone = RUNS / f"{name}-{stamp}"
    clone.parent.mkdir(parents=True, exist_ok=True)
    if sh(["git", "clone", "-q", "--no-hardlinks", "--branch", "w2/integrate", str(ROOT), str(clone)]).returncode:
        stop(4, "clone failed")
    # A pinned head (CLOSE-HEAD, one commit id): until the live-guard tests are revised after ACT 1, closes test on
    # the head before ACT 1, which holds every merge they close (DEC-955); the merges are checked against it below.
    pin = ORCH / "CLOSE-HEAD"
    if pin.is_file():
        want = pin.read_text().strip()
        if sh(["git", "-C", str(clone), "checkout", "-q", want]).returncode:
            stop(4, f"the pinned head {want[:12]} cannot be checked out")
        note(f"head pinned by CLOSE-HEAD to {want[:12]}")
    head = git("rev-parse", "HEAD", cwd=clone)
    run["head"] = head[:12]
    for i in items:
        i["merges"] = i["merge"].split(",")
        for m in i["merges"]:
            if sh(["git", "-C", str(clone), "merge-base", "--is-ancestor", m, "HEAD"]).returncode:
                stop(4, f"{i['w2']}'s merge {m[:12]} is not in w2/integrate's head")
        i["merge"] = ",".join(m[:12] for m in i["merges"])
        note(f"{i['w2']} ({i['ticket']}, {i['profile']}) merges {i['merge']} on head {head[:12]}")

    env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
    env["PYTHONPATH"] = str(clone / "src")
    r0 = time.time()
    rb = sh(["flock", REBUILD_LOCK, sys.executable, "-m", "gov.cli.main", "rebuild", "--json"], cwd=clone, env=env)
    (log / "rebuild.txt").write_text(rb.stdout[-4000:] + rb.stderr[-4000:])
    if rb.returncode:
        stop(4, "clone rebuild failed")
    run["rebuild_s"] = int(time.time() - r0)
    note(f"clone rebuilt in {run['rebuild_s']} s")

    for i in items:
        sel = sh([sys.executable, str(ORCH / "tools/select_tests.py"), str(clone), i["w2"], i["ticket"],
                  "--merge", ",".join(i["merges"])], cwd=clone, env=env)
        if sel.returncode:
            (log / f"select-{i['w2']}.err").write_text(sel.stderr)
            stop(4, f"selection failed for {i['w2']}")
        (log / f"select-{i['w2']}.json").write_text(sel.stdout)
        i["sel"] = json.loads(sel.stdout)
        note(f"{i['w2']} selection: {i['sel']['scope']} {json.dumps(i['sel']['why_full'])[:200]}; "
             f"{len(i['sel']['selected'])} targets; governance left out {len(i['sel']['governance_left_out'])}")
    if a.full:
        scope, why = "full", [{"reason": "FULL_ASKED"}]
    elif len(items) > 1:
        scope, why = "full", [{"reason": "BATCH"}] + [w for i in items for w in i["sel"]["why_full"]]
    else:
        scope, why = items[0]["sel"]["scope"], items[0]["sel"]["why_full"]
    s = items[0]["sel"]
    opts = [] if scope == "full" else s["pytest_options"]
    run["scope"], run["why_full"] = scope, why
    run["selected"] = ["tests"] if scope == "full" else [x["target"] for x in s["selected"]]
    note(f"run scope {scope}")

    sys.path.insert(0, str(clone / "src"))
    from gov.close import select as gsel  # noqa: E402
    from gov.close.pytest_plugin.gov_close_serial_only import entries  # noqa: E402
    from gov.close.serial import phase  # noqa: E402
    serial = phase(clone, entries(clone))  # the nightly's entries are left to the nightly (W2-57's route)
    if scope != "full":
        serial = [e for e in serial if gsel.runs(e, s["ignore"], s["deselect"])]
    penv = dict(env, PYTHONPATH=f"{clone}/src:{clone}/src/gov/close/pytest_plugin",
                GOV_CLOSE_SERIAL_ONLY_OF=str(clone), PATH=NODE + ":" + env.get("PATH", ""))
    common = ["-q", "-p", "no:cacheprovider", "--no-header", "-p", "gov_close_serial_only",
              "-o", "tmp_path_retention_policy=failed", "-rs"]
    tmp = Path(f"/tmp/gov-os-close-{stamp}")
    tmp.mkdir(exist_ok=True)
    penv["TMPDIR"] = str(tmp)
    # DEC-954: closes take the test lock ahead of any lead's full run (leads wait in verify_lock.sh while this
    # flag names a live close)
    Path(WANTS_LOCK).write_text(str(os.getpid()))
    t1 = time.time()
    par = sh(["flock", VERIFY_LOCK, sys.executable, "-m", "pytest", "tests", "-n", "auto", *common, *opts,
              f"--junitxml={log}/parallel.xml"], cwd=clone, env=penv)
    (log / "parallel.txt").write_text(par.stdout[-20000:] + par.stderr[-5000:])
    t2 = time.time()
    ser_rc = 0
    if serial:
        senv = dict(penv, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial))
        ser = sh(["flock", VERIFY_LOCK, sys.executable, "-m", "pytest", *serial, *common,
                  f"--junitxml={log}/serial.xml"], cwd=clone, env=senv)
        (log / "serial.txt").write_text(ser.stdout[-20000:] + ser.stderr[-5000:])
        ser_rc = ser.returncode
    t3 = time.time()
    try:
        if Path(WANTS_LOCK).read_text().strip() == str(os.getpid()):
            Path(WANTS_LOCK).unlink()
    except OSError:
        pass
    run["parallel"] ={"exit": par.returncode, "s": int(t2 - t1), **totals(log / "parallel.xml")}
    run["serial"] = {"exit": ser_rc, "s": int(t3 - t2), "entries": len(serial), **totals(log / "serial.xml")}
    note(f"parallel exit {par.returncode} in {int(t2 - t1)} s {run['parallel']}; serial exit {ser_rc} in "
         f"{int(t3 - t2)} s {run['serial']}")
    if par.returncode not in (0, 1) or ser_rc not in (0, 1, 5):
        stop(3, f"a test run did not complete (parallel {par.returncode}, serial {ser_rc})")

    reds, flaky = [], []
    for node in failing([log / "parallel.xml", log / "serial.xml"]):
        alone = sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", node],
                   cwd=clone, env=dict(env, TMPDIR=str(tmp)), timeout=1800)
        (flaky if alone.returncode == 0 else reds).append(node)
        note(("passes alone (flaky candidate): " if alone.returncode == 0 else "red alone: ") + node)
    run["reds"], run["flaky_candidates"] = reds, flaky
    run["tests_s"] = int(t3 - t1)
    if reds:
        stop(3, f"{len(reds)} test(s) red alone")

    for i in items:
        if i["profile"] == "FULL":
            probes = sorted(glob.glob(str(ROOT / "docs/probes" / i["ticket"] / "*.md")))
            passing = [p for p in probes
                       if re.search(r"^(judgement|verdict|result|status):\s*(PASS|pass)", open(p).read(), re.M)]
            i["review"] = [os.path.relpath(p, ROOT) for p in passing]
            if not passing:
                stop(4, f"{i['w2']}: FULL ticket without a passing independent review record")
        else:
            i["review"] = "not required (" + (i["profile"] or "no profile") + ")"
        diff = log / f"change-{i['w2']}.diff"
        diff.write_text("\n".join(git("diff", m + "^1", m) for m in i["merges"]))
        gl = sh(["gitleaks", "detect", "--no-git", "--source", str(diff), "--no-banner", "--redact"])
        diff.unlink()
        i["gitleaks"] = "clean" if gl.returncode == 0 else "LEAKS"
        if gl.returncode:
            stop(4, f"{i['w2']}: gitleaks found a leak in the merge's change")
    run["wall_s"] = int(time.time() - t0)
    run["verdict"] = "CLOSED (build-phase close, DEC-953)"
    run["items"] = [{k: v for k, v in i.items() if k != "sel"} for i in items]
    (log / "run.json").write_text(json.dumps(run, indent=1))
    shutil.rmtree(clone, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if a.dry:
        note(f"DRY: would close {', '.join(i['ticket'] for i in items)}; wall {run['wall_s']} s")
        return

    for i in items:
        out = ROOT / "governance/project/orchestration/closes" / f"{i['w2']}-{i['ticket']}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        sel = i["sel"]
        lines = [f"# {i['w2']} ({i['ticket']}) closed: build-phase close (DEC-953)", "",
                 f"- Merges: {i['merge']}; tested on w2/integrate head {run['head']}; profile {i['profile']}",
                 f"- Its own selection: {sel['scope']}" + (f" (why full: {json.dumps(sel['why_full'])[:400]})"
                                                           if sel["scope"] == "full" else ""),
                 f"- Run: {scope}" + (f", batch of {', '.join(run['tickets'])}" if len(items) > 1 else ""),
                 f"- Selected: {', '.join(run['selected'][:40])}" + (" ..." if len(run['selected']) > 40 else ""),
                 f"- Parallel: {run['parallel']}", f"- Serial: {run['serial']}",
                 f"- Reds alone: none; flaky candidates: {', '.join(flaky) or 'none'}",
                 f"- Review: {i['review']}", f"- gitleaks on the merge's change: {i['gitleaks']}",
                 f"- Times: rebuild {run['rebuild_s']} s, tests {run['tests_s']} s, wall {run['wall_s']} s",
                 f"- Closed: {time.strftime('%F %T %Z')}, by the orchestrator under DEC-953 items 1 and 5", ""]
        out.write_text("\n".join(lines))
        tk = sh(["tk", "close", i["ticket"]], cwd=ROOT)
        note(f"tk close {i['ticket']}: " + (tk.stdout + tk.stderr).strip()[:200])
        paths = [os.path.relpath(out, ROOT), f".tickets/{i['ticket']}.md"]
        sh(["git", "-C", str(ROOT), "add", "--", *paths])
        cm = sh(["git", "-C", str(ROOT), "commit", "-q", "-m",
                 f"{i['w2']} ({i['ticket']}): closed on the 10 practices (DEC-953)",
                 "--trailer", f"Task: {i['ticket']}", "--trailer", "Implements: DEC-953", "--trailer",
                 "Role: orchestrator", "--trailer", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                 "--", *paths])
        note("commit: " + (git("log", "--oneline", "-1") if cm.returncode == 0 else "FAILED " + cm.stderr[:300]))
        note(f"CLOSED {i['w2']}")
    note(f"done; wall {run['wall_s']} s")


main()
