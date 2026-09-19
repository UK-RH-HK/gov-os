# Fixture 5 — Upstream learning / export security

A governed project (created by `gov init` in the harness) with four lessons that exercise the Upstream Export Gate
(framework §75E-G, protocol §13-14, INV-012 fail closed):

| Lesson | Scope | Expected outcome |
|---|---|---|
| `L-0001` | FRAMEWORK, clean, with a synthetic reproducer | packet prepared, submitted to `lessons/inbox/`, ledger written, lifecycle → promoted |
| `L-0002` | PROJECT | `UPSTREAM_SCOPE` — never eligible |
| `L-0003` | FRAMEWORK but contains an AWS key, a customer name, raw code and a product path | `UPSTREAM_BLOCKED` with reasons; `blocked.json` written; no packet |
| `L-0004` | FRAMEWORK with project/customer identifiers in prose | prepared with redactions; packet text contains no identifier |

Negative controls: submission without approval (`HUMAN_GATE_REQUIRED`), remote URL destination
(`REMOTE_TRANSPORT_NOT_CONFIGURED`), fixture files under a forbidden outbound path (blocked), the inbox receives only
`packet.yaml` and declared synthetic fixture files, and a grep of the inbox finds no secret, customer or project
identifier.

**First-run path: provision, then install (OWNER-DECISION-P2-0002).** The harness provisions each scenario machine with the certification suite's throw-away test root (`tests/certification/common.rs::provision`, published-seed keys — never a production root) and installs a release signed under it (`gov init --source <signed release>`; `common::signed_source`). A machine with no trust anchor refuses kernel material from any external source; only the `gov` binary's own embedded payload may be installed there, as a marked bootstrap installation that is never presented as current, verified or certified.
