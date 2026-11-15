---
type: probe
task: DAEO-g87r
reviewer_session: "8fa34821-7ea9-496c-9809-6e9f9b616aaa"
implementer_session: "c364ad9b-ffb5-417a-ad2a-8a9ed6340052, 9d799613-572a-4461-8e33-0d647201d4b7"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
scope: "the walls launcher's --reanchor flow (DEC-1186 (4)): S14, S15, the failure line S14/S15's failure, S12; review round 1 (independent-auditor, Opus, high, read-only)"
probed_commit: 61570944d71ab803e545068bcf27e8d898a048fc
decisions_applied: [DEC-1186, DEC-1180, DEC-820]
---

# W2-94 (DAEO-g87r) `--reanchor`: independent review, round 1

**Head probed:** `61570944d71ab803e545068bcf27e8d898a048fc` (`w2/W2-94`), base `883e1ba6b152`.

**task:** DAEO-g87r. **decisions:** DEC-1186 (4), DEC-1179 (6), DEC-1180 (2), DEC-820 (d), DEC-801, DEC-802, DEC-808, DEC-1010, DEC-1156 (7), DEC-959 (7).

## What I probed, and how
- I read the whole change in `indep_launch.py`: `check_args`, `load_kinds`, `plan_reanchor`, `ReanchorInfo`, `same_value`, `reanchor_same`, `deliver_reanchor`, `check_result` and `build_and_run`, together with `Landing`, `pack`, `finish` and `main`.
- I also read the schema's `reanchor` object, the W2-149 unit file's diff, `maintain.reanchor_item` and `measure._load`.
- I ran five probes on planted ReanchorWorlds (the acceptance support's World, a stub `claude`, everything under my `$TMPDIR`):
  - **P1:** a rename failing at the 2nd call into `hidden/`, and the rollback's own write failing too.
  - **P2:** a crash, with a staged hidden file made unreadable.
  - **P3:** a named alternative delivered without `path`.
  - **P4:** a result whose `corrected` and `replaced` disagree with the delivered files.
  - **P5:** a leak scan across five outcomes: an id repeated after case folding (10), two case-colliding hidden files (10), an undeclared kind (11), an id longer than 32 characters (10), and a dry run.
- I opened nothing real.

## Found sound
- **Hidden content (F1, DEC-820 (d)):**
  - Every launch-log line and every refusal word is a fixed word; a crash logs only the exception's type name.
  - The counts carry only `week` and numbers. The `present` stems, `.named` and `.sha256` never reach the counts or the log (`ReanchorInfo` is used only at lines 2424, 2676 and 2865).
  - `input/reanchor.json` holds only the staged ids, in the set's own spelling; an absent id never enters the wall.
  - WALL.json, SEEDS.log and the tree carry no id.
  - P2 and P5 found 0 planted strings in stdout, stderr, the planted HOME (runs and trees) or the repository, on every path probed. P2 exited 10, "refused 10 brief", with no leak.
- **The commit check (S14):**
  - The 14 comes after the form checks and before anything is built.
  - It compares the request's `audit_commit` with the resolved 40-hex commit.
  - `--reanchor` is refused 17 with `--fix`/`--reason`, `--counts-only`, any kind other than writer, or round 1. A brief with a `brief:` entry is refused 10.
- **The 11 check:**
  - The 11 check (line 2624) runs before any wall or tree is built.
  - The repository's `kinds.yaml`, `indep-walls/**` and `indep-briefs/**` are unchanged, which matches reading (5).
- **The case rule:**
  - Ids are grouped case-insensitively and staged in the set's own spelling.
  - Two case-colliding hidden files for a requested id refuse 10 (P5), which matches reading (1).
- **Delivered against staged (S15):**
  - The staged side is the hidden file's bytes, re-hashed against the sha recorded at planning, never the wall's `input/` (reading 4).
  - Every key outside `sources`, and every unnamed entry, must be equal by value and by type. In a named entry, each alternative may change only `path`, `lines`, `heading` and `commit` (reading 2).
  - A top-level `replace_reason` is ignored on both sides; a delivered one must be a non-empty string (reading 3).
  - Every change the drafted brief asks for is accepted: new lines, a new heading, an added `commit`, a moved `path`, an alternative left as it was, a `replace_reason` mark.
  - The launcher and `measure` read the file with the same loader (`yaml.safe_load`), so the parsed comparison holds.
- **Partial delivery:**
  - Every check runs before the first rename. `Landing` undoes the renames already made on a failure at any rename, and the acceptance cases cover the first, second and last.
  - An id not requested is never opened for writing.
  - The old files go into the tar as `replaced-hidden/<stem>.yaml`.
- **S12:**
  - The fix flow's delivery is unchanged.
  - `--help` hides the `--reanchor` line.
  - The new `load_kinds` check fires only when `input_reanchor` is present.
- **Acceptance tests:** only the test designer's commits touch `tests/acceptance/**`, and the tree at head equals `0292cc50f` there.

## Findings

**R1 — a rollback that itself fails is a partial delivery reported as nothing replaced** (failure line F1, "a partial delivery"; the bundle's F6, carried)
- **Where:** `indep_launch.py:2178-2190` (`Landing.commit`'s rollback ignores an `OSError`) and `:2120-2126` (`deliver_reanchor` then removes `.replaced`).
- **P1:** the 2nd rename into `hidden/` fails, then the rollback's write of the old bytes fails.
  - Result: exit 20 "rejected" with `delivered.files` 0, yet `hidden/Q01.yaml` holds the delivered bytes.
  - `.replaced` is removed, so the old bytes are not under `replaced-hidden/`. They survive in the tar as `<run>/input/Q01.yaml`, for all three ids.
- **Same class:** a signal arriving between a successful `os.replace` and `done.append` (2173-2177), or during the rollback loop (`except OSError` does not catch `Interrupted`).
- What should happen: a failed rollback keeps `.replaced` and records its own refusal word.
- **What would reverse it:** a rollback that cannot fail silently, or a case showing that P1's double fault leaves the hidden half byte-identical.
- Ordinary work: no, because it needs two filesystem faults in a row inside one landing, or a signal within a few bytecodes; no agent action produces that.
- Consequence: fails open (no bytes lost: the old copies stay in the tar's `input/`).
- Scope: in. A Wave 3 row (DEC-801), never a round.

**R2 — a named alternative may lose its `path`, and the delivered question no longer loads** (S15)
- **Where:** `REANCHOR_FREE` (`:123`) and `alternative_ok` (`:2045-2048`) let each free key be "added, changed or removed".
- **P3:** a delivery dropping `path` from a named alternative is accepted (exit 0).
- **Effect:** `measure._load` then refuses the question with "a source names no path" (`measure.py:257-259`).
- What should happen: `path` may change, but stays a non-empty string.
- **What would reverse it:** a governing reading that a named source may legitimately lose its `path`.
- Ordinary work: yes, because the writer has no shell and retypes the whole file, so a dropped line is a plausible slip.
- Consequence: other (a loud fault on the next measure, the old file in the tar, `check_gold` catches it).
- Scope: in. A row.

**R3 — `corrected` and `replaced` are not checked against the delivered files** (S15, the counts)
- **Where:** `check_result` (`:2423-2429`) checks only that the two numbers sum to the staged count.
- **P4:** one question delivered with a `replace_reason`, and a result saying `corrected` 3, `replaced` 0, is delivered with those numbers in the counts.
- **What would reverse it:** a rule that the counts are the writer's own claim only.
- Ordinary work: yes, because a writer's tally slip is ordinary.
- Consequence: other (a wrong number in the counts; the files themselves are right).
- Scope: in. A row.

**R4 — W2-149's unit file changed in two pins beyond the S13 path case** (S12)
- **Where:** `tests/unit/orchestration/test_w2_149_indep_launch.py:380-382`: the documented lines go from 10 to 11. And `:1098`: the `optional` map gains `reanchor`.
- **The gap:** the ticket's `allowed_paths` comment and P-W2-94-S13-1 cover only the `fix` entry. S12 says the suites "pass unchanged".
- Both edits follow from the Interface at claim: the documented usage line and the optional `reanchor` key.
- **What would reverse it:** a recorded path case for these two edits.
- Ordinary work: yes, because an interface change that adds a usage line and an optional key meets these pins in ordinary work.
- Consequence: other.
- Scope: in. A row: the lead records a path case.

**R5 — the 11 check accepts `input_reanchor: [reanchor]` without `questions`** (S14)
- **Where:** `:2624`. The docstring says the writer kind must declare `[questions, reanchor]`.
- **What would reverse it:** the ticket's wording ("does not declare `input_reanchor`") read as the bar.
- Ordinary work: no, because the line is written from the docstring and approved by the owner.
- Consequence: other.
- Scope: in. A row.

**R6 — `maintain` names questions by YAML `id`, the launcher by file name, and the drafted brief's stop rule compares them exactly** (S14; out of this change)
- **The mismatch:** `maintain.py:188` uses `q["id"]`, from both halves. The launcher matches `hidden/` file names case-insensitively. The drafted brief stops `input-malformed` when an input's `id` "is not its name".
- **Case 1:** a set holding `Q01.yaml` with `id: q01` stages `input/Q01.yaml`, and a writer that follows the brief to the letter stops. That week delivers nothing.
- **Case 2:** an id that differs from its file name beyond case is counted absent every week.
- **What would reverse it:** the real sets' files named exactly as their ids.
- Ordinary work: yes, because it depends only on how a set names its files.
- Consequence: other (a stop or an absent count, both loud; nothing replaced).
- Scope: out. A row for the brief's ACT: compare case-insensitively.

**R7 — the usage line's `--brief-sha256` is the hash of empty bytes** (S11/S14 documentation)
- **Where:** the docstring's usage line has `e3b0c442…`. A copied line is refused 10 (bytes).
- Ordinary work: yes, because an operator may copy the documented line.
- Consequence: other (it fails closed).
- Scope: out. A row.

Classification: 0 blocking. R1 is ordinary work no (a Wave 3 row). R2 to R7 have consequence other.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": [{"id": "R7", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S12", "verdict": "pass", "findings": [{"id": "R4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "S14", "verdict": "pass", "findings": [{"id": "R5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S15", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}, {"kpi": "F6", "verdict": "pass", "findings": []}, {"kpi": "F7", "verdict": "pass", "findings": []}]}
```

Overall: **pass**.
