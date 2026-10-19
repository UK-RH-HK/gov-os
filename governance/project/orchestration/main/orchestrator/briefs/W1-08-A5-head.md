You are the ticket lead for ticket `DAEO-uudf` (`W1-08`, "Record schemas and templates"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-08` on branch `w1/W1-08`. You run the ticket loop for this one ticket. Its implementer is a product-spec worker (brief A4, ticket mode), not an engineer. STANDARD has no reviewer step.

## State of this ticket

- Acceptance tests exist from test design batch 1 (`18b837e8`, `aa80f5bd`): 264 cases, red. The suite's README holds the designer's readings and its seven packages. Nothing is implemented.
- Every package is now decided. Read them in the register: DEC-224 (the project floor lives in `path-map.yaml`), DEC-225 (namespace `paths` patterns, exactly one namespace per tracked path, `memory_class` governance or product), DEC-226 (lesson scope and severity in lower case), DEC-227 (one shared definitions file for every id grammar), DEC-228 (W1-08 does not change `src/gov/config/`; the path map must still load in the minimal loader; W1-27 replaces the minimal schema), DEC-229 (`state_class`, six values; template defaults), DEC-230 (top-level keys `capabilities`, `policies`, `systems`; strength order; thirteen policy keys; twenty-two systems), DEC-238 (the kernel minimum per policy; `capabilities` is a closed list: `code_intelligence` with `languages`, and `research_corpus`), DEC-239 (identity keys: `id`, `type`, `status` required; `lifecycle`, `version`, `provenance`, `supersedes`, `superseded_by`, `consumers` optional; canonical path and `content_hash` derived by `gov`, not stored).
- The KPI line now reads "… are in the shared frontmatter or derived by gov" (DEC-239).
- The 48 committed tickets already carry `state_class: AUTHORITATIVE` (DEC-229, commit `c7aba533`).
- Older tracked schemas exist under `schemas/records/` (record, decision, lesson, checkpoint, research); the implementer may use them as a source. They are outside the ticket's `allowed_paths` and stay unchanged.

## What you do, in order

1. **Test design batch 2** (brief A1, a fresh designer, profile STANDARD, DEC-221: every KPI line's success and failure plus the key edge cases, no combinatorial expansion). It revises the suite for DEC-224 to DEC-230, DEC-238 and DEC-239, before implementation. Expected revisions of `tests/acceptance/W1-07/test_w1_07_config_details.py` only if a key the minimal loader checks changes (DEC-189, DEC-228); each is reported with its reason.
2. **Check red** yourself.
3. **Product-spec worker** (brief A4, ticket mode, fresh, role `product-spec`): the schemas under `template/governance/kernel/schemas/`, the templates under `template/governance/kernel/templates/`, and `governance/project/path-map.yaml`, which classifies every tracked path and must still load in the minimal loader in `src/gov/config/`.
4. **Verify** every suite and the validator.

