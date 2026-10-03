"""W1-48 — bubblewrap 0.9.0 and socat 1.8.0.0 are recorded as owner installs.

KPI success 3: "The sandbox prerequisites bubblewrap 0.9.0 and socat 1.8.0.0 are
recorded in governance/project/tool-registry.yaml as owner installs, with
version, install and uninstall commands, date and approving decision (DEC-141)".

KPI failure 2: "bubblewrap or socat is missing from the registry while gov
launch depends on it".

DEC-141: "the owner installed bubblewrap 0.9.0 and socat 1.8.0.0 with
``sudo apt-get``". DEC-197: "Older pins cite the decision that names them
(DEC-074, DEC-191, DEC-141)". DEC-203: both "enter the registry as owner
installs under DEC-141".

An owner install is recorded the way PyYAML's is (DEC-201): its install and
uninstall commands are ``sudo apt-get`` commands, which no agent session runs.

CAP-61 names its provider "Claude Code sandbox (bubblewrap 0.9.0, socat
1.8.0.0)": that line is how the contract says the launched sandbox depends on
the two. ``gov launch`` itself is W1-46.
"""

from __future__ import annotations

import datetime
import re

import pytest

import w1_48_support as support

# tool -> (names accepted for the entry, the version, the apt package, the command and its version flag)
PREREQS = {
    "bubblewrap": (support.BUBBLEWRAP, "0.9.0", "bubblewrap", ("bwrap", "--version")),
    "socat": (support.SOCAT, "1.8.0.0", "socat", ("socat", "-V")),
}
TOOLS = sorted(PREREQS)

APPROVAL = "DEC-141"
SUDO_APT = r"(?<![\w/-])sudo\s+(?:\S+=\S+\s+)*apt(?:-get)?\s+(?:-\S+\s+)*"


def _entry(registry, tool):
    return support.one(registry, PREREQS[tool][0])


def _package(tool):
    return rf"(?<![\w.+-]){re.escape(PREREQS[tool][2])}(?![\w.+-]|-)"


# --------------------------------------------------------------------------
# Success 3 and failure 2: the two entries
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool", TOOLS)
def test_a_sandbox_prerequisite_is_recorded_in_the_registry(registry, tool):
    """Failure 2: neither is missing."""
    _entry(registry, tool)


@pytest.mark.parametrize("tool", TOOLS)
def test_a_sandbox_prerequisite_is_recorded_at_the_version_the_owner_installed(registry, tool):
    version = PREREQS[tool][1]
    found = support.norm_version(_entry(registry, tool).get("version", ""))
    assert found == version, f"the registry records {tool} at {found!r}; DEC-141 records {version!r}"


@pytest.mark.parametrize("tool", TOOLS)
def test_a_sandbox_prerequisite_cites_dec_141(registry, tool):
    cited = support.approved_by(_entry(registry, tool))
    assert cited == APPROVAL, f"the {tool} entry's approved_by is {cited!r}; DEC-141 is the decision that names it"


@pytest.mark.parametrize("tool", TOOLS)
def test_dec_141_is_an_owner_decision_that_names_the_prerequisite_and_its_version(decisions, tool):
    """The register's side of the approval. It does not read the registry, so it holds before implementation."""
    assert APPROVAL in decisions, f"{APPROVAL} is not in {support.REGISTER_REL}"
    decision = decisions[APPROVAL]
    text = support.own_text(decision)
    assert decision.accepted_by_owner, f"{APPROVAL} is not accepted by the owner (status: {decision.status!r})"
    assert support.names_tool(text, tool), f"{APPROVAL} does not name {tool}"
    assert support.names_version(text, PREREQS[tool][1]), f"{APPROVAL} does not name {tool} {PREREQS[tool][1]}"


@pytest.mark.parametrize("tool", TOOLS)
def test_the_install_command_of_a_sandbox_prerequisite_is_the_owners(registry, tool):
    """ "As owner installs": ``sudo apt-get install`` of the package, as DEC-141 records it."""
    install = support.field(_entry(registry, tool), "install")
    assert re.search(SUDO_APT + r"install\b", install), (
        f"the {tool} entry's install command is not a `sudo apt-get install` (DEC-141): {install!r}"
    )
    assert re.search(_package(tool), install), (
        f"the {tool} entry's install command does not name the package {PREREQS[tool][2]}: {install!r}"
    )


@pytest.mark.parametrize("tool", TOOLS)
def test_the_uninstall_command_of_a_sandbox_prerequisite_is_the_owners(registry, tool):
    entry = _entry(registry, tool)
    uninstall = support.field(entry, "uninstall")
    assert uninstall and uninstall != support.field(entry, "install"), (
        f"the {tool} entry has no uninstall command of its own: {uninstall!r}"
    )
    assert re.search(SUDO_APT + r"(?:remove|purge|autoremove)\b", uninstall), (
        f"the {tool} entry's uninstall command is not a `sudo apt-get remove` or `purge`: {uninstall!r}"
    )
    assert re.search(_package(tool), uninstall), (
        f"the {tool} entry's uninstall command does not name the package {PREREQS[tool][2]}: {uninstall!r}"
    )


@pytest.mark.parametrize("tool", TOOLS)
def test_a_sandbox_prerequisite_carries_a_sha256_digest(registry, tool):
    """DEC-196: the distribution package's digest; its form is what can be checked offline."""
    value = support.field(_entry(registry, tool), "sha256")
    assert support.SHA256.fullmatch(value), f"the {tool} entry's sha256 is not a SHA-256 digest: {value!r}"


@pytest.mark.parametrize("tool", TOOLS)
def test_a_sandbox_prerequisite_carries_a_calendar_date(registry, tool):
    value = support.field(_entry(registry, tool), "date")
    assert support.ISO_DATE.match(value), f"the {tool} entry's date is not YYYY-MM-DD: {value!r}"
    datetime.date.fromisoformat(value[:10])


# --------------------------------------------------------------------------
# Failure 2: "while gov launch depends on it"
# --------------------------------------------------------------------------

def test_the_registry_records_the_prerequisites_the_contract_names_for_the_sandbox(registry):
    """Every tool and version in CAP-61's provider line "Claude Code sandbox (…)" is an entry at that version."""
    text = (support.REPO_ROOT / support.CONTRACT_REL).read_text(encoding="utf-8")
    line = re.search(r"^\s*- Claude Code sandbox \(([^)]*)\)\s*$", text, re.MULTILINE)
    assert line, f"{support.CONTRACT_REL} no longer names the sandbox's prerequisites in CAP-61's provider list"
    named = re.findall(r"([A-Za-z][\w-]*) (\d+(?:\.\d+)+)", line.group(1))
    assert named, f"CAP-61's provider line names no tool with a version: {line.group(0).strip()!r}"
    wrong = []
    for name, version in named:
        found = support.find(registry, PREREQS[name][0] if name in PREREQS else (name,))
        if not found:
            wrong.append(f"{name} {version}: not in the registry")
        elif support.norm_version(found[0].get("version", "")) != version:
            wrong.append(f"{name} {version}: recorded at {found[0].get('version')!r}")
    assert wrong == [], f"the sandbox depends on tools the registry does not record as the contract names them: {wrong}"


# --------------------------------------------------------------------------
# What is on this machine
# --------------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("tool", TOOLS)
def test_the_sandbox_prerequisite_on_this_machine_is_the_recorded_version(registry, tool):
    """``bwrap --version`` and ``socat -V`` print the version and touch nothing."""
    recorded = support.norm_version(_entry(registry, tool).get("version", ""))
    command, flag = PREREQS[tool][3]
    path = support.system_tool(command)
    assert path is not None, f"there is no `{command}` on PATH: {tool} is not installed on this machine"
    text, _ = support.printed_version([path, flag])
    head = text.splitlines()[:2]   # `socat -V` prints its version on the second line
    versions = support.VERSION_TOKEN.findall("\n".join(head))
    assert recorded in versions, f"{path} prints {head!r}; the registry records {tool} {recorded!r}"
