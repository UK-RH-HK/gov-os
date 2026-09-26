# run-1: consumption and secrecy audit, recorded by the orchestrator (OD-BR-03 items 4 and 5)

Source: the transcript of the demonstration agent `br-demo-0011`, `agent-a8a5be03e0483583d.jsonl`. **All 210 turns were on `claude-opus-5-5`.**

## Supplied artefacts, in bytes
* `packet/packet.md`: 274,798 bytes. `packet/manifest.json`: 419,496 bytes.
* `bootstrap.md`: 282,782 bytes. After its first 60 lines of operating context, the bootstrap is byte-identical to `packet.md`. The agent verified that itself with a diff.
* `task-inputs/`: 9,868 bytes (the public queries and the answers and receipt schemas, OBS-BR-07).
* Saved query outputs, written by the agent: 104 files, 1,063,203 bytes.
* Main packet plus saved query outputs: 1,338,001 bytes. This is the G7 packet-bytes figure under OBS-BR-06.

## What the agent actually consumed, by model-side token usage
* Turns: 210. Tool calls: {'Bash': 107, 'Read': 6, 'Write': 2, 'SubagentHandback': 1}.
* **Peak context: 503,981 tokens.** Cumulative input tokens across turns: 60,377,956; cached reads dominate this sum. Output tokens: 159,564.
* How it read `packet.md`: six Read calls, with line windows 1–400, 401–800, 801–1200, 1200–1579, 1579–2028 and 3226–3925. It also parsed `packet/manifest.json` with scripts, for example a compact dump of every G item. Lines 2029–3225 were **not** read through the Read tool.
* Transcript read extraction (`reads.json`): 92 read events; 43 distinct files; 0 whole-tree sweep commands.

## Secrecy audit (OD-BR-03 item 5; OBS-BR-04)
* Tool calls touching `.local/share`, `govbridge-sealed-*`, `.authoring`, `DEMONSTRATION/oracle*` or `oracle-tools`: **0 accesses.** One command merely contains the string `govbridge-sealed`: the agent grepping its **own saved query outputs** for that string, as a self-audit.
* Tool calls reading `ARCHITECTURE/**`, `AGENT_RUNS/**`, `HANDOFFS/BR-HO-0*` or another `DEMONSTRATION/` run: **0 reads.** The matches were `--exclude` arguments and self-audits of saved outputs.
* Excluded-path **exposure through the retrieval route**, which the agent self-disclosed: its first `search`, run before it added `--exclude`, returned one snippet of `ARCHITECTURE/demonstration-queries.yaml`. That snippet is public query text. A `history` output listed path metadata only for excluded directories. **Root cause: the query commands do not apply the task spec's `retrieval_exclusions` automatically (OBS-BR-08). It also bears on OD-BR-03 item 1.**
* The sealed-directory name appears in none of the agent's saved outputs, `answers.yaml` or `receipt.yaml`.
* **Oracle-overlap check.** Every oracle line of at least 50 characters was compared verbatim against every run-1 input and output. There were 73 overlaps, **all of them `path:` locator lines**, meaning repository file paths that any correct answer shares with the oracle. **Zero overlaps carry oracle substance.** The categorisation is in `oracle-overlap-audit.orchestrator.out`, which lists no oracle values.
* **Legitimate carriers of Review-8 conclusions.** Section A includes the Review-8 return and the Review-8 context pack as mandatory inputs, by owner design (OD-P2-10A/B, `mandatory_bridge_inputs`). The grade must therefore rest on anchors that were **verified at `3c880d8`**, not on restating those inputs (OD-BR-03 item 5).

## Rule deviation, minor
* The agent wrote temporary helper files (`gq.sh`, `gen_receipt.py`, `G_compact.txt` and a bootstrap tail) into the shared session scratchpad, outside RUN. They are not in the repository, not committed, and have no effect on the store.
