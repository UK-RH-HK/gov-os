---
id: AUD-ADOPT-A5
type: research
status: ACCEPTED
state_class: EVIDENCE
title: The independent auditor's verdict on the path map of this repository's adoption
verdict: pass
path_map_hash: cc4c56bed901ccdfcfeca68d414d2ee4e8935bb47f30795d0d55118aec68af7b
auditor_session: d9976438-5046-42b8-96a2-b28318846ce1
---

# The independent auditor's verdict on the path map of this repository's adoption

**Verdict: pass.** The path map is what DEC-617 decided, and no live code uses the old `cli/` tree.

Audited at `21e8bf0e` on `w1/integrate`, ticket `DAEO-03pw`, role `independent-auditor` (`printenv GOV_ROLE GOV_TICKET`
printed both). The session id is the value of `CLAUDE_CODE_SESSION_ID` in this session; it is not the session that ran
the stages (`45f2a529-6746-474d-b738-e1df6781c663`, named in the frontmatter of A0 to A4). I built nothing of what is
audited and changed nothing but this file.

## The hash

`sha256sum governance/adoption/A3-target-path-map.md` printed
`cc4c56bed901ccdfcfeca68d414d2ee4e8935bb47f30795d0d55118aec68af7b`, the value I was given. A4 names the same value in
`stands_on` and in `path_map_hash`. The chain below holds as well: A3 `stands_on` is the sha256 of A2 (`88f3fcfe…`),
A2 `stands_on` is the sha256 of A1 (`9ec1e8fe…`). The backup ref of A0 (`refs/gov/adoption/backup/8b23e345a02b`)
resolves to the baseline commit `8b23e345a02b99071ef616cebd984e054352d394`.

## 1. The path map and the plan

A script parsed the frontmatter of A3 and A4 and held it against `git ls-files cli` and `git ls-tree -r HEAD`. It printed:

- A3: 1,712 entries, 1,712 distinct paths; actions `KEEP` 1,596 and `DELETE_FROM_ACTIVE_TREE` 116, no other action.
- `git ls-files cli`: 116 files. The set of entries that are not `KEEP` equals that set exactly; none lies outside
  `cli/`; no entry under `cli/` is `KEEP`. All 116 carry `batch: 1`, and the blob of each equals the blob at HEAD.
- A `KEEP` entry carries `path` and `action` and no other key: nothing moves, nothing is renamed.
- A4: one batch (number 1, rollback point `refs/gov/adoption/rollback/batch-1`), 116 entries, the same set as
  `git ls-files cli`, every action `DELETE_FROM_ACTIVE_TREE`, every blob equal to HEAD; `dependents: []`,
  `retirements: []`.

This is what DEC-617 (`docs/DECISION_REGISTER.md` line 6576) and DEC-624 (line 6669) state: 116 files, one batch,
nothing else.

## 2. Does anything live use `cli/`?

No. What the tree holds: `cli/govbridge/` (36 files, a Python package), `cli/config/` (10), `cli/tests/` (70).

Searches were run with GNU grep (`command grep`) for `govbridge`, for `cli/` not preceded by a path or word character,
for `"cli"` as a path component, and for the base names of the files under `cli/config/`.

- **`src/`.** `govbridge` appears three times, all in module docstrings that say where code was ported from
  (`src/gov/retrieval/lexical.py:3-4`, `src/gov/retrieval/chunking.py:3`). No import. The one path is
  `src/gov/doctor/command.py:43`: `"cli/"` in `HISTORICAL_PATHS`, a prefix that excludes files from the stale-path
  report; it reads nothing and needs no file to exist. No base name of a file under `cli/config/` appears in `src/`.
- **Packaging.** `pyproject.toml` finds packages under `src` only and has one script, `gov = "gov.cli.main:main"`,
  the Python package. No other manifest is tracked at the top level (`copier.yml` does not name the tree).
- **Tests.** One use, and it skips: `tests/unit/retrieval/test_lexical.py:19` puts `cli` on `sys.path` and line 54
  does `pytest.importorskip("govbridge.core.chunking")` in `test_the_chunking_is_the_carried_one`. Every other hit is
  not this tree: `tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py:128,308` write a `cli/` file into a
  synthetic project of their own; `tests/acceptance/W1-39/w1_39_support.py:91` names `cli` among the names an
  installed product must not hold; `tests/unit/doctor/test_doctor.py:264,267` and
  `tests/unit/launch/test_command_modules.py` pass strings or build a package in a temporary directory; the W1-16
  hits are the argument `cli` of the code-intelligence tool. No `conftest.py` and no pytest configuration collects
  `cli/tests`.
- **Kernel template and check declarations.** No hit for the tree or for `govbridge` under `template/`, including
  `template/governance/kernel/checks/`. The retrieval-regression check (`src/gov/retrieval/retrieve_check.py:38-66`)
  indexes clones of the dev tiers, not this repository.
- **Hooks and CI.** `lefthook.yml` runs `gov ci …` only. `.github/workflows/ci.yml` installs the package from the
  checkout and runs `python3 -m pytest tests`, not `cli/tests`. No hit in `.rulesync/`.
- **`docs/plan/tools/`.** No hit.
- **The project's path map.** `governance/project/path-map.yaml:107-116`: the namespace `carried-code` has
  `paths: ["cli/**", "schemas/**"]`. No policy and no capability needs a file under `cli/`; line 164 is `src/gov/cli/**`.

## 4. What was run

- `PYTHONPATH=src python3 -m pytest tests/unit -q -x -n 4` in the repository: **1889 passed**.
- The same suite in a throwaway clone under the session's temporary directory with `git rm -r cli` applied there
  (nothing in the repository touched): **1888 passed, 1 skipped**. The skip is
  `tests/unit/retrieval/test_lexical.py:54: could not import 'govbridge.core.chunking'`.
- In that clone, `tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py` and
  `tests/acceptance/W1-39/test_w1_39_layout.py`: **12 passed**.
- `gov.check.pathmap.check` on the repository and on the clone without the tree: 0 findings both times.

## 3. Findings

None is a reason to stop the deletion.

1. **Low. One unit test loses its evidence.** `test_the_chunking_is_the_carried_one` compares the ported chunking with
   the carried one. After the deletion it skips for good, and line 19 of the file puts a missing directory on
   `sys.path`. The comparison passed at this commit; afterwards nothing holds the port against its origin.
2. **Low. Documents that point at `cli/` as if it were there.** `README.md:9-11` lists `cli/govbridge/`, `cli/config/`
   and `cli/tests/` in the layout. `docs/SOURCES.md` has 116 lines that name a file under `cli/` as a carried file.
   `docs/adr/ADR-0002-architecture-and-stack.md:67,156` and `docs/plan/WAVE_1_WBS.md:168` name `cli/govbridge`
   (the ADR already says "then removed").
3. **Low. A pattern that will match no file.** In the namespace `carried-code`, `cli/**` will hold nothing. The
   namespace itself is not empty: `schemas/**` holds 5 tracked files. The path-map check reports files without a
   namespace, not patterns without files, and stays at 0 findings.
4. **Low. Dead entries.** `.gitleaks.toml:45` allows `cli/tests/fixtures/core/repobuilder.py`;
   `src/gov/doctor/command.py:43` lists `cli/` as historical; the closed ticket `.tickets/DAEO-rxln.md:24` lists
   `cli/govbridge/**` among its paths. All harmless once the tree is gone.
5. **Low. The retention condition is not what I verified.** The namespace says the tree stays "until the tickets that
   reuse it have ported it into src/gov/". Only the lexical index and the chunking name a port in `src/`. Whether the
   rest (`authority`, `semantic`, `compile`, `gather`, `graph`, `core`) was meant to be ported is not something this
   audit establishes; DEC-617 retires the tree regardless, and it stays in history and at the backup ref.
6. **Info. The tree is Python, not Rust.** My brief called `cli/` a Rust prototype. It holds 83 `.py` files, 23 YAML
   files and fixtures, and no Rust. The register (DEC-617, DEC-624) says only "the old `cli/` tree", and the 116 files
   are the same either way.
7. **Info. Five tracked files have no entry in the path map:** the adoption records A0 to A4 themselves (1,717
   tracked files at HEAD, 1,712 entries). They were written after the inventory; they stay.
8. **Info. The rollback ref does not exist yet** (`git rev-parse refs/gov/adoption/rollback/batch-1` fails); by
   `src/gov/adopt/stages.py` stage A6 sets it when the batch runs.

## What I did not check, and how I worked

- `docs/source/` cannot be read from this session. The rest of `governance/project/` was not searched, as instructed;
  only `path-map.yaml` was read. The acceptance suites were not run as a whole.
- The dev query set of the retrieval-regression check lies outside the repository and was not read.
- A write of a script under `.gov-runtime/scratch/auditor/` was refused; the script and the clone went to the
  session's own temporary directories instead.
- The shell's `grep` in this session is a wrapper that returned no match for a pattern GNU grep matches (it missed
  `README.md:9` and `path-map.yaml:108`). Every search this report rests on was repeated with `command grep`.
