# P1-W1-01-EXEMPT-3: the owner's operator's commit `6fbe73b1adde` turns W1-01 red for every merge past it (DEC-253, DEC-906 item 3)

*Written 2026-11-11 about 19:00 UTC by a helper of the CTO. The owner has since ordered it (DEC-1136 (1)); this package is the record of the facts and the options.*

## 1. Context
W1-01's history case enforces "only the test designer commits to `tests/acceptance/`" (DEC-253, rewritten by DEC-906 item 2 and W2-70):
a commit that touches that folder without `Role: independent-test-designer` is an offender unless its **full id** is listed in
`governance/project/path-map.yaml` under `acceptance_exemptions` (an entry is `{commit, decision}`). A merge commit is judged by what it
brings in: it passes when every acceptance-test change comes from designers' commits or from listed commits (DEC-906 item 3).
The list is the owner's: DEC-906 item 1 makes the owner's own `Role: owner` commits the ratchet entries, the accepted-history
entries and the `acceptance_exemptions` entries, and the path map's comment says the three ratchet lists are frozen (DEC-1052 Q-10) except by the owner's commit.
It has eight entries now: `c9a086786444` (DEC-900), `0568d91baf56` (DEC-1031), and five from DEC-1123 (`cade65dfe045`, `04460404ea8a`,
`8c512d7e7921`, `ab169d051b82`, `15952bbfa576`). The model for a new entry is ACT-W1-01-EXEMPT-2 (DEC-1123 item 4). Links: the W2-81 lead's package
P-W2-81-LAND-3 (18:38 UTC), `docs/DECISION_REGISTER.md` DEC-253, DEC-906, DEC-1123, DEC-1136.

## 2. What happened (the evidence)
- At 17:41 UTC the owner's operator applied ACT-OPERATOR-ROUNDS-1 as commit `6fbe73b1adde40571f00d490b4b478cf86b70a52`, `Role: owner`, `Task: DAEO-sdxk`. It changes
  five files, one of them `tests/acceptance/W2-148/w2_148_support.py`, an acceptance support file. It is not the test designer's, and it is not listed.
- **Run read-only on `w2/integrate`** (a `--no-hardlinks` clone, W1-01's two history cases through the heavy-job gate, 46 s): `test_only_the_test_designer_commits_to_acceptance_tests`
  **fails**, naming `6fbe73b1adde` and no other commit: "commits touch tests/acceptance/** without the trailer `Role: independent-test-designer`, and are not listed by
  their full id in governance/project/path-map.yaml `acceptance_exemptions`". `test_the_integration_merges_of_this_repository_pass` passes today (no merge has brought
  the commit in yet). Rehearsal step A3 records it.
- **No other commit needs an entry.** Since the last entry's commit (`3428f659f095`, 11-10 22:11) the commits that touch `tests/acceptance/` are four designers' commits
  and three integration merges of designers' commits (the merge case passes them); `0c5032bc80a1` changes only briefs and `91c8885a407d` no test file. Only `6fbe73b1adde` is an owner
  commit with a test change, and it is already the only name in the red.
- Every non-fast-forward merge of `w2/integrate` past `6fbe73b1adde` brings the commit in, so the merge case would fail for it too: the lead of W2-81 found this at 18:38 (P-W2-81-LAND-3).

## 3. Why it matters
- The merge queue lands tickets by non-fast-forward merges. Each one now ends red on W1-01, and so does `w2/integrate` itself on any close or nightly that runs W1-01.
  A landing that is red for a reason outside the ticket cannot be told from a landing that broke something (question 2: a landing should never leave a red that hides a real one).
- The same will recur: any owner ACT that touches an acceptance support file turns W1-01 red the same way (DEC-1136 (2) now makes each such ACT carry its own entry).
- Nothing is lost or exposed by the commit itself; the failure is closed (it stops merges), not open.

## 4. Options
- **(a) The owner's by-hand ACT: one entry in `acceptance_exemptions`, decision DEC-1136** (the recommendation). Two lines in the path map, a `Role: owner` commit by the owner's operator,
  about three minutes; built, rehearsed (0 failures) and validated with the pin's reader; an undo is tested. Cost: the owner's yes plus three minutes; ACT-EXAMIN-SETS-1 and
  ACT-ACCEPTED-REDS-1 must be rebuilt on the new map (they decide by the map's sha256, so both would refuse after it), a mechanical job, about ten minutes each, plus the review question below.
  Risk: low. The list is frozen by DEC-1052 Q-10 "no new entry"; DEC-1123 and this decision are the owner's exceptions, as the earlier entries were. It widens nothing for agents: it only stops W1-01 naming one commit.
- **(b) Wait.** Keep landing with the red recorded, or hold the landings. Cost: every lead's landing waits, or lands red and each of those reds needs a note that it is this one; the
  waiting grows with each ticket that reaches the queue. Risk: a real W1-01 failure hides behind the known one.
- **(c) A `skip_known` entry** (`tools/skip_known.json`, DEC-915) naming the W1-01 case. W2-81's lead rejected it, and it is right: the file skips a whole case, not one commit, so
  it would hide every future offender of the rule, a real rule failure, for the sake of one named commit. It is also the CTO's tool file, not the owner's list the rule reads.
  Cost: cheap now; risk: high (a silent hole in DEC-253).
- **(d) Rewrite the commit** (it is already in history and in the operator's own sequence): refused; history is not rewritten, and the commit is the owner's.

## 5. Recommendation
**(a)**, confidence high: it is the form the owner already used for seven entries (DEC-900, DEC-1031, DEC-1123), the entry is exact and checked, and the owner has ordered it first (DEC-1136 (1)).
Findings' classification: **Ordinary work: yes (any owner ACT that edits an acceptance support file triggers it; ACT-OPERATOR-ROUNDS-1 did, in the normal way the owner's operator works); Consequence: other (fails closed: it stops every landing).**
Two facts for the owner, from the rehearsal: (1) W1-01 and the close's gate (h) read the list by full id and decision shape; they do not check the commit's role, so the same entry in a `Role: operator`
commit would also be green. The by-hand `Role: owner` commit is DEC-906's rule and the class table's, not enforced by code; (2) the entry's decision DEC-1136 names `6fbe73b1a`, as the close's
gate (h) needs (the decision must be the owner's and name the commit).
**For the CTO, on the rebuilds (not decided here):** ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 each hold one verdict bound to their manifest sha. A rebuild on the new map changes before and after in the
manifest, so its sha changes and the old verdict names another manifest. The operator agent's G4 (`operator_run.py`, `act_rounds`, DEC-1131 (3)) counts verdict blocks per ACT id across builds (cap: a third block refuses, to the owner)
and needs the last block to name the new manifest sha. So, in the code, a rebuild needs a new verdict block, which is round 2 (allowed, the last allowed). DEC-1131's text has no "re-check" without a block.
A reviewer's round-2 block on byte-identical entries is the cheapest valid form; ACT-ACCEPTED-REDS-1 is by hand (the agent's G6 refuses class (O)), so G4 would not run on it, but the same bar is the owner's policy (DEC-1131 (1)). Both facts, no ruling.

## 6. What it blocks
Every landing past `6fbe73b1adde` on W1-01 (W2-81's landing first), and integrate's own W1-01 run; indirectly ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1, which wait for the owner's yes and now run after this one (DEC-1136 (1)).
Waiting costs one red W1-01 per landing and a hidden-red risk; the ACT costs three minutes of the owner's operator and a rebuild of the two others.
