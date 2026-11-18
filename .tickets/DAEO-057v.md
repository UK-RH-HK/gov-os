---
id: DAEO-057v
status: in_progress
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-18
tags: [implementation, standard, emergency-2]
wbs_id: W2-18
title: 'Pinned install: a product repository runs a fixed release, never the development copy'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/install/**
- src/gov/release/__init__.py
- src/gov/doctor/install*
- src/gov/doctor/command.py
- src/gov/cli/main.py
- template/governance/kernel/hooks/**
- template/.rulesync/hooks.jsonc
- tests/unit/install/**
- tests/acceptance/W2-18/**
kpis:
  success:
  - '`gov install <version>` installs the release''s gov into the repository''s own tool environment from the release''s wheel, verified against the manifest''s sha256, never an editable install [CAP-43]. Verify: in a planted adopted repository whose source holds fixture release A (tag `vA`, its record): `gov install A` exits 0; `<common>/gov/pin.json` (`<common>` the repository''s git common dir) names A, the wheel''s name and sha256 equal to the manifest''s and the hash check passed; `<common>/gov/bin/gov --version` prints A''s CLI version; the environment''s gov lies in its own site-packages and no `direct_url.json` marks it editable; a fixture release whose wheel (given by `--wheel`, or built from the release commit) does not hash to the manifest''s sha256 is refused, exit non-zero naming the wheel and both hashes, and `<common>/gov/` is left as it was.'
  - '`gov doctor` in a product repository fails when its gov is an editable install, resolves to a source tree''s `src/`, or differs from `framework.lock` [CAP-43, W2-H021]. Verify: three planted repositories with a pin: the pin''s gov an editable install; the pin''s version and wheel sha256 differing from the release `framework.lock` names; doctor run by a gov that resolves to a source tree''s `src/gov` (`PYTHONPATH`, with `GOV_PIN=off`): each makes `gov doctor --json`''s `install` section fail naming its case (`editable`, `lock`, `source_tree`) and doctor exit non-zero; a repository whose pinned gov matches `framework.lock`, doctor run as `<common>/gov/bin/gov doctor --json`: the `install` section passes; a repository with no pin: the section is `unmeasured` and names `gov install`.'
  - 'The kernel hooks a session runs import the pinned gov, never the product''s own package named gov [W2-M123, W2-H032, W2-M279]. Verify: in a planted product repository with a pin and its own `src/gov` package whose `checkpoint/record.py` writes a marker file when imported: the PreCompact and Stop hook command lines of the template''s `.rulesync/hooks.jsonc`, run with `CLAUDE_PROJECT_DIR=<repository>` and `GOV_TICKET` set, write the checkpoint record under `.gov-runtime/scratch/checkpoints/` and leave no marker; the same from a linked worktree of the repository (the pin found through the git common dir).'
  - 'With no gov installed, the kernel hooks say so clearly instead of blocking every call [W2-L172, W2-L230, W2-L173, W2-L174]. Verify: a planted repository with no pin, no `$HOME/.local/bin/gov`, no gov on PATH and a `python3` that imports no gov: each kernel hook command line of the template''s `.rulesync/hooks.jsonc` exits 0 and prints one line on stderr naming the missing gov.'
  - 'Two repositories on the machine run two different releases side by side [CAP-43]. Verify: two planted repositories pinned to releases A and B: `gov --version`, the same console script run from each repository''s folder, prints A''s version in one and B''s in the other (a `gov` started inside a repository with a pin runs that pin, unless `GOV_PIN=off`); neither repository''s files change.'
  failure:
  - 'A product session that imports a source tree''s `src/gov` is refused by doctor and reported. Verify: a planted repository with a pin, `gov doctor --json` run with `PYTHONPATH=<a source tree>/src` and `GOV_PIN=off`: exits non-zero, and its `install` section fails with case `source_tree` naming the path it imported; it never passes for that case.'
profile: STANDARD
sources:
- CAP-43
est_loc: 140
acceptance_tests:
  path: tests/acceptance/W2-18/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- CAP-43
- W2-H032
- W2-H021
list_rows:
- W2-H021
- W2-H032
- W2-L047
- W2-L172
- W2-L173
- W2-L174
- W2-L230
- W2-L231
- W2-M069
- W2-M123
- W2-M127
- W2-M206
- W2-M279
- W2-M318
---
# W2-18 Pinned install: a product repository runs a fixed release, never the development copy

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** The rest of K7 (DEC-941 item 3); W2-81 and EXAMIN install W2-16's release (DEC-954 Q8c).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-18), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.
- **KPIs, success:**
  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned `gov`, never a product's own package named `gov`. With no `gov` installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173, W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
- **KPIs, failure:** a product session that imports this repository's `src/gov` is refused by doctor and reported.

**D9-FATES (DEC-1083):** Wave 3 by DEC-1083 (D9-FATES, as P1-PLAN §C); the status is kept.

**Moved to Wave 3's list 2026-11-16 by the owner (DEC-1201 (3)):** W2-18 leaves Wave 2's list (status `deferred`, tag `wave-2` removed); it is not closed and not done. It is listed in `docs/plan/WAVE_3_PARKING.md` under "Moved from Wave 2 (DEC-1201)". `gov plan` no longer offers it.

**Emergency 2 (2026-11-17): built with W2-17** (EMERGENCY-2 §6.2 A-4: "`gov update` installs a pinned release"). The KPI lines above are rewritten for §2 and §8, approved by the CTO's brief to the ticket lead:

- **The guard is retired (§2.2, §6.1):** the line on "the guard and kernel hooks" keeps only the kernel hooks.
- **Where the pin lives:** in the repository's git common dir, `<common>/gov/`: `envs/<version>/` (a virtual environment with the system's packages, the release's wheel installed with `pip --no-deps --no-index`), `bin/gov` (a link switched by an atomic rename), `pin.json` (the version, the wheel's name and sha256, the manifest's sha256, the source and the release commit). Every worktree of the repository shares it, nothing in it is tracked, and the machine's own pin (`~/.local/bin/gov`) is untouched.
- **The wheel:** built from the release commit exactly as `gov release` builds it (`SOURCE_DATE_EPOCH` the commit's time), or taken from `--wheel <file>`; either is installed only when its sha256 is the manifest's.
- **No guard, no sandbox, no ACTs (§2):** `gov install` is an ordinary command; the hook command lines change by an ordinary commit (2.10).
