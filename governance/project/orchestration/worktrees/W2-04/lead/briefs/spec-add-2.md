## The specification's addendum (W2-04, round 2; DEC-1005, delegated by the CTO, deciding P-W2-04-2 (A) and P-W2-04-3 (b)): the same text for the test designer and the engineer

Where this addendum differs from the run-1 text above, this addendum holds.

**S1, amended (P-W2-04-3 (b); CAP-15.b).** A dependency ticket (a ticket the ticket names in its `deps`) is counted by its front matter only: its id, its status, its title and its KPI lines, never its whole file. Its token cost is that part's. Its `sha256` stays its file's (S3, a file of its own). The ticket's **own** text is still carried whole under `ticket_text` and counted whole (S1 unchanged for it). A dependency ticket whose body is very large therefore does not push a packet over its ceiling; a change to a dependency's body alone leaves the packet's `tokens` unchanged.

**S4 and S7, the supplementary block stays semantic-free (P-W2-04-2 (A)).** The supplementary block is built from deterministic lexical evidence only; it never depends on whether a semantic index answers. A question that needs the semantic route (an embedder, its query cache, its query vectors) is asked through `gov retrieve`, not through `gov context`: `gov context` sends nothing to an embedder.

**S7a, what one batch is, and where it is shown (P-W2-04-2 (A), the reading of "one batch").** One batch is one of the context's own lookups of ranked supplementary evidence. The packet shows them under a new key, `supplementary_batches`: a list, one entry per batch the context took, in the order taken; each entry is an object with
- `items`: the list, in rank order, of `{"id", "path"}` of the ranked items that batch read;
- `limit`: the largest number of items that batch could read (`len(items) <= limit`).

The batches' items taken together, in order, are the rank order: the `supplementary` block is, item for item, the first items of that sequence (nothing in `supplementary` is absent from it), and `further_batch` begins with the first ranked item that was not stacked. When room is left after one batch and evidence remains, a further entry appears; when the evidence ends, the last entry holds fewer items than its `limit` (or none). `further_batch` is at most as long as the largest `limit`. A project whose supplementary lookup found nothing, or failed, has `supplementary_batches` as an empty list or the entries it did take, and names a failure in `dropped` by its kind (S7). `supplementary_batches` is part of the packet, so of its `hash`; it is deterministic like everything else in the packet (S4).

**The packet's keys.** A packet built with `ok: true` carries the keys it carried before this ticket, plus exactly these four: `ticket_text`, `supplementary_query`, `further_batch`, `supplementary_batches` (and `synthesis` only when the project holds synthesis notes, S10).
