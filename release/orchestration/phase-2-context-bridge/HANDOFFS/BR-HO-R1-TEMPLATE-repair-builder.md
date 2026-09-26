# BR-HO-R1-TEMPLATE: the common part of every REPAIR-1 builder brief

A REPAIR-1 brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; it still binds you) **plus this file plus
your node section**. Your node section is the node in `ARCHITECTURE/REPAIR-1/REPAIR_DAG.yaml` whose id your
dispatch message names. Where the three differ, your node section governs scope and deliverables, and this file
governs the REPAIR-1 rules.

## Why REPAIR-1 exists (public summary; no oracle content)

The Review-8 demonstration run-1 **failed**. The bridge preserved authority exactly but did not deliver **complete
relevance**. A fresh failure analyst measured the causes (`ARCHITECTURE/REPAIR-1/CAUSE_ANALYSIS.md`) and wrote a
generic repair plan and DAG (`REPAIR_PLAN.md`, `REPAIR_DAG.yaml`). Read `REPAIR_PLAN.md` §0–§1, the sections your
node cites, and §9 on genericity.

## REPAIR-1 rules. These bind every repair builder.

1. **Never read `bridge/grade-*`,** in any form (`git show`, `git log -p`, checkout). Never read any directory named
   `govbridge-sealed-*`, anything under `~/.config/gov-bridge/sealed/`, `DEMONSTRATION/oracle*` or
   `DEMONSTRATION/grading/**`. Those hold held-out grading material. Reading them invalidates the next demonstration,
   and every transcript is audited.
2. **Do not use the public demonstration query texts or the run-1 answers as acceptance input.** That covers
   `ARCHITECTURE/demonstration-queries.yaml` and `DEMONSTRATION/run-1/answers.yaml`. For real-view acceptance use
   **CONTROL-A**: `tests/fixtures/controls/control-a/`, with its baseline in `baseline/`. Use synthetic fixtures for
   everything else. The run-1 *packet* and *metrics* in `CAUSE_ANALYSIS.md` are fine to read.
3. **Generic only (OC-BR-02).** No code, config, facet, scope or test may name a Review-8 item, an F-finding, a
   Phase-2 file or a symbol from the Review-8 chains. Fixture *data* is exempt. R1-INT audits this.
4. **The hard authority invariant is unchanged.**
   * Section A is resolver-only, and lifecycle never removes a mandatory input (BR-ARCH-RULING-1).
   * Nothing retrieved enters A or D.1.
   * The six named invariant tests, the import-boundary test and the class-table test must pass **unmodified**.
5. **Existing tests.** You may add tests freely. Modify an existing test file only to extend or correct it, and list
   and justify every modification in your checkpoint's `decisions`. Never weaken an assertion.
6. **Stores.**
   * Use your own store, `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-<RUN_ID>`.
   * `store-BR-AR-0010` (the run-1 demonstration store) is **read-only**: no `index update` or `rebuild` against it.
     Copy it if you need a mutable real-view store: `cp -a` into your own store path.
   * The venv is read-only. Never pip-install. If a wheel is missing, report BLOCKED.
7. **Shared files are sequenced, never edited at the same time** (`REPAIR_PLAN.md` §12). If your node edits
   `govbridge/cli.py` or `govbridge/compile/packet.py`, your base already contains the previous editor's merged work.
   Keep your edits minimal and localised.
8. **The discipline you already know.** Never `rm`. Never pipe without `set -o pipefail`. Every wait is bounded and
   has a timeout action. Never wait on the orchestrator.

## Return: the SCHEMA-2 worker completion checkpoint (OD-BR-04 A), enforced by `integrate-check`

Commit on your branch.

**`AGENT_RUNS/<RUN_ID>.report.yaml`**, with these keys:

- `run_id`
- `role`
- `model_observed`
- `branch`
- `commit`
- `status`: `COMPLETED` or `BLOCKED`
- `claims`
- `evidence`
- `mutation_scope_respected`: `true`
- `open_issues`

**`AGENT_RUNS/<RUN_ID>.checkpoint.yaml`**, with these keys:

- `run_id`
- `commit`
- `commands`: a list of {cmd, exit_code, output_path, output_sha256}. There is **one entry per acceptance check**.
  Save each output inside your scope and hash it with sha256.
- `role`
- `model_observed`
- `input_manifest`: a list of {path, sha256} covering your brief, your node section's DAG file, and every input you
  relied on
- `task_contract`: {handoff_path, handoff_sha256, mutation_scope}
- `artifacts_changed`: **every** changed path. `integrate-check` compares this list with `git diff`.
- `findings`
- `failed_approaches`
- `unresolved`
- `decisions`: those made within your authority, those you request, and every modified existing test with its
  justification
- `lessons`
- `next_consumer`: the DAG node or nodes that depend on yours
- `final_commit`

Self-check with `python3 release/orchestration/phase-2-context-bridge/tools/check_state.py integrate-check <RUN_ID>`
before you return. End with your commit SHA and `<RUN_ID> RETURNED <COMPLETED|BLOCKED>`.

## Amendment R1-T1 (BR-DAG-AMEND-R1-4): the full suite is part of every node's acceptance

This amendment applies to runs dispatched after wave 1, and to reopened passes. A wave-1 node's targeted acceptance
passed while its own new test failed in the full suite, because the test depended on test order.

1. **Run the FULL domain suite.** From the domain, run
   `$HOME/.cache/gov-bridge/venv/bin/python -m pytest -q -p no:cacheprovider tests` as your **last** acceptance check.
   Save the output as a check output and add it to `commands`. It must show **0 failures**. The one exception is
   `tests/compile/test_compile_real_view_mandatory_in_a.py`, which is non-hermetic until R1-RM repairs it
   (BR-DAG-AMEND-R1-2). If that test fails, list the failure explicitly in `open_issues`. Do not skip it or mark it
   xfail.
2. **Tests must be hermetic.** A new test must not depend on:
   * the process cwd (pass `--repo` or `repo=` explicitly; do not `chdir`);
   * live refs of the shared repository (pin a view or use a fixture repo);
   * `GOVBRIDGE_*` environment left over from another test (use `monkeypatch.setenv`/`delenv`);
   * test order.
   Run each new test file on its own **and** within the full suite.
