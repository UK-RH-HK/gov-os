"""Replaces RESUME HERE's "### Now" block (up to "### Standing owner rules") with the state of 2026-10-28 22:30, and
moves the old block to the archive's top."""
import pathlib

CP = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md")
AR = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT-ARCHIVE.md")
NEW = """### Now
- **Pin:** gov = pin-5c401220 (DEC-935, registry `bc37c419`); pin-6a4696eb kept. Tools read the pin from
  ~/.local/bin/gov's first line. The nightly route takes 15 entries out of the close (nightly only now).
- **Merged-not-closed:** W2-58, W2-63, W2-07, W2-67 (r1), W2-57. W2-65's worktree kept (guard refused my rm of its
  stray `pytest-of-usain/`) -> digest.
- **ACT-W2-57-LS-1 done** (owner `6367e965`). ACT-W2-57-LS-2 (W1-46 x23, W1-19) next: validate with the new pin
  (`tools/act_clone_run.sh`), then send.
- **Nightly:** committed `governance/project/orchestration/nightly/` (DEC-934; ping gate DEC-936, 28/28 tests);
  crontab 3 lines + Windows wake task (owner, checked). Morning: read status.txt + pings.log, relay P1s (prompt §7);
  digest reports each night's line, estimate vs actual.
- **Lessons 2026-10-28:** checks on untracked files prove nothing about tracked ones (`a999f97b`, W1-08); no commit
  chained after `;` (`1916501d`); a ticket citing a new DEC: commit the register first. W2-58's review cases fail
  from inside a Claude session (env leak): row.
- **Rows added:** W2-L449, W2-M407, W2-L450. Run clones under ~/gov-os-runs/W2-00 (3G+) never removed ->
  P-TOOLS-REVIEW-1.
- **W2-67** held (probe stale: W1-26/W1-27 + w1_07_support.py; `d0140d4d`).
- **Owner's asks in the register:** DEC-929 (P-SCOPE-RECORDS-1), DEC-930 + DEC-936 item 3 (the re-plan package with
  its 5 + 6 points), DEC-936 item 2 (carry on, leads in parallel, P2 delegated, only P1/ACT ping).

"""
lines = CP.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("### Now"))
stop = next(i for i, l in enumerate(lines) if l.startswith("### Standing owner rules"))
old = "\n".join(lines[start:stop])
CP.write_text("\n".join(lines[:start] + NEW.split("\n")[:-1] + lines[stop:]), encoding="utf-8")
text = AR.read_text(encoding="utf-8")
marker = "## Moved from RESUME HERE 2026-10-28 10:30 (replaced by the new state)"
AR.write_text(text.replace(marker, "## Moved from RESUME HERE 2026-10-28 22:30 (replaced by the new state)\n" + old
                           + "\n\n" + marker, 1), encoding="utf-8")
print("replaced %d lines" % (stop - start))
