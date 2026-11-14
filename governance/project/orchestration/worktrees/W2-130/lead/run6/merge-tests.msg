W2-130 (DAEO-q8cl): merge w2/W2-130-tests: pin run 2 (ed0e54dfe): S4's three HEAD cases at counts-after.measured_at; every pinned case runs the pinned tree's own gov links

The CTO's answers (DEC-1164 (18), DEC-1156 (7)): F1 measured_at confirmed; P-W2-130-PIN-S4 (a); F4 pin the tool.
Cases now run by the pinned tree's own src: the three S4 HEAD cases and S8's counts and left cases (at measured_at
6b62de94e), S8's before-counts case (at 232efc47d), and the two propose-sources cases (at each commit's parent).

Task: DAEO-q8cl
Role: orchestrator
Implements: DEC-1073, DEC-1010
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
