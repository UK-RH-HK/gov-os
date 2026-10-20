---
id: W2-58-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-20
branch: w2/W2-58
base: 9afe3d00
ticket: DAEO-5j8b (W2-58)
author: engineer (W2-58)
decisions_recorded: [DEC-821]
state_class: EVIDENCE
---

# W2-58: change-execution record (CIT-E)

This records the changes of W2-58 (DAEO-5j8b) under DEC-821, which approves this guard and launcher change under
CAP-33: Policy 2 (DEC-820) in the guard and the launcher. Reads are open but for four things: (a) secrets and keys,
(b) the held-out material's contents, (c) the counterpart's work on the session's ticket and (d) the hidden part of
an evaluation set that measures the session. The listing and search refusals over `governance/` and `.claude/`
(DEC-508, DEC-525, DEC-557) are gone (DEC-857 item 3). No write rule widens; a guard error still fails closed.

## 1. The changes

| # | File | Change | Evidence |
|---|---|---|---|
| 1 | `src/gov/guard/protected.py` | The read refusals of the settings file and the held-out file are removed: the file named, a folder above it, a glob that matches it, a search from the folder it lies under, copies of either. What stays: the second names of either file, of a copy of one or of a folder that holds one (a move, a hard or symbolic link, a linking copy `cp -l` or `cp -s`, an in-place edit with a backup), now with their own message `SECOND_NAME_REFUSAL`, which names the rule and DEC-821 item 4 and carries no path; the NUL-byte refusal (DEC-562); the bounded-time refusals (the substitutions, the brace expansions, the paths times filters of a search, the folders resolved; DEC-562, DEC-570). A second name behind a prefix command (`timeout 5 mv …`) is now read as the command it is. An interpreter's in-place edit (`perl -i`, `perl -pi.bak`, `ruby -i`) of either file stays refused: the allow-list does not read it as a write, and before W2-58 the read rule refused it, so lifting the read rule alone would have widened the writes. The helpers only the removed rules used are removed (`_takes_folder`, `_reads_input`, `_tokenised`, `_search_reads`, `_git_quiet`, `starts_at`, `holds`); the parsing `reads.py` shares stays. | `tests/unit/guard/test_protected.py` (136 cases), `test_protected_one_reader.py` (36) |
| 2 | `src/gov/guard/reads.py` (new) | Policy 2's (a), (c), (d). (a): `.env`, `.env.*` at any depth, `*.pem`, `*.key`, `config/secrets*`, anything under `~/.ssh/`, `~/.claude/.credentials.json`: a content read that names one (Read, Grep at it, a Bash word, a piece of one that exists, an input redirect, `git show <rev>:<path>`, `cp`), for every role; a search from a folder above is not refused for them; a short constant list (DEC-135). (c) engineer: `tests/acceptance/<wbs_id>/` of the session's ticket. (c) test designer: the files `git diff --name-only <merge base with w2/integrate> HEAD` names but `tests/acceptance/` and `.tickets/`; `git show <rev>:<file>` is allowed when its blob is the base's; no `w2/integrate`, nothing refused; a git command that fails, refused. (d): the hidden globs of the sets that measure the session (its role in `measures.roles`, or its ticket id or WBS id in `measures.tickets`). For a part: a call aimed at or under it is refused whether or not it exists; a content search from a folder above (Grep, `grep -r`, `rg`, `git grep`, `find … -exec`) is refused where the part's files exist and no positive glob keeps them out; a listing from above (Glob with `**`, `find` with no action that opens files, `ls -R`, `rg --files`) only names files, and is refused only where it names a part's file in the folder it lists (`ls src/app`, Glob `src/app/*`, `find src/app -name '*.py'`); `git log -p`, `git show <rev>`, `git diff <rev>` are refused unless a pathspec keeps the part out or `--stat`/`--name-only`/`--name-status`/`--shortstat`/`--numstat` is given; `pytest` and `python3 -m pytest` are not judged, so the tests run and show names, results and failure messages; an `rg` fed by a pipe or an input redirect searches what feeds it. A word that is a write target of its own command, or the folder one lands in, or the destination of `cp`, `mv` or `install`, is left to the allow-list, which judges it and names it (as the read rule of the two files left it); a `cp` source is a read. The acting role is the subagent's type when it is a role, the session's otherwise. Fail closed: a ticket file that is neither YAML nor gives a WBS id to the line reader, a path map that cannot be read, a malformed set that could concern the session, a git failure, any exception: the call is refused with a fixed message. Bounded time: the folders resolved per call are bounded as `protected.py`'s are (`_MOST_RESOLVED`), a part's files walked at most 10 000, a shell glob word is matched against the parts' files (and, wildcards in its last name only, one folder's names for secrets), never expanded over the file system. | `tests/unit/guard/test_reads.py` (97 cases); acceptance `tests/acceptance/W2-58/` (563 passed) |
| 3 | `src/gov/guard/decide.py` | The read rules only: after `read_refusal`, `reads.policy_refusal` for the read tools and Bash (with the role, the ticket and the subagent type). The write tools never reach it, so the write rules and an Edit of the guard stay as they were. | `tests/unit/guard/test_decide.py` (one case moved: a link to the engineer's own acceptance folder is now refused under (c); a link to another ticket's folder stays allowed) |
| 4 | `src/gov/launch/launcher.py` | The sandbox's read denials only: `build_settings` adds `reads.read_denials`: `Read(//<root>/tests/acceptance/W2-5[8]/**)` for an engineer (the folder's last letter written as a class), `Read(//<root>/<file>*)` for each changed file of a test designer, `Read(//<root>/<hidden glob>)` for a measured session (a literal folder before `/**` gets the same class, `hidde[n]/**`; a literal path gets `*` and the class form). Each rule holds a wildcard inside a name, so it binds the file tools and, on Linux, the CLI skips it for the commands' sandbox (as `_runtime_rules` records): the session's pytest still reads the tests and imports the code. **A trailing `/**` alone is not skipped:** this engineer's own relaunched session (on the commits through `bf12ac1e`) carried `Read(//…/tests/acceptance/W2-58/**)` and `Read(//…/fixtures/evaluation/memory-retrieval/hidden/**)`, and its sandbox's read-deny list held both folders as literal paths, beside the held-out folder, whose rule has the same form; `pytest tests/acceptance/W2-58 --co` collected nothing and `git status` showed the suite's files as deleted. Fixed in `31ed6074`. A malformed `evaluation_sets` block, or a git failure for a test designer, refuses the launch. | `tests/unit/launch/test_launcher.py` (2 cases added) |
| 5 | `template/governance/kernel/schemas/path-map.schema.json` | The optional `evaluation_sets` block: a map from a set's name to `visible` (list of project-relative paths or globs), `hidden` (the same, at least one) and `measures` (`roles` and/or `tickets`, at least one non-empty). A set without `hidden`, a `hidden` that is no list, or a path that is no string does not validate. | §3 |
| 6 | `governance/project/path-map.yaml` | Only the `evaluation_sets` block is added, after the last line; no other line changes (`accepted_reds`, `load_sensitive` untouched, DEC-757, DEC-766). | §3 |

## 2. The rules removed and the rules added

**Removed** (every role): a read of `governance/project/held-out.yaml` or `.claude/settings.json` by any route (DEC-508);
a folder above either inside the project, a glob that matches either (DEC-525); a search or listing that starts at
the repository root, `governance/`, `governance/project/` or `.claude/` (DEC-557); a read of a copy of either below
the root, in another checkout or worktree, in the home folder, and of `~/.claude/settings.json` (DEC-548, DEC-553 as
reads). The held-out list's names are readable; the material it names stays refused (DEC-162, DEC-215, unchanged).

**Kept:** the held-out rule and its fail-closed load (DEC-162, DEC-215, DEC-218) and the edit exception of
`names_held_out`; the launcher's held-out `Read` deny rules; the second names of the two files (now for the write
side, DEC-821 item 4); the NUL-byte and bounded-time refusals.

**Added:** (a), (c) for the engineer and the test designer, (d), as in §1 row 2; the sandbox's `Read` deny rules of
row 4.

## 3. The evaluation set declared

    evaluation_sets:
      memory-retrieval:
        visible: ["docs/assessment/2026-10/B-memory-retrieval.md"]
        hidden: ["fixtures/evaluation/memory-retrieval/hidden/**"]
        measures:
          roles: [engineer, research]

`visible` is lens B's 20 questions. The hidden path lies under `fixtures/`, whose namespace `fixtures` is the only
namespace with `paths: ["fixtures/**"]` and has memory class `product`; the indexer reads only paths whose every
namespace is governance memory (`gov.secrets._governance`, `indexable`), so it never reads the hidden answers, and
the path names none of the visible paths. `measures` names the roles that build or tune retrieval; W2-61 narrows it
to tickets when it fills the hidden part. Until then nothing exists under the hidden path, so it refuses nothing to
anyone's searches; a call aimed at it is refused to a measured session.

Checks with the block in place: the path map validates against the schema (`jsonschema` with `common.schema.json`
resolved); `gov.check.pathmap.check` finds nothing; the guard reads the block (`reads.evaluation_sets`). The
schema refuses a set without `hidden`, a `hidden` that is a string, a non-string hidden or visible path, empty
`measures`, empty `roles`; it accepts a set measured by tickets alone.

## 4. Tests

Every run in this worktree with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src` (DEC-732).

| Suite | Code | Result |
|---|---|---|
| `tests/acceptance/W2-58` | `3fe394a2` | 563 passed (also at `9b3f841c`; 341 failed, 222 passed at `c772c86c`) |
| `tests/acceptance/W2-58` | `d545c34b` (final) | **not run**: the relaunched session's sandbox hid the folder (§1 row 4); pytest collects nothing |
| `tests/acceptance/W1-02` (by file) | final | 3623 passed, 32 failed (§5 items 1, 2) |
| `W1-03`, `W1-28`, `W1-32`, `W1-38`, `W1-39` | `bf12ac1e` | 364, 151, 81, 201, 71 passed |
| `W1-27` | `bf12ac1e` | 132 passed, 1 failed (`test_rebuild_codeintel_is_recreated_when_tool_answers`: `gov rebuild`'s code index, no guard code) |
| `W1-46` | `31ed6074` | 457 passed, 36 errors (`test_w1_46_live_sessions.py`: live sessions, network denied by the session's proxy) |
| `W1-47`, `W1-48` | `31ed6074` | 983, 172 passed |
| `W1-05` | `d545c34b` | 98 passed, 1 failed (the switch-over record runs W1-02 with `-x` and meets §5 item 1) |
| `W1-50` | `d545c34b` | 683 passed, 2 failed (`freeze_launcher`, `freeze_live_pause`: live sessions, `api.anthropic.com` denied) |
| `W2-50` (by file) | `05401735`, `d545c34b` | all files green: 1, 72, 32, 82, 25, 18, 88, 6, 167, 15, 54, 23, 53 passed |
| `tests/unit/guard`, `tests/unit/launch` | final | 979, 138 passed |

`python3 -m gov.guard.hooks` loaded after every guard edit.

## 5. Residuals

1. **29 earlier cases rewritten on this branch ask a refusal's wording of a read Policy 2 allows** (W1-02 `copies` 3,
   `name_filters` 5, `root_searches` 7, `search_on_a_pipe` 9, `wildcard_globs` 5): each fails with "the refusal of …
   names a decision and no rule", the base helper `assert_says_nothing_of_the_file`, which fails on an empty reason;
   an allowed call has none. Returned as a package (the test designer's).
2. **3 earlier cases expect an engineer's search from the root under the glob `*.py` or `**/*.py` to be allowed**
   (W1-02 `root_searches` 2, `protected_reads_open` 1), in a world where the engineer's own
   `tests/acceptance/<wbs>/test_fixture.py` exists: the brief's item 3 refuses a content search from above that no
   glob keeps out. Returned as a package.
3. The ticket's suite on the final code is to be run outside a session launched with the W2-58 rules of
   `bf12ac1e` (the lead's).
4. `perl -i`/`ruby -i` edits are kept refused only for the two files; the allow-list does not read them as writes
   elsewhere (a write-side gap, not this ticket's).
5. Proportion: the code is about 890 lines added and 210 removed against an estimate of 150; `reads.py` is the bulk.
