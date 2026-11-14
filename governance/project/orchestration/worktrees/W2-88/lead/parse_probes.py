"""Run W2-184's launcher parse (_probe_record, _fails_open, _promotion) over the ticket's six probe records."""
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-88/src")
from gov.launch import launcher  # noqa: E402

root = Path("/home/usain/gov-os-worktrees/W2-88")
for path in sorted((root / "docs/probes/DAEO-2bdu").glob("*.md")):
    rel = path.relative_to(root).as_posix()
    loaded = launcher._probe_record(rel, path.read_bytes())
    if loaded is None:
        print(rel, "-> not a probe record (skipped)")
        continue
    front, body = loaded
    print(rel, "-> judgement:", front.get("judgement"), "| fails open:", launcher._fails_open(rel, body))
print("promotion:", launcher._promotion(root, ["DAEO-2bdu", "W2-88"], launcher._launch_records(root)))
