**A note first:** an earlier engineer session on this batch ended before it finished, because it waited on a pytest run it had started in the background (a headless session ends when it stops to wait). It left `tests/unit/guard/test_w2_42a_blob_refs_2.py` uncommitted: yours to keep, change or delete. Run every command in the foreground (never `run_in_background`, never a Monitor); a heavy-slot queue is waited out in the same foreground call. Commit before you return.

# Brief: engineer, W2-42a (DAEO-03ub), R4 (blob revision-colon-paths judged as reads) and R5 (the guard's judge never raises) (DEC-1157 (12), DEC-1180 (4)): second batch

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head 4692b61ddac6.
Your paths: src/gov/guard/reads.py (the fix); src/gov/guard/decide.py or src/gov/guard/bash_writes.py only if a crash
sits there; tests/unit/guard/test_w2_42a* for unit cases of what you change; one short paragraph in
docs/changes/W2-42a-evidence.md. Nothing else changes. Never tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1157, DEC-1180, DEC-1128, DEC-1133" -- <your paths>`

## What to make pass
The acceptance cases below fail on 4692b61ddac6; their failing output is all you are given. Make them pass by changing the
product's guard, under these rules:
- A revision-colon-path naming a blob (`git diff REV:PATH REV:PATH`, one or both sides; `git show REV:PATH`) is read as
  its path, under the read rules that path names (the hidden part, secrets, held-out, the counterpart's work): a path
  the role may read is allowed; one it may not is refused by its rule. A revision word that names no commit, tree or
  blob is refused, by a ruled refusal (a refusal text naming why), not an exception.
- A crash becomes a ruled decision: no Bash or tool input makes the judge (`reads._Judge.tool`/`command`, `decide()`,
  the parser `decide.py`/`bash_writes.py` reaches) raise inside itself. Fix each crash at its cause (a length check, a
  guarded index), not by wrapping the judge in a blanket `except` that turns every fault into a refusal or an allow.
- The error path itself stays for genuine faults (git missing, an unreadable path map, the deadline): they still fail
  closed.
- Nothing refused today that writes into a walled path (tests/acceptance/, outside a reviewer's record) or reads a
  refused one (secrets, the hidden part, held-out material) becomes allowed. Fail closed when in doubt.
Also, for this batch (the failing cases below are of these kinds):
- In `<rev>:<path>` the path starts at the top of the tree `<rev>` names. Only a commit (or the index: an empty
  `<rev>`, `:<n>:`) places it at the repository's top; a `<rev>` that names a tree other than a commit's top (a
  subtree's id) cannot be placed: for a session with a refused part it is a ruled refusal, in git diff, git show and
  git cat-file alike.
- An object named by its id alone that git prints as a file's text (`git cat-file blob <id>`, `git cat-file -p <id>`
  of a blob) is a ruled refusal for a session with a refused part, as `git show <blob id>` already is; `-t`, `-s`,
  `-e` and a commit object stay allowed.
- git's own `--output=<file>` and `--output <file>` (git diff, show, log) write that file: the parser gives it as a
  write target (resolved against the command's cwd, also after `git -C` and `cd`), so the write rules judge it; the
  file word of `--output <file>` is no revision word for the read judge.
Also run the whole acceptance folder tests/acceptance/W2-42a and tests/unit/guard: nothing green there may turn red.

## How to run (pytest only through the heavy slot; one line each; `mkdir -p $TMPDIR/empty-home` first)
`cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py tests/acceptance/W2-42a/test_w2_42a_r5_error_path.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Whole folders: the same line with `tests/acceptance/W2-42a tests/unit/guard -n auto -m "not local_only" -k "not real and not green_here and not time_limit"`.
The heavy slot may queue: that is a wait. Anything longer than one line goes in a script file under `$TMPDIR`, run
with bash or python3. Use the sandbox's own `$TMPDIR`; never write outside it and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit hash(es) (12), the
counts of the failing files and of the two whole folders after your fix; in `work_completed`: each crash you fixed
as file:function and the change, and how the blob read is judged (the functions changed: the live hook's ACT copies
them). A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it.
Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in other words.
Never open the evaluation sets' root or any hidden or memory-verdict folder. No merge in the sandbox. A resource
gate's refusal is a wait.

## The failing output (on 4692b61ddac6)

```
heavy_slot: all 3 slots taken; waiting (2026-11-14 16:53:02)
........................................................................ [ 23%]
........................................................................ [ 47%]
........................................................................ [ 71%]
.............................FFFFFFFFFFFFFFFFFFFFFFFFF..............FFFF [ 95%]
FFFFFFFFFFF...                                                           [100%]
=================================== FAILURES ===================================
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-first-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-first-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-second-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff HEAD:docs/a.md bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-second-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff HEAD:docs/a.md bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-hidden-tree-path-first-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-hidden-tree-path-first-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-subtree-path-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git show bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-subtree-path-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git show bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-hidden-tree-path-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git show 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-hidden-tree-path-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git show 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-p-subtree-path-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file -p bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-p-subtree-path-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file -p bb33639bf4871db0ab705d2ac7f0a4e6afea1472:hidden/q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-blob-hidden-tree-path-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file blob 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-blob-hidden-tree-path-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:212: in test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file blob 5deeda268f7744e7156b33a317bc130a61c18a17:q01.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-subtree-path-first] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-subtree-path-second] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-hidden-tree-path-first] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[show-subtree-path] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[show-hidden-tree-path] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[cat-file-p-subtree-path] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[cat-file-blob-hidden-tree-path] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:220: in test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook
    assert got[0] == "deny", f"a fail-open through the hook: want deny, got {got}"
E   AssertionError: a fail-open through the hook: want deny, got ('allow', '', 0)
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-blob-id-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:245: in test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file blob f0d6b396d84fb1a8a77c29612679be7f521598f4
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-blob-id-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:245: in test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file blob f0d6b396d84fb1a8a77c29612679be7f521598f4
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-p-blob-id-research] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:245: in test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file -p f0d6b396d84fb1a8a77c29612679be7f521598f4
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-p-blob-id-engineer] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:245: in test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal
    assert_refused_ruled(fill(template, planted), planted["root"], who)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:153: in assert_refused_ruled
    assert got[0] == "deny", f"a fail-open: want a ruled refusal, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: want a ruled refusal, got ('allow', '')
E     --- the command (cwd None) ---
E     git cat-file -p f0d6b396d84fb1a8a77c29612679be7f521598f4
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-blobs-output-eq-last] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff HEAD:docs/a.md HEAD:docs/b.md --output=tests/acceptance/X/zz.txt
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-eq-first-blobs] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff --output=tests/acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-space-commits] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:168: in assert_write_refused
    assert T in got[1], f"want the write refusal naming {T}, got: {got[1]}{show(command, cwd)}"
E   AssertionError: want the write refusal naming tests/acceptance/X/zz.txt, got: the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree or blob, or it is given at run time (a variable, a substitution, --stdin), so what the call shows cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist
E     --- the command (cwd None) ---
E     git diff --output tests/acceptance/X/zz.txt HEAD~0 HEAD
E   assert 'tests/acceptance/X/zz.txt' in 'the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree o...s cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist'
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-eq-commits] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git diff --output=tests/acceptance/X/zz.txt HEAD~0 HEAD
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[show-output-eq-blob] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git show --output=tests/acceptance/X/zz.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[log-p-output-eq-range] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git log -p --output=tests/acceptance/X/zz.txt HEAD~1..HEAD
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[log-p-1-output-eq-path] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     git log -p -1 --output=tests/acceptance/X/zz.txt -- docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-diff-output-eq] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj/docs) ---
E     git -C /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj diff --output=tests/acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-diff-output-space] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:168: in assert_write_refused
    assert T in got[1], f"want the write refusal naming {T}, got: {got[1]}{show(command, cwd)}"
E   AssertionError: want the write refusal naming tests/acceptance/X/zz.txt, got: the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree or blob, or it is given at run time (a variable, a substitution, --stdin), so what the call shows cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist
E     --- the command (cwd /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj/docs) ---
E     git -C /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj diff --output tests/acceptance/X/zz.txt HEAD~0 HEAD
E   assert 'tests/acceptance/X/zz.txt' in 'the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree o...s cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist'
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-show-output-eq] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj/docs) ---
E     git -C /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj show --output=tests/acceptance/X/zz.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-log-output-eq] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj/docs) ---
E     git -C /tmp/w2-42a-lead/tmp/pytest-of-usain/pytest-10/w242a-r4b0/proj log -p --output=tests/acceptance/X/zz.txt HEAD~1..HEAD
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-diff-output-eq-relative] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     cd tests && git diff --output=acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-diff-output-space-relative] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:168: in assert_write_refused
    assert T in got[1], f"want the write refusal naming {T}, got: {got[1]}{show(command, cwd)}"
E   AssertionError: want the write refusal naming tests/acceptance/X/zz.txt, got: the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree or blob, or it is given at run time (a variable, a substitution, --stdin), so what the call shows cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist
E     --- the command (cwd None) ---
E     cd tests && git diff --output acceptance/X/zz.txt HEAD~0 HEAD
E   assert 'tests/acceptance/X/zz.txt' in 'the call names a revision the guard cannot resolve: git does not resolve it (or its <rev>:<path>) to a commit, tree o...s cannot be judged against the parts refused to this session (DEC-820): refused; name a revision and a path that exist'
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-show-output-eq-relative] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     cd tests && git show --output=acceptance/X/zz.txt HEAD:docs/a.md
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
_ test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-log-output-eq-relative] _
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:294: in test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule
    assert_write_refused(fill(template, planted), root, os.path.join(root, sub) if sub else None)
tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py:167: in assert_write_refused
    assert got[0] == "deny", f"a fail-open: git writes {T}, want deny, got {got}{show(command, cwd)}"
E   AssertionError: a fail-open: git writes tests/acceptance/X/zz.txt, want deny, got ('allow', '')
E     --- the command (cwd None) ---
E     cd tests && git log -p --output=acceptance/X/zz.txt HEAD~1..HEAD
E   assert 'allow' == 'deny'
E     
E     - deny
E     + allow
=========================== short test summary info ============================
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-first-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-first-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-second-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-subtree-path-second-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-hidden-tree-path-first-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[diff-hidden-tree-path-first-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-subtree-path-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-subtree-path-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-hidden-tree-path-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[show-hidden-tree-path-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-p-subtree-path-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-p-subtree-path-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-blob-hidden-tree-path-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal[cat-file-blob-hidden-tree-path-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-subtree-path-first]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-subtree-path-second]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[diff-hidden-tree-path-first]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[show-subtree-path]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[show-hidden-tree-path]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[cat-file-p-subtree-path]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook[cat-file-blob-hidden-tree-path]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-blob-id-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-blob-id-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-p-blob-id-research]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal[cat-file-p-blob-id-engineer]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-blobs-output-eq-last]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-eq-first-blobs]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-space-commits]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[diff-output-eq-commits]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[show-output-eq-blob]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[log-p-output-eq-range]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[log-p-1-output-eq-path]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-diff-output-eq]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-diff-output-space]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-show-output-eq]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[git-C-log-output-eq]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-diff-output-eq-relative]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-diff-output-space-relative]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-show-output-eq-relative]
FAILED tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule[cd-log-output-eq-relative]
40 failed, 262 passed in 16.60s
```
