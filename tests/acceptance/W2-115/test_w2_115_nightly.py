"""S8: the nightly rebuilds its worktree's stores with the full secrets scan (``GOV_SECRETS_FULL_SCAN=1``) before its
run, whatever the caller's environment, and its record says so.

The nightly is ``python3 -m gov.close.nightly main --root <project> --json`` (W2-66's command); its record is the
file its answer names under ``docs/close/nightly/``.

Red on today's code: today's nightly record has no ``secrets_full_scan`` and today's nightly rebuilds no store.
"""

import json
import os
import time

import w2_115_support as support


def test_the_nightly_rebuilds_the_stores_with_the_full_secrets_scan_before_its_run(make_project, sandbox):
    """S8: with ``GOV_SECRETS_FULL_SCAN`` unset in the caller's environment, the nightly's record says
    ``secrets_full_scan: true``, and a store under ``.gov-runtime/`` was written after the nightly began and before
    the first planted test ran."""
    project = make_project(nightly=None)
    env = support.quiet_env(sandbox)
    assert "GOV_SECRETS_FULL_SCAN" not in env
    started = time.time()
    run = support.run_module(project, sandbox, support.NIGHTLY_MODULE, "main", env=env)
    envelope = support.envelope(run)
    body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    rel = (body or {}).get("record")
    assert isinstance(rel, str) and rel.startswith(support.NIGHTLY_DIR_REL + "/"), \
        f"the nightly names no record under {support.NIGHTLY_DIR_REL}/\n{run.describe()}"
    record = json.loads((project.root / rel).read_text(encoding="utf-8"))
    assert record.get("secrets_full_scan") is True, f"the nightly's record does not say the full scan ran: {record}"
    times = [r["time"] for case in os.listdir(project.told) for r in project.told_runs(case)]
    assert times, f"the nightly ran no planted test\n{run.describe()}"
    first_test = min(times)
    store = project.root / ".gov-runtime"
    rebuilt = [p for p in store.rglob("*") if p.is_file()
               and not {"close", "nightly"} & set(p.relative_to(store).parts)
               and started <= p.stat().st_mtime <= first_test]
    assert rebuilt, "no store under .gov-runtime/ was rebuilt between the nightly's start and its first test"
