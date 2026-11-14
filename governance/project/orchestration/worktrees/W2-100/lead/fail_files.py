"""The failing output of run 6 for the fix brief: each failed scenario's session reply and the judge's full reply."""
import json
from pathlib import Path

t = Path("/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/transcripts")
out = Path("/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval")
cases = {
    "api-2": ("20261114T031827175364332-63770", "20261114T031855649123083-66154",
              "api, scenario 2 (A rename in a published response), run 6, skill 1.0.1, run_at 2026-11-14T03:18:27+00:00"),
    "data-2": ("20261114T031928664875295-68762", "20261114T032043541889103-83430",
               "data, scenario 2 (An import that lets bad rows through), run 6, skill 1.0.1, run_at 2026-11-14T03:19:28+00:00"),
}
for name, (sess, judge, title) in cases.items():
    s = json.loads((t / f"{sess}.json").read_text())["result"].strip()
    j = json.loads((t / f"{judge}.json").read_text())["result"].strip()
    text = f"# FAIL: {title}\n\n## The session's reply\n\n~~~~\n{s}\n~~~~\n\n## The judge's reply\n\n~~~~\n{j}\n~~~~\n"
    (out / f"fail-{name}-run6.md").write_text(text)
    print(name, len(text.splitlines()))
