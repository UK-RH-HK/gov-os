#!/usr/bin/env python3
"""Normalised failure/panic messages of an R1 held-out run output (paths, thread ids, hex digests and 3+-digit
integers normalised) so two runs of the same unedited suites can be compared line by line.
Usage: failure_messages.py <run.out>"""
import re, sys
txt = open(sys.argv[1]).read()
out = []
for m in re.finditer(r"^---- (\S+) stdout ----\n(.*?)(?=^---- |\nfailures:\n|\Z)", txt, flags=re.M | re.S):
    name, body = m.group(1), m.group(2)
    for line in body.splitlines():
        if not line.strip() or line.startswith("note: run with"):
            continue
        line = re.sub(r"/tmp/[^\s\"':,)]+", "<PATH>", line)
        line = re.sub(r"\(\d+\)", "(<TID>)", line)
        line = re.sub(r"\b[0-9a-f]{16,}\b", "<HEX>", line)
        line = re.sub(r"\b\d{3,}\b", "<N>", line)
        out.append(f"{name}: {line}")
print("\n".join(sorted(set(out))))
