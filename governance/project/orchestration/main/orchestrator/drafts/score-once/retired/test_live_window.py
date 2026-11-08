"""Tests of live_window.sh's control flow and of live_verdict.py, on stand-ins. live_window.sh holds no test seam:
each case runs a temporary copy with one line added (``. "$LW_STUBS"``, before the OUT line), which sources a stubs
file replacing the GPU reads, the samplers, the services, the warm-up, the probe, the searches, the stops, the hold
and the live service (no GPU, no service, no real folder written); W0 checks the copy less that line is the shipped
file byte for byte. W4 and W5 keep the real ``arm`` and ``disarm`` with a stand-in backstop. Then live_verdict.py
alone on made folders.

    python3 test_live_window.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOW, VERDICT = HERE / "live_window.sh", HERE / "live_verdict.py"
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + str(detail) if detail and not ok else ''}")


STUBS = r'''
T=__T__
P=$T/runs; TR=$T/tr; RUN1=$TR/run; RUN2=$TR/run2
BASE_TRIES=1; BASE_EVERY=0; WARM_SETTLE_S=0
ev() { echo "EVENT $*"; }
gpu() { cat $T/gpu_now; }
gpu_total() { echo 16303; }
warm() { :; }
start_sampler() { ev "sampler start $(basename "$1")"; tr ' ' '\n' < $T/samples-$(basename "$1") > "$1"; printf -v "$2" %s stub; }
stop_sampler() { [ -n "${!1}" ] && ev "sampler stop $1"; printf -v "$1" %s ""; }
restore() { ev restore; }
take_hold() { HELD=1; ev hold; }
release_hold() { [ "$HELD" = 1 ] && ev "hold released"; HELD=0; }
stop_live() { LIVE_STOPPED=1; ev "live stopped"; }
stop_group() { ev "stop group $1"; cp $T/gpu_after_stop $T/gpu_now; }
__ARM__
conditions() { ev conditions; }
embedders() { ev embedders; }
slots_after_stop() { ev slots; }
req() { echo "{\"trial\": \"request\", \"texts\": 1, \"padded_chars\": 50, \"seconds\": $2, \"peak_reserved_mib\": $3, \"reserved_after_mib\": $4}" >> "$1/service.log"; }
start_svc() {
  local k=$1 dir=$3 d=$4
  mkdir -p "$dir"; touch "$dir/service.log"; echo "library noise" >> "$dir/service.log"
  wc -l < "$dir/service.log" > "$d/service-$k.from"
  ev "start $k $2"
  if [ "$k" = one ]; then SP1=101; SVC1=-101; else SP2=102; SVC2=-102; fi
  arm "$MG" $SP2 $SP1
  cp $T/gpu_raw $T/gpu_now
}
warm_svc() { ev "warm $1"; req "$(dirname "$1")" 0.01 900 800; cp $T/gpu_warm $T/gpu_now; echo "warm-up: ok in 0.01 s"; }
probe_svc() {
  ev "probe $1 $2 $3"
  if [ "$(dirname "$1")" = "$RUN1" ]; then req "$RUN1" 1.5 3300 800; else req "$RUN2" 0.4 1500 700; fi
  echo "1x$2: ok"
}
searches() { ev "searches $1 $2"; arm "$MG" "$SP2" "$SP1"; mkdir -p "$3/$1"; cp $T/summary-$1.json "$3/$1/summary-$1.json"; echo "summary $1" > "$3/$1.txt"; }
'''
STUB_ARM = 'arm() { ev "arm $*"; }\ndisarm() { BS=""; }'
# W4, W5: the real arm and disarm, with the tools folder pointed at a stand-in backstop and a copy of proc.sh
REAL_ARM = "O=$T/orch"
ANCHOR = 'if [ "${DRY:-0}" != 1 ]; then OUT='
STUB_LINE = '. "$LW_STUBS"\n'
SHIPPED = WINDOW.read_bytes()


def copy_with_stubs(t: Path) -> Path:
    """The shipped window with the one stubs line before its OUT line."""
    text = SHIPPED.decode()
    at = text.index(ANCHOR)
    path = t / "live_window.copy.sh"
    path.write_text(text[:at] + STUB_LINE + text[at:])
    return path


def summary(mode, median=2.0, failed=0, unranked=0, timeouts=0):
    return {"mode": mode, "median_s": median, "p90_s": median + 0.5, "slowest_s": median + 1, "failed": failed,
            "unranked": unranked, "timeouts": timeouts, "median_less_gpu_reads_s": median - 0.3,
            "slowest_request_s": 1.2}


def window(name, alone, once, gpu_after_stop, cells=("M2", "M3"), extra="", backstop=None):
    """Runs the copy on stand-ins; ``backstop``: None (arm stubbed), or the body of a stand-in gpu_backstop.sh run
    by the real arm."""
    t = Path(tempfile.mkdtemp(prefix=f"lw-{name}-"))
    if backstop is not None:
        tools = t / "orch/tools"
        tools.mkdir(parents=True)
        (tools / "gpu_backstop.sh").write_text(backstop.replace("__T__", str(t)))
        (tools / "proc.sh").write_bytes((HERE.parent.parent / "tools/proc.sh").read_bytes())
    arm = REAL_ARM if backstop is not None else STUB_ARM
    (t / "stubs.sh").write_text(STUBS.replace("__T__", str(t)).replace("__ARM__", arm) + extra)
    for f, v in {"gpu_now": "6100", "gpu_raw": "11800", "gpu_warm": "11550", "gpu_after_stop": gpu_after_stop,
                 "samples-gpu-load.txt": "7000 11800 15000", "samples-gpu.txt": "11550 12900 13100 11600"}.items():
        (t / f).write_text(v)
    (t / "summary-alone.json").write_text(json.dumps(alone))
    (t / "summary-once.json").write_text(json.dumps(once))
    env = {**os.environ, "LW_STUBS": str(t / "stubs.sh")}
    env.pop("DRY", None)
    r = subprocess.run(["bash", str(copy_with_stubs(t)), *cells], capture_output=True, text=True, env=env,
                       timeout=180)
    outs = list((t / "runs/live-window").glob("*"))
    return r, t, (outs[0] if outs else None)


def at(lines, text, after=-1):
    for i, line in enumerate(lines):
        if i > after and text in line:
            return i
    return None


def ordered(lines, texts):
    """True when each text is found after the one before it."""
    pos = -1
    for text in texts:
        pos = at(lines, text, pos)
        if pos is None:
            return False
    return True


# W0. the shipped file has no seam; the tested copy is it plus the one stubs line, byte for byte
t0 = Path(tempfile.mkdtemp(prefix="lw-seam-"))
copy = copy_with_stubs(t0).read_bytes()
shipped = SHIPPED.decode()
check("W0 the shipped window names no stubs, LW_TEST or LW_STUBS, and its OUT line is there once",
      b"LW_STUBS" not in SHIPPED and b"LW_TEST" not in SHIPPED and shipped.count(ANCHOR) == 1)
check("W0b the tested copy less its one stubs line is byte-identical to live_window.sh",
      copy.count(STUB_LINE.encode()) == 1 and copy.replace(STUB_LINE.encode(), b"", 1) == SHIPPED)

# W1. a clean window: the warm-up order, the readings, the judged window, both cells judged
r, t, out = window("pass", summary("alone"), summary("once"), "6200")
lines = r.stdout.splitlines()
check("W1 the window runs to its end on stand-ins (exit 0)", r.returncode == 0 and out is not None,
      r.stdout[-800:] + r.stderr[-400:])
check("W1b the order: load sampler, two then one, the raw reading, the warm-ups, the warm reading, then the judged "
      "sampler, the probes, the searches", ordered(lines, [
          "EVENT sampler start gpu-load.txt", "EVENT start two gte", "EVENT start one q4b",
          "GPU after both loads, before the warm-up: 11800", f"EVENT warm {t}/tr/run/rerank.sock",
          f"EVENT warm {t}/tr/run2/rerank.sock", "GPU after the warm-up (the steady state): 11550",
          "EVENT sampler stop LOADSAMP", "EVENT sampler start gpu.txt", "EVENT probe", "EVENT probe",
          "EVENT searches alone 20", "EVENT searches once 10", "EVENT sampler stop SAMP", "EVENT stop group -101"]),
      lines)
d = out / "M2" if out else Path("/nonexistent")
check("W1c both readings kept: gpu-after-loads-raw 11800, gpu-after-warmup 11550",
      (d / "gpu-after-loads-raw.txt").exists() and (d / "gpu-after-loads-raw.txt").read_text().strip() == "11800"
      and (d / "gpu-after-warmup.txt").read_text().strip() == "11550")
check("W1d the 4B probed at its bound (12000, 8), gte at 24000, 16", any("rerank.sock 12000 8" in x for x in lines)
      and any("run2/rerank.sock 24000 16" in x for x in lines), [x for x in lines if "EVENT probe" in x])
v = json.loads((d / "verdict.json").read_text()) if (d / "verdict.json").exists() else {}
check("W1e the load peak (15,000) is reported, not judged: the cell is eligible on the judged samples (peak 13,100)",
      v.get("eligible") is True and v["gpu"]["load_peak"] == 15000 and v["gpu"]["judged_peak"] == 13100, v.get("gpu"))
check("W1f the derived bound: after the warm-up 11,550 + one's rise 2,500 + two's rise 800 = 14,850, reported",
      v.get("gpu", {}).get("derived_bound") == 14850 and v["services"]["one"]["rise_mib"] == 2500
      and v["services"]["two"]["rise_mib"] == 800 and any("derived bound 11550 + 2500 + 800 = 14850 MiB" in x
                                                          for x in lines), v.get("services"))
check("W1g M3 judged too, on its own service-log lines only (its 2 requests, not M2's 4 in the same log)",
      (out / "M3/verdict.json").exists() and json.loads((out / "M3/verdict.json").read_text())["services"]["one"][
          "requests"] == 2, (out / "M3").exists() if out else None)
check("W1h the verdicts before the restore, the hold released last",
      ordered(lines, ["M2: ELIGIBLE", "M3: ELIGIBLE", "EVENT restore", "EVENT hold released",
                      "the live window ends (exit 0)"]), lines[-12:])

# W2. a mid-window stop (the GPU does not return to the base after M2): M2 is judged by the trap, M3 never started;
# M2's alone searches had failures, so its speed line is not met even with a 2.0 s median
r, t, out = window("stop", summary("alone", failed=2), summary("once"), "9000")
lines = r.stdout.splitlines()
d = out / "M2" if out else Path("/nonexistent")
v = json.loads((d / "verdict.json").read_text()) if (d / "verdict.json").exists() else {}
check("W2 the window stops at the return to base after M2 (exit 1)", r.returncode == 1
      and any("STOP: the GPU did not return to the base after M2" in x for x in lines), lines[-10:])
check("W2b M2's verdict written on that stop, before the restore; M3 not started",
      v.get("cell") == "M2" and ordered(lines, ["STOP: the GPU did not return", "M2 NOT MET", "M2: NOT ELIGIBLE",
                                                "M3: not started, not judged", "EVENT restore"])
      and not (out / "M3").exists(), lines[-14:])
check("W2c the alone line not met with a 2.0 s median and 2 failed searches", v.get("lines")
      and v["lines"][0][1] is False and "failed 2" in v["lines"][0][2] and v["lines"][1][1] is True, v.get("lines"))

# W3. a stop inside a cell (the searches killed: no summary): the verdict says not measured
EXTRA = '\nsearches() { ev "searches $1"; return 1; }\nend_cell() { stop "stand-in stop inside $1"; }\n'
r, t, out = window("mid", summary("alone"), summary("once"), "6200", cells=("M2",), extra=EXTRA)
d = out / "M2" if out else Path("/nonexistent")
v = json.loads((d / "verdict.json").read_text()) if (d / "verdict.json").exists() else {}
check("W3 a stop inside a cell: the trap still marks the service logs and judges it (alone not measured)",
      r.returncode == 1 and v.get("eligible") is False and v.get("lines") and v["lines"][0][2] == "not measured"
      and (d / "service-one.to").exists() and any("EVENT stop group -101" in x for x in r.stdout.splitlines()),
      r.stdout[-600:])

# W4. the real arm with a backstop that exits at once (a bad argument): the window stops loudly at the first arm,
# the trap judges and restores
DIES = "#!/usr/bin/env bash\necho \"start $$ $(date +%s.%N) $*\" >> __T__/backstop.log\nexit 2\n"
r, t, out = window("bs-dies", summary("alone"), summary("once"), "6200", cells=("M2",), backstop=DIES)
lines = r.stdout.splitlines()
check("W4 a backstop that exits at once stops the window at the first arm, before any warm-up or search",
      r.returncode == 1 and any("STOP: the backstop on groups" in x and "did not stay up" in x for x in lines)
      and not any("EVENT warm" in x or "EVENT searches" in x or "EVENT start one" in x for x in lines), lines[-12:])
check("W4b ... then the trap: the service stopped, the cell judged, the live service restored",
      ordered(lines, ["did not stay up", "EVENT stop group -102", "M2: NOT ELIGIBLE", "EVENT restore",
                      "the live window ends (exit 1)"]), lines[-12:])

# W5. the real arm with a backstop that stays up: each new one alive before the old one stops; none left at the end
LIVES = ("#!/usr/bin/env bash\necho \"start $$ $(date +%s.%N) $*\" >> __T__/backstop.log\n"
         "trap 'echo \"stop $$ $(date +%s.%N)\" >> __T__/backstop.log; exit 0' TERM\n"
         "for i in $(seq 1 600); do sleep 0.1; done\n")
r, t, out = window("bs-lives", summary("alone"), summary("once"), "6200", cells=("M2",), backstop=LIVES)
events = [x.split() for x in (t / "backstop.log").read_text().splitlines()] if (t / "backstop.log").exists() else []
starts = [(e[1], float(e[2])) for e in events if e[0] == "start"]
stops = {e[1]: float(e[2]) for e in events if e[0] == "stop"}
check("W5 four backstops (two loads, two measures), each stopped by the end", r.returncode == 0 and len(starts) == 4
      and all(p in stops for p, _ in starts), (r.returncode, events, r.stdout[-500:]))
check("W5b each new backstop up (and checked a second later) before the old one stops",
      len(starts) == 4 and all(starts[i][1] + 0.9 <= stops[starts[i - 1][0]] for i in range(1, 4)), events)
check("W5c the first backstop on the script's group and two's, the second adds one's",
      len(events) >= 2 and events[0][3:] == [events[0][3], "102"] and events[1 if events[1][0] == "start" else 2][3:]
      == [events[0][3], "102", "101"], events[:4])

# V. live_verdict.py alone: the speed line's rule
def verdict_of(alone, once=summary("once")):
    t = Path(tempfile.mkdtemp(prefix="lv-"))
    d = t / "M2"
    (d / "alone").mkdir(parents=True)
    (d / "once").mkdir()
    if alone is not None:
        (d / "alone/summary-alone.json").write_text(json.dumps(alone))
    (d / "once/summary-once.json").write_text(json.dumps(once))
    for k in ("one", "two"):
        (d / f"probe-{k}.rc").write_text("0")
    (d / "gpu.txt").write_text("12000\n13000\n")
    r = subprocess.run([sys.executable, str(VERDICT), str(t), "14255", str(t / "none1"), str(t / "none2"), "M2"],
                       capture_output=True, text=True, timeout=60)
    return json.loads((d / "verdict.json").read_text()), r


cases = [("V1 median 3.0, none failed or unranked: met", summary("alone", 3.0), True),
         ("V2 median 3.01: not met", summary("alone", 3.01), False),
         ("V3 median 1.0 but one failed: not met", summary("alone", 1.0, failed=1), False),
         ("V4 median 1.0 but one unranked: not met", summary("alone", 1.0, unranked=1), False),
         ("V5 no summary: not measured, not met", None, False)]
for name, alone, want in cases:
    v, r = verdict_of(alone)
    check(name, v["lines"][0][1] is want, (v["lines"][0], r.stderr[-200:]))
v, _ = verdict_of(summary("alone", 2.9))
check("V6 the speed line is judged on the full median (2.9), the less-GPU-reads figure (2.6) only reported",
      v["lines"][0][1] is True and "median 2.90 s (the harness's GPU reads included)" in v["lines"][0][2]
      and "reported only: less the GPU reads 2.60 s" in v["lines"][0][2], v["lines"][0])
v, _ = verdict_of(summary("alone"), summary("once", timeouts=1))
check("V7 10 at once: a request timed out: not met", v["lines"][1][1] is False and v["eligible"] is False)

print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
