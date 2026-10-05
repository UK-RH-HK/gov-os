"""Fourth batch: gitleaks' built-in allowlist shelters nothing (DEC-347); no secret in the daemon directory (DEC-346) [CAP-03.e, CAP-12.b].

Tests added after implementation, reason "delegated decision":

- **DEC-347.** gitleaks' built-in defaults carry a global allowlist, and ``[extend] useDefault = true`` (both
  gitleaks files have it) merges it over every rule, the project's included. A canary or a token-shaped string
  that holds the alphabet run in lower or upper case, holds ``false``, begins with ``true`` or ends with ``null``
  is therefore not reported, though the project's canary rule or token rules flag it once the built-in allowlist
  is not there. The pre-index filter ``gov.secrets.indexable(root, paths)`` leaves out a file whose content holds
  such a string, and ``gov.secrets.path_holds_secret(root, path)`` is true for a path whose name holds one. The
  same words with no secret change nothing: the file is returned, the path name is no secret.
- **DEC-346.** The files the tool's daemon leaves in ``gov.codeintel.daemon_dir(root)`` are an accepted residual.
  After an index run of a repository with a planted secret, no file of that directory holds the planted string.

Only what the filter refuses and what it lets through is held, not how it decides. Nothing is asserted about the
pre-commit hook or about a plain ``gitleaks`` run with either file as it is.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

CLEAN_PAGE = "notes/clean.md"
CLEAN_TEXT = "# Notes\n\nOrdinary text.\n"


def _written(kind, value):
    """The file a sheltered value is planted in: a token as a string value in code, a canary in prose."""
    if kind == "token":
        return "app/planted.py", f'"""Settings."""\n\nVALUE = "{value}"\n'
    return "notes/planted.md", support.in_prose(value)


# --------------------------------------------------------------------------
# The premise: the planted values are secrets by the project's own rules
# --------------------------------------------------------------------------

def test_the_sheltered_values_are_secrets_by_the_projects_rules_alone(gitleaks, tmp_path, sandbox):
    """With either file's rules and no ``[extend]``, each planted value is flagged by its rule, and the clean files by none."""
    planted = {}
    for shelter, (kind, value) in support.SHELTERED.items():
        planted[f"content/{shelter}/" + _written(kind, value)[0]] = (kind, _written(kind, value)[1])
    for shelter, (kind, value) in support.PATH_SHELTERED.items():
        planted[f"path/{shelter}.txt"] = (kind, support.sheltered_path(kind, value) + "\n")
    clean = {f"clean/{rel}": text for rel, text in support.SHELTER_WORDS_CLEAN.items()}
    clean["clean/paths.txt"] = "\n".join(support.SHELTER_WORDS_PATHS) + "\n"
    tree = support.plant_tree(tmp_path / "tree", {**{rel: text for rel, (_, text) in planted.items()}, **clean})
    for which in support.CONFIGS:
        findings = support.scan(tree, support.rules_alone(which, tmp_path / f"{which}-alone.toml"), sandbox)
        missed = sorted(rel for rel, (kind, _) in planted.items()
                        if not any(file == rel and rule.startswith(support.rule_family(kind))
                                   for file, rule in findings))
        assert not missed, f"{which}: the rules alone do not flag a planted value under its own rule: {missed}"
        extra = sorted(finding for finding in findings if finding[0] in clean)
        assert not extra, f"{which}: the rules alone flag a file that holds only ordinary words: {extra}"


# --------------------------------------------------------------------------
# DEC-347: the filter
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shelter", list(support.SHELTERED))
def test_a_file_with_a_secret_the_builtin_allowlist_shelters_is_not_indexable(gitleaks, shelter, tmp_path, sandbox):
    """A canary or a token of the project's rules stays out of an index, whatever gitleaks' own defaults allow."""
    kind, value = support.SHELTERED[shelter]
    repo = support.Repo(tmp_path / "project")
    rel, text = _written(kind, value)
    planted, clean = repo.write(rel, text), repo.write(CLEAN_PAGE, CLEAN_TEXT)
    allowed = support.indexable(repo.root, [planted, clean], sandbox)
    assert planted not in allowed, \
        f"a {kind} that gitleaks' built-in allowlist shelters ({shelter}) is let through to the indexer: {allowed}"
    assert allowed == [clean], f"the clean neighbour was dropped too: {allowed}"


def test_a_file_with_the_sheltering_words_and_no_secret_is_indexable(gitleaks, tmp_path, sandbox):
    """Clean stays clean: the alphabet run, ``false``, ``true`` and ``null`` in ordinary code and prose keep no file out."""
    repo = support.Repo(tmp_path / "project")
    asked = [repo.write(rel, text) for rel, text in support.SHELTER_WORDS_CLEAN.items()]
    allowed = support.indexable(repo.root, asked, sandbox)
    assert allowed == asked, f"a file with ordinary words and no secret is kept from the indexer: {allowed}"


# --------------------------------------------------------------------------
# DEC-347: the path-name check
# --------------------------------------------------------------------------

def _verdict(repo, rel, what, sandbox):
    """``path_holds_secret(root, path)`` for one path: ``True`` or ``False``."""
    run = support.run_calls("gov.secrets", repo.root, [(support.NAME_CHECK, [rel])], sandbox)
    if run.results is None:   # said without the run itself: its call holds the planted name
        pytest.fail(f"gov.secrets.{support.NAME_CHECK}(root, path) did not answer for {what} (exit code "
                    f"{run.returncode}):\n{run.stderr[-800:]}", pytrace=False)
    verdict = run.results[0]
    assert verdict is True or verdict is False, f"{support.NAME_CHECK}(root, path) returns no truth value: {verdict!r}"
    return verdict


@pytest.mark.parametrize("shelter", list(support.PATH_SHELTERED))
def test_a_path_name_with_a_secret_the_builtin_allowlist_shelters_holds_a_secret(gitleaks, shelter, tmp_path, sandbox):
    """A token-shaped file name and a folder named like a canary are secrets, whatever gitleaks' own defaults allow."""
    kind, value = support.PATH_SHELTERED[shelter]
    repo = support.Repo(tmp_path / "project")
    rel = repo.write(support.sheltered_path(kind, value), "def helper(value):\n    return value + 1\n")
    beside = repo.write("app/beside.py", "def beside_helper(value):\n    return value + 1\n")
    assert _verdict(repo, rel, f"the {kind} in a path name", sandbox) is True, \
        f"a path name with a {kind} that gitleaks' built-in allowlist shelters ({shelter}) is not told as a secret"
    assert _verdict(repo, beside, "the ordinary path", sandbox) is False, "an ordinary path name is told as a secret"


def test_a_path_name_with_the_sheltering_words_and_no_secret_holds_no_secret(gitleaks, tmp_path, sandbox):
    """Clean stays clean: ``true``, ``false``, ``null`` and the alphabet run in ordinary file and folder names."""
    repo = support.Repo(tmp_path / "project")
    told = {}
    for rel in support.SHELTER_WORDS_PATHS:
        repo.write(rel, "\n")
        told[rel] = _verdict(repo, rel, rel, sandbox)
    secrets = sorted(rel for rel, verdict in told.items() if verdict)
    assert not secrets, f"an ordinary path name is told as a secret: {secrets}"


# --------------------------------------------------------------------------
# DEC-346: the daemon directory
# --------------------------------------------------------------------------

DAEMON_PLANTED = (support.STRING_SECRET, support.COMMENT_SECRET, support.NAME_SECRET)
DAEMON_FILES = {
    "app/settings.py": (
        '"""Settings."""\n\n'
        f'API_KEY = "{support.STRING_SECRET}"\n\n'
        f"# rotated value: {support.COMMENT_SECRET}\n"
        f"def {support.NAME_SECRET}(value):\n"
        "    return settings_helper(value)\n\n\n"
        "def settings_helper(value):\n"
        "    return value + 1\n"
    ),
    "app/clean.py": "def clean_helper(value):\n    return value + 1\n\n\n"
                    "def clean_entry(value):\n    return clean_helper(value)\n",
}


def test_no_planted_secret_stands_in_the_daemon_directory_after_an_index_run(module, cbm, gitleaks, tmp_path, sandbox):
    """The bytes of every regular file under ``daemon_dir(root)``; what cannot be read as a file (a socket) is skipped."""
    repo = support.Repo(tmp_path / "planted")
    for rel, text in DAEMON_FILES.items():
        repo.write(rel, text)
    repo.commit("first")
    run = support.codeintel(repo.root, [("index", []), ("callers", ["clean_helper"]),
                                        ("definitions", ["settings_helper"]), ("daemon_dir", [])], sandbox)
    _, callers, left_out, directory = run.results
    assert "clean_entry" in [name for _, name in support.entries(callers, "callers")], \
        "the index was not built: the clean file has no caller in it"
    assert support.entries(left_out, "definitions") == [], \
        "the premise does not hold: the file with the planted secret was indexed"
    assert isinstance(directory, str) and Path(directory).is_absolute() and Path(directory).is_dir(), \
        f"daemon_dir(root) is no directory after a run of the tool: {directory!r}"
    named = support.names_holding(directory, DAEMON_PLANTED)
    assert not named, f"{len(named)} file or folder name(s) of the daemon directory hold a planted secret"
    found, read, skipped = support.regular_files_holding(directory, DAEMON_PLANTED)
    assert not found, \
        f"planted secrets stand in the daemon directory {directory}: " \
        f"{ {rel: len(hits) for rel, hits in found.items()} } ({len(read)} file(s) read, {len(skipped)} skipped)"
