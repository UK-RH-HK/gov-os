# The permissions asked for last night, grouped by form, and the allow-list ACT (DEC-1126 (10))

Read `LIFT-common.md` first (scratch only). Role: ACT-preparation helper, Sonnet high, class C2 (DEC-1120). Scratch
folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-permissions-3/`.
Model your bundle on ACT-PERMISSIONS-2: `governance/project/orchestration/packages/ACT-PERMISSIONS-2.md`, its folder
`packages/ACT-PERMISSIONS-2/`, and `drafts/act-permissions-2/`; also `packages/P-PERMISSIONS-1.md` and
`governance/project/operator/class-rules.yaml` (the `settings` row: an allow rule is class (b), applied by the
owner's operator agent after a rehearsal and a fixed-brief review). Never edit a settings file yourself.

## The source
`.gov-runtime/scratch/orchestrator/log/approval-queue.jsonl` (the PermissionRequest hook's log,
`governance/project/orchestration/tools/permission_request.py`): every request since `2026-11-10 17:00`, 39 rows
(`at`, `tool`, `what`, `cwd`, `session`, `outcome`). Sessions: `8ddb8b14` is the CTO's (its in-session helpers share
the id), `412a4e37` the previous CTO, `e6ecf226`, `244c903e`, `7963582a` launched workers (find their tickets from
their cwd). The CTO's grouping, to check and correct:
- A. Write and Read in the helpers' own `/tmp/gov-os-emg-*/` folders (about 28).
- B. Bash: a throwaway venv and `pip install --no-deps --no-index` of a local wheel in `/tmp` (the re-pin rehearsal),
  and a copy of `.claude/hooks/` into a rehearsal clone (2).
- C. Monitor until-loops polling a test log in the worker's own `/tmp/gov-launch-*/` folder (7, launched workers).
- D. Write to a mistaken path `/tmp/claude-1000/-home-usain/Dynamic-Agentic-Engineering-OS/...` (slash, not the
  scratchpad's dashes) (2).
- E. AskUserQuestion (1).

## Your work
1. The table of forms: form, count, sessions, example, why it was asked (which settings file and which rule's
   absence; read `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json`, and the
   launched workers' composed settings as `gov launch` writes them: find where in `src/gov/launch/`), and your
   recommendation per form: allow (with the exact rule and the file it goes in), keep asking (why), or fix at the
   source instead (a brief line or a launch template line, with who owns it). The owner's rules: no installs for
   non-orchestrator roles; the hidden-half folders and the sets root keep asking or stay denied; a rule never wider
   than the form (no `Write(//tmp/**)`).
2. The ACT bundle for the forms you recommend allowing: `ACT-PERMISSIONS-3.md` (what, why, the exact JSON
   change, the class by `class-rules.yaml`, the rehearsal, the rollback), the manifest and apply script in the
   operator's form (copy the form of ACT-PERMISSIONS-2's bundle), and a rehearsal in a scratch copy of the settings
   files in your folder: each form's example now allowed, and each kept-asking form (B's install, D's mistaken path,
   the sets root, a hidden folder) still asked or denied. A launch-template change, if you recommend one, is a
   separate list item for an engineer ticket, not this ACT.

## Return
The twelve fields, short; the table; the ACT's files and rehearsal count. Estimate 1 to 1.5 h.
