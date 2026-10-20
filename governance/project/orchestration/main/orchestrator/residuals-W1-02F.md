
## W1-02 follow-up: the guard refuses reads of the settings file and the held-out file, for every role (DEC-508, DEC-525, DEC-548, DEC-553, DEC-562; 2026-10-09)

Merged from `w1/W1-02` at `e9e6ee25` (probed at that commit; 1690 cases in the suite, 1161 of them new in
three batches). Built: the read rule in `src/gov/guard/protected.py`, called from the guard's decision for
every role and for a session with no role (the reading tool, the search tools, the notebook tool, the
shell); copies at the same project-relative path under another folder are treated as the files are (the
home folder's settings file among them); a second name (move, link, linking copy, in-place edit with a
backup, a move or link of a holding folder) is a read; the helper `python3 -m gov.guard.hooks` lists the
registered hooks with deny values and deny paths redacted. The refusal text names DEC-508 and DEC-525 and
no path. Comparisons over 420,000 and 840,000 random calls against the earlier heads: none refused before
and allowed after. From this merge on, a command or commit message that carries either file's path is
refused: write "the settings file" and "the held-out file".

**Built next, in the round of DEC-557 (after this merge, with its own probe):** a search from the project
root with no path or glob is refused for every role (14 cases of four suites rewritten, "owner decision
P-23"); a shell search with a name filter that names or matches either file (probe finding 1: a read that
gets through in ordinary work, such as `grep -rn . --include='*.<extension>' .`); an answer in bounded time
for every pattern and command (probe finding 7: a glob of many star pairs took 39 s and more; what the
harness does with a hook past its time limit is to be established); a NUL byte refused wherever it stands.

**What a command-line guard cannot see (residuals):**

1. A script file that opens either file; a script on the command line that builds the name; an interpreter
   or shell fed by a pipe or standard input.
2. A name that arrives at run time (substitution, a variable the command sets, `xargs`, `find -exec`):
   refused for writes, not held for reads.
3. A command that names no path and reads the tree or history (`git diff` with no path, `git show`,
   `git log -p`, `git grep`, an archive of the root); a git object read by its id.
4. A second name or copy made earlier, outside the call; a copy under another name or relative path; a copy
   that is itself a symbolic link named through a path that resolves elsewhere.
5. A program that reads the settings file by itself (`claude`, `rulesync`); a tool the guard does not know.
6. `git -C <another checkout>` with a relative path; a `cd` into a folder that exists only at run time.
7. A copy reached by a glob or search that starts above its folder (answered with DEC-557's round where the
   pattern names the file); a path that ends in a file's project-relative path and names no file yet.
8. A second name by a program the guard does not know (`rsync --link-dest`, `install`, `cp --reflink`,
   `git mv`, `tar`, `rename`, a bind mount, an editor's backup); in-place options that cannot be told from a
   suffix (`sed -i bak` without a dot); a move or copy with an option the operand reader cannot read; a move
   or link of the folder a copy's folder lies under, or of a folder above it.
9. A user-level settings file that is not at `$HOME` of the hook's environment.
10. A wildcard-only word in a command that is no reader; other spellings of "everything".

**From the probe (session `cc784d3e-ecb5-4176-8726-847f86f79cf6`; record in `docs/probes/DAEO-emkd/`), each
in a deliberate or unusual shape:**

11. A `cd` is followed whether or not it takes effect (in a subshell, a pipeline, a background job, a branch
    not taken, or to a folder that does not exist): `(cd /tmp); cat <the file>` is allowed; the reverse
    refuses two ordinary listings after a `cd` into the folder above the file.
12. Shell spellings the token expansion gives up on are allowed: `$'…'`, `$"…"`, `~+/`, an unset variable or
    `$@` glued to the name.
13. A script on the command line with an operator glued to the name (`bash -c "cat <the file>|head"`, the
    same with `<`, `>`, `&&`, a backtick), `eval` of the same, and a here-string into a shell are allowed.
14. Search-tool globs with an escaped dot, a leading backslash, single braces, or a comma list are allowed
    (the rule reads only `*`, `?` and `[` as pattern signs).
15. An in-place edit that prints (`sed -i 'w /dev/stdout'`) by a role that may write the file is allowed.
16. The helper prints a deny path when the rule's shape is not the one the project's writer produces (a
    deeper pattern after the path, a shell rule, a tool name with a hyphen, a stray space or newline), when
    the path stands outside `permissions.deny` (in the ask or allow list, in the sandbox's list, a deny that
    is no list), in `matcher` or as an event key, with a doubled slash or `/./`, after a shorter deny value
    was replaced inside it, or resolved with `HOME=/`. Each needs a hook command that carries the path.
17. Helper: a project-relative spelling, `$HOME/…`, `${HOME}/…`, `~user/…`, a longer name that begins with
    a deny path, a rule that is the home folder itself.
18. A reading tool call whose path field is a list or a number is answered allow (the tool cannot run it).
19. A command of 200 KB of short words costs about 8 s in the read rule.

- **Two test-designer commits of the first batch, `15a0dbc4` and `56f1476d`, carry no `Implements:`**: named
  exceptions for the exit auditor (DEC-558).
- **Latency under load (DEC-372):** in the second run one W1-02 p95 case (about 220 ms with three runs in
  parallel) and one W1-05 p95 case (about 190 ms) failed and passed alone; none in the third run.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** none; 1161 added in
  three planned batches, each red first.
