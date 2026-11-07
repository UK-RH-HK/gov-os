"""Tests of E4's new parts, on stand-ins: e4_window.sh's and e4_replays.sh's control flow, e4_prepare.py and
e4_count.py. Neither script holds a test seam: each case runs a temporary copy with one line added (``. "$E4TEST_STUBS"``,
before the OUT line), which sources a stubs file replacing the GPU reads, the sampler, the service, the measures, the
stops, the hold and the live service (no GPU, no service, no real folder written); E0 and R0 check each copy less that
line is the shipped file byte for byte. E7 keeps the real ``arm`` and ``disarm`` with a stand-in backstop. G1-G3 (review
F1) run the copy in its own session with real stand-in processes for the trial service and the measure (``setsid
sleep``), then signal its WHOLE process group (TERM, INT) or close its output, and read the window's log file. C5 imports
the real rx.py (window 4's clone's gov on PYTHONPATH, so_measure.sh's form) with HOME a temporary folder and a strict
replay's environment, so no reranker can be reached. No GPU, no question read. Every temporary folder is made under
one root, removed when every case passes (kept for a look when one fails); no byte code is written (review F6).

    python3 test_e4.py
"""
import hashlib
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
ROOT = tempfile.mkdtemp(prefix="e4tests-")


def mkd(prefix: str) -> str:
    return tempfile.mkdtemp(prefix=prefix, dir=ROOT)


HERE = Path(__file__).resolve().parent
WINDOW, REPLAYS = HERE / "e4_window.sh", HERE / "e4_replays.sh"
sys.path.insert(0, str(HERE))
import e4_count  # noqa: E402
import e4_prepare  # noqa: E402

CLONE_SRC = Path.home() / "gov-os-runs/D4B/w4-e0/repo/src"
Q06 = "Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473"
GTE = "Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c"
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + str(detail) if detail and not ok else ''}")


ANCHOR = 'if [ "${DRY:-0}" != 1 ]; then OUT='
STUB_LINE = '. "$E4TEST_STUBS"\n'


def copy_with_stubs(src: Path, t: Path) -> Path:
    text = src.read_text()
    at = text.index(ANCHOR)
    path = t / (src.stem + ".copy.sh")
    path.write_text(text[:at] + STUB_LINE + text[at:])
    return path


def ordered(lines, texts):
    pos = -1
    for text in texts:
        nxt = next((i for i, line in enumerate(lines) if i > pos and text in line), None)
        if nxt is None:
            return False
        pos = nxt
    return True


# ------------------------------------------------------------------------------------------------ the window
W_STUBS = r'''
T=__T__
P=$T/runs; Q=$P/e4; QC=$Q/caches; CNT=$Q/count; TR=$T/tr; RUN=$TR/run
BASE_TRIES=1; BASE_EVERY=0
ev() { echo "EVENT $*"; }
gpu() { cat $T/gpu_now; }
gpu_total() { echo 16303; }
warm() { :; }
start_sampler() { ev "sampler start $(basename "$1")"; echo 7000 > "$1"; SAMP=stub; }
stop_sampler() { [ -n "$SAMP" ] && ev "sampler stop"; SAMP=""; }
restore() { ev restore; }
take_hold() { HELD=1; ev hold; }
release_hold() { [ "$HELD" = 1 ] && ev "hold released"; HELD=0; }
stop_live() { LIVE_STOPPED=1; ev "live stopped"; cp $T/gpu_base $T/gpu_now; }
stop_group() { ev "stop group $1"; cp $T/gpu_after_stop $T/gpu_now; }
__ARM__
conditions() { ev conditions; }
embedders() { ev embedders; }
slots_free() { echo 1; }
start_svc() { ev "start $1"; SP=101; SVC=-101; arm "$MG" "$SP"; cp $T/gpu_load $T/gpu_now; }
measure() {
  ev "measure $1 $2"; MP=202; arm "$MG" "$SP" "$MP"
  local rc=0; [ -e $T/fail-$1-$2 ] && rc=1
  [ -e $T/term-$1-$2 ] && { kill -TERM $$; sleep 1; }
  echo $(( $(cat $T/scores-$1) + 7 )) > $T/scores-$1
  [ -e $T/routes-grow-$1 ] && echo 900 > $T/routes-$1
  MP=""; arm "$MG" "$SP"; return $rc
}
scores_in() { cat $T/scores-$(basename "$1"); }
routes_in() { cat $T/routes-$(basename "$1"); }
lacking() { ev "lacking $1"; [ ! -e $T/lacks-$1 ]; }
figures() { ev "figures $1"; }
'''
STUB_ARM = 'arm() { ev "arm $*"; }\ndisarm() { BS=""; }'


def made(name, base="6100", after_stop="6200", files=(), backstop=None, extra=""):
    t = Path(mkd(prefix=f"e4w-{name}-"))
    if backstop is not None:
        tools = t / "orch/tools"
        tools.mkdir(parents=True)
        (tools / "gpu_backstop.sh").write_text(backstop.replace("__T__", str(t)))
        (tools / "proc.sh").write_bytes((HERE.parent.parent / "tools/proc.sh").read_bytes())
    arm = "O=$T/orch" if backstop is not None else STUB_ARM
    (t / "stubs.sh").write_text(W_STUBS.replace("__T__", str(t)).replace("__ARM__", arm) + extra.replace("__T__", str(t)))
    for f, v in {"gpu_now": "7400", "gpu_base": base, "gpu_load": "8000", "gpu_after_stop": after_stop,
                 "scores-gte": "5486", "scores-zer": "5486", "routes-gte": "875", "routes-zer": "875"}.items():
        (t / f).write_text(v)
    for f in files:
        (t / f).write_text("")
    return t


def window(name, models=("gte", "zer"), base="6100", after_stop="6200", files=(), backstop=None, dry=False, extra=""):
    t = made(name, base, after_stop, files, backstop, extra)
    env = {**os.environ, "E4TEST_STUBS": str(t / "stubs.sh")}
    env.pop("DRY", None)
    if dry:
        env["DRY"] = "1"
    r = subprocess.run(["bash", str(copy_with_stubs(WINDOW, t)), *models], capture_output=True, text=True, env=env,
                       timeout=180)
    return r, t, r.stdout.splitlines()


shipped = WINDOW.read_bytes()
t0 = Path(mkd(prefix="e4w-seam-"))
copy = copy_with_stubs(WINDOW, t0).read_bytes()
check("E0 the shipped window names no stubs and its OUT line is there once",
      b"E4TEST_STUBS" not in shipped and shipped.decode().count(ANCHOR) == 1)
check("E0b the tested copy less its one stubs line is byte-identical to e4_window.sh",
      copy.count(STUB_LINE.encode()) == 1 and copy.replace(STUB_LINE.encode(), b"", 1) == shipped)

r, t, lines = window("pass")
check("E1 a clean window runs to its end on stand-ins (exit 0)", r.returncode == 0, r.stdout[-900:] + r.stderr[-400:])
check("E1b the order: conditions, embedders, hold, live stop, base; gte loaded, r80, r60, stopped by group, back to "
      "the base, checked; then zer the same; the restore and the hold released last", ordered(lines, [
          "EVENT conditions", "EVENT embedders", "EVENT hold", "EVENT live stopped",
          "base GPU (the live service stopped, both embedders warm): 6100", "== ", "EVENT start gte",
          "EVENT sampler start gpu-gte.txt", "EVENT measure gte r80", "EVENT measure gte r60", "EVENT sampler stop",
          "EVENT stop group -101", "gte: GPU after the stop 6200", "gte: texts newly scored 14 (cache 5486 -> 5500); "
          "route answers 875 -> 875", "EVENT lacking gte", "EVENT figures gte", "EVENT start zer",
          "EVENT measure zer r80", "EVENT measure zer r60", "EVENT stop group -101", "EVENT lacking zer",
          "EVENT figures zer", "all models scored once", "EVENT restore", "EVENT hold released",
          "the E4 window ends (exit 0)"]), lines)
check("E1c each measure under a backstop on the script's group, the service's and the measure's",
      sum(1 for x in lines if x.startswith("EVENT arm ") and x.endswith(" 101 202")) == 4, lines)
check("E1d one service at a time: zer starts only after gte's group is stopped",
      ordered(lines, ["EVENT start gte", "EVENT stop group -101", "EVENT start zer"])
      and sum(1 for x in lines if x.startswith("EVENT start ")) == 2)

r, t, lines = window("fail", files=("fail-gte-r60",))
check("E2 gte's r60 measure fails: the window stops, the service stopped by group, the live service restored, zer "
      "never started (exit 1)", r.returncode == 1 and ordered(lines, [
          "EVENT measure gte r60", "gte: the r60 measure ended with an error", "EVENT stop group -101",
          "STOP: gte's runs failed", "EVENT restore", "EVENT hold released", "the E4 window ends (exit 1)"])
      and not any("EVENT start zer" in x for x in lines), lines[-12:])

r, t, lines = window("lacks", files=("lacks-gte",))
check("E3 gte still lacks texts after its runs: the window stops before zer, restores (exit 1)",
      r.returncode == 1 and ordered(lines, ["EVENT lacking gte", "STOP: gte still lacks texts", "EVENT restore"])
      and not any("EVENT start zer" in x for x in lines), lines[-10:])

r, t, lines = window("nobase", after_stop="9000")
check("E4 the GPU does not return to the base after gte: the window stops, restores (exit 1)",
      r.returncode == 1 and ordered(lines, ["STOP: the GPU did not return to the base after gte", "EVENT restore"])
      and not any("EVENT start zer" in x for x in lines), lines[-10:])

r, t, lines = window("headroom", base="6100", extra='figures() { ev "figures $1"; echo 8100 > __T__/gpu_now; }\n')
check("E5 headroom on the GPU read just before each load (review F2): the window's base is 6,100 (zer would pass on "
      "it: 12,620), the GPU reads 8,100 before zer's load (8,100 + 6,220 + 300 = 14,620): zer is never loaded, the "
      "window stops and restores (exit 1)", r.returncode == 1 and ordered(lines, [
          "gte: headroom 6100 + 1563 + 300 < 14255; a slot free", "EVENT figures gte",
          "STOP: zer: the GPU now 8100 + its rise 6220 + 300 reaches the budget 14255: not loaded",
          "EVENT restore"]) and not any("EVENT start zer" in x for x in lines), lines[-10:])
r, t, lines = window("emptybase", base="")
check("E5b an empty base reading is a failed check, not 0 (review F2): stopped before any load, restored (exit 1)",
      r.returncode == 1 and ordered(lines, ["STOP: the base GPU reading is not a number ('')", "EVENT restore"])
      and not any("EVENT start" in x for x in lines), lines[-8:])
r, t, lines = window("emptyload", extra='slots_free() { : > __T__/gpu_now; echo 1; }\n')
check("E5c an empty reading just before the load: gte not loaded, restored (exit 1)",
      r.returncode == 1 and ordered(lines, ["STOP: gte: the GPU reading before the load is not a number ('')",
                                            "EVENT restore"]) and not any("EVENT start" in x for x in lines),
      lines[-8:])
r, t, lines = window("noslot", extra='slots_free() { local n; n=$(cat __T__/sc 2>/dev/null || echo 0); '
                                       'echo $((n + 1)) > __T__/sc; [ "$n" = 0 ] && echo 1 || echo 0; }\n')
check("E5d a slot free after the live stop but taken before the load (checked again there, review F2): gte not "
      "loaded, restored (exit 1)", r.returncode == 1 and ordered(lines, [
          "STOP: gte: no GPU reranker slot free (slots 0-1): not loaded", "EVENT restore"])
      and not any("EVENT start" in x for x in lines), lines[-8:])

STUCK = ('stop_group() { ev "stop group $1"; cp __T__/gpu_after_stop __T__/gpu_now; [ "$1" != -101 ]; }\n'
         'stuck_hold() { ev "stuck hold"; }\n')
r, t, lines = window("stuck", extra=STUCK)
check("E5e a trial service that survives SIGKILL (review F3): the window stops, does NOT restore beside it, says so, "
      "keeps the hold rewritten (exit 1)", r.returncode == 1 and ordered(lines, [
          "EVENT stop group -101", "STOP: the trial service's group 101 survived SIGKILL",
          "NOT RESTORED: the trial service's group 101 survived SIGKILL", "EVENT stuck hold",
          "the E4 window ends (exit 1)"]) and not any(x in ("EVENT restore", "EVENT hold released") for x in lines)
      and not any("EVENT start zer" in x for x in lines), lines[-10:])
check("E5f the restore's gov calls run in their own session with INT, TERM and PIPE back to their defaults (so the "
      "live service does not inherit the cleanup's ignores)",
      WINDOW.read_text().count("setsid -w env --default-signal=INT,TERM,PIPE ~/.local/bin/gov retrieve") == 2)

r, t, lines = window("routes", files=("routes-grow-gte",))
check("E6 the trial runs asked the routes anew (875 -> 900): the window stops before zer, restores (exit 1)",
      r.returncode == 1 and ordered(lines, ["route answers 875 -> 900", "STOP: gte: the trial runs asked the routes "
                                            "anew", "EVENT restore"]), lines[-10:])

r, t, lines = window("term", files=("term-gte-r80",))
check("E6b a TERM during gte's r80: the trap stops the measure's group, then the service's, restores, releases the "
      "hold (exit 143)", r.returncode == 143 and ordered(lines, [
          "EVENT measure gte r80", "EVENT stop group -202", "EVENT stop group -101", "EVENT restore",
          "EVENT hold released", "the E4 window ends (exit 143)"]), lines[-10:])

r, t, lines = window("dry", dry=True)
check("E6c DRY=1: the conditions and the plan, then nothing stopped, started, held or restored (exit 0)",
      r.returncode == 0 and any("DRY: 0 condition(s) not met; nothing stopped or started" in x for x in lines)
      and any(x.startswith("plan gte:") for x in lines) and any(x.startswith("plan zer:") for x in lines)
      and not any(x in y for y in lines for x in ("EVENT live stopped", "EVENT hold", "EVENT start", "EVENT restore",
                                                   "EVENT measure")), lines)
check("E6d DRY=1 writes no window folder", not (t / "runs/e4/window").exists())

DIES = "#!/usr/bin/env bash\necho \"start $$ $(date +%s.%N) $*\" >> __T__/backstop.log\nexit 2\n"
r, t, lines = window("bs-dies", models=("gte",), backstop=DIES)
check("E7 the real arm with a backstop that exits at once: the window stops at gte's first arm, before any measure; "
      "the trap stops the service and restores (exit 1)", r.returncode == 1 and ordered(lines, [
          "EVENT start gte", "did not stay up", "EVENT stop group -101", "EVENT restore",
          "the E4 window ends (exit 1)"]) and not any("EVENT measure" in x for x in lines), lines[-10:])
LIVES = ("#!/usr/bin/env bash\necho \"start $$ $(date +%s.%N) $*\" >> __T__/backstop.log\n"
         "trap 'echo \"stop $$ $(date +%s.%N)\" >> __T__/backstop.log; exit 0' TERM\n"
         "for i in $(seq 1 600); do sleep 0.1; done\n")
r, t, lines = window("bs-lives", models=("gte",), backstop=LIVES)
events = [x.split() for x in (t / "backstop.log").read_text().splitlines()] if (t / "backstop.log").exists() else []
starts = [(e[1], float(e[2])) for e in events if e[0] == "start"]
stops = {e[1]: float(e[2]) for e in events if e[0] == "stop"}
check("E7b the real arm with a backstop that stays up: five (the load, each measure and after it), each stopped by "
      "the end, each new one up before the old one stops", r.returncode == 0 and len(starts) == 5
      and all(p in stops for p, _ in starts)
      and all(starts[i][1] + 0.9 <= stops[starts[i - 1][0]] for i in range(1, len(starts))),
      (r.returncode, events, r.stdout[-600:]))

# G. review F1: the WHOLE process group signalled, or the caller's output closed. The copy runs in its own session
# (as `setsid bash e4_window.sh`); its trial service and measure are real stand-in processes (`setsid sleep`, their own
# sessions, as the real ones); stop_group kills a group for real. The window's log file is read, not its stdout.
REAL = r'''
start_svc() { ev "start $1"; setsid sleep 300 < /dev/null > /dev/null 2>&1 & SP=$!; SVC=-$SP; echo $SP >> __T__/svc.pids; arm "$MG" "$SP"; cp __T__/gpu_load __T__/gpu_now; }
measure() {
  ev "measure $1 $2"; setsid sleep ${MEASURE_S:-300} < /dev/null > /dev/null 2>&1 & MP=$!; echo $MP >> __T__/measure.pids
  arm "$MG" "$SP" "$MP"; touch __T__/in-measure; wait $MP; local rc=$?; MP=""
  echo $(( $(cat __T__/scores-$1) + 7 )) > __T__/scores-$1; return $rc
}
stop_group() { ev "stop group $1"; kill -KILL -- "$1" 2>/dev/null; cp __T__/gpu_after_stop __T__/gpu_now; return 0; }
'''


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    st = Path(f"/proc/{pid}/stat")
    return not (st.exists() and st.read_text().split(") ")[-1].startswith("Z"))


def window_group(name, sig=None, close=False, measure_s=300):
    t = made(name, extra=REAL + f"MEASURE_S={measure_s}\n")
    env = {**os.environ, "E4TEST_STUBS": str(t / "stubs.sh")}
    env.pop("DRY", None)
    p = subprocess.Popen(["bash", str(copy_with_stubs(WINDOW, t)), "gte"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, env=env, start_new_session=True)
    for _ in range(200):
        if (t / "in-measure").exists():
            break
        time.sleep(0.1)
    if sig is not None:
        os.killpg(p.pid, sig)
    if close:
        p.stdout.close()
    try:
        rc = p.wait(timeout=90)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        rc = None
    logs = list((t / "runs/e4/window").glob("*/window.log"))
    text = ""
    for _ in range(50):  # the tee writes the last lines just after the script ends
        text = logs[0].read_text() if logs else ""
        if "the E4 window ends" in text:
            break
        time.sleep(0.1)
    if not close:
        p.stdout.read()
        p.stdout.close()
    pids = [int(x) for f in ("svc.pids", "measure.pids") if (t / f).exists() for x in (t / f).read_text().split()]
    return rc, text.splitlines(), pids


for label, sig, code in (("TERM", signal.SIGTERM, 143), ("INT", signal.SIGINT, 130)):
    rc, lines, pids = window_group(f"group-{label}", sig=sig)
    check(f"G{1 if label == 'TERM' else 2} {label} to the window's WHOLE process group during gte's r80 (the L-0075 "
          f"form / Ctrl-C): the log shows the measure's and the service's groups stopped, the live service restored, "
          f"the hold released (exit {code}); no stand-in trial service or measure left",
          rc == code and ordered(lines, ["EVENT measure gte r80", "stopping the measure's group",
                                         "stopping the trial service", "EVENT restore", "EVENT hold released",
                                         f"the E4 window ends (exit {code})"])
          and len(pids) == 2 and not any(alive(p) for p in pids), (rc, lines[-10:], pids))
rc, lines, pids = window_group("closed", close=True, measure_s=2)
check("G3 the caller's output closed during gte's r80: the window goes on to its end in its log (r60, the stop, the "
      "checks, the restore, exit 0); no stand-in trial service or measure left",
      rc == 0 and ordered(lines, ["EVENT measure gte r80", "EVENT measure gte r60", "EVENT stop group",
                                  "EVENT lacking gte", "all models scored once", "EVENT restore",
                                  "EVENT hold released", "the E4 window ends (exit 0)"])
      and len(pids) == 3 and not any(alive(p) for p in pids), (rc, lines[-12:], pids))
rc, lines, pids = window_group("closed-term", sig=signal.SIGTERM, close=True)
check("G3b the output closed AND the group TERMed: still restored, nothing left (exit 143)",
      rc == 143 and ordered(lines, ["EVENT restore", "EVENT hold released", "the E4 window ends (exit 143)"])
      and not any(alive(p) for p in pids), (rc, lines[-8:], pids))

# ------------------------------------------------------------------------------------------------ the replays
R_STUBS = r'''
T=__T__
P=$T/runs; Q=$P/e4; QC=$Q/caches; CNT=$Q/count; E=$T/e0b
ev() { echo "EVENT $*"; }
conditions() { ev conditions; }
copy_own() { ev "copy own $1"; }
replay() {
  ev "replay $1 $2"; mkdir -p $P/e4
  local u=0 l=0; [ -e $T/unscored-$1-$2 ] && u=1; [ -e $T/live-$1-$2 ] && l=3
  echo "$1 $2: 10 s; median search 300 ms; unscored $u; texts cut at the request bound 0; texts cut by the model 0; combined passes 3; texts scored live (GOV_RX_LIVE_MISSING) $l; texts read from the replay's own cache 5" >> $P/e4/measure.log
  [ ! -e $T/fail-$1-$2 ]
}
figures() { ev "figures $1"; }
against_b() { ev "against $1"; }
'''


def replays(name, cells=(), files=(), dry=False):
    t = Path(mkd(prefix=f"e4r-{name}-"))
    (t / "stubs.sh").write_text(R_STUBS.replace("__T__", str(t)))
    for f in files:
        (t / f).write_text("")
    env = {**os.environ, "E4TEST_STUBS": str(t / "stubs.sh")}
    env.pop("DRY", None)
    if dry:
        env["DRY"] = "1"
    r = subprocess.run(["bash", str(copy_with_stubs(REPLAYS, t)), *cells], capture_output=True, text=True, env=env,
                       timeout=120)
    return r, t, r.stdout.splitlines()


shipped = REPLAYS.read_bytes()
copy = copy_with_stubs(REPLAYS, Path(mkd(prefix="e4r-seam-"))).read_bytes()
check("R0 the shipped replays script names no stubs; the tested copy less its stubs line is byte-identical",
      b"E4TEST_STUBS" not in shipped and shipped.decode().count(ANCHOR) == 1
      and copy.replace(STUB_LINE.encode(), b"", 1) == shipped)
r, t, lines = replays("pass")
check("R1 M3 then M1, each on a fresh own cache, r80 then r60, each read strict, then its figures and E0b B",
      r.returncode == 0 and ordered(lines, [
          "EVENT conditions", "EVENT copy own m3", "EVENT replay m3 r80", "m3 r80: 10 s", "EVENT replay m3 r60",
          "EVENT figures m3", "EVENT against m3", "EVENT copy own m1", "EVENT replay m1 r80", "EVENT replay m1 r60",
          "EVENT figures m1", "EVENT against m1", "E4 replays done"]), lines)
r, t, lines = replays("unscored", files=("unscored-m3-r60",))
check("R2 a replay with an unscored pass is not strict: stopped, M1 not run (exit 1)",
      r.returncode == 1 and any("STOP: m3 r60: not strict" in x for x in lines)
      and not any("replay m1" in x for x in lines), lines[-5:])
r, t, lines = replays("live", files=("live-m1-r80",))
check("R3 a replay that scored texts live is not strict: stopped (exit 1)",
      r.returncode == 1 and any("STOP: m1 r80: not strict" in x for x in lines), lines[-5:])
r, t, lines = replays("fail", files=("fail-m3-r80",))
check("R4 a replay that fails (a text lacking stops it) stops the script before its strictness read (exit 1)",
      r.returncode == 1 and any("STOP: m3 r80: the replay failed" in x for x in lines)
      and not any("replay m3 r60" in x for x in lines), lines[-5:])
r, t, lines = replays("dry", dry=True)
check("R5 DRY=1: the plan for m3 and m1, no replay, no log written", r.returncode == 0
      and any(x.startswith("plan m3 (E4 M3") for x in lines) and any(x.startswith("plan m1 (E4 M1") for x in lines)
      and any('"rule":{"kind":"merge","a":"zer","b":"gte"}' in x for x in lines)
      and any('"rule":{"kind":"merge","a":"q06","b":"gte"}' in x for x in lines)
      and not any("EVENT replay" in x for x in lines) and not (t / "runs").exists(), lines)


# ------------------------------------------------------------------------------------------------ the review pin
PINNED = ["rx.py", "so_measure.sh", "seed_scores.py", "rerank_worker.py", "e4_prep.sh", "e4_prepare.py",
          "e4_count.py", "e4_window.sh", "e4_replays.sh"]


def pin_case(script: Path, name: str, drop=None, change=None, absent=False):
    """Runs the script's own ``pinned`` (the stubs line, after every function, points S at a made folder, calls it
    and exits with its code)."""
    t = Path(mkd(prefix=f"e4pin-{name}-"))
    s = t / "s"
    s.mkdir()
    lines = []
    for f in PINNED:
        (s / f).write_text(f"stand-in {f}\n")
        if f != drop:
            lines.append(f"{hashlib.sha256((s / f).read_bytes()).hexdigest()}  {f}\n")
    if not absent:
        (s / "E4-REVIEWED.sha256").write_text("".join(lines))
    if change:
        (s / change).write_text("changed after the review\n")
    (t / "stubs.sh").write_text(f"S={s}\npinned; exit $?\n")
    env = {**os.environ, "E4TEST_STUBS": str(t / "stubs.sh")}
    env.pop("DRY", None)
    return subprocess.run(["bash", str(copy_with_stubs(script, t))], capture_output=True, text=True, env=env,
                          timeout=60).returncode


for script, tag in ((WINDOW, "window"), (REPLAYS, "replays")):
    check(f"PIN1 {tag}: all nine files pinned as they are: met", pin_case(script, "ok") == 0)
    check(f"PIN2 {tag}: a pin that leaves out e4_count.py: not met", pin_case(script, "drop", drop="e4_count.py") != 0)
    check(f"PIN3 {tag}: e4_window.sh changed after the review: not met",
          pin_case(script, "chg", change="e4_window.sh") != 0)
    check(f"PIN4 {tag}: no pin yet: not met", pin_case(script, "none", absent=True) != 0)


# ------------------------------------------------------------------------------------------------ e4_prepare.py
def key(*parts) -> str:
    return hashlib.sha256(repr(parts).encode()).hexdigest()


def clone_at(root: Path, head: str) -> Path:
    (root / ".gov-runtime").mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(root / ".gov-runtime/store.db")
    db.execute("DROP TABLE IF EXISTS fingerprints")
    db.execute("CREATE TABLE fingerprints (head TEXT, code TEXT, records TEXT, kind TEXT)")
    db.execute("INSERT INTO fingerprints VALUES (?, 'c', 'r', 'rebuild')", (head,))
    db.commit()
    db.close()
    return root


def cache(folder: Path, meta: dict, scores: dict = None, memo: dict = None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(folder / "cache.db")
    db.execute("CREATE TABLE memo (k TEXT PRIMARY KEY, v BLOB)")
    db.execute("CREATE TABLE score (k TEXT PRIMARY KEY, s REAL)")
    db.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    db.executemany("INSERT INTO meta VALUES (?, ?)", list(meta.items()))
    db.executemany("INSERT INTO score VALUES (?, ?)", list((scores or {}).items()))
    db.executemany("INSERT INTO memo VALUES (?, ?)", list((memo or {}).items()))
    db.commit()
    db.close()
    return folder


def refused(fn, *a):
    try:
        fn(*a)
    except SystemExit as e:
        return str(e)
    return None


tp = Path(mkd(prefix="e4p-"))
clone = clone_at(tp / "clone", "h1")
want = json.dumps([str(clone.resolve()), "h1"])
seed = cache(tp / "seed", {"rerank_model": GTE, "memo_keys": "store"}, {key("rr", GTE, "q", "a"): 0.5})
src = cache(tp / "a", {"memo_keys": "store", "store": want}, {key("rr", Q06, "q", "z"): 0.1},
            {"m1": b"x", "m2": b"y"})
rep = e4_prepare.routes(tp / "w", seed, src, clone)
w = sqlite3.connect(tp / "w/cache.db")
meta = dict(w.execute("SELECT k, v FROM meta").fetchall())
check("P1 routes: the seed's scores only (not the source's 0.6B score), the source's route answers, its store, the "
      "model mark", rep["scores"] == 1 and rep["routes"] == 2 and meta == {"rerank_model": GTE, "memo_keys": "store",
                                                                          "store": want}
      and w.execute("SELECT COUNT(*) FROM score WHERE k = ?", (key("rr", Q06, "q", "z"),)).fetchone()[0] == 0, rep)
check("P2 a folder that holds a cache already is refused", "exists: refused" in (refused(
    e4_prepare.routes, tp / "w", seed, src, clone) or ""))
clone_at(tp / "clone2", "h2")
check("P3 a routes cache filled for another store (the clone rebuilt: another head) is refused",
      "refused" in (refused(e4_prepare.routes, tp / "w3", seed, src, tp / "clone2") or ""))
bad_seed = cache(tp / "seedm", {"rerank_model": GTE, "memo_keys": "store"}, {}, {"m": b"x"})
check("P4 a seed holding route answers (not seed_scores.py's form) is refused",
      "not one model's scores alone" in (refused(e4_prepare.routes, tp / "w4", bad_seed, src, clone) or ""))
two = cache(tp / "seed2", {"rerank_model": GTE, "rerank_model2": Q06, "memo_keys": "store"})
check("P4b a seed marking two models is refused",
      "not one model's scores alone" in (refused(e4_prepare.routes, tp / "w5", two, src, clone) or ""))
legacy = cache(tp / "leg", {}, {}, {"m": b"x"})
check("P4c a routes cache keyed without its store is refused",
      "not keyed by their store" in (refused(e4_prepare.routes, tp / "w6", seed, legacy, clone) or ""))
ok, line = e4_prepare.check(tp / "w", clone, GTE, seed)
check("P5 check: the fresh window cache passes, with its seed (nothing scored into it yet)", ok, line)
w.execute("INSERT INTO score VALUES ('new', 0.2)")
w.commit()
ok_seed, line_seed = e4_prepare.check(tp / "w", clone, GTE, seed)
ok_plain, _ = e4_prepare.check(tp / "w", clone, GTE)
check("P6 after a score: not its seed's any more (named), still a valid window cache without the seed",
      not ok_seed and "1 scores beyond its seed's 1" in line_seed and ok_plain, line_seed)
ok, line = e4_prepare.check(tp / "w", clone, Q06)
check("P7 check names a wrong model", not ok and f"not {Q06}" in line, line)
ok, line = e4_prepare.check(tp / "w", tp / "clone2", GTE)
check("P8 check names another store", not ok and "not the clone's" in line, line)
k1 = cache(tp / "k1", {"rerank_model": GTE}, {key("rr", GTE, "q", "a"): 0.5, key("rr", GTE, "q", "b"): 0.6},
           {"g1-route": b"x"})
r = subprocess.run([sys.executable, str(HERE / "seed_scores.py"), str(tp / "s2"), str(k1)], capture_output=True,
                   text=True, timeout=60)
r2 = subprocess.run([sys.executable, str(HERE / "e4_prepare.py"), "routes", str(tp / "w7"), str(tp / "s2"), str(src),
                     str(clone)], capture_output=True, text=True, timeout=60)
r3 = subprocess.run([sys.executable, str(HERE / "e4_prepare.py"), "check", str(tp / "w7"), str(clone), GTE,
                     str(tp / "s2")], capture_output=True, text=True, timeout=60)
check("P9 end to end: seed_scores.py (the kept cache's g1 route answer dropped), then routes, then check: 2 scores, "
      "E0b's 2 route answers", r.returncode == 0 and r2.returncode == 0 and r3.returncode == 0
      and "2 scores, 2 route answers" in r3.stdout, (r.stdout, r2.stdout + r2.stderr, r3.stdout))


# ------------------------------------------------------------------------------------------------ e4_count.py
tc = Path(mkd(prefix="e4c-"))
gte_cache = cache(tc / "gte", {"rerank_model": GTE}, {key("rr", GTE, "q", "a"): 0.5})
fake = types.SimpleNamespace(COMBINE={"rule": {}}, LIVE_MISSING=False, TRIAL=None, LIVE=None, _key=key,
                             scores=lambda q, texts: [0.25] * len(texts))
e4_count.install(fake, {"gte": {"model": GTE, "caches": [str(gte_cache)]}}, tc / "out")
got = fake.scores("q", ["a", "b", "b"])
need = (tc / "out/need-gte.txt").read_text().split()
lack = (tc / "out/lack-gte.txt").read_text().split()
check("C1 the wrapped scores return rx.py's own scores unchanged; every key asked written, the lacking ones apart",
      got == [0.25] * 3 and need == [key("rr", GTE, "q", t) for t in ("a", "b", "b")]
      and lack == [key("rr", GTE, "q", "b")] * 2, (got, len(need), len(lack)))
check("C2 the summary counts distinct texts: 2 asked, 1 lacking",
      e4_count.summary(tc / "out") == {"gte": {"asked": 2, "lacking": 1}}, e4_count.summary(tc / "out"))
for label, attrs in (("no replay", {"COMBINE": None}), ("GOV_RX_LIVE_MISSING", {"LIVE_MISSING": True}),
                     ("a trial socket", {"TRIAL": "/x"}), ("the live two-model mode", {"LIVE": {"rule": {}}})):
    f = types.SimpleNamespace(**{**vars(fake), **attrs, "scores": lambda q, t: []})
    check(f"C3 refused: {label} (the count calls no reranker)", refused(
        e4_count.install, f, {"gte": {"model": GTE, "caches": [str(gte_cache)]}}, tc / "o2") is not None)
check("C3b refused: a spec with no cache, and a missing cache",
      refused(e4_count.install, types.SimpleNamespace(**vars(fake)), {"gte": {"model": GTE, "caches": []}}, tc / "o3")
      and refused(e4_count.install, types.SimpleNamespace(**vars(fake)),
                  {"gte": {"model": GTE, "caches": [str(tc / "none")]}}, tc / "o4"))
check("C4 check: 1 of 2 still lacking in the seed; 0 once the window cache holds b",
      e4_count.check(tc / "out", "gte", [gte_cache]) == (2, 1))
both = cache(tc / "gte-w", {"rerank_model": GTE}, {key("rr", GTE, "q", "b"): 0.7})
r = subprocess.run([sys.executable, str(HERE / "e4_count.py"), "--check", str(tc / "out"), "gte", str(gte_cache),
                    str(both)], capture_output=True, text=True, timeout=60)
r1 = subprocess.run([sys.executable, str(HERE / "e4_count.py"), "--check", str(tc / "out"), "gte", str(gte_cache)],
                    capture_output=True, text=True, timeout=60)
check("C4b --check exits 0 with nothing lacking, 1 with one, its line of counts",
      r.returncode == 0 and "2 distinct texts needed" in r.stdout and "0 lacking" in r.stdout
      and r1.returncode == 1 and "1 lacking" in r1.stdout, (r.stdout, r1.stdout))

# C5: the real rx.py in a strict replay (so_measure.sh's form: system python3, the clone's gov on PYTHONPATH)
if (CLONE_SRC / "gov/retrieval/rerank.py").is_file():
    t5 = Path(mkd(prefix="e4c5-"))
    q06c = cache(t5 / "q06", {"rerank_model": Q06, "memo_keys": "store"},
                 {key("rr", Q06, "q", "a"): 0.9, key("rr", Q06, "q", "b"): 0.1})
    gc = cache(t5 / "gte", {"rerank_model": GTE, "memo_keys": "store"}, {key("rr", GTE, "q", "a"): 0.4})
    prog = ("import importlib.util, json, os, sys\n"
            f"sys.path.insert(0, {str(HERE)!r})\n"
            "import e4_count\n"
            f"spec = importlib.util.spec_from_file_location('rx', {str(HERE / 'rx.py')!r})\n"
            "rx = importlib.util.module_from_spec(spec); spec.loader.exec_module(rx)\n"
            f"e4_count.install(rx, json.loads(os.environ['E4_COUNT']), {str(t5 / 'out')!r})\n"
            "print(json.dumps([rx.scores('q', ['a', 'b']), rx._fusion.__globals__['scores'] is rx.scores,"
            " rx.scores.__name__]))\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GOV_", "E4_")) and k != "PYTHONPATH"}
    env.update({"HOME": str(t5), "PYTHONPATH": str(CLONE_SRC), "GOV_RX_NO_MAIN": "1", "GOV_RX_CACHE": str(t5 / "own"),
                "GOV_RX_COMBINE": json.dumps({"models": {"q06": Q06}, "caches": {"q06": str(q06c)},
                                              "rule": {"kind": "alone", "m": "q06"}}),
                "E4_COUNT": json.dumps({"gte": {"model": GTE, "caches": [str(gc)]}})})
    r = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, env=env, timeout=120)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        out = None
    check("C5 the real rx.py: the replay's own 0.6B scores returned, the search's own lookup goes through the wrapper "
          "(rx._fusion's globals), gte's lacking text counted", out == [[0.9, 0.1], True, "counted"]
          and e4_count.summary(t5 / "out") == {"gte": {"asked": 2, "lacking": 1}}, (out, r.stderr[-800:]))
    env2 = {**env, "GOV_RX_LIVE_MISSING": "1"}
    r = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True, env=env2, timeout=120)
    check("C5b the real rx.py with GOV_RX_LIVE_MISSING=1: the count refuses (it calls no reranker)",
          r.returncode != 0 and "the count calls no reranker" in r.stderr, r.stderr[-400:])
else:
    print("skip C5, C5b: window 4's clone is not on this machine")

print(f"{sum(results)} of {len(results)} passed")
if all(results):
    shutil.rmtree(ROOT, ignore_errors=True)
else:
    print(f"temporary folders kept for a look: {ROOT}")
sys.exit(0 if all(results) else 1)
