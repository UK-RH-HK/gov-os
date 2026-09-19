#!/usr/bin/env bash
# P2-AR-0016 evidence adapter (NOT product code): runs the real `gov` with `--role orchestrator` injected when the
# invocation declares no role (no --role argument and no GOV_ROLE). The audit-of-record probes relied on the removed
# default-orchestrator behaviour for their setup steps; this adapter declares the role those steps assumed, so the
# probes' other checks can be evaluated. Invocations that declare a role (flag or GOV_ROLE) pass through untouched.
REAL="${WS03_REAL_GOV:?set WS03_REAL_GOV to the gov binary (not GOV_*: probe harnesses strip GOV_* variables)}"
for a in "$@"; do [ "$a" = "--role" ] && exec "$REAL" "$@"; done
[ -n "${GOV_ROLE:-}" ] && exec "$REAL" "$@"
exec "$REAL" --role orchestrator "$@"
