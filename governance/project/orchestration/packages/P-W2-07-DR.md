# P-W2-07-DR — Three closes blocked by old decision-record commits that W2-07's rule, as built, does not measure

- **Priority:** P2 (it gates three closes: W2-58, W2-63, W2-07). **Raised:** 2026-10-26 21:25 GMT, by the orchestrator, after the first re-pin's smoke test (DEC-922).

## 1. Context

- On 2026-10-22, W2-58's close was refused as WORK_WITHOUT_TASK. Seven `Task: decision-record` commits had changed its path map (package P-W2-58-C1).
- The owner answered with DEC-896 item 1, a W2-07 KPI: "a decision-record commit that changes only governance records, under an ACCEPTED decision, counts as measured for the work-without-a-task gate".
- DEC-896 item 2 added that ticket-file commits carry their ticket's `Task:` from then on.
- W2-63 was told to wait for W2-07 (DEC-892). W2-07 is now merged and pinned: the first re-pin, DEC-922.

## 2. What happened

The queue's gate (h) runs the close's own check with the new judge's code. It now also subtracts the commits the judge measures by their decision (`gov.close.gates.decision_records`, exactly as `gov close` does). It still finds:

| Commit | Tickets it blocks | What it changed | Decision it names | Why the judge does not measure it |
|---|---|---|---|---|
| `8f56ada1` | W2-58 | the path map | DEC-903 | delegated, not an owner decision |
| `c9a08678` | W2-58 | the path map, W1-42's tests | DEC-900 | the owner's `Role: owner` commit, but it changes tests, which are not records |
| `4166d8d9` | W2-58 | the path map, `.tickets/DAEO-j8gn.md`, the register, plan files | DEC-891 | `.tickets/` is not a governance record for the judge |
| `b772b2fe` | W2-58 | `.tickets/DAEO-5j8b.md`, the register, the WBS | DEC-880 | a ticket file, and DEC-880 has since been superseded |
| `65039414` | W2-58 | the register, the path map | DEC-876 | DEC-876 has since been superseded |
| `8d625805` | W2-63, W2-07 | `.tickets/DAEO-pl6k.md`, `.tickets/DAEO-r9ss.md`, records | DEC-892 | a ticket file |
| `611955fa` | W2-07 | six ticket files including `.tickets/DAEO-r9ss.md`, records | DEC-889, DEC-890 | ticket files; DEC-890 is delegated |

As built, the judge's rule (`gates.py`) has two limits:
- **What counts as a record:** only `docs/plan/`, `governance/project/prompts/`, `governance/project/briefs/`, `governance/project/orchestration/`, the register and the path map. DEC-891 also counts `.tickets/`, `docs/checkpoints/`, `docs/close/` and `docs/probes/` as records.
- **Which decisions count:** every decision the commit names must be an ACCEPTED owner decision that is still in force. DEC-896 item 1 says "an ACCEPTED decision".

These are commit gates. The judge refuses on them before any test, and such a refusal spends no attempt. The queue stops before the close in any case.

The other seven merged-but-not-closed tickets pass gates (e) and (h) and are in the queue: W2-70, W2-69, W2-66, W2-72, W2-59, W2-65 and W2-73. W2-67 stays held (stale probe; rounds 2 and 3 not merged).

## 3. Why it matters

- Exit criterion 1 needs every ticket closed by a clean `gov close`. These three cannot close cleanly until the judge measures commits made by the owner's decisions.
- The gap is in the judge, not in the tickets' work. All seven commits are the orchestrator's or the owner's records of owner decisions, made before DEC-896 item 2's ticket-file rule.

## 4. Options

- **(a) A W2-07 round 2 (recommended).** It brings the rule up to DEC-896 item 1 as written, in W2-07's worktree, with one FULL review. The fix:
  1. Records are DEC-891's list: add `.tickets/`, `docs/checkpoints/`, `docs/close/` and `docs/probes/`.
  2. "An ACCEPTED decision" counts a delegated decision, and a decision that was ACCEPTED and later superseded or changed. A decision that was never accepted still refuses.
  3. A `Role: owner` commit with `Task: decision-record` that names an ACCEPTED owner decision is measured by it, whatever paths it changes: it is the owner's own act. Ratchet entries already rest on `Role: owner` (DEC-862 (a)), and W2-12 will later move this to the owner's push.

  The fix is carried by the second re-pin (with W2-68 and W2-71). The three tickets then close.
  - Cost: one lead run (about half a day) and a review.
  - Risk: low. It widens one commit gate only for records and the owner's own commits; code and test commits by agents stay unmeasured.
  - Changes: W2-07's ticket file (KPI text, under this decision), WBS card, nothing in the Contract.
- **(b) The same as (a) without part 3.** `c9a08678` still blocks W2-58, which would then need an owner decision-close (option c) or W2-58's path-map paths removed by decision (but W2-58's own commits changed the path map, so containment would then refuse).
- **(c) An owner decision-close of the three.** DEC-896 item 1 said "Not (c): a decision-close would hide the gap", and it fails exit criterion 1 for each ticket.

## 5. Recommendation

(a), with all three parts. Confidence: medium-high.

Classification (DEC-809): one finding.
- `Ordinary work: yes, because every decision-record commit before DEC-896 item 2 that touched a ticket file or a ticket's path hits it.`
- `Consequence: other (it refuses: fails closed, loses no work).`

## 6. What it blocks, and what waiting costs

- **It blocks:** the closes of W2-58, W2-63 and W2-07, three of the eleven.
- **It does not block:** the other seven closes, W2-57, or any other start.
- **Waiting costs:** the three stay merged but not closed, and the progress line keeps them in that column. Under (a), W2-07's round 2 runs in the first free slot after W2-57 starts, and the three close after the second re-pin.
