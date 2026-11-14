# This run's marks audit (independent auditor, session d51ff894-0d36-4511-87bf-05ca51f1a74a)

**Step 0, sandbox check:** passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a109c3397a44b19239a00adfa9472eb0`). `git update-index --refresh` exited 0.
- (b)'s hash-object left one unreferenced loose object in the shared `.git`. That is the only write of this session.
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-q8cl`.
- `ps` check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- `git status --porcelain` is empty at the end. HEAD = 09542040f7c66260cba26e5e62a251cf602da9be.

- task: DAEO-q8cl (W2-130), the independent auditor's check of the follow-up marks (KPI S3)
- status: done. S3 passes on one condition: the DEC-1115 mark is committed in its corrected text (F1).
- work_completed: Checked the 2 marks to be committed against both entries in full. Checked all 8 B pairs and 11 C pairs against both entries and ARCHIVE-SUPERSEDED §A. Read how `gov links` builds a mark (`src/gov/links/check.py:438-489`) and how it tells a pair is marked (`check.py:479` against `src/gov/store/loader.py:214`, which takes the status line, the first line after the heading).
- files_changed: none
- evidence: the register and archive at 09542040f (`git show`); `.gov-runtime/scratch/lead/propose-marks-0954.patch`; `src/gov/links/check.py`, `src/gov/links/patch.py`, `src/gov/store/loader.py`.
- tests: none run; this is a read-only audit. `tests/acceptance/W2-130/` does not exist at 09542040f.
- discoveries: `tests/acceptance/W2-130/` is absent at this head, though the S1/S2/S3/F3 Verify lines point to it.
- risks: if the proposed DEC-1115 text is committed as it stands, the mark points to a part of DEC-1122 that does not exist (F1).
- lessons: `gov links --propose-marks` takes the part named after the *changed* id in the changer's label and puts it after the *changer* id. Elsewhere in the register, `DEC-n (k)` means item k of DEC-n (F1, F2).
- proposed_decisions: none
- unresolved: none
- recommended_next_action: commit the two marks in the corrected texts below; leave all 19 B and C pairs unmarked.

---

Independent auditor, 2026-11-13T22:46:14+00:00, at 09542040f (09542040f7c66260cba26e5e62a251cf602da9be), W2-130 follow-up marks check.

## A. The two marks to be committed

| pair | mark text (proposed) | verdict | the changer's words | the changed entry's words | fate |
|---|---|---|---|---|---|
| DEC-1115 <- DEC-1122 | ` · **Changed by:** DEC-1122 (4)` | **right as a change; the part is wrong as written (F1)** | DEC-1122 status: "**Changes:** DEC-1115 (4) (its 80 % trigger brought forward to now, until the weekly reset)". Item (2): "**Usage (A), from now:** only the lift's critical path runs; the helpers already running finish; everything else waits for the weekly reset (11-15 09:00 Europe/London)." DEC-1122 has only items (1)–(3); there is no item (4). | DEC-1115 (4): "**Standing until the lift:** if the week's usage passes 80 % before the lift, the lift's critical path comes first and work outside it waits for the weekly reset." Its status line already reads "item (4) changed by DEC-1149 (3) …; item (4) spent at the lift, DEC-1164 (7)". | commit as ` · **Changed by:** DEC-1122 (2) (item (4): its 80 % trigger brought forward to now, until the weekly reset)` |
| DEC-026 <- DEC-086 | ` · **Changed by:** DEC-086` | **right**; the part should be named (F2) | DEC-086 status: "**Settles:** DEC-004 measurement, DEC-026 for Wave 1". Decision: "counted deterministically per ticket by the `gov` CLI. The denominator … read from the harness's local session logs by ccusage." The owner's DEC-083 corroborates it: "DEC-026 (as settled by DEC-086)". | DEC-026: "Start with Claude Code OpenTelemetry → local collector → Prometheus → Grafana … **Primary metric:** governance tokens per completed task (DEC-004)." | commit as ` · **Changed by:** DEC-086 (for Wave 1)` |

**Reasons.**
- **DEC-1115 <- DEC-1122:** DEC-1122 (2) amends DEC-1115 (4). It brings forward the trigger ("past 80 %") to now, until the weekly reset. That is a change, not an application.
- **The part in the DEC-1115 mark:** the "(4)" `gov links` copied is DEC-1115's item. The register writes the changer's item after the changer's id, as in "DEC-1149 (3)", "DEC-1164 (7)" and DEC-1053's "DEC-1164 (12) (item (6): …)". So "DEC-1122 (4)" would point to an item DEC-1122 does not have. The corrected text still clears the finding, because `check.py:479` only needs `DEC-1122` on the status line.
- **DEC-026 <- DEC-086:** for Wave 1, DEC-086 settles how DEC-026's primary metric is measured: by `gov` CLI counts plus ccusage, rather than through the OTel stack. That changes what DEC-026 says for Wave 1; it is not just an implementation. The part is the label's own words, "for Wave 1". `gov links` dropped them because its part pattern (`check.py:438`) accepts only a parenthesis or `item|Q|§|part`.

## B. The eight pairs to stay unmarked

| pair | mark text (proposed) | verdict | the changer's words | the changed entry's words | fate |
|---|---|---|---|---|---|
| DEC-853 <- DEC-884 | `DEC-884 (item 4)` | wrong | "**Changes:** … DEC-853 item 4 (the re-pin at a commit holding W2-50's fix): **still holds**, since the combined re-pin's commit holds it." It is also under "**Under:** … DEC-853 item 4". | DEC-853 4: "after W2-59, it reaches the judge with the owner's re-pin, which must be at a commit that holds both." | stays unmarked (DEC-884 confirms it) |
| DEC-1050 <- DEC-1057 | `DEC-1057 (8)` | wrong | "**Under:** … DEC-1050 (8), (9)"; "**Changes:** … DEC-991's `rm` ask (corrected by DEC-1050 (8))". The decision text never names DEC-1050. | DEC-1050 (8): "agents may delete freely (`rm`) without asking …" | stays unmarked (the subject is DEC-991; DEC-1050 is cited as the one that corrects it) |
| DEC-120 <- DEC-173 | `DEC-173` | wrong | DEC-173: "**Extends:** DEC-163 · **Amends:** Charter v5 §6 (install sentence)". It never names DEC-120. | The source is a version-table row inside DEC-120's span: "DEC-172 (… withdraws the settings second line of DEC-120 and DEC-151), DEC-173 (DP-4: …)". | stays unmarked (the row's subject is DEC-172, already marked) |
| DEC-724 <- DEC-860 | `DEC-860` | wrong | DEC-860 is about context: "Never one giant query and never one giant context …". It never names DEC-724. | The source is section 252's preamble: "The owner committed DEC-859 and DEC-860 (`f0680605`) and set a standing rule that replaces DEC-724's …". DEC-724 is already "Changed by … DEC-861". | stays unmarked (the rule is DEC-861's) |
| DEC-056 <- DEC-017 | `DEC-017` | wrong | DEC-017 ("Embedding & reranking models") never names DEC-056. | DEC-056: "Failures: missing ONNX adapter (12, replaced by DEC-017)". | stays unmarked (the subject is the code adapter) |
| DEC-072 <- DEC-064 | `DEC-064` | wrong | DEC-064 ("Full scope, built in waves", 2026-09-29) never names DEC-072. | DEC-072: "Q4 is superseded by DEC-064." | stays unmarked (the subject is S0a's Q4; the changer is older) |
| DEC-162 <- DEC-156 | `DEC-156` | wrong | DEC-156: "**Amends:** DEC-150". It never names DEC-162. | The source is a version-table row in DEC-162's span: "DEC-150 (DP-7 orchestrator standing rights; amended by DEC-156)". | stays unmarked (the subject is DEC-150; the changer is older) |
| DEC-1053 <- DEC-880 | `DEC-880` | wrong | DEC-880 (2026-10-21) never names DEC-1053. | DEC-1053 (2): "`w2/W2-48` (the cache withdrawn by DEC-880) is deleted." | stays unmarked (the subject is W2-48's cache; the changer is older) |

## C. The census pairs no status line names

| pair | mark text | verdict | the changer's words | the changed entry's words | fate |
|---|---|---|---|---|---|
| DEC-454 <- DEC-904 | — | wrong | DEC-904 never names DEC-454. Its "**Changes:**" are DEC-898, DEC-889 item 7, DEC-490, DEC-493, DEC-880 item 2 (b). | Archive §A: "DEC-454: changed by DEC-868, DEC-899 and DEC-908." | stays unmarked |
| DEC-455 <- DEC-904 | — | wrong | DEC-904 never names DEC-455. | Archive: "DEC-455: changed by DEC-868, DEC-899 and DEC-908." | stays unmarked |
| DEC-480 <- DEC-899 | — | wrong | DEC-899 never names DEC-480. Its P-IS-1 to P-IS-7 are ticket and card drafts. | Archive: "DEC-480: changed by DEC-868 and DEC-908." | stays unmarked |
| DEC-480 <- DEC-904 | — | wrong | DEC-904 never names DEC-480. | Same archive line. | stays unmarked |
| DEC-490 <- DEC-868 | — | wrong | DEC-868 never names DEC-490. It is about the pre-close gate. | Archive: "DEC-490: changed by DEC-904." Status: "Changed by: DEC-904 item 6". | stays unmarked |
| DEC-490 <- DEC-899 | — | wrong | DEC-899 never names DEC-490. | Same. | stays unmarked |
| DEC-490 <- DEC-908 | — | wrong | DEC-908 marks "DEC-455's, DEC-480's and DEC-454's status lines", not DEC-490. | Same. | stays unmarked |
| DEC-492 <- DEC-904 | — | wrong | DEC-904 6: "**The superseded expectations, marked under DEC-866:** DEC-492 (marked `17e5c3a9`)". This records an earlier mark. DEC-492 is absent from DEC-904's "**Changes:**". | Archive: "DEC-492: changed by DEC-868 and DEC-899." The status names both. | stays unmarked |
| DEC-492 <- DEC-908 | — | wrong | DEC-908 never names DEC-492. | Same. | stays unmarked |
| DEC-780 <- DEC-775 | — | wrong | DEC-775 (a blocker sweep, spent) never names DEC-780. | DEC-780: "P-W2-31: the blocker sweep (DEC-775) ran W2-53's close on a scratch merge while two leads ran." DEC-780 cites DEC-775 as its cause. | stays unmarked |
| DEC-501 <- DEC-512 | — | wrong | DEC-512: "**Corrects:** DEC-502 (one sentence) · **Refines:** DEC-502, DEC-507". It never names DEC-501. | Archive now: "DEC-501: corrected by DEC-502"; "DEC-502: corrected by DEC-512". DEC-501's status already names DEC-502. | stays unmarked |

None of the B or C pairs is right as a mark.

## Findings

**F1: the proposed DEC-1115 mark names a part of DEC-1122 that does not exist.** `gov links` copies the part that follows the changed id in the changer's label: "DEC-1115 **(4)**". It puts that part after the changer id, giving `DEC-1122 (4)`. Everywhere else in the register, `DEC-n (k)` means item k of DEC-n. DEC-1122 has items (1)–(3); the item that does the change is (2). DEC-853 <- DEC-884 "(item 4)" has the same pattern, but that pair stays unmarked. Committing the corrected text above fixes it. For the tool itself, this is a row.
- Ordinary work: yes, because a lead applying `--propose-marks` output as it stands would commit it.
- Consequence: other (the mark points to the wrong place; nothing fails open and no work is lost).
- Evidence that would reverse it: a register convention or decision saying the part after a changer id is the changed entry's part.

**F2: the proposed DEC-026 mark leaves out its part.** `check.py:438`'s part pattern does not catch "DEC-026 for Wave 1", so the mark loses "for Wave 1". Without it, the mark reads as a change to DEC-026 in every wave. Commit `DEC-086 (for Wave 1)`.
- Ordinary work: yes, because the proposed text would be committed as it stands.
- Consequence: other (the mark is less exact; nothing fails open and no work is lost).
- Evidence that would reverse it: a governing source saying DEC-086's settlement of DEC-026 applies beyond Wave 1.

Classification: two findings, both ordinary work yes and consequence other. Both are fixed by the commit texts above; neither justifies a round (DEC-801, DEC-802).

What I probed and found sound:
- Both marks change their entries, rather than applying or citing them.
- All 19 B and C pairs are wrong as marks. In each, either the changer's text never names the entry, or it names it only as a confirmation, a citation, or someone else's subject.
- The corrected texts still clear `UNMARKED_CHANGE`, because `check.py:479` matches the changer id anywhere on the status line.
- The patch's ten hunks match the ten pairs the brief names.

```verdict
{"head": "09542040f7c66260cba26e5e62a251cf602da9be", "date": "2026-11-13T22:46:14+00:00", "marks": [{"changed": "DEC-1115", "changer": "DEC-1122", "verdict": "right", "commit_as": " · **Changed by:** DEC-1122 (2) (item (4): its 80 % trigger brought forward to now, until the weekly reset)"}, {"changed": "DEC-026", "changer": "DEC-086", "verdict": "right", "commit_as": " · **Changed by:** DEC-086 (for Wave 1)"}], "unmarked": [{"changed": "DEC-853", "changer": "DEC-884", "verdict": "wrong"}, {"changed": "DEC-1050", "changer": "DEC-1057", "verdict": "wrong"}, {"changed": "DEC-120", "changer": "DEC-173", "verdict": "wrong"}, {"changed": "DEC-724", "changer": "DEC-860", "verdict": "wrong"}, {"changed": "DEC-056", "changer": "DEC-017", "verdict": "wrong"}, {"changed": "DEC-072", "changer": "DEC-064", "verdict": "wrong"}, {"changed": "DEC-162", "changer": "DEC-156", "verdict": "wrong"}, {"changed": "DEC-1053", "changer": "DEC-880", "verdict": "wrong"}, {"changed": "DEC-454", "changer": "DEC-904", "verdict": "wrong"}, {"changed": "DEC-455", "changer": "DEC-904", "verdict": "wrong"}, {"changed": "DEC-480", "changer": "DEC-899", "verdict": "wrong"}, {"changed": "DEC-480", "changer": "DEC-904", "verdict": "wrong"}, {"changed": "DEC-490", "changer": "DEC-868", "verdict": "wrong"}, {"changed": "DEC-490", "changer": "DEC-899", "verdict": "wrong"}, {"changed": "DEC-490", "changer": "DEC-908", "verdict": "wrong"}, {"changed": "DEC-492", "changer": "DEC-904", "verdict": "wrong"}, {"changed": "DEC-492", "changer": "DEC-908", "verdict": "wrong"}, {"changed": "DEC-780", "changer": "DEC-775", "verdict": "wrong"}, {"changed": "DEC-501", "changer": "DEC-512", "verdict": "wrong"}], "kpis": [{"kpi": "S3 follow-up marks check", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
