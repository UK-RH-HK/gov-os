---
id: DP-0000
type: decision-package
status: PROPOSED     # open while PROPOSED (DEC-308)
state_class: AUTHORITATIVE
title: The question, in one line
rank: P2             # P1, P2 or P3, by critical path and irreversibility
cit: CIT-0000        # the CIT this gate belongs to; it authorises nothing in another CIT
constrains: []       # the tickets that wait on this package (DEC-308)
# The structured form `gov decisions page` reads (all optional in the schema; the page takes a package only when all hold):
question: ""         # one or two sentences, 300 characters at most
found: ""            # what was found, in plain words, 900 at most
options:             # 2 to 6, keys a, b, c in order; label 80, cost 240, consequence 240 characters at most
  - {key: a, label: "", cost: "", consequence: ""}
  - {key: b, label: "", cost: "", consequence: ""}
recommendation: {option: a, reason: "", confidence: medium}   # one key of options; reason 400; low, medium or high
sources: []          # files, decision ids and commits; each must exist; 12 at most
blocks: nothing      # or what stops until it is answered; 200 at most
rubric: P1.1         # the escalation rubric line that makes it the owner's: P1.1 to P1.10, or P2.brought
touches: []          # what it changes: spec, kpi, standing-decision, contract, charter, shared-code, cross-stream,
                     # kernel-text, secret, paid-service, model-effort, release, own-ticket
reversible: yes      # yes or no
inside: repository   # worktree, repository or outside; with `touches` these compute the level (P3, P2, P1)
# optional: deadline, meanwhile (200), under [DEC-n], raised {by, ticket, date}, replaces DP-n, file_only, spends,
# rounds, emergency
---

# DP-0000 — The question, in one line

<!-- Rules for whoever fills this in. Delete this comment from a filled package.

Routing. Class every contradiction before you raise it:
- agent-resolvable: one source outranks the other (Charter, Contract, ADRs, specifications, tasks, retrieval,
  inference). Settle it by precedence, record what you settled, and raise no package.
- human-resolvable: precedence does not settle it, or it is a question that matters to the owner (specification,
  features, security, privacy, hosting, cost, an irreversible choice). Raise it as a package, from this form.

Batching. At most five open packages are asked at a time; the rest wait, highest rank first.
A P1 package may bypass the cap (DEC-093).

State. A gate is in one of five states: open, answered, declined, revoked, stale.
The state lives in `status` alone, with no second key (DEC-328): `PROPOSED` is open, `ACCEPTED` is answered,
`DECLINED` is declined, `REVOKED` is revoked and `STALE` is stale.
Only an answered gate of the same CIT permits the next actions.

Links (LINK-INTEGRITY §5). Name every decision the question rests on by id, ACCEPTED ones as rules and a PROPOSED
one as "proposed"; `constrains:` holds ticket ids only (DEC-1073).
-->

## Question

## Why now

## Current state

## Options

## Impact

## Reversibility

## Cost of rework

## Recommendation

<!-- Required. Name one option. A package without a recommendation is not sent. -->

## Confidence

<!-- Required. One of: low, medium, high. A package without a confidence is not sent. -->

## Exact permitted next actions

<!-- What may be done while this is open, and what each option permits once it is answered. -->

## Answer

<!-- Filled when the owner answers; empty while the package is open. -->

- Option chosen:
- Decision record: DEC-000, appended as ACCEPTED (who, YYYY-MM-DD)

Who decided and the date are both required: an answer without a date is not recorded.
