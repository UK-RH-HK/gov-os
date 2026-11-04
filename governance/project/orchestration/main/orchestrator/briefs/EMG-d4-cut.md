# D-4, the test suite cut: the list for the owner (test designers; CTO session 33b3628c, 2026-11-03)

Read first, whole: `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` and
`governance/project/orchestration/INTENT-DEC-1052.md`. Your task brief names your part (A or B).

**The owner's decision (DEC-1052, "the test suite"):** before the full suite runs (D-10), the suite is cut from about
19,000 cases to **about 5,000 or fewer, every kept KPI line still covered by at least one test**. Start with the guard's
~9,000: keep what the five rules need (now with G-14's `role_paths`, live since `4edd196c`, DEC-1059); the cases of
lifted rules and the breadth of roles x tools x input forms go, or are reduced to representative cases. Tests of
features that stay built but off (the strict close, the full guard and the like) leave the full suite: per group,
delete or keep as an opt-in suite outside the full run (proposed). **The list of deletions and merges comes to the
owner first; nothing is deleted or merged now.** The count and the full suite's expected time, before and after.

**What is lifted** (so its tests can go or move): `governance/project/orchestration/DECISIONS-IN-FORCE.md`, its
"Lifted" section, and the approved rows of `governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md`
(the DEC-1052 list in `packages/LIFT-1/P1-PLAN.md`'s first section). **The inventory already done:**
`governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md` (§1 sizes, §2 counts and seconds per suite, §3
no longer needed, §4 repeats and merges, §5 the KPI coverage method, §6a its list) and `packages/P1-INVENTORY-1.md`
(its rows D1-D3, M1, M2, R1-R5, M4-M7, M9 were approved by DEC-1040 (1)): build on them, do not redo them.

**Your output:** `governance/project/orchestration/packages/LIFT-1/D4-LIST-<A|B>.md`, written in the main tree (that
file only; the CTO commits it). For each group (a suite, a file or a family of cases):
- the action: keep, delete, merge, parametrise into representative cases, or move to an opt-in suite outside the full
  run (name it);
- cases before and after, and case-seconds before and after (from §2's figures or the latest JUnit files the inventory
  names; mark estimates "est.");
- **every KPI line the removed cases covered, and the kept case that still covers it** (the inventory's §5 method);
  a KPI line left uncovered is not allowed: keep a representative case for it;
- the reason (the decision or row that lifts it, or "repeat of <case>");
- your confidence.
End with the totals: cases before and after for your part, case-seconds before and after, and the lines you could not
place. Keep to facts you checked; name every estimate.

**How:** read the tests and the tickets' KPI lines (`.tickets/*.md`) freely; read the integrated code only where you
need to know what a test exercises (DEC-963). Counting runs (`pytest --collect-only -q`) through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, TMPDIR as
your brief says; **no full suite and no long runs** (DEC-1049: the full suite only on the owner's word). Never read the
hidden half (`~/gov-os-eval`), the held-out material or secrets.

**Return:** the twelve fields of EMG-common; your totals in `evidence`; anything that needs the owner (a feature's
suite to keep or drop, a KPI line that cannot stay covered cheaply) in `proposed_decisions`, with a recommendation.
