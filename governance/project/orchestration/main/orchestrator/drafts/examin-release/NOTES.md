# NOTES: assumptions I could not check, and the gaps I found (P-RELEASE-1, EXAMIN-CTO-first-brief)

The CTO's helper, 2026-11-14. Paths are relative to `/home/usain/Dynamic-Agentic-Engineering-OS` unless they are
absolute.
- **Read-only, except two things:** two wheel builds in my session scratchpad, plus one export of
  `797495bdfc70:pyproject.toml src`. Nothing was committed, tagged, pushed or installed.
- **Not read:** the evaluation sets root, the workbench and the real EXAMIN repository.
- **One guard refusal**, noted at G-7. I did not retry the same form: a literal revision was decidable, and the export
  then ran.

## Checked (the evidence behind the packages' claims)

- **E-1, the release's wheel is the re-pin's wheel.**
  - Two builds in `gov release`'s own form gave sha256 `04b094fbd587…d7c3`. That form is `git archive <C>
    pyproject.toml src`, then `setuptools.build_meta.build_wheel`, with `SOURCE_DATE_EPOCH` = the commit's time
    (`src/gov/release/__init__.py:125-142`). The commit was `797495bdfc70`, run with the pin's Python.
  - That is the live pin's wheel (`~/.local/share/gov-os/wheels/797495bdfc70/gov-0.1.0-py3-none-any.whl`), which the
    ladder built with `pip wheel --no-build-isolation` from a full export (`REPIN-COMMANDS-W5.sh:132-146`).
  - setuptools is 68.1.2, the system one, both from the system `python3` and from the pin (`--system-site-packages`).
- **E-2, the wheel holds no `template/`.** It holds 191 entries: `gov/**`, `gov/retrieval/retrieve_baseline.yaml` and
  the dist-info (`pyproject.toml:15-19`).
- **E-3, the live pin lacks commands.** It has no `gov adapters` and no `gov wait` (`~/.local/bin/gov adapters --help`
  answers "invalid choice"). The head has both, and `src/gov/release` and `src/gov/lock` are unchanged since
  `797495bdfc70`.
- **E-4, tags and records.** The repository's version-like tags are `v4.1.3-rc1`, `v4.1.4-rc1` and `v4.1.5-rc1`. No
  `docs/releases/<v>/` exists in any ref's history; only the README.
- **E-5, `gov release`'s checks:** the semantic-version form (`release/__init__.py:40-42,161`), the version not already
  known (`:89-113,174-176`), a clean tree including untracked files (`:164`), and HEAD in `refs/heads/w2/integrate`
  (`:168-171`). It never compares the version with `cli_version` (`:182-205`). The caller checks are in
  `src/gov/release/command.py:55-108`.
- **E-6, the guard's commands.** The guard's install rule does not count `pip wheel`, `copier copy` or `python3 -m
  venv` as installs. `pip install` it does (`gov.guard.install.has_install`, run on those strings).
- **E-7, no user-level hooks.** `~/.claude/settings.json` has no `hooks` key (only its keys were listed). So before the
  kit install, a session in the clone runs only EXAMIN's own project settings, with no Gov OS guard.

## Gaps in the product

- **P-1, A9 and the other `parents[3]` reads fail from an installed wheel.** `Path(__file__).resolve().parents[3]`
  stands for the Gov OS repository root (`src/gov/adopt/fabric.py:36`, `src/gov/adopt/memory_sets.py:29`,
  `src/gov/adopt/safety.py:33`). From a wheel it is `<pin>/lib/python3.12` (E-2). As a result:
  - A9's kernel copy refuses with `KERNEL_SOURCE_MISSING` (`fabric.py:154-170`);
  - its standard pool falls back silently (`fabric.py:53-60`);
  - the walls copy is empty (`memory_sets.py:136`);
  - the MEMORY-AUDIT-1 briefs are read from this repository's own overlay path (`memory_sets.py:30`);
  - A0's `.gitleaks.toml` fallback refuses with `TEMPLATE_MISSING` when the project has none
    (`safety.py:44-49`). After `copier copy` it has one (`template/.gitleaks.toml`), so A0 passes;
  - `src/gov/store/loader.py:628` and `src/gov/close/select.py:57` have fallbacks.

  Not run: I did not install the head's wheel to show the refusal (an install), so this rests on reading the code and
  E-2. W2-88b's smoke run (DEC-1176 (2)) will meet the same.
- **P-2, the live pin cannot install the kit.** It cannot run `gov adapters generate` (the hooks into
  `.claude/settings.json`) or `gov wait` (the copy's facts line), per E-3. The re-pin must come first.
- **P-3, A0 installs no hooks.** It writes `.gitleaks.toml`, the `.gov-runtime/` ignore line and the coordination
  ticket and roster key (`src/gov/adopt/stages.py:149-162`, `safety.py:41-60`). The hooks come from the kit:
  - `template/governance/kernel/hooks/`, `template/governance/kernel/settings.json` and `template/.rulesync/hooks.jsonc`;
  - written into `.claude/settings.json` by `gov adapters generate` (`src/gov/adapters/command.py:1-24`).

  DEC-1174 (2)(i) says "right after A0 has installed them" (`docs/DECISION_REGISTER.md:15053`). The brief reads it as
  "after the kit install and A0".
- **P-4, the product cannot wall the sets root's hidden folders.** The `sets_root_hidden` rule (the sets root's hidden
  folders, refused per role) is implemented only in this repository's live hook (`.claude/hooks/pretooluse.py:374-381`).
  `grep -rl sets_root_hidden src/ template/` finds nothing. The only product rule that walls an outside path is
  `governance/project/held-out.yaml` `held_out_paths` (`src/gov/guard/heldout.py:21-55`; `decide.py:1171-1180`). It
  refuses any call whose text holds the path, for every role.
  - The template ships no `held-out.yaml` (`template/governance/project/` holds `close.yaml`, `path-map.yaml` and
    `test-map.yaml`), and nothing in adoption writes one.
  - P-EXAMIN-CTO-1 §6 asked whether the product can declare the held-out root (`P-EXAMIN-CTO-1.md:91-93`). It can, by
    `held-out.yaml`, written by hand. That is not W2-84's rule.
- **P-5, the orchestrator can rewrite its own walls.** Its write scope is `**` (`decide.py:94-102`). Edits to
  `held-out.yaml` and `.claude/settings.json` are exempt from the held-out content rule (`heldout.py:114-122`). I found
  no write rule protecting either file in `decide.py`.
- **P-6, the write wall is partial.**
  - A Bash write whose target the guard cannot work out is allowed (`decide.py:1203-1210`, "if wt is None: return
    allow").
  - Writes to the system temp folder are allowed when the project is not under it (`decide.py:139-148`).
  - The EXAMIN CTO is started by tmux (`P-EXAMIN-CTO-1.md:29-31`), not by `gov launch`, so it has no OS sandbox
    (SANDBOX-1 covers launched workers).
  - So the probes prove only the writes the guard can read.
- **P-7, stage MA must write outside the project** (`src/gov/adopt/assess.py:98,281-284`, `OUT_INSIDE_PROJECT`;
  `stages.py:76-79`). This conflicts with DEC-1174 (2)'s "write only in the clone". The brief names
  `/home/usain/gov-os-runs/W2-27/ma-out/` as the one exception. gov writes it itself, so the guard never sees it.
- **P-8, an installed `gov` cannot be told apart by its version.** Every installed `gov` reports "gov 0.1.0 (commit
  unknown)" (`src/gov/cli/main.py:196-217`; every pin's wheel is `gov-0.1.0`). Only the wheel's sha256 tells the release
  from older pins.

## Gaps in the process

- **G-1, the README's tag instruction is ambiguous.** It says "tag the release commit" (`docs/releases/README.md:23`).
  The manifest's `commit` is the built commit, the record's parent (`release/__init__.py:167,204`). But `lock_from`
  needs the tagged tree to hold `docs/releases/<v>/` (`release/__init__.py:307-309`). So the tag goes on the record
  commit, and P-RELEASE-1 §4 step 6 says so.
- **G-2, the owner's release commit has no stated trailer form.** No rule or README names it.
  - `Task: decision-record` is measured only for governance-record paths (`src/gov/close/gates.py:27-31,144-157`), and
    `docs/releases/` is not one.
  - The landing check passes any `Role: owner` (`governance/project/operator/landing_check.py:8-13,60-62`).
    `docs/releases/**` falls to the (O) catch-all, which is not a control path
    (`governance/project/operator/class-rules.yaml:1-15`).
  - The proposed form follows the owner's ACT commits (`git log`: `5f13be0ef`, `80d1da428`: `Role: owner`,
    `Task: DAEO-sdxk`, `Implements:`). That is an assumption for the owner to confirm.
- **G-3, does W2-81's run block W2-27?** DEC-954 Q1 says W2-27 "starts only when K9's entry criteria are met: … the
  proving ground passed" (`.tickets/DAEO-h4rh.md:130`). DEC-1167 (3) and P-EXAMIN-CTO-1 §2 name only W2-88 and W2-60a
  (`P-EXAMIN-CTO-1.md:9-15`). W2-81 is closed (`.tickets/DAEO-l78m.md:3`), but its real run "on a pinned release (W2-16's
  numbered, frozen release)" (`:32`) has not happened: `~/gov-os-runs/W2-81/` is empty. The owner settles it.
- **G-4, W2-42a is reopened.** It is in W2-27's deps (`.tickets/DAEO-h4rh.md:63`, `DAEO-03ub`) and `in_progress`
  (reopened at `2b034037a`). P-EXAMIN-CTO-1 §2 counted it as met (`:12`).
- **G-5, P-EXAMIN-CTO-1 is stale in two places.**
  - It names W2-102's release skill (`P-EXAMIN-CTO-1.md:20-22`), which DEC-1083 retired; W2-102 is closed
    (`.tickets/DAEO-rpfv.md`).
  - Its §5 and §6 paths (`/home/usain/gov-os-runs/W2-27/FINDINGS.md`, reports/, evidence/; `:62-67,82-83`) are
    overtaken by DEC-1174 (2).
- **G-6, the replies file.** P-EXAMIN-CTO-1 put it at `/home/usain/gov-os-runs/W2-00/examin-replies.md` (`:76`). Under
  the product rule, the CTO has no own folder there:
  - `DAEO-sdxk` is `status: open`, not `in_progress` (`src/gov/guard/runs.py:132`);
  - `~/gov-os-runs/W2-00/` has no `.gov-os-repository` marker (`runs.py:76-93`).

  Whether the live hook lets the CTO write there is unverified. So the brief uses this repository's scratch,
  `.gov-runtime/scratch/orchestrator/examin/REPLIES.md`:
  - the CTO can write it (`decide.py:139-144`, the scratch rule; it is gitignored by `.gitignore:18`);
  - the EXAMIN CTO can read it (reads are open, DEC-820; nothing in `held-out.yaml` names it).

  The cost: the EXAMIN CTO reads one file of this repository. The brief forbids reading anything else here.
- **G-7, the guard refuses git revisions held in shell variables.** In this session, `git archive $C …` with
  `C=797495bdfc70…` set in the same line was refused: "guard (DEC-953): could not decide: git cannot say whether a
  revision holds the hidden part" (`src/gov/guard/reads.py:126`). The same command with the literal id was allowed. The
  CTO's hash-check commands therefore use literal revisions.
- **G-8, the clone's `origin` remote names the workbench.** A clone of the workbench copy keeps `origin` pointing at
  it, and `git fetch` would read the workbench (DEC-723). The operator removes the remote (P-RELEASE-1 §6, step 2).
- **G-9, Copier may hit EXAMIN's existing files.** Copier 9.18.2 asks before overwriting an existing file, and a Claude
  Bash call has no terminal. The template writes `.gitignore`, `.gitleaks.toml`, `.github/`, `.rulesync/`, `openspec/`,
  `lefthook.yml` and `governance/` (`ls template`). The brief uses `--pretend`, then `--skip` per existing path, and
  never `--overwrite` or `--force`. Whether skipping EXAMIN's own `.gitignore` or `.github/` leaves the kit whole is
  unverified: A0 adds the `.gov-runtime/` line itself (`safety.py:50-60`).
- **G-10, always pass `--vcs-ref`.** Without it, Copier takes the latest tag by PEP 440 and skips prereleases by
  default. `-g` would select `v4.1.5-rc1`, which has no record, and `lock_from` would refuse it
  (`release/__init__.py:307-309`).
- **G-11, one pin serves the whole machine.** `~/.local/bin/gov` serves this repository and the copy's hooks
  (`template/governance/kernel/settings.json:13`, `template/.rulesync/hooks.jsonc:7`). So a later re-pin moves EXAMIN
  off the release (RL-2, P-RELEASE-1 §6).
- **G-12, the ladder installs from a commit, not from a release.** It never reads a manifest or a tag
  (`.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-W5.sh:30-33,132-146`). Its frozen-src rule ties the re-pin to
  "no src change after the release" (`governance/project/orchestration/packages/ACT-REPIN-W5.md:12-17`). That is RL-1
  and RL-3.
- **G-13, no `docs/plan/wave-2/examin-copy/` yet.** The release-check record is its first file.

## Assumptions I could not verify

- **A-1:** `gov release` passes its ancestry check in the owner's WSL terminal: `/proc` readable up to PID 1
  (`src/gov/release/command.py:70-75`). It has never been run for real: no record exists.
- **A-2:** `copier copy --vcs-ref v0.1.0` from the local repository path checks out the tag in a temporary clone, and
  `_copier_conf.src_path` is that clone, so `lock_from` sees `docs/releases/0.1.0/` (`copier.yml:13-14`).
- **A-3:** Copier records `_commit: v0.1.0` in `.copier-answers.yml` when the checkout is at the tag, using
  `git describe --tags`. `lock_from` reads that value as the version (`release/__init__.py:295-309`). The annotated
  tag is proposed so either describe form finds it.
- **A-4:** a Claude Code Write tool call creates missing parent folders. That is why the brief's Write-tool probes name
  only `~/.claude` and `~/.local`, and the probes of this repository, the workbench and the real EXAMIN repository use
  shell redirects, which never create a folder.
- **A-5:** the product guard's refusal texts in the clone are "the call names a held-out path" (`decide.py:1180`) and
  "Bash write to '<path>' denied for role 'orchestrator'" (`decide.py:1251-1253`), as at the head. The release code
  could differ from the head if W2-42a R3 changes them.
- **A-6, the time estimates.** "About half a day" for W2-42a R3, "2 to 4 h" for P-1's fix and "a few hours to a day"
  for W2-81's run are estimates. The $3 to $5 review figure follows DEC-1176 (3)'s auditor estimate
  (`docs/DECISION_REGISTER.md`, DEC-1176 (3)(a)). The EXAMIN CTO's $150 to $300 is P-EXAMIN-CTO-1 §7 (`:96-100`).
- **A-7:** W2-100's and W2-101's template additions are about 70 files (`git diff --stat
  w2/integrate...w2/W2-100 -- template`: 40 files; `...w2/W2-101 -- template`: 30). The final count is after their hand
  merge.
- **A-8:** `gov launch` can start an independent auditor in the clone for the A5, A7 and A10 verdicts. DEC-1176 (3)
  describes the verdict, not who launches it in an adopted project. If it cannot, the brief makes that a finding.
- **A-9:** the EXAMIN CTO's `GOV_ROLE=orchestrator` without a `GOV_TICKET` still gets the orchestrator's `**` scope
  (`decide.py:94-102`). The CTO install rule then refuses installs, because there is no coordination ticket
  (`src/gov/guard/install.py:324`), which is the intent.
