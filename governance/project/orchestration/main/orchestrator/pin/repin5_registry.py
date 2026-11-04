"""Re-pin window 3 (DEC-1068 (e)): the owner's registry edit, run by the owner after the switch.

Replaces window 2's gov entry (9894b0cf, its sha256 94931d3d...) in governance/project/tool-registry.yaml with the new
pin's. Refuses, changing nothing, unless the new wheel has the expected sha256 (the dry run's, two builds alike), the
gov link is a link into the new pin's own environment, and the old entry is there exactly once. Prints the new entry;
the owner commits the file (Role: owner).
    python3 repin5_registry.py <commit12> <expected sha256> <epoch>
The paths default to the live ones; the rehearsal points them at scratch (REPIN-COMMANDS-<12>.sh passes them):
GOV_REPIN_PINS (the pins' folder, ~/.local/share/gov-os), GOV_REPIN_LINK_HOME (the HOME of .local/bin/gov, ~) and
GOV_REPIN_REGISTRY_REPO (the repository whose registry is edited, the main tree).
"""
import datetime
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("GOV_REPIN_REGISTRY_REPO") or "/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
OLD_COMMIT = "9894b0cf"
OLD_SHA = "94931d3d6f836a24ae4a78aac6f03e2ab13b42a3ddcaf22390270537fe1525c2"
OLD_APPROVAL = "DEC-1037"  # window 2's entry cites DEC-1037 since 7842fd94 (W1-06's red); the new entry keeps it
COMMIT, EXPECTED, EPOCH = sys.argv[1], sys.argv[2], sys.argv[3]
PINS = Path(os.environ.get("GOV_REPIN_PINS") or Path.home() / ".local/share/gov-os")
LINK_HOME = Path(os.environ.get("GOV_REPIN_LINK_HOME") or Path.home())
PIN = PINS / f"pin-{COMMIT}"
WHEEL = PINS / "wheels" / COMMIT / "gov-0.1.0-py3-none-any.whl"
OLD_START = f'  - name: gov\n    version: "0.1.0"\n    sha256: "{OLD_SHA}"\n'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(why: str) -> None:
    print(f"REFUSED, nothing changed: {why}", file=sys.stderr)
    sys.exit(2)


if len(COMMIT) != 12 or len(EXPECTED) != 64 or not EPOCH.isdigit():
    refuse("usage: repin5_registry.py <commit12> <expected sha256> <epoch>")
if not WHEEL.is_file() or sha256(WHEEL) != EXPECTED:
    refuse(f"{WHEEL} is missing or its sha256 is not {EXPECTED}")
link = LINK_HOME / ".local/bin/gov"
if not link.is_symlink() or Path(os.path.realpath(link)) != (PIN / "bin/gov").resolve():
    refuse(f"{link} is not a link to {PIN / 'bin/gov'}")
script_sha = sha256(PIN / "bin/gov")
text = REGISTRY.read_text(encoding="utf-8")
if text.count(OLD_START) != 1:
    refuse(f"window 2's gov entry ({OLD_COMMIT}) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if f'approved_by: "{OLD_APPROVAL}"' not in old or f"pin-{OLD_COMMIT}" not in old:
    refuse(f"the gov entry found is not window 2's (pin-{OLD_COMMIT}, {OLD_APPROVAL})")
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
    f'    approved_by: "{OLD_APPROVAL}"\n'
    f'    note: "Re-pin window 3 (DEC-1068 (e), under DEC-1037\'s re-pin windows): a non-editable install of the wheel '
    f'built from commit {COMMIT}, w2/integrate after the night of DEC-1067 (W2-32: G1, the embedder and reranker '
    f'limits, S8 routing by question type and the phrasings, the reranker requests bounded at 16 texts and 24,000 '
    f'padded characters, contextual headers when embedded; switched on by rebuild.yaml embed_headers and retrieval.yaml '
    f'routing and phrasings) (git archive, then pip wheel --no-deps --no-build-isolation with SOURCE_DATE_EPOCH={EPOCH}, '
    f'the commit\'s time; two builds gave the same bytes), in its own environment ~/.local/share/gov-os/pin-{COMMIT} '
    f'(Python 3.12, with the system and user site packages for PyYAML, pytest, pytest-xdist, pytest-timeout and '
    f'sqlite-vec), linked from ~/.local/bin/gov by an atomic rename; the integration store re-embedded with headers at '
    f'the same commit before the switch. sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a link) has '
    f'sha256 {script_sha}. Replaces window 2\'s entry (pin-{OLD_COMMIT}); pin-{OLD_COMMIT} stays for a one-command '
    f'rollback (the uninstall line)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer DEC-1068 (Role: owner)")
