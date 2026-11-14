"""W2-60a, KPI failure 3, round 2 -- the owner's user-level permission rules still reach the session.

KPI failure 3: "A refusal the launcher makes today that no longer refuses".
KPI success 6 keeps the user settings out (``--setting-sources project,local``,
``test_w2_60a_kept_out.py``), and that drops the user settings file
``~/.claude/settings.json`` as a whole; before this ticket a launched worker got
that file's ``permissions.ask`` and ``permissions.deny`` rules (on the owner's
machine, ``ask`` rules for ``rm`` and for ``owner-ping``, which make a ``-p``
worker's ``rm`` refused). So a protection a launched worker has today would be
lost.

Review 1's finding F2, as a behaviour (DEC-136, DEC-802): every string of the
user settings file's ``permissions.ask`` and ``permissions.deny`` lists is in
the ``--settings`` value's ``permissions.ask`` and ``permissions.deny``, beside
the launcher's own deny rules, which stay; nothing else of the user settings
file is carried (no ``allow`` rule, no ``defaultMode``, no ``env``, no
``model``, no ``effortLevel``, no hooks). A user settings file that is absent
carries nothing and launches. One that exists but cannot be read, is not a JSON
object, or whose ``permissions`` is not a map or whose ``ask`` or ``deny`` is
not a list of strings refuses the launch: it cannot be shown to keep its
protections.

The test home's user settings file (``w2_60a_support.user_settings``) holds
``ask`` and ``deny`` rules, an ``allow`` rule, a ``defaultMode``, an ``env``
variable, a model, an effort and a hook. A refusal is held to
``LAUNCH_REFUSED`` and "settings", after a control launch in the same home whose
user settings file is well formed.
"""

from __future__ import annotations

import json
import os
import stat

import pytest

import w2_60a_support as s


def _user_file(sandbox):
    return sandbox.home / s.USER_SETTINGS_REL


def _permissions(result):
    block = result.settings().get("permissions")
    assert isinstance(block, dict), f"the --settings value has no permissions map: {result.settings()}"
    return block


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_the_user_s_ask_and_deny_rules_reach_the_session_beside_the_launcher_s_own(sandbox, launch, role):
    plain_home = _user_file(sandbox).read_text(encoding="utf-8")
    _user_file(sandbox).unlink()
    without = launch(role)
    s.assert_launched(without)
    s.write(_user_file(sandbox), plain_home)
    result = launch(role)
    s.assert_launched(result)
    permissions = _permissions(result)
    for key, planted in (("ask", s.USER_ASK), ("deny", s.USER_DENY)):
        listed = permissions.get(key) or []
        missing = [rule for rule in planted if rule not in listed]
        assert not missing, f"the user settings' {key} rules {missing} are not in the session's permissions.{key}"
    lost = [rule for rule in s.deny_rules(without.settings()) if rule not in s.deny_rules(result.settings())]
    assert not lost, f"the launcher's own deny rules {lost[:5]} are gone once the user's rules are carried"


def test_nothing_else_of_the_user_settings_file_is_carried(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    settings = result.settings()
    permissions = settings.get("permissions") or {}
    text = json.dumps(settings)
    carried = [rule for rule in s.USER_ALLOW if rule in text]
    assert not carried, f"the user settings' allow rules {carried} reached the session's settings"
    assert permissions.get("defaultMode") != s.USER_MODE, "the user settings' defaultMode reached the session"
    assert s.USER_VARIABLE not in (settings.get("env") or {}), "the user settings' env reached the session's env"
    assert s.HAIKU not in text, f"the user settings' model {s.HAIKU} reached the session's settings"
    assert settings.get("effortLevel") in (None, s.DEFAULTS[s.ENGINEER][1]), (
        f"the session's settings carry the user's effortLevel {settings.get('effortLevel')!r}")
    assert f"echo {s.USER_WORD}" not in text, "the user settings' hook reached the session's settings"


def test_an_absent_user_settings_file_carries_nothing_and_launches(sandbox, launch):
    _user_file(sandbox).unlink()
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert not (result.settings().get("permissions") or {}).get("ask"), (
        f"no user settings file, but the session's settings carry ask rules: {result.settings().get('permissions')}")


CARRY_NOTHING = {
    "no-permissions": {"model": s.HAIKU},
    "allow-only": {"permissions": {"allow": list(s.USER_ALLOW)}},
    "empty-lists": {"permissions": {"ask": [], "deny": []}},
}


@pytest.mark.parametrize("case", sorted(CARRY_NOTHING))
def test_a_user_settings_file_with_no_ask_or_deny_rule_launches(sandbox, launch, case):
    s.write(_user_file(sandbox), json.dumps(CARRY_NOTHING[case]) + "\n")
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert not (result.settings().get("permissions") or {}).get("ask"), (
        f"the user settings have no ask rule, but the session's settings carry some: "
        f"{result.settings().get('permissions')}")


# --------------------------------------------------------------------------
# Refusals: a user settings file that cannot be shown to keep its protections
# --------------------------------------------------------------------------

def _unreadable(path):
    if os.geteuid() == 0:
        pytest.skip("an unreadable file does not stop root")
    path.chmod(0)


def _a_folder(path):
    path.unlink()
    path.mkdir()


def _text(text):
    return lambda path: path.write_text(text, encoding="utf-8")


def _json(data):
    return _text(json.dumps(data) + "\n")


FAULTS = {
    "unreadable": _unreadable,
    "a-folder": _a_folder,
    "not-json": _text("{ not json\n"),
    "not-an-object": _json(list(s.USER_ASK)),
    "permissions-not-a-map": _json({"permissions": list(s.USER_ASK)}),
    "ask-not-a-list": _json({"permissions": {"ask": s.USER_ASK[0]}}),
    "ask-holds-a-non-string": _json({"permissions": {"ask": [s.USER_ASK[0], 3]}}),
    "deny-not-a-list": _json({"permissions": {"deny": {s.USER_DENY[0]: True}}}),
    "deny-holds-a-non-string": _json({"permissions": {"deny": [None]}}),
}


@pytest.mark.parametrize("case", sorted(FAULTS))
def test_a_user_settings_file_that_cannot_be_shown_to_keep_its_rules_refuses_the_launch(sandbox, launch, case):
    s.assert_launched(launch(s.ENGINEER))
    path = _user_file(sandbox)
    FAULTS[case](path)
    try:
        s.assert_refused(launch(s.ENGINEER), "LAUNCH_REFUSED", "settings")
    finally:
        if path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)
