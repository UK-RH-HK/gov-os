"""Writes log/facts-runs.md: the clones, the rebuilds (times, exits, digests, store sha256) and the gates. Paths only."""
import json
import subprocess
from pathlib import Path

L = Path("/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log")


def read(name):
    p = L / name
    return p.read_text(encoding="utf-8").strip() if p.exists() else "(none)"


def digest(name):
    try:
        d = json.loads(read(name))
    except ValueError:
        return "(unreadable)", {}
    r = d.get("result", d)
    return r.get("digest"), {"ok": d.get("ok"), "stores": r.get("stores"), "timing": r.get("timing")}


lines = ["# W2-91 run facts (lead)", ""]
for which in ("base", "head"):
    clone = f"/home/usain/gov-os-runs/W2-91/{which}"
    commit = subprocess.run(["git", "-C", clone, "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True).stdout.strip()
    dg, info = digest(f"{which}-rebuild.json")
    lines += [f"## {which}",
              f"- clone: `{clone}` (`git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS`, detached at `{commit}`)",
              f"- disk gate before the rebuild: {read(which + '-gate.txt')}",
              f"- rebuild: pinned gov (`GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python`, "
              f"no PYTHONPATH, no GOV_TICKET) through `tools/rebuild_slot.sh` (a heavy-job slot and the clone's own lock, DEC-1001 (d)); "
              f"script start {read(which + '-rebuild.start')}, end {read(which + '-rebuild.end')}, exit {read(which + '-rebuild.exit')}",
              f"- rebuild result: ok {info.get('ok')}; stores {info.get('stores')}; timing {info.get('timing')}",
              f"- digest (`result.digest`): `{dg}`",
              "- sha256 after the rebuild:", "```", read(which + "-sha.txt"), "```",
              f"- measure: start {read(which + '-measure.start')}, end {read(which + '-measure.end')}, exit {read(which + '-measure.exit')}, "
              f"stderr {'empty' if not read(which + '-measure.err') or read(which + '-measure.err') == '(none)' else 'see log'}",
              ""]
lines += ["## Notes",
          "- The base clone also serves as the measure's own clone: the measure's code (`src/gov/retrieval/measure.py`) and the visible set are read from it (`--sets-root`), at `f46b96537d74`, which was `w2/integrate`'s head when the ticket started.",
          "- `git diff --stat f46b96537d74 b652fc96d2b5 -- src` is empty: the code is the same at base and head.",
          "- The head (`b652fc96d2b5`) holds, besides the ticket's commits, the lead's merge of `w2/integrate` (`904bb3a0e7c6`) for the ticket's claim; it brought records, the merge queue's tool and its unit test, no code under `src/`.",
          "- The head's rebuild script started at 16:45:25 but waited for a heavy-job slot until about 17:11 (all three slots were busy).",
          "- The head's first measure was stopped by the lead before it wrote a record (its background task's two-hour limit was minutes away); the measure was then run alone on the same store (`measure_head_only.sh`). The store was not rebuilt again.",
          "- The control's rebuild of the first attempt waited on the old machine-wide lock and was stopped before it started (never a running rebuild); the rebuilds above are the second attempt, in the new form."]
(L / "facts-runs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
