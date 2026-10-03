"""Check declarations (DEC-186): one YAML file per check under ``template/governance/kernel/checks/``.

A declaration is a map with the five string fields below. A ticket registers a
check for the component it builds by adding a file. Running checks is W1-26.
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import read_yaml

CHECKS_DIR = "template/governance/kernel/checks"
FIELDS = ("id", "family", "tier", "severity", "command")
SEVERITIES = ("hard-block", "warning")
INVALID = "CHECK_DECLARATION_INVALID"


def load_declarations(root: Path) -> list[dict]:
    """Every declaration under ``root``, in file-name order. Reads the files; starts no command."""
    declarations = []
    for path in sorted((Path(root) / CHECKS_DIR).glob("*.yaml")):
        rel = f"{CHECKS_DIR}/{path.name}"
        document = read_yaml(path, INVALID, rel)
        if not isinstance(document, dict):
            raise GovError(INVALID, f"{rel}: the top level must be a map", {"file": rel, "key": None})
        for field in FIELDS:
            value = document.get(field)
            if not isinstance(value, str) or (field == "severity" and value not in SEVERITIES):
                expected = " or ".join(SEVERITIES) if field == "severity" else "a string"
                raise GovError(INVALID, f"{rel}: key '{field}' must be {expected}", {"file": rel, "key": field})
        declarations.append({field: document[field] for field in FIELDS})
    return declarations
