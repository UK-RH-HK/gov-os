"""Unit tests for the decision-citations check: the register file and the base commit (DEC-473, DEC-474)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check import citations  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402

PATH_MAP = "governance/project/path-map.yaml"
REGISTER = "records/log.md"


class Project:
    def __init__(self, root):
        self.root = root
        root.mkdir()
        self.env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@t",
                    "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(root.parent), "LC_ALL": "C"}
        self.git("init", "-q", "-b", "main")

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments], capture_output=True, check=True,
                              env=self.env, text=True).stdout.strip()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))

    def configure(self, **keys):
        """A path map the configuration loader accepts, with ``keys`` as further top-level lines."""
        self.write(PATH_MAP, "namespaces: {}\n" + "".join(f"{key}: {value}\n" for key, value in keys.items()))

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def flagged(self):
        return sorted((found["code"], found["commit"], found.get("decision") or found.get("path"))
                      for found in citations.check(self.root))


@pytest.fixture()
def project(tmp_path):
    return Project(tmp_path / "project")


# --------------------------------------------------------------------------
# _entries: the heading grammar
# --------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    "### DEC-101 The title", "### DEC-101: The title", "### DEC-101 — The title", "### DEC-101 - The title",
    "### DEC-101-The title", "### DEC-101 — The title\r",
])
def test_an_entry_heading_records_its_id(line):
    assert citations._entries(f"# Decisions\n\n{line}\n- body\n".encode("utf-8")) == {"DEC-101"}


@pytest.mark.parametrize("line", [
    "## DEC-101 — The title", "#### DEC-101 — The title", " ### DEC-101 — The title", "See ### DEC-101 — The title",
    "### DEC-101", "### DEC-101 ", "### DEC-101:", "### DEC-101 —", "### DEC-101x The title", "###DEC-101 The title",
    "### ADR-0101 — The title", " ### DEC-101 — The title",
])
def test_a_line_that_is_no_entry_heading_records_nothing(line):
    assert citations._entries(f"# Decisions\n\n{line}\n- body\n".encode("utf-8")) == set()


def test_a_longer_id_is_recorded_as_itself():
    assert citations._entries(b"### DEC-1010 - Another\n") == {"DEC-1010"}


def test_a_heading_in_a_fence_does_not_count_and_the_fence_ends_where_it_is_closed():
    text = ("```\n### DEC-101 - In a fence\n```\n### DEC-102 - After it\n"
            "~~~~ text\n### DEC-103 - In a fence\n```\n~~~\n### DEC-104 - Still in it\n~~~~\n### DEC-105 - After\n"
            "```\n### DEC-106 - In a fence that is never closed\n")
    assert citations._entries(text.encode("utf-8")) == {"DEC-102", "DEC-105"}


@pytest.mark.parametrize("content", [b"### DEC-101 - Title\n\xff\xfe", b"### DEC-101 - Title\n\0"])
def test_a_register_that_is_not_text_has_no_entries_to_give(content):
    assert citations._entries(content) is None


# --------------------------------------------------------------------------
# _configured: the two keys of the path map
# --------------------------------------------------------------------------

def test_no_path_map_and_a_path_map_without_the_keys_name_nothing(project):
    assert citations._configured(project.root) == (None, None)
    project.configure()
    assert citations._configured(project.root) == (None, None)


def test_the_two_keys_are_read(project):
    project.configure(decision_register=REGISTER, decision_citations_base='"0123abcd"')
    assert citations._configured(project.root) == (REGISTER, "0123abcd")


@pytest.mark.parametrize("key", ["decision_register", "decision_citations_base"])
@pytest.mark.parametrize("value", ["12345678", "[a, b]", "null", '""'])
def test_a_key_that_is_not_a_string_is_an_error_not_an_absent_key(project, key, value):
    project.configure(**{key: value})
    with pytest.raises(GovError) as raised:
        citations._configured(project.root)
    assert raised.value.code == "CITATIONS_CONFIG_INVALID" and key in raised.value.message


def test_a_path_map_that_is_not_yaml_is_the_loaders_error(project):
    project.write(PATH_MAP, "decision_register: [\n")
    with pytest.raises(GovError) as raised:
        citations.check(project.root)
    assert raised.value.code == "CONFIG_INVALID"


# --------------------------------------------------------------------------
# The register file at the citing commit
# --------------------------------------------------------------------------

def test_the_register_is_read_from_the_tree_of_the_citing_commit(project):
    project.configure(decision_register=REGISTER)
    project.write(REGISTER, "### DEC-101 - First\n")
    early = project.commit("Work (DEC-101, DEC-102)")
    project.write(REGISTER, "### DEC-102 - Second\n")
    late = project.commit("Work (DEC-101, DEC-102)")
    assert project.flagged() == sorted([("DECISION_UNRECORDED", early, "DEC-102"),
                                        ("DECISION_UNRECORDED", late, "DEC-101")])


def test_a_file_of_entries_that_is_not_named_records_nothing(project):
    project.write(REGISTER, "### DEC-101 - First\n")
    commit = project.commit("Work (DEC-101)")
    assert project.flagged() == [("DECISION_UNRECORDED", commit, "DEC-101")]


@pytest.mark.parametrize("state", ["absent", "directory", "link", "not-text"])
def test_a_named_register_that_cannot_be_read_is_a_finding_that_names_it(project, state):
    project.configure(decision_register=REGISTER)
    project.write("docs/adr/DEC-101.md", "---\nid: DEC-101\ntype: decision\n---\n")
    if state == "directory":
        project.write(f"{REGISTER}/part.md", "### DEC-101 - First\n")
    elif state == "link":
        project.write("records/real.md", "### DEC-101 - First\n")
        (project.root / REGISTER).symlink_to("real.md")
    elif state == "not-text":
        project.write(REGISTER, b"### DEC-101 - First\n\xff\xfe\n")
    commit = project.commit("Work (DEC-101)")
    assert project.flagged() == [("REGISTER_UNREADABLE", commit, REGISTER)]


# --------------------------------------------------------------------------
# The base commit
# --------------------------------------------------------------------------

def test_the_commits_after_the_base_are_judged_and_the_base_is_not(project):
    project.commit("Before (DEC-801)")
    base = project.commit("The base (DEC-802)")
    after = project.commit("After (DEC-900)")
    for written in (base, base[:8], base.upper()):
        project.configure(decision_citations_base=f'"{written}"')
        assert project.flagged() == [("DECISION_UNRECORDED", after, "DEC-900")]
    project.configure()
    assert len(project.flagged()) == 3


def test_a_name_of_hex_digits_is_not_a_base_commit(project):
    project.commit("Before (DEC-801)")
    project.commit("Named (DEC-802)")
    project.git("tag", "beef")
    project.commit("After")
    project.configure(decision_citations_base='"beef"')
    with pytest.raises(GovError) as raised:
        citations.check(project.root)
    assert raised.value.code == "CITATIONS_BASE_UNKNOWN"


def test_a_base_that_gives_nothing_to_judge_is_an_error(project):
    project.git("checkout", "-q", "-b", "aside")
    aside = project.commit("Aside")
    project.git("checkout", "-q", "--orphan", "other")
    head = project.commit("Work")
    project.git("tag", "v1")
    for base, code in ((aside, "CITATIONS_BASE_UNKNOWN"), ("0123456789abcdef0123456789abcdef01234567",
                       "CITATIONS_BASE_UNKNOWN"), ("v1", "CITATIONS_BASE_UNKNOWN"), ("--all", "CITATIONS_BASE_UNKNOWN"),
                       (head, "CITATIONS_NOTHING_JUDGED")):
        project.configure(decision_citations_base=f'"{base}"')
        with pytest.raises(GovError) as raised:
            citations.check(project.root)
        assert raised.value.code == code, base
