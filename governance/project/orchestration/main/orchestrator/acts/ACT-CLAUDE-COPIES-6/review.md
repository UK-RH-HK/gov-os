# ACT-CLAUDE-COPIES-6: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session, not the ACT's author. It worked under the operator's fixed reviewer brief (sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`).
- Manifest sha256: `85c9b1c71e07603a1bfeeeeac283079f370c083baa8736c3cc82b9bef6e7d8c8`.
- Reviewed at live HEAD `5bac674cb`, with W2-33 at `9ace61e8ce72`.

task: ACT-CLAUDE-COPIES-6 (W2-33, DAEO-lrre)
decisions: DEC-1156, DEC-1160, DEC-1112, DEC-1109, DEC-315, DEC-1057, DEC-1104, DEC-801, DEC-808, DEC-1010, DEC-1014, CAP-33

Classification: 0 blocking; F1–F5 are rows (not reachable in ordinary work, or consequence other).

## Per check
1. **Touched list, generation and path rule: PASS.**
   - In a clone of integrate `a8b0a9a41` with W2-33 `9ace61e8ce72` merged, the reviewer's own `compose()` and rulesync 24.0.0 run are byte-equal to all 18 `after/` files and to the 8 `template-patch/after/` files.
   - Portability then exits 0 with no findings.
   - The before files are integrate's bytes. W2-33 and the two newer integrate commits touch none of the 26 paths.
   - The kernel role files and the template's orchestrator source equal the owner-approved bytes at `c4b97716164e`.
   - `path_rule`, `validate_manifest` and `check_act` pass when re-run read-only.
2. **Undo: PASS.** In a clone, apply changes 18 files and undo returns the tree clean. The rehearsal shows undo byte for byte, and the commit, undo and commit sequence ends with an empty diff.
3. **Rehearsal: PASS.** It is a real run in clones with a planted HOME and ends with `failures: 0`. Its W1-33 counts are stale against W2-33's current head (F1).
4. **Checks: PASS.**
   - Check 1 covers the 18 targets.
   - Check 2 covers the 9 kernel role files and the 9 template sources. It is red without W2-33's merge or without the CTO's template commit, so G8 refuses an out-of-order run.
   - `apply.sh check` refuses an edited file, a stray file, the wrong working folder and a second apply (exit 3).
5. **Class: PASS, (b).** `act_class` gives the rows `agents-skills-kernel` and `rulesync-other` with no hits. `template/.rulesync/**` is the `unknown` row ((O), `control: false`), so the CTO's template commit outside the bundle is consistent with the class rules.
6. **Guard replay: not applicable.** No path-map or deny entry is added.

**The authored front matter of qa-engineer, senior-engineer and ticket-lead:**
- It follows the existing sources' form: name, targets, a quoted description, and the same eight tools in the same order.
- The skills equal each kernel role file's Skills line, and each skill exists.
- The descriptions summarise each kernel Purpose faithfully.
- No role's front matter carries model or effort. RUBRIC-2's launch lines, including qa-engineer's C0 Haiku low (DEC-1160), reach the agents through the kernel body.

**Sound:**
- before/after hashes, list/manifest/package agreement;
- the refusals by `apply.sh`;
- the fail-closed order through check 2 and G8;
- the new agents are fail-closed at runtime (the guard does not know their roles yet; W2-60b adds them).

## Findings (none blocks)
- **F1** (check 3, scope in): the package and rehearsal were measured at W2-33 `707d23b82932`. W2-33 now stands at `9ace61e8ce72`, which carries run 4's two W1-33 revisions. The package's "two cases still red after the landing" is stale in the safe direction: the reviewer's W1-33 run on the landed tree at `9ace61e8ce72` gave 111 passed, 1 skipped and 0 failed. The 26 files' bytes and check 2 are unaffected.
  - Ordinary work: yes, because a branch moves after its bundle is built.
  - Consequence: other.
  - What would reverse it: any of the 26 bytes, or a kernel role file, differing at merge time.
- **F2** (check 4, scope in): G9 holds the ACT while the CTO's `log/act-in-progress.txt` exists, while a close queue runs, while NIGHTLY-RUNNING is fresh, or from 02:10 to 08:00 without the night hold. The package's step 1, "hold the queue and the nightly", does not name how. Holding by that freeze file, or sitting in the night window, would stall the ACT at G9 (refused at `hold_max_s`). Integrate would then stay in the window state with the queue held. This fails closed.
  - Ordinary work: yes, because that freeze file is the CTO's usual hold.
  - Consequence: other.
  - What would reverse it: `holds()` not reading the CTO's freeze file or the close flag.
- **F3** (check 4, scope out): §2 does not make the owner's yes, and this review being in hand, a precondition of step 2. A late yes or a G7/G8 refusal therefore lengthens the window. Leads' merge-backs of integrate during the window would pull in the half state: red checks, but no lost work.
  - Ordinary work: yes.
  - Consequence: other.
  - What would reverse it: package text that gathers the yes before the merge and holds merge-backs.
- **F4** (authored part, scope out): the new sources list the kernel's full Skills line. The existing sources carry partial lists (engineer 1 of 4, orchestrator 1 of 5). That drift predates this ACT, and the new entries follow the kernel.
  - Ordinary work: yes.
  - Consequence: other.
  - What would reverse it: a decision that front matter carries only a role's primary skill.
- **F5** (check 1, scope out): `apply.sh undo` restores the before bytes without first comparing the live bytes with the after hash. A listed file edited between the apply and the undo would be overwritten. This is the same as ACT-CLAUDE-COPIES-1 to -5, the operator's undo has its own foreign check, and `.claude/**` and `.rulesync/**` are written only by ACTs.
  - Ordinary work: no, because sessions cannot write these paths.
  - Consequence: other.
  - What would reverse it: an operator undo path without its foreign check.

```verdict
{"kpis": [{"kpi": "act-claude-copies-6", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}],
 "manifest_sha256": "85c9b1c71e07603a1bfeeeeac283079f370c083baa8736c3cc82b9bef6e7d8c8",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T01:45:00+00:00",
 "replay_refused": []}
```
