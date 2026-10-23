"""The interim skip guard (owner, DEC-899 item 7), until W2-57 lands: after a gov close, the skip count of the close's
full regression (its parallel run, where W1-38's rulesync fixture skips silently on a probe timeout, lens I's I4 F2)
must equal the expected count. Exit 0 when it does; exit 1 with the counts otherwise; exit 2 when the close's JSON
cannot be read. Usage: skip_gate.py <close JSON> [expected, default 31]."""
import json
import sys

try:
    runs = json.loads(open(sys.argv[1]).read()[open(sys.argv[1]).read().index("{"):])["result"]["test_runs"]
except (OSError, ValueError, KeyError, IndexError) as error:
    print(f"skip guard: the close's JSON cannot be read ({error})")
    sys.exit(2)
expected = int(sys.argv[2]) if len(sys.argv) > 2 else 31
regression = [r for r in runs if r.get("run") == "regression" and r.get("form") == "parallel"]
if not regression:
    print("skip guard: the close ran no full parallel regression (a scoped close); counts by run: "
          + ", ".join(f"{r.get('run')}/{r.get('form')} {r.get('skipped')}" for r in runs))
    sys.exit(1)
skipped = sum(int(r.get("skipped", 0)) for r in regression)
if skipped != expected:
    print(f"skip guard: the regression skipped {skipped}, not the expected {expected} (a silent skip, lens I's I4 F2?)")
    sys.exit(1)
print(f"skip guard: the regression skipped {skipped}, as expected")
