#!/usr/bin/env python3
"""DEC-1180: the register entry + version row, the DIF line, DND rows 204-206. Run from the repo root."""
import sys
D = ".gov-runtime/scratch/orchestrator/drafts/dec-1180/"
REG = "docs/DECISION_REGISTER.md"
t = open(REG, encoding="utf-8").read()
entry = open(D + "entry.md", encoding="utf-8").read().rstrip("\n") + "\n"
anchor = "\n\n| Version | Date | Change |\n"
assert "### DEC-1180" not in t
i = t.index("### DEC-1179 ")
j = t.index(anchor, i)
t = t[:j] + "\n\n" + entry.rstrip("\n") + t[j:]
row = ("| 0.561 | 2026-11-14 | Owner (recorded by the orchestrator, DEC-861): DEC-1180 (N2 (b): changed heading-cited "
       "sections listed for the walled writer; P-Q02-RUN-1 (a): a one-question fix flow, W2-94 reopened, run today; the "
       "EXAMIN CTO tonight after the re-pin and the operator's setup; standing: no deferral). Next free id: DEC-1181. |\n")
assert t.endswith("|\n")
t = t + row
open(REG, "w", encoding="utf-8").write(t)

DIF = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
d = open(DIF, encoding="utf-8").read().rstrip("\n") + "\n"
d += ("- DEC-1180 (2026-11-14, (4) standing): **no deferral: everything that can be done now is done now; nothing waits "
      "for the next morning, the next digest or a later batch, and a defect spotted is fixed in the same flow; only an "
      "item waiting on the owner (until the owner says they are asleep, DEC-1156 (8)) or a dependency between tickets "
      "holds work; an owner wait goes to the owner at once as a full package with its line, everything else keeps "
      "moving.** Basis: \"Standing, from now on: stop deferring. Do now everything you can do now ...\"\n")
open(DIF, "w", encoding="utf-8").write(d)

DND = "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
n = open(DND, encoding="utf-8").read().rstrip("\n") + "\n"
assert "| 204 |" not in n
n += ("| 204 | DEC-1180 (2): q02's one-question fix flow (W2-94 reopened, S6-S12), then the owner's operator installs the "
      "variant, runs the flow and `check_gold` (20 of 20), today | IN PROGRESS 11-14: reopened; the launch clone's "
      "scaffold 2 (the variant) committed 52208402587e; the lead next |\n"
      "| 205 | DEC-1180 (1): W2-61h's N2 (b) test revision and narrow check, then the operator's walled re-run and the close; "
      "W2-187 S10 (6) / I10 item 6 amended | IN PROGRESS 11-14: tickets amended; the revision's lead next |\n"
      "| 206 | DEC-1180 (3): the EXAMIN CTO starts tonight right after the owner's re-pin and the operator's setup | WAITS "
      "on release 0.1.0 (W2-88's land), the re-pin and the setup |\n")
open(DND, "w", encoding="utf-8").write(n)
print("ok")
