"""The second re-pin (DEC-933 item 1, P-REPIN-2): the owner's registry edit, run by the owner after the install.

Replaces the first re-pin's gov entry (6a4696eb, DEC-922) in governance/project/tool-registry.yaml with the new pin's
(5c401220). Refuses, changing nothing, unless the new wheel has the expected sha256 (the dry run's, two builds alike),
~/.local/bin/gov is a link into the new pin's own environment, and the old entry is there exactly once. Prints the new
entry; the owner commits the file (Role: owner).
"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
OLD_COMMIT, COMMIT = "6a4696eb", "5c401220"
OLD_SHA = "73a281fff667c16eef5cc9157798e727d0a91cdd7c0d7846d474be57e6c6b6c9"
EXPECTED = "e4f35131d8cff32f124863c6780efad368c2500be59824dc7fe9458d126905d0"
EPOCH = "1793182278"
HOME = Path.home()
PIN = HOME / ".local/share/gov-os" / f"pin-{COMMIT}"
WHEEL = HOME / ".local/share/gov-os/wheels" / COMMIT / "gov-0.1.0-py3-none-any.whl"
OLD_START = f'  - name: gov\n    version: "0.1.0"\n    sha256: "{OLD_SHA}"\n'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(why: str) -> None:
    print(f"REFUSED, nothing changed: {why}", file=sys.stderr)
    sys.exit(2)


if not WHEEL.is_file() or sha256(WHEEL) != EXPECTED:
    refuse(f"{WHEEL} is missing or its sha256 is not {EXPECTED}")
link = HOME / ".local/bin/gov"
if not link.is_symlink() or Path(os.path.realpath(link)) != (PIN / "bin/gov").resolve():
    refuse(f"{link} is not a link to {PIN / 'bin/gov'}")
script_sha = sha256(PIN / "bin/gov")
text = REGISTRY.read_text(encoding="utf-8")
if text.count(OLD_START) != 1:
    refuse(f"the first re-pin's gov entry ({OLD_COMMIT}, DEC-922) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if 'approved_by: "DEC-922"' not in old:
    refuse("the gov entry found is not DEC-922's")
today = datetime.date.today().isoformat()
new = (
    '  - name: gov\n'
    '    version: "0.1.0"\n'
    f'    sha256: "{EXPECTED}"\n'
    f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{COMMIT} && '
    f'~/.local/share/gov-os/pin-{COMMIT}/bin/python -m pip install --no-deps --no-index '
    f'~/.local/share/gov-os/wheels/{COMMIT}/gov-0.1.0-py3-none-any.whl && '
    f'ln -sfn ~/.local/share/gov-os/pin-{COMMIT}/bin/gov ~/.local/bin/gov"\n'
    f'    uninstall: "ln -sfn ~/.local/share/gov-os/pin-{OLD_COMMIT}/bin/gov ~/.local/bin/gov && '
    f'rm -rf ~/.local/share/gov-os/pin-{COMMIT}"\n'
    f'    date: "{today}"\n'
    '    approved_by: "DEC-933"\n'
    f'    note: "The second re-pin (DEC-933 item 1, P-REPIN-2 (a)): a non-editable install of the wheel built from '
    f'commit {COMMIT}, w2/integrate after W2-57 (the rulesync and doctor probes, the serial pass and its route to the '
    f'nightly) and W2-07 round 2 (gate (h) measures DEC-891\'s records under any ACCEPTED decision and the owner\'s '
    f'lists) (git archive, then pip wheel --no-deps --no-build-isolation with SOURCE_DATE_EPOCH={EPOCH}, the commit\'s '
    f'time; two builds gave the same bytes), in its own environment ~/.local/share/gov-os/pin-{COMMIT} (Python 3.12, '
    f'with the system and user site packages for PyYAML, pytest, pytest-xdist, pytest-timeout and sqlite-vec), linked '
    f'from ~/.local/bin/gov. sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has sha256 '
    f'{script_sha}. Replaces DEC-922\'s entry; the first re-pin pin-{OLD_COMMIT} stays for a one-command rollback '
    f'(the uninstall line)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-933 (Role: owner)")
