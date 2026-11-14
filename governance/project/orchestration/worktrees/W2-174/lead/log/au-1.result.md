The audit passes: all eight KPI lines (S1–S5, F1–F3) hold at 7920da077ac2. I found nothing that blocks; my four findings are rows only. Classification: 4 findings, 0 in scope + ordinary work + fails open or loses work; 4 rows, no round.

task: DAEO-zmo4 (W2-174)
status: DONE (audit only, nothing written in any tree)
work_completed: Ran the Step 0 sandbox check and the identity check. Read the ticket (all KPI lines, Interface, Rabbit holes, both owner sections), the lead's L1–L9, the diff f2b1d38af..7920da077ac2, `verify_pass.py`, `facts.py`, the `command.py` change, `build.py` (`kpi_rows`, `ready_check`, `build`, `Tickets.find`), `frontmatter.parse`, the ticket and facts schemas, and the acceptance cases (S1, S2, S3, S4/F1, S5, F2/F3). Probed by hand in five fixture repositories under `$TMPDIR`.
files_changed: none
evidence:
- **Step 0 (sandbox check):** passes.
  - (a) the `python3 open(...)` write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-174` failed with `OSError: [Errno 30] Read-only file system`, exit 1, and no file was created.
  - (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0), and `git update-index --refresh` exited 0.
- **`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1).
- **Identity:** `GOV_TICKET=DAEO-zmo4`; HEAD is `7920da077ac201ac5247cbeea23e8d60df4655a6`.
- **Tree:** `git status --porcelain` is empty at the end.
- **F2:** `git diff --name-only f2b1d38af 7920da077ac2 | grep -E '^(src/gov/brief/|template/governance/kernel/(templates|schemas)/)'` matched nothing (exit 1). The diff names 18 files, all under `src/gov/adopt/`, `tests/unit/adopt/` or `tests/acceptance/W2-174/`.
tests: I re-ran no pytest. The role says to re-run nothing the lead ran, and nothing I found needed a pytest to reproduce. I judged the lead's figures (94/94 for `gov accept`; whole suite 5,897 with the two named reds) by reading the cases, not by running them. Neither red is a W2-174 or W2-152 case. The whole-suite figures remain the lead's own evidence.
discoveries:
- The four rows below.
- The plain-scalar re-quoting is forced by YAML: a block plain scalar cannot hold `": "`. I judge that S2's reading keeps the line's point (see S2).
risks: Low. Every hole I found fails closed: a refusal by name, or `gov brief` still refusing later.
lessons: none
proposed_decisions: none
unresolved: none
recommended_next_action: Land on this check. Hand rows F3 and F4 to W2-27's CTO, who fills EXAMIN's facts and runs the pass. Rows F1 and F2 are optional Wave 3 hardening.

reviewer_session: unknown (no session id in the environment)
probed_commit: 7920da077ac201ac5247cbeea23e8d60df4655a6

### S1: pass (`--verify-list`)
**What I read:**
- `missing()` lists a ticket whose front-matter `status` is `open` or `in_progress` and which has at least one `kpi_rows` label whose verify is None. Tickets are sorted by id; labels come in `kpi_rows` order.
- The command builds `text` as one line per ticket, or `none` when nothing is missing.
- The acceptance cases cover the S1 fixtures: three tickets, an all-verified repository, no tickets, and only a closed ticket. One case checks that the list agrees with `ready_check`.

**What I ran:**
- A ticket mixing plain, double-quoted, single-quoted, mapping and failure lines listed `DAEO-aaa1 S1 S2 S3 F1` (exit 0). The mapping that carries a verify (S4) was left out.
- With a CRLF ticket and a flow-style failure list, both tickets were listed correctly.
- An empty `.tickets/` printed `{"missing": [], "text": "none"}` (exit 0).
- A ticket with `status: closed` or `status: blocked` is not listed. `status` is tk's own field (open, in_progress, closed), so the filter matches the KPI.
- Output form: the CLI prints gov's result dict, with `text` exactly `none`, not a bare `none`. That is the lead's L1 and gov's output convention; I do not count it as a finding.

**F1, `none` for a root with no `.tickets/`:** `--verify-list --root /nonexistent` printed `none` with exit 0. The same happens for any root without a `.tickets/` folder, such as a mistyped `--root`. It should say that there is no tickets folder, rather than report that nothing lacks a verify.
- Ordinary work: yes, because a mistyped or parent `--root` is a plausible slip.
- Consequence: other. Nothing is written, and `gov brief` still refuses each unverified ticket with `KPI_NO_VERIFY`.
- Scope: in (S1). This is a row.
- What would reverse it: the KPI or L1 stating that a missing `.tickets/` reads as no tickets.

**F4, an unreadable ticket is skipped without a word:** a ticket whose front matter is not valid YAML (`title: a: b: c`) is silently left out of the list, which prints `none`. Naming that ticket in an answers file gives `VERIFY_PASS_UNKNOWN_TICKET`, which is misleading because the file exists. It should be named as unreadable, as `gov brief` does with `TICKET_UNREADABLE`.
- Ordinary work: yes, because tickets written before adoption may hold front matter that does not parse.
- Consequence: other. It fails closed: nothing is written, and `gov brief` refuses the ticket by name.
- Scope: in (S1). This is a row.
- What would reverse it: the pass reporting unreadable tickets, or the KPI scoping the list to readable tickets.

### S2: pass (`--verify-apply`, text-only edit, marker)
**What I read:**
- `_edits` finds each answered item through `yaml.compose` and replaces only that node's character range.
  - A double-quoted item gets the clause before its closing quote, with `\` and `"` escaped.
  - A single-quoted item gets it with `'` doubled.
  - A plain item becomes one single-quoted scalar, and its trailing comment stays outside it.
- The marker replaces an existing `verify_pass:` line, or is added just before the closing `---`. CRLF is kept.
- `_reread` re-parses the edited text before any write. It checks:
  - every other top-level value;
  - the marker's value;
  - each row's label and line, and each verify;
  - the unanswered items, and the other `kpis` keys.

  Any change gives `VERIFY_PASS_EDIT_FAILED`.
- The acceptance case `test_s2_byte_diff_…` compares the whole file to the exact expected text. A sibling case checks that only the edited items' lines change.

**What I ran:** one apply with four tricky clauses on a ticket with comments.
- The clauses held `'`, `"`, `#`, `: `, and a backslash with a quote.
- `diff` showed exactly the four items and one added line `verify_pass: 2026-11-13 sess-1`.
- `kpi_rows` read back each clause exactly, and the comments were intact.

On a CRLF ticket that already had a marker and a multi-line plain item:
- The marker was replaced in place; there was still exactly one.
- `\r\n` was kept on every line, as `od -c` showed.
- The two lines of the plain item became one single-quoted line, with its `# c` comment kept.
- The flow list `["flow item", "x"]` took both clauses inside its quotes.

Further runs:
- Without `--session`, argparse refused with exit 2 and wrote nothing.
- A second apply with `DAEO-aaa1: {}` printed `changed: []`, and the file was unchanged.
- Re-applying the same answers gave `VERIFY_PASS_UNKNOWN_LABEL`, and nothing was written.

**On the brief's question:** turning a plain item into one single-quoted scalar keeps S2's point. YAML cannot hold ` Verify: …` in a block plain scalar. Only the answered item's bytes change: its quotes and doubled `'` are added, its value is the line plus the clause, and its comment stays. The S2 line asks for no YAML dump, for comments and key order to survive, and for no other value to change, and all of that holds. The re-read also checks that each value is the same.

### S3: pass (ready after apply)
**What I read:**
- The unit case `test_w2_174_ready.py` calls `ready_check`.
- The acceptance cases `test_s3_…` run `gov brief engineer` on a fixture with its own filled facts file and expect exit 0.

**What I ran:** a fixture with copied kernel templates and the default facts file.
- Before the apply, `gov brief engineer` refused with `KPI_NO_VERIFY S1` plus the placeholder names.
- After the apply, `KPI_NO_VERIFY` was gone, and only the default facts file's placeholders were left.

The brief build itself depends on the filled facts file, which the S3 cases supply.

### S4: pass (checks before any write)
**What I read:**
- `_checked` raises on the first bad entry, and nothing is written before every entry is checked. The order is:
  - an unknown ticket;
  - a closed ticket;
  - a label that is not one of the lines lacking a verify;
  - an unanswered line;
  - an empty clause: not a string, blank, or only TBD, TODO, n/a or none, in any case, with a trailing `.` ignored.
- An answers file that cannot be read gives `VERIFY_PASS_ANSWERS_UNREADABLE`.
- The acceptance cases check one refusal per code and that each wrote nothing. They also check that a clause starting with a placeholder word but carrying words of its own is accepted.

**What I ran:**
- A closed ticket gave `VERIFY_PASS_CLOSED` (exit 1).
- A W2 id gave `VERIFY_PASS_UNKNOWN_TICKET`.
- A label already verified gave `VERIFY_PASS_UNKNOWN_LABEL`.
- `diff -r` against a copy showed only the intended edits.

**F2, a ticket named by its W2 id is refused:** an answers file naming a ticket by its `wbs_id` (`W2-901:`) is refused as an unknown ticket, though `gov brief` accepts W2 ids. It should either resolve the W2 id the way `Tickets.find` does, or name the expected form in the refusal.
- Ordinary work: yes, because this project refers to tickets by W2 id in most places.
- Consequence: other. It fails closed: refused by name, nothing written.
- Scope: in (S4). This is a row.
- What would reverse it: the Interface's `<ticket id>` read as the front-matter `id` only, which is the lead's L1.

### S5: pass (facts file)
**What I read:**
- `write_default` writes only when no file exists, opening it with `"x"`. `ready.new_since` is `'<today>'`, quoted.
- Commands are `gov …` forms, or `{UNSET_<NAME>}` for both `run` and `check`. `wait_for` is `gov wait {EXIT_FILE}`.

**What I ran:**
- `gov adopt --facts` printed `written: true`. A second run printed `written: false`, and so did `--facts --facts`.
- `jsonschema.validate` against `facts.schema.json` passed, and `new_since` was `'2026-11-13'`.
- `gov brief engineer` no longer gave `BRIEF_FACTS_MISSING`. It named `UNSET_IDENTITY`, `UNSET_WHERE`, `UNSET_UNIT_TESTS` and `UNSET_PYTEST_FOLDER`.
- `gov brief lead --run build` named eight placeholders, `UNSET_LEAD_VERIFY` among them.

**F3, more placeholders than the KPI's two examples:** the default file writes ten commands as placeholders, not only `lead_verify`:
- identity, where, pytest_folder, unit_tests, schema_check, lead_verify;
- launch_worker, tests_worktree, merge_tests, tests_worktree_remove.

So a fresh adoption's engineer brief names four placeholders, and the lead brief names eight. The KPI allows this ("a command with no product equivalent") and L7 leaves `launch_worker` to the engineer. W2-27's CTO will have to fill all ten.
- Ordinary work: yes, because every adoption hits it.
- Consequence: other. It fails closed: `gov brief` refuses each placeholder by name.
- Scope: in (S5). This is a row, information for W2-27.
- What would reverse it: a product `gov` form existing for one of these, such as `gov launch` for launch_worker.

### F1: pass (all or nothing; unnamed or closed ticket never edited; no partial mark)
**What I read:**
- Every check, every in-memory rewrite and every re-read finishes before the first write.
- Each write goes to a temporary file in `.tickets/` and is then swapped in with `os.replace`. If an `OSError` occurs, the files already written are restored.
- `VERIFY_PASS_UNANSWERED` prevents marking a ticket with a line still lacking a verify.
- Acceptance cases cover:
  - `test_f1_nine_good_entries_and_one_bad_one…`, parametrised by fault and position, which leaves the tree byte-identical;
  - an unnamed ticket never edited;
  - no ticket marked while a line still lacks a verify.

**What I ran:**
- With a refused mapping item and with a closed ticket, `diff -r` showed the refused tickets unchanged.
- Only the explicitly answered `DAEO-blk1` and `DAEO-crl1` changed.

### F2: pass (`gov brief`, the ready check, the template and the schema untouched)
- The diff check is in evidence: no path matched.
- `test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged` checks `stages.py` and `tests/acceptance/W2-152`.
- That W2-152 passes rests on the lead's whole-suite run, whose two reds are W2-23 S6 and W2-112.

### F3: pass (verify pass scope; no model, no network)
**What I read:**
- `verify_pass.py` imports only `datetime`, `os`, `re`, `pathlib`, `yaml`, `gov.brief.build`, `gov.cli.errors` and `gov.util.frontmatter`.
- `gov.brief.build` imports nothing that reaches a network or a model.
- It reads `.tickets/*.md` and the answers file, and writes only inside `.tickets/`.

**What I ran:**
- After the list and apply runs, `diff -r` with a decoy `repo/decoy.txt` showed no change outside `.tickets/` and no new file.
- `find` showed no write under the empty HOME.
- The acceptance cases also trace file opens and connections.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```