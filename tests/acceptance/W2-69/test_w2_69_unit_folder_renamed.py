"""W2-69 (K7): tests/unit/secrets/ is renamed tests/unit/secrets_check/, so it no longer shadows the standard library.

Success: "tests/unit/secrets/ is renamed tests/unit/secrets_check/, so it no
longer shadows the standard library's secrets module under plugins that import it
first; collection is clean with pytest-rerunfailures and pytest-randomly loaded
[W2-L373, I2 F8, DEC-899]."

pytest-rerunfailures and pytest-randomly are not installed on this machine, and
nothing may be installed. What they need is tested instead: with a plugin of this
suite (``w2_69_stdlib_secrets_first``), loaded first with ``-p``, that imports the
standard library's ``secrets`` as they do, collecting the unit tests gives no error,
in one process and under two xdist workers; ``tests/unit/secrets/`` is gone; and the
check's builder tests are under ``tests/unit/secrets_check/``.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest

import w2_69_support as support

UNIT = support.REPO_ROOT / "tests" / "unit"
OLD, NEW = UNIT / "secrets", UNIT / "secrets_check"
# The builder's test files of tests/unit/secrets/ on w2/integrate when this suite was written.
BUILDER_TESTS = ("test_scan_scale.py", "test_secrets.py", "test_token_rule.py")
PLUGIN = "w2_69_stdlib_secrets_first"


def test_the_unit_folder_named_secrets_is_gone():
    assert not OLD.exists(), (
        f"{OLD.relative_to(support.REPO_ROOT)} still exists: a test package named secrets shadows the standard "
        f"library's secrets wherever that is imported first")


def test_the_checks_builder_tests_are_under_secrets_check():
    assert NEW.is_dir(), f"{NEW.relative_to(support.REPO_ROOT)} does not exist"
    missing = [name for name in BUILDER_TESTS if not (NEW / name).is_file()]
    assert not missing, f"the check's builder tests {missing} are not under {NEW.relative_to(support.REPO_ROOT)}"


def _xdist():
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.parametrize("workers", ("one-process", "two-xdist-workers"))
def test_unit_collection_is_clean_with_a_plugin_that_imports_the_standard_librarys_secrets_first(workers, tmp_path):
    if workers == "two-xdist-workers" and not _xdist():
        pytest.skip("pytest-xdist is not installed")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([support.python_path(), str(support.HERE)])
    env["TMPDIR"] = str(tmp_path)
    argv = [sys.executable, "-m", "pytest", "-p", PLUGIN, "-q", "-p", "no:cacheprovider",
            str(UNIT.relative_to(support.REPO_ROOT))]
    if workers == "two-xdist-workers":   # each worker collects; no test is selected, so none runs
        argv += ["-n", "2", "-k", "w2_69_selects_no_test"]
        ok = (0, 5)
    else:
        argv += ["--collect-only"]
        ok = (0,)
    done = subprocess.run(argv, cwd=str(support.REPO_ROOT), env=env, capture_output=True, text=True, timeout=600)
    output = done.stdout + done.stderr
    assert done.returncode in ok, (
        f"collecting tests/unit with {PLUGIN} loaded first failed (exit code {done.returncode}):\n"
        + "\n".join(line for line in output.splitlines()
                    if re.search(r"ERROR collecting|not a package|Interrupted|errors? in|^E ", line))[-3000:])
    assert not re.search(r"ERROR collecting|\d+ errors? in|'secrets' is not a package", output), output[-3000:]
    if workers == "one-process":
        assert "w2-69 plugin: the standard library's secrets was imported first" in output, (
            f"the plugin {PLUGIN} did not load first\n{output[-2000:]}")
        assert "tests/unit/secrets_check/" in output, (
            f"no test of tests/unit/secrets_check/ was collected\n{output[-2000:]}")
