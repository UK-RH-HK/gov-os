# W2-32's S9: a disposition in line with DEC-1097 (DEC-1126 (6))

Read `LIFT-common.md` first (scratch only). Role: product-spec helper, Sonnet high, class C1 (DEC-1120). Scratch
folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-32-s9/`.

## The question
W2-32 stays open at the lift (DEC-1126 (6)). Its S9 line is the hit@5 bar (85 % hit@5 on the fresh 80, DEC-1083 (2));
the fresh 80 measured 58.3 %. The owner says DEC-1097's end-to-end bar replaced the hit@5 bar (DEC-1097 (1)(d): right
end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it). Bring the owner a
disposition of S9 in line with DEC-1097.

## Read (in the register and the records, never from memory)
- W2-32's ticket (find it in `.tickets/` by `wbs_id: W2-32`), its S9 line and its `sources`.
- DEC-1083 (2), DEC-1097 (whole), DEC-1092, DEC-1101, DEC-1125 (2), and whatever recorded the fresh 80's verdict
  (search the register and `governance/project/orchestration/packages/` for FRESH-80 and K9; the verdict package and
  its figures: end-to-end right, wrong claims, hit@5). **Never open** `~/gov-os-eval/`, `~/gov-os-runs/`, or any
  folder named `hidden`, `memory-verdict` or `memory-verdict-2`: the published figures in the packages and the
  register are enough. Whether DEC-1083 (2) carries a "Changed by DEC-1097" note on its status line (DEC-866
  supersession); if not, say so: it is record drift for the CTO.
- DEC-105 (a contradiction against a closed specification: three costed options) and the ticket template's rule
  that a closed ticket is never edited (W2-32 is open, so its KPI lines can be re-worded by the owner's decision).

## Write `DISPOSITION.md` in your folder
1. What S9 says now, word for word, and what DEC-1097 decided, word for word.
2. Whether the 80's recorded end-to-end result meets DEC-1097's bar, with the figures and where they are recorded.
3. Options (each: the exact new S9 line or the change, what it means for W2-32's close, its cost in lead-hours, and
   what it leaves open): at least (a) S9 re-worded to DEC-1097's end-to-end bar, measured by the weekly memory audit
   (DEC-1125 (2)) or by the 80's recorded result; (b) S9 retired as overtaken, with hit@5 kept as a reported figure;
   (c) any option the records show is better. Your recommendation with confidence.
4. The supersession sweep (DEC-866): every other place that still states the hit@5 85 % bar as a gate (tickets, the
   path map, tests, skills, packages, the orchestrator prompt), by id and by value; a list only.
Plain language for the owner; short. Return the twelve fields, short. Estimate 45 min to 1 h.
