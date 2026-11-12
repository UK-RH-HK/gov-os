"""The dispatcher's configuration: ``governance/project/dispatch.yaml``, the mapping under ``dispatch:`` (S2, S6).

Read here, as the project's own keys are, not by ``gov.config``. Nothing is defaulted that names a branch, a path of
the project's own or a ticket: ``integration_branch`` and ``worktrees_root`` have no default, and neither have
``max_leads``, ``stagger_s`` and ``cpu_band``. A missing or malformed value is a ``ConfigError`` naming its key.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FILE = Path("governance") / "project" / "dispatch.yaml"
SECTION = "dispatch"
DEFAULT_LAUNCH = ["gov", "launch", "lead", "{ticket}"]
PLACEHOLDERS = ("{ticket}", "{w2}", "{brief}", "{log}")
CLOCK = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ConfigError(Exception):
    """A configuration the pass cannot use: exit 2, the message names the key (or the file)."""


@dataclass(frozen=True)
class Config:
    max_leads: int
    stagger_s: float
    cpu_band: float
    integration_branch: str
    worktrees_root: str
    briefs_dir: str = ".gov-runtime/dispatch/briefs"
    launch_command: list = field(default_factory=lambda: list(DEFAULT_LAUNCH))
    never_ran_after_s: float = 300
    unread_escalate_s: float = 3600
    command_timeout_s: float = 60
    history: str = ".gov-runtime/dispatch/history.jsonl"
    probes_dir: str = "docs/probes"
    job_markers: dict = field(default_factory=dict)
    nightly_hold: dict | None = None
    landing_command: list | None = None
    notifier_command: list | None = None


def _bad(key: str, why: str) -> ConfigError:
    return ConfigError(f"{FILE}: {key}: {why}")


def _number(values: dict, key: str, default=None, *, minimum=0, whole=False, positive=False):
    if key not in values:
        if default is None:
            raise _bad(key, "is missing")
        return default
    value = values[key]
    kind = int if whole else (int, float)
    if isinstance(value, bool) or not isinstance(value, kind) or value != value or value < minimum \
            or (positive and value <= 0):
        raise _bad(key, f"{'a whole number' if whole else 'a number'} of at least {minimum}"
                        f"{' (above 0)' if positive else ''} is needed, not {value!r}")
    return value


def _text(values: dict, key: str, default=None) -> str:
    if key not in values:
        if default is None:
            raise _bad(key, "is missing")
        return default
    value = values[key]
    if not isinstance(value, str) or not value.strip():
        raise _bad(key, f"a non-empty text is needed, not {value!r}")
    return value


def _argv(values: dict, key: str, default=None):
    if key not in values or values[key] is None:
        return default
    value = values[key]
    if not isinstance(value, list) or not value or not all(isinstance(a, str) and a for a in value):
        raise _bad(key, f"a list of arguments (an argv, not one string) is needed, not {value!r}")
    return value


def _hold(values: dict):
    value = values.get("nightly_hold")
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"from", "until"} \
            or not all(isinstance(v, str) and CLOCK.match(v) for v in value.values()):
        raise _bad("nightly_hold", f'{{from: "HH:MM", until: "HH:MM"}} is needed, not {value!r}')
    return {"from": value["from"], "until": value["until"]}


def _markers(values: dict) -> dict:
    value = values.get("job_markers", {})
    if value is None:
        return {}
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) and k and v
                                              for k, v in value.items()):
        raise _bad("job_markers", f"a map of job kind to a command-line substring is needed, not {value!r}")
    return dict(value)


def load(root: Path) -> Config:
    import yaml

    file = Path(root) / FILE
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"{FILE}: the file is missing (the project's dispatcher configuration)") from None
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise ConfigError(f"{FILE}: cannot be read: {str(error).splitlines()[0] if str(error) else error}") from None
    values = data.get(SECTION) if isinstance(data, dict) else None
    if not isinstance(values, dict):
        raise ConfigError(f"{FILE}: a `{SECTION}:` mapping is needed")
    launch = _argv(values, "launch_command", list(DEFAULT_LAUNCH))
    return Config(
        max_leads=_number(values, "max_leads", whole=True),
        stagger_s=_number(values, "stagger_s"),
        cpu_band=_number(values, "cpu_band"),
        integration_branch=_text(values, "integration_branch"),
        worktrees_root=_text(values, "worktrees_root"),
        briefs_dir=_text(values, "briefs_dir", Config.briefs_dir),
        launch_command=launch,
        never_ran_after_s=_number(values, "never_ran_after_s", 300),
        unread_escalate_s=_number(values, "unread_escalate_s", 3600),
        command_timeout_s=_number(values, "command_timeout_s", 60, positive=True),
        history=_text(values, "history", Config.history),
        probes_dir=_text(values, "probes_dir", Config.probes_dir),
        job_markers=_markers(values),
        nightly_hold=_hold(values),
        landing_command=_argv(values, "landing_command", None),
        notifier_command=_argv(values, "notifier_command", None),
    )
