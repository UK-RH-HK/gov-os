"""The interim skip guard (owner, DEC-899 item 7; read by skip reasons since DEC-915), until W2-57 lands: after a gov
close, the queue reads the close's own evidence block (W2-66: every skip with its test and reason) and stops the queue
before the close's outputs are committed, as a P1 package:
  - on W1-38's "rulesync is not installed" skip whenever `rulesync --version` answers on this machine (lens I's I4 F2,
    the silent skip of a probe timeout), wherever the close ran it, scoped or full;
  - on any skip whose (test, reason) is not on the known list (`skip_known.json` beside this file, versioned on the
    record branch; every addition is named in the daily digest, DEC-915 item 2).
A close whose answer holds no evidence block (a close by a pin before W2-66) is judged as before: the skip count of its
full parallel regression must equal 31. Exit 0 when the guard passes; 1 with the reasons otherwise; 2 when the close's
JSON or the known list cannot be read, or rulesync's answer cannot be had. Prints test ids and reasons only.
Usage: skip_gate.py <close JSON> [expected count for a close without an evidence block, default 31]."""
import json
import subprocess
import sys
from pathlib import Path

KNOWN = Path(__file__).resolve().parent / "skip_known.json"
SILENT = "rulesync is not installed"

try:
    text = open(sys.argv[1]).read()
    result = json.loads(text[text.index("{"):])["result"]
except (OSError, ValueError, KeyError, IndexError) as error:
    print(f"skip guard: the close's JSON cannot be read ({error})")
    sys.exit(2)

evidence = result.get("evidence")
if not isinstance(evidence, dict) or not isinstance(evidence.get("skips"), list):
    # A close without W2-66's evidence block: DEC-899 item 7 as first written.
    expected = int(sys.argv[2]) if len(sys.argv) > 2 else 31
    runs = result.get("test_runs") or []
    regression = [r for r in runs if r.get("run") == "regression" and r.get("form") == "parallel"]
    if not regression:
        print("skip guard: no evidence block and no full parallel regression; counts by run: "
              + ", ".join(f"{r.get('run')}/{r.get('form')} {r.get('skipped')}" for r in runs))
        sys.exit(1)
    skipped = sum(int(r.get("skipped", 0)) for r in regression)
    if skipped != expected:
        print(f"skip guard: the regression skipped {skipped}, not the expected {expected} (a silent skip, I4 F2?)")
        sys.exit(1)
    print(f"skip guard: the regression skipped {skipped}, as expected (no evidence block: the count rule)")
    sys.exit(0)

try:
    known = {(e["test"], e["reason"]) for e in json.loads(KNOWN.read_text())["entries"]}
except (OSError, ValueError, KeyError, TypeError) as error:
    print(f"skip guard: the known list cannot be read ({error})")
    sys.exit(2)

skips = [(str(s.get("test")), str(s.get("reason"))) for s in evidence["skips"]]
silent = [s for s in skips if SILENT in s[1]]
installed = None
if silent:
    try:
        installed = subprocess.run(["rulesync", "--version"], capture_output=True, text=True,
                                   timeout=60).returncode == 0
    except FileNotFoundError:
        installed = False
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"skip guard: rulesync's answer cannot be had ({error}); {len(silent)} skip(s) say it is not installed")
        sys.exit(2)
unknown = [s for s in skips if s not in known and not (s in silent and not installed)]
problems = []
if silent and installed:
    problems.append(f"{len(silent)} skip(s) say rulesync is not installed, but `rulesync --version` answers "
                    f"(the silent skip, I4 F2): " + "; ".join(t for t, _ in silent[:5]))
others = [s for s in unknown if s not in silent]
if others:
    problems.append(f"{len(others)} skip(s) not on the known list: "
                    + "; ".join(f"{t} ({r[:120]})" for t, r in others[:10]))
if problems:
    print("skip guard: " + " | ".join(problems))
    sys.exit(1)
print(f"skip guard: {len(skips)} skip(s), each on the known list; no silent rulesync skip")
