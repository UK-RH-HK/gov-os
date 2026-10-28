"""Replaces RESUME HERE's header and its first sections (up to "### Standing owner rules") with the state of
2026-10-28 00:45, and moves the old text to the archive's top block."""
import pathlib

CP = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md")
AR = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT-ARCHIVE.md")
NEW = """## RESUME HERE (2026-10-28 00:45 GMT — QUEUE DONE: all 7 closed exit 0 (W2-66 full 76 min; six scoped 10-28 min); W2-57 MERGED `57e363c5`; W2-07 r2 lead run 5 (merge-back + re-verify) RUNNING (task b8gq2vln2); ACT-W2-57-LS-1 clone run RUNNING (task b28ua0o6h); next free DEC-932)

### Now
- **Pin:** gov = pin-6a4696eb (DEC-922); pin-fecb870c kept for rollback.
- **Queue 2026-10-27c done** (log `log/close-queue-20261027-1957/`): W2-66 `f8d1f60a` (full), W2-72 `6c439d8a`, W2-59
  `f0f933e1`, W2-65 `be18d1c7`, W2-73 `74c08ed8`, W2-74 `182823e4`, W2-69 `07a8d624` (each scoped, base `00b371a0`,
  30 targets: OWN 1, UNIT 1, EVERY_CLOSE 3, RECORD_READING 26). Gates before each close ~12 min (rebuild 4, collect,
  records 2, check 5): longer than the scoped close itself -> re-plan item (batched closes).
- **Done after it:** close_queue.sh exits 4 on a refused close (DEC-929 item 3; `tools/test_close_queue_refusal.sh`
  PASS). Worktrees+branches removed: W2-59, W2-66, W2-69, W2-72, W2-73, W2-74. **W2-65's worktree kept** (guard
  refused my rm of its stray `pytest-of-usain/`, 5.8M; branch merged): for the owner/digest. Lead temp folders of
  W2-69 and W2-65 removed. Rows marked `76fb5f18` (W2-H044, W2-M153, W2-L437, W2-M404, W2-M395, W2-L373, part W2-L419).
- **W2-57 merged `57e363c5`** (review current: integrate changed no src since a42e899b); probe_impact: W2-67 + 1 file
  (`tests/acceptance/W1-07/w1_07_support.py`), already stale. Rebuild ok.
- **ACT-W2-57-LS-1 (DEC-931):** patch `drafts/ACT-W2-57-LS-1.patch`: removes 6 load_sensitive (W1-38 x3, W1-07
  [doctor], W1-30 r13, unit follow-up) + W2-57's 2 DEC-927 corrections (named in register `f06ccf4b`). Validated:
  pinned readers PASS 2/2, ratchet counts 24 kept / 0 refused, record checks green, 69 dependent tests pass. Clone run
  in the close's form WITH THE PIN: `tools/act_clone_run.sh` -> `log/act-runs/ACT-W2-57-LS-1-*/run.txt`. If the unit
  follow-up case fails there, drop it from the patch (5 entries). Then write `packages/ACT-W2-57-LS-1.md` (operator
  commits Role: owner; Implements: DEC-931, DEC-927), commit it, ping ACT.
  ACT-W2-57-LS-2 (W1-46 x23, W1-19 warm p95) right after the second re-pin.
- **Finding for rows:** a lone `pytest tests/unit/close/test_serial.py` under the pin fails to import gov.close.serial
  (the pin's gov loads first); the full run collects because some unit conftests put src/ first. The close itself sets
  PYTHONPATH=src. Fragile for a narrow scoped selection -> row.
- **validate_entry.py** now scans only added lines for placeholders (a removed "00:2x" failed it).
- **W2-07 r2 run 5:** brief `briefs/W2-07-A5-run5.md`; expects merge clean, unmeasured 0/0/0, full run; DONE ->
  merge W2-07 (second), then probe_impact.
- **W2-67** held (probe stale on W1-26/W1-27 files + w1_07_support.py; r2+r3 unmerged at `d0140d4d`).
- **Owner's asks in the register:** DEC-929 (P-SCOPE-RECORDS-1 package; record commits between queues), DEC-930
  (re-plan package after the second re-pin; four weekly numbers from now), DEC-931 (the two ACTs).

"""
lines = CP.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## RESUME HERE"))
stop = next(i for i, l in enumerate(lines) if l.startswith("### Standing owner rules"))
old = "\n".join(lines[start:stop])
CP.write_text("\n".join(lines[:start]) + "\n" + NEW + "\n".join(lines[stop:]), encoding="utf-8")
text = AR.read_text(encoding="utf-8")
marker = "## Moved from RESUME HERE 2026-10-27 21:40 (size limit)"
AR.write_text(text.replace(marker, "## Moved from RESUME HERE 2026-10-28 00:45 (replaced by the new state)\n" + old
                           + "\n\n" + marker, 1), encoding="utf-8")
print("replaced %d lines" % (stop - start))
