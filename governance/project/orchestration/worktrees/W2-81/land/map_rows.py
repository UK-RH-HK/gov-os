"""Name the README map rows gov accept's parser refuses (diagnosis only; prints line numbers and KPI cells)."""
import sys
from pathlib import Path

from gov.accept import runner

text = Path(sys.argv[1]).read_text(encoding="utf-8")
lines = text.splitlines()
# Re-run the parser on growing prefixes: the first prefix that refuses ends at the bad row.
for end in range(1, len(lines) + 1):
    try:
        runner.parse_map("\n".join(lines[:end]))
    except runner.Unlisted as refusal:
        print("UNLISTED at line", end, refusal.args)
        break
    except runner.Unreadable:
        print("UNREADABLE at line", end, ":", lines[end - 1][:200])
        break
else:
    mapping = runner.parse_map(text)
    print("OK", len(mapping), "lines mapped:", ", ".join(runner.ordered(mapping)))
