"""KPI failures 2 and 3, second batch: secrets in path names, and roots the wrapper must refuse [CAP-12.b, CAP-03.e].

Behaviours a review described after the first suite went green (DEC-136):

- **A secret in a file name or a folder name.** The index stores paths, and a staged copy keeps them. A clean
  source file whose name is a token-shaped string, and a clean source file in a folder named like a canary, are
  not in the index at all: the planted value stands in no file and in no file or folder name under
  ``.gov-runtime/``, and comes back in no answer.
- **A root that is not the top level of a git repository** is refused: a sub-folder of a repository (an index
  there would be in the repository and outside its ``.gov-runtime/``), and a plain directory. Nothing is
  created, and nothing that stood there is deleted.
- **``.gov-runtime`` as a symbolic link** to a folder outside the repository is refused: the outside folder
  gains no file.

Refused means the child process raises; the exception's class and message are not held.
"""

from __future__ import annotations

import json

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

TOKEN_NAMED = f"app/{support.PATH_TOKEN}.py"
UNDER_SECRET_FOLDER = f"web/{support.FOLDER_SECRET}/panel.ts"
# Clean in their content: only the path holds a planted value.
PATH_SECRET_FILES = {
    TOKEN_NAMED: "def token_named_helper(value):\n    return value + 1\n\n\n"
                 "def token_named_entry(value):\n    return token_named_helper(value)\n",
    UNDER_SECRET_FOLDER: "export function canaryFolderLabel(name: string): string {\n  return name.trim();\n}\n\n"
                      "export function canaryFolderTitle(name: string): string {\n"
                      "  return canaryFolderLabel(name);\n}\n",
}
NEIGHBOURS = {
    "app/beside.py": "def beside_helper(value):\n    return value + 1\n\n\n"
                     "def beside_entry(value):\n    return beside_helper(value)\n",
    "web/beside.ts": "export function besideLabel(name: string): string {\n  return name.trim();\n}\n\n"
                     "export function besideTitle(name: string): string {\n  return besideLabel(name);\n}\n",
    "README.md": "# Paths\n\nA repository with clean files, two of them under a path that holds a fake secret.\n",
}
ONLY_UNDER_SECRET_PATHS = ("token_named_helper", "token_named_entry", "canaryFolderLabel", "canaryFolderTitle")
IN_NEIGHBOURS = {"beside_helper": "app/beside.py", "besideLabel": "web/beside.ts"}

SMALL = {"lib/small.py": "def small_helper(value):\n    return value + 1\n\n\n"
                         "def small_entry(value):\n    return small_helper(value)\n"}


def _repository(base, files):
    repo = support.Repo(base)
    for rel, text in files.items():
        repo.write(rel, text)
    return repo.commit("first")


# --------------------------------------------------------------------------
# A secret in a file name or a folder name (failure 3)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pathed(module, cbm, gitleaks, module_sandbox, tmp_path_factory):
    """A repository with a token-shaped file name and a canary folder name, indexed once through the wrapper."""
    repo = _repository(tmp_path_factory.mktemp("w1-16-paths") / "pathed", {**PATH_SECRET_FILES, **NEIGHBOURS})
    support.codeintel(repo.root, [("index", [])], module_sandbox)
    return repo


@pytest.mark.parametrize("config", list(support.CONFIGS), indirect=True)
def test_the_planted_path_names_are_secrets_by_the_rules(gitleaks, config, sandbox, tmp_path):
    """The premise: written in a file, the file name is flagged by the token rule and the folder name by the canary rule."""
    target = support.plant_tree(tmp_path / "tree", {"notes/token.md": support.in_prose(support.PATH_TOKEN),
                                                    "notes/folder.md": support.in_prose(support.FOLDER_SECRET)})
    found = support.scan(target, config, sandbox)
    assert [rule for rel, rule in found if rel == "notes/token.md" and rule.startswith(support.TOKEN_RULE)], \
        f"the planted file name is not token-shaped by the rules: {found}"
    assert ("notes/folder.md", "gov-canary") in found, f"the planted folder name is no canary by the rules: {found}"


def test_no_secret_of_a_path_name_stands_under_gov_runtime(pathed, module_sandbox, sandbox):
    """Neither in a file (bytes and SQLite rows: the index stores paths) nor in a file or folder name (a staged copy)."""
    runtime = pathed.root / support.RUNTIME_REL
    home = support.one(pathed.root, "home", [], sandbox)
    assert support.index_files(home), f"nothing was indexed: {home} holds no index file"
    named = support.names_holding(runtime, support.PATH_PLANTED)
    assert not named, f"{len(named)} file or folder name(s) under .gov-runtime/ hold a planted path secret"
    found = support.files_holding(runtime, support.PATH_PLANTED)
    assert not found, \
        f"planted path secrets stand in files under .gov-runtime/: { {rel: len(hits) for rel, hits in found.items()} }"
    for place in module_sandbox.places:
        left = support.files_holding(place, support.PATH_PLANTED) or support.names_holding(place, support.PATH_PLANTED)
        assert not left, f"planted path secrets were left in {place}: {len(left)} place(s)"


def test_a_file_under_a_secret_path_is_not_in_the_code_graph(pathed, sandbox):
    """Its functions have no definition, no answer names its path, and the clean files next to it are answered."""
    calls = [(kind, [name]) for name in ONLY_UNDER_SECRET_PATHS
             for kind in ("definitions", "references", "callers", "impact")] + [("dead_code", [])]
    calls += [("definitions", [name]) for name in IN_NEIGHBOURS] + [("callers", ["beside_helper"])]
    run = support.codeintel(pathed.root, calls, sandbox)
    asked = dict(zip(run.calls, run.results))
    leaked = [number for number, secret in enumerate(support.PATH_PLANTED)
              if secret in json.dumps(run.results) + run.output]
    assert not leaked, f"{len(leaked)} planted path secret(s) came back from the code graph"
    known = [name for name in ONLY_UNDER_SECRET_PATHS if asked[("definitions", (name,))]]
    assert not known, f"functions of files under a secret path have a definition: {known}"
    for name, rel in IN_NEIGHBOURS.items():
        found = support.entries(asked[("definitions", (name,))], f"definitions({name})", pathed.root)
        assert (rel, name) in found, f"the clean file {rel} next to a secret path is not indexed"
    callers = support.entries(asked[("callers", ("beside_helper",))], "callers(beside_helper)", pathed.root)
    assert ("app/beside.py", "beside_entry") in callers, "the clean file app/beside.py has lost its caller"


def test_the_secrets_indexing_check_of_w1_15_stays_green_with_secret_path_names(pathed, sandbox):
    """The backstop (W1-15): no store under ``.gov-runtime/`` holds a secret by the project's rules."""
    run = support.run_calls("gov.secrets", pathed.root, [("stores_with_secrets", [])], sandbox)
    assert run.results is not None, f"gov.secrets.stores_with_secrets did not answer (exit code {run.returncode})"
    assert run.results[0] == [], f"{len(run.results[0])} store(s) hold a secret"


# --------------------------------------------------------------------------
# A root that is not the top level of a git repository (failure 2)
# --------------------------------------------------------------------------

def test_a_sub_folder_of_a_repository_is_refused_and_nothing_is_created(module, cbm, gitleaks, sandbox, tmp_path):
    """An index of the sub-folder would stand in the repository, outside the repository's ``.gov-runtime/``."""
    outer = _repository(tmp_path / "outer", SMALL)
    # The sub-folder is adopted as a project is, so that the filter can answer there: only the root is wrong.
    inner = support.Repo(outer.root / "pkg", fresh=False)
    inner.write("src/inner.py", "def inner_helper(value):\n    return value - 1\n")
    outer.commit("a sub-folder with its own path map and gitleaks file")
    before = {"repository": support.tree(outer.root, skip=(".git",)),
              **{place: support.tree(place) for place in (sandbox.home, sandbox.tmpdir, sandbox.elsewhere)}}

    run = support.run_calls("gov.codeintel", inner.root, [("index", [])], sandbox)

    created = sorted(support.tree(outer.root, skip=(".git",)) - before["repository"])
    assert support.refused(run), \
        f"index(root) on a sub-folder of a repository was not refused; it created {created[:8]}\n{run.describe()}"
    assert not created, f"the refused call created files in the repository: {created[:8]}"
    assert outer.status() == [], f"the refused call changed the repository: {outer.status()}"
    for place in (sandbox.home, sandbox.tmpdir, sandbox.elsewhere):
        left = sorted(support.tree(place) - before[place])
        assert not left, f"the refused call created files in {place}: {left[:8]}"
    assert not support.index_files(sandbox.runtime), "the refused call left an index file in the runtime directory"


def test_a_directory_that_is_no_git_repository_is_refused_and_nothing_is_deleted(module, cbm, gitleaks, sandbox,
                                                                                tmp_path):
    """A refused call leaves the directory as it was: an earlier ``.gov-runtime/codeintel/`` is still there."""
    plain = tmp_path / "plain"
    files = {
        support.PATH_MAP_REL: support.path_map_text(support.EVERYTHING),
        "lib/plain.py": "def plain_helper(value):\n    return value + 1\n",
        f"{support.RUNTIME_REL}/codeintel/home/earlier.txt": "an earlier index stood here\n",
        f"{support.RUNTIME_REL}/codeintel/files/lib/plain.py": "def plain_helper(value):\n    return value + 1\n",
        f"{support.RUNTIME_REL}/other/keep.txt": "another store of the directory\n",
    }
    support.plant_tree(plain, files)
    (plain / support.ROOT_CONFIG_REL).write_bytes(support.config_path("template").read_bytes())
    before, before_files = support.tree(plain), support.snapshot(plain)

    run = support.run_calls("gov.codeintel", plain, [("index", [])], sandbox)

    assert support.refused(run), f"index(root) on a directory that is no git repository was not refused\n{run.describe()}"
    after = support.tree(plain)
    assert not sorted(before - after), f"the refused call deleted: {sorted(before - after)}"
    assert not sorted(after - before), f"the refused call created: {sorted(after - before)[:8]}"
    assert support.snapshot(plain) == before_files, "the refused call changed a file of the directory"


# --------------------------------------------------------------------------
# .gov-runtime as a symbolic link (failure 2)
# --------------------------------------------------------------------------

def test_a_gov_runtime_that_links_outside_the_repository_is_refused(module, cbm, gitleaks, sandbox, tmp_path):
    """The index, the tool's files and the staged copy would be written outside the repository."""
    repo = _repository(tmp_path / "linked", SMALL)
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo.root / support.RUNTIME_REL).symlink_to(outside, target_is_directory=True)

    run = support.run_calls("gov.codeintel", repo.root, [("index", [])], sandbox)

    gained = sorted(support.tree(outside))
    assert support.refused(run), \
        f"index(root) was not refused though .gov-runtime links outside the repository; the outside folder gained " \
        f"{len(gained)} path(s), such as {gained[:5]}"
    assert not gained, f"the refused call wrote into the folder outside the repository: {gained[:8]}"
    assert (repo.root / support.RUNTIME_REL).is_symlink(), "the refused call replaced the link"
