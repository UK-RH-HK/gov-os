# Lead brief: the register by group (G4), then Charter v6 and Contract v5 (G5) ready for the owner by group

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
You are the product-spec lead (docs only). Branch `e2/g4-g5` from `w2/integrate`, worktree
`/home/usain/gov-os-worktrees/E2-g4-g5`. `Task: emergency-2`, `Class: Q`, `Role: product-spec` on your commits.

**The owner's decisions (DEC-1214):** G4 (a): audit 8's 33 groups as listed; the CTO settles the 48 doubtful rows;
DEC-027 superseded. G5 (a): Charter v6 and Contract v5 in one change, approved by group. G6 (a): fresh audits at the
release acceptance and adoption stages A5, AS, A7, A10, otherwise only for a red, a failed landing or a feature not
working; the Contract changes to match. L3 (a): pinned and hash-checked releases, no signing. M1 (c): `gov context`
retired. K1, L1, L2 (the landing and the close are one deterministic action), T1-T3, Q-UPD, Q-CLOSE as recorded.

**Read:** audit 8 `docs/emergency-2/audits/08-register.md` and `08-register.csv` (1,206 decisions: 153 kept, 185
superseded, 34 retired, 834 history, 33 groups, 48 doubtful); audit 7 `docs/emergency-2/audits/07-contract-rebaseline.md`
(every MR and CAP clause: kept, changed, dropped, moved; its D-1 to D-4; A-14 the Charter); EMERGENCY-2 §9.2 (the
clauses that contradict it); `docs/contract/` (Contract v4.4 since DEC-1213), `docs/charter/`; DEC-1211 to DEC-1214.

**Part 1, G4 (approved, lands):** apply audit 8's classes to the register: each decision's status line gets its class
(kept / superseded by DEC-n / retired / history) as audit 8 lists it, group by group, one commit per group. Settle the 48
doubtful rows yourself with a one-line reason each (in a table `docs/emergency-2/audits/08-doubtful-settled.md`); flag
any you cannot settle for the CTO. Then the old register becomes read-only history as EMERGENCY-2 §11.3 says: propose
in your return how it leaves memory's index (a path-map or index exclusion) and the kept decisions' new home, but do not
move the register file tonight.

**Part 2, G5 (needs the owner's yes by group in the morning; on your branch only):** write Charter v6 and Contract v5 in
one change from audit 7's tables, applying EMERGENCY-2 and DEC-1211 to DEC-1214 (the guard, the sandbox, the box gone;
G6's audit points; L3; M1; CAP-31's repair ticket gone; three iterations to two rounds; gitleaks only before going
public; CAP-45 `gov update` in the release; CAP-44.m's leftovers: the 275 capability records' version, DEC-1200 in the
`decisions:` list, the source map). Regenerate the capability records from the yaml (no committed generator exists:
write one under `docs/contract/tools/` that first reproduces the current 277 records byte for byte, then generate).
Then write the owner's approval page `docs/emergency-2/G5-APPROVAL.md`: one line per group (what changes, how many
clauses, the risk), with the codes he answers ("G5-1 yes, G5-2 yes, ..."). Run W2-49, W1-48, W2-51 and
`docs/plan/tools/validate_w2.py` on your branch; list any test v5 turns red and why (a test asserting a dropped clause
is retired by a test designer with a Rewrite-Reason only after the owner's yes: note it, do not do it tonight).
