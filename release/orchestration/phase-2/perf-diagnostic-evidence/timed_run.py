#!/usr/bin/env python3
"""Deterministic instrumentation for the Governance OS certification suite (run P2-PERF-0001).

Runs a command, timestamping each stdout line as it arrives, and records:
  * wall clock (monotonic)
  * total CPU (user+sys) of the child AND every subprocess it reaped -- via os.wait4.
    The libtest harness spawns `gov` and `git` as children; when they are reaped their
    CPU is folded into the figure wait4 reports, so this measures subprocess CPU too.
  * per-test durations, derived from line arrival deltas. Sound ONLY for --test-threads=1,
    where libtest emits one completion line per test in order. Marked in the metadata.
  * load average before and after.

No shell pipe is used anywhere: the exit status comes straight from wait4, so a red suite
cannot be reported green by a pipeline swallowing the status.
"""
import json
import os
import re
import subprocess
import sys
import time

TEST_LINE = re.compile(r"^test (\S+) \.\.\. (ok|FAILED|ignored)")
RUNNING = re.compile(r"^running (\d+) test")
RESULT = re.compile(r"^test result: (\w+)\.\s*(\d+) passed;\s*(\d+) failed;\s*(\d+) ignored")


def loadavg():
    with open("/proc/loadavg") as f:
        return f.read().strip()


def main():
    label = sys.argv[1]
    outdir = sys.argv[2]
    serial = sys.argv[3] == "serial"
    cmd = sys.argv[4:]
    os.makedirs(outdir, exist_ok=True)

    load_before = loadavg()
    t_start = time.monotonic()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )

    timed = []          # (offset, line)
    for line in p.stdout:
        timed.append((time.monotonic() - t_start, line.rstrip("\n")))
    p.stdout.close()

    # wait4 gives the exit status AND rusage including reaped grandchildren (gov/git).
    _pid, status, ru = os.wait4(p.pid, 0)
    wall = time.monotonic() - t_start
    load_after = loadavg()
    rc = os.waitstatus_to_exitcode(status)

    # ---- derive per-test durations -------------------------------------------------
    tests = []
    prev = None
    declared = None
    result = None
    for off, line in timed:
        m = RUNNING.match(line)
        if m:
            declared = int(m.group(1))
            prev = off
            continue
        m = RESULT.match(line)
        if m:
            result = {
                "verdict": m.group(1), "passed": int(m.group(2)),
                "failed": int(m.group(3)), "ignored": int(m.group(4)),
            }
            continue
        m = TEST_LINE.match(line)
        if m and prev is not None:
            tests.append({"test": m.group(1), "outcome": m.group(2),
                          "duration_s": round(off - prev, 3),
                          "completed_at_s": round(off, 3)})
            prev = off

    with open(f"{outdir}/{label}.raw.txt", "w") as f:
        f.write("\n".join(l for _, l in timed) + "\n")
    with open(f"{outdir}/{label}.timed.tsv", "w") as f:
        for off, line in timed:
            f.write(f"{off:.3f}\t{line}\n")
    with open(f"{outdir}/{label}.tests.tsv", "w") as f:
        f.write("duration_s\toutcome\ttest\n")
        for t in sorted(tests, key=lambda x: -x["duration_s"]):
            f.write(f"{t['duration_s']}\t{t['outcome']}\t{t['test']}\n")

    cpu_user, cpu_sys = ru.ru_utime, ru.ru_stime
    meta = {
        "label": label, "cmd": cmd, "started_at_utc": started_at,
        "exit_code": rc,
        "wall_s": round(wall, 3),
        "cpu_user_s": round(cpu_user, 3), "cpu_sys_s": round(cpu_sys, 3),
        "cpu_total_s": round(cpu_user + cpu_sys, 3),
        "cpu_per_wall": round((cpu_user + cpu_sys) / wall, 3) if wall else None,
        "max_rss_kb": ru.ru_maxrss,
        "involuntary_ctx_switches": ru.ru_nivcsw,
        "voluntary_ctx_switches": ru.ru_nvcsw,
        "block_input_ops": ru.ru_inblock, "block_output_ops": ru.ru_oublock,
        "load_before": load_before, "load_after": load_after,
        "declared_tests": declared, "result": result,
        "per_test_timing_sound": serial,
        "n_test_lines": len(tests),
        "sum_test_durations_s": round(sum(t["duration_s"] for t in tests), 3),
    }
    with open(f"{outdir}/{label}.meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))
    # Propagate failure loudly: a non-zero child status must not look like success.
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
