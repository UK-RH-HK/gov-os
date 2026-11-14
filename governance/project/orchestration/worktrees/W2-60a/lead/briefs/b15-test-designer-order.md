You are a fresh independent test designer. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a-tests`, branch `w2/W2-60a-tests` (the tests worktree; an engineer works in the main tree `/home/usain/gov-os-worktrees/W2-60a` at the same time: never write there). One job: revise 11 assertions in `tests/acceptance/W2-60a/` to the launcher's decided behaviour, keeping each case's point.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a-tests`, `w2/W2-60a-tests`). If anything differs, stop and say so.

## Standing rules

- Foreground only; your session ends with your last message.
- Your files: `tests/acceptance/W2-60a/test_w2_60a_launch_record.py`, `test_w2_60a_model_and_effort.py`, `test_w2_60a_refused_arguments.py`, and `w2_60a_support.py` only if a shared helper is the cleanest form. Nothing else; never code under `src/`.
- If the guard refuses a write to your files, that refusal is the answer: stop and report it (refused twice for the same call: stop; never another form).
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with your session's own `$TMPDIR` as TMPDIR, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's refusal is a wait.
- Write with the Write and Edit tools and absolute paths. No `git merge`, `checkout`, `reset`, `stash`, `clean`, rebase or push. Commit your files only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-839" --trailer "Rewrite-Reason: <why, one line>" -- <your paths>`. Commit hashes in 12 digits. Time budget about 45 minutes.

## The decided behaviour

Since the merge of `w2/integrate` (W2-153), `gov launch` hands one `--append-system-prompt-file <TMPDIR>/role-<role>.md` (the role file's bytes, one blank line, the role template's bytes), placed **last**, after the caller's arguments (the lead's decision for the merge, joining W2-153's template, which integrate's tests pin as the last two arguments, and W2-60a's role text). And since W2-136 (DEC-1088 (5)), a launch of `orchestrator` is a lead launch, refused (for a ticket on no approved ready list) with `LAUNCH_REFUSED: no lead for ticket '<id>': no approved ready list can be read …`; it is still refused, with no CLI start and no record.

## The 11 cases (the lead's names; check them on your own run first)

1. Ten argv-tail checks, red because the appended file now follows the caller's arguments:
   - `test_w2_60a_launch_record.py:264` `resumed.args[-len(passed):] == passed` (3 cases: spaced, joined, short);
   - `test_w2_60a_model_and_effort.py:51` and `:64` `args[-len(arguments):] == arguments` (2 + 2);
   - `test_w2_60a_refused_arguments.py:87` and `:124` `args[-2:] == ["-p", prompt]`, `:117` `args[-len(arguments):] == arguments` (`--no-chrome`).
   Revise each to keep its point: the caller's arguments reach the CLI unchanged, in order, as one contiguous run, once (and, where the case says so, after the launcher's own flags), with the appended-file pair the last two arguments. Not a weaker "is somewhere in argv".
2. `test_w2_60a_refused_arguments.py:189` `[orchestrator]` (the assertion at `w2_60a_support.py:866` expects "not a worker role"): revise it to the lead-launch refusal (`LAUNCH_REFUSED` and "no lead for ticket"), keeping that the CLI never started and no record was left.

3. `tests/acceptance/W2-60a/test_w2_60a_plan.py` (written before you by another designer to an interface that said exit 2): the CTO decided (P-6 (a), recorded in the ticket) that the plan's refusal exits **1**, like every `LAUNCH_REFUSED` through `gov` (2 is reserved for usage errors). Revise its refusal cases' exit code to 1 (Rewrite-Reason naming P-6 (a)), and add one case: a role file with a malformed default line (e.g. `model sonnet, effort high`) fails the plan the same way (`LAUNCH_REFUSED`, the role file's path named, exit 1, nothing started), as the interface states. Nothing else in it changes. The merge conflicts that the brief's earlier text mentions are resolved in this tree now (b12's 2cf3882ddd09 is merged in).

## Second job (P-7 (a), the CTO's decision, recorded in the ticket): a vendored skill's version from its manifest

Add cases in `tests/acceptance/W2-60a/test_w2_60a_skills.py` (your file for this job too), using the support module's fixtures. Interface (the lead's statement of P-7 (a)):
- The vendored Superpowers skill copies (`.claude/skills/<name>/SKILL.md`) carry no version. Their version is in the manifest `template/governance/kernel/skills/superpowers/vendored.yaml` (or `governance/kernel/skills/superpowers/vendored.yaml` in the adopted layout): a top-level `version: "v6.4.2"` and the skills listed as the keys of a `token_sizes` map (see this repository's own file).
- When a loadable skill's copy carries no version (neither top-level `version` nor `metadata.version`) and its name is a key of the manifest's `token_sizes`, the launch record lists it with the manifest's `version` and one more key, `"version_source"`, whose value is the manifest's repository-relative path; its `sha256` stays the loaded copy's. A named one launches. Skills whose version comes from their copy have no `version_source` key.
- A copy with no version that is not listed (or with no manifest, or a manifest not a YAML mapping) is `no version` as today, and a named one still refuses with "carries no version".
Cases at least: a role naming a listed, unversioned skill launches, and its record entry has the manifest's version, `version_source` equal to the manifest's path, and the copy's sha256; the same skill unnamed is recorded the same way; a listed skill whose copy has its own version keeps the copy's (no `version_source`); a named unversioned skill not listed refuses; with no manifest it refuses. Show each red or green on this tree's code and say which (the code for it is being written in parallel).

## Verify, then return

Run `tests/acceptance/W2-60a` (the form above). On this tree's code the 11 must be green; the reds expected from code not yet written are the metadata-version case in `test_w2_60a_skills.py` and the `--plan` cases in `test_w2_60a_plan.py` (if that file is in the tree). Name every other red: file:line, assertion, message. Return the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the counts, every red named, the guard refusals met (count), and your commit's hash and trailers.
