# ACT-CLASS-RULES-AGENTS-1: the independent ACT review (round 1)

- task: ACT-CLASS-RULES-AGENTS-1 (Task: DAEO-sdxk)
- status: done, READY on every check (verdict block below)
- work_completed: a fresh read-only review of the bundle against the fixed reviewer's brief (sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a, computed); I re-ran the ACT myself in three fresh clones of w2/integrate (head e437c799c931) with planted HOMEs under /tmp/claude-1000/rev-carag/work
- files_changed: this record only
- evidence: /tmp/claude-1000/rev-carag/rehearse.sh, /tmp/claude-1000/rev-carag/probe2.sh, /tmp/claude-1000/rev-carag/rehearse.out
- tests: no pytest run. The builder's part 4 (654 passed) is not re-run. The bundle changes no code, only one rule-table row
- discoveries: F1 to F3 below. All are rows; none blocks
- risks: the order with ACT-LANDING-CTO-ROUTE-1 (F3)
- lessons: none new
- proposed_decisions: none
- unresolved: none
- recommended_next_action: the CTO copies this record into the bundle as review.md. Then the owner's yes line, as the package's section 6 gives it
- decisions: DEC-1173 (2), DEC-1104 (2) (4), OPERATOR-AGENT-1 §2 §5, DEC-1057, DEC-801, DEC-808, DEC-1010, DEC-1014

I checked the identity first. The manifest.json sha256 is 244d5a399df53418f02e93f97b44222605645260dea20ffe7bc17f1734aadc09, which matches the brief I was given. The main tree head is e437c799c93190b1b414634f1200dda611ae54cc. DEC-1173 (2) is ACCEPTED in docs/DECISION_REGISTER.md and says what the bundle does: one fixed (b) row, `agent-instructions`, class (O), applied by hand with APPROVED's hash line. No superseded or PROPOSED rule is used.

## What I probed and found sound

1. **The touched list and the path rule (check 1).**
   - All 18 bundle files hash as the `files` map says, and no file is unlisted.
   - `touched` equals list.txt, and `alt_base.touched` equals alt/landing/list.txt, row for row.
   - The before copies equal the live bytes today: the tree's class-rules.yaml and the install's copy are both 38ac2f2decce, and the install's APPROVED is 3744df3a637f.
   - The live install's thirteen other files hash as keep.txt says.
   - The after table differs from the before only by the seven lines of the new row, placed straight after `guard-hook`. APPROVED differs only in its class-rules.yaml line.
   - On my planted HOME, `apply` changed exactly the three listed files. The install's two files are 0444, and the tree's file keeps 0644. No temporary file and no `__pycache__` was left.
   - apply.sh and the five checks name no live path, and none runs a bare `cd`, `cd ~` or `cd $HOME`. apply.sh reaches the repository through its own folder (F2). Check 4 runs `cd` into `$HOME/gov-os-operator/install`, which is a subfolder, not HOME itself.
   - The one extra write is the lock file in F1.
2. **The undo (check 2).** On both bases, `undo` put back every touched file byte for byte: hash, mode and listing. The only exception is the lock file in F1. The builder's log shows the same (cases 20, 21, 26, 39, 49 and 51).
3. **The rehearsal (check 3).** The log was written at 19:57, after apply.sh at 19:53. The drafts' apply.sh has the same sha256 (41a83378d91e). build_act.py copies that file into the bundle and runs the copy. The log ends `cases: 91`, `failures: 0`. My own run agrees with every case I repeated: check, verify before, apply, verify, apply again, undo, both bases, both orders, and LANDING's refusal.
4. **The checks (check 4).** I ran the five checks from my clone with the planted HOME:
   - after the apply, every check gave exit 0 and count 1, on today's base and on the LANDING base;
   - on the before, every check gave exit 1 and count 0, so all five are red.

   Check 4 calls the install's own `act_class`. It sends `CLAUDE.md` and `AGENTS.md` to `agent-instructions` (b), the home `~/.claude/CLAUDE.md` to `agents-skills-kernel` (b), and `docs/CLAUDE.md` to `unknown` (O).
5. **The class (check 5).** I ran the live install's `act_class.classify` on the bundle. It gives class O: all three files fall under the row `operator-own`, and there is no script hit. The rule table, APPROVED and the install are the operator's own files, so OPERATOR-AGENT-1 §2 makes this (O) whatever the claim. The ACT claims O, and I find O.
6. **The guard replay (check 6).** This bundle adds nothing to the path map or a deny list, so `replay_refused` is empty.

**The rule's effect, to see whether anything fails open.** The new row matches only the repository's root `CLAUDE.md` and `AGENTS.md`; its globs are whole-path literals. Those two paths rise from the catch-all `unknown` (O, refused at G6) to a governed (b). That is the loosening the owner decided in DEC-1173 (2). Nearby paths keep their classes:
- `CLAUDE.local.md`, `docs/CLAUDE.md` and other names stay (O) under the catch-all;
- the repository's `.claude/CLAUDE.md` stays (b) under `claude-rest`;
- the home `~/.claude/CLAUDE.md` stays (b).

No path falls to (a). `control: true` adds both files to the landing check, which only tightens. The operator's control snapshot and the freeze gate use their own fixed lists, so this row does not move them. The freeze gate in the main tree runs only while `install/act-in-progress.txt` exists, and this hand-applied ACT does not write that file.

**The other refusals.** Run from a copy outside the repository, `check` and `apply` exit 3 and touch nothing (my probe).

**The live state.** After my runs, the live install (every file), the crontab and `git status` of the main tree are unchanged.

## Both orders with ACT-LANDING-CTO-ROUTE-1 (re-run in my clones)

| Order | Result I observed | Matches the package |
|---|---|---|
| LANDING first, then this ACT | LANDING's check, apply and verify exit 0. This ACT's check names "the install after ACT-LANDING-CTO-ROUTE-1"; apply and verify exit 0; APPROVED is 4209aac246a9; landing_check.py is kept (fd0b59ede124); the five checks pass. LANDING's verify then exits 3. LANDING's undo exits 3 too ("moved: … APPROVED"), with nothing touched. This ACT's undo restores the LANDING install byte for byte, and LANDING's undo then restores today's base byte for byte (except F1's lock file). | yes, section 7 row 1 (it says nothing of LANDING's undo, see F3) |
| This ACT first, then LANDING | LANDING's check and apply exit 3 ("moved: home/gov-os-operator/install/APPROVED"), with nothing touched | yes, section 7 row 2 |

## Findings

**F1: an extra lock file in a HOME that has none (check 1).** Run on a HOME with no `gov-os-operator/log/launch.lock`, both `apply` and `undo` create an empty one there, and the undo does not remove it. That file is not in `touched`. On the live HOME the file already exists (0 bytes, dated 2026-11-09), and the script opens it only to append, so its bytes do not change. The builder's own snapshot skips `launch.lock` by name. That is why its case 38 can say "nothing else written".
- Ordinary work: no, because the live lock exists already, and the operator's launcher keeps it there.
- Consequence: other (one empty lock file, no control file touched).
- What would reverse it: a live HOME without `log/launch.lock` when the owner's operator runs the apply. In that case the touched list would not be exact, and this would become a check 1 fail.

**F2: the repository is found from the script's folder, not the cwd (check 1).** apply.sh finds the repository by going five folders up from its own folder; it does not use the cwd that the brief names. Run from a copy anywhere else, it refuses with exit 3 and touches nothing. The package's steps run it from its scratch path, which works. ACT-W2-148-S15-1 did the same.
- Ordinary work: no, because the ACT is (O) and applied by hand from the printed path. No operator dry run copies it.
- Consequence: other (it fails closed).
- What would reverse it: this bundle being handed to the operator agent's dry run, which copies the bundle out of the tree. Then it would refuse rather than rehearse.

**F3: the order with ACT-LANDING-CTO-ROUTE-1 (check 5, the package's section 7).**
- If this ACT is applied first, LANDING's bundle goes stale: it needs a rebuild and a new yes.
- If LANDING is applied first, then this ACT, LANDING's `verify` and also its `undo` refuse with exit 3 until this ACT is undone.

The package states the first case and LANDING's verify. It does not say that LANDING's undo is blocked as well.
- Ordinary work: yes, because the owner's operator may apply the two ACTs in either order.
- Consequence: other (every case refuses with nothing touched; no work is lost and nothing fails open).
- What would reverse it: a LANDING undo, or an apply out of order, that changes a file instead of refusing.

Classification: F1 in scope, ordinary work no, other; F2 in scope, ordinary work no, other; F3 in scope, ordinary work yes, other. None blocks, so there is no round (DEC-1010). All three land as rows.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "2", "verdict": "pass", "findings": []}, {"kpi": "3", "verdict": "pass", "findings": []}, {"kpi": "4", "verdict": "pass", "findings": []}, {"kpi": "5", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "6", "verdict": "pass", "findings": []}], "manifest_sha256": "244d5a399df53418f02e93f97b44222605645260dea20ffe7bc17f1734aadc09", "class": "O", "reviewer": "independent ACT reviewer, Claude Opus 5.5, session 016M9azhexJUKN7Gd8mX5KQp (not the ACT's author)", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-13T20:21:00+00:00", "replay_refused": []}
```
