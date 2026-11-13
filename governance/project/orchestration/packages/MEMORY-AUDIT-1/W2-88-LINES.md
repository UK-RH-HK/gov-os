# Proposed lines for W2-88 (`DAEO-2bdu`): the audit in an adopted repository

Proposed by the product-spec helper for the CTO, 2026-11-11 (DEC-1101 (1), DEC-1125 (2)). **W2-88's ticket file is not
edited here**; another helper audits tickets tonight. The CTO adds these lines when W2-88 is next touched, in W2-88's
own form (they are numbered after its S17).

Each line: one outcome with its `Verify:`.

- **depends_on, to add:** `DAEO-61vm` (W2-170), `DAEO-k1e2` (W2-171) and `DAEO-p8tv` (W2-172), so that W2-88's memory
  part calls the audit's core and carries no second copy.
- **allowed_paths, to check:** `src/gov/adopt/memory_sets.py` is already listed (DEC-1099 (2)); no new path is needed.

**S18 The audit's schedule at adoption.** An adopted repository is audited on the same rhythm by the same tool (weekly
while active, monthly once stable, by W2-172's rule). Adoption writes the repository's audit record: its sets root, its
audit names, its mode, the three briefs' variant ids and their sha256, and the first audit's earliest date. It starts no
audit and installs no schedule line itself (the crontab is an ACT). Verify: a planted adoption writes the record with
those fields; a grep of the planted crontab and sets root before and after finds no change [DEC-1101 (1)-(2), DEC-1125
(2)].

**S19 The briefs' variants, approved once.** The adopted repository's writer, checker and auditor briefs are the Gov OS
briefs (`packages/MEMORY-AUDIT-1/briefs/`, once approved) with two parts replaced by the repository's own: the domain
table (the writer's section 5 items 1 and 3, the checker's section 5a) mapped from S12's twelve categories to the
repository's domains, with every dropped category recorded, and the list of records the audit stays blind to. Nothing
else changes. Each variant is approved once by the repository's owner and hashed; a launch under an unapproved variant is
refused. Verify: a planted adoption's variants differ from the Gov OS briefs only in those two parts (a diff test); a
launch under a variant not on the planted approved list exits 10 [DEC-1101 (2), DEC-1099 (2)].

**S20 One core, not two.** `src/gov/adopt/memory_sets.py` calls `gov.memaudit` (W2-170's checks and declaration,
W2-171's measure and pool) and defines no pre-flight, use-once marker or figures of its own. Verify: a test that the
module imports from `gov.memaudit` and defines none of those functions; S12 and S13's planted runs produce the same
declaration and verdict line as the audit's [DEC-1101 (1), DEC-1099 (2), DEC-1125 (2)].

**S21 The first scheduled audit follows the verdict set.** An adopted repository's first scheduled audit runs only after
its verdict set (S13) was used and its result record written; the audits' log starts at the verdict set's commit
(`gov.memaudit baseline`), and the tuning and verdict sets join the repository's pool. Verify: a planted adoption
before S13's USED marker: `due` says `not due: no verdict set used`; after it: the baseline line holds the verdict
commit [DEC-1101 (1), DEC-1098 (1)].

**S22 The walls for an adopted repository by one ACT.** Adoption writes one ACT package for the repository's owner's
operator: the walls' template copy, the sets root folder (mode 0700), the approved list with the three variant briefs,
and the path-map hidden globs. Adoption never applies it. Verify: a planted adoption writes the package and nothing in
the planted sets root or path map [DEC-1101 (2)-(3), DEC-1099 (2)].

**S23 The audit's cost is stated at adoption.** The adoption record gives, for the repository's set size, the estimated
tokens and USD per audit, the GPU minutes and the owner's minutes, from `packages/MEMORY-AUDIT-1.md` section 7, and
names the figure to replace once the first audit has measured them. Verify: a string test on a planted adoption record
for the four figures [DEC-1101 (3)].

**Failure lines to add:** an audit started by adoption; a variant brief launched without the repository owner's
approval; a second copy of the pre-flight, the use-once marker or the figures in `src/gov/adopt/`.
