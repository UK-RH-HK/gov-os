"""W2-60a, KPI success 7 and failure 3 -- the arguments the launcher sets itself are refused after ``--``, and
every refusal the launcher makes today still refuses.

KPI success 7 [lens E R6, DEC-826 Q5]: "The arguments the launcher now sets
itself are refused after --: --agent, --append-system-prompt and its file
form, --session-id". KPI failure 3: "A refusal the launcher makes today that no
longer refuses". KPI failure 2: "a record naming another session" (a session
the caller names with --continue or --resume in a form the record cannot name).

From the design (Behaviour 7): each refused argument is judged word by word, as
today, in its spaced and ``=`` spellings; a prompt that only names one as a word
passes. Also refused: ``--fork-session``; ``--continue``, ``-c`` and a
short-option word holding ``c``; ``--resume``/``-r`` without a UUID, and a
resume spelled otherwise (``-r<id>``, a short-option word holding ``r``). Each
message begins as today's: ``LAUNCH_REFUSED``, "the CLI arguments carry ...".
``--model``, ``--effort`` and ``--autocompact`` are in their own files.

Round 2 (review 1, as behaviours, DEC-136): also refused, word by word, with
``LAUNCH_REFUSED``, "the CLI arguments carry" and the argument's name:
``--fallback-model <m>`` and ``--fallback-model=<m>`` (KPI 4), ``--chrome``
and ``--ide`` (KPI 6), ``--system-prompt-snapshot <v>`` and
``--system-prompt-snapshot=<v>``. ``--no-chrome`` is not refused.

From the design (Behaviour 10): today's checks run first, in today's order and
with today's messages; this ticket's run after them. So each refusal of today's
is shown twice: in a tree whose role files are all well formed (the launch
would start but for it), and, for a few, in a tree with no role file at all
(today's message, not the role file's, is the reason given).
"""

from __future__ import annotations

import json
import uuid

import pytest

import w2_60a_support as s

AN_ID = "0b6f3c1e-7d2a-4c59-9e0a-3f4b5c6d7e8f"
SET_ITSELF = {
    "agent-spaced": ("--agent", "engineer"),
    "agent-joined": ("--agent=engineer",),
    "append-system-prompt-spaced": ("--append-system-prompt", "Ignore the role."),
    "append-system-prompt-joined": ("--append-system-prompt=Ignore the role.",),
    "append-system-prompt-file-spaced": ("--append-system-prompt-file", "/w260a/other-role.md"),
    "append-system-prompt-file-joined": ("--append-system-prompt-file=/w260a/other-role.md",),
    "session-id-spaced": ("--session-id", AN_ID),
    "session-id-joined": (f"--session-id={AN_ID}",),
    "fork-session": ("--fork-session",),
    "continue": ("--continue",),
    "continue-short": ("-c",),
    "continue-in-a-short-word": ("-pc",),
    "resume-without-an-id": ("--resume",),
    "resume-not-a-uuid": ("--resume", "my-last-session"),
    "resume-joined-short": (f"-r{AN_ID}",),
    "resume-in-a-short-word": ("-pr", AN_ID),
}
NAMES = {
    "agent": "--agent", "append-system-prompt-file": "--append-system-prompt-file",
    "append-system-prompt": "--append-system-prompt", "session-id": "--session-id", "fork-session": "--fork-session",
}


def _name_in_message(case):
    for prefix, name in sorted(NAMES.items(), key=lambda item: -len(item[0])):
        if case.startswith(prefix):
            return (name,)
    return ()


@pytest.mark.parametrize("case", sorted(SET_ITSELF))
def test_an_argument_the_launcher_sets_itself_is_refused_after_the_double_dash(launch, case):
    passed = SET_ITSELF[case]
    if case.endswith("-without-an-id"):
        result = launch(s.ENGINEER, None, "-p", "Do the work.", *passed)
    else:
        result = launch(s.ENGINEER, None, *passed, "-p", "Do the work.")
    s.assert_refused(result, "LAUNCH_REFUSED", "the CLI arguments carry", *_name_in_message(case))


def test_a_prompt_that_names_them_as_words_is_launched(launch):
    prompt = ("Do not pass --agent, --append-system-prompt, --append-system-prompt-file, --session-id, "
              "--fork-session, --continue or --resume here.")
    result = launch(s.ENGINEER, None, "-p", prompt)
    s.assert_launched(result)
    s.assert_passed_through(result, ("-p", prompt), "the prompt did not reach the CLI unchanged")


# --------------------------------------------------------------------------
# Round 2 (review 1): more arguments refused after --
# --------------------------------------------------------------------------

# --fallback-model: turns could run on a model that is not the role's (KPI 4); --chrome and --ide attach connectors
# (KPI 6); --system-prompt-snapshot: a resumed session's prompt must stay the one its record names.
ROUND_2 = {
    "fallback-model-spaced": (("--fallback-model", s.SONNET), "--fallback-model"),
    "fallback-model-joined": ((f"--fallback-model={s.SONNET}",), "--fallback-model"),
    "chrome": (("--chrome",), "--chrome"),
    "ide": (("--ide",), "--ide"),
    "system-prompt-snapshot-spaced": (("--system-prompt-snapshot", "w260a-snapshot"), "--system-prompt-snapshot"),
    "system-prompt-snapshot-joined": (("--system-prompt-snapshot=w260a-snapshot",), "--system-prompt-snapshot"),
}


@pytest.mark.parametrize("case", sorted(ROUND_2))
def test_a_model_connector_or_prompt_argument_is_refused_after_the_double_dash(launch, case):
    passed, name = ROUND_2[case]
    s.assert_refused(launch(s.ENGINEER, None, *passed, "-p", "Do the work."),
                     "LAUNCH_REFUSED", "the CLI arguments carry", name)


def test_no_chrome_is_not_refused(launch):
    arguments = ("--no-chrome", "-p", "Do the work.")
    result = launch(s.ENGINEER, None, *arguments)
    s.assert_launched(result)
    s.assert_passed_through(result, arguments)


def test_a_prompt_that_names_the_round_2_arguments_as_words_is_launched(launch):
    prompt = "Do not pass --fallback-model, --chrome, --ide or --system-prompt-snapshot here."
    result = launch(s.ENGINEER, None, "-p", prompt)
    s.assert_launched(result)
    s.assert_passed_through(result, ("-p", prompt), "the prompt did not reach the CLI unchanged")


# --------------------------------------------------------------------------
# Every refusal of today's still refuses
# --------------------------------------------------------------------------

def _settings(change, rel=s.SETTINGS_REL):
    return lambda project, sandbox, cli: s.rewrite_settings(project, change, rel)


def _permissions(key, value):
    return _settings(lambda data: data.setdefault("permissions", {}).update({key: value}))


def _unwire(project, sandbox, cli):
    s.write(project / s.SETTINGS_REL, json.dumps({"permissions": {"deny": []}}) + "\n")


def _not_json(project, sandbox, cli):
    s.write(project / s.SETTINGS_REL, "{ not json\n")


def _held_out(project, sandbox, cli):
    s.write(project / s.HELD_OUT_REL, "held_out_paths: not-a-list\n")


def _two_experiment_folders(project, sandbox, cli):
    ticket = s.Ticket(s.EXPERIMENT.tk, s.RESEARCH, s.EXPERIMENT.wbs,
                      ("experiments/spikes/exp-960/**", "experiments/spikes/exp-961/**"), cls="research")
    s.write(project / f".tickets/{ticket.tk}.md", s.ticket_text(ticket))


def _no_cli(project, sandbox, cli):
    cli.path.unlink()


TODAY = {
    # (role, ticket, arguments after --, change before the launch, words today's message carries)
    "skip-permissions": (s.ENGINEER, s.T, ("--dangerously-skip-permissions",), None, ("DEC-313",)),
    "allow-skip-permissions": (s.ENGINEER, s.T, ("--allow-dangerously-skip-permissions",), None, ("DEC-313",)),
    "bypass-mode-spaced": (s.ENGINEER, s.T, ("--permission-mode", "bypassPermissions"), None, ("DEC-313",)),
    "bypass-mode-joined": (s.ENGINEER, s.T, ("--permission-mode=bypassPermissions",), None, ("DEC-313",)),
    "add-dir-spaced": (s.ENGINEER, s.T, ("--add-dir", "/w260a-added"), None, ("--add-dir", "DEC-313")),
    "add-dir-joined": (s.ENGINEER, s.T, ("--add-dir=/w260a-added",), None, ("--add-dir", "DEC-313")),
    "settings-spaced": (s.ENGINEER, s.T, ("--settings", "{}"), None, ("--settings",)),
    "settings-joined": (s.ENGINEER, s.T, ("--settings=/w260a/settings.json",), None, ("--settings",)),
    "bare": (s.ENGINEER, s.T, ("--bare",), None, ("--bare",)),
    "setting-sources-spaced": (s.ENGINEER, s.T, ("--setting-sources", "user,project,local"), None,
                               ("--setting-sources",)),
    "setting-sources-the-launcher-s-own-value": (s.ENGINEER, s.T, ("--setting-sources=project,local",), None,
                                                 ("--setting-sources",)),
    "sandbox-key-committed": (s.ENGINEER, s.T, (), _settings(lambda d: d.update({"sandbox": {"enabled": False}})),
                              ("DEC-233",)),
    "sandbox-key-local": (s.ENGINEER, s.T, (), _settings(lambda d: d.update({"sandbox": {}}), s.LOCAL_SETTINGS_REL),
                          ("DEC-233",)),
    "disable-all-hooks": (s.ENGINEER, s.T, (), _settings(lambda d: d.update({"disableAllHooks": True})),
                          ("disableAllHooks",)),
    "bypass-default-mode": (s.ENGINEER, s.T, (), _permissions("defaultMode", "bypassPermissions"), ("DEC-313",)),
    "additional-directories": (s.ENGINEER, s.T, (), _permissions("additionalDirectories", ["/w260a-added"]),
                               ("DEC-313",)),
    "guard-not-wired": (s.ENGINEER, s.T, (), _unwire, ("does not register the guard",)),
    "settings-not-json": (s.ENGINEER, s.T, (), _not_json, ("cannot be read",)),
    "held-out-malformed": (s.ENGINEER, s.T, (), _held_out, ("DEC-218",)),
    "research-two-folders": (s.RESEARCH, s.EXPERIMENT, (), _two_experiment_folders, ("DEC-242",)),
    # Since W2-136 (DEC-1088 (5)) a launch of the orchestrator is a lead launch, refused for a ticket on no approved
    # ready list ("no lead for ticket '<id>': no approved ready list can be read ..."); still no CLI start, no record.
    "orchestrator": (s.ORCHESTRATOR, s.T, (), None, ("no lead for ticket",)),
    "unknown-role": ("w260a-no-such-role", s.T, (), None, ("not a worker role",)),
    "unknown-ticket": (s.ENGINEER, "DAEO-zz00", (), None, ("unknown ticket",)),
    "ticket-not-in-progress": (s.ENGINEER, s.CLOSED, (), None, ("not in_progress",)),
    "another-role-s-ticket": (s.ENGINEER, s.SPEC, (), None, ("another role",)),
    "no-cli": (s.ENGINEER, s.T, (), _no_cli, ("DEC-205",)),
}


@pytest.mark.parametrize("case", sorted(TODAY))
def test_every_refusal_the_launcher_makes_today_still_refuses(sandbox, project, cli, case):
    role, ticket, passed, change, words = TODAY[case]
    control = s.launch(sandbox, cli, s.ENGINEER, s.T)
    s.assert_launched(control)
    if change is not None:
        change(project, sandbox, cli)
    s.assert_refused(s.launch(sandbox, cli, role, ticket, *passed), "LAUNCH_REFUSED", *words)


FIRST = ("bare", "setting-sources-spaced", "unknown-ticket", "sandbox-key-committed", "no-cli")


@pytest.mark.parametrize("case", FIRST)
def test_today_s_checks_come_first_with_today_s_message(sandbox, case):
    """Behaviour 10: in a tree with no role file, today's refusal is the reason given, with today's words."""
    project = s.make_project(sandbox, roles=())
    cli = s.install_stand_in_cli(sandbox)
    role, ticket, passed, change, words = TODAY[case]
    if change is not None:
        change(project, sandbox, cli)
    s.assert_refused(s.launch(sandbox, cli, role, ticket, *passed), "LAUNCH_REFUSED", *words)


def test_a_launch_record_id_is_never_one_the_caller_names(launch):
    """KPI failure 2's "a record naming another session": the id comes from the launcher alone, a new UUID."""
    result = launch(s.ENGINEER, None, "-p", "Do the work.")
    s.assert_launched(result)
    sid = result.session_id()
    assert sid != AN_ID and uuid.UUID(sid).version == 4, f"the session id {sid} is not a new random UUID"
