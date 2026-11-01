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
