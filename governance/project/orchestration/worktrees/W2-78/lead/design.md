# W2-78 (DAEO-v4is) design note — behaviour, not code

## 1. The record files
- Four files under `governance/project/records/`: `load-sensitive.yaml`, `accepted-reds.yaml`, `accepted-history.yaml`,
  `acceptance-exemptions.yaml`. Each is a YAML mapping with `version: 1` and one key, the path map's own key name
  (`load_sensitive`, `accepted_reds`, `accepted_history`, `acceptance_exemptions`), holding the path map's list as it
  stands at the branch's base on `w2/integrate`: entry for entry, in order, every field (`test, decision, reason,
  fixed_by`; `commit, decision, should_implement`), the values unchanged (an empty list stays an empty list).
- Each has a schema of its own, a new file under `template/governance/kernel/schemas/` (four new files; no existing
  schema edited, `path-map.schema.json` included).

## 2. The readers: one source at any commit
- **Source:** each list is read from its record file only: the ratchet's `accepted_reds` and `load_sensitive`
  (ratchet), `accepted_history` (history, hence the close's trailer gate, the product-traceability check and
  gates' owner-listed commits), `acceptance_exemptions` (gates' owner-listed commits). The path map is still read
  for its configuration (`decision_register`, `trailers_base`, the floors); never for a moved list's entries, and
  never the union of the two.
- **A record file that is missing, unreadable, not a mapping, or not valid against its schema** is named by the
  close (a finding naming the file and why; for the ratchet's lists the close refuses before any test, as a refused
  entry does today; for accepted history the trailer gate's refusal; the product-traceability check reports it as a
  finding). It is never read as empty and never replaced by the path map's list. Deleted is missing: a record file
  that `HEAD`'s history held and the tree no longer holds is named. A project whose path map never had the list
  and whose history never held the file has no such list (as a missing key today).
- **The path map's old key** (refused rather than silently ignored): while the path map still holds one of the four
  keys, it must be the exact copy of its record file (same entries, same order, same fields). Any difference, or
  the key held while the record file is absent, is named by the close and refuses, and the path map's entries are
  never counted. This guard compares; it never reads the path map's list as a source. The exact copy is tolerated
  only so that the pinned judge (which reads the path map) and the new readers judge the same lists until the ACT
  removes the keys. Once removed, a key added back with any entry the record lacks is refused by name.
- **The ratchet's rule unchanged on the new files (DEC-757, DEC-766, DEC-862):** an entry counts only with an
  ACCEPTED owner decision naming the test and only if every commit that added it carries `Role: owner`. The commits
  that add an entry are read on the history of the record file **and** the path map, one source per commit: at a
  commit that holds the record file, its entries; at an older commit that does not, the path map's list at that
  commit. So the move adds no entry (its parent already held each in the path map) and the original owner commits
  stay the adders; an entry changed or added in the move, or later added to a record file by a commit without
  `Role: owner`, is refused by name. A removal is a shrink: nothing refuses it.
- `ratchet._refused_because` and `history._refused_because` keep their signatures (the orchestrator's
  `validate_entry.py` calls them from the pin, DEC-895).
- `select.py`: no change expected; the selection is driven by the test map's lists (below).

## 3. The test map (only `record_only` and `record_reading` change)
- `record_only` gains the four record files by exact path, and `governance/project/prompts/**.md` and
  `governance/project/briefs/**.md` (the list's own idiom, so that no code file there is hidden; every file
  tracked there today is `.md`). `shared_core` keeps `governance/project/path-map.yaml`: an edit of the path map's
  configuration still runs in full.
- `record_reading` gains every test that reads, on the live tree, a moved list (directly, or through the readers:
  `gov close`, the trailer gate, the product-traceability check and every test that runs `gov check` or the declared
  checks on the live tree) or a prompt or a brief (W2-62's session-start case among them); W2-78's own suite; and
  the ratchet's own suites (W2-53's acceptance suite; `tests/unit` always runs), so that a removal from
  `load_sensitive` runs them.

## 4. The migration's order (the package)
- **ACT-1, before the merge (owner):** the path map's `project-overlay` namespace gains
  `governance/project/records/**` (today nothing maps the folder: `gov check pathmap` and W1-08 are red on the
  branch until it lands). Harmless to the pinned judge.
- **The record files ride this branch** (an engineer commit), accepted by decision as the owner's entries moved
  unchanged; proven by W2-78's entry-for-entry case and by the ratchet's own provenance rule above.
- **Merge W2-78, re-pin, then ACT-2 (owner):** the path map's four lists removed (patch prepared in
  `.gov-runtime/scratch/lead/act/`, never committed by this ticket). Until ACT-2 the exact-copy guard keeps the
  two judges equal.
- **Before ACT-2 lands (outside this ticket's paths):** `command.py:234` decides from the path map whether the runs
  tell each test's result for the ratchet (it would stop after ACT-2: a package for W2-68/W2-57's paths); the
  earlier acceptance tests that read or plant the lists in the path map are revised (a package); the orchestrator's
  tools (`validate_entry.py`, `trailer_gate.py`, the queue's gate (e)) and `nightly_alone.py` read the record files.
- A later entry in the path map's old list: refused by the exact-copy guard (§2). No `path-map.schema.json` edit is
  needed; forbidding the keys there is an optional later hardening after W2-58's close.
