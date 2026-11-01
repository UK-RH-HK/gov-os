# P1-NEW-TICKETS-2026-10-31: two new tickets the leads' returns need (DEC-974: a new WBS ticket is the owner's)

For the owner. Two proposals, neither filed. Each in the six parts (DEC-818).

## T1. W2-113: an adopted product's CTO is named at adoption (W2-110's P-W2-110-2)

1. **Context:** W2-110 (`DAEO-3r1j`, FULL, built, its review passed) makes the kernel's guard ask the owner for an install only from the orchestrator on the project's coordination ticket (DEC-971 item 4). Its KPI says that key (`coordination_ticket` in the project's roster) is "set at adoption".
2. **What happened:** no path of W2-110 can write the key at adoption; and its reviewer found the template's orchestrator role file (both copies) still says the guard asks on every install, naming neither the key nor the CTO's `GOV_TICKET` (F3), and that the refusal's words mislead when the rule cannot run (F5).
3. **Why it matters:** an adopted product (EXAMIN first) starts with no key, so its CTO's installs are refused until someone writes it by hand; the role file tells its CTO the old rule.
4. **Options:**
   - (a) **A small ticket W2-113** (product-spec then engineer, STANDARD, about 60 lines): the adopt step writes `coordination_ticket` from the coordination ticket it creates; both copies of the orchestrator role file state the rule and the key; the refusal names `GOV_TICKET` and how to set the key. After W2-110 and W2-52 (the adopt files); before EXAMIN's copy.
   - (b) The template ships a roster with an empty key: still closed (every install refused), and the CTO writes it by hand.
   - (c) Rely on the refusal's how-to alone.
5. **Recommendation:** (a), high confidence (the lead's and the reviewer's).
6. **Blocks, and the cost of waiting:** nothing now; EXAMIN's first install, without it.

## T2. W2-114: W1-28's whole-tree copy check reads message text as a copy (W2-108's follow-up)

1. **Context:** W1-28's check (`test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs`) looks through the acceptance tests for routes that copy the repository's whole tree (DEC-385).
2. **What happened:** it refused tonight's batch of six on W2-108's scope test, which copies nothing: its `pytest.skip(f"{REPO_ROOT} is not a git worktree")` names the repository root and the words "git worktree" in a message. W2-108's test designer rewrote the message (DEC-977); the check itself still reads message text.
3. **Why it matters:** the next test that names the root in a skip, a fail or an assertion message refuses a close for nothing, and costs a resume (tonight, about 3 hours of a batch run).
4. **Options:**
   - (a) **A small test-revision ticket W2-114** (independent test designer, LITE): the check ignores the arguments of `pytest.skip`, `pytest.fail` and assertion messages, and looks for route words only in argument lists and in `subprocess` and `os.system` calls; every true copy it finds today it still finds (planted cases), nothing lowered (DEC-906: under the owner's named decision).
   - (b) Leave it; each false hit costs a resume.
5. **Recommendation:** (a), medium confidence (the lead's).
6. **Blocks, and the cost of waiting:** nothing now; a false refusal each time it recurs.

## Also noted (no decision asked)

- W2-110's P-W2-110-3, renewing the owner's pinned gov after its merge, is ACT 2's one re-pin (DEC-954 item 6).
