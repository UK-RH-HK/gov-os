---
name: shipped-folder-exactness-tests
description: "src/gov/_shipped/ must hold exactly fabric.PACKAGED (a W2-88 unit test and W2-88 acceptance S24 enforce it); adding a file there needs fabric.py, test_w2_88_shipped.py and the W2-88 acceptance ITEMS"
metadata:
  node_type: memory
  type: project
  originSessionId: 3fc4cbea-07c7-4c03-afe8-bd04a3068f2a
  modified: 2026-11-15T23:12:17.975Z
---

Since W2-88's S24/S29 (landed a13a3a31f, 2026-11-15), anything added under `src/gov/_shipped/` turns two tests red unless it is also named in three places: `fabric.PACKAGED` (src/gov/adopt/fabric.py:72), `THE_SHIPPED` (tests/unit/adopt/test_w2_88_shipped.py, `test_the_package_ships_nothing_but_the_shipped_set`), and `ITEMS` (tests/acceptance/W2-88/test_w2_88_p1_shipped_bytes.py, `test_s24_the_shipped_folder_holds_only_the_copies`; a test designer's file).

**Why:** W2-174 r2b (11-15 23:2x): the CTO widened the ticket only to `_shipped/.../schemas/**` and pyproject.toml; en-3 shipped the two schemas and both tests went red. The brief (mine) had grepped S29 only. That made a PACKAGES round trip.

**How to apply:** before briefing or widening for a new shipped file, grep tests/ for `_shipped` and `rglob` and name all three places in the widening. Related: [[cto-fixes-path-cases]].
