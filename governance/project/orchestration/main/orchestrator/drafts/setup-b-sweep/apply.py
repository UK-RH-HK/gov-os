#!/usr/bin/env python3
"""Set-up B sweep (DEC-1128 (4)): SWITCHED-OFF-1.md section 5, S1 S5-S11 S13 S15 S16.

Run from the repo root:  python3 <this file> [--check]
--check only counts: every old string must occur exactly once; nothing is written.
S12 (.tickets/DAEO-wnnz.md) is skipped: the ticket is closed (DEC-1088 (6): a closed ticket is never edited).
S2, S14, S18 are the owner's; S3, S4, S17, S19, S20 are keep.
"""
import sys
from pathlib import Path

CHECK = "--check" in sys.argv
D = "DEC-1128 (4)"
EDITS = []  # (id, file, old, new)


def e(sid, path, old, new):
    EDITS.append((sid, path, old, new))


# ---- S1: retire W3-P30 (mark, not delete)
e("S1", "docs/plan/WAVE_3_PARKING.md",
  "| W3-P30 | Set-up B (the sandbox generated from the path map)",
  "| W3-P30 | RETIRED 2026-11-14 (DEC-1128 (4): set-up B dropped; the S2 gap stays a named, accepted gap, W2-56 S2/F1): "
  "Set-up B (the sandbox generated from the path map)")

# ---- S5 / S11 (DEC-1103) / S15 (DEC-769): "Changed by" marks on Status lines, register form copied from DEC-1112
REG = "docs/DECISION_REGISTER.md"
e("S5a", REG,  # DEC-1098 status (existing list: appended with "; ")
  "· **Changed by:** DEC-1179 (7); DEC-1164 (7) ((6) spent at the lift)",
  "· **Changed by:** DEC-1179 (7); DEC-1164 (7) ((6) spent at the lift); "
  "DEC-1128 (4): item (4)'s sandbox experiment loses set-up B (dropped entirely, not a Wave 3 row); set-up A stays")
e("S5b", REG,  # DEC-1099 status
  "after SANDBOX-GUARD-EXP-1, W2-88-STANDARD-1 and FORECAST-W2-1 · **Changed by:** DEC-1176",
  "after SANDBOX-GUARD-EXP-1, W2-88-STANDARD-1 and FORECAST-W2-1 · **Changed by:** DEC-1176; "
  "DEC-1128 (4): the experiment as designed loses set-up B (dropped entirely, not a Wave 3 row); set-up A stays")
e("S11b", REG,  # DEC-1103 status (no existing Changed by: new field)
  "after the selection ACTs were applied (`8038e0ee`; the hook 6fbbf312…) and the push (`795d97c7`, `3ce6394f`)\n- **Decision:**\n  - (1) **W2-20's gate file",
  "after the selection ACTs were applied (`8038e0ee`; the hook 6fbbf312…) and the push (`795d97c7`, `3ce6394f`) · "
  "**Changed by:** DEC-1128 (4): item (3)'s \"the sandbox added once proven\" is withdrawn, no sandbox will come (set-up B dropped)\n- **Decision:**\n  - (1) **W2-20's gate file")
e("S15b", REG,  # DEC-769 status
  "so for them the guard's reading of shell text is the only layer. · **Changed by:** DEC-953 (item 2)",
  "so for them the guard's reading of shell text is the only layer. · **Changed by:** DEC-953 (item 2); "
  "DEC-1128 (4): leads are not sandboxed and no sandbox work follows for them (the title's \"Leads run sandboxed\" is withdrawn); the workers' launcher sandbox stays")

# ---- S6: DECISIONS-IN-FORCE
e("S6", "governance/project/orchestration/DECISIONS-IN-FORCE.md",
  "beside D-10 (set-up B a Wave 3 row); W2-56 builds",
  "beside D-10 (set-up B dropped, DEC-1128 (4)); W2-56 builds")

# ---- S7: DECIDED-NOT-DONE rows 25, 29, 66, 137
DND = "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
e("S7-25", DND,
  "| (4) the design package to the owner first; then run; both results before W2-56 builds |",
  "| (4) the design package to the owner first; then run; both results before W2-56 builds "
  "[Re-worded 2026-11-14 by DEC-1128 (4), set-up B dropped: \"both results\" is set-up A's result only; W2-56 builds on it] |")
e("S7-29", DND,
  "| (1) beside D-10; brake at twice the projection; both results to the owner before W2-56 builds |",
  "| (1) beside D-10; brake at twice the projection; both results to the owner before W2-56 builds "
  "[Re-worded 2026-11-14 by DEC-1128 (4), set-up B dropped: \"both results\" is set-up A's result only] |")
e("S7-66", DND,
  "| DEC-1112 (1): set-up A fully beside D-10; set-up B a Wave 3 row |",
  "| DEC-1112 (1): set-up A fully beside D-10; set-up B a Wave 3 row "
  "[Re-worded 2026-11-14 by DEC-1128 (4), set-up B dropped: set-up A fully beside D-10; set-up B is dropped entirely, not a Wave 3 row] |")
e("S7-137", DND,
  "| NOT STARTED, trigger met (row 135 DONE 11-11): the list S1-S20",
  "| DONE 2026-11-14 except the owner's S2, S14, S18 (asked 11-14) · was: NOT STARTED, trigger met (row 135 DONE 11-11): the list S1-S20")

# ---- S8: LIFT-1 P1-19
e("S8", "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
  "the path-map guard alone, measured fully, set-up B a Wave 3 row;",
  "the path-map guard alone, measured fully, set-up B dropped (DEC-1128 (4));")

# ---- S9: SANDBOX-GUARD-EXP-DECLARATION
DECL = "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-DECLARATION.md"
e("S9-header", DECL,
  "- **By:** a research agent for the CTO, 2026-11-09.\n- **Committed before any run.**",
  "- **By:** a research agent for the CTO, 2026-11-09.\n"
  "- **Set-up B: not run, dropped (DEC-1128 (4), note of 2026-11-14).** Set-up B's text below is kept as the record of the "
  "pre-registration; it is not a Wave 3 row and will not run. Set-up A is the experiment that stays.\n"
  "- **Committed before any run.**")
e("S9-A1", DECL,
  "Set-up B is a Wave 3 row, built by a different route. Its text below",
  "Set-up B is dropped entirely, not a Wave 3 row [Re-worded 2026-11-14 by DEC-1128 (4); the amendment first read: "
  "\"Set-up B is a Wave 3 row, built by a different route.\"]. Its text below")

# ---- S10: SANDBOX-GUARD-EXP-1 header note
e("S10", "governance/project/orchestration/packages/SANDBOX-GUARD-EXP-1.md",
  "at a 100 % bar (DEC-1098 (4))\n\n- **For:**",
  "at a 100 % bar (DEC-1098 (4))\n\n"
  "> Note 2026-11-14 (DEC-1128 (4)): set-up B (the guard plus a sandbox) was dropped entirely and never run; "
  "its text here is kept as the record. Set-up A stays.\n\n- **For:**")

# ---- S11: ACT-INDEP-WALLS-1 lines 103 and 204
WALLS = "governance/project/orchestration/packages/ACT-INDEP-WALLS-1.md"
e("S11-103", WALLS,
  "**Its wall** is set-up B's sandbox, once proven (§7 residual 1).",
  "**Its wall** was to be set-up B's sandbox, once proven; no sandbox will come (set-up B dropped, DEC-1128 (4), 2026-11-14), "
  "so the wall is the seal and this settings layer, and the residual stays named (§7 residual 1).")
e("S11-204", WALLS,
  "the tuner's brief forbids both, and set-up B's sandbox closes them;",
  "the tuner's brief forbids both; no sandbox will close them (set-up B dropped, DEC-1128 (4), 2026-11-14), "
  "so they stay named residuals of 2b and 2c;")

# ---- S12: .tickets/DAEO-wnnz.md SKIPPED: status closed; DEC-1088 (6): a closed ticket is never edited.

# ---- S13: W2-56-CIT-E dated note (no rewrite)
e("S13", "docs/changes/W2-56-CIT-E.md",
  "(S1's two lines), `template/governance/kernel/settings.json` (S14).\n\n## 1. How each allowed-path form is held (S3)",
  "(S1's two lines), `template/governance/kernel/settings.json` (S14).\n\n"
  "> Note 2026-11-14 (DEC-1128 (4)): set-up B is dropped entirely, not a Wave 3 row, and the leads are not sandboxed. "
  "Where this record says set-up B, a write list made from the path map, or `gov rebuild` inside the sandbox \"is Wave 3's\" "
  "or is \"deferred to Wave 3 with set-up B\" (section 1 and section 7), no Wave 3 row follows: the script-write gap of "
  "section 1 stays a named, accepted gap (S2/F1), and the path-map guard is the control. The workers' launcher sandbox stays. "
  "The text below is as written.\n\n## 1. How each allowed-path form is held (S3)")

# ---- S15: WBS:624 and REVISED_PLAN "leads sandboxed"
e("S15a", "docs/plan/WAVE_2_WBS.md",
  "- **DEC-769 (owner, 2026-10-18), leads sandboxed:** first a feasibility test",
  "- **[RETIRED 2026-11-14, DEC-1128 (4): leads are not sandboxed; W2-21 closed with the ticket-lead role and lead rights, no sandbox; "
  "the path map and the guard are the controls; the workers' launcher sandbox stays. The text below is the old plan.]** "
  "**DEC-769 (owner, 2026-10-18), leads sandboxed:** first a feasibility test")
PLAN = "docs/plan/WAVE_2_REVISED_PLAN.md"
e("S15c", PLAN,
  "### 4.6 Keystone 6: the sandbox and write lists per role; leads sandboxed\n\n- **W2-20:**",
  "### 4.6 Keystone 6: the sandbox and write lists per role; leads sandboxed\n\n"
  "> [RETIRED 2026-11-14, DEC-1128 (4): the \"leads sandboxed\" promise here, in the table row for keystone 6 and in section 4's "
  "W2-21 lines, is retired. W2-21 closed with the ticket-lead role and lead rights, no sandbox; the leads are not sandboxed; the "
  "path map and the guard are the controls; the workers' launcher sandbox stays. The text below is the old plan.]\n\n- **W2-20:**")
e("S15d", PLAN,
  "`gov launch lead`, the ticket-lead role, leads sandboxed under their own role, and launch records.",
  "`gov launch lead`, the ticket-lead role, leads sandboxed under their own role [retired 2026-11-14, DEC-1128 (4): leads are not sandboxed], and launch records.")

# ---- S16: w2-orchestrator.md (line 69 "not sandboxed" is kept)
e("S16", "governance/project/prompts/w2-orchestrator.md",
  "- **After W2-21 closes:** gov launch lead <ticket> starts a lead, and leads start every worker with gov launch <role> <ticket>, sandboxed, with the role's network profile. These are the only ways in.",
  "- **Leads and workers (W2-21 is closed; DEC-1128 (4)):** gov launch lead <ticket> starts a lead, with the ticket-lead role's rights and no sandbox "
  "(leads are not sandboxed; the path map and the guard are the controls); leads start every worker with gov launch <role> <ticket>, "
  "sandboxed, with the role's network profile. These are the only ways in.")


def main():
    by_file = {}
    for sid, path, old, new in EDITS:
        by_file.setdefault(path, []).append((sid, old, new))
    bad = 0
    n = 0
    pending = {}
    for path, items in by_file.items():
        p = Path(path)
        if not p.is_file():
            print(f"MISSING FILE {path}")
            bad += len(items)
            continue
        text = p.read_text(encoding="utf-8")
        for sid, old, new in items:
            c = text.count(old)
            ok = c == 1
            print(f"{'ok ' if ok else 'BAD'} {sid:8} {path}  (old occurs {c}x)")
            if not ok:
                bad += 1
                continue
            text = text.replace(old, new, 1)
            n += 1
        pending[p] = text
    if not CHECK and bad == 0:
        for p, text in pending.items():
            p.write_text(text, encoding="utf-8")
    if bad:
        print(f"{bad} problem(s); " + "nothing written.")
        sys.exit(1)
    print(f"{n} edits in {len(by_file)} files; " + ("check only, nothing written." if CHECK else "written."))


if __name__ == "__main__":
    main()
