"""The project's configuration: ``governance/project/session-watch.yaml``, the mapping under ``session_watch:``.

Every key is optional; a missing file is the defaults. A key of the wrong kind is a ``ConfigError`` naming it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

FILE = Path("governance") / "project" / "session-watch.yaml"
SECTION = "session_watch"


class ConfigError(Exception):
    """A configuration the checks cannot use; the message names the file and the key."""


@dataclass(frozen=True)
class Items:
    source: str = "dispatcher"          # "dispatcher" or "file"
    path: str = ""                      # the item file, relative to the project (source: file)
    reader: str = "lines"               # "lines" or "module.path:function"


@dataclass(frozen=True)
class Config:
    waiter_commands: tuple = ()
    waiter_arm: str = ""
    standby_max_age_h: float = 2
    pid_globs: tuple = (".gov-runtime/**/*.pid",)
    items: Items = field(default_factory=Items)


def _bad(key: str, why: str) -> ConfigError:
    return ConfigError(f"{FILE}: {key}: {why}")


def _strings(values: dict, key: str, default: tuple) -> tuple:
    value = values.get(key)
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        raise _bad(key, f"a list of non-empty texts is needed, not {value!r}")
    return tuple(value)


def _items(values: dict) -> Items:
    value = values.get("items")
    if value is None:
        return Items()
    source = value.get("source", "dispatcher") if isinstance(value, dict) else None
    if source == "dispatcher":
        return Items()
    path, reader = value.get("path"), value.get("reader", "lines")
    if source != "file" or not isinstance(path, str) or not path or not isinstance(reader, str) \
            or not (reader == "lines" or ":" in reader):
        raise _bad("items", "{source: dispatcher} or {source: file, path: <relative>, reader: lines | module:function} "
                            f"is needed, not {value!r}")
    return Items("file", path, reader)


def load(root: Path) -> Config:
    import yaml

    file = Path(root) / FILE
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return Config()
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise ConfigError(f"{FILE}: cannot be read: {str(error).splitlines()[0] if str(error) else error}") from None
    values = data.get(SECTION) if isinstance(data, dict) else None
    if values is None:
        return Config()
    if not isinstance(values, dict):
        raise ConfigError(f"{FILE}: `{SECTION}:` must be a mapping")
    commands = _strings(values, "waiter_commands", ())
    arm = values.get("waiter_arm")
    if arm is not None and (not isinstance(arm, str) or not arm.strip()):
        raise _bad("waiter_arm", f"a non-empty text is needed, not {arm!r}")
    age = values.get("standby_max_age_h", 2)
    if isinstance(age, bool) or not isinstance(age, (int, float)) or age < 0:
        raise _bad("standby_max_age_h", f"a number of hours, 0 or more, is needed, not {age!r}")
    return Config(waiter_commands=commands, waiter_arm=arm or (commands[0] if commands else ""),
                  standby_max_age_h=age, pid_globs=_strings(values, "pid_globs", Config.pid_globs),
                  items=_items(values))
