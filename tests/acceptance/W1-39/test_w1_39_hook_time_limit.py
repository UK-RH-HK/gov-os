"""DEC-580: a project made from the template has the time limit on every guard hook entry of its installed settings.

DEC-580: "The kernel template's settings carry ``"timeout": 60`` on every guard
hook entry, so that every adopted project gets it." Why: a hook that passes its
time limit lets the call through (``docs/research/EXP-hook-time-limit.md``).

How a project gets the kernel's settings is this suite's ground: ``copier copy``
writes them, with the rest of the kernel, to ``governance/kernel/settings.json``
of the project, and ``copier update`` brings a later release's. Neither writes
anything in the folder the adapter generation owns, so settings a project had
there before are not touched by either; no command of ``gov`` merges the two.

The cases read the installed file of a created project and judge it with the
words of ``tests/acceptance/W1-47/w1_47_hook_time_limit.py`` (what a guard hook
entry is, and what carrying the limit is), against the hook programs installed
in that project. The kernel template's own file is held in W1-47.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-47"))

import w1_39_support as support  # noqa: E402
import w1_47_hook_time_limit as limit  # noqa: E402

KERNEL_SETTINGS_REL = f"{support.KERNEL_REL}/settings.json"
# A project's own settings: a file in the folder the adapter generation owns, which the copy does not write.
OWN_SETTINGS_REL = f"{support.GENERATED_BY_RULESYNC[2]}/settings.json"
OWN_SETTINGS = json.dumps({
    "permissions": {"deny": ["Edit(config/secrets*)"]},
    "hooks": {
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "sh scripts/own-check.sh"}]}],
        "Notification": [{"hooks": [{"type": "command", "command": "sh scripts/notify.sh", "timeout": 5}]}],
    },
}, indent=2) + "\n"


def _faults(project):
    """What the installed settings of ``project`` lack of the limit, judged against its installed hook programs."""
    settings = limit.load(project / KERNEL_SETTINGS_REL, f"{KERNEL_SETTINGS_REL} of the created project")
    programs = limit.program_names(project / support.HOOKS_REL)
    assert limit.guard_entries(settings, programs), (
        f"{KERNEL_SETTINGS_REL} of the created project registers no guard hook entry, so the time limit would be "
        f"held for nothing"
    )
    return limit.faults(settings, programs)


def _message(found, how):
    return (f"{KERNEL_SETTINGS_REL} of a project {how}: a guard hook entry without "
            f"`\"{limit.LIMIT_KEY}\": {limit.LIMIT_S}` (DEC-580):\n  " + "\n  ".join(found))


def _copied_beside_own_settings(copier_bin, source, sandbox, tmp_path):
    """A folder that holds settings of its own, and the kernel copied into it."""
    destination = tmp_path / "product"
    (destination / OWN_SETTINGS_REL).parent.mkdir(parents=True)
    (destination / OWN_SETTINGS_REL).write_text(OWN_SETTINGS, encoding="utf-8")
    done = support.copy(copier_bin, sandbox, source, destination)
    assert done.returncode == 0, f"`copier copy` failed\n{done.describe()}"
    return destination, done


def test_a_created_project_has_the_time_limit_on_every_guard_hook_entry(installed):
    """``copier copy``: every guard hook entry of the installed settings carries the limit."""
    found = _faults(installed)
    assert not found, _message(found, "created by `copier copy`")


def test_a_project_that_had_settings_of_its_own_gets_the_time_limit_on_the_guard_s_entries(copier_bin, source, sandbox,
                                                                                         tmp_path):
    """The same where the folder held settings of its own before the copy."""
    destination, _done = _copied_beside_own_settings(copier_bin, source, sandbox, tmp_path)
    found = _faults(destination)
    assert not found, _message(found, "that had settings of its own before `copier copy`")


def test_copy_leaves_a_project_s_own_settings_as_they_were(copier_bin, source, sandbox, tmp_path):
    """The project's own entries, with a limit of their own or without one, are byte for byte what they were."""
    destination, done = _copied_beside_own_settings(copier_bin, source, sandbox, tmp_path)
    assert (destination / OWN_SETTINGS_REL).read_text(encoding="utf-8") == OWN_SETTINGS, \
        f"`copier copy` changed the settings the folder held before\n{done.describe()}"
    assert (destination / KERNEL_SETTINGS_REL).is_file(), "the kernel's settings were not installed beside them"


def test_a_project_of_an_earlier_release_gets_the_time_limit_by_an_update(copier_bin, source, sandbox, tmp_path):
    """``copier update``: a project installed from a release whose guard entries had no limit has it afterwards."""
    shipped = (source.template / KERNEL_SETTINGS_REL).read_text(encoding="utf-8")
    earlier = json.loads(shipped)
    programs = limit.program_names(source.template / support.HOOKS_REL)
    for _where, _group, entry in limit.guard_entries(earlier, programs):
        entry.pop(limit.LIMIT_KEY, None)
    support.write_template_file(source, KERNEL_SETTINGS_REL, json.dumps(earlier, indent=2) + "\n")
    support.git(source.path, "tag", "-d", support.FIRST_TAG)
    support.release(source.path, support.FIRST_TAG, "an earlier release: no time limit on the guard's hook entries")
    project = support.create_project(copier_bin, sandbox, source, tmp_path / "product")
    assert _faults(project), "the project of the earlier release has the limit already: the case shows nothing"
    support.write_template_file(source, KERNEL_SETTINGS_REL, shipped)
    support.release(source.path, support.SECOND_TAG, "the release that ships the kernel template's settings as they are")
    done = support.update(copier_bin, sandbox, source, project)
    assert done.returncode == 0, f"`copier update` failed\n{done.describe()}"
    found = _faults(project)
    assert not found, _message(found, "updated by `copier update` to the release that ships the template as it is")
