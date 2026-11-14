# ACT-GUARD-FIX-5 (round 2): the live hook reads `bash -euo pipefail <<'EOF'` (and every shell with options) as a shell (P1-GUARD-HEREDOC-OPTS-1, option (a))

- **For:** the owner (one yes line); **applied by the owner's operator** (class (b): `.claude/hooks/**` is the `guard-hook` row,
  `act_class.py` gives **b**) after one independent review (round 2's verdict block in `review.md`).
- **Review: not written yet for round 2.** Round 1 FAILED (record: `acts/ACT-GUARD-FIX-5.review-round-1.md`, manifest
  `d2903e7d`, reviewer brief e8670330…): F1 (blocking, fails open), F2 (stray `__pycache__` in the bundle), F3 (check 3 saw only
  the `_kind` mapping), F5 (check 3 wrote bytecode), F6 (stale head and ref); F4 (the unquoted delimiter stays open) is out of
  scope and is closed here too. Section 0 says how each is answered.
- **By:** an ACT-preparation helper of the CTO, 2026-11-13. **Nothing live was changed or started:** no commit, no stage, no
  write to the main tree's tracked files, `.claude/`, `~/gov-os-operator` or any queue. Built and rehearsed on fresh clones of
  `w2/integrate` (head f7b9ff50cbd4 when this round was finished; `refs/heads/w2/W2-42a` at a4afc4166136) under
  `/tmp/claude-1000/agf5-*` (removed at the end); rehearsal A8 re-checks the committed blob on each run.
- **Under:** **DEC-953 (item 2)** (the five-rule hook), **DEC-958** (rules 1 and 5 read what a command writes), **DEC-1050 (12)**
  (G-1: rule 1 judges the writes the guard resolves); each ACCEPTED in the register (G2's own test). The manifest's `dec` is
  those three. **The owner's line that asks for this ACT is "GUARD-HEREDOC (a), no hold on launches" (the owner, 2026-11-13)**;
  it is not in the register under its own DEC id yet, so `dec` does not name it. If the CTO adds that id later, `dec` changes,
  the manifest hash changes and so do the yes line's digits (section 8).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-5/` (`bash_writes.py` the after, `bash_writes.py.before`,
  `bash_writes.py.round1` (round 1's after, kept for the comparison), `bash_writes.diff`, `checks.json`, `build_checks.py`,
  `build_manifest.py`, `rehearse.sh`, `replay5.py`, `cases_probe.py`, `matrix_cases.py`, `f1_round2_cases.json`, `fx_probe.py`,
  `followup-tests.diff`, `rehearsal.log`; the round 1 versions of the scripts, log and manifest end in `.round1`).
  **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-5/` (exactly: `apply.sh`, `list.txt`, `manifest.json`,
  `rehearsal.log`, `followup-tests.diff`, `before/` and `after/` with the one file each).

## 0. The short version, the yes line, who applies it, and what round 2 changes

1. **The defect (P1-GUARD-HEREDOC-OPTS-1):** `_kind` (`.claude/hooks/bash_writes.py:1068-1087`) took every word not starting with
   `-` for a shell's script file. In `bash -euo pipefail <<'EOT'` the word `pipefail` (the value of `-o`) made the heredoc body
   "data", so an engineer's write into `tests/acceptance/` was never judged. Plain `bash <<'EOT'` was refused (MR-3).
2. **Round 1's change, kept:** `_kind`'s shell branch calls a new `_shell_kind(args)`: it skips the value of `-o`, `-O`, `+o`, `+O`
   (any such letter in a short cluster) and of `--rcfile` and `--init-file`; reads `-`, `/dev/stdin`, `/dev/fd/0`,
   `/proc/self/fd/0` as standard input (a shell); reads a shell with an unknown option as a shell; keeps `-c` as data and `-s` as
   shell; and keeps the earlier reading as a floor (`-s` anywhere, or words that all start with `-`, is a shell).
3. **Round 1's F1, the cause (confirmed by rehearsal C):** a shell with options used to be read as *data*, and the data path
   judges an unquoted body's command substitutions and registers a body written to a file the command then runs. Read as a
   *shell*, an unquoted body fell into a branch that made one "unresolvable" finding, which rule 1 drops under G-1 (DEC-1050 (12)),
   and the file registration was skipped. So `bash -o pipefail <<EOF` with `$(touch tests/acceptance/X/zz.py)` in the body, or
   `bash -o pipefail > s.sh <<EOF` / `tee s.sh <<EOF | bash -o pipefail` then `bash s.sh`, went from refused to allowed: 13 of
   round 2's cases (the review counted ten).
4. **Round 2's change (the same file; 60 lines added, 7 removed; two more places beside `_kind`):**
   - `body()`'s shell branch: a **quoted** body, or an **unquoted body with nothing for the shell to expand or join** (no `$`,
     backtick or backslash), is judged as the commands it holds. This closes W2-42a's 15th spelling
     (`bash-eu-o-pipefail-unquoted`) and plain `bash <<EOF` with a literal body.
   - an **unquoted body with an expansion** has its command substitutions judged as commands, exactly as the data path does for
     `cat` (and still yields the one "unresolvable" finding it always did).
   - the **held-body loop** registers a body written to a file for a *shell* reader too (`kind in ("data", "shell")`), so a body
     written to `s.sh` and then run is judged as that file's code, as before round 1.
   `pretooluse.py` and every other line are unchanged (rehearsal A7: every changed block lies in one of those three places).
5. **Stricter only, measured through the whole hook** (section 4): the 45 round 2 cases, a 1,280-call differential matrix, the
   logged refusals and the last 48 hours' shell-heredoc calls: **no call refused before is allowed after**, and the round 1 file is
   looser than before on 13 of the 45 and 63 of the 1,280 (which is what the review found).
6. **Answers to the review:** F1 as above. **F2:** the two `__pycache__` folders are removed; the rehearsal checks the bundle holds
   only its listed files (A10, A11) and no bytecode before and after the run (A10, G3); every rehearsal and probe runs `python3 -B`
   (`PYTHONDONTWRITEBYTECODE=1`) on copies of the frozen files, never in place. **F3:** check 4 (new) runs 20 commands through
   `.claude/hooks/pretooluse.py` itself as an engineer under `tests/acceptance/`, not only the `_kind` mapping. **F5:** every
   check runs `python3 -B -I`. **F6:** head and W2-42a ref refreshed (above). **F4:** closed by the `body()` change.

**The owner's line: `yes ACT-GUARD-FIX-5 ef9078eb`** (the first 8 digits of round 2's manifest sha256, section 7). Round 1's
`d2903e7d` is void.

**Who applies it:** class (b): **the owner's operator**, by its gates (G1 path rule, G2, G3 rehearsal, G4 review, G6 class). By
hand, what the operator runs (the same steps as the rehearsal, from the repository):
```
G=.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-5
bash $G/apply.sh check     # exit 0: "state before (sha256 bb246a21735e)"
bash $G/apply.sh apply     # exit 0: "state applied (sha256 e55c48a3bec6)"
bash $G/apply.sh verify    # exit 0
```
The hook reads `bash_writes.py` at each call: the apply replaces it by `mv`, so a call in flight keeps the module it loaded and the
next call reads the new file. The commit is the operator's (`Role: owner`, as GUARD-FIX-4's was); it names only the one file.

## 1. What was found (file and line)

- `.claude/hooks/bash_writes.py:1081-1086` (`_kind`), feeding the heredoc bodies (`:1217`, `:1528`) and the pipe test (`:1263`).
- `body()` (`:1489-1507`): kind `shell` with a quoted body is judged; any other shell body is one "unresolvable" finding.
- The held-body loop (`:1232`, the `if kind == "data":` that registers the file): only a `data` reader registers a body written to a file.
- The CTO's dry decisions in P1-GUARD-HEREDOC-OPTS-1 reproduce (rehearsal C and H, through the real hook, the pinned interpreter,
  as an engineer): before, 12 of W2-42a's 15 shell spellings are allowed; after, all 15 are refused.

## 2. The change (after minus before)

`drafts/act-guard-fix-5/bash_writes.diff`: `_kind`'s five-line shell branch becomes `return _shell_kind(args)`; three constants
(`_SHELL_FLAGS`, `_SHELL_LONG`, `_SHELL_STDIN`) and `_shell_kind` follow `_kind`, before `_PARAM`; `body()`'s `elif kind == "shell"
and body["quoted"]` becomes the quoted-or-nothing-to-expand test, and its fall-through gains the substitution judgement for a
shell; the held-body loop's `if kind == "data":` becomes `if kind in ("data", "shell"):`.

## 3. The follow-up tests (`followup-tests.diff`, applied by the CTO's route after the apply)

Files it touches: `tests/unit/hooks/test_live_hook.py` (+117) and two new files in `tests/unit/hooks/fixtures/`:
`f1_shell_options.json` (a copy of `tests/acceptance/W2-42a/fixtures/f1_shell_options.json` on `refs/heads/w2/W2-42a`; the
rehearsal checks it byte for byte, D1b) and `f1_round2_cases.json` (the round 2 cases; the rehearsal checks it is the file it ran
in C, D1c). The live hook's own suite is `tests/unit/hooks/test_live_hook.py`; it runs the tree's `.claude/hooks/pretooluse.py`
as Claude Code does. What it adds, all as an engineer writing under `tests/acceptance/` unless a role is named:
- group "a heredoc run by a shell that has options": the F1 spellings (`-euo pipefail`, `-o pipefail`, `+o`, `-O`, `+O`, `--rcfile`,
  `--init-file`, `cat | bash -o pipefail`, `bash -`, `/dev/stdin`, `/dev/fd/0`, `-s`, an unknown option, an unknown letter, plain
  `bash`), plus plain `bash <<EOT` and `bash -euo pipefail <<EOT` with an **unquoted** literal body: all **deny**; the test
  designer through `bash -euo pipefail`: **allow**. 12 are red on the before.
- group "a heredoc that is data for a shell, as before": `bash -c`, `bash script.sh`, `bash -o pipefail script.sh`,
  `--norc script.sh`, `cat <<EOF`, `cat > /tmp/x`, `cat | grep`: **allow**, green before and after.
- `test_a_shell_s_option_values_are_not_its_script`: 42 argument lists against `_kind`.
- `test_w2_42a_f1_spellings_as_an_engineer[<id>]`: W2-42a's 19 ids: the **15** shell spellings deny (the unquoted one too), the 4
  data controls allow.
- `test_round_2_unquoted_bodies_and_files_run_by_a_shell[<id>]`: 45 cases (`f1_round2_cases.json`): 19 forms and their 19 quoted
  twins, all deny, and 7 controls, all allow. The forms: a command substitution or backticks in an unquoted body read by
  `-o pipefail`, `-euo pipefail`, `-O extglob`, `--rcfile`, `--init-file`, `/dev/stdin`, `-`, `sh -eu`, or through `cat | bash -o
  pipefail`; `$(rm -rf tests/acceptance/X)`; a body written to `s.sh` by `bash -o pipefail > s.sh <<EOF` (with and without an
  expansion) or `tee s.sh <<EOF | bash -o pipefail`, then `bash s.sh`; the same with `-euo`; and unquoted literal bodies
  (W2-42a's 15th spelling, `-euo`, `cat | bash -o pipefail`, plain `bash`).

Rehearsal D: before the apply **31 failed, 36 passed** of the 67 new tests (the 12 F1-group cases, the `_kind` table, 12 of W2-42a's
19, 17 of round 2's 45 are red); after, **67 passed**; then `tests/unit/hooks`, `tests/unit/guard/test_w2_141_search.py` and
`tests/acceptance/W2-141/test_w2_141_hook.py` (the suites that import `bash_writes`): **561 passed, 1 skipped**, with
`test_the_logged_refusals_replay_as_decided` run on the CTO's corpus, not skipped.

**Round 2's cases, per id, through the hook as Claude Code runs it, as an engineer (rehearsal C; the round 1 file is the one the
review found looser than before).** `before / round 1 / after`; every row's after is deny.

| form | unquoted | its quoted twin |
|---|---|---|
| subst `-o pipefail` | deny / **allow** / deny | allow / deny / deny |
| subst `-euo pipefail` | deny / **allow** / deny | allow / deny / deny |
| subst `-O extglob` (backticks) | deny / **allow** / deny | allow / deny / deny |
| subst `--rcfile` | deny / **allow** / deny | allow / deny / deny |
| subst `--init-file` | deny / **allow** / deny | allow / deny / deny |
| subst `/dev/stdin` | deny / **allow** / deny | allow / deny / deny |
| subst `bash -` | allow / allow / deny | deny / deny / deny |
| subst `sh -eu` | allow / allow / deny | deny / deny / deny |
| subst `rm -rf` the folder | deny / **allow** / deny | allow / deny / deny |
| subst `cat \| bash -o pipefail` | deny / **allow** / deny | allow / deny / deny |
| file: `bash -o pipefail > s.sh`, then `bash s.sh` | deny / **allow** / deny | deny / deny / deny |
| the same, body with an expansion | deny / **allow** / deny | deny / deny / deny |
| file: `tee s.sh <<EOF \| bash -o pipefail`, then `bash s.sh` | deny / **allow** / deny | deny / deny / deny |
| the same, body with an expansion | deny / **allow** / deny | deny / deny / deny |
| file: `bash -euo pipefail > s.sh`, then `bash s.sh` | deny / **allow** / deny | deny / deny / deny |
| literal body `bash -eu -o pipefail` (W2-42a's 15th) | allow / allow / deny | allow / deny / deny |
| literal body `bash -euo pipefail` | allow / allow / deny | allow / deny / deny |
| literal body `cat \| bash -o pipefail` | allow / allow / deny | allow / deny / deny |
| literal body, plain `bash` | allow / allow / deny | deny / deny / deny |

The 7 controls (`cat <<EOF` with a write-looking body, `cat` with `$(date)`, `bash script.sh`, `bash -o pipefail script.sh`,
`bash -c 'echo hi'`, a shell with options and a harmless body, quoted or not) are allowed before, in round 1 and after.
Bold: refused before, allowed by round 1 (review F1): 13 cases.

**W2-42a's fixture, per id (rehearsal H):** 12 of the 15 shell spellings allowed before, **all 15 refused after** (round 1:
14; the 15th was `bash-eu-o-pipefail-unquoted`); the 4 data controls allowed before and after.

**Copies of the hook in the acceptance fixtures, for the CTO's route:** none of `bash_writes.py`. `git ls-files` and a search of
`tests/`, `src/`, `template/` and `docs/` find it only in `.claude/hooks/bash_writes.py`. The nearest copies, none changed by this
ACT: `docs/changes/W2-141-hook/pretooluse.py` (a staged copy of `pretooluse.py`; W2-141's tests import `bash_writes` from the tree's
`.claude/hooks/`); `.gov-runtime/codeintel/files/.claude/hooks/bash_writes.py` (an untracked index copy); older ACT drafts under
`drafts/act-guard-fix-*`. The product's parser (`src/gov/guard/decide.py`, W2-42a's own F1 fix on `refs/heads/w2/W2-42a`) is a
separate file with the same gap and is not touched.

## 4. The checks and the rehearsal (`rehearsal.log`, last line `failures: 0`)

The manifest's four checks (none names a live HOME or repository path; all `python3 -B -I`): (1) the file parses; (2) the shape
(`_shell_kind` once, called once, `_kind`'s branch is its one call, the stdin words and `--rcfile`/`--init-file` named, no
`subprocess`, `open(`, `os.`, `write` or `import` in the new code, the `body()` and held-body edits present, the order of the
pieces); (3) a behaviour bed: `_kind` on 34 argument lists and the stricter-only run against an inlined copy of the old rule
(2,000 seeded lists); (4) **the whole hook** (review F3): 20 commands through `.claude/hooks/pretooluse.py` as an engineer under
`tests/acceptance/` (quoted and unquoted spellings, substitutions in an unquoted body, a body written to a file and run, plain
`bash <<EOF`, with controls and the test designer allowed), the guard's call log pointed at a temp folder. On the before, checks 2,
3 and 4 exit 1 (B2); on the after, all exit 0 (B9).

`rehearse.sh <bed> <repository> <call set>`, bed under `/tmp/claude-1000/agf5-*`, every pytest through `heavy_slot.sh` with `TMPDIR`
in the bed, `PYTHONDONTWRITEBYTECODE=1`. A. the bundle (hashes; before = committed blob = main tree; the three changed places; no
stray file or bytecode); B. a fresh clone: check, checks before, apply, mode kept, verify, apply again, only `bash_writes.py`
changed, checks after; C. the hook as Claude Code runs it, on the bundle's before and after copies (13 planted cases), then
**round 2's 45 cases before, with round 1's file, and after**, then **a differential matrix of 1,280 calls** (20 heads x 8 bodies x
quoted or not x 2 tails, as an engineer and as an auditor): refused before 308, after 700; **refused before and allowed after: 0**
(round 1's file: 63); 392 newly refused, every one a body that writes into `tests/acceptance/` (or deletes it) or, for the auditor,
into `src/` (touch 82, `echo >` 82, `rm -rf` 82, `$(touch)` 53, backticks 53, `src/gov` 40); a harmless body (`echo hi`,
`echo $(date)`) is never refused; D. the follow-up tests (above); E. undo byte for byte, and apply/undo/verify refuse a changed
file and a link; H. W2-42a's fixture per id; F. the main tree unchanged; **G. the guard replay** (the 87 logged refusals of the
CTO's corpus `corpus4.json`, and the 633 Bash calls with a heredoc and a shell word of the last 48 hours' call set,
`build_replay_calls.py`, 30,146 calls, window 2026-11-11T16:22Z to 2026-11-13T16:22Z): **720 calls, 25 refused before and the same
25 after, 0 refused before and allowed after, 0 newly refused, 0 hook errors**. **`replay_refused` is empty: no call is newly
refused, so there is no write to classify** (the review counted 16 calls of the 48 hours that used the spelling; none wrote into
the tests, and none changes verdict).

**Result: 52 ok, 0 failed; `failures: 0`** (rehearsal.log sha256 `ec894ae7d077ec1aabf8cde7d1accee26ebbba02439d49d3e1ac1f9399be1226`).

The operator's own read-only tools on the bundle: `validate_manifest` pass, `check_act` pass, `path_rule` pass; `act_class.py` gives
**b** (row `guard-hook`, no script hits). No `__pycache__` was written beside the operator's files (`-B`).

## 5. Risks

1. **More refusals than before, for the bodies that write there.** A shell (with or without options) reading an unquoted or quoted
   heredoc body now refuses when the body writes into `tests/acceptance/` (engineer) or outside a reviewer's records (auditor),
   and an unquoted body is no longer let through under G-1 when it has nothing to expand. The matrix shows only such bodies newly
   refused, and no logged call of the last 48 hours changes verdict.
2. **An unquoted body that has an expansion is still one "unresolvable" finding** for the body as a whole (as plain `bash <<EOF`
   with `$VAR` is today): only its command substitutions are judged, so `bash <<EOF` with `$X` naming a path the guard cannot
   resolve stays let through under G-1 (backstops: the landing check, the tripwire). A body with a backslash is treated the same
   way, so a line continuation cannot be used to split a path in a body the guard reads as literal.
3. **A guard-code change on the live path.** About 40 new lines in `_shell_kind` and three small edits; a bug raises, and the hook
   fails closed on any error. Rehearsal D6's 561 tests, check 4 and the matrix pin it.
4. **Unverified, outside this ACT:** `_script_words` (`:1001-1007`) skips only the exact words `-o`, `+o`, `-O`, `+O`, so a cluster
   like `-euo pipefail name` names `pipefail` as the file there; not changed. A heredoc written to a file in the same command and
   run by `bash <name>` was allowed in an earlier probe before and after, even for plain `bash s.sh` (a probe in a scratch
   directory; the cases above, written as the review wrote them, are refused).

## 6. Undo

`bash $G/apply.sh undo` puts the frozen before back byte for byte, only when the file is as this ACT left it (rehearsal E1-E7); then
the operator's revert of the commit. The follow-up tests' red-before cases go red after an undo, so they are reverted with it.

## 7. Hashes

| file | sha256 |
|---|---|
| `before/repo/.claude/hooks/bash_writes.py` | `bb246a21735e70ad0b3a8213102a942bfcf1688838977aae618052c2f1f54732` |
| `after/repo/.claude/hooks/bash_writes.py` | `e55c48a3bec603c44329e85b87d13f817e4af830c6ef6bab47f6758f20c5bfd7` |
| `apply.sh` | `4449e17ad7e49101dc6e9fc634b47e94d968e3df34e8052519ab7607e531cf12` |
| `list.txt` | `52c62bfc8458a542d867bc64445597854e020a4d1f016e97d7e3e343b8b6ebbc` |
| `rehearsal.log` | `ec894ae7d077ec1aabf8cde7d1accee26ebbba02439d49d3e1ac1f9399be1226` |
| `followup-tests.diff` | `6f8ecdb4bea49558471722bcc1dbddc6919837c5a42daa2067a91d7249014d36` |
| `manifest.json` | `ef9078eb4ae59abd01a19e22feb1f8c2e9ddd25d60d13ab1d2e00ef44b1380fd` |

## 8. Before the yes

- One independent review of round 2 (verdict block in `review.md`; **Review: not written yet**), by the operator's
  `reviewer-brief.md`; its `replay_refused` list is empty (section 4 G).
- The owner's line "GUARD-HEREDOC (a), no hold on launches" is named in the text and not in `dec`: if the CTO adds a DEC id for it,
  rebuild with `drafts/act-guard-fix-5/build_manifest.py` (the rehearsal log does not change) and the yes line's digits change.
- The CTO's route for `followup-tests.diff` (tests/ is not an ACT's path), after the apply.
