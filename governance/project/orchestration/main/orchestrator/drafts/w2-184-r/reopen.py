#!/usr/bin/env python3
"""W2-184 (DAEO-6f0s) reopened for the narrow check's F1-F3 (DEC-1180 (4): fixed in the same flow, not Wave 3 rows). Run from the repo root."""
p = '.tickets/DAEO-6f0s.md'
t = open(p, encoding='utf-8').read()


def one(o, n):
    global t
    assert t.count(o) == 1, o[:40]
    t = t.replace(o, n)


one('status: closed\n', 'status: in_progress\n')
K = ("  - 'R1 (F1, 2026-11-14): a lead launch (`gov launch orchestrator <ticket>`) given `--reason`, `--trial` or `--owner-named` is "
     "refused with exit 2 and a message saying a lead takes none of them; nothing starts and no record is written; a lead launch "
     "without them is unchanged [rv-f1 F1, interface 7.1/7.2a, DEC-1180 (4)] Verify: the `test_r1_*` cases in tests/unit/launch/ "
     "pass (each option alone and together refused for a lead; the worker cases unchanged)'\n"
     "  - 'R2 (F2, 2026-11-14): a launch record is written atomically: its bytes go to a temporary file in the same folder that no "
     "reader takes as a record, then it is linked or renamed to its final name without overwriting; a launch killed at any point "
     "leaves either no record or a whole one under the final name; the reader still refuses a final-name record that is not JSON "
     "[rv-f1 F2, DEC-1180 (4)] Verify: the `test_r2_*` cases pass (a write interrupted after the create and before the bytes leaves "
     "no final-name file; a leftover temporary file does not refuse a launch; a planted non-JSON final-name record still refuses, "
     "naming it; two writers of the same name: one wins, the other is refused as today)'\n"
     "  - 'R3 (F3, 2026-11-14): the same probe-record path found under more than one root with different contents is read from "
     "every root, and a promotion any copy shows applies; identical copies count once [rv-f1 F3, P-td5-2 revised, DEC-1180 (4)] "
     "Verify: the `test_r3_*` cases pass (a stale launch-root copy without the fail-open finding and a newer ticket-branch copy with "
     "it: promoted; two identical copies: counted once); `test_f1_a_path_under_both_roots_is_read_from_the_launch_root_s_copy` is "
     "revised to this rule by the test designer'\n")
one("  failure:\n", K + "  failure:\n")
for path in ("- tests/unit/launch/test_w2_184_*.py\n",):
    pass
one("sources: [DEC-1167,", "sources: [DEC-1180, W2-60a, DEC-1167,")
t = t.rstrip('\n') + '\n\n' + (
    "**Reopened 2026-11-14 by the CTO (DEC-1180 (4): a defect spotted is fixed in the same flow; DEC-1157 (12), within the "
    "ticket's purpose; listed for the owner's reading): R1-R3 for the narrow check's F1-F3** (`docs/probes/DAEO-6f0s/"
    "PR-DAEO-6f0s-f1.md`, landed at d79c8c939). F1: a lead launch drops the three options silently (`command.py:41-45`, "
    "`launcher.py:938-950`). F2: `record.write` (`record.py:91-110`) creates then writes, so a killed launch leaves an empty "
    "record that refuses every worker launch (`launcher.py:494-500`). F3: a stale launch-root copy of a probe record wins over a "
    "newer copy elsewhere (`launcher.py:521-534`; fails open in that case). Order: a fresh test designer (R1-R3 as described "
    "behaviour, the one F3 case revised with `Rewrite-Reason: DEC-1180 (4), rv-f1 F3`), a fresh engineer, gov accept, a narrow "
    "independent check of this change only (DEC-1156 (7)).") + '\n'
open(p, 'w', encoding='utf-8').write(t)
print('ok')
