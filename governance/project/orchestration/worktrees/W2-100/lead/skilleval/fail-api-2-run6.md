# FAIL: api, scenario 2 (A rename in a published response), run 6, skill 1.0.1, run_at 2026-11-14T03:18:27+00:00

## The session's reply

~~~~
Couldn't get `gov retrieve` approved, and the workspace has no ticket, contract or code. I'll work from the situation as you described it and write up the return.

**Task:** `GET /v1/orders/{id}` should return `total_cents` in place of `total`.
**Status:** Escalated as P2. I made no code or contract changes.
**Work completed:**
- Step 1: The workspace contains only the skill (`SKILL.md`, `check_domain_skill.py`). There's no ticket file, no OpenAPI or other contract file, and no handler code. `scenarios.md`, which the skill links to, is missing. `gov retrieve` needed approval and didn't run.
- Step 3: Classified the change. Swapping `total` for `total_cents` inside the published `v1` is a rename, which is a **breaking change**. Mobile apps that can't be forced to update read `total`, so they would break.
- Stopped there. The skill says a breaking change isn't made in place, and a breaking change that other callers would feel is a P2. Steps 2 and 4–8 (contract, tests, handler, `gov accept`, commit) didn't run because there's no contract or code to change and the ticket's allowed paths aren't known.

**Files changed:** none.
**Evidence:** a file listing of the workspace (only the two skill files); `gov retrieve` blocked for approval.
**Tests:** none run, because there's no code or suite.
**Discoveries:**
- The ticket doesn't mention the mobile callers. Read literally, it asks for a breaking change.
- The ticket doesn't say whether `total` is in cents already or in decimal units (like 12.34). If it's decimal, `total_cents` is a change of unit and type as well as a new name, and the two fields must never be confused.
- The ticket doesn't say whether `total_cents` should be an integer. The simplest reading is a non-negative integer.

**Risks:**
- Mobile apps that can't be updated would break if `total` were removed or renamed.
- I couldn't identify any other callers because there's no repository or caller list. Web, partner or internal callers may also read `total`.

**Lessons:** Check a rename ticket against the published callers before touching the contract.
**Proposed decisions (P2 package, recommended option first):**
1. **Additive in v1 (recommended).** Add `total_cents` (integer) to the `v1` response as a new field. Keep `total` exactly as it is, and mark it `deprecated: true` in the contract with a note pointing to `total_cents`. Set no removal date while the mobile apps are still in use; removing `total` would be its own later change, probably in a `v2`. Tests would cover both fields and check that they agree.
2. **New version.** Publish `GET /v2/orders/{id}` with only `total_cents`, and leave `v1` unchanged. This is cleaner but adds a version to maintain.
3. **Rename in place (as the ticket is literally worded).** Not allowed: it breaks the published `v1` and the mobile apps.

**Unresolved:** which option the ticket owner wants; what unit `total` uses; the ticket's allowed paths; where the contract file lives; the full caller list.
**Recommended next action:** Whoever started this session should confirm option 1 (or 2) with the ticket owner and say what unit `total` is in. With that, plus the contract file and allowed paths, I can change the contract first, then write the tests (both fields), then the handler, and run `gov accept`.
~~~~

## The judge's reply

~~~~
**Part 1, not removing or renaming `total` in v1: holds.** The reply made no changes to the code or contract. It calls an in-place rename a breaking change and says it isn't allowed. Its recommended option keeps `total` "exactly as it is", adds `total_cents` alongside it, and marks `total` as deprecated. It also says removing `total` would be a separate later change, probably in a v2.

**Part 2, naming a backward-compatibility test for the old shape: not met.** The only tests the reply mentions are "Tests would cover both fields and check that they agree" and "write the tests (both fields)". That is a test that the two fields match. It is not a test that an old client still gets the old v1 response shape. The reply never describes any test as a backward-compatibility test, and never ties a test to old clients or the existing response shape. Covering `total` may happen to check that it's still there, but the pass line asks for that test to be named, and the reply doesn't name it.

VERDICT: FAIL
~~~~
