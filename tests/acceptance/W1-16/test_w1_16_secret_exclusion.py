"""KPI success 2 and failure 3: no planted secret enters the codebase-memory index [CAP-03.e, CAP-12.b].

A repository in a temporary directory holds clean source files and source
files with a planted secret, in Rust, Python and TypeScript. The secret stands
where the tool would store it (an identifier) and where it reads it (a string,
a comment). After indexing through the wrapper, no planted string stands in any
file under ``.gov-runtime/`` (bytes and SQLite rows: the graph, the full-text
index, the per-file surfaces, any staged copy), none comes back in an answer,
and the files that hold one are not in the graph at all, because the indexer
reads only what ``gov.secrets.indexable`` returns. The clean files are there.
"""

from __future__ import annotations

import json
import subprocess

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

SECRET_FILES = {
    "app/settings.py": (
        '"""Settings."""\n\n'
        f'API_KEY = "{support.STRING_SECRET}"\n\n'
        f"# rotated value: {support.COMMENT_SECRET}\n"
        f"def {support.NAME_SECRET}(value):\n"
        "    return settings_helper(value)\n\n\n"
        "def settings_helper(value):\n"
        "    return value + 1\n"
    ),
    "web/config.ts": (
        f'export const API_TOKEN = "{support.TS_SECRET}";\n\n'
        "export function getToken(): string {\n"
        "  return API_TOKEN;\n"
        "}\n"
    ),
    "core/src/keys.rs": (
        f'pub const KEY: &str = "{support.RUST_SECRET}";\n\n'
        "pub fn key_reader() -> &'static str {\n"
        "    KEY\n"
        "}\n"
    ),
}
CLEAN_FILES = {
    "app/clean.py": "def clean_helper(value):\n    return value + 1\n\n\n"
                    "def clean_entry(value):\n    return clean_helper(value)\n",
    "web/clean.ts": "export function cleanLabel(name: string): string {\n  return name.trim();\n}\n\n"
                    "export function cleanTitle(name: string): string {\n  return cleanLabel(name);\n}\n",
    "core/src/clean.rs": "pub fn clean_sum(a: i64, b: i64) -> i64 {\n    a + b\n}\n\n"
                         "pub fn clean_total(a: i64) -> i64 {\n    clean_sum(a, a)\n}\n",
    "README.md": "# Planted\n\nA repository with clean files and files that hold a fake secret.\n",
}
# Names defined only in a file that holds a secret, and names defined only in a clean file.
ONLY_IN_SECRET_FILES = ("settings_helper", "getToken", "key_reader", "API_KEY", "API_TOKEN", "KEY",
                        support.NAME_SECRET)
IN_CLEAN_FILES = {"clean_helper": "app/clean.py", "cleanLabel": "web/clean.ts", "clean_sum": "core/src/clean.rs"}


def _plant(base, extra=None, namespaces=None):
    repo = support.Repo(base, namespaces=namespaces)
    for rel, text in {**SECRET_FILES, **CLEAN_FILES, **(extra or {})}.items():
        repo.write(rel, text)
    return repo.commit("first")


@pytest.fixture(scope="module")
def shared_sandbox(module_sandbox):
    return module_sandbox


@pytest.fixture(scope="module")
def planted(module, cbm, shared_sandbox, tmp_path_factory):
    """The planted repository, indexed once through the wrapper; the tests that use it only ask."""
    repo = _plant(tmp_path_factory.mktemp("w1-16-planted") / "planted")
    support.codeintel(repo.root, [("index", [])], shared_sandbox)
    return repo


# Every kind of question about every name of the planted files, and what is asked of the clean files.
LEAK_CALLS = [(kind, [name]) for name in ONLY_IN_SECRET_FILES
              for kind in ("definitions", "references", "callers", "impact")] + [("dead_code", [])]
CLEAN_CALLS = [("definitions", [name]) for name in IN_CLEAN_FILES] + [("callers", ["clean_helper"])]


@pytest.fixture(scope="module")
def answers(planted, shared_sandbox):
    """The questions of the three cases that only read the planted repository, asked in one child process: the
    code tool's start is paid once for them (DEC-561). ``(the run, call -> result)``; the run's output is the
    whole output of every question asked."""
    run = support.codeintel(planted.root, LEAK_CALLS + CLEAN_CALLS, shared_sandbox)
    assert len(run.results) == len(run.calls), f"not one result for each call\n{run.describe()}"
    return run, dict(zip(run.calls, run.results))


def test_the_tool_alone_would_index_a_planted_secret(cbm, sandbox, tmp_path):
    """Why the wrapper is needed. Passes before W1-16: it runs the tool, not the wrapper, on a planted folder."""
    tree = support.plant_tree(tmp_path / "tree", {**SECRET_FILES, **CLEAN_FILES})
    home = sandbox.tmpdir / "raw-home"
    env = support.child_env(sandbox) | {"CBM_CACHE_DIR": str(home)}
    done = subprocess.run([support.TOOL, "cli", "--json", "index_repository", "--repo-path", str(tree)],
                          cwd=str(sandbox.elsewhere), env=env, capture_output=True, text=True,
                          timeout=support.TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, done.stdout + done.stderr
    assert support.files_holding(home, [support.NAME_SECRET]), \
        "the tool no longer stores an identifier of a planted file: the planted strings prove nothing"


def test_the_filter_drops_exactly_the_planted_files(planted, sandbox):
    """The premise: the pre-index filter keeps the clean files and drops the three that hold a secret."""
    allowed = support.indexable(planted.root, sorted({**SECRET_FILES, **CLEAN_FILES}), sandbox)
    assert sorted(allowed) == sorted(CLEAN_FILES), f"the filter lets through: {allowed}"


def test_no_planted_secret_is_in_any_file_under_gov_runtime(planted, sandbox):
    home = support.one(planted.root, "home", [], sandbox)
    assert support.index_files(home), f"nothing was indexed: {home} holds no index file"
    found = support.files_holding(planted.root / support.RUNTIME_REL, support.PLANTED)
    assert not found, f"planted secrets stand under .gov-runtime/: { {rel: len(hits) for rel, hits in found.items()} }"


def test_no_planted_secret_is_left_outside_the_repository(planted, shared_sandbox):
    """HOME, TMPDIR, the runtime directory and the working directory of the run that indexed the repository."""
    for place in shared_sandbox.places:
        found = support.files_holding(place, support.PLANTED)
        assert not found, f"planted secrets were left in {place}: {sorted(found)}"


def test_no_planted_secret_comes_back_from_the_code_graph(answers):
    """Failure 3: every kind of question, about every name of the planted files."""
    run, asked = answers
    assert all((kind, tuple(args)) in asked for kind, args in LEAK_CALLS), run.describe()
    text = json.dumps(run.results) + run.output   # every result and the whole output of the run that asked
    leaked = [number for number, secret in enumerate(support.PLANTED) if secret in text]
    assert not leaked, f"{len(leaked)} planted secret(s) came back from the code graph"


def test_a_file_with_a_secret_is_not_in_the_code_graph(answers):
    """The indexer does not read the file: nothing defined in it is known, whatever the tool would have stored."""
    run, asked = answers
    names = [name for name in ONLY_IN_SECRET_FILES]
    known = {name: asked[("definitions", (name,))] for name in names if asked[("definitions", (name,))]}
    assert not known, f"names of files that hold a secret are in the graph: {sorted(known)}"
    dead = support.entries(asked[("dead_code", ())], "dead_code()")
    assert not [pair for pair in dead if pair[0] in SECRET_FILES], "a file that holds a secret is in the dead code answer"


def test_the_clean_files_are_in_the_code_graph(planted, answers):
    """Leaving everything out does not pass: the clean neighbours are indexed and answered, in all three languages."""
    run, asked = answers
    for name in IN_CLEAN_FILES:
        found = support.entries(asked[("definitions", (name,))], f"definitions({name})", planted.root)
        assert (IN_CLEAN_FILES[name], name) in found, f"{name} is not answered\n{run.describe()}"
    callers = support.entries(asked[("callers", ("clean_helper",))], "callers(clean_helper)", planted.root)
    assert ("app/clean.py", "clean_entry") in callers, run.describe()


def test_the_secrets_indexing_check_of_w1_15_is_green_on_the_index(planted, sandbox):
    """The backstop (W1-15): no store under ``.gov-runtime/`` holds a secret by the project's rules."""
    run = support.run_calls("gov.secrets", planted.root, [("stores_with_secrets", [])], sandbox)
    assert run.results is not None, run.describe()
    assert run.results[0] == [], f"stores with a secret: {run.results[0]}"


def test_a_file_the_path_map_classes_as_product_data_is_not_in_the_code_graph(module, cbm, sandbox, tmp_path):
    """The indexer reads what the filter returns: a clean file of a product namespace stays out as well (W1-15)."""
    namespaces = {"top": (["*"], "governance"), "overlay": (["governance/**"], "governance"),
                  "code": (["app/**", "web/**", "core/**"], "governance"),
                  "tenant-exports": (["tenant-exports/**"], "product")}
    extra = {"tenant-exports/report.py": "def tenant_only_report(rows):\n    return len(rows)\n"}
    repo = _plant(tmp_path / "mapped", extra, namespaces)
    run = support.codeintel(repo.root, [("index", []), ("definitions", ["tenant_only_report"]),
                                        ("definitions", ["clean_helper"])], sandbox)
    assert run.results[1] == [], f"a product-data file is in the code graph\n{run.describe()}"
    assert ("app/clean.py", "clean_helper") in support.entries(run.results[2], "definitions(clean_helper)", repo.root)


def test_a_secret_added_after_the_first_index_leaves_the_graph(module, cbm, sandbox, tmp_path):
    """A clean file is indexed, then gains a secret: after the next index nothing of it is known or stored."""
    planted = _plant(tmp_path / "later")
    planted.write("app/later.py", "def later_helper(value):\n    return value - 1\n")
    planted.commit("later")
    first = support.codeintel(planted.root, [("index", []), ("definitions", ["later_helper"])], sandbox)
    assert ("app/later.py", "later_helper") in support.entries(first.results[1], "definitions(later_helper)"), \
        first.describe()
    planted.write("app/later.py", f'TOKEN = "{support.STRING_SECRET}"\n\n\n'
                                  "def later_helper(value):\n    return value - 1\n")
    planted.commit("leak")
    second = support.codeintel(planted.root, [("index", []), ("definitions", ["later_helper"])], sandbox)
    assert second.results[1] == [], f"the file is still in the graph after it gained a secret\n{second.describe()}"
    found = support.files_holding(planted.root / support.RUNTIME_REL, support.PLANTED)
    assert not found, f"planted secrets stand under .gov-runtime/: {sorted(found)}"


@pytest.mark.parametrize("tier", list(support.DEV_PLANTED))
def test_no_dev_canary_reaches_the_code_index(tier_runs, tier):
    """The dev tiers as they are: none of the seven dev canaries stands in the tier's code index (CAP-03.e)."""
    run = tier_runs(tier)
    canaries = support.DEV_PLANTED[tier]
    assert support.files_holding(run.repo.root, canaries, skip=(".git", support.RUNTIME_REL)), \
        f"the {tier} tier holds none of its planted values"
    found = support.files_holding(run.repo.root / support.RUNTIME_REL, canaries)
    assert not found, f"dev canaries stand in the code index of {tier}: {sorted(found)}"
    text = json.dumps([list(answers.values()) for answers in run.answers.values()])
    assert not [canary for canary in canaries if canary in text], f"a dev canary came back in an answer on {tier}"
