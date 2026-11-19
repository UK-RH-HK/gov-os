"""The owner's exceptions to the model rule (W2-201; DEC-1212 (2), DEC-1214 K1).

``governance/project/model-exceptions.yaml`` holds ``exceptions: [{subagent_type, model, decided, class?}]``. An entry
lifts the refusal of another model for the role it names; ``model`` is the alias ``opus`` or a model id, and an entry
that names Opus covers every Opus model. With ``class`` the entry holds only for a ticket of that class (``C3``).
While DEC-1215's substitution is active, an entry that names Opus covers Claude Fable 5.2 as well. The helper hook
(``.claude/hooks/agent_model.py``) reads the same file by the same rule; it stays standalone, and a unit test holds
the two equal. A file that cannot be read or is not of the stated form refuses (fail closed).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gov.cli.errors import GovError

REL = "governance/project/model-exceptions.yaml"
FABLE = ("fable", "claude-fable-5-2")


def names_opus(model: object) -> bool:
    return isinstance(model, str) and (model == "opus" or model.startswith("claude-opus-"))


def model_matches(entry_model: object, model: str, substituted: bool) -> bool:
    """True when an entry's ``model`` covers ``model``: the same text, Opus for Opus (alias or id), and, while the
    substitution is active (``substituted``), Opus for Fable."""
    if entry_model == model:
        return True
    return names_opus(entry_model) and (names_opus(model) or (substituted and model in FABLE))


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


def find(root: Path, role: str, model: str, ticket_class: str | None, substituted: bool) -> dict | None:
    """The first entry that names ``role`` and covers ``model`` and whose ``class``, when it has one, is the
    ticket's; ``None`` when there is none."""
    for entry in load(root):
        if entry.get("subagent_type") == role and model_matches(entry.get("model"), model, substituted) \
                and ("class" not in entry or entry["class"] == ticket_class):
            return entry
    return None
