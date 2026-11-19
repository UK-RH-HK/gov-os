---
id: DAEO-o5wi
status: closed
deps: []
links: []
created: 2026-11-18T09:00:00Z
type: task
priority: 2
assignee: engineer
external-ref: W2-198
tags: [implementation, standard, emergency-2]
wbs_id: W2-198
title: "Three small tools EMERGENCY-2 calls for: gov backup (hourly git bundles outside the tree, 2.8), gov memaudit scan (the hidden-set transcript scan, 2.7 A-12), gov decisions basis (the basis line checked by code, with the weekly review, 10.1 A-8)"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: STANDARD
depends_on: []
waits_on: []
closes:
- CAP-66.a
- CAP-67.a
- CAP-68.a
- CAP-68.b
allowed_paths:
- src/gov/backup/**
- src/gov/memaudit/command.py
- src/gov/memaudit/scan.py
- src/gov/decisions/command.py
- src/gov/decisions/basis.py
- tests/unit/backup/**
- tests/unit/memaudit/test_w2_198*
- tests/unit/decisions/test_w2_198*
- tests/acceptance/W2-198/**
est_loc: 600
kpis:
  success:
  - 'S1 `gov backup` bundles every ref of the repository into one dated, verified file outside the tree. `gov backup --root <repo>` writes one file `<dest>/<name>-<YYYYMMDDTHHMMSSZ>.bundle` (UTC), where `<name>` is the main worktree''s folder name (`--name` replaces it) and `<dest>` is `$GOV_BACKUP_ROOT/<name>/`, `GOV_BACKUP_ROOT` defaulting to `~/.gov-os/backups`; `--dest <dir>` names the folder itself. The bundle holds every ref `git for-each-ref` lists (branches, tags, stash, the branches checked out in other worktrees) and each worktree''s detached HEAD; it is written under a temporary name and renamed only once `git bundle verify` passes. Run from any worktree of the repository, it bundles the same refs. Text form: exactly one line on stdout naming the file, the number of refs, `verified`, and the counts kept and removed; `--json` gives the envelope with `{file, bytes, refs, verified, kept, removed}`. Verify: a fixture repository (two branches, a tag, a linked worktree on its own branch with a commit of its own, a detached worktree with a commit of its own) under a fixture HOME: `gov backup` exits 0; one file in `~/.gov-os/backups/<name>/` of the name form; `git bundle list-heads` names every ref of `git for-each-ref` and the detached worktree''s commit; a clone of the bundle holds each branch''s commit; stdout is one line; with `GOV_BACKUP_ROOT` and with `--dest` the file goes there; run from the linked worktree, the same refs. [EMERGENCY-2 2.8]'
  - 'S2 It keeps the last N and one a day for 30 days, and touches nothing else. After writing, it keeps the newest `--keep` bundles (default 48) and the newest bundle of each UTC day of the last `--days` days (default 30), and deletes every other file of its own name form (`<name>-<YYYYMMDDTHHMMSSZ>.bundle`) in `<dest>`; the time is read from the file''s name, never its mtime; the clock is `GOV_BACKUP_NOW` (ISO-8601) when set. Verify: a fixture dest holding planted bundle files of the name form, hourly for 3 days and three a day for the 40 days before, plus a file of another name, another repository''s bundle and a `.tmp` file: after one run with a planted `GOV_BACKUP_NOW`, exactly the newest 48 (the new one among them) and the newest of each of the 30 days remain, the deleted are exactly the rest of the name form, the three other files are untouched; with `--keep 5 --days 3` the same rule at those numbers; the result''s `removed` lists the deleted names. [EMERGENCY-2 2.8; the CTO''s brief]'
  - 'S3 `gov memaudit scan` reports every transcript written in the window that names the set''s path or one of its question ids. `gov memaudit scan --set <path> --since <ISO> [--until <ISO>] [--id <id> ...] [--allow-session <id> ...] [--projects <dir>]` reads every `*.jsonl` under `--projects` (default `~/.claude/projects`), sub-agent transcripts included, whose mtime is at or after `--since`, and in each the lines whose `timestamp` lies in [since, until] (`--until` defaults to now; a line without a timestamp counts when its file is in the window). A line names the set when one of its decoded text values (so JSON escaping hides nothing; a line that is not JSON is read as text) holds the set''s path (its absolute real path, its `~/` and `$HOME/` forms, and its part from a `fixtures/evaluation/` segment on, when it has one) or a question id as a whole token (not inside a longer word or number: `q01` does not match `q010` or `aq01`). The ids are the stems of the `*.yaml` files under the set''s path (names only; no file is opened for them), or exactly the `--id` values when given. Each finding gives the transcript file, the session id (the line''s `sessionId`, else the file''s stem), the 1-based line number, the role (the `agentType` of the sibling `<stem>.meta.json`, else null), the kind (`path` or `id`) and the matched id or path form. Any finding: exit 1, the text form''s first line says the measure is void, then one line a finding; none: exit 0 and one line. `--allow-session` sessions (the writer''s, the checker''s) are listed as allowed and never void the measure. Verify: a fixture set (`<tmp>/eval/fixtures/evaluation/memory-audit-20261101/hidden/q01.yaml` to `q03.yaml`) and a fixture projects root of transcripts in the form Claude Code writes, with mtimes and timestamps planted: a line in the window naming each path form, one naming `q02`, one in a sub-agent transcript with a `.meta.json` naming `agentType`, give one finding each with the right file, session, line, role, kind and match, exit 1; the same names in lines before `--since` or after `--until`, in a file whose mtime is before `--since`, inside `q020` or `xq02`, or in an allowed session give none; a projects root with none gives exit 0; `--id h7` finds `h7` and no longer finds `q02`; the JSON form holds the same findings. [EMERGENCY-2 2.7, A-12]'
  - 'S4 `gov decisions basis` refuses a new rule without a basis line that names an incident. For each decision entry (a line `### DEC-<n> — <title>`; a hyphen or en dash for the em dash is read too) present at the range''s end and absent at its start in the register (`--register`, default `docs/DECISION_REGISTER.md`), both read from git objects (never the working tree), it decides whether the entry adds a rule: its title or body (outside its `**Basis:**` and `**Governing sources:**` lines) holds `rule`, `gate`, `check`, `practice` or `standing` as a word (plural or `-ed` forms too, any case), unless the entry has a line `- **Adds:** no rule`. A rule entry passes only when its `- **Basis:**` line (with its continuation lines) names an incident: a date `YYYY-MM-DD` and at least five more words of what happened, or a path that exists in the tree at the range''s end. `gov decisions basis [--range <A>..<B>]` (default `HEAD^..HEAD`) exits 0 when every new entry passes and 1 when any fails, naming each failing entry''s id and reason (`no basis line`, `basis names no incident`); one line an entry in the text form, the envelope with `{range, entries: [{id, title, rule, basis, verdict, reason}]}` under `--json`. Verify: a fixture repository whose register gains, in one commit range, a rule entry with a dated incident basis, one with a basis of an existing incident record''s path, one with `**Basis:** question 1 (role separation)`, one with no basis line, one with a basis naming a path that does not exist and no date, one with no rule word, and one with a rule word and `- **Adds:** no rule`: exit 1 naming exactly the third, fourth and fifth with their reasons; an entry that lacked a basis before the range is not named; with only the passing entries in the range, exit 0; an uncommitted edit to the register changes no answer; `--register` reads another file. [EMERGENCY-2 10.1, A-8; retro-P3 F11]'
  - 'S5 The weekly basis review: `gov decisions basis --week [--since <YYYY-MM-DD>]` lists every entry the register gained in the week (since the date, default 7 days before now: present at HEAD, absent at the last commit before it), each with its id, title, the date of the commit that added it, whether it adds a rule, its basis line in full and its verdict, and exits 0 whatever the verdicts. Verify: a fixture repository with register commits dated (author and committer) 10 days and 2 days before now: `--week` lists only the 2-day-old entries, each with the fields above and the basis text whole; `--since` a date before both lists all; exit 0 with failing entries listed; `--json` holds the same. [EMERGENCY-2 10.1, A-8 "with a weekly basis review"]'
  failure:
  - 'F1 A failed backup loses no backup: when the new bundle fails `git bundle verify` (a `git` first on PATH that fails `bundle verify` only), `gov backup` exits 1 with `BACKUP_VERIFY_FAILED`, no file of the name form from this run remains (nor its temporary file), and no older bundle is deleted; a repository with no commit exits 1 with `BACKUP_FAILED` and deletes nothing; a `<dest>` inside the repository or any of its worktrees exits 1 with `BACKUP_DEST_INSIDE` and writes nothing. Verify: each case on a fixture dest holding planted older bundles: the dest''s listing is unchanged after the run.'
  - 'F2 The scan never prints a question''s text, and an unreadable transcript is never read as clean: no output of `gov memaudit scan` (stdout or stderr, text or JSON, with findings or without) holds any line of a set file but its id; a transcript in the window it cannot read is named in the result''s `problems`, and when nothing is found it exits 3 with `SCAN_INCOMPLETE` instead of 0. Verify: fixture questions with a distinctive question and gold answer text, the same text present in a transcript line that also names an id: neither text is in any output; a transcript of mode 000 in the window and no finding: exit 3 naming it.'
non_goals:
- 'The cron line for `gov backup` (the CTO adds it) and any change to the crontab'
- 'Wiring `gov decisions basis` into a commit hook, the landing or the weekly digest (the CTO decides where it runs, under 3.5); this ticket builds the check'
- 'Reading or matching a hidden set''s question text in transcripts; the real `~/gov-os-eval` in any test'
- 'Restoring from a bundle, pushing bundles anywhere, encrypting them'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [EMERGENCY-2 2.7, EMERGENCY-2 2.8, EMERGENCY-2 10.1, A-8, A-12, docs/audit/emergency-2026-11/retro-P3-lifts.md, docs/emergency-2/audits/02-memory-in-use.md]
acceptance_tests:
  path: tests/acceptance/W2-198/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-198: three small tools EMERGENCY-2 calls for

Created 2026-11-18 by the ticket lead from the CTO's brief (EMERGENCY-2 §4.3 step 1; the CTO approves the KPI lines by the brief). Three tools in the product (`src/gov/`), so adopted repositories get them too.

## Interface

All three are `gov` command modules (`src/gov/<name>/command.py`, the convention in `src/gov/cli/main.py`) that print their own output and end with their own code (`CHILD_EXIT_CODE = True`, as `gov msg` does): the API-0002 envelope under `--json`, else the text form; a refusal prints `gov <command>: <CODE>: <message>` on stderr. Each reads `--root` (default the working directory). Module top levels stay light (`gov --help` imports them).

**`gov backup`** (`src/gov/backup/command.py`, logic in `src/gov/backup/`). `gov backup [--dest <dir>] [--name <name>] [--keep <n>] [--days <n>]`. Bundle: `git bundle create <tmp> --all` in the repository of `--root` (any worktree), then `git bundle verify <tmp>`, then rename to `<name>-<YYYYMMDDTHHMMSSZ>.bundle`. The temporary file lives in `<dest>` under a name outside the name form. Clock: `GOV_BACKUP_NOW` (ISO-8601) when set. Exit codes: 0; 1 with `BACKUP_FAILED` (git failed, no commit), `BACKUP_VERIFY_FAILED`, `BACKUP_DEST_INSIDE`. Retention runs only after a verified bundle.

**`gov memaudit scan`** (`src/gov/memaudit/command.py`, logic in `src/gov/memaudit/scan.py`). `gov memaudit scan --set <path> --since <ISO> [--until <ISO>] [--id <id>]... [--allow-session <id>]... [--projects <dir>]`. Exit 0 nothing found; 1 found (`MEASURE_VOID`, the measure is void); 3 nothing found but a transcript unreadable (`SCAN_INCOMPLETE`). Result `{set, since, until, ids_count, transcripts_read, findings: [{file, session, line, role, kind, match}], allowed: [...], problems: [...]}`. The set's files are listed, never opened; no output carries a transcript line's text. `python3 -m gov.memaudit` is unchanged.

**`gov decisions basis`** (`src/gov/decisions/command.py`, logic in `src/gov/decisions/basis.py`). `gov decisions basis [--range <A>..<B>] [--register <path>]` and `gov decisions basis --week [--since <YYYY-MM-DD>]`. Exit 0 all pass (always 0 with `--week`); 1 `BASIS_MISSING` naming the failing entries. Reads git objects only.

**Closed at the land 2026-11-18 by the CTO (EMERGENCY-2 4.3 step 5):** merged into w2/integrate with gov accept green on the merged tree; no review (3.6).
