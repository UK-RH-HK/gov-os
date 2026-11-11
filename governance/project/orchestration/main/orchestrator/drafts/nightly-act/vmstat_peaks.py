"""Reads D-10's vmstat logs (30 s samples) and prints, per run and phase, the baseline and the peak of memory in use
(MemTotal - free - buff - cache), swap, and the lowest free+cache. Reads only. Usage: vmstat_peaks.py <vmstat.log> <split time or ->"""
import sys

TOTAL_KB = 24607392


def main(path, split):
    rows = []
    for line in open(path):
        p = line.split()
        if len(p) < 19 or not p[0].isdigit():
            continue
        free, buff, cache = int(p[3]), int(p[4]), int(p[5])
        rows.append((p[-2] + " " + p[-1], TOTAL_KB - free - buff - cache, int(p[2]), int(p[0]), free + cache + buff, int(p[6]) + int(p[7])))
    parts = [("all", rows)]
    if split != "-":
        parts = [("before " + split, [r for r in rows if r[0] < split]), ("after " + split, [r for r in rows if r[0] >= split])]
    for name, rs in parts:
        if not rs:
            continue
        base = rs[0][1]
        peak = max(rs, key=lambda r: r[1])
        print(f"{name}: samples {len(rs)}; first in-use {base / 1048576:.2f} GB; peak in-use {peak[1] / 1048576:.2f} GB at {peak[0]}; "
              f"rise {(peak[1] - base) / 1048576:.2f} GB; max swap {max(r[2] for r in rs) / 1024:.0f} MB; "
              f"max runnable {max(r[3] for r in rs)}; min free+buff+cache {min(r[4] for r in rs) / 1048576:.2f} GB; "
              f"max si+so {max(r[5] for r in rs)} KB/s")


main(sys.argv[1], sys.argv[2])
