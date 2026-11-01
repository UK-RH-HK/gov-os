"""Write the probe record between the reviewer's BEGIN/END markers to the given path.
Usage: extract_probe.py <log json> <out path>"""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
last = None
for line in text.splitlines():
    if line.strip().startswith("{"):
        try:
            last = json.loads(line)
        except ValueError:
            pass
result = last["result"]
start = result.index("--- PROBE RECORD BEGIN ---") + len("--- PROBE RECORD BEGIN ---")
end = result.index("--- PROBE RECORD END ---")
record = result[start:end].strip("\n") + "\n"
assert record.startswith("---\ntype: probe\n"), record[:80]
open(sys.argv[2], "w", encoding="utf-8").write(record)
print(len(record.splitlines()), "lines")
