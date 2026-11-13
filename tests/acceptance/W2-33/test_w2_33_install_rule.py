"""W2-33 S9 and F1: the CTO-only install rule in both copies of the template's orchestrator role file, and the old
wording ("the guard asks on every install") in neither. Tests read the two files only.

The rule (DEC-971 item 4, DEC-957): only the orchestrator on the project's coordination ticket is asked for an install;
every other session is refused; the key is ``coordination_ticket`` (``governance/project/roster.yaml``) and the session
is the one whose ``GOV_TICKET`` is that ticket. The statements are judged by their words (``w2_33_support``).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_33_support as W  # noqa: E402

COPIES = (W.KERNEL_ORCHESTRATOR_REL, W.RULESYNC_ORCHESTRATOR_REL)


def _text(rel):
    path = W.REPO_ROOT / rel
    assert path.is_file(), f"{rel} does not exist"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("rel", COPIES)
def test_s9_the_copy_states_the_cto_only_install_rule_and_names_the_key_and_gov_ticket(rel):
    W.matcher_selfcheck("s9")
    faults = W.install_rule_faults(rel, _text(rel))
    assert not faults, "\n".join(faults)


@pytest.mark.parametrize("rel", COPIES)
def test_f1_the_copy_does_not_say_the_guard_asks_on_every_install(rel):
    # The pattern first: it must match the old wording and its close variants and must not match the new rule.
    for variant in W.OLD_VARIANTS:
        assert W.old_rule_lines(variant), f"the old-wording pattern misses the variant {variant!r}"
    for sample in W.NEW_RULE_SAMPLES:
        assert not W.old_rule_lines(sample), f"the old-wording pattern matches the new rule {sample!r}"
    found = W.old_rule_lines(_text(rel))
    assert not found, f"{rel} still says the guard asks on every install ({len(found)} statement(s)): {found}"
