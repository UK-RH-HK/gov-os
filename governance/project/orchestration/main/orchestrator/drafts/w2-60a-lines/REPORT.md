# W2-60a (DAEO-cv58): RUBRIC-2's lines applied (DEC-1126 (3), DEC-105 apply now)

By the product-spec helper, 2026-11-11. One file edited: .tickets/DAEO-cv58.md (+12, -5). Not committed.

## Per line, old to new (file line numbers before the edit)
- Success 3 (cv58:33): "role's default model and effort, one default line [DEC-839 1,2,5]" -> RUBRIC-2 S3' (Launch default + Launch by criticality; criticality from criticality.yaml, never `class`; record tier, criticality, model_source; floor high, max needs --reason; Verify). Kept "(folds W2-21 S4)", CAP-35.c lite, lens F R1.
- Success 4 (cv58:34): "a model not the role's is refused" -> S4' (not the resolved tier's, unless --trial <id>; subagent model = tier model, a spawn naming its own wins; Verify). Kept lens E F14, "(folds W2-21 S4)".
- Success 8 (cv58:38, launch record): fields gain tier, criticality, model_source, trial id, promotion reason (null when not given). Cites DEC-1120 (3) added.
- DEC-1014 line (cv58:40, the 10th success item): -> S9' (second review the probe, Opus max; first Opus high; same setting twice refused unless owner named; max elsewhere needs --reason; Verify). Kept SMART-WORK-5 A, DEC-1015 item 3.
- New success 11 (S4''): promotion after two failed reviews or a fail-open finding, Opus at the table's effort, recorded with reason and record path.
- New failure line: "A model below its tier with no trial; a promotion not applied; an effort below the floor."
- allowed_paths: + src/gov/launch/criticality.py (the reader, beside role.py), + governance/project/criticality.yaml.
- sources: + DEC-1119, DEC-1120, DEC-1126 (DEC-1014 was already there).
- Body (cv58:72): "W2-11's widening" -> "W2-33's widening".
Each changed or new KPI/failure line ends `[changed, DEC-1120 (5), DEC-1126 (3)]`. Nothing else touched.

## Review-round question
DEC-1010 (1): "at most two review rounds, then the owner once with options, no more routine exceptions". DEC-1105 and DEC-1106 are the precedents: the owner gave one exception round each (W2-20, W2-148), by decision. DEC-1126 (3) says only "RUBRIC-2's lines go into W2-60a now"; DEC-1120 and DEC-1119 say nothing of rounds. So the register does NOT say the count restarts. The restart is the options package's reading (w2-60a-options.md §4, marked E) of new lines as a new scope. W2-60a had three rounds already. Recommendation: the CTO records the restart in its decision text or asks the owner in one line; until then treat the first review of the new lines as round 1 and expect no round 3 without the owner.
