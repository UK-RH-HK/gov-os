"""DEC-947 item 5 (owner, same day): the floor to 3 GiB with its trip-wire; and the parking list's new top entry,
W3-P09, hierarchical orchestration trialled on EXAMIN (owner, 2026-10-29). Safe to re-run."""
import pathlib
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = ROOT / "docs/DECISION_REGISTER.md"
PARK = ROOT / "docs/plan/WAVE_3_PARKING.md"
reg = REG.read_text(encoding="utf-8")
if "  5. **The floor goes from 6.4 GiB to 3 GiB" not in reg:
    edits = [
        ("  4. **Applied at once,** not held for the morning package; the staggered launches stay (DEC-946 item 8).\n",
         "  4. **Applied at once,** not held for the morning package; the staggered launches stay (DEC-946 item 8).\n"
         "  5. **The floor goes from 6.4 GiB to 3 GiB** (the owner's amendment the same day, not at the weekly "
         "re-measure): the verification run's peak is now reserved separately, and seven leads ran without memory "
         "trouble. If available memory ever falls below 2 GiB, or the kernel journal shows any out-of-memory kill, the "
         "floor goes back to 6.4 GiB at once and the next package reports it. The load gate stays as it is.\n"),
        ("  - `tools/gate_check.py` opens memory when MemAvailable plus what the running leads already hold is at least "
         "the floor (6,710,886 kB),",
         "  - `tools/gate_check.py` opens memory when MemAvailable plus what the running leads already hold is at least "
         "the floor (3,145,728 kB from item 5; 6,710,886 kB before),"),
        ("- **Where it goes (DEC-851):** this register, with DEC-942's status line; the prompt §3 (the gate) and §7 (the "
         "weekly re-measure), v3.41; RESUME HERE.\n- Next free id: DEC-948.\n",
         "  - **Item 5's trip-wire:** `tools/oom_watch.sh`, every 30 seconds: MemAvailable below 2,097,152 kB, or an "
         "out-of-memory line in `journalctl -k` since the watch began, puts the floor back to 6,710,886 kB in "
         "`gate-config.json` and logs it to `log/oom-watch.txt`. With item 5 the rule admits about five leads at once "
         "(21.1 − 3.0 − 7.1 = 11.0 GiB, at 2.04 GiB each; 20:47 on 2026-10-29).\n"
         "- **Where it goes (DEC-851):** this register, with DEC-942's status line; the prompt §3 (the gate) and §7 (the "
         "weekly re-measure), v3.41; RESUME HERE.\n- Next free id: DEC-948.\n"),
        ("Next free id: DEC-948. |\n",
         "Next free id: DEC-948. |\n| 0.330 | 2026-10-29 | Owner (recorded by the orchestrator, DEC-861): DEC-947 "
         "item 5 (the floor from 6.4 GiB to 3 GiB, put back at once if available memory falls below 2 GiB or an "
         "out-of-memory kill appears). Next free id: DEC-948. |\n"),
    ]
    for old, new in edits:
        if reg.count(old) != 1:
            sys.exit("register: not found once: " + old[:70])
        reg = reg.replace(old, new)
    REG.write_text(reg, encoding="utf-8")
    print("DEC-947 item 5 recorded")
park = PARK.read_text(encoding="utf-8")
if "W3-P09" not in park:
    row = ("| W3-P09 | **Top of the list (owner, 2026-10-29).** Hierarchical orchestration, trialled on EXAMIN. A master "
           "orchestrator owns the plan and priorities, the owner's interface, the register, integration, closes, re-pins "
           "and repository maintenance; a stream orchestrator per stream (each with its playbook, W2-83) owns its "
           "tickets' order, briefs, merge-backs and reviews, and proposes decisions up; only the master and the owner "
           "record decisions; ticket leads and workers as today. Aim: less compaction and drift, better stream-level "
           "decisions, streams that do not stall each other. Trial on EXAMIN with one stream orchestrator first, measured "
           "against a single orchestrator on compactions, the drift count and the close rate; extended if it wins. "
           "Depends on K3 (a stream-orchestrator role loaded at launch, with its own guard limits) and K4 (shared memory "
           "across streams). No Wave 2 work: only that W2-60a/W2-60b read roles from the kernel's role files, and that "
           "W2-04's context packet can be scoped to a set of tickets or a stream if that is small (else a Wave 3 row) | "
           "the owner | 2026-10-29 |\n")
    anchor = "|---|---|---|---|\n"
    if park.count(anchor) != 1:
        sys.exit("parking list: table head not found once")
    park = park.replace(anchor, anchor + row)
    PARK.write_text(park, encoding="utf-8")
    print("W3-P09 at the top of the parking list")
