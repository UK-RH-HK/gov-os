# Brief rev-1: independent auditor for DAEO-g29a (W2-113), STANDARD review round 1, class C2

You are the independent auditor (a fresh, read-only session) for ticket DAEO-g29a (W2-113: an adopted product's CTO is
named at adoption — Stage A0 creates the coordination ticket and writes the roster's `coordination_ticket` key; the
install refusal, when the rule cannot run, names `GOV_TICKET` and says how to set the key in true words). Audit the
branch head **6542b7ec525b** of `w2/W2-113` in /home/usain/gov-os-worktrees/W2-113 against the ticket's KPI lines
(success-1, success-2, failure-1, failure-2) and its `## Interface` section (I1, I2, I3 and the readings), which the
owner decided (DEC-1156 (4); I2 (iii) as PKG-3 (b), DEC-1157 (15)). The `moved:` line (role files, W2-33's) and the
`lifted:` line (the quiet-hours hook, DEC-1083) are out of scope.

You change nothing in the repository: no edit, no commit, no merge. Your verdict is your return.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g29a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must work.
If (a) wrote the file, stop there and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-g29a`).

## What to read
| what | path |
|---|---|
| the ticket (KPI lines; `## Interface`) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g29a.md (also in the context packet below) |
| the change | `git -C /home/usain/gov-os-worktrees/W2-113 diff 159abfe06..6542b7ec525b -- src tests/unit` (src/gov/adopt/stages.py `_coordination`, `a0`; src/gov/guard/install.py `coordination_ticket` docstring, `cto_install`'s no-key refusal; tests/unit/adopt/test_w2_113_coordination.py) |
| the independent acceptance suite (74 cases, all green at this head by `gov accept`) | tests/acceptance/W2-113/ (README.md maps KPI lines to cases; two cases revised to PKG-3 (b) in 3352f754b87e) |
| the guard that decides (rule 4 calls `cto_install`) | template/governance/kernel/hooks/pretooluse.py; W2-110's suites tests/acceptance/W2-110/, tests/unit/guard/test_w2_110_cto_install.py (line 172 pins "Set the top-level key") |
| A0's machinery | src/gov/adopt/project.py (`Run.finish`, the commit), src/gov/adopt/safety.py (`setup`), src/gov/tasks/tickets.py (`create`, `TK_REL`), governance/kernel/bin/tk in a generated product |
| W2-110's probe record (its F5 is the complaint success-2 answers) | docs/probes/DAEO-3r1j/ |
| the sources (by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-971 (item 4), DEC-957, DEC-982, DEC-974, DEC-1156 (4), DEC-1157 (15), DEC-1052 |

Search with Read, Grep and Glob; search again once in different words if the first does not answer (DEC-1065).

## Known to the lead (judge them; do not re-report them as new)
- The engineer's choices where the Interface is silent: a roster key that names no existing ticket is left as it is
  (A0 completes, creates nothing, its record says so; the guard stays closed); a roster that is not a readable mapping,
  or cannot take the key as one added line, is left as it is likewise; `tk` present but failing makes A0 refuse
  (`ADOPT_COORDINATION_TICKET_FAILED`) and write nothing; a second A0 run creates no second ticket (the key now names
  one). Say whether each is within I1/I2 and safe (fails closed), or contradicts them.
- Older suites red inside the worker sandbox, from the code-graph tool at A3 (`ADOPT_CODE_GRAPH_UNREADABLE`) and at
  `gov rebuild`: W1-41 (16), W2-23 (3), W2-52 (56 errors), W2-05 (1). The lead's verify run (outside the sandbox)
  judges them; you need not.
- `tests/acceptance/W2-23/test_w2_23_space.py:99` pins six kernel hooks and finds a seventh (`context_watch.py`), not
  A0's doing.

## What to probe (at least these; add your own)
1. Each KPI line and failure line against the code, not only the tests; where a test is weaker than its line, probe
   the line directly. failure-2 by every session form you can think of (roles, subagent types, an orchestrator on
   another ticket, by id and by WBS id, no ticket, odd spellings). Scope: `git diff --name-only 4ede6c3fee3d..6542b7ec525b`
   against the ticket's allowed_paths (tests/acceptance/W2-113/ is the test designer's; anything from the merge of
   w2/integrate is not this ticket's).
2. I1 end to end: a product generated from the template (copier, then `rulesync generate`, as W2-110's support does),
   committed, then `gov adopt --lite --stage A0` (this worktree's `src` on PYTHONPATH): the ticket's exact title
   (`<folder> coordination`), `class: coordination`, `state_class`, the roster key, A0's record entries (old keys kept,
   new ones added), everything in A0's one commit, the tree clean, the backup ref; then the hook's decisions.
3. I2: (i) a key by id and by WBS id kept, nothing created; (ii) the roster's other keys, comments, blank lines, order,
   a file with no final newline, an empty file, a comment-only file, odd YAML (flow mapping, anchors, a document
   marker `---`, CRLF line ends, a tab, a duplicate key, the key nested under another key) — does A0 ever write a
   roster the guard reads differently from what A0 recorded?; (iii) `tk` missing: success, no ticket, no key, the
   record says so in words, the guard closed and its refusal naming `GOV_TICKET`.
4. Failure paths of A0: `tk create` failing or printing something unexpected; the ticket file left behind or lost
   (A0 reads it back and deletes it before committing — what if the commit then fails?); A0 run twice; A0 when
   `.tickets/` holds a ticket with the same title; whether anything is written to the tree on a refusal.
5. success-2's words in each case the rule cannot run (no roster, no key, empty/null value, a key naming no ticket,
   unreadable roster): names `GOV_TICKET`, says how to set the key, no claim that a key was set when none was, still
   a refusal, `ESCALATE`'s tail kept, W2-110's line-172 sentence kept. Read the words as a CTO would: are they true
   in each case, and do they tell the CTO what to do?
6. No other behaviour of the guard changed: W2-110's acceptance and unit suites at this head.

Your probes are read-only on the repository and run by Bash in your own TMPDIR (DEC-1144 (7)): use the sandbox's
TMPDIR (outside the repository); plant everything there; scripts longer than one line go there too. Any pytest goes
through the heavy-slot gate:
`TMPDIR=<your tmp> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your tmp> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-113/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
A heavy-slot or resource refusal is a wait. Never `gov adopt`, `gov close` or `gov pause` on a real repository or
worktree (on a planted product in your TMPDIR it is the probe). Never open the evaluation sets' root or any hidden or
memory-verdict folder. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
reach the same effect by another form (DEC-1142 (9)). Clean up your TMPDIR trees before you return.

The ticket's context packet (`gov context DAEO-g29a --role independent-auditor --budget 12000`) follows.

----

{
  "ticket": "DAEO-g29a",
  "ticket_text": "---\nid: DAEO-g29a\nstatus: in_progress\ndeps: [DAEO-3r1j, DAEO-siiz]\nlinks: [DAEO-3r1j]\ncreated: 2026-10-31T23:05:58Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-113\ntags: [wave-2, implementation, adoption, standard]\nwbs_id: W2-113\ntitle: 'An adopted product''s CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestrator role file states the CTO-only install rule, the refusal names GOV_TICKET (W2-110''s P-W2-110-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-3r1j\n- DAEO-siiz\nallowed_paths:\n- src/gov/adopt/stages.py\n- template/governance/kernel/hooks/permission_request.py\n- src/gov/guard/install.py\n- tests/unit/adopt/test_w2_113*\n- docs/probes/DAEO-g29a/**  # the probe record (the CTO, 2026-11-12)\nkpis:\n  success:\n  - 'Adoption writes the project''s `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit Verify: a planted repository is adopted with no hand edit: the project''s config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision for an install by the session on that ticket is ask, and for any other session is refuse. [DEC-971 item 4, DEC-982]'\n  - 'The refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110''s review F5); it stays closed Verify: planted projects with no key and with a key naming no ticket: the install refusal text names `GOV_TICKET` and says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. [DEC-971 item 4]'\n  failure:\n  - 'An adopted project whose CTO''s installs are refused until the key is written by hand. Verify: a freshly adopted planted repository: the CTO session''s install is asked at once (not refused) with no key edited by hand; a refusal there is the failure.'\n  - 'Any session but the CTO''s asked or let through. Verify: planted engineer, test-designer, auditor and a second orchestrator session on another ticket each attempt an install in the adopted planted repository: each is refused, none is asked or let through.'\n  moved:\n  - 'Both orchestrator role-file copies state the CTO-only install rule (was S2) and no copy keeps the old rule (was F2) [moved to W2-33, DEC-1156 (4): one writer for orchestrator.md, the product-spec role (DEC-995, DEC-996 (1))]'\n  lifted:\n  - 'The kernel ships a quiet-hours permission hook (the host''s PermissionRequest event; this repository''s `governance/project/orchestration/tools/permission_request.py` as the model): inside the configured quiet hours it refuses at once, with a message naming the morning package, and queues the call under `.gov-runtime/`; outside them it gives no answer (the normal prompt); any error inside them refuses; every prompt is recorded; adoption wires it into the adopted CTO''s local settings only, with onFailure block; in a freshly adopted planted repository a prompting call at a forced 03:00 is refused and queued, and at 12:00 is not [DEC-991, DEC-994 item 3] [lifted (was S4), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\nprofile: STANDARD\nsources:\n- DEC-971\n- DEC-957\n- DEC-982\n- DEC-974\n- DEC-1083\n- DEC-991\n- DEC-994\nest_loc: 60\nacceptance_tests:\n  path: tests/acceptance/W2-113/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted repository adopted from the template\ntrack: B\nlist_rows: []\n---\n# W2-113 An adopted product's CTO is named at adoption\n\nThe owner's decision on P1-NEW-TICKETS-2026-10-31 T1 (DEC-982), from W2-110's P-W2-110-2.\n\n- **Why:** W2-110 makes the kernel's guard ask the owner for an install only from the orchestrator on the project's coordination ticket (DEC-971 item 4), with the key \"set at adoption\", but nothing writes it at adoption; the role file still states the old rule (review F3) and the refusal's words mislead when the rule cannot run (F5).\n- **The work:** a product-spec worker rewrites the role file's lines (both copies), then an engineer makes the adopt step write the key and the refusal's words, one after the other.\n- **Order:** after W2-110 (`DAEO-3r1j`) and W2-52 (`DAEO-siiz`, which holds the adopt files); before EXAMIN's copy (W2-27). W2-33 holds the rest of the role file: this ticket changes only the install lines.\n\n## Interface (DEC-1052; PKG-1 (a), the owner, DEC-1156 (4), 2026-11-12)\n\n- **I1 Stage A0 creates it,** inside `src/gov/adopt/stages.py` only (no new flag): A0 creates the coordination ticket through `gov.tasks.tickets.create(root, \"<project> coordination\")` with `class: coordination`, writes `governance/project/roster.yaml` with a top-level `coordination_ticket: <new id>`, and records both in A0's record, committed in A0's commit with its set-up files (`safety.setup`).\n- **I2 The three defaults:** a roster that already names an existing ticket: A0 keeps it and creates nothing; a roster without the key: A0 adds the key and changes nothing else; `tk` missing: A0 completes without creating the ticket or the key, and its record says so; the guard stays closed (every install refused, the refusal naming `GOV_TICKET` and how to set the key) (PKG-3 (b), the owner, DEC-1157 (15); was: A0 refuses and writes nothing).\n- **I3 \"A planted repository adopted\"** for the tests: a planted git repository with the template copied in (copier, then `rulesync generate`, as in W2-110's suite), then `gov adopt --lite --stage A0`; then the guard's decisions for the orchestrator on that ticket (ask), and for an engineer, a test designer, an auditor and an orchestrator on another ticket (each refused).\n- **Note for W2-88 and W2-174:** A0 gains this output; keep it at merge.\n- **PKG-2 (b):** the role-file lines (was S2, F2) moved to W2-33; this ticket is engineer work only.\n- **The test designer's readings, confirmed by the CTO (DEC-1112 (3)):** `<project>` is the repository's folder name and the title is exact; a roster key may name its ticket by id or WBS id, as the guard resolves it; A0 keeps the roster's comments and line order. The refusal keeps the sentence \"Set the top-level key\" (W2-110's unit test at line 172).\n",
  "authority": [
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-3r1j",
      "sha256": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "reason": "declared in sources",
      "tokens": 390
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    }
  ],
  "mandatory": [
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-3r1j",
      "sha256": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "reason": "declared in sources",
      "tokens": 390
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    }
  ],
  "supplementary": [
    {
      "id": "DEC-980",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  2. **P-W2-05-W2-72 (a):** a fresh independent test designer revises W2-72's four cases that a failing `git` first on `PATH` no longer reaches (containment takes git by absolute path, DEC-802 P-B1-2) onto routes containment still takes, `Rewrite-Reason: DEC-802 (P-B1-2)`, nothing lowered. In W2-05's resume.\n  3. **W2-05's H and R3-1 are already the owner's decisions:** DEC-971 item 3 (H (a) refined: DEC-805's comparison excepts exactly the two hook events ACT 1 lifted, named in it, ending when they return with W2-08) and R3-1 (b). W2-05's lead started before DEC-971 (12:50); its resume carries them.\n  4. **New tickets, to the owner as P1s (DEC-974), not decided here:** W2-110's P-W2-110-2 (the adopt step writes the coordination-ticket key; both orchestrator role files rewritten; the refusal names `GOV_TICKET`) and W2-108's W1-28 follow-up (its copy check reads message text as whole-tree routes). W2-110's P-W2-110-3 (renew the pinned gov after its merge) is ACT 2's re-pin (DEC-954 item 6).\n- **Where it goes (DEC-851):** this register; the two resume briefs; `packages/P1-NEW-TICKETS-2026-10-31.md`; the daily document.\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 295
    },
    {
      "id": "ddd4445ae271c4675546d540",
      "path": "governance/project/orchestration/packages/P1-NEW-TICKETS-2026-10-31.md",
      "text": "## T1. W2-113: an adopted product's CTO is named at adoption (W2-110's P-W2-110-2)\n\n1. **Context:** W2-110 (`DAEO-3r1j`, FULL, built, its review passed) makes the kernel's guard ask the owner for an install only from the orchestrator on the project's coordination ticket (DEC-971 item 4). Its KPI says that key (`coordination_ticket` in the project's roster) is \"set at adoption\".\n2. **What happened:** no path of W2-110 can write the key at adoption; and its reviewer found the template's orchestrator role file (both copies) still says the guard asks on every install, naming neither the key nor the CTO's `GOV_TICKET` (F3), and that the refusal's words mislead when the rule cannot run (F5).\n3. **Why it matters:** an adopted product (EXAMIN first) starts with no key, so its CTO's installs are refused until someone writes it by hand; the role file tells its CTO the old rule.\n4. **Options:**\n",
      "tokens": 225
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-112 | A | **New (DEC-982, P-RERANKER-1 (a)).** One reranker serves every session: a shared, on-demand service on a local socket; each search falls back to a private reranker, else an unranked order marked `rerank: unavailable` (`DAEO-clon`) | implementation | engineer | FULL | W2-32 | 200 | DEC-982, DEC-979, DEC-374 |\n| W2-113 | A | **New (DEC-982, P1-NEW-TICKETS-2026-10-31 T1).** An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key; the orchestrator role file states the CTO-only install rule; the refusal names `GOV_TICKET` (`DAEO-g29a`) | implementation | engineer | STANDARD | W2-110, W2-52 | 60 | DEC-982, DEC-971 |\n| W2-114 | A | **New (DEC-982, P1-NEW-TICKETS-2026-10-31 T2).** W1-28's whole-tree copy check reads code, not message text; every true copy still found (`DAEO-4eux`) | test-revision | independent-test-designer | LITE | none | 40 | DEC-982, DEC-385, DEC-906 |\n",
      "tokens": 234
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "### 3.8 The cap removed (the owner, 2026-11-12)\n\nThe owner's order (chat, 2026-11-12 ~02:30; the CTO records it as DEC-1141, replacing DEC-1118 (A) entirely): no\nsession has a token cap; the CTO, leads, workers and helpers each use their model's full window and compact, the\ncheckpoint and handover written by the hook before compaction and the summary opening with the read-first line. The\nowner withdrew the approval of `3a580a4b4d42`, because those bytes carry the cap. This replaces P4 (section 3.4) and\nthe CTO-only branch of DEC-1140 (4)'s delta.\n\n- **Code** (`c10be8fd0266`): `HANDOVER_CAP` and the coordination-ticket test (`is_cto`) removed; every session's window\n  is its own model's (`limit(model)`); the CTO's wording branch went with the test, so an orchestrator on the\n  coordination ticket gets an orchestrator's text (its CHECKPOINT via `checkpoint_rel`, its RESUME HERE section) and no\n  longer names `DECIDED-NOT-DONE.md` or `report-state.json` (P2's path is gone with the branch). Kept: R8's order, the\n  re-arm below 50 %, the subagent skip, the 256 KiB tail, exit 0 on any error.\n",
      "tokens": 276
    },
    {
      "id": "W2-176-CIT-P",
      "path": "docs/changes/W2-176-CIT-P.md",
      "text": "  longer names `DECIDED-NOT-DONE.md` or `report-state.json` (P2's path is gone with the branch). Kept: R8's order, the\n  re-arm below 50 %, the subagent skip, the 256 KiB tail, exit 0 on any error.\n- **Tests first** (`e36a9c51b`, red on the hook at `4dec7ec3c72c`: 33 failed, 44 passed): a lead, an engineer or a test\n  designer on each 1M model silent at 170k, 180k, 200k and 849,999 and reminded at 850k (18 red); no session (the\n  CTO, a lead, an engineer, a test designer) reminded below 85 % of its own window, four 1M models and an unknown one\n  (12 red: the non-CTO sessions on 1M models); an Opus transcript at 180k silent for every session (1 red); the\n  coordination ticket changes nothing in the text (2 red); the wording names no 200k, limit or cap (green before and\n  after, a guard). Removed: the CTO-only cases (DECIDED-NOT-DONE and report-state wording, the coordination-ticket\n  identity cases, the 180k CTO/lead contrast). Two lead cases planted at 190k on Opus moved to 900k.\n- **Green at `c10be8fd0266`**: the file 77 passed; `tests/unit/hooks` 197 passed, 36 deselected (`tests/conftest.py`'s\n",
      "tokens": 279
    },
    {
      "id": "3db3a8d4d6d72ec65759c616",
      "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py",
      "text": "\"\"\"KPI success 2 (fail closed) and failure 3 (\"A missing or unreadable coordination-ticket key read as 'ask\neveryone'\").\n\nThe coordination ticket is named in the project's own configuration, one key set at adoption: the top-level\n``coordination_ticket`` of ``governance/project/roster.yaml`` (DEC-971 item 4). With no roster, no such key, an\nempty or non-text value, a roster that cannot be read or parsed, or a key that names no ticket of the project, every\nsession's install is refused, the CTO's included, and the refusal says how to set it: it names the file and the key.\nNever an ``ask`` and never a pass-through.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport pytest\n\nimport w2_110_support as support\nfrom w2_110_support import (AUDITOR, COORDINATION, ENGINEER, ENGINEERING, MISSING_TICKET_ID, MISSING_WBS_ID,\n                            ORCHESTRATOR, PRODUCT_SPEC, RESEARCH, TEST_DESIGNER, TICKET_LEAD, OWN_TICKET, Session,\n                            cto)\nfrom w1_04_support import command_id\n\n\n",
      "tokens": 251
    },
    {
      "id": "38bf132c63682fa983e7923b",
      "path": "tests/acceptance/W2-110/README.md",
      "text": "### KPI success 2 and failure 3: fail closed (`test_w2_110_fail_closed.py`, 63 cases, 62 red)\n\nKPI success 2: \"with no such key, or a key naming no ticket, every session's install is refused and the refusal says\nhow to set it (fail closed)\". Failure 3: \"A missing or unreadable coordination-ticket key read as 'ask everyone'.\"\n\nEach case asserts that the decision is `deny`, so never `ask` and never a pass-through, and that the reason \"says how\nto set it\".\n\n| Case | What it holds | Red on the base |\n|---|---|---|\n| `test_the_cto_s_install_is_refused_when_the_key_cannot_be_read` \u00d7 18 | every fail-closed configuration; the orchestrator on `DAEO-c0rd` | R1 |\n| `test_an_orchestrator_whose_ticket_is_what_the_key_holds_is_refused` \u00d7 9 | `GOV_TICKET` holds the key's words exactly: `DAEO-gone`, `P-99`, `\"\"`, `\"   \"` and `\"7\"`, or is unset while the key is null, missing, or in a roster that is not there (`no-roster`, `as-generated`) | R1 |\n",
      "tokens": 236
    },
    {
      "id": "cd1946d017a297faecfd7d3b",
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "text": "- W2-157 (`DAEO-ozyt`, P2, engineer, open \u00b7 after the lift): The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills in\n- W2-171 (`DAEO-k1e2`, P2, engineer, open \u00b7 after the lift): The memory audit's measure: the control, the retrieval figures, the judged reader run, the fault rule, the mis\n**Batch 7**\n- W2-15a (`DAEO-rd0g`, P1, research, open): EXP-003, pass 1: the baseline\n- W2-60a (`DAEO-cv58`, P1, engineer, in progress): The role, its skills and its model and effort loaded at launch; the launch record\n- W2-111 (`DAEO-qvff`, P1, independent-test-designer, open): The hook-latency cases time the hook's own work: W1-02's, W1-05's and W2-57's p95-under-100-ms cases judge the\n- W2-113 (`DAEO-g29a`, P1, engineer, open): An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestr\n- W2-115 (`DAEO-emq1`, P1, engineer, open): gov close, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit\n",
      "tokens": 262
    },
    {
      "id": "21b7ac474be8b6bf304370e0",
      "path": "tests/acceptance/W2-113/test_w2_113_others_refused.py",
      "text": "def test_a_worker_on_the_coordination_ticket_is_refused(adoption, decide, role):\n    \"\"\"The key names the ticket, but only the orchestrator's session on it is the CTO's.\"\"\"\n    adopted = adoption(\"standard\")\n    support.assert_succeeded(adopted)\n    ticket = adopted.new_ticket()\n    assert_refused(decide(Session(f\"{role}-on-the-coordination-ticket\", role, ticket)), f\"the {role} on {ticket}\")\n",
      "tokens": 99
    },
    {
      "id": "dff1aa90cea0dd4cf4088413",
      "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py",
      "text": "    Session(\"no-role-on-the-coordination-ticket\", None, COORDINATION.id),\n    Session(\"empty-role-on-the-coordination-ticket\", \"\", COORDINATION.id),\n    Session(\"unknown-role-owner-on-the-coordination-ticket\", \"owner\", COORDINATION.id),\n    Session(\"no-role-and-no-ticket\", None, None),\n]\nSUBAGENTS_IN_THE_CTO_S_SESSION = [\n    Session(f\"{subagent}-subagent-in-the-cto-s-session\", ORCHESTRATOR, COORDINATION.id, subagent)\n    for subagent in (*OTHER_ROLES, \"general-purpose\", \"Explore\")]\nORCHESTRATOR_SUBAGENTS_ELSEWHERE = [\n    Session(\"orchestrator-subagent-in-a-lead-s-session\", ORCHESTRATOR, ENGINEERING.id, ORCHESTRATOR),\n    Session(\"orchestrator-subagent-in-an-orchestrator-session-without-a-ticket\", ORCHESTRATOR, None, ORCHESTRATOR),\n    Session(\"orchestrator-subagent-in-an-engineer-s-session\", ENGINEER, ENGINEERING.id, ORCHESTRATOR),\n    Session(\"orchestrator-subagent-in-an-engineer-s-session-on-the-coordination-ticket\", ENGINEER,\n            COORDINATION.id, ORCHESTRATOR),\n    Session(\"orchestrator-subagent-in-a-test-designer-s-session-on-the-coordination-ticket\", TEST_DESIGNER,\n            COORDINATION.id, ORCHESTRATOR),\n",
      "tokens": 286
    },
    {
      "id": "c6237a2cc0379aac14e8577b",
      "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py",
      "text": "def assert_fail_closed(answer, command, who, configuration):\n    assert answer.decision == \"deny\", (\n        f\"with the configuration {configuration}, `{command}` by {who} was {answer.decision}: a coordination-ticket \"\n        f\"key that cannot be read refuses every session's install, the CTO's included (DEC-971 item 4): \"\n        f\"{answer.describe()}\")\n    assert support.says_how_to_set_the_key(answer.reason), (\n        f\"with the configuration {configuration}, the refusal of `{command}` by {who} does not say how to set the \"\n        f\"coordination ticket: it must name {support.ROSTER_REL} and the key {support.KEY}: {answer.reason!r}\")\n",
      "tokens": 162
    },
    {
      "id": "e833d86f946f28d52b432908",
      "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py",
      "text": "\n\nEVERY_SESSION = [\n    cto(COORDINATION.wbs, \"cto-by-wbs-id\"),\n    Session(\"cto-orchestrator-subagent\", ORCHESTRATOR, COORDINATION.id, ORCHESTRATOR),\n    Session(\"lead-on-an-engineer-s-ticket\", ORCHESTRATOR, ENGINEERING.id),\n    Session(\"orchestrator-without-a-ticket\", ORCHESTRATOR, None),\n    *[Session(f\"{role}-on-its-own-ticket\", role, OWN_TICKET[role].id)\n      for role in (ENGINEER, TEST_DESIGNER, PRODUCT_SPEC, AUDITOR, RESEARCH, TICKET_LEAD)],\n    Session(\"no-role-on-the-coordination-ticket\", None, COORDINATION.id),\n    Session(\"orchestrator-subagent-in-an-engineer-s-session\", ENGINEER, ENGINEERING.id, ORCHESTRATOR),\n]\n\n\n@pytest.mark.parametrize(\"configuration\", [\"no-roster\", \"unparsable\"])\n@pytest.mark.parametrize(\"session\", EVERY_SESSION, ids=str)\n",
      "tokens": 192
    },
    {
      "id": "88d7f398e20f8e466f52a3b8",
      "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py",
      "text": "\n\n@pytest.mark.parametrize(\"session\", [\n    Session(\"orchestrator-on-the-first-coordination-ticket\", ORCHESTRATOR, COORDINATION.id),\n    Session(\"orchestrator-on-the-first-coordination-ticket-by-wbs-id\", ORCHESTRATOR, COORDINATION.wbs),\n    Session(\"orchestrator-on-the-product-s-W2-00-ticket\", ORCHESTRATOR, THIS_REPOSITORYS_ID.id),\n], ids=str)\n",
      "tokens": 87
    },
    {
      "id": "a784a8af4ce32b8223b43ccf",
      "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py",
      "text": "    Session(\"orchestrator-subagent-in-a-test-designer-s-session-on-the-coordination-ticket\", TEST_DESIGNER,\n            COORDINATION.id, ORCHESTRATOR),\n    Session(\"orchestrator-subagent-in-a-session-without-a-role-on-the-coordination-ticket\", None,\n            COORDINATION.id, ORCHESTRATOR),\n]\nEVERY_OTHER_SESSION = (LEADS_AND_OTHER_ORCHESTRATORS + OTHER_ROLE_SESSIONS + NO_ROLE_SESSIONS\n                       + SUBAGENTS_IN_THE_CTO_S_SESSION + ORCHESTRATOR_SUBAGENTS_ELSEWHERE)\n\n\n@pytest.mark.parametrize(\"session\", EVERY_OTHER_SESSION, ids=str)\n",
      "tokens": 138
    },
    {
      "id": "b83d8a73a596d78c34cc11f4",
      "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py",
      "text": "\n\nLEADS_AND_OTHER_ORCHESTRATORS = [\n    Session(\"lead-on-an-engineer-s-ticket\", ORCHESTRATOR, ENGINEERING.id),\n    Session(\"lead-on-an-engineer-s-ticket-by-wbs-id\", ORCHESTRATOR, ENGINEERING.wbs),\n    Session(\"orchestrator-on-another-orchestration-ticket\", ORCHESTRATOR, OTHER_ORCHESTRATION.id),\n    Session(\"orchestrator-on-the-product-s-W2-00-ticket\", ORCHESTRATOR, THIS_REPOSITORYS_ID.id),\n    Session(\"orchestrator-on-the-product-s-W2-00-ticket-by-wbs-id\", ORCHESTRATOR, THIS_REPOSITORYS_ID.wbs),\n    Session(\"orchestrator-without-a-ticket\", ORCHESTRATOR, None),\n    Session(\"orchestrator-with-an-empty-ticket\", ORCHESTRATOR, \"\"),\n    Session(\"orchestrator-on-a-ticket-the-product-does-not-have\", ORCHESTRATOR, MISSING_TICKET_ID),\n]\nOTHER_ROLE_SESSIONS = (\n    [Session(f\"{role}-on-its-own-ticket\", role, OWN_TICKET[role].id) for role in OTHER_ROLES]\n    + [Session(f\"{role}-on-the-coordination-ticket\", role, COORDINATION.id) for role in OTHER_ROLES])\nNO_ROLE_SESSIONS = [\n    Session(\"no-role-on-the-coordination-ticket\", None, COORDINATION.id),\n    Session(\"empty-role-on-the-coordination-ticket\", \"\", COORDINATION.id),\n",
      "tokens": 282
    },
    {
      "id": "915a32b38e4f234f34c79422",
      "path": "tests/acceptance/W2-110/test_w2_110_unchanged.py",
      "text": "\n\nSUDO_SESSIONS = [\n    (\"key-by-id\", LEAD),\n    (\"key-by-id\", ENGINEER_SESSION),\n    (\"key-by-id\", RESEARCH_IN_ITS_FOLDER),\n    (\"key-by-id\", Session(\"no-role-on-the-coordination-ticket\", None, COORDINATION.id)),\n    (\"key-by-id\", CTO_SUBAGENT),\n    (\"no-roster\", cto()),\n    (\"unparsable\", cto()),\n]\n\n\n@pytest.mark.parametrize(\"configuration,session\", SUDO_SESSIONS, ids=[f\"{c}-{s}\" for c, s in SUDO_SESSIONS])\n",
      "tokens": 104
    }
  ],
  "supplementary_query": "An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestrator role file states the CTO-only install rule, the refusal names GOV_TICKET (W2-110's P-W2-110-2)\nAdoption writes the project's `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit Verify: a planted repository is adopted with no hand edit: the project's config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision for an install by the session on that ticket is ask, and for any other session is refuse. [DEC-971 item 4, DEC-982]\nThe refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110's review F5); it stays closed Verify: planted projects with no key and with a key naming no ticket: the install refusal text names `GOV_TICKET` and says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. [DEC-971 item 4]\nAn adopted project whose CTO's installs are refused until the key is written by hand. Verify: a freshly adopted planted repository: the CTO session's install is asked at once (not refused) with no key edited by hand; a refusal there is the failure.\nAny session but the CTO's asked or let through. Verify: planted engineer, test-designer, auditor and a second orchestrator session on another ticket each attempt an install in the adopted planted repository: each is refused, none is asked or let through.",
  "further_batch": [
    {
      "id": "fe6ad702423402a2295b969b",
      "path": "tests/acceptance/W1-47/README.md"
    },
    {
      "id": "07f1efd527e854f8b012ae8f",
      "path": "tests/acceptance/W1-05/README.md"
    },
    {
      "id": "bb51cab5ee7b4177e7e7d2d1",
      "path": "tests/acceptance/W1-46/README.md"
    },
    {
      "id": "f0d894ff704d72f603f59438",
      "path": "tests/acceptance/W1-50/w1_50_freeze_README.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DEC-980",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "ddd4445ae271c4675546d540",
          "path": "governance/project/orchestration/packages/P1-NEW-TICKETS-2026-10-31.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "W2-176-CIT-P",
          "path": "docs/changes/W2-176-CIT-P.md"
        },
        {
          "id": "3db3a8d4d6d72ec65759c616",
          "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py"
        },
        {
          "id": "38bf132c63682fa983e7923b",
          "path": "tests/acceptance/W2-110/README.md"
        },
        {
          "id": "cd1946d017a297faecfd7d3b",
          "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md"
        },
        {
          "id": "21b7ac474be8b6bf304370e0",
          "path": "tests/acceptance/W2-113/test_w2_113_others_refused.py"
        },
        {
          "id": "dff1aa90cea0dd4cf4088413",
          "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c6237a2cc0379aac14e8577b",
          "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py"
        },
        {
          "id": "e833d86f946f28d52b432908",
          "path": "tests/acceptance/W2-110/test_w2_110_fail_closed.py"
        },
        {
          "id": "88d7f398e20f8e466f52a3b8",
          "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py"
        },
        {
          "id": "a784a8af4ce32b8223b43ccf",
          "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py"
        },
        {
          "id": "b83d8a73a596d78c34cc11f4",
          "path": "tests/acceptance/W2-110/test_w2_110_others_refused.py"
        },
        {
          "id": "915a32b38e4f234f34c79422",
          "path": "tests/acceptance/W2-110/test_w2_110_unchanged.py"
        },
        {
          "id": "fe6ad702423402a2295b969b",
          "path": "tests/acceptance/W1-47/README.md"
        },
        {
          "id": "07f1efd527e854f8b012ae8f",
          "path": "tests/acceptance/W1-05/README.md"
        },
        {
          "id": "bb51cab5ee7b4177e7e7d2d1",
          "path": "tests/acceptance/W1-46/README.md"
        },
        {
          "id": "f0d894ff704d72f603f59438",
          "path": "tests/acceptance/W1-50/w1_50_freeze_README.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "07f1efd527e854f8b012ae8f",
      "reason": "budget exceeded"
    },
    {
      "id": "bb51cab5ee7b4177e7e7d2d1",
      "reason": "budget exceeded"
    },
    {
      "id": "f0d894ff704d72f603f59438",
      "reason": "budget exceeded"
    },
    {
      "id": "fe6ad702423402a2295b969b",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 11996,
  "budget": {
    "limit": 12000,
    "used": 11996
  },
  "left_out": {
    "count": 11,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-798",
      "DEC-869",
      "DEC-875",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "b39c239c7da7e1536b60ff6b20a952871ef08f4c36ee7e3e7f1957f1bb9968dd"
}


----

## Return (your last message; nothing else is read)
First a fenced verdict block, exactly:
```verdict
ticket: DAEO-g29a
head: 6542b7ec525b
round: 1
verdict: PASS | FAIL
blocking: <n>
```
PASS only when no finding is blocking (a KPI or failure line not met, an Interface item I1/I2/I3 contradicted, a
session other than the CTO's asked or let through, the CTO refused in a freshly adopted product, a refusal that opens,
or words that claim a key was set when none was). Then each finding: id (R1-<n>), severity (blocking / non-blocking),
in scope or not, the KPI line or Interface item, file:line, what you did to show it (the probe's command and its
output, short), whether it happens in ordinary work (yes/no, because ...), and the behaviour that would be right
(described, not a patch). Then the probes you ran with their results (counts), and your judgement on each of the
lead's known items above. Then the twelve fields, each a labelled line ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action, and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
