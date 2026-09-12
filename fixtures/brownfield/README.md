# Fixture 2 — Deliberately dirty brownfield (mixed Python + TypeScript)

`shipping-quotes` is a legacy repository that has lived through three agent tools and two governance attempts.
It intentionally contains every hazard listed in framework §75C and protocol §7.2:

| Hazard | Where |
|---|---|
| Old provider/IDE-specific rule files, contradicting each other and claiming authority | `.cursorrules`, `AGENT_RULES_v2.md`, `.github/copilot-instructions.md` |
| Old chat/session memory stores with buried decisions and a secret | `memory/chat_history.sqlite` (built by the harness from `memory/chat_history.sql`), `.chat/sessions.jsonl` |
| Stale vector/index store referencing files that no longer exist | `.index/vectors.json`, `.index/manifest.json` |
| Contradictory specifications (retry limit 3 vs 5) | `docs/decisions/ADR-001-retries.md` vs `specs/requirements.md` |
| Governed record superseded but still ACTIVE (supersession conflict) | `spec/decisions/D-0001.yaml` ← `spec/decisions/D-0002.yaml` |
| Duplicated decision id | `docs/old/decision-2-copy.yaml` (id D-0002) |
| Misplaced files (spec under src, test under docs, source under docs) | `src/specs/feature-login.md`, `docs/test_utils.py`, `docs/legacy_module.py` |
| Code/spec disagreement | `src/app/retry.py` (`MAX_RETRIES = 3`) vs `specs/requirements.md` (5) |
| Missing tests | `src/app/billing.py` has none |
| Stale test | `tests/test_retry.py` asserts an old limit |
| Dead code | `src/app/old_export.py` (unreferenced) |
| Secrets that must never be indexed or exported | `.env`, `config/secrets.yaml`, and a **planted secret in a non-secret path** `src/app/config.py` |
| Broken graph edge | `spec/decisions/D-0002.yaml` references a missing requirement |

Exercised by `tests/certification/brownfield.rs`: full A0→A11 adoption with independence enforced (reviewer/verifier
sessions must differ from planner/executor/builder), legacy authority retired (INV-004), secrets never indexed (INV-009),
contradictions surfaced and resolved through CIT with a human gate, remediation iteration, final adoption verdict.
