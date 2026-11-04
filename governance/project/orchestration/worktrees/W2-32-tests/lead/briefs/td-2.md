# W2-32 test designer, round 2 (the CTO)

Same rules as round 1 (stand-ins only, no `gov retrieve`, no real model; the `ps` check in your return). Your marker
was written by the CTO (the Write was refused you in `.gov-runtime/scratch/lead/`). The CTO decided your three
proposals: P-W2-32-1 (the README's interface is now the engineer's spec in the ticket, `37cd5e19`), P-W2-32-2 (F1's
noise band is the spread of D-4b measure 1's **three runs with the merged code**, 0 today; the pinned run's record now
sits in `~/gov-os-runs/D4B/m1/records/pinned/`, so read only the top folder's records), P-W2-32-3 (the evidence file in
the engineer's paths).

**This round, other tickets' cases that W2-32's S2 now makes fail closed** (an engineer's S2 enforces the embedder pin:
a stand-in reporting another digest with no pin for it now fails closed, which is what S2 asks): revise each case to pin
its stand-in's digest in its planted project's `governance/project/models.yaml` (`embedder: {model, revision}`, the
interface in the ticket), keeping what the case guards:
- `tests/unit/rebuild/test_w2_122_seed.py::test_an_endpoint_now_reporting_another_revision_refuses_the_base` (its
  endpoint moves to digest `"b"*64`);
- W2-123's acceptance stand-in, which reports digest `"0"*64` (its rebuild cases);
- any other case you find, by a scan of `tests/` for stand-in digests other than the pin `ac6da0dfba84...`.
Show each revised case green on the engineer's head (merge `w2/W2-32` into your branch first, `--no-ff`; you may merge,
you do not read the engineer's code beyond running the tests) and still red on the change it guards (a planted change in
a scratch copy, never committed).

**The CTO's ruling on S3 (P2):** a memory-quality event for a miss on the hidden half is recorded by its id only: no
question text, gold answer, sources or regression case in the repository. If any S3 case of yours records a hidden-shaped
miss in full, revise it to the ruling, and add one case: a hidden miss (`H` + digits, or `part: hidden`) is refused unless
it carries the id only.

Commit with `Task: DAEO-0pyc`, `Implements: DEC-1055, DEC-1064`, `Role: independent-test-designer`, a `Rewrite-Reason:`
naming W2-32's S2 (or the ruling), Co-Authored-By. Return the twelve fields.
