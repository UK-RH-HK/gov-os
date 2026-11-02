# Brief: reviewer (FULL, read-only), DAEO-u4oz (W2-04), review 1 of the declared round

You are a fresh reviewer. Ticket `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`, at the head `b37b5c8f1741 (its full id: `git rev-parse HEAD`)`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-u4oz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04`, `w2/W2-04` and `b37b5c8f1741`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.cli.main retrieve "<question>" --json`, in this worktree, whose store the lead rebuilt at the head) for what you need to know before reading files at random. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph, if your session has it.
- **Reads (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read, print, search, diff or copy the held-out file under `governance/project/` or type its path, never read or name the qualification oracle; (d) the hidden half of any evaluation set. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put a longer probe in a script file in your session's own temporary folder and run that file. **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Run everything in the foreground, one command after another; your session ends with your last message. You write nothing, so no commit of yours will exist: return when your findings are complete.
- Write no file of the repository and make no commit. No `git checkout` of another commit, no `git reset`, no `git clean`, no stash. No subagents that write. Install nothing. No push, merge, rebase or tag. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild` (any form) here.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one from scratch in your temporary folder. Never write in `~/gov-os-workbench`. No file under any `.gov-runtime/` folder.
- **Row W2-L423's rule (DEC-911):** write commit hashes in your return as 12 digits, except the probed head, which you give in full once (the probe gate reads it); never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Disk (DEC-898):** your share is 3 GB and 150,000 files and folders, in the sandbox's own temporary folder; remove what you make when done.
- Inside a launched session `.gov-runtime/freeze` and the untracked dotfiles at the top show as placeholder device files: conclude nothing from them.
- Never ask or notify the owner; a question is a package in your return. Your temporary folder is removed when your session ends: every finding is in your final message.
- **Tests run no more than this (DEC-959 item 1):** do not re-run the acceptance or the scoped suites; the lead ran them (results below). Run the code with your own small probes.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md`: its KPI lines (seven success, one failure) and its `allowed_paths` (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`), its `list_rows`; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-04`).
- The sources: CAP-15 and CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md`); DEC-860 (retrieval in batches, ranked and stacked; never one giant query or context); W2-03's per-decision span and `content_hash`; DEC-768 (the dropped list's one order); DEC-552, DEC-568 (records that no longer stand); DEC-866.
- The specification and its addendum below (the same text both workers had; the CTO's decisions P-W2-04-2 (A) and P-W2-04-3 (b), DEC-1005, delegated: a semantic-free supplementary block; one batch = one of the context's own lookups, shown in `supplementary_batches`; a dependency ticket counted by its front matter). The lead's P3 calls: the same `CONTEXT_OVER_CEILING` refusal in both of the check's computations is reproduced and named (`REFUSED:`), any other error stays red; items left for lack of room are in `dropped` and named in `further_batch`; W2-M133 is a split outside this ticket.
- The change: `git diff w2/integrate...b37b5c8f1741` (code: `src/gov/context/__init__.py`, `src/gov/context/context_check.py`, `src/gov/retrieval/supplementary.py`; builder tests `tests/unit/context/`; acceptance tests `tests/acceptance/W2-04/` and the revised cases in `tests/acceptance/W2-54/` and `tests/acceptance/W1-41/`). Also what calls `gov.context.context`: `src/gov/close/command.py` (`_build_context`, the close turns a context error into `CONTEXT_FAILED`).

## The specification (W2-04, run 1): the same text for the test designer and the engineer

Sources: the ticket's KPI lines (`.tickets/DAEO-u4oz.md`), CAP-15 and its items CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md` §CAP-15), DEC-860 (retrieval in batches, ranked and stacked; never one giant query or context), W2-03's register entries (each decision with its own span and `content_hash`), and the list rows W2-H034, W2-L088, W2-L180, W2-L183, W2-L219, W2-M126, W2-M134, W2-M215, W2-M228, W2-M239, W2-M294, W2-M330 (`docs/plan/WAVE_2_LIST.md`; their sources are lines of `governance/project/bootstrap.md`: B:2340, B:1298, B:2341, B:2368, B:1300, B:1365, B:2339, B:2654, B:2782, B:1296). The public forms fixed below were settled by the lead inside the KPIs (a named error, three packet keys) so that tests and code written in parallel meet; anything not fixed here is the implementer's choice and is not tested.

The public interfaces: `gov context <ticket> [--json] [--budget N] [--brief] [--dry-run]` (`python3 -m gov.cli.main context …`, its JSON envelope `{"ok", "command", "result", "error": {"code", "message", "details"}}`, exit 0 on success, non-zero on an error); the in-process `gov.context.context(root, ticket, *, brief=False, budget=None, dry_run=False)`; the context-reproducibility check `python3 -m gov.context.context_check`, run in the project root (exit 0 green, non-zero otherwise, its lines on stdout); the store's records and register entries (`gov.records.records(root)` gives a register entry's `content_hash`, the sha256 of its span, W2-03).

**S1. The ceiling, and the ticket's own text (KPI 1; CAP-15, CAP-15.d).**
- The ceiling is `--budget N` tokens when given, else 6,000. A token is counted as the packet already counts it: the text's length in characters divided by 4, rounded up.
- Every packet that is returned with `ok: true` has `tokens <= budget.limit`, and `budget.used == tokens`. `tokens` counts the ticket's own text, every mandatory input's text as it is read (S3), and every supplementary item's text.
- The packet carries the ticket's own file text, verbatim and whole (front matter and body), under the key `ticket_text`. It is never dropped or shortened, whatever the pressure: under pressure the supplementary block is dropped first (CAP-15.d).

**S2. The refusal over the ceiling (KPI 2; AR-1, F-M5).**
- When the ticket's own text plus its mandatory inputs alone exceed the ceiling, `gov context` refuses: `ok: false`, error code `CONTEXT_OVER_CEILING`, a non-zero exit, a message that names the ticket, the ceiling and the mandatory size, and `details` holding at least `ticket`, `limit` and `mandatory_tokens`. With `--brief`, no packet file is written.
- It never returns `ok: true` with `tokens` over `budget.limit`, and supplementary items never take a packet over its ceiling.
- The failure KPI's case: DAEO-03pw (seven sources: DEC-070, DEC-088, DEC-092, DEC-096, MR-4, CAP-47, CAP-59; 814,821 tokens at the audit, because each decision was counted as the whole register) either fits (`ok: true`, under the ceiling) or refuses with `CONTEXT_OVER_CEILING`.

**S3. Each decision named by its own hash (KPI 3; W2-03, AR-1).**
- A mandatory input that is an entry of the decision register is read as its own span, never as the whole register file: its `sha256` (and its `constraint`) is the entry's own `content_hash`, the value the store gives for that id, and its token cost is its span's.
- Changing another entry of the register leaves its `sha256` unchanged; changing its own text changes it.
- A mandatory input that is a file of its own (a capability, a ticket, a specification) keeps its file's sha256, as today.

**S4. Reproducible (KPI 4; AR-9, W2-M239, W2-M294, W2-M330).**
- Two builds of one ticket's context give the same packet `hash`: in one process, in two separate processes, and on two stores each rebuilt from the same commit.
- The packet, and so its hash, is the same whether or not the semantic index answers (a live semantic index, or an unavailable one).
- Supplementary items of equal relevance (ties) are ordered by their `path`, then their `id`, whatever order the store, the index or the process gives them.
- The context-reproducibility check gives the same result on a stale store and on a fresh one, or it reports a stale store (built from another commit than `HEAD`) as unmeasured, by name, with a non-zero exit; it is never green on a stale store and red on a fresh one for the same tree.

**S5. An unreadable mandatory record (KPI 5; W2-H034, W2-L088, W2-M215, failure KPI).**
- A mandatory input whose file, or whose register span, cannot be read, or is missing, blocks the context (`BLOCKED`, non-zero exit, naming the id and the file) or is listed as not read (`"read": false`); it is never shown as read with the sha256 of empty content or with 0 tokens.
- A mandatory input whose record is SUPERSEDED, RETIRED or REJECTED does not satisfy the source: the context is `BLOCKED`, naming the id and its status.

**S6. The supplementary query (KPI 6; W2-M126).**
- The supplementary query is built from the ticket's KPI lines and its title, not from the title's first long word; the packet carries the query it used under the key `supplementary_query`.
- A planted document that matches only words of the ticket's KPI lines (none of its title's) can reach the supplementary block.

**S7. Batches, ranked and stacked; what is left is named (KPI 7; DEC-860).**
- The supplementary evidence is gathered by retrieval in batches, taken in order of relevance, and stacked in that order into the room the ceiling leaves after the ticket's text and the mandatory inputs. When room is left after one batch, the next batch is taken; the stack stops when the room or the evidence ends. No single query is asked for all evidence at once, and no batch is larger than the room can use.
- Stacking is strict rank order: it stops at the first item that does not fit; nothing ranked below an item that was left out is stacked.
- The packet names what it left for a further batch under the key `further_batch`: a list, in rank order, of `{"id", "path"}` of the ranked items that were not stacked for lack of room, beginning with the first one that did not fit, at most one batch long; an empty list when nothing was left.
- The `supplementary` block keeps its item form (`id`, `path`, `text`, `tokens`), in rank order. The `dropped` list keeps W2-54's form and its one order; a supplementary lookup failure is named there by its kind (W2-L180), never always as "index unavailable".

**S8. The context-reproducibility check's shapes (W2-M228, W2-L219).**
- A file of the ticket folder that the store holds no record of (a README, a ticket in a subfolder) is named and keeps the check red (it fails closed); when such files are the only content, the message says so, never "every ticket's context computation failed".
- A ticket file whose name ends otherwise than in lowercase `.md` (`.MD`, `.markdown`) is named and measured or refused by name, never unseen.
- Two ticket files that carry the same id are named as a duplicate id, and the check is not green.

**S9. One read of the ticket (W2-L183).** A context reads the ticket file once: its sources, dependencies, KPI lines, title and text all come from that one read.

**S10. Synthesis notes (W2-M134; CAP-15.f).** When the project holds synthesis notes (`.gov-runtime/synthesis/notes.json`), `gov context` runs their validator and acts on the result: notes that fail it are never presented as valid; the packet says whether they passed and names the failure codes. A project with no notes is unchanged.

**Never fail open.** An over-ceiling packet refuses; an unreadable record blocks or is marked not read; a stale store is not measured as fresh; a lookup failure is named, never hidden.

## The specification's addendum (W2-04, round 2; DEC-1005, delegated by the CTO, deciding P-W2-04-2 (A) and P-W2-04-3 (b)): the same text for the test designer and the engineer

Where this addendum differs from the run-1 text above, this addendum holds.

**S1, amended (P-W2-04-3 (b); CAP-15.b).** A dependency ticket (a ticket the ticket names in its `deps`) is counted by its front matter only: its id, its status, its title and its KPI lines, never its whole file. Its token cost is that part's. Its `sha256` stays its file's (S3, a file of its own). The ticket's **own** text is still carried whole under `ticket_text` and counted whole (S1 unchanged for it). A dependency ticket whose body is very large therefore does not push a packet over its ceiling; a change to a dependency's body alone leaves the packet's `tokens` unchanged.

**S4 and S7, the supplementary block stays semantic-free (P-W2-04-2 (A)).** The supplementary block is built from deterministic lexical evidence only; it never depends on whether a semantic index answers. A question that needs the semantic route (an embedder, its query cache, its query vectors) is asked through `gov retrieve`, not through `gov context`: `gov context` sends nothing to an embedder.

**S7a, what one batch is, and where it is shown (P-W2-04-2 (A), the reading of "one batch").** One batch is one of the context's own lookups of ranked supplementary evidence. The packet shows them under a new key, `supplementary_batches`: a list, one entry per batch the context took, in the order taken; each entry is an object with
- `items`: the list, in rank order, of `{"id", "path"}` of the ranked items that batch read;
- `limit`: the largest number of items that batch could read (`len(items) <= limit`).

The batches' items taken together, in order, are the rank order: the `supplementary` block is, item for item, the first items of that sequence (nothing in `supplementary` is absent from it), and `further_batch` begins with the first ranked item that was not stacked. When room is left after one batch and evidence remains, a further entry appears; when the evidence ends, the last entry holds fewer items than its `limit` (or none). `further_batch` is at most as long as the largest `limit`. A project whose supplementary lookup found nothing, or failed, has `supplementary_batches` as an empty list or the entries it did take, and names a failure in `dropped` by its kind (S7). `supplementary_batches` is part of the packet, so of its `hash`; it is deterministic like everything else in the packet (S4).

**The packet's keys.** A packet built with `ok: true` carries the keys it carried before this ticket, plus exactly these four: `ticket_text`, `supplementary_query`, `further_batch`, `supplementary_batches` (and `synthesis` only when the project holds synthesis notes, S10).

## The lead's results at this head

All at b37b5c8f1741 (this worktree's `src/`; `gov.__file__` = `/home/usain/gov-os-worktrees/W2-04/src/gov/__init__.py`):
- The store: rebuilt by the lead at this head (`rebuild_slot.sh`, rc 0, all three stores recreated, the semantic store's completeness check passed).
- The selection (`select_tests.py`): scope `scoped`, `core_changed` [], `unplaced` [].
- The scoped parallel run: 1 failed / 5,638 passed / 3 skipped. The one red is W2-55's backfill case (`test_w2_55_backfill::test_one_row_per_register_entry_at_the_base_in_its_order`): its proposal file stops at DEC-983 while the register at the base holds later entries; this branch touches neither file. Not this ticket's.
- W2-04's acceptance tests (in that run): 61 cases, 60 passed, 1 skipped (a case that runs only on the lead's machine). The engineer's `gov accept DAEO-u4oz`: all seven KPI lines pass.
- The W2-05 git-sweep case: green (the last fix, b37b5c8f1741, reads HEAD through the store loader's pinned git call; `context_check.py` starts no git of its own).
- The serial-only cases (4, all W2-54): 1 passed (query_vector), 3 failed, none this ticket's: `sandboxed_worker` (its planted repository lacks the hook file; red on the base too); `green_here` and `time_limit` (the context-reproducibility check ends with one error: ticket DAEO-i89t, filed on the base, names sources AR-5 and AR-6, which neither the store nor the external-references file holds, so its context is BLOCKED; the same code path on the base gives the same; the CTO has since fixed W2-120's sources on `w2/integrate`, DEC-1024). The check's 57 `REFUSED:` tickets count as passes by design (the lead's P3 call above).
- `gov check --json`: red context reproducibility (DAEO-i89t, above); red retrieval regression (the shared embedding server hung; time limit); yellow authority (DEC-1005, not in this tree's register) and product traceability (nothing to validate). The rest green.
- Collection: 19,154 of 19,156 collected (2 deselected), no error. Trailers: 16 commits, none lacking.
- Builder tests: `tests/unit/context/` 75 passed (the last engineer's run).

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:
- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open: here above all a packet returned `ok: true` over its ceiling, an unreadable or missing mandatory record shown as read, a record that no longer stands satisfying a source, a stale store measured as fresh, a context-reproducibility check green where two computations differ, a lookup failure hidden, a non-deterministic packet;
- and whether the revised W2-54 and W1-41 cases lowered any expectation (DEC-491, DEC-866): each still guards what it guarded, observed where the addendum puts it.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Judgement rules (carried word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## The structured verdict (DEC-1010 item 1)

Your return ends with one fenced block opened by three backticks and the word `verdict`, holding JSON only, one entry per KPI line of the ticket, with these line ids: `success-1` to `success-7` (the seven success lines in their order in the ticket's front matter) and `failure-1` (the failure line). Each entry: `{"kpi": "<line id>", "verdict": "pass|fail", "findings": [...]}`; each finding listed under the KPI line it bears on, with `id` (F1, F2, …, the same ids as in your text), `scope` (`in`: inside this ticket's KPIs and allowed paths; `out`: anything else), `ordinary_work` (`yes|no`) and `consequence` (`fails open|loses work|other`), exactly these words. A finding that bears on no KPI line goes under the line nearest to it, with `scope: "out"`. Example form: `{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, ...]}`. Before the block, one line `judgement: pass` or `judgement: fail`.

## The embedding server (today)

The shared embedding server (127.0.0.1:11434) is overloaded today. Nothing in this review needs it: the supplementary block is semantic-free by design. Wrap every `gov retrieve` call in `timeout 120`; if it does not answer, read the named files instead and say so. Do not probe live semantic retrieval.

## Return

The head you probed (in full, once), your verdict (`pass` or `fail`, by the rules above), and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound. The lead turns your return into the probe record; you write nothing and repair nothing (MR-4).

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

After the twelve fields: your verdict and the findings as above, ending with the `verdict` block; then a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
