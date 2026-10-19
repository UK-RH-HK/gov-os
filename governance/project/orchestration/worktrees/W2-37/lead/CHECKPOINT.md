# Lead checkpoint: DAEO-6n5k (W2-37, `gov impact`)

The resumed lead wrote this on 2026-10-19, after the owner's DEC-801 to DEC-809.
- **Branch.** `w2/W2-37`, stacked on the held W2-03. `w2/W2-03` is at `9a3e3456`, merged at `4d79565e`.
- **Head.** `2ff873b2c5fa5295f32cfe9299745c0c2b188e54`, the head the last reviewer probed.
- **Commits.** Nothing is committed after it.

## RESUME HERE

**State: PACKAGES, returned to the owner.** The second and last review (DEC-413) failed on A and B, both fail-open cases in ordinary work. There is no third round without the owner.

### Commits since `4d79565e`

| Commit | What | Role and session |
|---|---|---|
| `bb630e54` | acceptance tests | independent-test-designer |
| `cfface91` | CP-0002 | orchestrator |
| `2234049f` | gov impact | engineer, session 95a6e9ea-8399-43d2-a23d-448732a6d6d7 |
| `6b5640b0` | CP-0004, probed by review 1 | orchestrator |
| `59ea2993` | CP-0007, the round boundary | orchestrator |
| `ac4983f8` | test batch for F1, F2, F3, F6 and F8 | independent-test-designer, with Rewrite-Reason |
| `fd9c8f23` | the fixes | engineer, session b658f614-efea-46bf-aeca-1d047c7066b2 |
| `2ff873b2` | CP-0010, the hold; probed by review 2 | orchestrator |

### Reviews

| Review | Session | Probed | Judgement | Draft record |
|---|---|---|---|---|
| 1 | 606bdff7-6e36-41ce-a19e-9dd9357e8407 | `6b5640b0` | fail | `probes/PR-DAEO-6n5k-round-1.md` |
| 2 | 895b39f4-5a54-448f-b934-fbbcfab8803d | `2ff873b2` | fail | `probes/PR-DAEO-6n5k-round-2.md` |

### Round-2 findings (DEC-809 classification)

| Finding | Ordinary work | Consequence |
|---|---|---|
| A | yes | fails open |
| B | yes (narrow) | fails open |
| C | yes | other |
| D | no | fails open, so a row |
| E | yes | other |

The re-probes of F1, F2, F3, F6 and F8 are all sound.

### What is waiting on the owner
- **P-A/B:** A and B. Recommended: option 2, fold them into the held ticket's resume.
- **P-1:** the change skill's routing.
- **P-2:** the depth per radius (W2-L319).
- **P-3, P-5, P-6:** the owner readings.
- **P-4:** the close command's governance prefixes.
- **P-7:** the command lists.
- **DEC-779:** the guard does not see `gov` command writes (F5).

### Verification at `fd9c8f23`
- **W2-37:** 3 failed, the expected P-1 ×2 and P-2; 93 passed.
- **W1-32:** red on `impact`, which is P-7.
- **W1-42:** the 2 accepted reds.
- **W1-05 p95 and W1-46 setup:** load-sensitive; each passed when run alone.
- **Everything else green.** Unit tests: 2179 passed, 1 skipped.
- **gov check:** secrets-indexing is red (UTF-8, from W2-03's test text). context-reproducibility is red (a 60 s timeout, W2-54's).

## For the resume lead (after W2-03 closes)

1. **Merge.** Merge W2-03's closed state and `w2/integrate` into this branch. The merge commits carry `Task: DAEO-6n5k` and `Role: orchestrator`. Never use `-s ours`, and never drop the ticket's side.
2. **Fix round, if the owner takes option 2.** A test batch for A and B (independent-test-designer, Rewrite-Reason), then an engineer.
   - **A:** `--compare` uses the proposal as the store holds it, or refuses to say `matches: true` while the CIT-P file differs from HEAD.
   - **B:** the register named by the path map, differing from HEAD, makes `graphs.record` `stale`, even when HEAD has no entries.
3. **Riding along (DEC-802):**
   - F4: check the `--out` stem against existing ids.
   - C: carry the proposal's `complete` and gaps in the compare result.
   - E: give refusal messages that name the real cause.
4. **Verify and probe.** One full rebuild, every suite again, then a fresh probe of the resumed head with the DEC-801 paragraph in its brief.
5. **Wave 3 rows:** D, F5 and F7.

Loop count: held by the lead (DEC-096).
