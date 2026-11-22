"""The owner's exceptions to the model rule (W2-201; DEC-1212 (2), DEC-1225).

``governance/project/model-exceptions.yaml`` holds ``exceptions: [{subagent_type, model, decided, class?, task?,
decision?}]``. An entry lifts the refusal of another model for the role it names; ``model`` is the alias ``opus`` or a
model id, and an entry that names Opus covers every Opus model. Three keys limit an entry, and every one it carries
must be met (DEC-1225 (2)): ``class: C3`` (the ticket's class), ``task: <id or list>`` (the launch's ticket) and
``decision: <DEC-id or list>`` (the launch's ``--owner-named``). An entry that names Opus and carries none lifts
nothing. No entry covers Fable: no session runs it (DEC-1225 (3)). The helper hook (``.claude/hooks/agent_model.py``)
reads the same file by the same rule; it stays standalone, and a unit test holds the two equal. A file that cannot be
read or is not of the stated form refuses (fail closed).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gov.cli.errors import GovError

REL = "governance/project/model-exceptions.yaml"
LIMITERS = ("class", "task", "decision")


def names_opus(model: object) -> bool:
    return isinstance(model, str) and (model == "opus" or model.startswith("claude-opus-"))


def is_sonnet(model: object) -> bool:
    return isinstance(model, str) and (model == "sonnet" or model.startswith("claude-sonnet-"))


def names_fable(model: object) -> bool:
    return isinstance(model, str) and "fable" in model.lower()


def model_matches(entry_model: object, model: str) -> bool:
    """True when an entry's ``model`` covers ``model``: the same text, or Opus for Opus (alias or id). Never Fable."""
    if names_fable(model):
        return False
    return entry_model == model or (names_opus(entry_model) and names_opus(model))


def as_list(value: object) -> list:
    """A ``task`` or ``decision`` given as one string is a list of one."""
    return list(value) if isinstance(value, (list, tuple)) else [value]


def unmet(entry: dict, ticket_class: str | None, ticket: str | None, decision: str | None) -> list[str]:
    """What an entry's limiters say is not met: ``[]`` when every limiter it carries is met. An entry that names Opus
    and carries no limiter lifts nothing: it says so."""
    missing = []
    if "class" in entry and entry["class"] != ticket_class:
        missing.append(f"class (the entry holds for {entry['class']} work, the ticket's class is "
                       f"{ticket_class if ticket_class is not None else 'not known'})")
    if "task" in entry and ticket not in as_list(entry["task"]):
        missing.append(f"task (the entry holds for {', '.join(map(str, as_list(entry['task'])))}, the launch's "
                       f"ticket is {ticket if ticket is not None else 'none'})")
    if "decision" in entry and decision not in as_list(entry["decision"]):
        missing.append(f"decision (the entry holds for {', '.join(map(str, as_list(entry['decision'])))}, the launch "
                       f"was given --owner-named {decision if decision is not None else 'none'})")
    if not missing and names_opus(entry.get("model")) and not any(key in entry for key in LIMITERS):
        missing.append("limiter (an entry that names Opus carries a class, task or decision limiter, and this one "
                       "carries none, so it lifts nothing)")
    return missing


def load(root: Path) -> list[dict]:
    """The file's entries; refused, naming the file, when it cannot be read, is not YAML or is not a map with an
    ``exceptions`` list. An entry that is not a map covers nothing."""
    try:
        data = yaml.safe_load((Path(root) / REL).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise GovError("LAUNCH_REFUSED", f"{REL} cannot be read or is not YAML, so no exception can be found in it") \
            from None
    if not isinstance(data, dict) or not isinstance(data.get("exceptions"), list):
        raise GovError("LAUNCH_REFUSED", f"{REL} is not a map with an 'exceptions' list, so no exception can be found "
                                         f"in it")
    return [entry for entry in data["exceptions"] if isinstance(entry, dict)]


def find(root: Path, role: str, model: str, ticket_class: str | None, ticket: str | None = None,
         decision: str | None = None) -> tuple[dict | None, list[str]]:
    """``(entry, unmet)``: the first entry that names ``role``, covers ``model`` and whose limiters are all met, and
    ``[]``; or ``None`` and what the entries that name the role and the model say is not met (empty when none names
    them)."""
    said: list[str] = []
    for entry in load(root):
        if entry.get("subagent_type") == role and model_matches(entry.get("model"), model):
            missing = unmet(entry, ticket_class, ticket, decision)
            if not missing:
                return entry, []
            said += missing
    return None, said
