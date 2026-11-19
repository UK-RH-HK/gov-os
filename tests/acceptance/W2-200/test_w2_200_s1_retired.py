"""S1: the context command, its library and its check are gone; the four helpers count with ``gov.util.tokens``.

Through the command line on a fixture repository, the filesystem of the code under test (found as the child process
imports it), an import in a child process, and ``gov check --json`` on a project holding this tree's kernel check
declarations.
"""

from __future__ import annotations

import ast
import json
import re

import pytest

import w2_200_support as s

ARGVS = {"a ticket": ["context", "PROJ-0001"], "--in-force": ["context", "--in-force"]}


def _plain_repo(tmp_path, env):
    root = tmp_path / "plain"
    root.mkdir()
    s.git("init", "-q", "-b", "main", cwd=root, env=env)
    s.write(root / s.PATH_MAP_REL, s.path_map())
    s.write(root / s.REGISTER_REL, s.register(s.entry(110, "The plain decision")))
    s.git("add", "-A", cwd=root, env=env)
    s.git("commit", "-q", "--no-gpg-sign", "-m", "plain", cwd=root, env=env)
    return root


@pytest.mark.parametrize("argv", list(ARGVS.values()), ids=list(ARGVS))
def test_s1_the_context_command_is_an_invalid_choice(tmp_path, env, argv):
    root = _plain_repo(tmp_path, env)
    run = s.gov([*argv, "--root", root], env=env, cwd=root)
    assert run.code == 2, f"gov {' '.join(argv)} did not exit 2\n{run.describe()}"
    assert "invalid choice" in run.err and "'context'" in run.err, \
        f"the parser's refusal does not name 'context' as an invalid choice\n{run.describe()}"


def test_s1_gov_help_lists_no_context_command(tmp_path, env):
    run = s.gov(["--help"], env=env, cwd=tmp_path)
    assert run.code == 0, run.describe()
    assert re.search(r"(?m)^ {4}check\b", run.out), f"the fixture cannot read the command list\n{run.describe()}"
    listed = [line for line in run.out.splitlines() if re.match(r" {4}context(\s|$)", line)]
    assert not listed, f"gov --help lists the context command: {listed}"


def test_s1_the_library_folder_is_gone_and_its_import_fails(tmp_path, env):
    package = s.package_dir(env, tmp_path)
    assert not (package / "context").exists(), \
        f"{package / 'context'} still exists (a folder left with only __pycache__ in it also keeps a namespace import alive)"
    done = s.python("import gov.context", env=env, cwd=tmp_path)
    assert done.returncode != 0 and "ModuleNotFoundError" in done.stderr, \
        f"import gov.context did not raise ModuleNotFoundError: exit {done.returncode}\n{done.stderr[-1500:]}"


def test_s1_the_kernel_holds_no_context_reproducibility_check():
    assert not (s.KERNEL_CHECKS / "context-reproducibility.yaml").exists(), \
        "template/governance/kernel/checks/context-reproducibility.yaml still exists"


def test_s1_gov_check_names_no_context_reproducibility_family(tmp_path, env):
    root = s.kernel_checks_project(tmp_path, env)
    run = s.gov(["check", "--json", "--root", root], env=env, cwd=root)
    data = run.envelope()
    text = json.dumps(data)
    assert "families" in text, f"gov check gave no family names to read\n{run.describe()}"
    named = sorted(set(re.findall(r"context[-_ ]reproducibility", text, flags=re.IGNORECASE)))
    assert not named, f"gov check --json names the family or check {named}\n{run.describe()}"


_COUNTER = r'''
import json, sys

class _Blocked:
    def find_spec(self, name, path=None, target=None):
        if name == "gov.context" or name.startswith("gov.context."):
            raise ModuleNotFoundError(f"No module named {name!r} (blocked by the W2-200 test)")
        return None

sys.meta_path.insert(0, _Blocked())
from gov.util.tokens import TOKEN_CHARS, _tokens
counts = [_tokens(text) for text in ("", "a", "abcd", "abcde", "x" * 4001)]
import gov.telemetry.counter, gov.telemetry.sessionlog, gov.check.skill_validator, gov.retrieval.supplementary
print(json.dumps({"chars": TOKEN_CHARS, "counts": counts}))
'''


def test_s1_the_token_counter_lives_in_gov_util_tokens_and_the_helpers_import_without_gov_context(tmp_path, env):
    """The four helpers import with ``gov.context`` unimportable, and ``gov.util.tokens`` counts four characters a
    token, rounded up, as the retired library did."""
    done = s.python(_COUNTER, env=env, cwd=tmp_path)
    assert done.returncode == 0, f"the counter or a helper cannot be imported without gov.context:\n{done.stderr[-2500:]}"
    assert json.loads(done.stdout.strip().splitlines()[-1]) == {"chars": 4, "counts": [0, 1, 1, 2, 1001]}


def _imports_gov_context(tree: ast.AST) -> list:
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(node.lineno, alias.name) for alias in node.names
                      if alias.name == "gov.context" or alias.name.startswith("gov.context.")]
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "gov.context" or node.module.startswith("gov.context."):
                found.append((node.lineno, node.module))
            elif node.module == "gov" and any(alias.name == "context" for alias in node.names):
                found.append((node.lineno, "gov.context"))
    return found


def test_s1_no_module_of_the_code_imports_gov_context(tmp_path, env):
    """Every Python file of the ``gov`` package under test (but the kernel copies in ``_shipped``, the ticket's
    non-goal), at module level or inside a function: no import of ``gov.context``."""
    package = s.package_dir(env, tmp_path)
    found = []
    for path in s.source_files(package, skip=("__pycache__", "_shipped")):
        if path.suffix != ".py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        found += [f"{path.relative_to(package.parent)}:{line} imports {name}" for line, name in _imports_gov_context(tree)]
    assert not found, "modules still import gov.context:\n" + "\n".join(found)
