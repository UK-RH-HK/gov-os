"""DEC-822 step 1, the bootstrap pin: the owner's registry edit, run by the owner after the install.

Replaces the editable install's gov entry (DEC-605) in governance/project/tool-registry.yaml with the pinned wheel's.
Refuses, changing nothing, unless the wheel has the expected sha256, ~/.local/bin/gov is a link into the pin's own
environment, and the old entry is there exactly once. Prints the new entry; the owner commits the file.
"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
COMMIT = "fecb870c"
HOME = Path.home()
PIN = HOME / ".local/share/gov-os" / f"pin-{COMMIT}"
WHEEL = HOME / ".local/share/gov-os/wheels" / COMMIT / "gov-0.1.0-py3-none-any.whl"
EXPECTED = "385fd5f0eceb04e926be2294149cc761235855fb5e13dd31ba9e1cefe3d5f7bd"
OLD_START = '  - name: gov\n    version: "0.1.0"\n    sha256: "0ef910b0ab1f6377d83f2e1f2d300a1e50c3d2b11a42a8f0edb479b81b7f4c80"\n'


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
    refuse("the editable install's gov entry (DEC-605) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if 'approved_by: "DEC-605"' not in old:
    refuse("the gov entry found is not DEC-605's")
today = datetime.date.today().isoformat()
new = (
    '  - name: gov\n'
    '    version: "0.1.0"\n'
    f'    sha256: "{EXPECTED}"\n'
    f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{COMMIT} && '
    f'~/.local/share/gov-os/pin-{COMMIT}/bin/python -m pip install --no-deps --no-index '
    f'~/.local/share/gov-os/wheels/{COMMIT}/gov-0.1.0-py3-none-any.whl && '
    f'ln -sfn ~/.local/share/gov-os/pin-{COMMIT}/bin/gov ~/.local/bin/gov"\n'
    f'    uninstall: "rm ~/.local/bin/gov && rm -rf ~/.local/share/gov-os/pin-{COMMIT}"\n'
    f'    date: "{today}"\n'
    '    approved_by: "DEC-822"\n'
    f'    note: "The bootstrap pin (P-S1 step 1, DEC-822): this repository\'s own command line, a non-editable '
    f'install of the wheel built from commit {COMMIT} (git archive, then pip wheel --no-deps --no-build-isolation '
    f'with SOURCE_DATE_EPOCH=1792407780, the commit\'s time; two builds gave the same bytes), in its own environment '
    f'~/.local/share/gov-os/pin-{COMMIT} (Python 3.12.3, with the system and user site packages for PyYAML, pytest, '
    f'pytest-xdist and sqlite-vec), linked from ~/.local/bin/gov in place of DEC-605\'s editable install, which is '
    f'removed. sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has sha256 {script_sha}. '
    f'Replaces DEC-605\'s entry. Not yet pinned: the declared checks and the guard hooks still import the working '
    f'tree\'s src (the check runner and the hook lines put it first on PYTHONPATH): step 2 and the keystone-1 '
    f'ticket."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-822")
