# Lifted by DEC-953 (owner, 2026-10-30)

Draft of 2026-10-30. Each line names what is lifted, the decisions that held it, and one of two outcomes:
- **until whole:** lifted until `gov close` is proved on the proving ground (W2-81) and EXAMIN's copy. The feature stays built and tested in the product (item 1).
- **ended:** it does not come back as a working rule.

Nothing here deletes product code or tests. Spent one-off entries of these features are in `ARCHIVE-SUPERSEDED.md` part B, tagged "feature lifted".

## A. `gov close` and its gates (item 1)
- The pinned `gov close` as the gate to close or merge a ticket here (DEC-466, DEC-476, DEC-492; CAP-31/38/39/58/59 as gates). **Until whole.**
- The close's generic gates:
  - the rebuild and STORE_STALE before each close;
  - TREE_NOT_COMMITTED;
  - the context packet (CONTEXT_FAILED);
  - checkpoint freshness;
  - `gov check` at the close;
  - class and evidence;
  - the record-reading suites;
  - the network check;
  - the interim skip guard (DEC-899 item 7, DEC-915).
  **Until whole.**
- The escalation state at three counted refusals (CAP-59; DEC-455, DEC-870), and DEC-096 as applied to the close's refusals. **Until whole.**
- A repair ticket on every refused close (CAP-31; DEC-454 and DEC-490 in part; the repair tickets for refusals not caused by the ticket itself). **Until whole.**
- The fast pre-close gate (a) to (h) and the queue's duplicate gates (DEC-868 item 1, DEC-892's host check, DEC-896 item 4). **Ended.**
- The full record checks (`record_checks.sh`) before every record commit (DEC-868 item 2). Practice 10's seconds-long check replaces them. **Ended.**
- The work-without-a-task gate (DEC-896 item 1, DEC-923, DEC-924 items 1 and 2: reports in commits of their own). **Until whole.**
- Close-breaking rows fixed before the full closes they would hit (DEC-941 item 4.2). **Ended.**
- A clean `gov close` of this repo's tickets as Wave 2's exit criterion 1 and as Wave 2-grade evidence (WBS §0 rule 1, DEC-721, DEC-941 item 7 in part). The proof moves to W2-81 and EXAMIN's copy (item 6). **Ended here.**

## B. Containment, trailers, ratchet and probe staleness (item 1)
- Containment as a close gate: merge-base attribution, `judge_commits` (DEC-912, DEC-918; CAP-58.h). The live hook may still flag, as advice. **Until whole.**
- Trailers and traceability as refusals: the `Implements:` ids against the register, and the trailer gate (DEC-927 item 2, DEC-928; CAP-38.b). Trailers are still written. **Until whole.**
- The ratchet lists (`accepted_reds`, `load_sensitive`, `accepted_history`, `acceptance_exemptions`) and their rules (DEC-757, DEC-762, DEC-766, DEC-906 item 2). **Until whole.**
- Owner-only `Role: owner` commits for ratchet, history, exemption and escalation entries (DEC-862 (a), DEC-891, DEC-906 item 1's owner part), with their validation by the pinned readers (DEC-895 item 1). **Until whole.**
- Probe staleness and record-form checks at the close: `probe_impact.py` at each merge (DEC-895 item 2; CAP-38.f's staleness). The review itself stays (practice 3). **Until whole.**

## C. Pins, schedules, locks and holds (item 1, and DEC-952's lifted parts)
- The re-pin ladder (DEC-884, DEC-933 item 1, DEC-936 item 2.3):
  - each judge fix re-pinned;
  - trials, combined re-pins and rollback folders;
  - re-pins only when the owner chooses.
  **Until whole.**
- Re-pin 3's ACT for W2-68, W2-71 and W2-77 (DEC-952; after-queue item 6). **Ended.**
- ACT-TESTMAP-1, the test-map change and the owner's commit, with DEC-891's record places for it (DEC-952 item 1f). Item 4a replaces them. **Ended.**
- Closes as one morning batch after a green nightly (DEC-952). **Ended.**
- The verification lock beyond one mutex for full runs: the close lock held through scoped closes, and the interim rebuild lock (DEC-952, DEC-939 item 2). **Ended.**
- Quiet windows for closes, "closes first", and the CLOSE-PENDING hold on launches (DEC-780, DEC-806, DEC-942 item 4). **Ended.**
- The cut-offs (DEC-942 item 5, DEC-939 item 6, DEC-933 item 2.4):
  - no starts from 00:30 to 05:30;
  - no full run after 01:00 that cannot end by 02:00;
  - no heavy lead runs during the nightly.
  **Ended.**
- Holding record commits while a queue runs (DEC-929 item 2), and DEC-929 item 1's package for record files of their own (item 4a does it). **Ended.**
- The 90-minute rule in the lead brief. It existed only for the waits above (audit §4.14), and no register entry holds it. **Ended.**
- The hold on all closes after a red nightly (DEC-938 item 4; DEC-951 item A's release rule) (item 3). **Ended.**
- A red nightly as a P1 by default (DEC-933 item 2.7). Item 3 replaces it: a fix on the spot, or a P1 with a recommendation. **Ended.**
- Booking the nightly by its estimate inside a fixed 02:00 to 05:00 window (DEC-933 items 2.2, 2.3, 2.5 and 2.6). The plain full run takes the one mutex. **Ended.**

## D. Resource gate (item 1)
- The memory arithmetic as a gate (DEC-947, DEC-942 item 2's memory part, DEC-847's figures, DEC-798's fixed figures):
  - the floor;
  - the verification peak;
  - the working size per lead;
  - the trip-wire in `oom_watch.sh`.
  It remains W2-20's product feature. The disk and inode floors and the scratch budgets stay (practice 8). **Until whole.**

## E. The guard, down to four rules (item 2; the switch-off route comes to the owner, as an ACT if needed)
- Write scope at edit time for every role:
  - `allowed_paths` (DEC-041, DEC-178);
  - a session's own ticket folder under `~/gov-os-runs` (DEC-728 item 2);
  - the test designer's own folder (DEC-769 item 2);
  - the orchestrator's `.gov-runtime/` refusals (DEC-176, DEC-180, DEC-181).
  **Until whole.**
- The counterpart's work on the same ticket as a guard read refusal (DEC-820 (c), DEC-826 Q2 and Q4, DEC-873). **Until whole.**
- The command-form refusals, which fail closed:
  - `$VAR` write targets, heredocs, backticks, inline Python with braces, opaque interpreters, `rm`, copy doubt, option reading and unknown tools (DEC-110, DEC-111, DEC-115, DEC-764, DEC-765, DEC-778, DEC-685);
  - the lead brief's command-form rules (DEC-941 item 4.1).
  **Until whole.**
- Read refusals beyond the four rules:
  - the settings file (DEC-525, DEC-548, DEC-553);
  - root searches (DEC-557, DEC-573, DEC-575);
  - the workbench and worktree listings as guard refusals (DEC-723 item 4, DEC-728 item 4).
  The behavioural rule of DEC-723 stays in the in-force list. **Until whole.**
- The freeze, pause and lift path (DEC-409, DEC-402), as far as the guard enforces it. **Until whole.** (To confirm: see the report.)

## F. Standing rules changed but not wholly lifted
These keep their other items. The exact marks are in the orchestrator's supersession list:
- DEC-096
- DEC-820 item 2
- DEC-826
- DEC-822 item 1
- DEC-847
- DEC-849
- DEC-893
- DEC-906 items 1 and 2
- DEC-911
- DEC-933
- DEC-936
- DEC-938
- DEC-939
- DEC-941
- DEC-942
- DEC-946
- DEC-951
- DEC-952
