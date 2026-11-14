"""Re-pin from release 0.1.0 (DEC-1178 (3), P-RELEASE-1 §6): the owner's registry edit, run by the owner's script after
the switch.

Replaces window 5's gov entry (797495bdfc70, its sha256 04b094fb...) in governance/project/tool-registry.yaml with the
release pin's. Refuses, changing nothing, unless the new wheel has the release record's sha256, the gov link is a link
into the new pin's own environment, and the old entry is there exactly once. Prints the new entry; the owner commits
the file (Role: owner).
    python3 rel_registry.py <commit12> <the record's wheel sha256> <epoch> <version> <tag> <the record's sha256>
The paths default to the live ones; the rehearsal points them at scratch (the script passes them):
GOV_REPIN_PINS (the pins' folder, ~/.local/share/gov-os), GOV_REPIN_LINK_HOME (the HOME of .local/bin/gov, ~) and
GOV_REPIN_REGISTRY_REPO (the repository whose registry is edited, the main tree).
"""
import datetime
import hashlib
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("GOV_REPIN_REGISTRY_REPO") or "/home/usain/Dynamic-Agentic-Engineering-OS")
REGISTRY = REPO / "governance/project/tool-registry.yaml"
OLD_COMMIT = "797495bdfc70"
OLD_SHA = "04b094fbd587869036aea6ac1e4af2f86d1254fb484d71826c66ed1bc077d7c3"
OLD_APPROVAL = "DEC-1037"  # every window's entry cites DEC-1037, the re-pin windows' decision
NEW_APPROVAL = "DEC-1178"  # the owner's decision of the release and the re-pin from it (DEC-1178 (3))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(why: str) -> None:
    print(f"REFUSED, nothing changed: {why}", file=sys.stderr)
    sys.exit(2)


if len(sys.argv) != 7:
    refuse("usage: rel_registry.py <commit12> <wheel sha256> <epoch> <version> <tag> <record sha256>")
COMMIT, EXPECTED, EPOCH, VERSION, TAG, RECORD = sys.argv[1:7]
if (len(COMMIT) != 12 or not re.fullmatch(r"[0-9a-f]{64}", EXPECTED) or not EPOCH.isdigit()
        or not re.fullmatch(r"\d+\.\d+\.\d+", VERSION) or TAG != f"v{VERSION}" or not re.fullmatch(r"[0-9a-f]{64}", RECORD)):
    refuse("usage: rel_registry.py <commit12> <wheel sha256> <epoch> <version> <tag v<version>> <record sha256>")
PINS = Path(os.environ.get("GOV_REPIN_PINS") or Path.home() / ".local/share/gov-os")
LINK_HOME = Path(os.environ.get("GOV_REPIN_LINK_HOME") or Path.home())
PIN = PINS / f"pin-{COMMIT}"
WHEEL = PINS / "wheels" / COMMIT / "gov-0.1.0-py3-none-any.whl"
OLD_START = f'  - name: gov\n    version: "0.1.0"\n    sha256: "{OLD_SHA}"\n'

if not WHEEL.is_file() or sha256(WHEEL) != EXPECTED:
    refuse(f"{WHEEL} is missing or its sha256 is not {EXPECTED}")
link = LINK_HOME / ".local/bin/gov"
if not link.is_symlink() or Path(os.path.realpath(link)) != (PIN / "bin/gov").resolve():
    refuse(f"{link} is not a link to {PIN / 'bin/gov'}")
script_sha = sha256(PIN / "bin/gov")
text = REGISTRY.read_text(encoding="utf-8")
if text.count(OLD_START) != 1:
    refuse(f"window 5's gov entry ({OLD_COMMIT}) is not in the registry exactly once")
start = text.index(OLD_START)
end = text.find("\n  - name: ", start + 1)
end = len(text) if end == -1 else end + 1
old = text[start:end]
if f'approved_by: "{OLD_APPROVAL}"' not in old or f"pin-{OLD_COMMIT}" not in old:
    refuse(f"the gov entry found is not window 5's (pin-{OLD_COMMIT}, {OLD_APPROVAL})")
today = datetime.date.today().isoformat()
new = (
    '  - name: gov\n'
    f'    version: "{VERSION}"\n'
    f'    sha256: "{EXPECTED}"\n'
    f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{COMMIT} && '
    f'~/.local/share/gov-os/pin-{COMMIT}/bin/python -m pip install --no-deps --no-index '
    f'~/.local/share/gov-os/wheels/{COMMIT}/gov-0.1.0-py3-none-any.whl && '
    f'ln -s ~/.local/share/gov-os/pin-{COMMIT}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov"\n'
    f'    uninstall: "ln -s ~/.local/share/gov-os/pin-{OLD_COMMIT}/bin/gov ~/.local/bin/gov.new && '
    f'mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov && rm -rf ~/.local/share/gov-os/pin-{COMMIT}"\n'
    f'    date: "{today}"\n'
    f'    approved_by: "{NEW_APPROVAL}"\n'
    f'    note: "Re-pin from release {VERSION} (DEC-1178 (3), P-RELEASE-1 §6): a non-editable install of the wheel of the '
    f'numbered release {VERSION} (W2-16, DEC-772), tag {TAG} on the release record commit whose parent is {COMMIT}; the '
    f'record docs/releases/{VERSION}/manifest.json (sha256 {RECORD}) states this wheel sha256. The wheel was built twice '
    f'here from commit {COMMIT} (git archive, then pip wheel --no-deps --no-build-isolation with '
    f'SOURCE_DATE_EPOCH={EPOCH}, the commit\'s time; the same bytes, equal to the record\'s), in its own environment '
    f'~/.local/share/gov-os/pin-{COMMIT} (Python 3.12, with the system and user site packages for PyYAML, pytest, '
    f'pytest-xdist, pytest-timeout and sqlite-vec), linked from ~/.local/bin/gov by an atomic rename; the integration '
    f'store rebuilt before the switch at the head of w2/integrate at that time (its src and pyproject.toml the '
    f'commit\'s: the script stops if they differ); the shared reranker restarted from the new pin only if its bytes '
    f'changed (class 3); the git hooks not touched. sha256 is the wheel\'s; the installed script ~/.local/bin/gov (a '
    f'link) has sha256 {script_sha}. Replaces window 5\'s entry (pin-{OLD_COMMIT}, {OLD_APPROVAL}); pin-{OLD_COMMIT} '
    f'stays for a one-command rollback (the uninstall line)."\n'
)
REGISTRY.write_text(text[:start] + new + text[end:], encoding="utf-8")
print(new)
print(f"written: {REGISTRY}; commit it with the decision trailer {NEW_APPROVAL} (Role: owner)")
