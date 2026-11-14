# ACT-LANDING-CTO-ROUTE-1: the landing check passes a commit of the CTO's own (b) ACT (DEC-1167 (5))

- **For:** the owner (one yes line), then **the owner's operator, by hand** (class **(O)**, measured: the landing check is the operator's own
  install, §5 of OPERATOR-AGENT-1 and DEC-1104 (4)). About five minutes. The operator agent's queue cannot run it: G6 refuses an (O) bundle.
- **By:** an ACT-preparation helper of the CTO, 2026-11-13 from about 14:30 UTC. **Nothing live was changed or started:** no write under
  `~/gov-os-operator`, no commit, no stage, nothing in the main tree's tracked files, no queue line. Built and rehearsed on fresh clones of
  `w2/integrate` (`79159cd44c5b`) with a planted HOME under `/tmp/claude-1000/acts-landing-rules/`. **Not yet independently reviewed** (section 8).
- **Under:** **DEC-1167 (5)** (the owner, 2026-11-13: "the CTO brings soon the landing check's route for the CTO's (b) ACTs (`Role: orchestrator`
  with `Act:` and the approvals log entry), so they stop needing the owner's operator"); DEC-1104 (2) (the landing check, S16) and (4) (the
  install is the owner's, by hand); CAP-33. Manifest `dec`: "DEC-1167 (5), DEC-1104 (2), (4), CAP-33".
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-landing-cto-route-1/` (`code/landing_check.py` the after, `code/landing_check.py.before`,
  `landing_check.diff`, `code/test_landing_cto_route.py`, `build_landing_act.py`, `apply.sh`, `actkit.py`, `evidence/`). **The bundle:**
  `.gov-runtime/scratch/orchestrator/acts/ACT-LANDING-CTO-ROUTE-1/`.

## 0. The short version, the yes line, and the steps

1. **The change (111 lines added, 2 rewritten, one file):** `landing_check.py` (the operator's install, and its byte-equal source copy under
   `governance/project/operator/`). A commit outside a ticket on a (b) or (O) control path stays a P1 unless it carries `Role: owner`, or `Role:
   operator` with `Act:` (as today). **One route is added:** `Role: orchestrator` with one `Act: <ACT id>` and one `Act-sha: <manifest sha256>`
   passes **when, and only when, all three hold**; anything else stays the P1 it is today, with the refusal named in its reason:
   - **(1) the approvals log:** `log/act-approvals.jsonl` under the CTO's scratch folder holds a line for that ACT with that manifest (`act`, and
     `manifest` or `manifest_sha256`) whose `route` **begins "the CTO"**. The route names the applier: the CTO's lines ("the CTO (class (b), a
     watchers path), the owner's word") pass; the operator agent's own lines (no `route`) and a route such as "the owner's operator agent (class
     (b)), queued by the CTO" do not, though they mention the CTO.
   - **(2) class (b):** the manifest (found under `acts/<ACT>` or `acts/<ACT>.*` by **the sha256 of its bytes**, which must be the `Act-sha:`)
     names that ACT and claims `b`; the classifier's own vote on that bundle (`act_class.classify`) is `b`; and the class of the commit's paths by
     the rule table is `b`, never `O` (a list-shaped row counts at the higher of its `else` and `ratchet_class`, so the path map is `O` and
     `.claude/settings.json` is `b`; a path no row names is `O`).
   - **(3) the paths:** the commit's own change (first parent) is exactly the manifest's `touched` list, every entry of root `repo`.
   The trailers must be exactly one `Role: orchestrator`, one `Act:` (an ACT id) and one `Act-sha:` (64 hex).
2. **Who it is for:** commit `7cc654e49f9b` (ACT-DISPATCH-NIGHTLY-SLOT-1's) lacks `Act:`, so it **stays flagged** (rehearsal F1); the owner
   accepted it by DEC-1167 (5). The same commit made with the trailers passes (rehearsal F3, on the live approvals line and the live bundle,
   read only).
3. **No seam:** the approvals log and the acts folder are two constants in the file (the CTO's scratch folder). No option and no environment
   variable names another (a unit test runs the command line with the variables set and with extra options). The unit tests give the function
   its two folders as arguments.
4. **Class and who applies it: (O), the owner's operator by hand, as ACT-OPERATOR-HOURS-3's Part B.** `act_class.classify` gives (O) for all four
   files: `gov-os-operator/install/landing_check.py`, `install/APPROVED` and `governance/project/operator/landing_check.py` are the
   `operator-own` row (O, control); the new test file is the catch-all (O). The manifest claims `O`; the three votes agree.

**The owner's line, on its own line:**

yes ACT-LANDING-CTO-ROUTE-1 973eba5f

(the first 8 digits of the manifest's sha256 `973eba5fd258ef6293cf37500ff7c2777b5f551ff524a6f8caf6dac6d8fbd9e8`, section 6.)

**The steps** (the owner's operator, in the main tree, not at a :x0 minute when the cron launches, with nothing queued for the operator).
Before step 1 tell the CTO "starting LANDING-1": the CTO writes `log/act-in-progress.txt` and lands nothing on `w2/integrate` until you send
the commit id, so nothing lands between the apply and the commit.
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-LANDING-CTO-ROUTE-1
sha256sum $G/manifest.json    # expect 973eba5fd258ef6293cf37500ff7c2777b5f551ff524a6f8caf6dac6d8fbd9e8
bash $G/apply.sh check        # exit 0: "check: ready to apply (every listed file is the before; ...)"
bash $G/apply.sh apply        # exit 0: four "apply: ..." lines, "the install's own APPROVED check: ok", "APPROVED ef5afbac...", "state applied"
bash $G/apply.sh verify       # exit 0: "verify: every listed file is the after; the install's other files as built"
sha256sum ~/gov-os-operator/install/APPROVED   # expect ef5afbac78f3fce16ab7551ef88987a6898acd8f9a7a18439bf83aeb9216c157
git status --short -- governance/project/operator/landing_check.py tests/unit/operator/test_landing_cto_route.py   # " M" and "??"
git add governance/project/operator/landing_check.py tests/unit/operator/test_landing_cto_route.py
git commit -m "ACT-LANDING-CTO-ROUTE-1: the landing check passes the CTO's (b) ACTs by Role: orchestrator, Act: and Act-sha: (DEC-1167 (5))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1167" --trailer "Role: owner" -- governance/project/operator/landing_check.py tests/unit/operator/test_landing_cto_route.py
```
The commit changes no `tests/acceptance` path, so no path-map exemption entry is needed (HOURS-3's stage 2 does not apply). `apply.sh` refuses
(exit 3 "moved: ...") if any listed file or any other install file is not as built, or the source copy differs from the install's file; exit 6
"busy" if the operator holds a lock, a freeze, a journal or a queued request. After the commit, the CTO removes `log/act-in-progress.txt`.
The next landing (`landing_select.sh --hook`) reads the new file from the install.

**How the CTO then commits a (b) ACT** (not part of this ACT; for the package of each later ACT):
```
git commit -m "..." --trailer "Task: DAEO-sdxk" --trailer "Role: orchestrator" --trailer "Act: ACT-X" --trailer "Act-sha: <the manifest's full sha256>" -- <exactly the manifest's touched paths>
```
after the owner's yes and the CTO's `act-approvals.jsonl` line (`route` beginning "the CTO", the manifest's sha256 under `manifest`).

## 1. What was found (file and line)

- `landing_check.py` (the install's, `a0687ebd`): `check()` flags a first-parent commit that is outside a ticket (`Role: owner`, or no `Task:` but
  `DAEO-sdxk`), is not `Role: owner`, is not `Role: operator` with `Act:`, and touches a `control: true` row's path. `landing_select.sh` runs it
  with `python3 -I <install>/landing_check.py --repo <repo> <old>..<new>` after every landing and files each item as an inbox P1.
- The only difference between today's `Role: orchestrator` ACT commits and the operator's is the missing route, which this ACT adds: the CTO's
  own (b) ACTs (DISPATCH-NIGHTLY-SLOT-1 and the others) are applied by the CTO by hand after the owner's yes, with an approvals line whose
  `route` already says so (`log/act-approvals.jsonl`, three lines of 2026-11-13 13:52).
- `class-rules.yaml` rows: `operator-own` (the install, `governance/project/operator/**`) is class O, control true; so is every file here.

## 2. The change (after minus before)

`drafts/act-landing-cto-route-1/landing_check.diff` (made by `patch_after.py` from the before; no other line of the file changes): the module
docstring's paragraph on the route; the constants `CTO_ORCH`, `APPROVALS`, `ACTS_DIR`, `ACT_ID_RE`, `SHA_RE`; `path_class`, `cto_approved`,
`find_manifest`, `cto_route`; `check()` takes `approvals=None, acts_dir=None` (tests only; the command line passes neither) and, after the
control-path test, tries the route when the commit carries `Role: orchestrator`, `Act:` and `Act-sha:`. A commit that tried the route and failed
is flagged with its reason's text plus "; the CTO's route refuses: <why>". Every other commit's flag and reason are unchanged.

## 3. The unit tests and what they show

`tests/unit/operator/test_landing_cto_route.py` (40 cases, `38899c26546ae0c45c19f05b4f4d23320c2e5c3cc029164726bb0f28c516ea06`): the pass (all three; no `Task:`; several paths; a rebuild folder
`ACT.r1-...` found by the manifest's hash); each condition with only it missing: (1) no log, empty log, another ACT, another manifest, no route,
the operator agent's route, a route that mentions the CTO late, another route, a route that is not text, a malformed line skipped and the good
one counted; the trailers (no `Act-sha`, not a sha, the sha of nothing, two of either, a bad id, another ACT's id); a manifest changed after its
approval; a manifest naming another ACT; a folder that is a link; (2) claims `a`, `O` or nothing, the classifier's vote above (b) (a `sudo` in
`apply.sh`), an ACT on an (O) control path (the operator's own file), an (O) path beside a (b) one, a path map change the classifier reads as a
tightening beside a (b) path (refused by the path class); (3) an extra path, a path short, another path, a touched entry whose root is not the
repository; the pre-existing forms stay flagged with their reasons; the owner and operator routes unchanged; the command line has no seam.
**Rehearsal E:** the tests are red on the before code (39 failed, 1 passed) and green on the after; each of **eight** one-line mutants of the code (a
condition, the route text, the hash match, each of the three checks of (2), the touched-list and the root test) turns them red.

## 4. The rehearsal (`rehearsal.log`, last line `failures: 0`)

Fresh `--no-hardlinks` clone of `w2/integrate` (`79159cd44c5b`), HOME planted with a copy of the live install, `apply.sh` run from the bundle exactly as
the owner will, every pytest through `heavy_slot.sh` with `TMPDIR` under `/tmp/claude-1000/`. A: the bundle. B: check, the manifest's six checks
before (the install, APPROVED, tests, behaviour refuse) and after (all pass), apply, byte for byte, modes (0444 install, 0644 repository), verify,
only the two repository paths changed in the clone and only two install files in the planted install, apply again, undo byte for byte, apply again.
C: ten refusals, each with nothing touched (a changed install file, another install file, a stray file, a queued request, the commit freeze, a
source copy that is not the before, the test file already there, a half-applied state, a launch holding `log/launch.lock`). D: the owner's steps
literally (stage, commit with `Role: owner`, the planted new check raises nothing, undo, undo commit, empty diff, apply again). E: the tests above,
`tests/unit/operator` (509 passed), `tests/acceptance/W2-148` (185 passed). F: **the live example and the history** (the planted install's CLI, as
`landing_select.sh` runs it): `7cc654e49f9b` flagged by new and old; the same commit rebuilt on its parent with the trailers and ACT-DISPATCH-NIGHTLY-SLOT-1's
live approvals line and bundle (read only) passes the new check and is a P1 for the old; a wrong `Act-sha` and a commit with one path more are P1s that
say why; the old and the new check print the same items over the last 300 first-parent commits. G: the operator's `validate_manifest`, `check_act`,
`path_rule` pass; `act_class` gives (O). H: the live install, the source copy, the main tree's status, the live approvals log and the dispatch ACT's
manifest are unchanged.

## 5. Risks

- **The approvals line is the CTO's own.** The route moves the owner's yes from "the operator's G6 found the owner's line in the transcript" to "the
  CTO wrote an approvals line saying so". The check reads the line, the manifest by its hash, the class and the paths; it does not read the
  owner's `yes` line itself. The route is for the paths the owner has already said the CTO may apply (DEC-1167 (5)); a CTO that wrote a false line
  would still need a manifest of class (b) and a commit of exactly its paths. Hardening options are in section 7.
- **A (b) ACT of the CTO whose commit differs in content from the bundle's `after`** passes (the route reads paths, not bytes).
- **A bundle moved or deleted after its commit** makes the check unable to find the manifest; the commit is then a P1, which is the safe side.
- **The classifier vote reads the bundle in the CTO's scratch folder** (apply.sh, the manifest's commands and checks are scanned for `sudo`,
  `git push`, ...): a bundle whose scripts raise it above (b) refuses the route.
- **List-shaped rows:** a (b) ACT that touches `.claude/settings.json` is by path (b) and passes if the rest holds. The path map is (O) by path.
- **Cost:** a commit with `Role: orchestrator`, `Act:` and `Act-sha:` reads one log, lists `acts/`, runs the classifier once. Nothing else.

## 6. Hashes

| file | sha256 |
|---|---|
| `before/repo/governance/project/operator/landing_check.py` (and the install's) | `a0687ebde2365fb2d7b1b63a50cef2c3da94f2d56a4a01eede287e7d9f5afd32` |
| `after/repo/governance/project/operator/landing_check.py` (and the install's) | `fd0b59ede124bdd0913b58542daf6fc5da7fe675f60d1f2e9531d7994bd362cb` |
| `after/repo/tests/unit/operator/test_landing_cto_route.py` | `38899c26546ae0c45c19f05b4f4d23320c2e5c3cc029164726bb0f28c516ea06` |
| `before/home/gov-os-operator/install/APPROVED` | `3744df3a637feadc26c673b88a10cbc757e8c8746aced078d700300906962815` |
| `after/home/gov-os-operator/install/APPROVED` | `ef5afbac78f3fce16ab7551ef88987a6898acd8f9a7a18439bf83aeb9216c157` |
| `apply.sh` | `61478c8de6223962ef7d1f271be806624ea6c73111b2871b351a437f39e27819` |
| `list.txt` | `15274ba01d55096d4217c9c6fd64dda3eb2717b8d4762ddd8d4fe3444ea5951c` |
| `keep.txt` | `6f793b524f4dc0a65e8872c8f74548441e5ff475653fb1a63bb9829ff67e262c` |
| `rehearsal.log` | `ab792221b037064445ee02f9b55b359df8b8b1198ae3040dc948f9b111db4779` |
| `manifest.json` | `973eba5fd258ef6293cf37500ff7c2777b5f551ff524a6f8caf6dac6d8fbd9e8` |

The manifest's `files` hashes the before and after copies, `apply.sh`, `list.txt`, `keep.txt` and `rehearsal.log`; its six `checks` are run after the
apply by the rehearsal (the install's file and APPROVED by sha, the source copy equal to the install's, the test file by sha, APPROVED naming the
file, and a behaviour run: a planted repository, acts folder and approvals line, the commit passes; the line removed, it is flagged).

## 7. Options for the owner (proposed decisions, none taken here)

- **Hardening (a)**: the route also requires each touched path's blob at the commit to hash as the manifest's `after` (the commit is the
  reviewed bytes). Cost: about 8 lines and two cases; the ACT is rebuilt, re-reviewed, re-rehearsed. Benefit: a commit that differs from the
  bundle is a P1.
- **Hardening (b)**: the route reads the owner's `yes <ACT> <sha8>` line in the CTO session's transcript as the operator's G6 does
  (`oc.find_owner_line`). Cost: the check needs the transcript's location and the operator's helper (more code in the owner's file, and a coupling
  to the transcript's form); benefit: the route no longer rests on a line the CTO writes. Not built: DEC-1167 (5) names the approvals log entry.
- **Neither**: apply as built.

## 8. Before the yes

- One independent review (verdict block in `review.md`) under the operator's `reviewer-brief.md`. **Review: not written yet.**
- The CTO tells the owner when the review is in; the owner sends the yes line.

## 9. Undo

`bash $G/apply.sh undo` (same lock, same order, only over the after; the new test file removed, the two copies and APPROVED put back byte for
byte; the install's own APPROVED check ok), then the owner's `git add -A` of the two paths and a commit with `Role: owner`. Rehearsal B and D.
