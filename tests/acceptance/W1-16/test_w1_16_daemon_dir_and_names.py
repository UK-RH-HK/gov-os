"""Third batch: the daemon's directory (DEC-338), and two repairs of the secret rules (DEC-339) [CAP-12, CAP-03.e].

Tests added after implementation, reason "delegated decision":

- **DEC-338.** The tool's daemon keeps lock and socket files in the folder ``cbm-daemon-<uid>`` of a runtime
  directory: ``CBM_RUNTIME_DIR``, or ``/tmp``, one shared default for every repository of the user. The wrapper
  sets a directory of its own for each repository
  (``gov.codeintel.daemon_dir(root)``): outside the repository, short enough for a socket path, and decided by
  the wrapper, whatever the caller's environment says. A run leaves the shared default as it was.
- **DEC-339 R-1.** A prefixed string whose body begins with ``_`` or ``-`` is flagged by the token rule when the
  rest of the body is token-shaped (DEC-325), and not when the rest is an ordinary identifier or too short.
- **DEC-339 R-3.** ``gov.secrets.path_holds_secret(root, path)`` says whether a path name holds a secret by the
  project's rules, allowlists ignored (DEC-287, DEC-298); the wrapper imports no private name of ``gov.secrets``.

The child that runs without ``CBM_RUNTIME_DIR`` has a namespace of its own, in which the tool's shared default is a
directory of the sandbox: nothing reaches the user's.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

import w1_16_support as support

BOTH = pytest.mark.parametrize("config", list(support.CONFIGS), indirect=True)
WHICH = pytest.mark.parametrize("which", list(support.CONFIGS))

ALPHA = {"app/alpha.py": "def alpha_only_helper(value):\n    return value + 1\n\n\n"
                         "def alpha_entry(value):\n    return alpha_only_helper(value)\n"}
BETA = {"lib/beta.py": "def beta_only_helper(value):\n    return value * 2\n\n\n"
                       "def beta_entry(value):\n    return beta_only_helper(value)\n"}
LONG = {"lib/long.py": "def long_helper(value):\n    return value - 1\n"}
LONG_ROOT_BYTES = 150


def _repository(base, files):
    repo = support.Repo(base)
    for rel, text in files.items():
        repo.write(rel, text)
    return repo.commit("first")


def _stand_in(sandbox, name):
    made = sandbox.base / name
    made.mkdir(mode=0o700)
    return made


# --------------------------------------------------------------------------
# DEC-338: the daemon's directory
# --------------------------------------------------------------------------

@dataclass
class Daemons:
    alpha: support.Repo
    beta: support.Repo
    long: support.Repo
    given: Path             # the directory the caller's environment names, for beta's run
    absent_run: support.Run  # index and an answer for alpha, with no CBM_RUNTIME_DIR in the environment
    given_run: support.Run   # the same for beta, with CBM_RUNTIME_DIR naming ``given``
    shared_after: dict       # run -> what stands in the shared default the run saw (empty before it)
    given_after: list        # what stands in ``given`` after beta's run (empty before it)
    asked: dict              # key -> the run that asked daemon_dir(root)


@pytest.fixture(scope="module")
def daemons(module, cbm, gitleaks, namespace, module_sandbox, tmp_path_factory):
    """Two repositories indexed and asked through the wrapper, one without and one with a directory given by the caller."""
    sandbox, tmp_path = module_sandbox, tmp_path_factory.mktemp("w1-16-daemon")
    alpha, beta = _repository(tmp_path / "alpha", ALPHA), _repository(tmp_path / "beta", BETA)
    deep = tmp_path.joinpath(*["a-folder-with-a-long-name"] * 6) / "long"
    long = _repository(deep, LONG)   # never indexed: only its directory is asked for
    given = _stand_in(sandbox, "g")
    shared = {name: _stand_in(sandbox, name) for name in ("s1", "s2", "s3")}
    absent, named = support.daemon_env(sandbox), support.daemon_env(sandbox, given)

    def run(repo, calls, env, stand_in):
        return support.run_calls("gov.codeintel", repo.root, calls, sandbox, env=env,
                                 launcher=namespace(shared[stand_in]))

    shared_after = {}
    absent_run = run(alpha, [("index", []), ("callers", ["alpha_only_helper"])], absent, "s1")   # one job at a time
    shared_after["absent"] = sorted(support.tree(shared["s1"]))
    given_run = run(beta, [("index", []), ("callers", ["beta_only_helper"])], named, "s2")
    shared_after["given"], given_after = sorted(support.tree(shared["s2"])), sorted(support.tree(given))
    asked = {
        "alpha": run(alpha, [("daemon_dir", [])], absent, "s3"),
        "beta": run(beta, [("daemon_dir", [])], named, "s3"),
        "long": run(long, [("daemon_dir", [])], absent, "s3"),
        "alpha, a directory given": run(alpha, [("daemon_dir", [])], named, "s3"),
        "alpha, as the suite runs it": run(alpha, [("daemon_dir", [])], support.child_env(sandbox), "s3"),
    }
    return Daemons(alpha, beta, long, given, absent_run, given_run, shared_after, given_after, asked)


def _dir(daemons, key):
    """What ``daemon_dir(root)`` answered: an absolute path."""
    run = daemons.asked[key]
    assert run.results is not None, \
        f"gov.codeintel.daemon_dir(root) did not answer for {key} (exit code {run.returncode}):\n{run.stderr[-800:]}"
    value = run.results[0]
    assert isinstance(value, str) and Path(value).is_absolute(), \
        f"daemon_dir(root) for {key} is no absolute path: {value!r}"
    return Path(value)


def _answered(run, caller):
    """The run built the index and answered from it: a wrapper that runs no tool has no daemon to place."""
    assert run.results is not None, f"the wrapper did not index and answer\n{run.describe()}"
    assert caller in [name for _, name in support.entries(run.results[1], "callers")], \
        f"the index was not built: {caller} is no caller\n{run.describe()}"


@pytest.mark.local_only
def test_the_tool_alone_keeps_its_daemon_files_in_one_shared_default(cbm, namespace, sandbox, tmp_path):
    """The premise: with no ``CBM_RUNTIME_DIR`` the tool uses its shared default, whatever TMPDIR and XDG_RUNTIME_DIR say."""
    stand_in = _stand_in(sandbox, "s")
    source = support.plant_tree(tmp_path / "plain", ALPHA)
    env = support.daemon_env(sandbox) | {"CBM_CACHE_DIR": str(tmp_path / "home")}
    env.pop("PYTHONPATH")
    done = subprocess.run([*namespace(stand_in), support.TOOL, "cli", "--quiet", "--json", "index_repository",
                           json.dumps({"repo_path": str(source), "name": "plain"})],
                          cwd=str(sandbox.elsewhere), env=env, capture_output=True, text=True,
                          timeout=support.TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"{support.TOOL} could not index (exit code {done.returncode}):\n{done.stderr[-800:]}"
    assert support.daemon_files(stand_in), \
        f"the tool alone left no daemon file in its shared default {support.TOOL_SHARED_RUNTIME}"
    for place in (sandbox.runtime, sandbox.tmpdir, sandbox.home, sandbox.elsewhere):
        left = support.daemon_files(place)
        assert not left, f"the tool alone kept daemon files in {place}: {left[:5]}"


@pytest.mark.local_only
def test_a_run_does_not_use_the_tools_shared_default(daemons):
    """With no ``CBM_RUNTIME_DIR`` in the caller's environment, ``index(root)`` and an answer leave the shared default as it was."""
    _answered(daemons.absent_run, "alpha_entry")
    left = daemons.shared_after["absent"]
    assert not left, \
        f"the run used the tool's shared default {support.TOOL_SHARED_RUNTIME}: it gained {len(left)} file(s), " \
        f"such as {left[:4]}"
    directory = _dir(daemons, "alpha")
    shared = support.TOOL_SHARED_RUNTIME.resolve()
    assert directory.resolve() != shared and not directory.resolve().is_relative_to(shared), \
        f"the wrapper's directory {directory} is the tool's shared default, or in it"
    assert directory.is_dir() and support.daemon_files(directory), \
        f"the wrapper's directory {directory} holds no daemon file after a run: the daemon did not use it"


@pytest.mark.local_only
def test_a_directory_given_by_the_callers_environment_is_not_used(daemons):
    """The wrapper decides: a ``CBM_RUNTIME_DIR`` of the caller is neither where the daemon's files go nor what ``daemon_dir`` answers."""
    _answered(daemons.given_run, "beta_entry")
    assert not daemons.given_after, \
        f"the daemon's files went to the directory the caller's environment gave: {len(daemons.given_after)} " \
        f"file(s), such as {daemons.given_after[:4]}"
    assert not daemons.shared_after["given"], \
        f"the run used the tool's shared default: {daemons.shared_after['given'][:4]}"
    directory, given = _dir(daemons, "beta").resolve(), daemons.given.resolve()
    assert directory != given and not directory.is_relative_to(given), \
        f"daemon_dir(root) follows the caller's CBM_RUNTIME_DIR: {directory}"
    same = {key: _dir(daemons, key) for key in ("alpha", "alpha, a directory given", "alpha, as the suite runs it")}
    assert len(set(same.values())) == 1, f"daemon_dir(root) of one repository changes with the caller's environment: {same}"


@pytest.mark.local_only
def test_each_repository_has_a_daemon_directory_of_its_own(daemons):
    found = {key: _dir(daemons, key).resolve() for key in ("alpha", "beta", "long")}
    assert len(set(found.values())) == 3, f"repositories share a daemon directory: {found}"


@pytest.mark.local_only
def test_the_daemon_directory_is_outside_the_repository(daemons):
    """Not in the repository, so not under its ``.gov-runtime/``; and no daemon file stands in a repository after a run."""
    for key, repo in (("alpha", daemons.alpha), ("beta", daemons.beta), ("long", daemons.long)):
        directory, root = _dir(daemons, key).resolve(), repo.root.resolve()
        assert directory != root and not directory.is_relative_to(root), \
            f"{key}: the daemon directory {directory} is in the repository"
        assert not root.is_relative_to(directory), f"{key}: the repository is in the daemon directory {directory}"
    for key, repo in (("alpha", daemons.alpha), ("beta", daemons.beta)):
        inside = support.daemon_files(repo.root)
        assert not inside, f"{key}: daemon files stand in the repository: {inside[:5]}"
        assert repo.status() == [], f"{key}: the run changed the repository outside .gov-runtime/: {repo.status()}"


@pytest.mark.local_only
def test_a_socket_path_in_the_daemon_directory_fits_in_a_socket_address(daemons):
    """However long the repository's own path is: the daemon's longest socket path under the directory has at most 107 bytes."""
    assert len(os.fsencode(str(daemons.long.root))) >= LONG_ROOT_BYTES, "the long repository's path is not long"
    for key in ("alpha", "beta", "long"):
        directory = _dir(daemons, key)
        size = len(os.fsencode(str(directory)))
        assert size <= support.DAEMON_DIR_MAX, \
            f"{key}: the daemon directory has {size} bytes, more than {support.DAEMON_DIR_MAX}: the socket path " \
            f"{directory / support.DAEMON_SOCKET_REL} does not fit in {support.SOCKET_PATH_MAX} bytes"


# --------------------------------------------------------------------------
# DEC-339 R-1: a token body that begins with ``_`` or ``-``
# --------------------------------------------------------------------------

def _page(key):
    return f"notes/{key}.md"


@pytest.mark.local_only
@BOTH
def test_a_body_that_begins_with_a_separator_is_flagged_only_when_the_rest_is_token_shaped(gitleaks, config, tmp_path,
                                                                                         sandbox):
    """Flagged: the rest holds a digit or mixed case, 16 characters or more. Not flagged: lower-case or upper-case words, or a short rest."""
    tokens = {_page(key): support.in_prose(support.leading(*parts)) for key, parts in support.LEADING_TOKENS.items()}
    ordinary = {_page(key): support.in_prose(support.leading(*parts))
                for key, parts in support.LEADING_ORDINARY.items()}
    short = {_page("short-rest"): support.in_prose(support.leading(*support.LEADING_SHORT))}
    findings = support.scan(support.plant_tree(tmp_path / "tree", {**tokens, **ordinary, **short}), config, sandbox)
    flagged = sorted({file for file, rule in findings if rule.startswith(support.TOKEN_RULE)})
    missed, extra = sorted(set(tokens) - set(flagged)), sorted(set(flagged) - set(tokens))
    assert not missed, f"a body that begins with a separator and is token-shaped after it is not flagged: {missed}"
    assert not extra, f"a near miss that begins with a separator is flagged by the token rule: {extra}"
    other = sorted(finding for finding in findings if finding[0] in ordinary)
    assert not other, f"an ordinary identifier that begins with a separator is flagged: {other}"


@pytest.mark.local_only
@WHICH
def test_a_file_with_a_token_whose_body_begins_with_a_separator_is_not_indexable(gitleaks, which, tmp_path, sandbox):
    """Through the pre-index filter, with either file as the project's ``.gitleaks.toml``; the near miss is let through."""
    repo = support.Repo(tmp_path / "project", config=which)
    planted = [repo.write(_page(key), support.in_prose(support.leading(*parts)))
               for key, parts in support.LEADING_TOKENS.items()]
    name = support.leading(*support.LEADING_ORDINARY["underscore-lower-words"])
    near = repo.write("app/registry.py", f"def {name}(handlers):\n    return sorted(handlers)\n")
    clean = repo.write("notes/clean.md", "# Notes\n\nOrdinary text.\n")
    allowed = support.indexable(repo.root, [*planted, near, clean], sandbox)
    through = sorted(set(allowed) & set(planted))
    assert not through, f"a token whose body begins with a separator is let through to the indexer: {through}"
    assert allowed == [near, clean], f"the file with the ordinary identifier is kept from the indexer: {allowed}"


# --------------------------------------------------------------------------
# DEC-339 R-3: a public name check in gov.secrets
# --------------------------------------------------------------------------

TOKEN_NAMED = f"app/{support.PATH_TOKEN}.py"
UNDER_SECRET_FOLDER = f"web/{support.FOLDER_SECRET}/panel.ts"
ORDINARY_PATH = "app/beside.py"
# Clean in their content: only the path can hold a secret.
NAMED_FILES = {
    TOKEN_NAMED: "def token_named_helper(value):\n    return value + 1\n",
    UNDER_SECRET_FOLDER: "export function canaryFolderLabel(name: string): string {\n  return name.trim();\n}\n",
    ORDINARY_PATH: "def beside_helper(value):\n    return value + 1\n",
}
SHELTER = ("\n[[allowlists]]\ndescription = \"sheltered by the project\"\n"
           "paths = ['''.*''']\n\n[[allowlists]]\ndescription = \"sheltered by the project\"\nregexes = ['''.*''']\n")


def _verdicts(repo, sandbox):
    """``path_holds_secret(root, path)`` for the three paths, in one child process."""
    run = support.run_calls("gov.secrets", repo.root, [(support.NAME_CHECK, [rel]) for rel in NAMED_FILES], sandbox)
    if run.results is None:   # said without the run itself: its calls hold the planted names
        pytest.fail(f"gov.secrets.{support.NAME_CHECK}(root, path) did not answer (exit code {run.returncode}):\n"
                    f"{run.stderr[-800:]}", pytrace=False)
    verdicts = dict(zip(EXPECTED, run.results))
    assert all(verdict is True or verdict is False for verdict in verdicts.values()), \
        f"{support.NAME_CHECK}(root, path) returns no truth value: {verdicts}"
    return verdicts


EXPECTED = {"token-named file": True, "folder named like a canary": True, "ordinary path": False}


@pytest.mark.local_only
def test_a_path_name_that_holds_a_secret_is_told_from_an_ordinary_one(gitleaks, sandbox, tmp_path):
    """True for a token-shaped file name and for a folder named like a canary; false for an ordinary path."""
    repo = _repository(tmp_path / "project", NAMED_FILES)
    assert _verdicts(repo, sandbox) == EXPECTED


@pytest.mark.local_only
def test_an_allowlist_of_the_project_does_not_shelter_a_path_name(gitleaks, sandbox, tmp_path):
    """DEC-298: the project's file allowlists every path and every match, and the names are secrets all the same."""
    sheltering = tmp_path / "sheltering.toml"
    sheltering.write_text(support.config_path("template").read_text(encoding="utf-8") + SHELTER, encoding="utf-8")
    written = support.plant_tree(tmp_path / "tree", {"notes/token.md": support.in_prose(support.PATH_TOKEN),
                                                     "notes/folder.md": support.in_prose(support.FOLDER_SECRET)})
    assert support.scan(written, sheltering, sandbox) == [], \
        "the premise does not hold: gitleaks reports the planted values in spite of the project's allowlist"
    repo = _repository(tmp_path / "project", NAMED_FILES)
    (repo.root / support.ROOT_CONFIG_REL).write_bytes(sheltering.read_bytes())
    assert _verdicts(repo, sandbox) == EXPECTED


def _private_names_of_gov_secrets(source):
    """The private names of ``gov.secrets`` a module's source imports or reaches through an imported ``gov.secrets``."""
    tree, found, modules = ast.parse(source), [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            name = node.module or ""
            absolute = node.level == 0 and (name == "gov.secrets" or name.startswith("gov.secrets."))
            relative = node.level > 0 and (name == "secrets" or name.startswith("secrets."))
            if absolute or relative:
                found += [part for part in name.split(".") if part.startswith("_")]
                found += [alias.name for alias in node.names if alias.name.startswith("_")]
            elif name == "gov" or (node.level > 0 and not name):
                modules |= {alias.asname or alias.name for alias in node.names if alias.name == "secrets"}
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "gov.secrets" or alias.name.startswith("gov.secrets."):
                    found += [part for part in alias.name.split(".") if part.startswith("_")]
                    modules.add(alias.asname or "gov.secrets")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr.startswith("_") and not node.attr.endswith("__"):
            try:
                owner = ast.unparse(node.value)
            except Exception:   # noqa: BLE001 - an expression that cannot be written back is no module name
                continue
            if owner in modules:
                found.append(node.attr)
    return sorted(set(found))


def test_the_wrapper_imports_no_private_name_of_gov_secrets(module):
    """The wrapper uses the public interface of ``gov.secrets`` only: what its source imports, not how it works."""
    assert _private_names_of_gov_secrets("from gov.secrets import indexable, _hidden\n") == ["_hidden"]
    assert _private_names_of_gov_secrets("import gov.secrets as rules\nrules._hidden('x')\n") == ["_hidden"]
    assert _private_names_of_gov_secrets("from gov.secrets import indexable\nimport os\nos._exit\n") == []
    private = {}
    for path in sorted(module.rglob("*.py")):
        names = _private_names_of_gov_secrets(path.read_text(encoding="utf-8"))
        if names:
            private[path.relative_to(support.REPO_ROOT).as_posix()] = names
    assert not private, f"the wrapper imports private names of gov.secrets: {private}"
