"""Apply the owner's approved walled-route wording (DEC-1163 (10), 'Walled wording approved', 2026-11-13) to W2-94 (DAEO-g87r) S1-S3 and W2-93 (DAEO-6y0x) S5. Run from the repository root."""
from pathlib import Path

EDITS = {
    ".tickets/DAEO-g87r.md": [
        ("after writing, a recorded seeded draw, stratified by category, sends half to the visible folder and half to the hidden folder Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the visible and hidden folders each hold half (within one) with each category in both halves",
         "after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner''s release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release"),
        ("Written from a clone of the owner's copy made by exact path under ~/gov-os-runs/W2-94/examin/; the copy is only read by that clone; nothing written in the workbench or in EXAMIN's real repository Verify: the record names the clone's path under `~/gov-os-runs/W2-94/examin/`;",
         "Written by the walled writer from the wall''s tree, `git archive` of the CTO''s launch clone of the owner''s copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls'' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository Verify: the record names the clone''s path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy''s commit;"),
        ("Written by a session independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the guard's log",
         "Written by the walled writer session (the approved brief `governance/project/indep-briefs/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls'' launch log names the approved brief''s sha256; the guard''s log"),
    ],
    ".tickets/DAEO-6y0x.md": [
        ("The hidden half proves its own data valid with an automatic check (`validate_hidden.py`, beside the data, run before every commit of the hidden half and recorded):",
         "The hidden half proves its own data valid with an automatic check, `validate_hidden.py`, written by the ticket''s independent test designer (never the walled writer), run by the CTO on the delivered hidden half before it is used, printing counts and ids only, and recorded:"),
    ],
}

for path, pairs in EDITS.items():
    p = Path(path)
    text = p.read_text()
    for old, new in pairs:
        # the ticket files are YAML single-quoted: an apostrophe is written twice there
        old_y = old.replace("'", "''")
        hit = old_y if old_y in text else old if old in text else None
        if hit is None:
            raise SystemExit(f"{path}: line not found: {old[:80]}")
        text = text.replace(hit, new, 1)
    p.write_text(text)
    print(f"{path}: {len(pairs)} line(s) changed")
