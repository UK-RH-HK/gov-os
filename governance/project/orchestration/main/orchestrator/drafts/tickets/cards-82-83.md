#### W2-82 A Definition of Ready: gov claim checks it, and gov launch refuses a lead on a ticket that is not ready (STANDARD, engineer; DEC-944 item 2; EXAMIN minimum)
- **Why:** a ticket can be claimed and launched today with any file at all. Adopted products need the check from their first ticket.
- **Starts:** priority 5 (DEC-946), after W2-60a and W2-56 merge (both hold `src/gov/launch/launcher.py`).
- **Allowed paths:** `src/gov/tasks/dor.py`, `src/gov/claim/**`, `src/gov/launch/launcher.py` (the ticket check only), the kernel's `templates/ticket.md` and `schemas/ticket.schema.json` (CIT-P for these two only), their unit tests, the CIT-P and CIT-E; acceptance tests in `tests/acceptance/W2-82/`.
- **KPIs, success:**
  - `gov claim` sets `in_progress` only when the six conditions hold (sources resolving; allowed paths; KPIs with at least one success line citing an id; profile; acceptance-test path; dependencies met), and otherwise names every failing condition and writes nothing;
  - `gov launch` refuses a lead on a ticket that is not ready;
  - fail closed; the kernel carries the rule.
- **KPIs, failure:** a not-ready ticket claimed or launched; a condition that cannot be judged treated as met; any ticket-file rewrite by the guard (Wave 3).

#### W2-83a A playbook per stream: the form in the kernel template, its schema in gov check, and the adopt step (STANDARD, product-spec; DEC-944 item 3; EXAMIN minimum)
- **Why:** an adopted product should start with the form for its streams: purpose, standing practices, usual ticket classes, roles and the skills they load.
- **Starts:** priority 5 (DEC-946), after W2-64 (which holds `src/gov/check/schema.py`).
- **Allowed paths:** the kernel's `templates/playbook.md` and `schemas/playbook.schema.json`, the schema map's one line in `src/gov/check/schema.py`, the adopt skill and its copies, unit tests, the CIT-P and CIT-E; acceptance tests in `tests/acceptance/W2-83a/`.
- **KPIs, success:** the form and its schema in the kernel; `gov check` refuses a playbook missing any part; adoption writes the form into a product, which passes `gov check`; nothing project-specific in the kernel.
- **KPIs, failure:** an incomplete playbook passes; a rule of this repository in the kernel; a kernel file changed without its CIT-P.

#### W2-83b This project's nine keystone playbooks, placing annex D's standing practices (STANDARD, product-spec; DEC-944 item 3; spare capacity only)
- **Why:** 39 of annex D's 80 standing practices live only in the orchestrator's prompt, briefs and tools.
- **Starts:** after W2-83a, in spare capacity only, never ahead of the standing priorities (DEC-946).
- **Allowed paths:** `docs/playbooks/**`; acceptance tests in `tests/acceptance/W2-83b/`.
- **KPIs, success:** nine playbooks in W2-83a's form; every annex D practice placed, or marked retired or project-only with its reason; every class and skill named exists.
- **KPIs, failure:** a practice dropped; a skill or class named that does not exist.
- **Kept current:** updated with each new standing rule of its stream (DEC-944 item 3).
