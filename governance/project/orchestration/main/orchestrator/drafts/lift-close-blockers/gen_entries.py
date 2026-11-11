"""From survey JSON file(s), the accepted_history entries for every commit a WORK_WITHOUT_TASK finding names.
Usage: python3 -I gen_entries.py <clone> <decision> <survey.json> [<survey.json> ...] > entries.yaml
Writes to stdout only. Each entry: the full id, the decision, a comment with the date and the subject's start."""
import json
import re
import subprocess
import sys

clone, decision, files = sys.argv[1], sys.argv[2], sys.argv[3:]
found = {}
for f in files:
    for ticket, rows in json.load(open(f)).items():
        for r in rows:
            m = re.match(r"commit ([0-9a-f]{12}) names no task", r["what"])
            if m:
                found.setdefault(m.group(1), set()).add(ticket)


def git(*a):
    return subprocess.run(["git", "-C", clone, *a], capture_output=True, text=True, check=True).stdout.strip()


rows = []
for short in found:
    full = git("rev-parse", "--verify", short + "^{commit}")
    date, subject = git("log", "-1", "--format=%cI|%s", full).split("|", 1)
    rows.append((date, full, subject))
for date, full, subject in sorted(rows):
    print(f'  - commit: "{full}"')
    print(f"    decision: {decision}  # {date[:16]}Z; {subject[:90].replace(chr(34), chr(39))}")
