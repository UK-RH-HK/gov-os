# W2-110 (DAEO-3r1j) design note: a product's CTO-only install rule

Sources: DEC-971 item 4, DEC-957 (install rule), DEC-966 item 1, DEC-163, DEC-083 (DEC-040 amended). Model: this
repository's five-rule hook, rule 4 (`.claude/hooks/pretooluse.py`: CTO = session role `orchestrator`, acting role
`orchestrator`, session ticket whose WBS id is `W2-00`, hard-coded there).

## The one key

- **File:** `governance/project/roster.yaml` in the generated project (the project's overlay, which `copier update`
  never overwrites; `_skip_if_exists: governance/project/**`).
- **Key:** top-level `coordination_ticket: <ticket>`, a non-empty string: the coordination ticket's id (its file name
  under `.tickets/` without `.md`, as `GOV_TICKET` names it) or its WBS id (`wbs_id`). Set at adoption, by the owner or
  by adoption (adoption's writer is outside this ticket's paths: residual). Never written in the code.
- The key **resolves** when exactly that name is a ticket in `.tickets/` (by file name, or by `wbs_id`), as the
  kernel guard already resolves a session's ticket (`_load_ticket`).

## How the hook decides (install branch only)

1. sudo: refused to every role (unchanged, first).
2. not an install: unchanged.
3. frozen project: install refused (unchanged, before any role is looked at).
4. research in its experiment folder: allowed (DEC-163, unchanged).
5. **CTO:** session role (`GOV_ROLE`) is `orchestrator`, the acting role is `orchestrator` (main thread, or a
   declared orchestrator subagent in that session, as today), the key resolves to a ticket, and the session's ticket
   (`GOV_TICKET`) resolves to the same ticket file: **ask** the owner, with today's text (tool-registry record
   required) and today's record and snapshot.
6. **Everyone else** (a lead = orchestrator on another ticket, an orchestrator with no ticket, engineer, test
   designer, product-spec, auditor, ticket-lead, research outside its folder, no role): **deny**, saying to raise the
   install as a P1 escalation to the CTO, who asks the owner.
7. **No key, an unreadable or invalid file, a non-string or empty value, or a key naming no ticket:** every install
   refused, for every session (fail closed); the refusal names the file and the key and says how to set it. Any
   exception in reading the key is a refusal, never an ask.

## Unchanged

sudo refused to every role; the research exception inside its experiment folder; a frozen project refusing installs;
the owner's ask text and its tool-registry record; `decide()` and every non-install path; this repository's own
five-rule hook. W2-05 shares `src/gov/guard/install.py`: only the install decision's own function range is touched.
