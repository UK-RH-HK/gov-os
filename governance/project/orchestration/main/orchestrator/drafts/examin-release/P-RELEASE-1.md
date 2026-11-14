# P-RELEASE-1: the first numbered, frozen release of the Gov OS (0.1.0), for EXAMIN's copy

From: the CTO (DAEO-sdxk), 2026-11-14. Under: DEC-772, DEC-1089 (a), DEC-1090 (5), DEC-1174 (2), DEC-954 Q8c.
Draft: nothing has been built, committed or tagged. The notes and the evidence behind every claim are in `NOTES.md`
beside this file.

## (1) Context

- W2-27's KPI lines need the first numbered, frozen release: cut by you, hash-checked by me, recorded in
  `docs/plan/wave-2/examin-copy/release-check.md`, and installed. EXAMIN's copy must never run this repository's branch.
- No release exists yet. `docs/releases/` holds only its README, and `pyproject.toml` says 0.1.0.
- The live pin is `pin-797495bdfc70` (11-11). It is 1,290 commits behind the head, and it lacks `gov adapters` and
  `gov wait`, which the copy needs.
- W2-102's release skill was retired (DEC-1083), so the procedure is W2-16's: `docs/releases/README.md` and
  `gov release <version>`. Only you run it, in a plain terminal.
- DEC-1174 (2) asked for the EXAMIN CTO's fixed first brief to come with the release. It is
  `EXAMIN-CTO-first-brief.md`, beside this file.

## (2) What goes in: which commit

| | (A) Now: integrate head `2b034037a` | (B) Recommended: integrate head after three lands |
|---|---|---|
| What it holds | everything merged to date | (A) plus W2-100 and W2-101 (about 70 new kernel skill files, hand merge and their copies ACTs), and W2-42a R3 (the product guard's parser: a write after a here-string, and the fallback's three here-string fail-opens) |
| The guard EXAMIN runs | the parser with the known R3 fail-opens. That is the write wall the precondition probes rely on | the fixed parser |
| W2-27 can start? | no. W2-42a (`DAEO-03ub`) is in W2-27's own deps and is `in_progress` again since 04:39 today | yes, once W2-42a closes again |
| Follow-up | a 0.1.1 release and a second re-pin window within days (about 15 min of your time, 2 to 3 h of mine, one review) | none known |
| Delay | none | W2-100 and W2-101 wait on your yes to their CIT-Ps (`cdac25763`, `3bf1c96b4`); then hours. W2-42a R3 started at 04:40; my estimate is half a day |

**Recommendation: (B).** Option (A) saves under a day, but W2-27 cannot start on it anyway (W2-42a is reopened), and
it would ship the guard without the fix the precondition probes depend on.

**One more fix to choose now (P-1, found while drafting).** Stage A9 of `gov adopt` (W2-88's memory tools at
adoption) cannot work from an installed release:
- `src/gov/adopt/fabric.py:36` takes the Gov OS root as `Path(__file__).parents[3]`. From a wheel, that is
  `<pin>/lib/python3.12`, which holds no `template/`.
- So A9 refuses with `KERNEL_SOURCE_MISSING` (`fabric.py:154-170`).
- Its standard pool, its walls and its MEMORY-AUDIT-1 briefs fall back silently (`fabric.py:53-60`,
  `memory_sets.py:29-31,136`).
- I checked that the wheel holds no `template/`. W2-88's tests run from the source tree, so they never met it.

The choice:
- **(a)** I route it as a defect in W2-88's closed scope (DEC-1164 (18)), with a narrow independent check, and it
  joins the commit point (B).
- **(b)** We leave it, and the EXAMIN CTO hits it at A9 as a finding. That means a 0.1.1 release and a re-pin.

I recommend (a). It is known now, and a re-release costs a sitting of yours and a re-pin window.

## (3) The version: 0.1.0

What `gov release` checks (`src/gov/release/__init__.py`):
- the version is a semantic version (lines 40-42, 161);
- the repository does not know it yet: no record in the tree or in any ref's history, and no tag `v<version>` or
  `<version>` (lines 89-113, 174-176);
- the tree is clean, with no untracked files (line 164);
- HEAD is a commit of `w2/integrate` (lines 168-171).

It does **not** compare the version with the CLI's own. The tags `v4.1.3-rc1`, `v4.1.4-rc1` and `v4.1.5-rc1` exist,
so those three versions are refused. 0.1.0 is free.

Why 0.1.0:
- it equals `pyproject.toml`'s version, so the manifest's `cli_version`, the wheel's name (`gov-0.1.0-…whl`) and what
  `gov` itself reports all agree with the release, with no code change;
- 0.y.z is the semantic-versioning form for "not yet stable", which is right while Wave 2's exit criteria are open.

The cost: every older pin also reports "gov 0.1.0", so the number alone does not tell them apart. The manifest's wheel
sha256 does. Before 0.2.0, `pyproject.toml`'s version should be raised in a ticket.

## (4) Your exact steps (`docs/releases/README.md`, about 15 minutes)

**First, mine:** I say "release ready at `<C>`" only when all of this holds:
- `<C>` is `w2/integrate`'s head, and the main tree is clean;
- my hold is on: nothing lands on `w2/integrate` from that message until the re-pin in §6 is done. The release needs
  HEAD = `<C>`, and the re-pin's frozen-src rule needs `src/` and `pyproject.toml` unchanged after `<C>`.

**Then yours:**

1. Open a plain terminal (Windows Terminal, then WSL). Not a Claude Code session, not a terminal started from one, and
   not the operator console.
   ```
   env | grep '^GOV_'          # must print nothing; if it prints, run: unset GOV_ROLE GOV_TICKET
   ```
2. Check the checkout:
   ```
   cd /home/usain/Dynamic-Agentic-Engineering-OS
   git branch --show-current                     # w2/integrate
   git rev-parse HEAD                            # the <C> I named
   git status --porcelain --untracked-files=all  # must print nothing
   ```
3. Build:
   ```
   ~/.local/bin/gov release 0.1.0
   ```
   - It shows `type RELEASE-<4 digits> to build release 0.1.0:`. Type that code and press Enter.
   - It answers with `"version": "0.1.0"` and the record's path.
   - A `RELEASE_REFUSED` names its reason. Tell me, and do nothing else.
   - The release code in the live pin is the head's own: `src/gov/release` and `src/gov/lock` are unchanged since
     `797495bdfc70`.
4. Check the record:
   ```
   (cd docs/releases/0.1.0 && sha256sum -c manifest.sha256)   # manifest.json: OK
   git status --porcelain                                       # only: ?? docs/releases/0.1.0/
   ```
5. Commit it, with the trailers in ONE final paragraph:
   ```
   git add docs/releases/0.1.0
   git commit -F - <<'EOF'
   Release 0.1.0: the record of the first numbered, frozen release (W2-16, DEC-772)

   Built by gov release 0.1.0 from <C> on w2/integrate.

   Role: owner
   Task: DAEO-sdxk
   Implements: DEC-772, DEC-1089, DEC-<n>
   EOF
   git log -1 --format='%(trailers)'     # shows the three lines
   ```
   - `DEC-<n>` is the decision I record from your yes to this package.
   - **The trailer form is open: no rule or README states it.** I propose the form of your ACT commits (`Role: owner`,
     `Task: DAEO-sdxk`, `Implements:`).
   - `Task: decision-record` is wrong here. Gate (h) measures a decision-record commit only when it changes governance
     records, and `docs/releases/` is not one of them (`src/gov/close/gates.py:29-31`).
   - The landing check passes any `Role: owner` commit (`governance/project/operator/landing_check.py:10-13`).
   - `Task: DAEO-h4rh` (W2-27) would put `docs/releases/` outside W2-27's allowed paths at its close.
   - No `Co-Authored-By`: the commit is yours.
6. Tag **the record commit**, the one you just made, unsigned:
   ```
   git tag -a v0.1.0 -m "Release 0.1.0 (W2-16)"
   git rev-parse 'v0.1.0^{commit}' HEAD          # the same id twice
   git rev-parse HEAD^                           # <C>
   ```
   - The README says "tag the release commit", which is ambiguous. The install path checks out the tag and needs the
     tagged tree to hold `docs/releases/0.1.0/` (`src/gov/release/__init__.py:307-309`). A tag on `<C>` itself would be
     refused at install with "names no release".
   - An annotated tag is unsigned too. I propose it so Copier's `git describe` finds it. Copier's use of
     `git describe --tags` is my assumption (NOTES A-3).
7. Optional, yours, as usual (DEC-1087 (7)): `git push origin w2/integrate v0.1.0`.
8. Tell me "released".

## (5) My hash-check after it (about 30 minutes, written to `docs/plan/wave-2/examin-copy/release-check.md`)

The checks run in my scratch, and none of them runs `gov release`.
- **Use literal revisions in git commands.** The guard refuses a git revision held in a shell variable ("git cannot
  say whether a revision holds the hidden part"; seen today). `<C>` below is the 40-hex id typed out, and `<E>` is its
  commit time.
- **Use the pin that built the release.** `PY` is the interpreter of the pin `~/.local/bin/gov` named when you built,
  so its setuptools is the same.

```
R=/home/usain/Dynamic-Agentic-Engineering-OS
X=$R/.gov-runtime/scratch/orchestrator/release-check-0.1.0
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
mkdir -p $X
# 1. The record's own hash, and what the manifest states
(cd $R/docs/releases/0.1.0 && sha256sum -c manifest.sha256)
$PY -c 'import json,sys; m=json.load(open(sys.argv[1])); print(m["version"], m["commit"], m["cli_version"], m["wheel"]["name"], m["wheel"]["sha256"], len(m["files"]))' $R/docs/releases/0.1.0/manifest.json
# 2. The tag and its place
git -C $R cat-file -t v0.1.0                                    # tag
git -C $R rev-parse 'v0.1.0^{commit}^'                          # = <C>
git -C $R diff --name-only <C> 'v0.1.0^{commit}'                # only docs/releases/0.1.0/manifest.json and manifest.sha256
git -C $R merge-base --is-ancestor <C> w2/integrate && echo contained
git -C $R show -s --format=%ct <C>                              # = <E>
# 3. Two builds give the same bytes: the release's own form (git archive of pyproject.toml and src; build_meta), twice
mkdir -p $X/src-1 $X/src-2 $X/whl-1 $X/whl-2
git -C $R archive --format=tar <C> pyproject.toml src | tar -x -C $X/src-1
git -C $R archive --format=tar <C> pyproject.toml src | tar -x -C $X/src-2
for n in 1 2; do (cd $X/src-$n && SOURCE_DATE_EPOCH=<E> TMPDIR=$X $PY -c "import sys; from setuptools import build_meta; print(build_meta.build_wheel(sys.argv[1]))" $X/whl-$n); done
#    and a third in the re-pin ladder's form (full export, pip wheel), the form §6 installs
mkdir -p $X/full $X/whl-ladder
git -C $R archive --format=tar <C> | tar -x -C $X/full
SOURCE_DATE_EPOCH=<E> TMPDIR=$X python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w $X/whl-ladder $X/full
sha256sum $X/whl-1/*.whl $X/whl-2/*.whl $X/whl-ladder/*.whl    # all three = the manifest's wheel sha256
# 4. Every file matches the manifest: the product's verify, and an independent count
mkdir -p $X/tag
git -C $R archive --format=tar v0.1.0 template docs/releases/0.1.0 | tar -x -C $X/tag
$PY -c "from pathlib import Path; from gov.release import verify; d,h=verify(Path('$X/tag'),'0.1.0'); print('verify ok', h)"
python3 $X/check_files.py $X/tag 0.1.0        # prints: files N, matched N, mismatched 0, missing 0, extra 0
git -C $R diff --quiet <C> v0.1.0 -- template && echo "template unchanged by the record commit"
# 5. The install path's own check (the Copier task gov release --lock-from), in a scratch project
mkdir -p $X/lockcheck && git -C $X/lockcheck init -q
GOV_ROLE=orchestrator copier copy --trust --defaults --vcs-ref v0.1.0 $R $X/lockcheck
grep -n -A3 '^release' $X/lockcheck/governance/framework.lock  # version 0.1.0 and the manifest's sha256
```

- `check_files.py` is a 15-line script I write first. It reads `manifest.json`, hashes every file under
  `<tag>/template/` as stored (a link as its target), and counts mismatched, missing and extra files. It does not use
  gov's code.
- I tested step 3's method today on the live pin's commit `797495bdfc70`. Two release-form builds gave `04b094fb…d7c3`,
  the same sha256 as that pin's wheel, which the ladder built in its own form. So the release's wheel and the ladder's
  wheel are the same bytes on this machine's setuptools 68.1.2.
- Step 5 needs `gov` on PATH and runs it as the orchestrator, which the lock task allows (DEC-761).
- **After the re-pin (§6), two more lines** go in the same record:
  - `sha256sum ~/.local/share/gov-os/wheels/<C12>/gov-0.1.0-py3-none-any.whl` equals the manifest's wheel sha256;
  - `readlink -f ~/.local/bin/gov` names `pin-<C12>`.
- The record is committed with `Task: DAEO-h4rh`, `Role: orchestrator`, `Implements: DEC-1089, DEC-<n>` in one final
  paragraph. `docs/plan/wave-2/examin-copy/**` is in W2-27's paths.

## (6) How the release becomes what EXAMIN's copy installs

W2-27 needs two things installed from the release:
- the `gov` program;
- the kit (the kernel, its hooks and the lock) in the clone.

**What W2-27's lines require:** "W2-16's numbered, frozen release is the one installed, never this repository's
branch" and "the pinned, hash-verified release is installed". They do not ask for gov in the clone's own virtual
environment. The clone's venv is only for EXAMIN's own 10 product-suite packages, and those only with your approval
(W2-27's install-package line).

**`gov` is installed by the re-pin from the release.** A separate install into the clone's venv would not do:
- the product's hooks run `$HOME/.local/bin/gov` first, and use PATH only when that file is missing
  (`template/governance/kernel/settings.json:13`, `template/.rulesync/hooks.jsonc:7`);
- so the EXAMIN session's guard runs whatever `~/.local/bin/gov` is, whatever its venv holds.

**What the ladder supports today:**
- It builds from a commit and checks against the dry run's sha256 (`REPIN-COMMANDS-W5.sh:30-33, 132-146`).
- It can install the release: I fill in C = the manifest's `commit`, EPOCH = that commit's time, and SHA = the
  manifest's wheel sha256. The test in §5 shows its form gives the release's bytes.
- The rest is a usual window: dry run, rehearsal, independent review, your operator's run (about 5 minutes), and the
  rollback line.

**What it needs to do next, in order:**
1. **The re-pin from the release.** A window like ACT-REPIN-W5, with C = `<C>`. The script stops unless its two builds
   equal the manifest's sha256.
2. **The clone, by your operator:**
   - `git clone` the workbench copy (clean at `0a82082`) into `/home/usain/gov-os-runs/W2-27/examin`;
   - `git remote remove origin`, so that no git command in the copy reads the workbench (DEC-723);
   - write and commit `governance/project/held-out.yaml` with `held_out_paths: [/home/usain/gov-os-eval,
     /home/usain/gov-os-workbench]`. This is the only product rule that walls the sets root (P-4 below);
   - start the `examin-cto` session (P-EXAMIN-CTO-1 §3).
3. **The kit, from the tag:**
   ```
   copier copy --trust --defaults --vcs-ref v0.1.0 /home/usain/Dynamic-Agentic-Engineering-OS .
   gov adapters generate
   ```
   - Copier's task `gov release --lock-from` checks the tagged release against its hashes and writes
     `governance/framework.lock`, which `gov doctor` compares.
   - `gov adapters generate` writes `.claude/settings.json` with the product's hooks.
   - Then commit, then `gov adopt --lite --stage A0`, then the session's restart.
   - Who runs this is your choice (§9, line 4).

**Findings: what is missing, by name** (evidence in NOTES):
- **RL-1:** the ladder has no "from a release" input. It never reads `docs/releases/<v>/manifest.json` or the tag, and
  I copy C and SHA in by hand. One check line in the script would close it.
- **RL-2: one pin serves the whole machine.** `~/.local/bin/gov` serves this repository and the copy's hooks alike.
  So every re-pin during W2-27, including the fixes P-EXAMIN-CTO-1 §5 sends "as a re-pin", takes the copy off the
  release, unless that re-pin is itself a numbered release (0.1.1, …). Your choice is §9, line 3.
- **RL-3: the frozen-src rule.** The ladder stops if `src/` or `pyproject.toml` differ between C and integrate's head
  (ACT-REPIN-W5.md:12-17). Nothing that touches them may land between the release and the re-pin, so one hold covers
  both.
- **RL-4: the kit installs only by `copier copy` from this repository at the tag.** `gov install` and `gov update` are
  Wave 3 (W2-18, W2-17; `release/__init__.py:11-12`).
- **P-2:** the live pin has no `gov adapters` and no `gov wait`. The re-pin is needed before the kit install, and before
  the copy's facts line (`wait_for = gov wait`).
- **P-3:** A0 installs no hooks. It writes `.gitleaks.toml`, the `.gov-runtime/` ignore line and the coordination
  ticket (`src/gov/adopt/stages.py:149-162`). The hooks come from the kit install. So DEC-1174 (2)(i)'s "right after A0
  has installed them" should read "right after the kit install and A0". The brief says so.
- **P-4:** the sets root's hidden-folder rule (`sets_root_hidden`) is only in this repository's live hook
  (`.claude/hooks/pretooluse.py:374`). It is in neither `src/gov` nor `template/`. In an adopted project the only wall
  is `governance/project/held-out.yaml` (`src/gov/guard/heldout.py:21-55`, DEC-162). Nothing in adoption writes it,
  so your operator writes it.
- **P-5:** the orchestrator can edit `held-out.yaml` and `.claude/settings.json`. Its write scope is `**`
  (`decide.py:102`), and edits to those two files are exempt from the held-out content rule (`heldout.py:114-122`). The
  EXAMIN CTO could lift its own wall. The brief forbids it, and I compare the file's sha256 at every stage report.
- **P-6: the write wall is partial.**
  - A Bash write whose target the guard cannot work out is allowed (`decide.py:1209`).
  - Writes to the system temp folder are allowed (`decide.py:145-148`).
  - The EXAMIN CTO is started by tmux, not `gov launch`, so it has no OS sandbox.
  - The precondition probes test the writes the guard can read, and W2-42a R3 narrows the gap.
- **P-7:** stage MA must write outside the project (`OUT_INSIDE_PROJECT`, `src/gov/adopt/assess.py:281-284`). Its
  folder is `/home/usain/gov-os-runs/W2-27/ma-out/`, one exception to "write only in the clone", named in the brief.

## (7) W2-81's proving-ground run

- **Status:** `grep -l 'external-ref: W2-81$' .tickets/*.md` gives `.tickets/DAEO-l78m.md`, `status: closed` (11-11).
- Its real run has never happened: the orchestrator's `gov close` in each synthetic repository "on a pinned release
  (W2-16's numbered, frozen release)" (its KPI line 32). `~/gov-os-runs/W2-81/` is empty. The held-out half it reads
  (W2-93) is closed.
- **Does it block W2-27?**
  - By the ticket graph, no: W2-81 is closed, and merged dependencies count as met (DEC-1157). DEC-1167 (3) and
    P-EXAMIN-CTO-1 §2 name only W2-88 and W2-60a as start gates.
  - W2-27's KPI line orders only the release before the run ("before W2-81's proving-ground run and this ticket's
    adoption").
  - But W2-27's body still carries DEC-954 Q1: "starts only when K9's entry criteria are met: … the proving ground
    passed" (`.tickets/DAEO-h4rh.md:130`).
  - That is a conflict only you can settle.
- **Recommendation: (b).** It does not block. I start it on the release right after the re-pin, beside the clone's
  setup, with `w2_81_run.py --pinned-gov ~/.local/bin/gov --sets-root …`. Its result goes to you before W2-28's
  verdict. Option (a) holds the EXAMIN CTO until it passes; my estimate is a day, because its full form needs an
  adopting session per repository. It will very likely hit P-1 at A9 unless (a) of §2 is taken.

## (8) Costs and time

| Step | Who | Time | Cost |
|---|---|---|---|
| W2-100, W2-101 (your CIT-P yes, hand merge, copies ACTs) and W2-42a R3 land | me, the operator | about half a day after your yes (estimate) | in the leads' runs already |
| P-1's fix, if (a) | me, one narrow check | 2 to 4 h (estimate) | one check session, about $3 to $5 |
| Your release, commit and tag | you | about 15 min | nothing |
| My hash-check and record | me | about 30 min | nothing extra |
| The re-pin from the release (dry run, rehearsal, independent review, operator's run) | me, a reviewer, your operator | 2 to 3 h of mine; about 10 min of your operator's | one review session, about $3 to $5 |
| The clone's setup and the session's start | your operator | about 15 min | nothing |
| W2-81's run on the release | me | a few hours to a day (estimate) | its adopting sessions, if run in full |
| The EXAMIN CTO through W2-27 | EXAMIN CTO and workers | about 3 working days | $150 to $300 (P-EXAMIN-CTO-1 §7) |

From your yes on the CIT-Ps to the EXAMIN CTO's start: about one day. A 0.1.1 release later costs your 15 minutes, my
30-minute check and a re-pin window.

## (9) Your lines

1. `yes P-RELEASE-1`: commit point (B), version 0.1.0, your steps and trailers as §4, the re-pin from the release as
   §6. Or name your changes, for example `P-RELEASE-1 commit (A)`.
2. `P-RELEASE-1 P-1 (a)` (fixed before the release) or `(b)` (left for the EXAMIN CTO to find).
3. `P-RELEASE-1 pins (a)`: every re-pin while W2-27 runs is a numbered release cut by you. Or `(b)`: re-pins as today,
   and W2-27's line read as "a release at its start".
4. `P-RELEASE-1 setup (a)`: your operator does the kit install and A0, and the session is started after, so no agent
   runs without the product's hooks. Or `(b)`: the EXAMIN CTO does Part A, then is restarted (DEC-1174 (2)(i) as
   written).
5. `P-RELEASE-1 W2-81 (b)` (it does not block; it runs on the release beside the setup) or `(a)` (it blocks).
6. `yes EXAMIN-CTO-first-brief`, or your changes.
