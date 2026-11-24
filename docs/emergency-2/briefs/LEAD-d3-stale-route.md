# Lead brief: W2-212, the route that keeps stale, superseded and legacy documents out of default memory (D3; DEC-1227 D3 (a))

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Where this brief leaves a choice, make it and say what you chose in your return.

## Why
The owner, 2026-11-24: "The measured visible half missed by two stale citations: build the route that keeps stale and superseded documents out of default memory (D3) now, on its own, in 0.1.6, not waiting for the imports feature." DEC-1227 D3 (a) approved it (read it in `docs/DECISION_REGISTER.md`); DEC-1228 (1) had tied it to the imports feature, and the owner's message frees it. The evidence is `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`: read lines 125 to 260 (in particular the paragraph "Why the stale sources are in the bundle at all", row A6 of its fix table and fix 6 at its end). In 25 of the proving run's 29 misses, a stale or superseded document stayed retrievable because nothing in adoption (path map, A2, A3, the skill, the brief) sets the knobs the product already has (`lexical_policy`, `embedding_policy`, `retrieval_authority`), and the record graph demotes only records with `status: superseded` or a SUPERSEDES edge.

## The ticket (new; approved feature)
Open `.tickets/` W2-212 on your branch in the form of an open ticket (look at `.tickets/DAEO-rt4s.md`; use the repository's ticket tool if one exists, else by hand with a fresh `DAEO-xxxx` id), `kind: feature`, `specification: docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` (its row A6 and fix 6 are the spec), with these KPI lines, each with its verify and a failure line:
- **SR-1 Out of the default bundle.** In an adopted repository, a document in a namespace the path map marks superseded, historical or legacy (a declared class on the namespace, not a guess from its name) is absent from `gov retrieve`'s default bundle, lexical and semantic alike, and a current document on the same topic is present. Verify as fix 6 says: the python-app stand-in's `docs/design/lending.md` absent for the lending question, `lending-v2.md` present.
- **SR-2 Still findable on purpose.** Such a document is still found when asked for by path or by an explicit flag (choose the flag; for example `gov retrieve --include-stale`), and the bundle says it is stale when it shows it.
- **SR-3 Adoption sets it.** The adopt skill and the A3 form give such namespaces the declared class with `lexical_policy: not indexed` and `embedding_policy: not embedded`, and say so; A3 refuses a namespace named or described as superseded, historical, legacy or archive that lacks the class (a notice naming it is enough where the name alone is ambiguous: choose and say which).
- **SR-4 Every adopted repository gets it.** `gov update` carries the route; in an adopted repository whose path map already has such namespaces without the class, `gov doctor` names each one with the line to add (a notice, never a failure), so EXAMIN and ASMO OS can mark theirs. Gov OS's own path map: say which of its namespaces would take the class (do not edit Gov OS's live map; the CTO does).

Kernel text you may change (the CTO approves it by naming it here): the adopt skill under `template/governance/kernel/skills/adopt/` and the A3 form's text.

Code area: `src/gov/retrieval/` (the namespace filter), `src/gov/adopt/` (A3 form and its check), `src/gov/doctor/` (the notice part only), the path-map schema under `template/governance/kernel/schemas/` (a property added to an existing schema). Stay out of `src/gov/rebuild*` beyond reading the policy (the Phase 0 lead changes the refresh), and out of `src/gov/memaudit/`, `src/gov/dispatch/`, `src/gov/resources/`, `src/gov/launch/`, `src/gov/decisions/`, `src/gov/usage/` (other leads).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-d3-stale-route`, branch `e2/d3-stale-route` from `w2/integrate`.

## Green
LEAD-COMMON's flow (test designer first, red on the base, planted repositories only; then the engineer). Then exactly the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue <the new ticket's DAEO id>=e2/d3-stale-route --onto w2/integrate --select` (if `gov queue` refuses `TICKET_UNKNOWN` because the ticket file is only on your branch, say so in your return: the CTO places the ticket file on `w2/integrate` first, as for W2-210), through the heavy slot (DEC-1244 X-1); `gov accept` through the heavy slot too. Errors in `tests/acceptance/W1-35/` or `tests/unit/dispatch/` run together are I-22, not yours. Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; SR-1 to SR-4 with tests and result; the selected suites' summary lines; the namespaces of Gov OS's and EXAMIN's path maps (read only) that would take the class; reds not yours; the C3-trial counts.
