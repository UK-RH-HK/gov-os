"""The build-phase close (owner, DEC-953 items 1 and 5): a ticket closes on the audit's 10 practices, nothing more.

    python3 close_build.py <W2 id> [<W2 id> ...] [--dry]

One W2 id or several (a batch on the same head): always the scoped set (DEC-968): each ticket's own suite and every
suite its selection says its change can reach, core changes included; a batch runs the union. The full suite runs
only in the nightly. Steps, stopping at the first failure:
  1. a clean clone of w2/integrate's head (the merged code) under ~/gov-os-runs/W2-00/close/<name>-<stamp>/;
  2. the clone's stores rebuilt, under the rebuild lock;
  3. the one selection tool (select_tests.py, DEC-953 item 4, DEC-968) on each merge's own change;
  4. the selected tests in the close's form, once the gate has room (DEC-961, DEC-962): one parallel run, then the
     selected serial-only cases; every failing case re-run alone once (a pass alone is a flaky candidate, named);
     each red alone traced against the known state on a second clone (DEC-988, DEC-989: the last nightly with a
     verdict until a green one after ACT 1, then the last green one; --base overrides; never code made by undoing
     merges), with and without interleaved, 3 rounds (6 if mixed): cleared only if red there too with the same failure
     (named in the record and in unowned.txt, dealt with at once by the CTO); otherwise the close is refused (a batch:
     the whole batch, since no merge is undone to find a culprit);
  5. per ticket: a FULL ticket needs a passing independent review record in docs/probes/<id>/ (no staleness check);
     gitleaks on the merge's own change (not run when governance/project/secrets.yaml says scan: off, DEC-1045,
     and named in the record; a value other than on or off refuses the close before the clone);
  6. per ticket: the close record governance/project/orchestration/closes/<W2>-<id>.md and `tk close <id>`; one
     commit each with Task: <id>, Implements: DEC-953, Role: orchestrator.
Logs: .gov-runtime/scratch/orchestrator/log/close-build/<name>-<stamp>/. Exit 0 closed; 5 closed but for the culprits sent back (DEC-979 item 3); 3 tests red; 4 another step.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from secrets_switch import OFF_LINE, REL as SWITCH_REL, SwitchError, scan_on  # noqa: E402  (DEC-1045)

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
RUNS = Path("/home/usain/gov-os-runs/W2-00/close")
VERIFY_LOCK = "/tmp/gov-os-verify.lock"
REBUILD_LOCK = "/tmp/gov-os-rebuild.lock"
REBUILD_SLOT = ORCH / "tools/rebuild_slot.sh"  # DEC-1001 (d): a heavy-job slot, a lock of the tree's own


SEEDER = ORCH / "tools/seed_store.py"  # DEC-1032 (iv): no cold rebuild: a new clone seeded from the integration store


def rebuild_cmd(tree):
    """The rebuild of one tree: seeded first from the integration store when it has no store (seed_store.py: the
    whole store at the same commit, else its vectors; a seed refused is named and the rebuild runs as before), in a
    heavy-job slot with its own lock (DEC-1001 (d)); the old shared lock only if the wrappers are missing."""
    if SEEDER.is_file() and REBUILD_SLOT.is_file():
        return [sys.executable, str(SEEDER), "rebuild", str(tree), "--who", f"close {Path(tree).name}"]
    if REBUILD_SLOT.is_file():
        return ["env", f"GOV_REBUILD_PYTHON={sys.executable}", "bash", str(REBUILD_SLOT), str(tree)]
    return ["flock", REBUILD_LOCK, sys.executable, "-m", "gov.cli.main", "rebuild", "--json"]
WANTS_LOCK = "/tmp/gov-os-close-wants-lock"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"


def decisive(w_fail, wo_fail, rounds, absent):
    """Whether the traced rounds so far settle the case (no more rounds needed)."""
    return absent is not None or (w_fail == rounds and wo_fail == 0) or bool(wo_fail and w_fail <= wo_fail)


def attribute(w_fail, wo_fail, rounds, absent):
    """DEC-968's verdict on one traced red: "flaky" (green with the change in every round), "owned" (the change's:
    it cannot run without the change, or is green without it in every round, or is red with it in at least half the
    rounds more than without it) or "unowned" (not the change's; investigated at once)."""
    if absent is not None:
        return "owned"
    if w_fail == 0:
        return "flaky"
    return "owned" if wo_fail == 0 or 2 * (w_fail - wo_fail) >= rounds else "unowned"


def trace_node(with_rc, without_rc):
    """Trace one red: with_rc() and without_rc() each run the case alone once and return its exit code, interleaved,
    3 rounds and 3 more unless decisive. Without the change only exit 1 is red; any other non-zero exit there (2, 4,
    5: the case cannot run without the change, e.g. a test the change added) ends the trace as the change's.
    Returns (verdict, {"rounds", "red_with", "red_without", "without_exit"})."""
    w_fail = wo_fail = rounds = 0
    absent = None
    for batch in (3, 3):
        for _ in range(batch):
            w_fail += with_rc() != 0
            rc = without_rc()
            if rc not in (0, 1):
                absent = rc
                break
            wo_fail += rc == 1
            rounds += 1
        if decisive(w_fail, wo_fail, rounds, absent):
            break
    return attribute(w_fail, wo_fail, rounds, absent), {"rounds": rounds, "red_with": w_fail,
                                                        "red_without": wo_fail, "without_exit": absent}


def explained_without(run_once, rounds=3):
    """One candidate's verdict on a red the batch caused, with that ticket's merges taken out: run_once() runs the
    case alone once and returns its exit code. "yes": green (0) in every round. "no": red (1) in a round, or any
    other exit (a collection error, a crash, a signal): blame needs proof (DEC-979 item 3; reviews of 2026-10-31).
    A case that cannot even be collected without the ticket is "absent", decided by the caller before this."""
    for _ in range(rounds):
        rc = run_once()
        if rc != 0:
            return "no"
    return "yes"


def red_alone(run_once, rounds=3):
    """Whether a case fails (exit 1, a real failure) in every round: the proof that a ticket alone causes it."""
    return all(run_once() == 1 for _ in range(rounds))


def assign_culprits(reds, candidates, prepare, explains, confirm):
    """DEC-979 item 3. Every candidate is tried: prepare(candidate) makes a tree without that ticket's merges (False
    when it cannot: its merge holds another ticket's commits, a revert or a rebuild failed); explains(red) answers
    "yes" (green without it), "no", or "absent" (the case cannot be collected without it: the ticket added it).
    "absent" is blamed only if confirm(red, candidate) proves the red with that ticket alone (every other candidate's
    merges taken out); else the red stays unexplained. Returns ({red: [candidates]}, [unexplained reds], [skipped
    candidates]). The caller refuses the batch on any unexplained red or any skipped candidate (fail closed)."""
    culprit, absent, skipped = {red: [] for red in reds}, [], []
    for cand in candidates:
        if not prepare(cand):
            skipped.append(cand)
            continue
        for red in reds:
            v = explains(red)
            if v == "yes":
                culprit[red].append(cand)
            elif v == "absent":
                absent.append((red, cand))
    for red, cand in absent:
        if confirm(red, cand):  # unproven: not blamed; the red stays with any candidate proven "yes", else unexplained
            culprit[red].append(cand)
    unexplained = [r for r in reds if not culprit[r]]
    return {r: c for r, c in culprit.items() if c}, unexplained, skipped


def merge_is_own(git_fn, merge, ticket):
    """Whether a ticket's merge commit brings only that ticket's own commits (every non-merge commit in m^1..m^2
    carries `Task: <ticket>`), so that reverting it takes out that ticket's change and nothing of another's.
    git_fn(*args) runs git and returns its stdout."""
    commits = git_fn("rev-list", "--no-merges", f"{merge}^1..{merge}^2").split()
    if not commits:
        return False
    for c in commits:
        tasks = git_fn("log", "-1", "--format=%(trailers:key=Task,valueonly)", c).split()
        if ticket not in tasks:
            return False
    return True


def failure_types(output, node):
    """The exception types pytest names for `node` in its short summary (`FAILED <node> - <Type>: ...`,
    `ERROR <node> - <Type>...`), as a sorted list; empty when none is named."""
    found = set()
    for line in output.splitlines():
        line = line.strip()
        for word in ("FAILED ", "ERROR "):
            if line.startswith(word) and node in line and " - " in line:
                msg = line.split(" - ", 1)[1]
                if msg.lstrip().startswith("assert"):  # a bare assert carries no type (review of 2026-11-01)
                    found.add("AssertionError")
                    continue
                found.add(msg.split(":", 1)[0].split("(", 1)[0].strip())
    return sorted(found)


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git_retry(args, root=None, tries=3, wait=None):
    """A git command in the main tree, tried again (up to `tries` in all, `wait` s apart) while another process holds
    the index lock: land.py and close_build.py may commit records at the same moment (DEC-1014 item 1). Returns the
    last result; never raises on a held lock."""
    wait = float(os.environ.get("GIT_RETRY_WAIT", "2")) if wait is None else wait
    r = None
    for n in range(tries):
        r = sh(["git", "-C", str(root or ROOT), *args])
        if r.returncode == 0 or "index.lock" not in (r.stderr + r.stdout) or n == tries - 1:
            return r
        time.sleep(wait)
    return r


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
                if not case.get("classname") and not case.get("file"):
                    # a collection error: pytest's JUnit names the module (dotted) in `name`; re-run the file itself
                    out.append(case.get("name", "").replace(".", "/") + ".py")
                    continue
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


SCAN = True  # DEC-1045: the repository's switch, read at the start of main() (secrets_switch.py)


def change_scan(diff, merges):
    """gitleaks on the merges' own change, written to ``diff`` and removed: "clean" or "LEAKS"; with the switch off,
    no gitleaks call and the switch's line (DEC-1045)."""
    if not SCAN:
        return OFF_LINE
    diff.write_text("\n".join(git("diff", m + "^1", m) for m in merges))
    gl = sh(["gitleaks", "detect", "--no-git", "--source", str(diff), "--no-banner", "--redact"])
    diff.unlink()
    return "clean" if gl.returncode == 0 else "LEAKS"


def gitleaks_line(state):
    """The close record's gitleaks line: the scan's result, or the switch named."""
    return f"- {state}: the merge's change was not scanned" if state == OFF_LINE else \
        f"- gitleaks on the merge's change: {state}"


def main():
    os.environ["GOV_HEAVY_PRIORITY"] = "1"  # DEC-1011: a close takes the next free heavy-job slot before any lead's step
    ap = argparse.ArgumentParser()
    ap.add_argument("w2", nargs="+")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--dry", action="store_true", help="run the tests, write nothing in the repository")
    ap.add_argument("--reuse", help="an earlier close's log folder: its clone, selection and test results are re-used, "
                                    "and only the attribution of its failing tests is done again (the owner, 2026-11-01)")
    ap.add_argument("--base", help="the baseline to trace against: a known state (the last nightly's head), never "
                                   "code made by undoing merges (the owner, 2026-11-01)")
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
    rdir = Path(a.reuse) if a.reuse else None
    prev = json.loads((rdir / "run.json").read_text()) if rdir else None
    if rdir:
        for f in ("parallel.xml", "serial.xml", "parallel.txt", "serial.txt"):
            if (rdir / f).exists():
                shutil.copy(rdir / f, log / f)
        run["reused"] = str(rdir)

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

    global SCAN
    try:  # DEC-1045: read before any clone or run, so a switch that cannot be read refuses at once (fails closed)
        SCAN = scan_on(ROOT)
    except SwitchError as e:
        stop(4, f"the secrets-scan switch: {e}")
    run["gitleaks"] = "on" if SCAN else OFF_LINE
    if not SCAN:
        note(f"{OFF_LINE}: no merge's change is scanned ({ROOT / SWITCH_REL})")
    if sh(["bash", str(ORCH / "tools/disk_gate.sh")]).returncode:
        stop(4, "disk gate shut")
    t0 = time.time()
    clone = RUNS / (rdir.name if rdir else f"{name}-{stamp}")
    clone.parent.mkdir(parents=True, exist_ok=True)
    if rdir:
        if not (clone / ".git").exists():
            stop(4, f"the re-used run's clone {clone} is gone")
        note(f"re-using {rdir.name}: its clone, selection and test results (only the attribution is done again)")
    elif sh(["git", "clone", "-q", "--no-hardlinks", "--branch", "w2/integrate", str(ROOT), str(clone)]).returncode:
        stop(4, "clone failed")
    # A pinned head (CLOSE-HEAD, one commit id): until the live-guard tests are revised after ACT 1, closes test on
    # the head before ACT 1, which holds every merge they close (DEC-955); the merges are checked against it below.
    pin = ORCH / "CLOSE-HEAD"
    if pin.is_file() and not rdir:
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
    if rdir:
        run["rebuild_s"] = prev.get("rebuild_s", 0)
    else:
        rb = sh(rebuild_cmd(clone), cwd=clone, env=env)
        (log / "rebuild.txt").write_text(rb.stdout[-4000:] + rb.stderr[-4000:])
        if rb.returncode:
            stop(4, "clone rebuild failed")
        run["rebuild_s"] = int(time.time() - r0)
        note(f"clone rebuilt in {run['rebuild_s']} s")

    for i in items:
        if rdir:
            i["sel"] = json.loads((rdir / f"select-{i['w2']}.json").read_text())
            shutil.copy(rdir / f"select-{i['w2']}.json", log / f"select-{i['w2']}.json")
            continue
        sel = sh([sys.executable, str(ORCH / "tools/select_tests.py"), str(clone), i["w2"], i["ticket"],
                  "--merge", ",".join(i["merges"])], cwd=clone, env=env)
        if sel.returncode:
            (log / f"select-{i['w2']}.err").write_text(sel.stderr)
            stop(4, f"selection failed for {i['w2']}")
        (log / f"select-{i['w2']}.json").write_text(sel.stdout)
        i["sel"] = json.loads(sel.stdout)
        note(f"{i['w2']} selection: {i['sel']['scope']} {json.dumps(i['sel']['why_full'])[:200]}; "
             f"{len(i['sel']['selected'])} targets; governance left out {len(i['sel']['governance_left_out'])}")
    # DEC-968: the full suite runs only in the nightly; a close (one ticket or a batch) runs the scoped set: each
    # ticket's own suite and every suite its selection says its change can reach. A batch runs the union.
    if a.full:
        stop(4, "no full run outside the nightly (DEC-968)")
    scope, why = "scoped", []
    s = items[0]["sel"]
    targets = list(dict.fromkeys(x["target"] for i in items for x in i["sel"]["selected"]))
    if len(items) == 1:
        opts, run_args = s["pytest_options"], ["tests"]
    else:  # the union, named; deselects are left out (a batch runs a few more cases rather than fewer)
        opts, run_args = [], targets
    run["scope"], run["why_full"] = scope, why
    run["selected"] = targets
    run["core_changed"] = sorted({p for i in items for p in i["sel"].get("core_changed", [])})
    run["unplaced"] = sorted({p for i in items for p in i["sel"].get("unplaced", [])})
    note(f"run scope scoped: {len(targets)} targets; core changed {len(run['core_changed'])}, unplaced "
         f"{len(run['unplaced'])}")

    sys.path.insert(0, str(clone / "src"))
    from gov.close import select as gsel  # noqa: E402
    from gov.close.pytest_plugin.gov_close_serial_only import entries  # noqa: E402
    from gov.close.serial import phase  # noqa: E402
    serial = phase(clone, entries(clone))  # the nightly's entries are left to the nightly (W2-57's route)
    if len(items) == 1:
        serial = [e for e in serial if gsel.runs(e, s["ignore"], s["deselect"])]
    else:
        serial = [e for e in serial if any(e == t.rstrip("/") or e.startswith(t.rstrip("/") + "/")
                                           or e.startswith(t.rstrip("/") + "::") or e.startswith(t) for t in targets)]
    penv = dict(env, PYTHONPATH=f"{clone}/src:{clone}/src/gov/close/pytest_plugin",
                GOV_CLOSE_SERIAL_ONLY_OF=str(clone), PATH=NODE + ":" + env.get("PATH", ""))
    common = ["-q", "-p", "no:cacheprovider", "--no-header", "-p", "gov_close_serial_only",
              "-o", "tmp_path_retention_policy=failed", "-rs"]
    tmp = Path(f"/tmp/gov-os-close-{stamp}")
    tmp.mkdir(exist_ok=True)
    penv["TMPDIR"] = str(tmp)
    # DEC-962: no shared test lock and no "closes first"; the run waits only for the gate's room (DEC-961).
    # DEC-961: the full run gets its place by the gate's capacity (room for its measured peak), like a lead.
    # DEC-968: a close runs the scoped set, never the full suite, so it does not wait for a full run's room (that wait
    # is the nightly's alone); it waited 6.5 hours on 2026-10-31 when it did (the orchestrator's slip).
    run["gate_wait_s"] = 0
    t1 = time.time()
    if rdir:  # the earlier run's results stand; nothing is run again
        run["parallel"], run["serial"] = prev["parallel"], prev["serial"]
        t2 = t3 = t1
    if not rdir:
        # DEC-979 D1: the close's parallel run takes a heavy-job slot like a lead's (its -n auto capped by the slot).
        par = sh(["bash", str(ORCH / "tools/heavy_slot.sh"), sys.executable, "-m", "pytest", *run_args, "-n", "auto", *common, *opts,
                  f"--junitxml={log}/parallel.xml"], cwd=clone, env=penv)
        (log / "parallel.txt").write_text(par.stdout[-20000:] + par.stderr[-5000:])
        t2 = time.time()
        ser_rc = 0
        if serial:
            senv = dict(penv, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial))
            ser = sh([sys.executable, "-m", "pytest", *serial, *common,
                      f"--junitxml={log}/serial.xml"], cwd=clone, env=senv)
            (log / "serial.txt").write_text(ser.stdout[-20000:] + ser.stderr[-5000:])
            ser_rc = ser.returncode
        t3 = time.time()
        run["parallel"] ={"exit": par.returncode, "s": int(t2 - t1), **totals(log / "parallel.xml")}
        run["serial"] = {"exit": ser_rc, "s": int(t3 - t2), "entries": len(serial), **totals(log / "serial.xml")}
        note(f"parallel exit {par.returncode} in {int(t2 - t1)} s {run['parallel']}; serial exit {ser_rc} in "
             f"{int(t3 - t2)} s {run['serial']}")
        if par.returncode not in (0, 1) or ser_rc not in (0, 1, 5):
            stop(3, f"a test run did not complete (parallel {par.returncode}, serial {ser_rc})")

    def alone_rc(node, where, env_):
        """One case alone, in the run's own env (penv: the node PATH, the plugin path); a timeout counts as red (1)."""
        try:
            return sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", node],
                      cwd=where, env=env_, timeout=1800).returncode
        except subprocess.TimeoutExpired:
            return 1

    reds, flaky = [], []
    for node in failing([log / "parallel.xml", log / "serial.xml"]):
        rc = alone_rc(node, clone, penv)
        (flaky if rc == 0 else reds).append(node)
        note(("passes alone (flaky candidate): " if rc == 0 else "red alone: ") + node)
    run["tests_s"] = int(t3 - t1)
    unowned = []
    if reds:
        # DEC-988, DEC-989: the only baseline is a known state, the last nightly with a verdict until a green one after
        # ACT 1 (then the last green one; land.baseline() reads it), never code made by undoing merges.
        wo = RUNS / f"{name}-{stamp}-without"
        if sh(["git", "clone", "-q", "--no-hardlinks", str(clone), str(wo)]).returncode:
            stop(3, f"{len(reds)} test(s) red alone; the clone to trace them failed")
        if a.base:
            b, why_b = git("rev-parse", a.base), "given with --base"
        else:
            sys.path.insert(0, str(ORCH / "tools"))
            from land import baseline  # noqa: E402
            b, why_b = baseline()
            b = git("rev-parse", b)
        if not b or sh(["git", "-C", str(wo), "checkout", "-q", "--force", "--detach", b]).returncode:
            stop(3, f"{len(reds)} test(s) red alone; the baseline {b or a.base} cannot be checked out (refused)")
        run["trace_base"] = f"the known state {b[:12]} ({why_b}; DEC-989)"
        note(f"trace: against the known state {b[:12]} ({why_b})")
        wenv = dict(env, PYTHONPATH=str(wo / "src"))
        rb2 = sh(rebuild_cmd(wo), cwd=wo, env=wenv)
        wpenv = dict(penv, PYTHONPATH=f"{wo}/src:{wo}/src/gov/close/pytest_plugin", GOV_CLOSE_SERIAL_ONLY_OF=str(wo))
        if rb2.returncode:
            stop(3, f"{len(reds)} test(s) red alone; the clone without the change did not rebuild (refused)")
        # One run each way misjudged load-sensitive cases (2026-10-31 15:19: 11 hook-latency cases blamed on W2-106;
        # traced 3 rounds each way, they failed with and without it). So each red runs with and without the change,
        # interleaved, 3 rounds, then 3 more unless the first 3 are decisive. Caused by the change (refused, fail
        # closed): green without it in every round, or red with it in at least half the rounds more than without it
        # (the change makes a load-sensitive case fail much more often). Otherwise not this change's: named, and
        # investigated at once (DEC-968). Without the change, only a test failure (exit 1, or a timeout) counts as red;
        # a case that cannot run there (not found, collection error, no tests: exit 2, 4, 5; e.g. a test the change
        # added) is the change's (fail closed; review of 2026-10-31).
        owned, trace = [], {}
        for node in reds:
            verdict, c = trace_node(lambda: alone_rc(node, clone, penv), lambda: alone_rc(node, wo, wpenv))
            trace[node] = c
            w_fail, wo_fail, rounds = c["red_with"], c["red_without"], c["rounds"]
            if c["without_exit"] is not None:
                owned.append(node)
                note(f"cannot run without the change (exit {c['without_exit']}): the change's: {node}")
                continue
            if verdict == "flaky":
                flaky.append(node)
                note(f"green with the change in all {rounds} traced rounds (flaky candidate): {node}")
                continue
            mine = verdict == "owned"
            if not mine:
                # Red both ways: cleared only if it fails the same way (the same exception type) with and without
                # the change; a different failure of the same test id is the change's (review of 2026-11-01).
                def one(where, env_):
                    try:
                        r = sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-rfE",
                                node], cwd=where, env=dict(env_, COLUMNS="2000"), timeout=1800)  # the summary line uncut
                        return failure_types(r.stdout + r.stderr, node)
                    except subprocess.TimeoutExpired:
                        return ["Timeout"]
                tw, two = one(clone, penv), one(wo, wpenv)
                c["failure_with"], c["failure_without"] = tw, two
                if not tw or not two or tw != two:  # an unknown failure (a timeout, no summary) never matches
                    mine = True
                    note(f"red at the baseline too but not the same failure ({tw} here, {two} there): the "
                         f"change's: {node}")
            (owned if mine else unowned).append(node)
            note((f"caused by the change (red {w_fail}/{rounds} with, {wo_fail}/{rounds} without): " if mine else
                  f"red without the change too ({wo_fail}/{rounds}; with {w_fail}/{rounds}); not this change's "
                  "(red at the baseline, the same failure), to investigate now: ") + node)
        run["trace"] = trace
        shutil.rmtree(wo, ignore_errors=True)
        (log / "unowned.txt").write_text("".join(n + "\n" for n in unowned))
        run["flaky_candidates"], run["unowned_reds"] = flaky, unowned
        if owned:
            run["reds"] = owned
            if len(items) == 1:
                stop(3, f"{len(owned)} test(s) red alone, caused by this change")
            # DEC-988: no merge is undone, so a batch red the baseline does not clear cannot be traced to one ticket
            # here: the batch is refused (fail closed) and the CTO investigates at once (DEC-968). Tickets merge one
            # by one through the merge queue (W2-97), which isolates a culprit before anything lands.
            stop(3, f"{len(owned)} test(s) red alone that the baseline does not clear, in a batch of {len(items)}; "
                    "refused: no merge is undone to find the culprit (DEC-988); investigate at once")
    run["reds"], run["flaky_candidates"], run["unowned_reds"] = [], flaky, unowned

    for i in items:
        if i["profile"] == "FULL":
            probes = sorted(glob.glob(str(ROOT / "docs/probes" / i["ticket"] / "*.md")))
            sys.path.insert(0, str(ORCH / "tools"))
            from verdict import ready  # DEC-1010: READY computed from a structured verdict where the record has one

            def passes(p):
                text = open(p).read()
                ok, _ = ready(text)
                return ok if ok is not None else bool(re.search(r"^(judgement|verdict|result|status):\s*(PASS|pass)",
                                                                   text, re.M))
            passing = [p for p in probes if passes(p)]
            i["review"] = [os.path.relpath(p, ROOT) for p in passing]
            if not passing:
                stop(4, f"{i['w2']}: FULL ticket without a passing independent review record")
        else:
            i["review"] = "not required (" + (i["profile"] or "no profile") + ")"
        i["gitleaks"] = change_scan(log / f"change-{i['w2']}.diff", i["merges"])
        if i["gitleaks"] == "LEAKS":
            stop(4, f"{i['w2']}: gitleaks found a leak in the merge's change")
    run["wall_s"] = int(time.time() - t0)
    run["verdict"] = "CLOSED (build-phase close, DEC-953)"
    run["items"] = [{k: v for k, v in i.items() if k != "sel"} for i in items]
    (log / "run.json").write_text(json.dumps(run, indent=1))
    shutil.rmtree(clone, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if a.dry:
        note(f"DRY: would close {', '.join(i['ticket'] for i in items)}; wall {run['wall_s']} s")
        sys.exit(5 if run.get("sent_back") else 0)

    for i in items:
        out = ROOT / "governance/project/orchestration/closes" / f"{i['w2']}-{i['ticket']}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        sel = i["sel"]
        lines = [f"# {i['w2']} ({i['ticket']}) closed: build-phase close (DEC-953)", "",
                 f"- Merges: {i['merge']}; tested on w2/integrate head {run['head']}; profile {i['profile']}",
                 f"- Its own selection: {sel['scope']}" + (f" (why full: {json.dumps(sel['why_full'])[:400]})"
                                                           if sel["scope"] == "full" else ""),
                 f"- Run: {scope} ({len(run['selected'])} targets)" + (f", batch of {', '.join(run['tickets'])}" if len(run['tickets']) > 1 else ""),
                 f"- Selected: {', '.join(run['selected'][:40])}" + (" ..." if len(run['selected']) > 40 else ""),
                 f"- Parallel: {run['parallel']}", f"- Serial: {run['serial']}",
                 f"- Reds caused by the change: none; flaky candidates: {', '.join(flaky) or 'none'}",
                 *([f"- Sent back from this batch (DEC-979 item 3): {', '.join(run['sent_back'])}, which caused "
                    f"{', '.join(n for n in run['culprits'])} (green without it, 3 rounds); this ticket closes on "
                    f"the same run"] if run.get("sent_back") else []),
                 *([f"- Traced against: {run['trace_base']}"] if run.get("trace_base") else []),
                 f"- Red without the change too, not this change's, investigated by the CTO at once (DEC-968): "
                 f"{', '.join(unowned) or 'none'}",
                 f"- Core changed (scoped, not full, DEC-968): {', '.join(run['core_changed']) or 'none'}; "
                 f"unplaced: {', '.join(run['unplaced']) or 'none'}",
                 f"- Review: {i['review']}", gitleaks_line(i["gitleaks"]),
                 f"- Times: rebuild {run['rebuild_s']} s, tests {run['tests_s']} s, wall {run['wall_s']} s",
                 f"- Closed: {time.strftime('%F %T %Z')}, by the orchestrator under DEC-953 items 1 and 5", ""]
        out.write_text("\n".join(lines))
        tk = sh(["tk", "close", i["ticket"]], cwd=ROOT)
        note(f"tk close {i['ticket']}: " + (tk.stdout + tk.stderr).strip()[:200])
        paths = [os.path.relpath(out, ROOT), f".tickets/{i['ticket']}.md"]
        git_retry(["add", "--", *paths])
        cm = git_retry(["commit", "-q", "-m",
                 f"{i['w2']} ({i['ticket']}): closed on the 10 practices (DEC-953)",
                 "--trailer", f"Task: {i['ticket']}", "--trailer", "Implements: DEC-953", "--trailer",
                 "Role: orchestrator", "--trailer", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                 "--", *paths])
        note("commit: " + (git("log", "--oneline", "-1") if cm.returncode == 0 else "FAILED " + cm.stderr[:300]))
        note(f"CLOSED {i['w2']}")
    note(f"done; wall {run['wall_s']} s")
    if run.get("sent_back"):
        sys.exit(5)  # a partial close: the culprits went back (DEC-979 item 3)


if __name__ == "__main__":
    main()
