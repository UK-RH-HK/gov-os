---
type: probe
id: PR-DAEO-2bdu-s29
task: DAEO-2bdu
status: ACTIVE
state_class: EVIDENCE
round: "run 10: the narrow independent check (DEC-1154) of S29, the wheel ships every file the shipped-file resolver reads (DEC-1189 (1))"
reviewer_session: 517fe42d-c1ff-4a82-bfd8-55738fe53914
implementer_session: "eng-18 b656f678-185c-4ca0-aa02-40ee9ebd485f; test designer td-21 c49d0454-b77f-4bb4-a9fb-31bddc0b7c20"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: 6f91f123b38ec3c7e8ed9f0ade452c5468dc10cd
decisions_applied: [DEC-1189, DEC-1178, DEC-1183, DEC-1154, DEC-1010, DEC-820, DEC-1065, DEC-1142]
---

# Probe record: W2-88 (DAEO-2bdu), run 10: S29, the wheel ships every file the resolver reads: PASS

## The lead's judgement and runs
- **What changed.** W2-81's run on release 0.1.0 refused `SHIPPED_FILE_MISSING: template/.gitleaks.toml` at A0 in six repositories with no kit. The owner reopened W2-88 within S24 (DEC-1189 (1)). The lead read S29's "every file the shipped-file resolver is asked for" as covering every rel passed to `fabric.shipped`, so A9's four kernel sources (`KERNEL_FOLDERS`, `KERNEL_FILES`) ship as well; the resolver's order is unchanged. A fresh test designer (td-21, `c49d0454-b77f-4bb4-a9fb-31bddc0b7c20`) revised two S24 acceptance cases to that decided behaviour, kept S24's project-copy and refusal statements on rels the wheel does not ship, and added the A0-from-wheel case (`a30bf9309535`, `Rewrite-Reason: DEC-1189 (1), S29`; 11 red at the base for their stated reasons). A fresh engineer (eng-18, `b656f678-185c-4ca0-aa02-40ee9ebd485f`) added the five copies under `src/gov/_shipped/template/`, their package-data lines, `fabric.PACKAGED`, a unit scan of every `fabric.shipped` call and an A0-from-a-wheel-of-HEAD unit test (`018b56e33f8e`). Both workers ran claude-opus-5-5, effort high, through `launch_worker.sh` / `gov launch` under the OS sandbox, the promotion "a fail-open finding" applying. The lead merged the tests (`6f91f123b38e`).
- **Who checked.** A fresh, read-only Independent Auditor (`517fe42d-c1ff-4a82-bfd8-55738fe53914`, claude-opus-5-5, effort high, started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-15 22:24 with `--owner-named DEC-1154`, TMPDIR under `/tmp/`), its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-s29.md`). The guard refused it a `pip install` into a scratch venv (installs are refused outside the CTO's session) and one `git show` whose revision was behind a shell variable; it did not respell either and showed the same facts another way (the wheel's `gov/` identical, 283 files, to the export's `src/gov`, run from no source tree).
- **The verdict stands as PASS** (success-29, success-24). Two rows, neither blocking: **S29-1** (ordinary work no, consequence other): the unit scan does not see a `shipped` call made through an import alias; a missed rel still fails closed at run time by name. **S29-2** (ordinary work yes, consequence other): from an installed wheel, A9 now takes the kernel templates and the two skills from the gov package, so a gov newer than the project's kit replaces the kit's tracked kernel templates with its own bytes (as it already does from a source tree); A9 records the replaced paths and its undo restores them. Both are listed for the CTO (Wave 3 rows; S29-2 also the release notes: the gov and the kit of one release).
- **The lead's verification at the head `6f91f123b38e` (outside the sandbox, through heavy_slot):**
  - the two S24/S29 acceptance modules (`test_w2_88_p1_shipped_bytes.py`, `test_w2_88_p1_installed.py`, wheel-installing cases included) and the unit modules `test_w2_88_s29.py`, `test_w2_88_shipped.py`, `test_w2_88_p1.py`: **62 passed** (`.gov-runtime/scratch/lead/log/acc-s29.txt`, `acc-s29.xml`);
  - the rebuild (`rebuild_slot.sh`): ok, complete, four digests (`log/rebuild-10.txt`);
  - lead_verify: **GREEN**, parallel 7,252 tests, 0 failed, 0 errors, 6 skipped; serial 1 passed (`log/verify-10-6f91f12/`).

## The auditor's return (unchanged)

task: DAEO-2bdu (W2-88), run 10, S29: narrow independent check (DEC-1154)
status: DONE. S29 passes. A wheel built from the head carries every file the resolver reads, byte for byte, and A0 passes without the kit. No blocking finding; two rows.
work_completed: Ran the sandbox check and the identity check. Built the release-form wheel from a `git archive` of the head and compared every file in it with the head. Found every `fabric.shipped` call in `src/gov` by my own reading. Ran A0 and MA from the head on planted repositories with no kit, and the same from the base for contrast. Planted five mistakes (c1 to c5) and ran the unit scan and the shipped-bytes acceptance module against each. Checked each commit's paths and trailers.
files_changed: none
evidence: TMPDIR `/tmp/gov-launch-25o04yic/claude-1000/aud29/`: `wheels/gov-0.1.0-py3-none-any.whl`, `scripts/cmpwheel.py`, `a0/out.json`, `ma/out/memory-assessment.json`, `plants/c0` to `plants/c5`, `wh-c1/`, `wh-c2/`
tests: Via heavy_slot: `test_w2_88_s29.py` (without `test_a0_from_a_wheel`) and `test_w2_88_p1_shipped_bytes.py`. Clean copy c0: 15 passed, 1 deselected. c1: 3 failed. c2: 2 failed. c3: 3 failed. c5: 15 passed (blind spot, row S29-1). Not run by me: the cases that `pip install` a wheel (`test_a0_from_a_wheel…` and `test_w2_88_p1_installed.py`), because the guard refuses installs here; the lead's run outside the sandbox has 62 passed. The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out no case in these two modules.
discoveries: The guard refused `pip install` into a scratch venv (DEC-953 item 2). I did not respell it, and I did not install the wheel by any other route. Instead I showed that the wheel's `gov/` tree is identical, file for file (283 files), to the export's `src/gov`. I then ran gov from that export, which sits under no source tree (`_source_tree()` is None).
risks: Row S29-2: from an installed wheel, A9 now writes the gov package's kernel templates over the kit's tracked copies. Where the gov's release differs from the kit's tag, those files will differ from the kit's lock.
lessons: A check of `src/gov/_shipped/` alone does not catch a dropped package-data line (plant c2). Only the unit scan's package-data check, or a wheel build, catches it.
proposed_decisions: none
unresolved: The install-performing wheel cases were not re-run by me (guard refusal, stated above).
recommended_next_action: Land S29 with rows S29-1 and S29-2 for the Wave 3 list. Bump the version to 0.1.1 at the release cut (the wheel still says 0.1.0).

# W2-88 (DAEO-2bdu): narrow check of run 10, S29 (the wheel ships every file the resolver reads, DEC-1154)
probed_commit: 6f91f123b38ec3c7e8ed9f0ade452c5468dc10cd
base: 9fa839cba6d8

## Sandbox and identity
- **Sandbox check (a):** writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `Read-only file system`, and no file exists.
- **Sandbox check (b):** `git hash-object -w --stdin` exited 0 (`1ae28402…`) and `git update-index --refresh` exited 0. This step writes one loose object and refreshes the index, as the step-0 file requires.
- **Identity:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`; HEAD is `6f91f123b38ec3c7e8ed9f0ade452c5468dc10cd`; `status --porcelain` is empty. All the same at the start and at the end.
- **Processes:** `ps` shows no ollama or llama-server process, at the start or at the end.
- **Guard refusals, each once and not retried:**
  - a `pip install` into a scratch venv (installs are refused);
  - a `git show <rev>:<path>` whose revision sat behind a shell variable. I showed the same fact another way: the planted repository's status is clean against HEAD, and its blob id equals the template's.

## The wheel and A0 without the kit
**The wheel's `gov/_shipped/`.** Built from `git archive … src pyproject.toml template` of the head, with pip offline and no build isolation. It holds 16 files, each byte-identical to `git show 6f91f123b:<rel>`:
- `template/.gitleaks.toml`
- `template/governance/kernel/skills/{retrieval,discovery}/SKILL.md`
- `template/governance/kernel/templates/{brief.md,role-cto.md}`
- `governance/project/retrieval.yaml`
- `governance/project/indep-walls/*` (6 files)
- `governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/{auditor,checker,writer}.md`
- `governance/project/orchestration/tools/memaudit_cron.sh`

All 283 files under the wheel's `gov/` equal the export's `src/gov`, and none is missing.

**Each rel the resolver reads (my own grep and reading of `src/gov`), and where it is in the wheel:**
- `safety.TEMPLATE_GITLEAKS_REL` = `template/.gitleaks.toml`: called at `safety.py:49` and `:61` (A0) and `assess.py:143` (MA). In the wheel.
- `RETRIEVAL`: called at `fabric.py:114`, `:203` and `:280`. In the wheel.
- `KERNEL_FOLDERS` and `KERNEL_FILES`: called at `fabric.py:231`, `:239` and `:292`. At `:292` the argument is computed: every file under the two skill folders (one `SKILL.md` each at the head) and the two templates. All in the wheel.
- `memory_sets.WALLS` and `BRIEFS`: called at `fabric.py:797` and `:835`, and `memory_sets.py:198`. In the wheel, every file under them.
- `memory_sets.CRON`: called at `memory_sets.py:169`. In the wheel.

No other call exists.

**A0 run.** gov ran from the export's `src`, which has no `copier.yml`, so `_source_tree()` is None and the resolver reads the package copy. The environment was hermetic (`env -i`, scratch `HOME`, working folder outside any tree). The repository was planted with a README and one file, with no kit and no `.gitleaks.toml`.
- `gov adopt --root … --session aud29 --lite --stage A0 --json` exited 0 with `"set_up": [".gitignore", ".gitleaks.toml"]`.
- Its commit `b140843 gov adopt --lite A0: safety baseline` adds `.gitignore`, `.gitleaks.toml` and `governance/adoption/A0-safety-baseline.md`.
- The tree is clean. `.gitleaks.toml` is byte-identical to the template's (blob `04ac36d7…`, which equals `git hash-object template/.gitleaks.toml`).
- The scratch `HOME`, the scratch tmp and the worktree's status are unchanged.

**MA run.** On a second planted repository with no `.gitleaks.toml`, MA exited 0: `secrets_scanned: true`, `secrets_unscanned_reason: null`, and no `no secrets rules` reason.

**Contrast at the base.** Run from an export of 9fa839cba:
- A0 refuses `SHIPPED_FILE_MISSING: template/.gitleaks.toml`, which is W2-81's refusal.
- MA gives `SECRETS_UNSCANNED`, reason `no secrets rules (.gitleaks.toml) could be read`.

## The planted mistakes
**c1: `src/gov/_shipped/template/.gitleaks.toml` removed.**
- The unit scan goes red: `test_every_rel_…shipped_byte_identical` and `test_the_check_names…` fail with "template/.gitleaks.toml: no copy at …".
- The acceptance case `test_s24_each_shipped_copy_equals_its_source_byte_for_byte[the-secrets-configuration]` goes red.
- The rebuilt wheel lacks the file.
- A0 from that copy refuses `SHIPPED_FILE_MISSING`, naming `template/.gitleaks.toml` and each place looked. It makes no commit, and the tree stays clean.

**c2: the package-data line for `brief.md` dropped from `pyproject.toml`.**
- The unit scan goes red with "template/governance/kernel/templates/brief.md: not in pyproject.toml's package data…".
- The rebuilt wheel lacks `gov/_shipped/template/governance/kernel/templates/brief.md`.
- The shipped-bytes acceptance module stays green, because the source copy is still there. The installed-wheel acceptance case would catch it, but I could not run it (install refused).

**c3: a new file added to the source skill folder (`retrieval/references/later.md`), not shipped.** This stands for a later kernel addition.
- The unit scan goes red, naming the file (through `COMPUTED`'s `_sources(None)`).
- The acceptance case `[the-retrieval-skill]` goes red.

**c4: `_shipped/…/role-cto.md` removed.** A9's first read, `fabric._sources(root)`, on a repository with no kit refuses `SHIPPED_FILE_MISSING`, naming `template/governance/kernel/templates/role-cto.md`.

**c5: a module calling `shipped` through an alias** (`from gov.adopt.fabric import shipped as find`) with an unshipped rel. The unit scan stays green, so it misses this call (row S29-1).

## The lead's reading of S29
The reading is S29's. The KPI line and DEC-1189 (1) both say "every file the shipped-file resolver is asked for", and the unit check is to list "every constant passed to `fabric.shipped`". `KERNEL_FOLDERS` and `KERNEL_FILES` are such constants, so shipping them is required, not scope creep.

It breaks nothing S24 states:
- S24 asks that A9 copy the kernel files and read its other inputs "from shipped bytes". The package copy is shipped bytes of the same release.
- The resolver's order (source tree, then package, then the project's copy) is the one run 8 already set.
- S24's step-3 case and its refusal case are kept: the revised acceptance and unit cases now use rels the wheel does not ship (`planning`, `checkpoint.md`, `test-design`), and their intent is unchanged.

The one change in behaviour is row S29-2.

## What I probed and found sound
- **Wheel contents:** every rel and every file under it is in the wheel, byte-identical to the head; the package data, the files under `src/gov/_shipped/` and `fabric.PACKAGED` agree.
- **A0 and MA from the release form on a repository with no kit:** both pass, and A0 commits the template's bytes. Nothing outside the planted repository changes.
- **Refusals by name:** a missing shipped file is refused by name in A0 and in A9's source read, never replaced by a default.
- **The unit scan fails closed** on these arguments:
  - a parameter or local name, which it reports as unresolved with file and line (its own planted case);
  - a folder that gains a file;
  - a missing package-data line;
  - a missing or drifted copy.
- **Commit paths:**
  - engineer commit 018b56e33 changes only `pyproject.toml`, `src/gov/_shipped/**`, `src/gov/adopt/fabric.py` and `tests/unit/adopt/test_w2_88*`, all in `allowed_paths`;
  - test designer commit a30bf9309 changes only `tests/acceptance/W2-88/**`.
- **Commit trailers:** each of the three commits carries `Task: DAEO-2bdu` in one final trailer paragraph. Its `Implements:` (DEC-1189, DEC-1178, DEC-1183, DEC-954, CAP-44.f) lists only ids in `sources:`.
- **No acceptance test changed by the engineer.**
- **The engineer's two departures** (an empty here-document; `sed -i` on its own new test file) touched nothing outside its own path.

## Findings
**S29-1:** success-29, low. The unit scan matches calls only by the name `shipped` (`fabric.shipped(...)` or `shipped(...)`). A call through an import alias (`from gov.adopt.fabric import shipped as find`) is not seen, so a later unshipped rel passed that way would pass the scan.
- Reproduce: plant c5 (one module with the alias and an unshipped rel). The scan stays green, 15 passed.
- Should have: the scan resolves import aliases of `gov.adopt.fabric.shipped`, or fails on any binding of it under another name.
- Reversed by: a scan run in which such an aliased call is reported.
- `Ordinary work: no, because the code's one convention is fabric.shipped or shipped, and renaming the resolver on import is an unusual construction`
- `Consequence: other` (a missed rel fails closed at run time: `SHIPPED_FILE_MISSING` by name, as plant c1 shows)

**S29-2:** success-24/success-29, low. From an installed wheel, A9 now takes `brief.md`, `role-cto.md` and the two skills from the gov package's copy, before the kit's copy. Before S29 it copied the project's own `governance/kernel/templates/*.md` onto itself.
- So where the installed gov's release differs from the kit's tag, A9's commit replaces the kit's tracked kernel templates with the gov's bytes, and `gov lock`'s comparison of `governance/kernel/` would then report drift.
- This is the same as A9 already does when gov runs from a source tree, and it is the "as Gov OS ships them" that S24 and S29 ask for.
- Reproduce (by reading `fabric.install`, not run): a gov at a later release than the kit's tag, with a template that differs between the two, then A9.
- Should have: either this is accepted as the meaning of "as Gov OS ships them", or A9 or the kit states that the gov's and the kit's releases must match.
- Reversed by: a check, at A9 or before it, that refuses a gov and kit of different releases. Or no shipped kernel template differs between releases.
- `Ordinary work: yes, because a gov upgraded ahead of a project's kit is plausible`
- `Consequence: other` (A9 records the replaced paths and its undo restores them on a refusal; the earlier bytes stay in history; nothing opens or is lost)

## Notes, not findings
- I did not run the wheel-installing cases, because the guard refused installs here. The equivalence between the wheel's `gov/` and the export's `src/gov` (283 files, identical) is my evidence instead, beside the lead's 62 passed.
- The shipped-bytes acceptance module reads `src/gov/_shipped/`, not the wheel, so a dropped package-data line is caught only by the unit scan and the installed-wheel acceptance case (plant c2).
- The built wheel is versioned `0.1.0`. The bump to 0.1.1 belongs to the release cut, not S29.
- `src/gov/store/loader.py:635` still reads a schema through `parents[3]`. That read is outside this run's change and is not a `shipped` read.
- copier.yml sets no `_templates_suffix`, so `template/.gitleaks.toml` is copied verbatim, and the package's copy equals what copier installs.

```verdict
{"kpis": [{"kpi": "success-29", "verdict": "pass", "findings": [{"id": "S29-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "S29-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-24", "verdict": "pass", "findings": [{"id": "S29-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}], "overall": "pass"}
```
