"""Re-pin window 2 (DEC-1052 D-1, the refactoring): the owner's registry edit, run by the owner after the switch.

Replaces window 1's gov entry (a7182f6c, DEC-1037) in governance/project/tool-registry.yaml with the new pin's.
Refuses, changing nothing, unless the new wheel has the expected sha256 (the dry run's, two builds alike),
~/.local/bin/gov is a link into the new pin's own environment, and the old entry is there exactly once. Prints the new
entry; the owner commits the file (Role: owner).
    python3 repin4_registry.py <commit8> <expected sha256> <epoch>
"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
OLD_COMMIT = "a7182f6c"
OLD_SHA = "9ed615a8b62231795d9846204b146a517b1756361130bdba4d4450a9694e211b"
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
    refuse("usage: repin4_registry.py <commit8> <expected sha256> <epoch>")
if not WHEEL.is_file() or sha256(WHEEL) != EXPECTED:
    refuse(f"{WHEEL} is missing or its sha256 is not {EXPECTED}")
link = HOME / ".local/bin/gov"
if not link.is_symlink() or Path(os.path.realpath(link)) != (PIN / "bin/gov").resolve():
    refuse(f"{link} is not a link to {PIN / 'bin/gov'}")
script_sha = sha256(PIN / "bin/gov")
text = REGISTRY.read_text(encoding="utf-8")
if text.count(OLD_START) != 1:
    refuse(f"window 1's gov entry ({OLD_COMMIT}, DEC-1037) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if 'approved_by: "DEC-1037"' not in old:
    refuse("the gov entry found is not DEC-1037's")
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
    '    approved_by: "DEC-1052"\n'
    f'    note: "Re-pin window 2 (DEC-1052 D-1, the refactoring; P1-PLAN P1-3 (iii)): a non-editable install of the wheel '
    f'built from commit {COMMIT}, w2/integrate with the memory branches merged as built (W2-122 seeded rebuilds, '
    f'W2-123 parallel requests and the bounded retry, W2-126 the machine-wide vector cache with KPI 7, W2-112 the shared '
    f'reranker, W2-04 gov context) and the emergency branches emg/noscan (DEC-1045\'s product switch) and emg/select '
    f'(T-4) (git archive, then pip wheel --no-deps --no-build-isolation with SOURCE_DATE_EPOCH={EPOCH}, the commit\'s '
    f'time; two builds gave the same bytes), in its '
    f'own environment ~/.local/share/gov-os/pin-{COMMIT} (Python 3.12, with the system and user site packages for '
    f'PyYAML, pytest, pytest-xdist, pytest-timeout and sqlite-vec), linked from ~/.local/bin/gov by an atomic rename. '
    f'sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has sha256 {script_sha}. Replaces '
    f'DEC-1037\'s (window 1) entry; pin-{OLD_COMMIT} stays for a one-command rollback (the uninstall line)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-1052 (Role: owner)")
