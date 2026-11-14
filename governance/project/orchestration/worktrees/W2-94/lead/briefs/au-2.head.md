# W2-94 GOLD — the narrow independent check of the change to `check_gold.py`, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; the packet at the end carries its text). You write
nothing in the repository. Your final message is the probe record's body; the lead commits it.

## What you check, and only this (head `19e9739430ba5d9e1a9e01ab071814c161592269` of `w2/W2-94`, worktree `/home/usain/gov-os-worktrees/W2-94`)
The owner decided **W2-94 GOLD (owner, 2026-11-13; to be recorded as DEC-1175, not yet in the register)**: the
counts-only gold check `fixtures/evaluation/examin/check_gold.py` read a question writer's own words too literally; the
set stays unchanged; the check changes in exactly three ways, (i) to (iii) below, and nothing else changes.

- **The change under check:** commit `19e9739430ba5d9e1a9e01ab071814c161592269` by an engineer (session
  `afd71a8e-9188-42a7-b9be-9a3deb5f4ba6`), one file: `git show 19e973943 -- fixtures/evaluation/examin/check_gold.py`
  (37 insertions, 11 deletions; base `6c7772ef6`).
- **The cases it must satisfy:** written first by the independent test designer (commit `133b79626974`, merged at
  `95ac3ec049bb`): `tests/acceptance/W2-94/w2_94_cases.py` (the entries under the "W2-94 GOLD" comment in `S4_HOLDS`,
  `S4_BREAKS`, `S1_DRAW_FORMS`, `S1_DRAW_LITERAL`, `digit-form-k-differs-from-the-first-field`) and their tests in
  `test_w2_94_s4_gold_sources.py` and `test_w2_94_s1_split_form.py`. 29 were red against the unchanged script.
- **The guard cases:** the cases that kept the old behaviour's point and must stay green: every pre-GOLD case of the
  folder (434 green before the change), and the GOLD guard entries (other token kinds unchanged, a token without `/`
  literal only, segments out of order not held, the digit form's `k != k2` refusal, the refused spellings `SEED+K=`,
  `SEED+<k>=`, `SEED+x=`, spaces).

**The three changes, as the GOLD brief states them:**

**(i)** A hyphenated word with a digit is an identifier token (rule 2a) only when it is **id-shaped**: the part before
its first hyphen starts with an upper-case letter and holds only upper-case letters and digits (`DEC-051`, `W2-94`,
`CAP-10`, `X-5`). `level-2`, `top-3`, `Level-2`, `zqxw-9451` are not tokens. The word is judged whole: a hyphen-digit
match that is the tail of a longer word starting with a digit (the `D-3` that `NAMELIKE` finds inside `2D-3`) is not
id-shaped either. Only the hyphen-digit judgement changes; every other token kind (back-quoted pieces, `--flag`s, `_`,
`::`, `/`, camelCase, letters with digits and no hyphen, dotted names) and every other match is unchanged.

**(ii)** A token holding `/` is held when the existing literal rule holds it (substring of the union, or naming a
source's own path), tried first, **or** when its segments (split on `/`, empty segments dropped) occur in order in the
union: each segment found as a substring at or after the end of the previous segment's match. Tokens without `/` stay
literal only.

**(iii)** `DRAW_LINE` also accepts the literal letter `k` in `SEED+k=<value>`; then the k is the line's first field.
The digit form is unchanged, including its `k != k2` check (`DRAW_CATEGORY_MISMATCH`). Every other rule (seed
consistency, parity word, the brief's table, the ids, the parity rule) applies unchanged to both forms. No other
spelling is accepted.

The docstring changes exactly where these three change what it says, and nothing else. The output stays counts and ids
only.

**Questions to answer, each as findings with the two lines below:**
1. Does the diff implement (i), (ii) and (iii) exactly, and nothing beyond them? Name any behaviour the diff changes
   that is outside the three (a token kind other than hyphen-digit, a token without `/` now held by segments, a draw
   rule loosened for the digit form, a spelling other than `SEED+k=` accepted).
2. Could the change make the check **pass a real set it should fail** (fail open): e.g. (ii) holding a path token whose
   segments are scattered through unrelated text of the spans in a way an honest writer's wrong source would hit; (i)
   dropping a real identifier (so an answer's only token vanishes and the prose rule 2b holds it more loosely); (iii)
   letting a malformed line through?
3. Could it **fail a correct real set** that the GOLD change was meant to accept?
4. Does any new output path print text of the set (question, answer, heading, source path, file text)?
5. Do the GOLD cases and the guard cases each fail if their behaviour broke (spot-check by reading, or by running the
   cases on a copy of the script under your `$TMPDIR` with one change reverted)?

You may run the folder on its planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(the lead's run at this head: 463 passed; if the slot tool cannot run in your sandbox, run the same pytest without it
and say so; a resource gate's refusal is a wait).

## Walls (hard)
Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder
named `hidden` outside your `$TMPDIR`, any `fixtures/evaluation/examin/visible` or `hidden` folder of any tree, the
workbench, the owner's EXAMIN copy or EXAMIN's real repository. You need none of them. No GPU, model, network or
installs. One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR` (`/tmp` is
read-only in the sandbox). Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
work around a refusal. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in
different words if the first does not answer.

