---
type: probe
task: DAEO-zmo4
status: final
reviewer_session: 34ed6273-7811-4289-bc53-e8a09160c9f1
implementer_session: afdd30bf-acf9-409f-8860-eb5c0069a7a3
test_designer_session: 55aaf31f-3ac4-420d-bfa4-409f1ade1a97
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a1515ab1aa35db2635319a67a3e2c8d90fdba4e4
reviewed_commit: 61b5f5684c95
decisions_applied: [DEC-1154, DEC-1189, DEC-1156, DEC-802, DEC-801, DEC-808, DEC-809, DEC-1010, DEC-820]
scope: "W2-174 narrow independent check (DEC-1154) of r2b and r2c since 61b5f5684c95: the ticket schemas shipped in the wheel, jsonschema declared, the wheel test, and the two schemas in W2-88's shipped lists (fabric.PACKAGED, THE_SHIPPED, ITEMS), at a1515ab1aa35"
---

# Probe record: W2-174 (DAEO-zmo4), the narrow check of r2b/r2c at a1515ab1aa35 (DEC-1154)

## Summary

- **What was checked.** The ticket's own commits since the narrow re-check at `61b5f5684c95`, judged at head
  `a1515ab1aa35`:
  - engineer `7e3df63f5`: the kernel's ticket and common schemas shipped under `src/gov/_shipped/` and listed in
    `pyproject.toml`'s package data, and `jsonschema>=4.10` declared;
  - engineer `997e82314`: `test_w2_174_wheel.py`;
  - engineer `9b36aa33c` (session `afdd30bf`): the two schemas added to `fabric.PACKAGED` and to `THE_SHIPPED`;
  - independent test designer `1b34043d2` (session `55aaf31f`, merged at `a1515ab1a`): the two schemas added to
    W2-88's acceptance `ITEMS`, with `Rewrite-Reason: DEC-1189 (1), DEC-1156 (7)`;
  - the CTO's `allowed_paths` widenings, `d4555338f` and `0b0ddc574`.

  This answers that record's F1 (a wheel install refused every apply), and the CTO's P-W2-174-R2B-1 (A).
- **Who checked.** A fresh, read-only independent auditor (`claude-opus-5-5`, effort high, class C2,
  `--owner-named DEC-1154`), session `34ed6273-7811-4289-bc53-e8a09160c9f1`, launched through `launch_worker.sh`. Its
  brief carried JUDGEMENT.md word for word. It wrote nothing in the worktree (`git status --short` was empty).
  - It hit two guard refusals and worked around neither: a heredoc carrying a venv install line, and a `mkdir` of an
    existing folder.
  - It checked the installed gov from the unpacked wheel, plus the engineer's installing test.
- **The lead's evidence at `a1515ab1aa35`:**
  - `test_w2_88_shipped.py`, W2-88's `test_w2_88_p1*.py` and `test_w2_174_wheel.py`: 51 passed, 0 skipped;
  - `gov accept W2-174`: 222 passed, 0 failed, all eleven lines, none unmapped;
  - lead_verify: GREEN, 7578 tests with 0 failed, 0 errors and 8 skipped (parallel), and 1 serial entry passed.
- **Verdict.** Pass, no findings.

## The auditor's return, word for word

**Pass.** Findings: none. No round is proposed (DEC-809).

**Sandbox check (step 0, launch_worker.sh):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zmo4` failed with `OSError: [Errno 30] Read-only file system`, and no file exists.
- (b) `git hash-object -w --stdin` returned `1ae28402a109…` (exit 0), and `git update-index --refresh` exited 0.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1).
- HEAD is `a1515ab1aa35db2635319a67a3e2c8d90fdba4e4`. `$TMPDIR` is `/tmp/gov-launch-aomr1ua9/claude-1000`.

**Two refusals, each hit once and not worked around:**
- The guard refused the heredoc that wrote my venv install script ("installs are refused here … DEC-953 item 2"). As the brief directs, I ran the engineer's wheel test, which does the venv install. For my own check I built the wheel, unpacked it with `python -m zipfile -e`, and ran gov from that copy. Nothing was installed.
- The guard refused a `mkdir` of `.gov-runtime/scratch/empty-home` ("auditor writes only its own record …"). The folder already existed, so I used it as it was.

## 1. Does `gov adopt --verify-apply` work from a wheel built at the head?
Yes.

**What the wheel holds.** I ran `git archive a1515ab1a -- pyproject.toml src`, then `pip wheel --no-deps --no-build-isolation --no-index`, with PYTHONPATH and PYTHONHOME unset. The result is `gov-0.1.0-py3-none-any.whl`.
- It contains `gov/_shipped/template/governance/kernel/schemas/{ticket,common}.schema.json`, each byte-identical to `template/governance/kernel/schemas/` (`cmp`).
- METADATA declares `Requires-Dist: PyYAML >=6` and `Requires-Dist: jsonschema >=4.10`.

**My probe.** I ran gov from the unpacked wheel with PYTHONPATH set to the unpacked folder only, the working directory under `$TMPDIR`, and the entry point `gov.cli.main:main`.
- Without that PYTHONPATH, `import gov` fails, so no other gov is on the path.
- `gov.__file__` is `…/aud/run/site/gov/__init__.py`, and no folder above it holds the schemas (`False`). The `_shipped` copy is therefore the only one the pass can read.
- The fixtures come from `test_w2_174_support.ticket`/`repo_with` and `test_w2_174_fields.bare`/`COORD_ANSWER`/`REVIEW_ANSWER`.

| Probe | Exit | Result | Tree |
|---|---|---|---|
| Label-only apply | 0 | `{"changed": ["DAEO-aa11"]}` | `'one line Verify: a case'` and `verify_pass: 2026-11-16 W-1` written |
| Launch fields (S6's six) | 0 | `{"changed": ["exa-dt1z","exa-qu2x"]}` | `exa-qu2x` has role, allowed_paths, kpis, reads, needs, `waits_on: [exa-dt1z]` and verify_pass; comments and key order kept |
| `state_class: MADE_UP` (fails only the schema) | 1 | `VERIFY_PASS_SCHEMA` "fails the ticket schema: state_class: 'MADE_UP' is not one of …" | unchanged (sha256 of the tree) |

The third row shows the shipped schema is really being enforced, not just loaded.

**The engineer's `test_w2_174_wheel.py` does prove it, and it cannot pass from the source tree:**
- It removes PYTHONPATH and PYTHONHOME from the environment and runs `venv/bin/gov` in a tmp working directory.
- The fixture asserts that `gov.__file__` starts with the venv path and that no folder above the installed `verify_pass` holds the schemas.
- It asserts the shipped folder holds exactly the two names, each byte-identical to the kernel's.
- Its removal case shows the `_shipped` copy is the only file read.
- The user-site `.pth` only starts coverage, and gov is not importable outside the venv.
- It ran: 57 passed in all, none skipped (see question 3).

## 2. Does the pass fail closed when the schema cannot be had?
Yes.

**Reading `_validator`** (`src/gov/adopt/verify_pass.py:329-353`):
- If `jsonschema` cannot be imported, it raises `VERIFY_PASS_SCHEMA`.
- It looks in gov's own source tree (the folders above gov's install location, never the adopted repository), then in `<gov>/_shipped/…/schemas`. A read, JSON or SchemaError failure moves it to the next place; when both fail it raises `VERIFY_PASS_SCHEMA`.
- `apply()` (`:389-394`) builds the validator and validates every ticket before the write loop at `:396`, so a refusal leaves nothing written.

**Probes from the unpacked wheel:**
- With `ticket.schema.json` moved out: exit 1, `VERIFY_PASS_SCHEMA` "the kernel's ticket schema cannot be read (looked in: …/no-source-tree/…; …/_shipped/…)", tree unchanged.
- With a `jsonschema` stand-in that raises ImportError placed first on the path: exit 1, `VERIFY_PASS_SCHEMA` "jsonschema is not installed …", tree unchanged.
- The engineer's removal case for the installed venv also passed.

## 3. Do W2-88's shipped-file checks hold at the head?
Yes, and no edit weakened them.

**The run** used the heavy slot with the brief's command and exclusions, on `test_w2_174_wheel.py`, `test_w2_88_shipped.py`, `test_w2_88_s29.py`, `test_w2_88_p1_shipped_bytes.py` and `test_w2_88_p1_installed.py`. Result: **57 passed** in 124.92 s, none skipped (`-rs` printed nothing), none deselected.

**The edits only add entries:**
- `9b36aa33c` adds the two file paths to `fabric.PACKAGED` and `THE_SHIPPED`. `PACKAGED == THE_SHIPPED` still holds.
- `1b34043d2` adds two items to `ITEMS`, one per file and not the `schemas/` folder.
- No assertion was changed.

**The "only the copies" check is still per file.** Because the items are file paths, `rel.startswith(item + "/")` never covers a sibling file. To confirm, I exported HEAD to `$TMPDIR` and planted a byte-exact copy of `close.schema.json`, a kernel schema the product does not read, under `_shipped/…/schemas/`. Two checks refused it:
- `test_w2_88_shipped.py::test_the_package_ships_nothing_but_the_shipped_set` failed.
- `test_w2_88_p1_shipped_bytes.py::test_s24_the_shipped_folder_holds_only_the_copies` failed with `['template/governance/kernel/schemas/close.schema.json']`.
- 20 passed and 4 deselected. The deselected cases are the wheel-building ones, whose own check that the folder holds exactly the two names would also catch the plant.

## Findings
None.

```verdict
{"kpis": [{"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}]}
```

## Return fields
- **task:** DAEO-zmo4 (W2-174), a narrow independent check of r2b/r2c at `a1515ab1a` against `61b5f5684c95` (DEC-1154).
- **status:** pass. Findings: none.
- **work_completed:**
  - Ran the sandbox check.
  - Read the ticket's commits: `7e3df63f5`, `997e82314`, `9b36aa33c`, `1b34043d2`, and the `allowed_paths` widenings `d4555338f` and `0b0ddc574`.
  - Built a release-form wheel at the head and inspected it.
  - Ran five apply probes from the unpacked wheel: label-only, launch fields, schema refusal, schema removed, jsonschema blocked.
  - Ran W2-88's checks and the wheel test.
  - Planted an extra shipped schema in a scratch export to test the "only the copies" exactness.
- **files_changed:** none.
- **evidence:**
  - The wheel lists both schemas, byte-identical; METADATA has `Requires-Dist: jsonschema >=4.10`.
  - Probe exits 0/0/1/1/1 with the envelopes quoted above; tree sha256 unchanged on each refusal.
  - Pytest: 57 passed. The plant run: 2 failed, naming `close.schema.json`.
- **tests:**
  - `heavy_slot.sh python3 -m pytest` on the 5 files above: 57 passed, 0 skipped.
  - Plant run in the export: 2 failed (as expected), 20 passed, 4 deselected.
  - The `local_only`/real/green_here/time_limit exclusion deselected nothing in these files.
- **discoveries:** The guard refuses a heredoc whose text carries the venv install line, even when it only writes a script into `$TMPDIR`, so the brief's "script under `$TMPDIR`" route is closed. The engineer's test, which installs inside pytest's subprocess, is the only installed-venv evidence. Mine ran from the unpacked wheel, which has the same layout as an install.
- **risks:** None within scope.
- **lessons:** For this guard, an auditor's check of "the installed gov" is best done by unpacking the wheel. That needs no install line.
- **proposed_decisions:** none.
- **unresolved:** none.
- **recommended_next_action:** The lead commits this record under `docs/probes/DAEO-zmo4/`, and the ticket lands.

**`git status --short` in the worktree:** (empty)
