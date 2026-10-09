"""Check declarations (DEC-186): one YAML file per check under the kernel's ``checks/`` folder.

A declaration is a map with the five string fields below. A ticket registers a
check for the component it builds by adding a file. Running checks is W1-26.

A project holds its kernel in the template layout, in the installed layout or in both (DEC-579). The
declarations of both are read: a check declared alike in the two is one check, a file that only one of them
holds is read, and one check id declared differently in the two is refused.
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import read_yaml

CHECKS_DIR = "template/governance/kernel/checks"
INSTALLED_CHECKS_DIR = "governance/kernel/checks"
CHECKS_DIRS = (CHECKS_DIR, INSTALLED_CHECKS_DIR)
FIELDS = ("id", "family", "tier", "severity", "command")
SEVERITIES = ("hard-block", "warning")
INVALID = "CHECK_DECLARATION_INVALID"


def _read(path: Path, rel: str) -> dict:
    """The declaration file ``rel`` as it is written, every key of it. A file that is not valid is refused."""
    document = read_yaml(path, INVALID, rel)
    if not isinstance(document, dict):
        raise GovError(INVALID, f"{rel}: the top level must be a map", {"file": rel, "key": None})
    for field in FIELDS:
        value = document.get(field)
        if not isinstance(value, str) or (field == "severity" and value not in SEVERITIES):
            expected = " or ".join(SEVERITIES) if field == "severity" else "a string"
            raise GovError(INVALID, f"{rel}: key '{field}' must be {expected}", {"file": rel, "key": field})
    return document


def load_declarations(root: Path) -> list[dict]:
    """Every declaration under ``root``, in file-name order. Reads the files; starts no command."""
    read = []  # (file name, path in the project, the document), the template layout's files first
    template: dict[str, tuple[str, dict]] = {}
    for checks_dir in CHECKS_DIRS:
        for path in sorted((Path(root) / checks_dir).glob("*.yaml")):
            rel = f"{checks_dir}/{path.name}"
            document = _read(path, rel)
            if checks_dir == CHECKS_DIR:
                template.setdefault(document["id"], (rel, document))
            elif document["id"] in template:
                other_rel, other = template[document["id"]]
                if document != other:  # which of the two the project means is not known: neither is taken
                    key = next(key for key in sorted(set(document) | set(other), key=str)
                               if document.get(key) != other.get(key))
                    raise GovError(INVALID, f"{other_rel} and {rel}: check '{document['id']}' is declared "
                                            f"differently in the two layouts (key '{key}')",
                                   {"file": rel, "key": key})
                continue  # declared alike in both layouts: one check
            read.append((path.name, rel, document))
    return [{field: document[field] for field in FIELDS} for _, _, document in sorted(read, key=lambda each: each[0])]
