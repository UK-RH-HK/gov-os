"""Add two skips to the known list after the first re-pin (DEC-915 item 2: every addition named in the digest)."""
import json
from pathlib import Path

path = Path(__file__).resolve().parent / "skip_known.json"
known = json.loads(path.read_text())
new = [
    {"test": "tests.unit.retrieval.test_lexical::test_the_chunking_is_the_carried_one",
     "reason": "could not import 'govbridge.core.chunking': No module named 'govbridge.core.chunking'"},
    {"test": "tests.acceptance.W1-03.test_w1_03_probe_findings::"
             "test_a_check_that_cannot_run_is_reported_and_recorded_with_the_call_s_own_fields[the-gov-package-is-missing]",
     "reason": "this interpreter finds a `gov` package without PYTHONPATH"},
]
have = {(e["test"], e["reason"]) for e in known["entries"]}
for entry in new:
    if (entry["test"], entry["reason"]) not in have:
        known["entries"].append(entry)
note = ("2026-10-27, after the first re-pin (DEC-922): the pinned close runs its tests with the pin's interpreter, where "
        "gov is installed, so W1-03 [the-gov-package-is-missing] skips; the govbridge parity case skips with the longer "
        "module name in its message (the same cause as its known entry)")
if note not in known["additions"]:
    known["additions"].append(note)
path.write_text(json.dumps(known, indent=2, ensure_ascii=False) + "\n")
print(f"{len(known['entries'])} entries")
