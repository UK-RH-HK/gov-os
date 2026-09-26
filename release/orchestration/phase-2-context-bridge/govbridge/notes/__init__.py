"""Hierarchical evidence notes (REPAIR_PLAN.md section 2.10, OD-BR-05 section 7, OD-BR-06 section 4): the DERIVED
record the bridge computes when complete relevant evidence for a query exceeds one packet. A note groups the
overflow into claims, each grounded in one or more cited sources with full lineage (item_id, path, commit, blob,
lines, content_sha256), and discloses whatever it could not resolve. A note is never authoritative and is never
placed in section A (class DERIVED_NOTE, non-ladder; ARCHITECTURE.md section 5.1's DERIVED row).

Submodules:

* ``schema``  -- loads ``config/notes-schema.yaml`` and does structural (shape/required-field) checks.
* ``build``   -- constructs a note from claims and computes/recomputes ``built_from_sha256``.
* ``validate``-- the full validator (structural + source resolution against Git + placement + hash), and the
  ``govbridge notes validate <file>`` CLI entry point.
* ``cli``     -- ``govbridge notes {validate|build} ...`` subcommand dispatch, mirroring ``govbridge.demo.cli``.

The class name lives once as code, ``govbridge.notes.schema.NOTE_CLASS`` (``"DERIVED_NOTE"``), matching
``config/notes-schema.yaml``'s own ``class`` key -- ``tests/notes/test_schema.py`` asserts the two never drift,
the same technique ``govbridge.authority.classes`` uses against ``ORCHESTRATOR_STATE.yaml``.
"""
from __future__ import annotations
