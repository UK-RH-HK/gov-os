Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: engineer, DAEO-emq1 (W2-115), FULL, class C3 — the smart close's last three reds (build run 2, eng-3, iteration 3)

Budget: projection 4 USD. Keep your context short: read only what each red needs; cut long outputs to head and tail.

You are a fresh engineer for ticket DAEO-emq1 (W2-115), in `/home/usain/gov-os-worktrees/W2-115` on `w2/W2-115`
(DEC-963), head 20b33403fea4. Step 0 (the sandbox check), every standing rule, the writes, the never-read rule for
`tests/acceptance/W2-115/**`, the Interface, the commands, the commit form and the return are those of the first
engineer's brief, copied beside this one: `/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/eng-1.md`
(read it whole), and the lead's answers in `eng-2.md` beside it (binding: the batch via `gov.close.batch run`, a
load-sensitive case = a serial-only entry of kind `latency`, W1-39 and W2-77 not yours). Do step 0 first and report it
first. **Every pytest run adds `PYTHONUSERBASE=/home/usain/.local`** to the brief's `env`. `gov accept` crashes in the
sandbox: do not run it; the lead runs it outside.

`gov accept` outside the sandbox at 20b33403fea4 gives 74 passed, 3 failed. The failing output, message and traceback
tail only (do not open the test files): `/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-2.txt`.

1. **S6, a candidate that cannot be isolated:** `gov.close.batch run A B C --root <project> --json` exits 3 with
   `{"ok": false, "command": "batch", "result": {}, ...}` and the refusal's text does not name `CANDIDATE_NOT_ISOLATED`.
   Every refusal of the scoped batch must carry its code in the JSON envelope's error (and on stderr), the way the
   close's refusals do.
2. **S4, three rounds for a load-sensitive red:** a red whose node id a `# serial: latency: ...` entry of the planted
   project's `tests/acceptance/serial-only.txt` names got only 2 runs on the head (its run and one alone); it needs its
   run plus 3 rounds alone on the head (and 3 on the head without the change). Check how the entry is matched to the
   red (an entry may name the file, the node id or a parametrised id; match as the serial plugin's `declares` and
   `_ratchet.covers` do) and that the rounds count is applied on both sides.
3. **S2, a governance file alone selects nothing:** a change to a governance-overlay file alone selected the
   `record_reading` suite. eng-2's batch 1 made the change "everything since the newest green record plus the ticket's
   own commits"; the governance-alone rule must hold on that wider change too: governance files select nothing by
   themselves, record places alone select `record_reading` alone, and a change holding both governance files and
   record places (no code) selects `record_reading` alone only if a record place is in it. Check that the classifier
   does not count the planted ticket's own record commits (`.tickets/`, the close record) as part of a governance-only
   change when they are only the ticket's bookkeeping; choose the narrowest fail-closed reading and name it.

Done: your unit tests (add one per red) and the brief's strict suites (F4) pass; commit each fix with eng-1.md's form;
return as eng-1.md says, `status` DONE when the three are fixed in your runs.
