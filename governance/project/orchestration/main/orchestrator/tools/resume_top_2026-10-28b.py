"""Replaces RESUME HERE's header and "### Now" (up to "### Standing owner rules") with the state of 2026-10-28 10:30;
the old text goes to the archive's top block."""
import pathlib

CP = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md")
AR = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT-ARCHIVE.md")
NEW = """## RESUME HERE (2026-10-28 10:30 GMT — W2-07 r2 MERGED `8555aafc`, W2-57 re-probe MERGED `4904a60f`; ACT-W2-57-LS-1 READY (`5c401220`, clone run green); ACT-NIGHTLY-1 sent; RE-PIN 2 LADDER RUNNING: full run on head `5c401220` (task bfxlzqklt, nightly.sh day), wheel dry run OK (e4f35131…905d0 twice); next DEC-934)

### Now
- **Pin:** gov = pin-6a4696eb (DEC-922); pin-fecb870c kept. Tools now read the pin from ~/.local/bin/gov's first line.
- **Queue 2026-10-27c done:** 7 closed (W2-66 full; six scoped off `00b371a0`). Gates ~12 min per close > the scoped
  close -> re-plan item. Closed tickets' worktrees removed except **W2-65's** (guard refused my rm of its stray
  `pytest-of-usain/`, 5.8M) -> digest. Rows moved to §4 (`4f2fc3d6`).
- **Merged today:** W2-57 `57e363c5`; W2-07 r2 `8555aafc` (run 5: full 16479 passed, serial 180; probe_impact made
  W2-57's probe stale on command.py); W2-57 re-probe `4904a60f` (PR-DAEO-cy5o-reprobe-1.md pass). Rebuilds ok. Temp
  folders of W2-07, W2-57 removed. Merged-not-closed now: W2-58, W2-63, W2-07, W2-67 (r1), W2-57.
- **ACT-W2-57-LS-1** (`packages/ACT-W2-57-LS-1.md`, `5c401220`): 6 removals + 2 DEC-927 corrections; the clone run
  with the pin (`log/act-runs/ACT-W2-57-LS-1-20261028-0052/`): parallel 16431 passed 0 failed, serial 180, green.
  Owner's operator commits it. ACT-W2-57-LS-2 (W1-46 x23, W1-19) right after re-pin 2, validated with the new pin.
- **Re-pin 2 (DEC-933, P-REPIN-2):** pins `5c401220`. Done: `pin/repin_dry2.sh` (two builds e4f35131…905d0; wheel
  holds serial.py, gates.py), `pin/repin2_registry.py` (refuses before install: checked), `pin/REPIN-COMMANDS-
  5c401220.sh`. Running: the full regression on a fresh clone with the head's code (`tools/nightly.sh` day; first
  run of the rewritten script; its record step writes `log/nightly/history.jsonl`). Then write
  `packages/ACT-REPIN-2.md` (plain terminal), ping ACT. After it: smoke test, update the prompt's pin line (DEC-895's
  command), ACT-W2-57-LS-2, queue W2-58, W2-63, W2-07, W2-57.
- **Nightly (DEC-933):** `tools/nightly.sh night` + `tools/nightly_estimate.py` (estimate 84 min; effective
  parallelism 7.4) tested 8/8 (`tools/test_nightly_night_mode.sh`); ACT-NIGHTLY-1 (crontab 02:00) with the owner.
- **Rows added:** W2-L449 (bare run loads the pin), W2-M407 (product nightly rule), W2-L450 (W2-57 designer p95
  under load, not on load_sensitive).
- **Run clones** under ~/gov-os-runs/W2-00 (2.6G+, plus 560M ACT clone) never removed -> P-TOOLS-REVIEW-1.
- **W2-67** held (probe stale: W1-26/W1-27 + w1_07_support.py; `d0140d4d`).
- **Owner's asks in the register:** DEC-929 (P-SCOPE-RECORDS-1), DEC-930 (re-plan after re-pin 2; four weekly
  numbers), DEC-931/932 (ACTs), DEC-933 (re-pin cadence; nightly rule).

"""
lines = CP.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## RESUME HERE"))
stop = next(i for i, l in enumerate(lines) if l.startswith("### Standing owner rules"))
old = "\n".join(lines[start:stop])
CP.write_text("\n".join(lines[:start]) + "\n" + NEW + "\n".join(lines[stop:]), encoding="utf-8")
text = AR.read_text(encoding="utf-8")
marker = "## Moved from RESUME HERE 2026-10-28 00:45 (replaced by the new state)"
AR.write_text(text.replace(marker, "## Moved from RESUME HERE 2026-10-28 10:30 (replaced by the new state)\n" + old
                           + "\n\n" + marker, 1), encoding="utf-8")
print("replaced %d lines" % (stop - start))
