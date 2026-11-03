# G-14 (DAEO-sdxk): where it stopped, 2026-11-03 (owner's stop before a fresh session)

## Done
- Reading only. No candidate files, no path-map patch, no replay, no test run. No TMPDIR was made, and no process is
  running. This file is the only one written.
- Sources read: EMG-common, INTENT-DEC-1052 (role separation paragraph), DEC-1052 G-14, DEC-820 (c), DEC-821 item 1,
  DEC-963, INVESTIGATION-1 row G-14, path-map.yaml (no role section; every namespace's `permitted_roles` lists all six
  roles, so it separates nothing and reading it adds nothing: the recommendation is to leave it unread), the live
  `.claude/hooks/pretooluse.py`, and the reading helpers in `bash_writes.py`.

## Measured
- Nothing yet: no replay counts.

## Findings that shape the design
- The pinned product `gov/guard/reads.py` (under `~/.local/share/gov-os/pin-9894b0cf/.../site-packages/`) already holds
  W2-58's machinery: `parts()` with TESTS_REFUSAL and CHANGED_REFUSAL, and `_Judge`, which also refuses searches "from
  above" and run-time listings (RUNTIME_REFUSAL). That shell guessing is the W2-58 cost (26.2 h). **Do not reuse
  `_Judge` for G-14.** Reuse only `_Part(tree, [glob], reason).inside(path)` for glob matching (it touches no disk
  unless `.files` is called), plus `reads._ticket`/`_front` for the ticket's WBS id.
- The hook already uses `reads.acting_role(role, agent_type)`. Judge the role reads for both the session role and the
  acting role, as rule 2 does (`for r in dict.fromkeys((role, acting))`).
- Tickets: the front matter has `wbs_id` and `allowed_paths` (example: `~/gov-os-worktrees/W2-126-tests/.tickets/DAEO-jpr0.md`).
  `allowed_paths` includes `tests/unit/...` and `tests/conftest.py`. The brief's "outside tests/" leaves the
  engineer's unit tests readable by the designer. Flag this to the owner.
- Worktrees: `~/gov-os-worktrees/<W2>`, `<W2>-tests`, and `W2-00-store{,-a,-b}`. There are 93 transcript folders
  matching `~/.claude/projects/-home-usain-gov-os-worktrees-W2-*`.
- `bash_writes.py` has reusable reading helpers: `heredocs`, `lift` (substitutions), `tokens`, `simples`, `lead`,
  `variants`, `environ`, and `Judgement.cd`/`place`. `Unreadable` means let the call through.

## Exact next step
1. Make `drafts/g14/` copies of `.claude/hooks/pretooluse.py` and `bash_writes.py`. Add a small `role_reads.py` with:
   - `section(root)`: the path map's `role_paths:`. If the section is absent, there is no check.
   - `denied(root, role, ticket)`: (tree or None, glob) pairs. Plain globs apply in any tree: `tree_roots(root)`
     plus every direct child of `~/gov-os-worktrees`. `{ticket_tests}` expands to `tests/acceptance/<W2>/**`.
     `{ticket_impl}` expands to (`~/gov-os-worktrees/<W2>`, each allowed_path not under `tests/`).
   - Tool paths: Read `file_path`, NotebookRead `notebook_path`, Grep `path` (+ the `glob` param's literal lead),
     Glob `path` + the pattern's literal lead. Count Glob separately, since it shows names only.
   - Bash: walk simple commands with bash_writes' helpers, tracking `cd`. Readers: cat tac nl head tail less more
     bat grep/egrep/fgrep/rg (pattern skipped unless -e/-f), sed (script skipped unless -e/-f), awk, wc, diff, cmp,
     od, xxd, strings, base64, cut, sort, uniq, jq, and cp sources. For git show/diff/blame/cat-file, the path args
     are `rev:path` (relative to the cwd's tree), args after `--`, and bare args that exist as paths. A `rev` equal
     to `w2/<W2>` also judges the path in the ticket's worktree. pytest, `gov accept` and python scripts are not
     reads. A target that is unresolved, a search from a folder above, or an unreadable command: let through.
   - Refusal reason: `role_paths.<role>.reads_denied: "<glob>" (governance/project/path-map.yaml, DEC-1052 G-14)`.
   - Wire it into `main()` after rule 2's read judge.
2. Write `drafts/g14/path-map-role_paths.patch` with the defaults: engineer `["tests/acceptance/**"]`,
   designer `["{ticket_impl}"]`.
3. Write a replay script. Take the role from the transcript's `agent_type`/subagent `subagent_type` and from
   `GOV_ROLE=` in launch commands or the first user message. Feed each Read/Grep/Glob/Bash call through the
   candidate. Report the would-be refusals and hand-classify the honest ones. Run both defaults (all acceptance
   tests vs `{ticket_tests}` only).
4. Planted cases, then `drafts/act-guard-fix-4/test_guard_fix_4.py` pointed at the candidate. Every run goes
   through `heavy_slot.sh`, with `TMPDIR=/tmp/gov-os-emg-g14`.
5. Write `drafts/g14/ACT-G14.md`.
