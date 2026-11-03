"""The repository's secrets-scan switch (DEC-1045): `governance/project/secrets.yaml`, key `scan: on|off`.

The same file the product reads (gov.config.loader), read here with a few lines of YAML so the CTO's tools need no
product import: one setting governs both. Absent file, empty file or absent key: on (today's behaviour). `on`/`off`
(YAML reads them as true/false; quoted strings are taken too). Anything else, or a file that does not parse: an error
(fail closed), never "off".
"""
from pathlib import Path

REL = "governance/project/secrets.yaml"
OFF_LINE = "gitleaks: off by configuration (DEC-1045)"


class SwitchError(Exception):
    """The switch cannot be read or holds another value: the caller stops (fails closed)."""


def scan_on(root) -> bool:
    """True when gitleaks scanning is on for the repository at ``root``; raises SwitchError otherwise unreadable."""
    path = Path(root) / REL
    if not path.exists():
        return True
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 (any unreadable form fails closed)
        raise SwitchError(f"{path}: cannot be read as YAML ({type(e).__name__}: {e})") from e
    if data is None:
        return True
    if not isinstance(data, dict):
        raise SwitchError(f"{path}: not a mapping (DEC-1045: one key, scan: on|off)")
    if "scan" not in data:
        return True
    value = data["scan"]
    if value is True or value == "on":
        return True
    if value is False or value == "off":
        return False
    raise SwitchError(f"{path}: scan is {value!r}; only on or off (DEC-1045)")
