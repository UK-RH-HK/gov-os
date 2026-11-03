"""Merge and close in one step through W2-97's merge queue (owner, DEC-988, DEC-989).

    python3 land.py <W2>[=<commit>] [<W2>[=<commit>] ...] [--base <commit>] [--check]

For each ticket (default commit: the head of w2/<W2>, its lead's final, verified result; one merge per ticket):
  1. the close's practices that need no test run, BEFORE anything lands: a FULL ticket has a passing independent
     review record in docs/probes/<id>/ at that commit; gitleaks on the ticket's change (not
     run when governance/project/secrets.yaml says scan: off, DEC-1045, and named; a value other than on or off
     refuses); every changed YAML file parses; the disk gate is open;
  2. enqueue and approve it (the CTO approves until the three layers start);
then one queue run (merge_queue.py run, --base: the attribution baseline, DEC-989: the last nightly with a verdict
until a green one after ACT 1, then the last green one; read from log/nightly/status.txt unless given), and for every
ticket the run landed: its close record (governance/project/orchestration/closes/<W2>-<id>.md, citing the queue's
record), `tk close <id>` and one commit (Task: <id>, Implements: DEC-953, DEC-989, Role: orchestrator). No ticket
sits merged but not closed. --check: step 1 only.
Exit: the queue's (0 all landed and closed; 3 some ejected; 4 the run stopped), 2 a pre-check refused, 6 a ticket
landed but its close step failed (fix at once).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from secrets_switch import OFF_LINE, REL as SWITCH_REL, SwitchError, scan_on  # noqa: E402  (DEC-1045)

ROOT =Path(os.environ.get("LAND_ROOT", "/home/usain/Dynamic-Agentic-Engineering-OS"))  # LAND_ROOT: tests only
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
MQ = ROOT / "governance/project/orchestration/tools/merge_queue.py"
QUEUE = ORCH / "merge-queue"
STATUS = ORCH / "log/nightly/status.txt"
NIGHTLY = ORCH / "log/nightly"
JUNIT = Path("/tmp/gov-os-nightly-junit")  # the nightly's JUnit folders (nightly.sh)
WARM = Path.home() / "gov-os-runs/W2-00/merge-queue/warm"  # the queue's warm clones (DEC-1001 (b))
# DEC-1032 (iv): the integration store (the link to its ready half): the queue seeds its clones from it, re-runs the
# head without the batch in it (never rebuilt), and promotes each landed result's stores into it.
STORE = Path.home() / "gov-os-worktrees/W2-00-store"
ACT1_FIRST_NIGHT = "2026-10-31"  # ACT 1 was committed on 2026-10-30 evening; the first nightly after it is 10-31's


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


def git(*args):
    return sh(["git", "-C", str(ROOT), *args]).stdout.strip()


def baseline(status=STATUS):
    """DEC-989: the last green nightly after ACT 1; until one exists, the last nightly that ran to a verdict."""
    ran = []
    for line in Path(status).read_text().splitlines():
        m = re.match(r"(\d{4}-\d\d-\d\d) ran \| verdict: (\w+).*? head ([0-9a-f]{12})", line)
        if m:
            ran.append((m.group(1), m.group(2), m.group(3)))
    green = [r for r in ran if r[1] == "green" and r[0] >= ACT1_FIRST_NIGHT]
    pick = (green or ran or [None])[-1]
    if not pick:
        sys.exit("no nightly with a verdict in " + str(status))
    return pick[2], f"the nightly of {pick[0]} ({pick[1]})"


def base_record(head12):
    """DEC-1001 (c): the baseline nightly's own record, (its JUnit folder, its run file), for the nightly whose run file
    names this head; (None, None) when either is missing (the queue then traces the baseline as before)."""
    for run in sorted(NIGHTLY.glob("*/run.txt"), reverse=True):
        try:
            if re.search(r"^head " + re.escape(head12) + r"\b", run.read_text(encoding="utf-8"), re.M):
                junit = JUNIT / run.parent.name
                if any(junit.glob("*.xml")):
                    return junit, run
                return None, None
        except OSError:
            continue
    return None, None


def ticket_of(w2):
    for path in glob.glob(str(ROOT / ".tickets/*.md")):
        text = open(path, encoding="utf-8").read()
        if re.search(r"^wbs_id: " + re.escape(w2) + r"$", text.split("\n---", 1)[0], re.M):
            prof = re.search(r"^profile: (\S+)$", text, re.M)
            return Path(path).stem, (prof.group(1) if prof else "")
    sys.exit(f"no ticket for {w2}")


SCAN = True  # DEC-1045: the repository's switch, read once in main() (secrets_switch.py); off: no gitleaks call


def scan_change(w2, commit):
    """gitleaks on the ticket's change (True: a leak); with the switch off, no call, and False."""
    if not SCAN:
        return False
    diff = git("diff", f"w2/integrate...{commit}")
    tmp = ORCH / "log" / f"land-{w2}.diff"
    tmp.write_text(diff)
    gl = sh(["gitleaks", "detect", "--no-git", "--source", str(tmp), "--no-banner", "--redact"])
    tmp.unlink()
    return bool(gl.returncode)


def gitleaks_line():
    """The close record's gitleaks line: the scan's, or the switch named (DEC-1045)."""
    return ("- gitleaks on the change: clean (checked before it was queued)" if SCAN
            else f"- {OFF_LINE}: the change was not scanned")


def precheck(w2, tid, profile, commit):
    """The practices that need no test run; returns a list of refusals (empty: fine) and the review it found."""
    bad, review = [], "not required (" + (profile or "no profile") + ")"
    if profile == "FULL":
        files = [f for f in git("ls-tree", "-r", "--name-only", commit, f"docs/probes/{tid}/").splitlines()
                 if f.endswith(".md")]
        from verdict import ready  # DEC-1010: READY computed from a structured verdict where the record has one

        def passes(f):
            text = git("show", f"{commit}:{f}")
            ok, _ = ready(text)
            return ok if ok is not None else bool(re.search(r"^(judgement|verdict|result|status):\s*(PASS|pass)",
                                                               text, re.M))
        passing = [f for f in files if passes(f)]
        review = ", ".join(passing)
        if not passing:
            bad.append(f"{w2}: FULL ticket without a passing independent review record at {commit[:12]}")
    if scan_change(w2, commit):
        bad.append(f"{w2}: gitleaks found a leak in its change")
    for f in git("diff", "--name-only", f"w2/integrate...{commit}").splitlines():
        if f.endswith((".yaml", ".yml")) and git("cat-file", "-t", f"{commit}:{f}") == "blob":
            r = sh([sys.executable, "-c", "import sys, yaml; yaml.safe_load(sys.stdin)"],
                   input=git("show", f"{commit}:{f}"))
            if r.returncode:
                bad.append(f"{w2}: {f} does not parse as YAML")
    return bad, review


def close_record(w2, tid, profile, landed, rec, review, base_why):
    sel = rec.get("selection") or {}
    lines = [f"# {w2} ({tid}) closed: merged and closed in one step by the merge queue (DEC-989)", "",
             f"- Commit tested (the lead's final, verified result): {landed['commit'][:12]}; merge {landed['merge'][:12]}"
             f"; w2/integrate {rec['base'][:12]} -> {rec['head'][:12]} (fast-forward to the tested merge); profile {profile}",
             f"- Queue record: {landed['record']}; log {rec.get('log')}",
             f"- Batch: {', '.join(t['ticket'] for t in rec.get('tickets', []))}",
             f"- Run: " + (f"skipped: {rec['skipped']}" if rec.get("skipped") else
                           f"scoped, {len(sel.get('targets', []))} targets; counts {rec.get('counts')}"),
             f"- Selected: {', '.join(sel.get('targets', [])[:40])}" + (" ..." if len(sel.get('targets', [])) > 40 else ""),
             f"- Reds caused by the change: none (the queue advances only then); flaky candidates: "
             f"{', '.join(rec.get('flaky') or []) or 'none'}",
             f"- Traced against: {rec.get('trace_base') or 'n/a'} ({base_why}; DEC-989)",
             f"- Red at the baseline too, the same failure, not this change's (investigated by the CTO at once, "
             f"DEC-968): {', '.join(rec.get('unowned') or []) or 'none'}",
             f"- Core changed (scoped, not full, DEC-968): {', '.join(sel.get('core_changed') or []) or 'none'}; "
             f"unplaced: {', '.join(sel.get('unplaced') or []) or 'none'}",
             f"- Review: {review}", gitleaks_line(),
             f"- Queue run: {rec.get('started')} to {rec.get('finished')}",
             f"- Closed: {time.strftime('%F %T %Z')}, by the orchestrator under DEC-953 items 1 and 5, DEC-989", ""]
    return "\n".join(lines)


def strays(queue, names):
    """Approvals in the queue for tickets this call does not name (DEC-1037 (5)): a queue run lands every approval, so
    one left from a stopped landing would ride along (2026-11-02 14:16: six stopped tickets batched with two fixes)."""
    return sorted(p.stem for p in (Path(queue) / "approved").glob("*.json") if p.stem not in set(names))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickets", nargs="+")
    ap.add_argument("--base")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    global SCAN
    try:
        SCAN = scan_on(ROOT)
    except SwitchError as e:  # fails closed: nothing is queued on a switch that cannot be read
        print(f"REFUSED before anything was queued: the secrets-scan switch: {e}", flush=True)
        sys.exit(2)
    if not SCAN:
        print(f"{OFF_LINE}: no ticket's change is scanned ({ROOT / SWITCH_REL})", flush=True)
    if a.base:
        base, base_why = git("rev-parse", a.base), f"given with --base"
    else:
        base, base_why = baseline()
        base = git("rev-parse", base)
    items, bad = [], []
    if sh(["bash", str(ORCH / "tools/disk_gate.sh")]).returncode:
        bad.append("disk gate shut")
    left = strays(QUEUE, [t.partition("=")[0] for t in a.tickets])
    if left:
        bad.append(f"approved in the queue but not in this landing: {', '.join(left)} (park them with "
                   f"tools/queue_park.py park, or name them)")
    for t in a.tickets:
        w2, _, commit = t.partition("=")
        tid, profile = ticket_of(w2)
        commit = git("rev-parse", "--verify", "-q", (commit or f"w2/{w2}") + "^{commit}")
        if not commit:
            bad.append(f"{w2}: no commit")
            continue
        b, review = precheck(w2, tid, profile, commit)
        bad += b
        items.append({"w2": w2, "tid": tid, "profile": profile, "commit": commit, "review": review})
        print(f"{w2} ({tid}, {profile}) at {commit[:12]}: " + ("; ".join(b) or "pre-check passed"), flush=True)
    if bad:
        print("REFUSED before anything was queued: " + "; ".join(bad), flush=True)
        sys.exit(2)
    print(f"baseline {base[:12]} ({base_why})", flush=True)
    if a.check:
        return
    for i in items:
        for cmd in (["enqueue", "--queue", str(QUEUE), "--ticket", i["w2"], "--task", i["tid"], "--branch",
                     f"w2/{i['w2']}", "--commit", i["commit"], "--repo", str(ROOT)],
                    ["approve", "--queue", str(QUEUE), "--ticket", i["w2"], "--by", "CTO"]):
            r = sh([sys.executable, str(MQ), *cmd])
            if r.returncode:
                sys.exit(f"{i['w2']}: merge_queue {cmd[0]} failed: {r.stderr.strip()[:300]}")
    started = time.strftime("%F %T")
    junit, nightly_run = base_record(base[:12])
    extra = ["--warm", str(WARM), "--integration-store", str(STORE), "--nightly-log", str(NIGHTLY),
             "--nightly-junit", str(JUNIT)]
    if junit and nightly_run:
        extra += ["--base-results", str(junit), "--base-run", str(nightly_run)]
        print(f"the baseline's own record: {junit}, {nightly_run}", flush=True)
    run = subprocess.run([sys.executable, str(MQ), "run", "--repo", str(ROOT), "--queue", str(QUEUE), "--base", base,
                          *extra])
    print(f"queue run exit {run.returncode}", flush=True)
    failed_close = False
    for i in items:
        lf = QUEUE / "landed" / f"{i['w2']}.json"
        if not lf.is_file():
            ej = QUEUE / "ejected" / f"{i['w2']}.json"
            print(f"{i['w2']}: not landed" + (f" (ejected: {json.loads(ej.read_text())['reason']})" if ej.is_file()
                                               else " (still approved)"), flush=True)
            continue
        landed = json.loads(lf.read_text())
        if landed.get("landed_at", "") < started or landed["commit"] != i["commit"]:  # both "%Y-%m-%d %H:%M:%S"
            print(f"{i['w2']}: its landed entry is not this run's; not closed here", flush=True)
            continue
        rec = json.loads(Path(landed["record"]).read_text())
        out = ROOT / "governance/project/orchestration/closes" / f"{i['w2']}-{i['tid']}.md"
        out.write_text(close_record(i["w2"], i["tid"], i["profile"], landed, rec, i["review"], base_why))
        tk = sh(["tk", "close", i["tid"]], cwd=ROOT)
        paths = [str(out.relative_to(ROOT)), f".tickets/{i['tid']}.md"]
        git_retry(["add", "--", *paths])
        cm = git_retry(["commit", "-q", "-m",
                 f"{i['w2']} ({i['tid']}): merged and closed in one step by the merge queue (DEC-989)",
                 "--trailer", f"Task: {i['tid']}", "--trailer", "Implements: DEC-953, DEC-989", "--trailer",
                 "Role: orchestrator", "--trailer", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                 "--", *paths])
        if tk.returncode or cm.returncode:
            failed_close = True
            print(f"{i['w2']}: LANDED BUT NOT CLOSED: tk {tk.returncode} {tk.stderr.strip()[:200]}; commit "
                  f"{cm.returncode} {cm.stderr.strip()[:200]}", flush=True)
            continue
        (QUEUE / "closed").mkdir(exist_ok=True)
        lf.rename(QUEUE / "closed" / lf.name)
        print(f"CLOSED {i['w2']}: {git('log', '--oneline', '-1')}", flush=True)
    sys.exit(6 if failed_close else run.returncode)


if __name__ == "__main__":
    main()
