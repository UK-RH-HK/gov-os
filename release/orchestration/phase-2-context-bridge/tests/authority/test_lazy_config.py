"""BR-DAG-AMEND-R1-12 regression test.

``govbridge.authority.classes.BRIDGE_STATE_PATH`` used to be a plain top-level statement
(``BRIDGE_STATE_PATH = _load_bridge_state_path()``), read against ``GOV_BRIDGE_DOMAIN`` AT IMPORT TIME. Merely
importing ``govbridge.authority`` (even transitively, for a caller like ``govbridge.code.lineage_layer``/
``govbridge.graph.derive`` that needs it only for id-grammar resolution and never touches
``BRIDGE_STATE_PATH`` itself) read ``config/state-aliases.yaml`` at that moment -- a process-global side effect of
the FIRST importer's environment, fixed for the rest of the process. ``tests/code/conftest.py`` used to force the
real domain's value to win that race with a collection-time pre-import; this module proves that workaround is no
longer needed by demonstrating, in fresh SUBPROCESSES (never sharing state with this test process or with each
other), that:

1. merely importing ``govbridge.authority`` never touches the filesystem, even with ``GOV_BRIDGE_DOMAIN`` pointed
   at a domain with no ``config/state-aliases.yaml`` at all (the exact pre-fix crash scenario);
2. ``BRIDGE_STATE_PATH`` is still a plain string once something actually asks for it (``from
   govbridge.authority.classes import BRIDGE_STATE_PATH`` still works, byte-for-byte, for every existing consumer);
3. asking for it against a domain that genuinely lacks the config file still raises, clearly, at the point of
   actual use -- never silently, and never at an unrelated import.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOMAIN = Path(__file__).resolve().parents[2]


def _run(script: str, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, timeout=30)


def _base_env(domain: Path) -> dict:
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(DOMAIN) + os.pathsep + env.get("PYTHONPATH", "")
    env["GOV_BRIDGE_DOMAIN"] = str(domain)
    return env


def test_importing_authority_never_touches_the_filesystem(tmp_path):
    """The exact pre-fix crash scenario, reproduced directly: a domain with NO config/ directory at all, imported
    fresh. Before R1-XC, ``import govbridge.authority`` alone raised (FileNotFoundError, from the top-level
    ``_load_bridge_state_path()`` statement); after it, the bare import succeeds regardless."""
    empty_domain = tmp_path / "empty-domain"
    empty_domain.mkdir()
    env = _base_env(empty_domain)

    r = _run("import govbridge.authority\nprint('IMPORT_OK')", env=env)
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "IMPORT_OK" in r.stdout


def test_importing_a_transitive_consumer_never_touches_the_filesystem_either(tmp_path):
    """Mirrors the real regression path named in BR-DAG-AMEND-R1-12's own reason: a package that needs
    govbridge.authority for something OTHER than BRIDGE_STATE_PATH (id-grammar resolution -- here simulated by
    importing govbridge.authority.records, the module that actually implements it) must not crash on a domain
    lacking config/state-aliases.yaml either."""
    empty_domain = tmp_path / "empty-domain"
    empty_domain.mkdir()
    env = _base_env(empty_domain)

    r = _run("import govbridge.authority.records\nprint('IMPORT_OK')", env=env)
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "IMPORT_OK" in r.stdout


def test_bridge_state_path_is_still_a_plain_string_once_actually_used(tmp_path):
    """Every existing consumer (``govbridge.authority.lifecycle``, and a dozen test fixture builders) does
    ``from govbridge.authority.classes import BRIDGE_STATE_PATH`` and then treats it as a bare string (``root /
    BRIDGE_STATE_PATH``). The lazy module ``__getattr__`` must keep that contract exactly: a caller that actually
    asks for the value still gets a plain string, computed correctly from THIS domain's own config/state-aliases.yaml."""
    domain = tmp_path / "domain-with-config"
    (domain / "config").mkdir(parents=True)
    (domain / "config" / "state-aliases.yaml").write_text(
        "aliases:\n  bridge: some/custom/STATE.yaml\n", encoding="utf-8"
    )
    env = _base_env(domain)

    r = _run(
        "from govbridge.authority.classes import BRIDGE_STATE_PATH\n"
        "print(type(BRIDGE_STATE_PATH).__name__)\n"
        "print(BRIDGE_STATE_PATH)",
        env=env,
    )
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    lines = r.stdout.strip().splitlines()
    assert lines[0] == "str"
    assert lines[1] == "some/custom/STATE.yaml"


def test_asking_for_it_against_a_domain_without_the_config_file_raises_at_use_not_at_import(tmp_path):
    """A domain that genuinely never carries config/state-aliases.yaml (never a REPAIR-1 test fixture's own
    situation -- every real fixture ships one) still raises when something actually asks for BRIDGE_STATE_PATH,
    clearly, at the point of use -- never silently, and (per the two tests above) never merely from importing the
    package."""
    empty_domain = tmp_path / "empty-domain"
    empty_domain.mkdir()
    env = _base_env(empty_domain)

    r = _run(
        "import govbridge.authority\n"
        "print('IMPORTED')\n"
        "from govbridge.authority.classes import BRIDGE_STATE_PATH\n"
        "print('SHOULD NOT REACH HERE: ' + BRIDGE_STATE_PATH)",
        env=env,
    )
    assert r.returncode != 0
    assert "IMPORTED" in r.stdout
    assert "SHOULD NOT REACH HERE" not in r.stdout
    assert "FileNotFoundError" in r.stderr


def test_unknown_attribute_still_raises_attribute_error():
    from govbridge.authority import classes

    import pytest
    with pytest.raises(AttributeError):
        classes.NOT_A_REAL_ATTRIBUTE
