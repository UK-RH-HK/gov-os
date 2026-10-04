"""W1-46 -- the research allowlist: the kernel default, extended by the project's file (DEC-241).

KPI success 3 [CAP-61.c]: "research or experiment work gets an allowlist built
from an owner-extensible list (GitHub, PyPI, npm, Hugging Face, arXiv,
documentation sites)".

DEC-241: "``governance/project/research-allowlist.yaml`` extends the kernel
default. The owner extends the list." The starting hosts are the hosts the
decision names "and the subdomains of ``readthedocs.io``", less
``cdn-lfs.huggingface.co``, which DEC-316 drops because it does not resolve:
sixteen hosts, copied from the register into ``w1_46_support.STARTING_HOSTS``.

The project's file is this repository's, copied into the temporary project.
DEC-272: "The list is under the key ``hosts``. A project without
``governance/project/research-allowlist.yaml`` launches a research session on
the kernel default alone: no file means no extension."

"Nothing may fail open": a file that cannot be read as a list of host names
refuses the launch, with a non-zero exit and a named reason, and nothing is
started.

No session is started. That the sandbox accepts these entries is shown by the
research session of ``test_w1_46_live_sessions.py``.
"""

from __future__ import annotations

import pytest
import yaml

import w1_46_support as support

RESEARCH = support.RESEARCH


def _hosts(value):
    """The list of entries a research allowlist file holds, or None when it has another shape."""
    if isinstance(value, dict):
        lists = [item for item in value.values() if isinstance(item, list)]
        value = lists[0] if len(lists) == 1 else None
    return value if isinstance(value, list) else None


def test_this_repository_has_the_research_allowlist_file():
    """DEC-241 names the file; it is in the ticket's ``allowed_paths``. A list of host names, as text."""
    path = support.REPO_ROOT / support.ALLOWLIST_REL
    assert path.is_file(), f"{support.ALLOWLIST_REL} does not exist"
    entries = _hosts(yaml.safe_load(path.read_text(encoding="utf-8")))
    assert entries is not None, f"{support.ALLOWLIST_REL} holds no list of hosts (top level, or one list in a mapping)"
    assert all(isinstance(entry, str) and entry.strip() for entry in entries), (
        f"an entry of {support.ALLOWLIST_REL} is not a host name"
    )


def test_the_research_allowlist_carries_the_starting_hosts(launch):
    """Each of the sixteen hosts DEC-241 and DEC-316 leave is an entry of the built allowlist, under its own name."""
    assert len(set(support.STARTING_HOSTS)) == 16 and support.DROPPED_HOST not in support.STARTING_HOSTS
    domains = support.allowed_domains(launch(RESEARCH).settings())
    missing = [host for host in support.STARTING_HOSTS if host not in domains]
    assert missing == [], f"the built research allowlist does not carry {missing}; it holds {domains}"


def test_the_host_the_owner_dropped_is_not_in_the_built_allowlist(launch):
    """DEC-316: ``cdn-lfs.huggingface.co`` is no starting host, in the kernel default and in the project's file."""
    domains = support.allowed_domains(launch(RESEARCH).settings())
    assert support.DROPPED_HOST not in domains and not support.accepts(domains, support.DROPPED_HOST), (
        f"the built research allowlist still accepts {support.DROPPED_HOST}; it holds {domains}"
    )


def test_the_research_allowlist_carries_the_readthedocs_subdomain_entry(launch):
    """ "And the subdomains of readthedocs.io": the sandbox's subdomain form, which accepts a project's own host."""
    domains = support.allowed_domains(launch(RESEARCH).settings())
    assert support.READTHEDOCS_ENTRY in domains, (
        f"the built research allowlist has no entry {support.READTHEDOCS_ENTRY}; it holds {domains}"
    )
    assert support.accepts(domains, support.READTHEDOCS_HOST)


def test_the_research_allowlist_is_a_list_of_named_domains(launch):
    """Strict: no entry accepts every host, and a made-up host is not accepted."""
    domains = support.allowed_domains(launch(RESEARCH).settings())
    assert all(isinstance(entry, str) and entry.strip("*.") for entry in domains), f"an entry names no domain: {domains}"
    assert not support.accepts(domains, support.NOT_A_RESEARCH_HOST), "the research allowlist accepts a made-up host"


def test_a_host_added_to_the_project_file_is_in_the_built_allowlist(launch, project):
    """ "The owner extends the list": the file is read at launch, and it extends; it does not replace."""
    before = support.allowed_domains(launch(RESEARCH).settings())
    assert support.ADDED_HOST not in before
    support.rewrite_allowlist(project, lambda entries: entries + [support.ADDED_HOST])
    after = support.allowed_domains(launch(RESEARCH).settings())
    assert support.ADDED_HOST in after, (
        f"a host added to {support.ALLOWLIST_REL} is not in the next launch's allowlist: {after}"
    )
    lost = [host for host in (*support.STARTING_HOSTS, support.READTHEDOCS_ENTRY) if host not in after]
    assert lost == [], f"the allowlist lost starting hosts once the project file was extended: {lost}"


def test_the_project_file_does_not_reach_the_three_other_roles(launch, project):
    """DEC-158: engineer, test designer and auditor keep an empty allowlist, whatever the research list holds."""
    support.rewrite_allowlist(project, lambda entries: entries + [support.ADDED_HOST])
    for role in support.EMPTY_ALLOWLIST_ROLES:
        domains = support.allowed_domains(launch(role).settings())
        assert domains == [], f"the allowlist of a launched {role} is not empty: {domains}"


MALFORMED = {
    "not-yaml": None,
    "a-word-where-the-list-is": lambda entries: "github.com",
    "an-entry-that-is-a-number": lambda entries: entries + [42],
    "an-entry-that-is-a-mapping": lambda entries: entries + [{"host": support.ADDED_HOST}],
    "an-entry-that-is-empty": lambda entries: entries + [""],
    "an-entry-that-is-a-url": lambda entries: entries + [f"https://{support.ADDED_HOST}/simple/"],
    "an-entry-that-accepts-every-host": lambda entries: entries + ["*"],
}


@pytest.mark.parametrize("name", sorted(MALFORMED))
def test_a_malformed_allowlist_file_refuses_the_launch(launch, project, name):
    """Nothing fails open: no session with a part of the list, the kernel default alone, or every host."""
    launch(RESEARCH).session()
    if MALFORMED[name] is None:
        support.write(project, support.ALLOWLIST_REL, "hosts: [unclosed\n  - : :\n")
    else:
        support.rewrite_allowlist(project, MALFORMED[name])
    support.assert_refused(launch(RESEARCH), "allowlist")


# --------------------------------------------------------------------------
# DEC-272: the key is ``hosts``; a project without the file launches on the kernel default alone
# --------------------------------------------------------------------------

def test_this_repositorys_allowlist_holds_its_list_under_the_key_hosts():
    data = yaml.safe_load((support.REPO_ROOT / support.ALLOWLIST_REL).read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get(support.ALLOWLIST_KEY), list), (
        f"{support.ALLOWLIST_REL} holds no list under the key '{support.ALLOWLIST_KEY}'"
    )


OTHER_SHAPES = {
    "another-key": lambda hosts: {"allowed_domains": hosts},
    "a-list-at-the-top-level": lambda hosts: hosts,
}


@pytest.mark.parametrize("name", sorted(OTHER_SHAPES))
def test_a_list_that_is_not_under_the_key_hosts_refuses_the_launch(launch, project, name):
    """Nothing fails open: the owner's hosts under another key are not dropped silently."""
    launch(RESEARCH).session()
    hosts = [*support.STARTING_HOSTS, support.ADDED_HOST]
    support.write(project, support.ALLOWLIST_REL, yaml.safe_dump(OTHER_SHAPES[name](hosts), default_flow_style=False))
    support.assert_refused(launch(RESEARCH), "allowlist", support.ALLOWLIST_KEY)


def test_a_project_without_the_allowlist_file_launches_on_the_kernel_default_alone(launch, project):
    """DEC-272: "no file means no extension". The host the project's file added is gone with the file."""
    support.rewrite_allowlist(project, lambda entries: entries + [support.ADDED_HOST])
    assert support.ADDED_HOST in support.allowed_domains(launch(RESEARCH).settings())
    (project / support.ALLOWLIST_REL).unlink()
    result = launch(RESEARCH)
    assert result.run.returncode == 0, f"gov launch refused a project without {support.ALLOWLIST_REL}\n{result.describe()}"
    assert support.sandbox_faults(result.settings()) == []
    domains = support.allowed_domains(result.settings())
    missing = [host for host in (*support.STARTING_HOSTS, support.READTHEDOCS_ENTRY) if host not in domains]
    assert missing == [], f"without the project's file the allowlist lacks the kernel default's {missing}"
    assert support.ADDED_HOST not in domains, "a host of the removed file is still in the allowlist"
