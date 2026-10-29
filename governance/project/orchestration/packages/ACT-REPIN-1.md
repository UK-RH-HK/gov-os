# ACT-REPIN-1 — The first re-pin and the settings regeneration (ACT)

From: the W2 orchestrator, 2026-10-25 (DEC-884, DEC-889 item 15, DEC-899 item 4, DEC-918, DEC-921). Gates: every close after it (the merged-not-closed tickets wait for it), W2-57's start, and the lead clean-up rule. Your acts are in `.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-6a4696eb.sh` (its copy is in the record).

## 1. Context

- **Today's judge** is the bootstrap pin `fecb870c`, which predates W2-50's merge and everything since. Every close, `gov check` and guard hook is judged by it.
- **This re-pin** carries the merge `6a4696eb` on `w2/integrate`. It holds W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 and W2-72.

## 2. What was done before it (the ladder)

- **All seven merged,** each with its tree equal to git's own merge and `tools/probe_impact.py` after it. W2-72's merge is `4a57bf6b`; W2-59 and W2-65 are the single merge `6a4696eb` (DEC-921).
- **W2-66's FULL review passed** (its third, the last), and its fixture trial passed:
  - a shared-core change runs everything;
  - a one-module change runs its suites;
  - a record-only commit runs the record-reading set;
  - 32 of 32 planted faults were caught.
  Batching and reuse are W2-68's (DEC-890), for the second re-pin.
- **The other six each passed their own ladder,** with a passed probe record where their profile requires one: W2-72's second review, W2-69's third (DEC-909), W2-59's CIT-P second review. W2-58 and W2-07 merged on their ladders before; W2-65 is LITE.
- **Clean history (DEC-921's conditions):**
  - containment finds nothing in any pending ticket's commits (W2-72's fix; all nine tickets judged);
  - the trailer gate lacks nothing;
  - W1-01's history cases pass;
  - nothing is pushed beyond `18ad2382`.
- **The full regression on the tree of `6a4696eb`** (`30442e9f`, a fresh clone in the close's form, 2026-10-25 05:06 to 06:33):
  - parallel 16,295 passed, 3 failed, 31 skipped; serial-only 265 passed;
  - W2-54's case and one W1-03 case pass alone;
  - one W1-03 case is a measured pre-existing fixture flake (6 of 10 fail alone today, 7 of 10 before W2-72), which fails closed. Its fix, W2-73, is running and merges before the first closes.
- **The wheel's dry run:** two builds from clean exports of `6a4696eb` give the same sha256, `73a281ff…c6b6c9`. `pytest-timeout` is reachable from a `--system-site-packages` pin.

## 3. Why it matters

Without it no fix since 2026-10-19 judges a close: Policy 2's reads, scoped closes, the commit gates first, the secrets check without the chance red, containment matching DEC-912. The merged-not-closed tickets cannot close by DEC-896 item 4's bar.

## 4. Your acts, in order

1. **Part A, the re-pin** (A1 to A6 in the script): export `6a4696eb`, build the wheel and check its sha256, install it in its own environment `pin-6a4696eb`, link `~/.local/bin/gov` to it, verify, then write and commit the registry entry (Role: owner). The bootstrap pin stays for the rollback.
2. **Part B, the settings regeneration:**
   - by hand, delete the two `"./docs/source/**": "deny"` entries in `.rulesync/permissions.jsonc` (P-I1-2);
   - `rulesync generate …`, then the pinned `gov.guard.heldout` (DEC-641);
   - commit (Role: owner).
3. **Then I run the smoke test:** the pinned `gov check` (adapter-portability should turn GREEN), one guard decision allowed and one refused, and the skip guard's and keyword warning's dry runs. I report it before any close and before I remove the backup ref `w2/integrate-before-reset-2026-10-24` (DEC-921).
4. **One choice, the lead clean-up rule** (DEC-904 item 2, "only its own temp folder, by its literal path"). A static settings file cannot say "its own":
   - **(a)** No allow rule yet: I go on removing returned leads' temp folders after a holder check. Lets through nothing.
   - **(b)** One literal rule per in-flight lead (`Bash(rm -rf /tmp/gov-os-lead-W2-57)` and so on), added at each regeneration. Exactly "its own", but each new lead needs one of your regenerations.
   - **(c)** One pattern rule (`Bash(rm -rf /tmp/gov-os-lead-W2-*)`). Lets a lead remove another lead's temp folder, even one in use.

   **Recommendation: (a)** until the guard can tell a lead's own folder (a row for W2-18).
5. **Before you start:** no Claude session may be running a gov command. W2-73's lead is running now; I'll tell you when it has returned, or you can run Part A once it has.

## 5. Recommendation

Run Parts A and B as written, with (a) for item 4.

## 6. What I need from you

The ACT, Parts A and B; your choice on item 4; and a word when they are done, so I run the smoke test.

**Rollback:** `ln -sfn ~/.local/share/gov-os/pin-fecb870c/bin/gov ~/.local/bin/gov`, then revert the two commits.
