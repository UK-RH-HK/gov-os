"""The first re-pin (DEC-884, DEC-921): the owner's registry edit, run by the owner after the install.

Replaces the bootstrap pin's gov entry (DEC-822, fecb870c) in governance/project/tool-registry.yaml with the new pin's
(6a4696eb). Refuses, changing nothing, unless the new wheel has the expected sha256 (the dry run's, two builds alike),
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
OLD_COMMIT, COMMIT = "fecb870c", "6a4696eb"
OLD_SHA = "385fd5f0eceb04e926be2294149cc761235855fb5e13dd31ba9e1cefe3d5f7bd"
EXPECTED = "73a281fff667c16eef5cc9157798e727d0a91cdd7c0d7846d474be57e6c6b6c9"
EPOCH = "1792954352"
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
    refuse(f"the bootstrap pin's gov entry ({OLD_COMMIT}, DEC-822) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if 'approved_by: "DEC-822"' not in old:
    refuse("the gov entry found is not DEC-822's")
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
    '    approved_by: "DEC-921"\n'
    f'    note: "The first re-pin (DEC-884, DEC-889 item 15, DEC-899 item 4, DEC-918, DEC-921): a non-editable install '
    f'of the wheel built from commit {COMMIT}, the merge that holds W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 and W2-72 '
    f'(git archive, then pip wheel --no-deps --no-build-isolation with SOURCE_DATE_EPOCH={EPOCH}, the commit\'s time; '
    f'two builds gave the same bytes), in its own environment ~/.local/share/gov-os/pin-{COMMIT} (Python 3.12, with '
    f'the system and user site packages for PyYAML, pytest, pytest-xdist, pytest-timeout and sqlite-vec), linked from '
    f'~/.local/bin/gov. sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has sha256 '
    f'{script_sha}. Replaces DEC-822\'s entry; the bootstrap pin pin-{OLD_COMMIT} stays for a one-command rollback '
    f'(the uninstall line). From this pin the declared checks and the guard hooks run the pinned judge (W2-59)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-921 (Role: owner)")
