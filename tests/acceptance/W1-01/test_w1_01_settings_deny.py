"""W1-01: deny rules in ``.claude/settings.json``.

Each test makes one attempt against the repository's deny rules, the way an
implementer session would, and expects it to be denied. The rule model is in
``w1_01_support.py``.

D-4 (DEC-1061, row D1 approved by DEC-1040 (1)): the interim guardrail's cases
(the acceptance-test, install and pipe-to-shell deny rules, and ordinary work
left alone), which skipped on every run since W1-05 retired the guardrail
(DEC-084), are deleted with their ``interim`` fixture. The guard's own cases
carry those rules now (W1-02, W1-04, W1-05, W1-33, W1-47, and
``tests/unit/hooks/test_live_hook.py``).
"""

from __future__ import annotations

import pytest

import w1_01_support as support

# KPI success 1 — secret files (DEC-074 Q9, CAP-03): one attempt per pattern at
# the repository root, and one below it for the patterns that name no directory.
SECRET_PATHS = [
    pytest.param(".env", id="dotenv"),
    pytest.param(".env.local", id="dotenv-suffix"),
    pytest.param("services/api/.env.production", id="dotenv-nested"),
    pytest.param("server.pem", id="pem"),
    pytest.param("deploy/tls/server.pem", id="pem-nested"),
    pytest.param("signing.key", id="key"),
    pytest.param("ops/keys/deploy.key", id="key-nested"),
    pytest.param("config/secrets.yaml", id="config-secrets"),
]


@pytest.mark.parametrize("path", SECRET_PATHS)
@pytest.mark.parametrize("tool", ["Edit", "Write"])
def test_write_to_secret_file_is_denied(deny_rules, tool, path):
    hits = support.denying_rules(deny_rules, tool, path)
    assert hits, f"{tool} on {path} is not denied by {support.SETTINGS_REL}"


# KPI failure 2 (a docs/source deny rule lost) is retired by DEC-925 item 1: docs/source left the tree on
# 2026-10-01 and DEC-922's settings regeneration dropped its two deny rules (P-I1-2, DEC-899). README, "Failure 2".
