"""The CTO's idle check, a Stop hook (DEC-1110 (1)): planted DECIDED-NOT-DONE files and planted running states."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HOOK = Path(os.environ.get("GOV_STOPIDLE_HOOK") or Path(__file__).resolve().parents[3]
            / "governance/project/orchestration/tools/stop_idle_check.py")
LIVE_DND = Path(os.environ.get("GOV_STOPIDLE_LIVE_DND") or Path(__file__).resolve().parents[3]
                / "governance/project/orchestration/packages/DECIDED-NOT-DONE.md")
CTO = "ad44f5fe-0000-0000-0000-000000000000"

DND = """# Decided but not done

## 0. Fates: the tracking table
| # | item | fate | state |
|---|---|---|---|
| 1 | the first | (2) | **DONE 11-08**: applied `15952bbf` |
| 4 | fewer pairs | (10) | WAITS: after the lift |
| 14 | the label audit | (13) | **DONE (trigger set)**; rubric v3 **DUE NOW** (after the 80) |

## 0b. Items
| # | item | state |
|---|---|---|
| 25 | the experiment | **Design to the owner 11-09**; WAITS: the owner's answers |
| 30 | W2-56's result-independent tests | NOT STARTED |
| 35 | W2-15a with W2-32 | Noted in P1-13; WAITS: the lift |
| 63 | W2-139 and W2-140, one batch | IN PROGRESS |
| 72 | a fresh session | WAITS: the running helpers |

## 1. Every item not done
| # | item | state |
|---|---|---|
| 99 | outside the tracking tables | NOT STARTED |
"""

ALL_WAIT = """# D

## 0. T
| # | item | state |
|---|---|---|
| 1 | a | **MERGED 11-09** (`b1e2c3b9`) |
| 2 | b | WAITS: the owner's word |
| 3 | c | WAITS: W2-20, then D-10 and the owner's word |
| 4 | d | WAITS: the running helpers |
| 5 | e | WAITS: after the lift |
| 6 | f | STANDING (from now) |
"""


def status(**over):
    st = {"time": "now", "leads": [], "lead_count": 0, "jobs": [], "pending_launches": [], "gate_open": True,
          "gate": "OPEN leads=0", "disk_open": True, "disk": "disk gate open", "admit": True,
          "admit_reason": "forecast admits", "close_running": False, "land_running": False,
          "forecast": {"lead": {"ok": True, "reason": "forecast admits"}}}
    st.update(over)
    return st


class World:
    def __init__(self, tmp):
        self.tmp = tmp
        self.orch = tmp / "orch"
        (self.orch / "log").mkdir(parents=True)
        (self.orch / "dispatch").mkdir()
        (self.orch / "log/cto-session.txt").write_text(CTO + "\n")
        self.dnd = tmp / "DND.md"
        self.dnd.write_text(DND)
        self.tasks = tmp / "tasks"
        self.tasks.mkdir()
        self.sub = tmp / "subagents"
        self.sub.mkdir()
        self.procs = []
        self.pidglobs = [str(tmp / "trees/*/.gov-runtime/scratch/lead/log/*.pid")]
        self.transcript = tmp / "session.jsonl"
        self.transcript.write_text(json.dumps({"type": "user", "uuid": "turn-1", "message": {"content": "go"}}) + "\n")
        self.set_status(status())

    def set_status(self, st, age=0):
        p = self.orch / "dispatch/status.json"
        p.write_text(json.dumps(st))
        t = time.time() - age
        os.utime(p, (t, t))

    def agent(self, name, finished=False, age=0):
        (self.sub / f"agent-{name}.meta.json").write_text(json.dumps(
            {"description": name, **({"finished": True} if finished else {})}))
        j = self.sub / f"agent-{name}.jsonl"
        j.write_text("{}\n")
        t = time.time() - age
        os.utime(j, (t, t))

    def task(self, tid, cmd, pid, started_ago=60):
        out = self.tasks / f"{tid}.output"
        out.write_text("")
        self.procs.append({"pid": pid, "cmdline": f"/bin/bash -c source snap && eval '{cmd}' < /dev/null && pwd -P",
                           "start": time.time() - started_ago, "fds": [str(out)]})

    def worker(self, tree, name, pid, started_ago=60, written_ago=50, cmdline="sleep 1", exit_file=False, live=True):
        d = self.tmp / "trees" / tree / ".gov-runtime/scratch/lead/log"
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{name}.pid"
        f.write_text(f"{pid}\n")
        t = time.time() - written_ago
        os.utime(f, (t, t))
        if exit_file:
            (d / f"{name}.exit").write_text("0\n")
        if live:
            self.procs.append({"pid": pid, "cmdline": cmdline, "start": time.time() - started_ago, "fds": []})

    def say(self, *texts, after_turn=True):
        with open(self.transcript, "a") as f:
            for t in texts:
                f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}}) + "\n")

    def new_turn(self, uuid):
        with open(self.transcript, "a") as f:
            f.write(json.dumps({"type": "user", "uuid": uuid,
                                "message": {"content": "<task-notification> done </task-notification>"}}) + "\n")

    def wakeup(self, uuid):
        """A scheduled wakeup as this Claude Code writes it: a meta user entry carrying turnOrigin and wakeupSource."""
        with open(self.transcript, "a") as f:
            f.write(json.dumps({"type": "user", "uuid": uuid, "isMeta": True, "turnOrigin": "scheduled",
                                "wakeupSource": "schedule_wakeup",
                                "message": {"content": "<scheduled-wakeup> the 18:00 digest </scheduled-wakeup>"}}) + "\n")

    def meta(self, uuid):
        """A system reminder: a meta user entry with no turnOrigin, inside the same turn."""
        with open(self.transcript, "a") as f:
            f.write(json.dumps({"type": "user", "uuid": uuid, "isMeta": True,
                                "message": {"content": "<system-reminder> x </system-reminder>"}}) + "\n")

    def run(self, session=CTO, active=False, raw=None, extra=None):
        procfile = self.tmp / "procs.json"
        procfile.write_text(json.dumps(self.procs))
        env = dict(os.environ, GOV_STOPIDLE_ORCH=str(self.orch), GOV_STOPIDLE_DND=str(self.dnd),
                   GOV_STOPIDLE_TASKS=str(self.tasks), GOV_STOPIDLE_SUBAGENTS=str(self.sub),
                   GOV_STOPIDLE_PROC=str(procfile), GOV_STOPIDLE_PIDGLOBS=":".join(self.pidglobs))
        data = {"session_id": session, "stop_hook_active": active, "transcript_path": str(self.transcript),
                "hook_event_name": "Stop", **(extra or {})}
        out = subprocess.run([sys.executable, "-E", str(HOOK)], input=raw if raw is not None else json.dumps(data),
                             capture_output=True, text=True, env=env, timeout=30)
        assert out.returncode == 0, out.stderr
        assert out.stderr == "", out.stderr
        return json.loads(out.stdout) if out.stdout.strip() else None

    def log(self):
        p = self.orch / "log/stop-idle.log"
        return p.read_text() if p.exists() else ""


def test_idle_with_unblocked_items_blocks_and_names_them(tmp_path):
    w = World(tmp_path)
    ans = w.run()
    assert ans["decision"] == "block"
    r = ans["reason"]
    assert "DEC-1110" in r and "IDLE-REASON" in r
    assert "#30 W2-56's result-independent tests (NOT STARTED)" in r
    assert "#63 W2-139 and W2-140, one batch (IN PROGRESS)" in r
    assert "#14 the label audit" in r and "DUE NOW" in r          # a DONE row with a DUE NOW part is open
    assert "3 unblocked" in r
    for not_open in ("#1 ", "#4 ", "#25 ", "#35 ", "#72 ", "#99 "):  # closed, waits, or outside the §0 tables
        assert not_open not in r
    assert "\tblock\t3 unblocked\t" in w.log()
    assert json.loads((w.orch / "log/stop-idle-state.json").read_text())["turn"] == "turn-1"


def test_every_open_item_waiting_lets_the_turn_end_and_names_the_case(tmp_path):
    w = World(tmp_path)
    w.dnd.write_text(ALL_WAIT)
    ans = w.run()
    assert "decision" not in ans
    assert "every open item waits (2 on the owner, 1 on a running job, 1 on a trigger)" in ans["systemMessage"]
    assert "\tthrough\tevery open item waits" in w.log()


def test_a_running_background_agent_lets_the_turn_end_silently(tmp_path):
    w = World(tmp_path)
    w.agent("D-5 the templates")
    assert w.run() is None
    assert "running: 1\tagent D-5 the templates" in w.log()


def test_a_finished_or_stale_agent_is_not_running(tmp_path):
    w = World(tmp_path)
    w.agent("done one", finished=True)
    w.agent("lost one", age=3600)
    ans = w.run()
    assert ans["decision"] == "block"
    assert "lost one" not in ans["reason"] and "done one" not in ans["reason"]
    assert "agent lost one: unfinished but silent 60 min (stale, not counted)" in w.log()


def test_a_running_background_task_counts_but_the_watchers_do_not(tmp_path):
    w = World(tmp_path)
    w.task("bwait01", "bash /x/tools/inbox_wait_quiet.sh", 101)
    w.task("bsent01", "bash /x/tools/sentinel_check.sh", 102)
    w.task("btimer1", "sleep 1800", 103)
    assert w.run()["decision"] == "block"
    w2 = World(tmp_path / "second")
    w2.task("bjob001", "python3 -m pytest tests/unit -q", 104)
    assert w2.run() is None
    assert "task bjob001: python3 -m pytest tests/unit -q" in w2.log()


def test_a_finished_task_whose_file_nobody_holds_is_not_running(tmp_path):
    w = World(tmp_path)
    (w.tasks / "bold001.output").write_text("done\n")
    assert w.run()["decision"] == "block"


def test_a_launched_worker_by_its_pid_file_counts(tmp_path):
    w = World(tmp_path)
    w.worker("W2-129-d6", "W2-129-engineer-d6", 201)
    assert w.run() is None
    assert "pid 201 (W2-129-d6: W2-129-engineer-d6.pid)" in w.log()


def test_a_worker_with_its_exit_file_or_a_dead_pid_is_not_running(tmp_path):
    w = World(tmp_path)
    w.worker("W2-1", "done", 202, exit_file=True)
    w.worker("W2-2", "gone", 203, live=False)
    assert w.run()["decision"] == "block"


def test_a_reused_pid_is_not_counted_unless_it_is_a_launcher(tmp_path):
    w = World(tmp_path)
    w.worker("W2-3", "old", 204, started_ago=60, written_ago=86400 * 20, cmdline="python3 someone_else.py")
    assert w.run()["decision"] == "block"
    w2 = World(tmp_path / "second")
    w2.worker("W2-4", "old", 205, started_ago=60, written_ago=86400 * 20,
              cmdline="bash /x/tools/launch_worker.sh --run /t W2-4 engineer high b base")
    assert w2.run() is None


def test_the_dispatchers_leads_and_jobs_count(tmp_path):
    w = World(tmp_path)
    w.set_status(status(lead_count=1, leads=["W2-20"]))
    assert w.run() is None
    w2 = World(tmp_path / "second")
    w2.set_status(status(jobs=[{"kind": "slot", "name": "pid 9", "phase": "test"}]))
    assert w2.run() is None
    assert "dispatcher job: slot pid 9 (test)" in w2.log()


def test_the_gate_shut_or_the_machine_full_lets_the_turn_end_and_names_which(tmp_path):
    w = World(tmp_path)
    w.set_status(status(gate_open=False, gate="SHUT load 19.5"))
    assert "the gate shut (SHUT load 19.5)" in w.run()["systemMessage"]
    w2 = World(tmp_path / "second")
    w2.set_status(status(forecast={"lead": {"ok": False, "reason": "REFUSES, binding CPU"}}))
    assert "the machine full (REFUSES, binding CPU)" in w2.run()["systemMessage"]
    w3 = World(tmp_path / "third")
    w3.set_status(status(disk_open=False, disk="disk gate SHUT: 90 GiB"))
    assert "the gate shut (disk gate SHUT: 90 GiB)" in w3.run()["systemMessage"]


def test_a_stale_dispatcher_status_is_named_and_not_relied_on(tmp_path):
    w = World(tmp_path)
    w.set_status(status(gate_open=False, lead_count=2), age=900)
    ans = w.run()
    assert ans["decision"] == "block"
    assert "dispatcher status unusable (written" in ans["reason"]


def test_it_blocks_at_most_once_per_turn(tmp_path):
    w = World(tmp_path)
    assert w.run()["decision"] == "block"
    again = w.run()                                     # the same turn, even without stop_hook_active
    assert "decision" not in again and "second stop this turn" in again["systemMessage"]
    assert "bound: blocked once this turn" in w.log()
    w.new_turn("turn-2")
    assert w.run()["decision"] == "block"               # a new turn is checked again


def test_stop_hook_active_never_blocks(tmp_path):
    w = World(tmp_path)
    ans = w.run(active=True)
    assert "decision" not in ans and "IDLE-REASON" in ans["systemMessage"]


def test_a_stated_reason_line_lets_the_turn_end_and_is_recorded(tmp_path):
    w = World(tmp_path)
    w.say("Waiting.\nIDLE-REASON: every item needs the GPU window at 22:00\nThat is all.")
    ans = w.run()
    assert "decision" not in ans
    assert "every item needs the GPU window at 22:00" in ans["systemMessage"]
    assert "the CTO's stated reason\tevery item needs the GPU window at 22:00" in w.log()


def test_a_reason_line_from_an_earlier_turn_does_not_count(tmp_path):
    w = World(tmp_path)
    w.say("IDLE-REASON: an old excuse")
    w.new_turn("turn-2")
    w.say("nothing to do")
    assert w.run()["decision"] == "block"


def test_the_last_assistant_message_field_is_read_too(tmp_path):
    w = World(tmp_path)
    ans = w.run(extra={"last_assistant_message": "IDLE-REASON: the owner's sitting at 21:00 decides all of them"})
    assert "decision" not in ans and "owner's sitting" in ans["systemMessage"]


def test_a_declared_stand_by_does_not_let_an_idle_turn_end(tmp_path):
    w = World(tmp_path)
    (w.orch / "log/cto-standby.txt").write_text("waiting on the owner\n")
    assert w.run()["decision"] == "block"


def test_another_session_or_no_registered_session_says_nothing(tmp_path):
    w = World(tmp_path)
    assert w.run(session="someone-else") is None
    (w.orch / "log/cto-session.txt").unlink()
    assert w.run() is None
    assert w.log() == ""


def test_a_missing_or_malformed_file_is_named_and_the_turn_ends(tmp_path):
    cases = {
        "missing": None,
        "no state column": "## 0. T\n| # | item | fate |\n|---|---|---|\n| 1 | a | b |\n",
        "no tracking section": "# D\n## 1. Other\n| # | item | state |\n|---|---|---|\n| 1 | a | NOT STARTED |\n",
        "short row": "## 0. T\n| # | item | fate | state |\n|---|---|---|---|\n| 1 | a |\n",
        "section without table": "## 0. T\nnothing here\n## 0b. U\n| # | item | state |\n|---|---|---|\n",
    }
    for i, (name, text) in enumerate(cases.items()):
        w = World(tmp_path / str(i))
        if text is None:
            w.dnd.unlink()
        else:
            w.dnd.write_text(text)
        ans = w.run()
        assert ans is not None and "decision" not in ans, name
        assert "could not run" in ans["systemMessage"] and "DECIDED-NOT-DONE" in ans["systemMessage"], name
        assert "\terror\tCheckError: DECIDED-NOT-DONE" in w.log(), name


def test_bad_input_is_named_not_silent(tmp_path):
    w = World(tmp_path)
    ans = w.run(raw="not json")
    assert "could not run" in ans["systemMessage"]
    assert "\terror\t" in w.log()


def test_the_live_decided_not_done_parses(tmp_path):
    """The tree's own file reads without error; a state in no known form is named, never an error or silence."""
    w = World(tmp_path)
    w.dnd = LIVE_DND
    ans = w.run()
    assert ans is not None and "could not run" not in json.dumps(ans)


def test_a_state_in_no_known_form_is_open(tmp_path):
    """F2: only DONE, MERGED, APPLIED (and STANDING, SUPERSEDED, CLOSED) with no pending step close a row."""
    w = World(tmp_path)
    w.dnd.write_text(ALL_WAIT + "| 7 | g | Built (45 tests), to review |\n")
    ans = w.run()
    assert ans["decision"] == "block" and "#7 g (Built (45 tests), to review)" in ans["reason"]


def test_the_default_paths_are_the_trees_own(tmp_path):
    """Installed at <repo>/governance/project/orchestration/tools/, it reads <repo>'s scratch and DECIDED-NOT-DONE."""
    import shutil
    repo = tmp_path / "repo"
    tools = repo / "governance/project/orchestration/tools"
    tools.mkdir(parents=True)
    (repo / "governance/project/orchestration/packages").mkdir()
    (repo / "governance/project/orchestration/packages/DECIDED-NOT-DONE.md").write_text(DND)
    orch = repo / ".gov-runtime/scratch/orchestrator"
    (orch / "log").mkdir(parents=True)
    (orch / "log/cto-session.txt").write_text(CTO + "\n")
    shutil.copy(HOOK, tools / "stop_idle_check.py")
    (tmp_path / "procs.json").write_text("[]")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_STOPIDLE_")}
    env.update(GOV_STOPIDLE_PROC=str(tmp_path / "procs.json"), GOV_STOPIDLE_PIDGLOBS="",
               GOV_STOPIDLE_TASKS=str(tmp_path / "none"), GOV_STOPIDLE_SUBAGENTS=str(tmp_path / "none"))
    out = subprocess.run([sys.executable, "-E", str(tools / "stop_idle_check.py")],
                         input=json.dumps({"session_id": CTO, "stop_hook_active": False}),
                         capture_output=True, text=True, env=env, timeout=30)
    assert out.returncode == 0 and out.stderr == ""
    ans = json.loads(out.stdout)
    assert ans["decision"] == "block" and "#30 W2-56" in ans["reason"]
    assert "dispatcher status unusable" in ans["reason"]          # no status.json in this tree: named
    assert "\tblock\t" in (orch / "log/stop-idle.log").read_text()


# ---- round 2 (the review's F1, F2, F3)
def test_f1_a_scheduled_wakeup_is_a_new_turn_after_a_block(tmp_path):
    w = World(tmp_path)
    assert w.run()["decision"] == "block"
    w.wakeup("wake-1")
    assert w.run()["decision"] == "block"


def test_f1_a_reason_line_does_not_carry_into_a_scheduled_wakeup(tmp_path):
    w = World(tmp_path)
    w.say("IDLE-REASON: the owner decides tonight")
    w.wakeup("wake-1")
    w.say("nothing new")
    assert w.run()["decision"] == "block"


def test_f1_a_meta_entry_without_turn_origin_stays_in_the_turn(tmp_path):
    w = World(tmp_path)
    assert w.run()["decision"] == "block"
    w.meta("reminder-1")
    assert "second stop this turn" in w.run()["systemMessage"]


F2_ROWS = """# D

## 0. T
| # | item | state |
|---|---|---|
| 21 | W2-88's lines | ANSWERED 11-09 (DEC-1099 (2)); next: the lines into W2-88 (marked) |
| 32 | the nonexistent-id ticket | **Filed 11-09**: W2-146 `DAEO-f6x3` (`cbbe9733`); next: its test designer |
| 38 | W2-66c | Filed `DAEO-btcs` (`28b4b5ba`); its test designer next |
| 52 | the operator-agent package | APPROVED (DEC-1104 (2)); next: build it, tests first, one review |
| 69 | D-10's red-fix list | **READY 11-09**: W1-06 on `w2/W2-130-d10-tests` (reviewed), both reviews READY, not merged |
| 28 | the seal | Rehearsed; inside ACT-INDEP-WALLS-1 |
| 50 | the gate file | **APPLIED twice 11-09**: ACT-GATE-CONFIG-1 (`d7490945`), then ACT-GATE-CONFIG-2 (`0fcd02b0`) |
| 41 | the cycle break | **MERGED 11-09** W2-147 (`7ed72a1e`, review READY); live at the lift's re-pin |
| 13 | ADR-0002 | **DONE 11-09**: ADR-0002 ACCEPTED; WAITS: re-read at the lift's re-pin |
| 16 | the old scripts | **DONE 11-08**: moved to `retired/`; next: delete them after the lift |
| 47 | unindexed-path notices | STANDING (from now) |
| 49 | the re-pin ACT | WAITS: W2-20, then D-10 and the owner's word |
| 60 | the temp folder | **DONE (part 1)**; part 2 NOT STARTED |
"""


def test_f2_a_closed_word_with_a_pending_next_step_is_open(tmp_path):
    w = World(tmp_path)
    w.dnd.write_text(F2_ROWS)
    r = w.run()["reason"]
    for n in ("#21 ", "#32 ", "#38 ", "#52 ", "#69 ", "#28 ", "#16 ", "#60 "):
        assert n in r, n
    for n in ("#50 ", "#41 ", "#13 ", "#47 ", "#49 "):   # final words with no pending step; waits
        assert n not in r, n
    assert "8 unblocked" in r


def test_f3_a_task_older_than_the_bound_is_not_counted_and_is_named(tmp_path):
    w = World(tmp_path)
    w.task("bqav99d", "until grep -q done x.output; do sleep 10; done", 301, started_ago=4 * 3600)
    ans = w.run()
    assert ans["decision"] == "block"
    assert "over the 3 h bound, not counted: task bqav99d" in ans["reason"]
    w2 = World(tmp_path / "second")
    w2.task("byoung1", "until grep -q done x.output; do sleep 10; done", 302, started_ago=2 * 3600)
    assert w2.run() is None


def test_f3_a_pid_file_older_than_the_bound_is_not_counted_and_is_named(tmp_path):
    w = World(tmp_path)
    w.worker("D4B", "svc", 303, started_ago=5 * 3600, written_ago=5 * 3600)
    ans = w.run()
    assert ans["decision"] == "block"
    assert "over the 3 h bound, not counted: pid 303 (D4B: svc.pid) 5 h" in ans["reason"]


def test_f2_the_open_words_are_the_upper_case_states_not_prose(tmp_path):
    w = World(tmp_path)
    w.dnd.write_text(ALL_WAIT + '| 12 | K9 | **DONE 11-08**: status_block.py reads the lists; K9 now "in progress" |\n')
    assert "decision" not in w.run()
