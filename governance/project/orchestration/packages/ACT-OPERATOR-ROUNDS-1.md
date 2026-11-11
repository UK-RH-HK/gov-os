# ACT-OPERATOR-ROUNDS-1: a failed KPI line blocks READY; the two-round cap counts per ACT id (DEC-1131 (3))

- **For:** the owner, by hand, as the message in section 5 (the operator's own files, class (O), like ACT-OPERATOR-1 and -2).
  About two minutes. Nothing is committed by the script; the owner commits the five repository paths.
- **By:** a helper for the CTO (orchestrator DAEO-sdxk), 2026-11-11, Sonnet high, C1-class preparation (DEC-1120); round 1
  built it, round 2 is the one fix pass after the independent review's READY WITH FIXES (DEC-1133 (4); section 8). Built and
  rehearsed in scratch. **Nothing live is changed** until the owner runs section 5. Independent review: round 1 READY WITH FIXES; **round 2 (the last) READY** (2026-11-11 16:33 UTC, manifest.sha256 `79c95ff3`, `reviews/ACT-OPERATOR-ROUNDS-1-review-r2.md`; R2-F1..F3 rows, no further round).
- **Under:** DEC-1131 (3) (the two code gaps fixed now, each by its usual route); DEC-1010 (changed by DEC-1131);
  DEC1010-REVIEW 2.4 (1) and 4.2; DEC-1104 (4) (the operator's own install is the owner's, by hand); DEC-1057 (rehearsed).
- **Class: (O).** `class-rules.yaml`'s `operator-own` row (`governance/project/operator/**` and `gov-os-operator/**`):
  class (O), control, the owner's. The operator agent cannot apply it (rule 2d; APPROVED). No queue request, no yes line.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds/` (section 4).

## 1. What and why
1. **`verdict.py`: READY needs no KPI line marked fail.** Today a record is READY when no finding blocks, even if a KPI
   line is marked `fail` (lines 11-12 of the file, its docstring, said so on purpose: the moderator's triage). The ACT reviewer's brief
   says the opposite (`reviewer-brief.md` line 46) and the operator's G4 already refuses a non-pass line, so tickets and ACTs
   disagreed. Now a line marked `fail` blocks on its own; a line whose verdict is neither `pass` nor `fail` (missing,
   `partial`, `PASS`) blocks too, fail closed, as every other unknown value in this file already does.
2. **`operator_run.py`: the cap counts per ACT id.** G4 counted the verdict blocks in one `review.md`. Each rebuild of an ACT
   has a new manifest sha, a new frozen copy `acts/<ACT>-<sha12>/` and a new `review.md`, so the count restarted. Now
   `Run.act_rounds()` adds the blocks of the review record of every other frozen copy of the same ACT id (folder named
   `<ACT>-<12 hex>`, its `manifest.json` naming that `act`). A block a later record carries forward counts once (compared by
   text; a text counts as many times as the record holding it most often holds it). Three or more refuses at G4 with the
   count and "to the owner", and the P1 is pushed as before. The G4 log line keeps `rounds` (this record) and adds `act_rounds`.
3. **`operator_run.py`: G1 refuses a manifest whose `act` is missing or is not the requested id** (review round 1, P1-F1).
   Nothing required that field, and a build whose manifest left it out, or named another id, was silently dropped from the
   count: the reset this ACT closes. Fail closed was chosen over counting by the folder name alone: the folder name is built
   from the request, so the check also catches a request made under the wrong id, the frozen copy then always names the
   id its folder carries, and the count reads one field the operator has checked, not two that may differ. The reuse path
   (a second request for a sha already frozen) makes the same check. Cost: a bundle without `act` is refused, once, at G1; all
   13 bundles under scratch and the six frozen copies carry it, and the kit and the unit tests build every manifest with it.

## 2. What it changes for each caller (found by search, all of them)
| Caller | Before | After |
|---|---|---|
| `operator_run.py` G4 (the install's `verdict.py`, loaded by `load_verdict`) | `ready()` ignored a fail line; a later check ("a KPI is not marked pass") refused it | `ready()` refuses first: "not READY by verdict.py: K7: the KPI line is marked fail". The later check stays (second wall). Gate G4 either way; W2-148's test `test_g4_a_fail_without_a_blocking_finding_refuses` still passes |
| the CTO's `tools/land.py` (line 155) and `tools/close_build.py` (line 532), through `tools/verdict.py` | a FULL ticket's probe record passed on no blocking finding | passes only with no KPI line marked fail. A record with no verdict block keeps the old text reading |
| `tools/test_verdict.py` (the CTO's tests) | one case expected a fail line READY | that case now uses a pass line; one case reads `any(...)`; three new cases (below) |
| `operator_run.py` G1 (new check, `check_act`) | a manifest with no `act`, or another id, passed G1 (and was then not counted at G4) | refused at G1: "the manifest names no act ..." or "the manifest names act 'X', not the requested Y"; nothing is frozen, nothing applied. Every manifest the kit and the tests build carries `act` |
| the install's pin (`test_w2_148_parts.py:187`; acceptance `w2_148_support.py:39`, S4's `test_s4_the_install_pins_verdict_py_byte_for_byte`) | `277c8ca9f06c...` | `30214f3de29d...` (both edited in the package) |
| the reviewers' briefs, `JUDGEMENT.md`, the ticket template | no code reads `verdict.py` there | no change. They say what a reviewer writes; the code decides |

**Historical records.** `scan_history.py` over the committed records with a verdict block (57 on today's head; 54 when built;
rerun by `rehearse.sh`, hidden and memory-verdict paths excluded by git's own pathspec): the same **3** are READY today with
a KPI marked fail in the last block and would not be after: `docs/probes/DAEO-jpr0/PR-DAEO-jpr0.md` (success-7),
`governance/project/orchestration/reviews/w2-128-r1.md` (F7), `.../w2-153-r1.md` (S5). Reading "neither pass nor fail" as
a block adds none. W2-128 and W2-153 are tickets in flight; if a close or a landing reads a round-1 record like these, it
now needs the round-2 record (or the owner's call). DAEO-jpr0's record is a closed ticket's.

**The live operator, real data (read only; `real_replay.log`).** The six frozen copies in `~/gov-os-operator/acts/` read
`act_rounds` 1,1,1,1,2,1 (DEADMAN-WAKE-1 has two blocks in one build): all still READY, none near three. ACT-CLAUDE-COPIES-3
shows two G4 passes on one sha (a re-request of the same build): not counted twice (the build's own folder is skipped).

**A limit to know.** `act_rounds` sees only ACTs that were run through the operator (G1 freezes the bundle). ACT-W2-149-INSTALL-1's
four builds were reviewed before any queue request (the operator log has no line for it), and the owner-by-hand ACTs (class O,
like this one) never reach G4. For those the count is the CTO's ledger (DEC-1131 (1)), not this code. Also: a frozen copy with
an unreadable `manifest.json` or `review.md` counts nothing; the cap is then no looser than today's. The count is **per exact ACT
id**: the CTO's ids carry a number (ACT-CLAUDE-COPIES-1/-2/-3, ACT-EFFORT-HIGH-1/-2), so a rebuild filed under the next number
starts at zero. And the code counts verdict **blocks**, not rounds as DEC-1131 (2) defines them, so a re-review of a blocking-only
fix counts as a round: stricter, and it fails closed. For both the hand ledger (DEC-1131 (1)) is the count (section 7).

## 3. The two diffs (exact)
`verdict.py` (the CTO's `tools/verdict.py` gets the same file, byte for byte: `30214f3de29d...`) and `operator_run.py`
(`fe2e2f424616...` to `037208586796...`; `import collections` is the only other line outside `check_act`, its two calls and `act_rounds`):
```diff
    --- before/verdict.py	2026-11-11 15:12:39.275307646 +0000
    +++ after/verdict.py	2026-11-11 15:13:41.782721874 +0000
    @@ -7,7 +7,8 @@
     ready(text) returns (True|False, reasons) for a record with such a block, or (None, []) when it has none (the caller
     then keeps its older reading). A finding blocks when it is in scope, reachable in ordinary work and fails open or loses
     work; a malformed block, an unknown value or a finding missing a field blocks (fail closed). A KPI line marked fail
    -with no blocking finding does not block on its own: the moderator's triage put its findings out of the round."""
    +blocks on its own, whatever its findings (DEC-1131 (3): one bar, READY is judged against the KPI lines); a KPI line
    +whose verdict is neither pass nor fail blocks (fail closed)."""
     import json
     import re
     
    @@ -29,6 +30,10 @@
             return False, ["the verdict block is not the structured form (fail closed)"]
         reasons = []
         for k in kpis:
    +        if isinstance(k, dict) and k.get("verdict") == "fail":
    +            reasons.append(f"{k.get('kpi')}: the KPI line is marked fail")
    +        elif isinstance(k, dict) and k.get("verdict") != "pass":
    +            reasons.append(f"{k.get('kpi')}: the KPI line's verdict is neither pass nor fail (fail closed)")
             for f in (k.get("findings") or []) if isinstance(k, dict) else [None]:
                 if not isinstance(f, dict) or f.get("scope") not in SCOPES or f.get("ordinary_work") not in ORDINARY \
                         or f.get("consequence") not in CONSEQ:
    --- before/operator_run.py	2026-11-11 15:12:39.275348365 +0000
    +++ after/operator_run.py	2026-11-11 16:06:15.861949034 +0000
    @@ -23,6 +23,7 @@
     The result is the last line of stdout, one JSON object; exit 0 when applied, undone (the undo step) or digested.
     The undo step and the journal's recovery that leave a file not the ACT's own say "refused" and exit 1 (DEC-1107).
     """
    +import collections
     import hashlib
     import json
     import os
    @@ -84,6 +85,17 @@
             return False
     
     
    +def check_act(m, act):
    +    """G1 (DEC-1131 (3), review P1-F1): the manifest names the ACT it is requested under. Fails closed: act_rounds counts the
    +    earlier builds of an ACT id by this field, so a manifest that leaves it out or names another id would drop its build
    +    from the count and bring back the reset DEC-1131 (3) closes. Raises Refused at G1."""
    +    named = m.get("act") if isinstance(m, dict) else None
    +    if not isinstance(named, str) or not named:
    +        raise oc.Refused("G1", f"the manifest names no act (its \"act\" must be the requested id {act}); DEC-1131 (3)")
    +    if named != act:
    +        raise oc.Refused("G1", f"the manifest names act {named!r}, not the requested {act}; DEC-1131 (3)")
    +
    +
     def validate_manifest(m):
         """The manifest's form (the interface's fields); raises ValueError on anything else."""
         if not isinstance(m, dict):
    @@ -275,6 +287,7 @@
                     validate_manifest(m)
                 except (ValueError, UnicodeDecodeError) as exc:
                     raise oc.Refused("G1", f"the manifest is malformed: {exc}")
    +            check_act(m, self.act)
                 listed = dict(m["files"])
                 found = set()
                 for top, dirs, files in os.walk(tmp):
    @@ -321,6 +334,7 @@
                 validate_manifest(m)
             except (OSError, ValueError, UnicodeDecodeError):
                 raise oc.Refused("G1", "the existing frozen copy's manifest cannot be read: changed after review")
    +        check_act(m, self.act)
             self.msha = oc.sha256_bytes(raw)
             if self.msha != self.sha:
                 raise oc.Refused("G1", "the existing frozen copy's manifest is not the requested sha: changed after review")
    @@ -435,6 +449,35 @@
             self.line("G3", "pass")
     
         # ---------------------------------------------------------------------------------------------------------- G4
    +    def act_rounds(self, vmod, blocks):
    +        """The review rounds of this ACT id (DEC-1131 (3)): the verdict blocks of this build's review record and of the
    +        review record in every other frozen copy of the same ACT id (acts/<id>-<sha12>/, its manifest naming this id;
    +        G1 refuses a manifest that does not, so every copy frozen under this code does), so a rebuild does not reset the
    +        count. A block that a later record carries forward counts once: blocks are
    +        compared by their text, and a text counts as many times as the record holding it most often holds it. A copy
    +        without a readable review record counts nothing (this build's own record is read as before)."""
    +        total = collections.Counter(blocks)
    +        acts = os.path.join(self.s["operator_root"], "acts")
    +        pat = re.compile(r"^" + re.escape(self.act) + r"-[0-9a-f]{12}$")
    +        try:
    +            names = sorted(os.listdir(acts))
    +        except OSError:
    +            names = []
    +        for n in names:
    +            d = os.path.join(acts, n)
    +            if not pat.match(n) or os.path.abspath(d) == os.path.abspath(self.frozen) or os.path.islink(d):
    +                continue
    +            try:
    +                with open(os.path.join(d, "manifest.json"), encoding="utf-8") as f:
    +                    if json.load(f).get("act") != self.act:
    +                        continue
    +                with open(os.path.join(d, "review.md"), encoding="utf-8") as f:
    +                    for t, c in collections.Counter(vmod.BLOCK.findall(f.read())).items():
    +                        total[t] = max(total[t], c)
    +            except (OSError, ValueError, UnicodeDecodeError, AttributeError):
    +                continue
    +        return sum(total.values())
    +
         def g4(self):
             vmod = load_verdict()
             p = os.path.join(self.frozen, "review.md")
    @@ -447,10 +490,12 @@
             blocks = vmod.BLOCK.findall(text)
             if not blocks:
                 raise oc.Refused("G4", "the review record holds no verdict block")
    -        if len(blocks) >= 3:
    +        rounds = self.act_rounds(vmod, blocks)
    +        if rounds >= 3:
                 oc.notify(self.s, self.act, "P1", "to-owner",
                           f"{self.act}: a third review round; refused, to the owner", manifest_sha256=self.sha)
    -            raise oc.Refused("G4", f"a third review round ({len(blocks)} verdict blocks): to the owner")
    +            raise oc.Refused("G4", f"a third review round ({rounds} verdict blocks across this ACT's builds, "
    +                                   f"{len(blocks)} in this one; DEC-1131 (3)): to the owner")
             try:
                 v = json.loads(blocks[-1])
                 assert isinstance(v, dict)
    @@ -487,7 +532,7 @@
             if not isinstance(rr, list) or not all(isinstance(x, (str, int)) for x in rr):
                 raise oc.Refused("G4", "replay_refused is not a list of call ids")
             self.verdict = dict(v, _time=rtime, replay_refused=[str(x) for x in rr])
    -        self.line("G4", "pass", rounds=len(blocks), review_sha256=self.review_sha)
    +        self.line("G4", "pass", rounds=len(blocks), act_rounds=rounds, review_sha256=self.review_sha)
     
         # ---------------------------------------------------------------------------------------------------------- G5
         def g5(self):
```
(The file diffs are in `verdict.diff` and `operator_run.diff` in the drafts folder.)

## 4. The files (drafts, checked by hash before they apply)
| File | sha256 (first 12) |
|---|---|
| `code/governance/project/operator/verdict.py` (also the CTO's `after/cto-verdict.py`) | `30214f3de29d` (was `277c8ca9f06c`) |
| `code/governance/project/operator/operator_run.py` | `037208586796` (was `fe2e2f424616`) |
| `code/tests/unit/operator/test_w2_148_parts.py` (the pin) | `bca1d3c5e0e2` (was `051eec8a3f22`) |
| `code/tests/acceptance/W2-148/w2_148_support.py` (the pin) | `247996d86290` (was `b4302cf7aea3`) |
| `code/tests/unit/operator/test_dec1131_rounds.py` (new, 17 cases) | `7e73c8683688` |
| `after/cto-test_verdict.py` (the CTO's tools test, for the CTO) | `914f05c4918c` |
| `apply.sh`: check, apply, undo | `13e4eba77334` |
| `rehearse.sh`, `rehearsal.log` | `599b4183de98`, `3f30a3b45328` |
| `manifest.sha256` (every file of this folder but itself, this package file and tmp/; this package has no manifest.json: class (O), by hand) | `79c95ff36618` (this file's own hash is in the CTO's return) |

**What changes where, and in what order** (`apply.sh apply`; the running operator sees only step 2):
1. **The main tree (source, for the owner's commit):** the two code files, the two pins, the new test file. The operator
   reads none of them, so nothing running sees step 1. It stops first if any of the five is not as built (the CTO rebuilds).
2. **`~/gov-os-operator/install/`:** takes `log/launch.lock`, then `verdict.py` and `operator_run.py` (a new file beside each,
   made by `mktemp` in the same folder, 0444, renamed over), then **`APPROVED` last** (sha256sum's form over every install file
   but itself). The cron's launcher does not wait for the lock: it checks `APPROVED` first, then tries the lock without waiting.
   A launch in the instant between the code files and `APPROVED` refuses "APPROVED mismatch" once; a launch while the lock is
   held exits "busy"; either way nothing runs half-changed, and the next one (+10 minutes) runs (as ACT-OPERATOR-2 section 8
   item 4): hence not at a :x0 minute. Then the install's own `APPROVED` check runs. The two lines in `APPROVED` change; the
   other twelve are checked unchanged first. `APPROVED` itself:
   `b4a15c8f3b7c...` before, **`97c9a3a5bd22e0bc3546cc12c6c5d9aca8f9f39d145825b6f129b59259895820`** after (printed by apply).
   `reviewer-brief.md` (`e8670330...`) does not change, so every verdict block's `reviewer_brief_sha256` stays valid.
3. **The CTO**, after the owner's commit: copies `after/cto-verdict.py` over `tools/verdict.py` and `after/cto-test_verdict.py`
   over `tools/test_verdict.py` (the CTO's own files, not the operator's; `tools/land.py` and `close_build.py` read the file
   as they do today), and records the apply.

`apply.sh check` and `apply` stop unless: every draft hashes as built; the five repository files are all as built before (or
all after, "already applied"); the install is exactly as ACT-OPERATOR-2 left it (twelve unchanged files by hash, no stray
file, the two old files, `APPROVED` `b4a15c8f...`); no freeze (`install/act-in-progress.txt`), no journal, no failed-undo lock,
no request in `queue/`, no launch running. It backs both sides up with sha256s (`backup/`), and writes nothing else. Every file
it writes goes through a `mktemp` file in the same folder and a rename (no fixed temp name a planted link could use; EXAMIN-SETS-1's
review F4). `undo` checks the install backup **and each repository backup file** against the expected before hashes before it
writes anything (P1-F2), as well as `SHA256SUMS`. If `apply` or `undo` stops after the backup is taken, it prints the hand
restore as the exact `cp -pf` and `rm -f` lines (P1-F3): `undo` itself refuses any state but fully applied.

## 5. The owner's steps: the message
> **ACT-OPERATOR-ROUNDS-1 (DEC-1131 (3)): a failed KPI line blocks READY; the two-round cap counts per ACT id.** The
> operator's own files, by hand. About two minutes. Not at a :x0 minute, and not while a CTO close is running (the main tree
> must be clean until you commit).
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds
> bash $G/apply.sh check      # "state: before (install APPROVED b4a15c8f3b7c)", then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply      # backup; the repository files; the install; APPROVED last; "the install's own APPROVED check: ok"; "state applied"
> sha256sum ~/gov-os-operator/install/APPROVED    # expect 97c9a3a5bd22e0bc3546cc12c6c5d9aca8f9f39d145825b6f129b59259895820
> git status --short          # 4 M and 1 ?? (governance/project/operator/{verdict,operator_run}.py, the two pins, test_dec1131_rounds.py)
> git add governance/project/operator/verdict.py governance/project/operator/operator_run.py tests/unit/operator/test_w2_148_parts.py tests/acceptance/W2-148/w2_148_support.py tests/unit/operator/test_dec1131_rounds.py
> git commit -m "ACT-OPERATOR-ROUNDS-1: a KPI line marked fail blocks READY; the two-round cap counts per ACT id, across its builds (DEC-1131 (3))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1131" --trailer "Role: owner"
> ```
> If `check` stops, send its line to the CTO and apply nothing. If `apply` stops partway, `undo` will refuse (it takes only a
> fully applied state): `apply` prints the hand restore, a few `cp -pf` and `rm -f` lines from `$G/backup/` (checked by its
> `SHA256SUMS`); run those lines, then `bash $G/apply.sh check` must read "state: before"; send the output to the CTO either way.
> **Undo:** `bash $G/apply.sh undo` puts the install and the five repository paths back byte for byte (`APPROVED`
> `b4a15c8f...` again); it refuses while a run, a request or a launch holds the operator. After the commit, undo leaves a
> working-tree diff: `git add` the same five paths and commit "ACT-OPERATOR-ROUNDS-1 undone" with the same three trailers.

## 6. The rehearsal (DEC-1057): `rehearsal.log`, ends `failures: 0`
`bash rehearse.sh > rehearsal.log` (round 2, 2026-11-11 at 16:19 UTC (the log's write time); round 1's log is kept as `rehearsal.round1.log`), as the
owner will run it, only the root substituted: its own `git clone --no-hardlinks` of the main tree's committed head (w2/integrate;
the log names the head), HOME planted under `tmp/` (a copy of the live install), the untracked tools and this folder's `apply.sh` and
`code/` copied in at the same relative paths. **The owner's lines are read from section 5 of this file and run as written**, each with
`bash -c`, its exit logged (this package has no `manifest.json`, so these lines are its checks; EXAMIN-SETS-1's review F1). The plain
`apply` is the one rehearsed (no `ACT_BACKUP_BESIDE`; EXAMIN-SETS-1's review F2). Live files, the live install and the live tree's
status under the three folders that hold the five paths are hashed before and after: unchanged.

| Step | Result |
|---|---|
| `apply.sh` cases | check ready; refused with a request in `queue/`, with the freeze held, with the journal, with a launch holding `launch.lock` (and no `backup/` left), with a repository file moved, with a stray install file; apply (the install's own APPROVED check ok, `97c9a3a5...`); the owner's `sha256sum` line equals the value section 5 says to expect; `git status --short` shows 4 M and 1 `??`; a second apply refused; check "already applied"; no temp file left beside any written file; the installed files byte for byte the repository's; every install file hashes as `APPROVED` says; undo (every install file and `APPROVED` as before, the tree clean); undo again refused |
| Flow B: the owner's whole message, then undo after the commit | apply, the owner's `git add` and `git commit` lines as written (tree clean, trailers present); undo after the commit leaves 5 paths (4 M, 1 D) in the working tree, as section 5 says; the "undone" commit; clean; check ready again |
| Tampered backups (P1-F2) | an install backup altered: refused by `SHA256SUMS`; a repository backup altered together with its `SHA256SUMS`: refused "is not the before file", **nothing written**; mended, undo clean |
| A stop part way (P1-F3) | the repository files written, the install folder not writable: apply stops, prints "stopped part way" and the 7 restore lines; `undo` refuses the state; the printed lines run as printed; the tree clean and check reads "state: before"; every install file as at the start |
| The operator's own unit tests and W2-148's acceptance tests on the applied tree | **420 passed**, nothing deselected (237 unit, 183 acceptance; the clone is a full one, so the two tests that read the repository's history now run). Before this ACT: 220 unit; the 17 new cases are the difference |
| The 17 new cases (`test_dec1131_rounds.py`) on the old code (P1-F5 (a)) | **14 fail, 3 pass** (the fail line READY; the unknown verdict READY; the rebuild resetting the count; `act_rounds` absent; and the four G1 cases, which the old code does not refuse at G1), 3 pass (the cases that need no change); on the new code all 17 pass |
| New (P1-F1): a manifest with `act` absent, null or empty; a manifest naming another id | refused at G1 ("the manifest names no act ..."; "the manifest names act 'ACT-SOMETHING-ELSE', not the requested ACT-RA2"); nothing applied, no frozen copy left |
| New: a verdict with no blocking finding and one KPI `fail` | refused: `ready()` gives `(False, ["K7: the KPI line is marked fail"])`; at G4 "not READY by verdict.py: K7: the KPI line is marked fail" |
| New: the second build of the same ACT id after two reviews | build 1 (two blocks) applied; build 2 (one block): **refused at G4**, "a third review round (3 verdict blocks across this ACT's builds, 1 in this one; DEC-1131 (3)): to the owner"; a P1 `to-owner`; nothing applied |
| New: one review on each of two builds | passes; the G4 lines read `act_rounds` 1 then 2 |
| New: a different ACT id | unaffected (two blocks, applied) |
| New: a record carrying the earlier block forward; the same build asked twice; a lookalike id (`ACT-R8-1` and `ACT-R8`); a folder whose manifest names another ACT | counted once; not counted twice; not counted; not counted |
| The CTO's `tools/test_verdict.py` (P1-F5 (b)) | on the old `verdict.py`: 3 failed, 5 passed; on the new: **8 passed** (the log runs both) |
| Historical scan | 57 records on today's head, the same 3 change reading (P1-F7) |
| Real data, read only | section 2 |

## 7. Residuals
1. **The cap sees only ACTs run through the operator** (section 2). The by-hand owner ACTs and the CTO's scratch builds are
   counted by the CTO's ledger (DEC-1131 (1)), until the counting code of DEC-1131 (1).
2. **A third round is final for the ACT id, and the count is per exact id, in verdict blocks.** The owner's way on is a new ACT id
   (a decision of the owner's); there is no override in the code, as today. But the CTO's ids carry a number
   (ACT-CLAUDE-COPIES-1/-2/-3, ACT-EFFORT-HIGH-1/-2), so a rebuild filed under the next number starts at zero in the code; and the
   code counts verdict blocks, not rounds as DEC-1131 (2) defines them, so a re-review of a blocking-only fix counts as a round
   (stricter; it fails closed). The hand ledger (DEC-1131 (1)) covers both.
3. **Three records change reading** (section 2); the CTO checks the round-2 records of W2-128 and W2-153 before their closes.
4. **The same install carries F1 of ACT-OPERATOR-2's review** (the install's own check writes `install/__pycache__`); not changed here.

## 8. Review
**Round 1** (independent-auditor, claude -p, 2026-11-11 15:55 UTC; `governance/project/orchestration/reviews/ACT-OPERATOR-ROUNDS-1-and-MEMORY-AUDIT-INSTALL-1-review.md`):
READY WITH FIXES, no finding blocking. **Round 2** is the one fix pass (DEC-1133 (4)); what changed per finding:

| Finding | What changed |
|---|---|
| P1-F1 (fails open) | G1 refuses a manifest whose `act` is missing, null, empty or not the requested id (`check_act`, in the fresh and the reuse path); chosen over counting by folder name for the reasons in section 1.3; 4 new cases (missing x3, mismatched) |
| P1-F2 | `undo` checks each repository backup file against its expected before hash before any write; rehearsed with a backup altered together with its `SHA256SUMS` |
| P1-F3 | any stop after the backup prints the hand restore as exact `cp -pf` and `rm -f` lines; `apply`'s old "run undo" text is gone; rehearsed (the printed lines run as printed) |
| P1-F4 | section 4: the launcher does not wait; it refuses "APPROVED mismatch" or exits "busy" |
| P1-F5 | `rehearse.sh` runs and logs the 17 cases on the old code (14 fail, 3 pass) and the CTO's `test_verdict.py` on old (3 failed, 5 passed) and new (8 passed) |
| P1-F6 | section 2 ("a limit to know") and section 7.2: the count is per exact id, in blocks |
| P1-F7 | 57 records on today's head, the same 3 (section 2, rerun in the log) |
| EXAMIN-SETS-1's lessons | the owner's lines run as written with `bash -c` and their exit logged; the plain apply rehearsed; temp files by `mktemp` in the same folder; the rehearsal is a full clone, as the owner's tree is |

The reviewer (a fresh read-only session, under the operator's fixed reviewer brief, not the author) reads `apply.sh`, the two code
files, the new tests and `rehearsal.log`; the CTO gives the bundle. Class vote proposed: (O).

**What it costs:** one directory listing and at most a few small file reads per G4 (the ACT's own frozen copies); the owner's two minutes. No install, no GPU.

**Basis:** question 2 (a failed line never reads as ready; a rebuilt ACT does not reset its review count).
