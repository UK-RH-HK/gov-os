"""Fills run 4's reviewer brief: the head and the lead's verification."""
from pathlib import Path

OUT = Path("/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/briefs/rev-4.md")

VERIFY = """- `gov.__file__`: `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`.
- The merge of `w2/integrate` at `848f5ab366b9` (`27f290a2beef`) had no conflict. `w2/integrate` has since moved to `26309d7b430c` (records and W2-68's and DAEO-5j8b's closes); `git diff --stat 848f5ab366b9 w2/integrate -- src tests` is empty, so the lead did not merge again.
- Full `gov rebuild --json` at this head, under the rebuild lock: exit 0, digest `f472681e02e0`. A first `gov check` after the 12:29 rebuild was RED on index freshness and recovery/rebuild, only because the lead's checkpoint record `CP-DAEO-cy5o-0015.md` was committed after that rebuild; the rebuild at the head cleared both. The keyword warning (row W2-L423's rule): 0 files.
- `gov check --json` at the head: ok; 17 families, 15 GREEN, 2 YELLOW (`core-decision-citations`, history commits citing a decision their tree does not record; `openspec-validate`, openspec not on PATH), no RED; the same two as at the earlier reviews.
- `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's parallel form (`-n auto -p gov_close_serial_only -o tmp_path_retention_policy=failed`, under the verify lock): 493 passed, 0 failed, 0 skipped (run 3: 466; the new cases are W2-68's in `tests/unit/close/`).
- The one serial entry in that scope (`tests/acceptance/W2-57/test_w2_57_designer_read_p95.py`), alone, as the close's serial phase runs it: waiting for the machine-wide verify lock as this brief is written; its result goes into the lead's note of the probe record (it passed at run 3).
- Collection over `tests` in one process: run after the serial entry; at run 3, `16690/16692 tests collected (2 deselected)`, no error."""

text = OUT.read_text(encoding="utf-8")
text = text.replace("@@HEAD@@", "bd418982e6c0").replace("@@VERIFY@@", VERIFY)
text = text.replace("the worktree's store was rebuilt at the merge `27f290a2beef`; the head adds only a checkpoint record, so a facet may read \"stale\": if so, say so and read the named files",
                    "the worktree's store was rebuilt at this head; if a facet reads \"stale\", say so and read the named files")
text = text.replace("## The lead's verification at the merge `27f290a2beef` (code identical at `bd418982e6c0`)",
                    "## The lead's verification at the head `bd418982e6c0` (code identical to the merge `27f290a2beef`)")
assert "@@" not in text
OUT.write_text(text, encoding="utf-8")
print(OUT, len(text), text.count("Can an honest agent hit this in ordinary work"), "rebuilt at this head" in text)
