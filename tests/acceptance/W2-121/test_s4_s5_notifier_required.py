"""S4 and S5, review round 1 finding F-3: the notifier is required at load, and no configuration error comes late.

Reading fixed by the fix round: ``notifier_command`` is a required key. Missing, empty or not an argv list is a
configuration error at load: exit 2 naming ``notifier_command``, nothing started, and the first line of ``status.txt``
``PASS FAILED <time>: ...notifier_command...`` with ``"ok": false`` and the reason in ``status.json`` (as for every other
missing key). No pass raises a configuration error after it has started a session: every key the pass reads later (the
unread time, the never-ran time, the job markers, the probes folder, the history file) is checked at load too, so a
malformed one is exit 2, named, with nothing started even where an entry would start.
"""

from __future__ import annotations

import re

import pytest

import w2_121_support as support
from w2_121_support import explain


def assert_failed_at_load(p, r, key: str) -> None:
    assert r.code == 2, r
    assert key in r.out + r.err, f"the configuration error does not name {key}\n{r}"
    p.settle(0.5)
    assert p.launches() == [], "a session started although the configuration is in error"
    assert p.started() == [], p.started()
    text = p.status_text() if (p.state / "status.txt").is_file() else ""
    first = text.splitlines()[0] if text else ""
    assert re.match(rf"PASS FAILED\b.*{key}", first), f"first line of status.txt: {first!r}\n{explain(p, r)}"
    status = p.status_json()
    assert status.get("ok") is False, status
    reasons = [v for v in support.values_under(status, "reason") + support.values_under(status, "error")
               if isinstance(v, str) and key in v]
    assert reasons, f"status.json names no reason that holds {key}: {status}"


@pytest.mark.parametrize("how", ["missing", "empty-list", "null", "string", "empty-string"])
def test_s4_a_dispatch_yaml_without_a_usable_notifier_command_is_exit_2_at_load(project, how):
    p = project
    entry = p.add_ticket(901)
    if how == "missing":
        p.cfg_drop("notifier_command")
    else:
        p.cfg(notifier_command={"empty-list": [], "null": None, "string": "notify-send", "empty-string": ""}[how])
    p.ready(entry)
    assert_failed_at_load(p, p.tick(), "notifier_command")


def test_s5_a_missing_notifier_command_fails_the_pass_at_the_top_of_a_status_that_was_good(project):
    p = project
    entry = p.add_ticket(901)
    assert p.tick().code == 0
    assert p.status_json().get("ok") is True
    p.cfg_drop("notifier_command")
    p.ready(entry)
    r = p.tick()
    assert_failed_at_load(p, r, "notifier_command")
    assert p.status_text().splitlines()[0] != "", p.status_text()


@pytest.mark.parametrize("key, value", [("unread_escalate_s", "soon"), ("unread_escalate_s", -1),
                                        ("never_ran_after_s", -1), ("never_ran_after_s", "late"),
                                        ("job_markers", "lead"), ("probes_dir", 5), ("history", 5)])
def test_s5_a_malformed_value_read_later_in_the_pass_is_exit_2_at_load_with_nothing_started(project, key, value):
    p = project
    entry = p.add_ticket(901)
    p.cfg(**{key: value})
    p.ready(entry)
    assert_failed_at_load(p, p.tick(), key)
