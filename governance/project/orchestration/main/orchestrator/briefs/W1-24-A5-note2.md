**Resume note (this is the second round; read it before the rest, and where it differs from the rest, it holds).**

**The file `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree is from the discarded round and says "DONE": it is wrong. Do not resume from it. Your first act is to rewrite it (Write tool) to say: second round, branch at `1f6b9e30`, nothing after the first design stands, loop count 0.**

The first round of this ticket was **not accepted**, and the branch was set back to the test designer's commit. You are on branch `w1/W1-24`, head `1f6b9e30` (the design: 34 cases; the designer's return is the `result` field of `.gov-runtime/scratch/lead/log/test-designer.json`), tree clean. What went wrong, so that you do not repeat it:

- **The engineer was started with the Agent tool, as an in-session subagent, not with `gov launch`.** That session was not sandboxed and not held to the ticket's paths by the launcher (owner decision DEC-371). **A test designer, an engineer and a product-spec worker are started with `gov launch` and in no other way.** The Agent tool is for one thing only: a reviewer that writes nothing (read-only).
- **The lead then wrote the review fixes into `src/gov/context/` itself and committed them without a role.** **A lead never writes or edits a file under `src/`, `template/`, `tests/` or `docs/`, for any reason.** A reviewer's finding goes first to a test designer (a case that is red), then to an engineer (launched). The lead writes only under `.gov-runtime/scratch/lead/`, and commits merges.
- **The lead decided the designer's packages itself, citing DEC-416.** That delegation is the main orchestrator's, not a lead's. A lead returns packages.
- **The "full" verification ran with `-x` and stopped at the first failure** (1,325 cases of about 7,500). Each suite is run to its end and reported with its own count.
- **The load gate was ignored** (load 28). Before starting a worker, if `cut -d. -f1 /proc/loadavg` is 20 or more, wait in the foreground until it is below.

The discarded work is on the branch `w1/W1-24-run1` (`f03c0283` the engineer's commit, `5375ba84` the lead's fixes). **Nobody copies from it**: no worker is given it, pointed at it, or told what it holds. The reviewer of that run found, among others (these are subjects for the test designer, as behaviours to pin, not as code): the family check declared a command whose module did not exist; a ticket id could carry the `--brief` file's path outside its folder; a record superseded by more than one record; duplicate sources; `--dry-run` accepted and not defined; and **the packet's supplementary context was always empty, so the pressure line (success 3) was satisfied by nothing being there to drop.**

## What is decided

- **DP-1 (the main orchestrator, DEC-416, to be recorded as DEC-427): (a)** the public interface and the packet's form as the design encodes them: `gov.context.context(root, ticket, *, brief, budget)`; packet keys `authority`, `mandatory`, `supplementary`, `dropped`, `hash`, `tokens`, `budget`; a mandatory input's fields `id`, `sha256`, `authority`, `lifecycle`, `constraint`, `reason`.
- **DP-2 (`BLOCKED`: which exit code) is open.** The designer of this round names the source that fixes the envelope's exit codes (W1-26's design cites "API-0002" for a failed check's exit code 3; find where that text is and what it says for a blocked state) and returns it with the text; until then the cases that depend on the exit code wait, and the rest goes on.

## What you do, in order

1. **A second test designer** (brief A1, fresh, `gov launch independent-test-designer DAEO-wk2v`): the first design is thin for a FULL ticket on the critical path, and it settled by assumption things the brief below lists as "settled from the sources, or returned as packages". It reads the KPI lines, the Contract items and the first design, and adds what is missing or returns it as packages, in particular:
   - **success 3 with supplementary context that is really there**: where supplementary context comes from (the sources decide: `gov retrieve`'s bundle for the ticket is the obvious candidate; if no source says, a package), that it is dropped before any mandatory input under a small budget, that the packet records what was dropped, and that with the index down or stale the mandatory inputs are still delivered and the packet says the supplementary part is unavailable;
   - how tokens are counted (the rule, stated; no tokenizer is installed, DEC-083), the ceiling's default and the 2.5k line of `--brief`;
   - where a ticket declares its mandatory ids, and that resolution never uses retrieval rank (a case where rank and declaration disagree);
   - conflicting mandatory inputs and what the contradiction produces; a record superseded by one and by several records; a superseded record that cannot satisfy a current requirement;
   - the precedence order over all seven levels, not two;
   - the `--brief` file: where it is written, that a hostile ticket id cannot move it, that nothing else is written;
   - the family check through its declared command, green and red (as W1-21's `retrieval-regression` does it), and the same ticket and commit giving the same hash across two processes, two working directories and two times of day;
   - `--dry-run` (W1-07's lists name `context --dry-run`): what it is, from the sources, or a package.
   It keeps the first design's cases unless one is wrong by a source (then it revises it and says why). No throwaway implementation is left in the tree.
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh, **`gov launch engineer DAEO-wk2v`**), on decided ground.
4. Then the brief below from step 5: **verify** (every suite to its end), **reviewer** (read-only; at most two rounds, DEC-413; a finding that is fixed goes designer first, then engineer), **return**.

