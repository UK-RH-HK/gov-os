"""W2-121c, RT-2 every end of a launched session is one wake message to whoever launched it (success line 5).

``gov launch`` of a planted worker on W2-60a's recording stand-in CLI (behind a wrapper that captures the session's
registry entry while it runs) under a fixture HOME: at the session's end the launcher sends one ``wake`` message to the
launching process's ``$GOV_MSG_ADDRESS`` (else ``cto``) with the id ``end:<boot>:<pid>:<start_ticks>`` of its registry
entry; the session's environment carries ``GOV_MSG_ADDRESS=<role>:<ticket>``; the entry carries ``notify`` and
``address``.
"""

from __future__ import annotations

import re

import w2_121c_support as s

LAUNCHER = "lead:DAEO-x"
EXIT_CODE = 5


def _launched(tmp_path, extra_env):
    kit = s.LaunchKit(tmp_path, rubric=True)
    kit.exit_with(EXIT_CODE)
    result = kit.launch(extra_env=extra_env)
    assert len(result.calls) == 1, f"gov launch did not start the stand-in once\n{result.describe()}"
    return kit, result


def _end_message(kit, address):
    found = s.poll(lambda: [m for m in kit.messages(address) if m.get("kind") == "wake"], 5.0)
    assert found, f"no wake message in {address}'s inbox within 5 s of the session's end"
    assert len(found) == 1, f"{len(found)} wake messages in {address}'s inbox, not one: {found}"
    return found[0]


def test_rt2a_the_end_is_one_wake_message_to_the_launching_address_naming_role_ticket_and_exit_code(tmp_path):
    kit, result = _launched(tmp_path, {"GOV_MSG_ADDRESS": LAUNCHER})
    role, ticket = kit.s.ENGINEER, kit.ticket
    message = _end_message(kit, LAUNCHER)
    words = s.message_words(message)
    assert role in words and ticket in words, f"the end message does not name the role and the ticket: {message}"
    assert re.search(rf"\b{EXIT_CODE}\b", words), f"the end message does not name exit code 5: {message}"

    seen = kit.registry_entries()
    assert len(seen) == 1 and seen[0]["entry"], f"the session's registry entry was not seen while it ran: {seen}"
    entry = seen[0]["entry"]
    assert message.get("id") == s.end_id(entry), (
        f"the end message's id is {message.get('id')!r}, not the entry's {s.end_id(entry)!r}")
    assert entry.get("notify") == LAUNCHER, f"the registry entry's notify: {entry.get('notify')!r}"
    assert entry.get("address") == f"{role}:{ticket}", f"the registry entry's address: {entry.get('address')!r}"
    assert result.calls[0]["env"].get("GOV_MSG_ADDRESS") == f"{role}:{ticket}", (
        f"the session's environment has GOV_MSG_ADDRESS={result.calls[0]['env'].get('GOV_MSG_ADDRESS')!r}")
    assert result.run.returncode == EXIT_CODE, f"gov launch exited {result.run.returncode}, not the session's 5"


def test_rt2a_without_gov_msg_address_the_end_message_goes_to_cto(tmp_path):
    kit, result = _launched(tmp_path, None)
    message = _end_message(kit, "cto")
    assert kit.ticket in s.message_words(message), f"the end message does not name the ticket: {message}"
    entry = kit.registry_entries()[0]["entry"] or {}
    assert entry.get("notify") == "cto", f"the registry entry's notify: {entry.get('notify')!r}"
