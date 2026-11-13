task: DAEO-k1e2
decisions_applied: DEC-1010, DEC-136, DEC-1091, DEC-1097, DEC-1101
# PKG-W2-171-REV1-1: review round 1 FAIL (F-1 major); the fix round is blocked by the W2-171 spend brake

**State.** Run 3 merged w2/integrate (1ba9203a94fe). lead_verify at that head is RED with 7 of 4249. Those 7 are the same as run 2's: the six W2-96 shared reds and W2-170's F5 path case, which is branch-scoped (98076b44c (a)). All 341 W2-171, memaudit and W2-170 cases other than that one are green.

The FULL review rev-1 (independent-auditor, Opus, high, C2; session 304d57c6, 4.99 USD) returned FAIL on 1ba9203a94fe with 4 findings. Its launch tripped the runaway brake: W2-171 has spent 19.64 USD against a projection of 9.50 USD, and the brake is at 19.00. While log/brake/W2-171.json exists, launch_worker.sh refuses every launch, so the fix engineer cannot start.

## Findings and the lead's triage

| id | sev | KPI | where | finding | triage |
|---|---|---|---|---|---|
| F-1 | major | S3 | src/gov/memaudit/figures.py:154 (with :117) | The VERDICT line prints the exact 95 % interval from FIGURES.json's 4-place values, so the interval is rounded twice. 32 of 40 prints `64.3 to 91.0 %` where it should print `64.4 to 90.9 %`. 78 of 79 prints `93.2` where f80lib printed `93.1`. At n=40 the outcomes r = 8, 31 and 32 are wrong. | **Valid; fix in round 2.** Confirmed by reading the code: line 117 stores `round(lo, 4)` and line 154 prints that stored value. The fix is to print from `scores.exact_interval(right, n)` (unrounded) and keep the stored value rounded. A fresh engineer, Sonnet, high, C2, adds a unit case at r=32, n=40 and r=78, n=79. DEC-136 asks for a test-design batch first: an acceptance case at r=32, n=40 expecting `64.4 to 90.9 %`. |
| F-2 | minor | S2 | src/gov/memaudit/measure.py:181 | `measure --kept <n>` prints `RETRIEVAL attempt <n>` for an attempt that faulted. Item 8 says a faulted attempt's figures are never printed. Nothing counts this output. | Include it in round 2 for little extra cost: refuse to print, or print `FAULT`, for a faulted attempt under --kept. Or record it as a row. |
| F-3 | minor | S1/S2 | src/gov/memaudit/measure.py:152 | Nothing checks that the --repo tree is at the declared audit_commit and clean. It fails open only after a hand checkout without a rebuild, because DC-STORE ties the store to --commit. | Wave 3 row, not this round. |
| F-4 | minor | S3/S8 | src/gov/memaudit/judge.py:237 | An unexpected worker error (an OSError on the ledger) exits 4 after the other questions finish, and leaves reader/ without a brake STOPPED. Neither a rerun nor --resume can then finish it, only a hand ACT (ruling 5). Nothing is lost. | Recorded row. |

Reviewer risk R-1, the pool after MS-POOLFAULT, is already ruled by the CTO to stand.

## Question

How does round 2 proceed?

| option | what | cost | blocks |
|---|---|---|---|
| (a) recommended | The CTO clears the brake with more projection: `spend.py clear W2-171 --projection-usd 17 --note 'W2-171 review round 2: F-1 fix + review 2'`. The lead then runs round 2: td batch (F-1 acceptance case, Sonnet) about 1.5 USD, engineer (Sonnet, high, C2, F-1 + F-2) about 2 USD, rebuild + verify, review round 2 (Opus, high) about 5 USD. | about 8.5 USD; about 1.5 h | nothing after |
| (b) | Same as (a), without the test-design batch (engineer-only fix with unit cases), as the run 3 brief says. | about 7 USD; about 1 h | nothing after; DEC-136's test-first form is not used for F-1 |
| (c) | An owner ruling that item 8's "one decimal" means one decimal of the stored 4-place fraction. F-1 is then by design and round 1 is read as PASS with minors. | 0 USD | an owner decision, which is not delegated |

Recommendation: (a). Confidence high that F-1 is real and the fix is small. It blocks this ticket's DONE and its land.
