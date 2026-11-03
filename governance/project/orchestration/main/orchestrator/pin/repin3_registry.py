"""The emergency re-pin (DEC-1037 (1), window 1): the owner's registry edit, run by the owner after the switch.

Replaces the second re-pin's gov entry (5c401220, DEC-933) in governance/project/tool-registry.yaml with the new pin's.
Refuses, changing nothing, unless the new wheel has the expected sha256 (the dry run's, two builds alike),
~/.local/bin/gov is a link into the new pin's own environment, and the old entry is there exactly once. Prints the new
entry; the owner commits the file (Role: owner).
    python3 repin3_registry.py <commit8> <expected sha256> <epoch>
"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
OLD_COMMIT = "5c401220"
OLD_SHA = "e4f35131d8cff32f124863c6780efad368c2500be59824dc7fe9458d126905d0"
COMMIT, EXPECTED, EPOCH = sys.argv[1], sys.argv[2], sys.argv[3]
HOME = Path.home()
PIN = HOME / ".local/share/gov-os" / f"pin-{COMMIT}"
WHEEL = HOME / ".local/share/gov-os/wheels" / COMMIT / "gov-0.1.0-py3-none-any.whl"
OLD_START = f'  - name: gov\n    version: "0.1.0"\n    sha256: "{OLD_SHA}"\n'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(why: str) -> None:
    print(f"REFUSED, nothing changed: {why}", file=sys.stderr)
    sys.exit(2)


if len(COMMIT) != 8 or len(EXPECTED) != 64 or not EPOCH.isdigit():
    refuse("usage: repin3_registry.py <commit8> <expected sha256> <epoch>")
if not WHEEL.is_file() or sha256(WHEEL) != EXPECTED:
    refuse(f"{WHEEL} is missing or its sha256 is not {EXPECTED}")
link = HOME / ".local/bin/gov"
if not link.is_symlink() or Path(os.path.realpath(link)) != (PIN / "bin/gov").resolve():
    refuse(f"{link} is not a link to {PIN / 'bin/gov'}")
script_sha = sha256(PIN / "bin/gov")
text = REGISTRY.read_text(encoding="utf-8")
if text.count(OLD_START) != 1:
    refuse(f"the second re-pin's gov entry ({OLD_COMMIT}, DEC-933) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if 'approved_by: "DEC-933"' not in old:
    refuse("the gov entry found is not DEC-933's")
today = datetime.date.today().isoformat()
new = (
    '  - name: gov\n'
    '    version: "0.1.0"\n'
    f'    sha256: "{EXPECTED}"\n'
    f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{COMMIT} && '
    f'~/.local/share/gov-os/pin-{COMMIT}/bin/python -m pip install --no-deps --no-index '
    f'~/.local/share/gov-os/wheels/{COMMIT}/gov-0.1.0-py3-none-any.whl && '
    f'ln -s ~/.local/share/gov-os/pin-{COMMIT}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov"\n'
    f'    uninstall: "ln -s ~/.local/share/gov-os/pin-{OLD_COMMIT}/bin/gov ~/.local/bin/gov.new && '
    f'mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov && rm -rf ~/.local/share/gov-os/pin-{COMMIT}"\n'
    f'    date: "{today}"\n'
    '    approved_by: "DEC-1037"\n'
    f'    note: "The emergency re-pin (DEC-1037 (1), P1-REPIN-EMERGENCY (a), window 1; changes DEC-954 Q8 (b) under '
    f'DEC-105): a non-editable install of the wheel built from commit {COMMIT}, w2/integrate with fix (b) of DEC-1033 '
    f'(a question\'s vector from any device), W2-87, W2-55, W2-108, gov accept and release, and W2-84\'s reads; '
    f'W2-122 and W2-123 come with window 2 (the owner, 2026-11-02 ~17:00) (git archive, then pip wheel --no-deps '
    f'--no-build-isolation with SOURCE_DATE_EPOCH={EPOCH}, the commit\'s time; two builds gave the same bytes), in its '
    f'own environment ~/.local/share/gov-os/pin-{COMMIT} (Python 3.12, with the system and user site packages for '
    f'PyYAML, pytest, pytest-xdist, pytest-timeout and sqlite-vec), linked from ~/.local/bin/gov by an atomic rename. '
    f'sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has sha256 {script_sha}. Replaces '
    f'DEC-933\'s entry; pin-{OLD_COMMIT} stays for a one-command rollback (the uninstall line)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-1037 (Role: owner)")
