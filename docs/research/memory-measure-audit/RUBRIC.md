# A rubric for a good memory-measure question (DEC-1068, the audit of the 48 questions, step 1)

- **Status:** DRAFT for the owner. Nothing in the set changes until the owner decides (DEC-1068 (3)).
- **Written by:** a session independent of the retrieval work, 2026-11-04, at `w2/integrate` `8284fb408bd4`.
- **Drawn from:** W2-61's KPIs and failure lines (`.tickets/DAEO-iw1f.md`), W2-61h's KPIs and failure lines
  (`.tickets/DAEO-h2k3.md`), DEC-1009, DEC-1060, DEC-1067 (c), DEC-1068 (the audit), the path map
  (`governance/project/path-map.yaml`, D-7's M-4 split), the measure's question form and matching rule
  (`src/gov/retrieval/measure.py`, docstring), the context packet's precedence (`src/gov/context/__init__.py`,
  `PRECEDENCE`), the path map's `retrieval_authority` tiers, the kernel skills, the role files and the briefs.
- **Not used:** no search result, measure record or figure, and no rank of any question. A question passes or fails
  on what the repository holds, never on how retrieval did with it (DEC-1067 (b), (c)).

## 1. How to apply it

1. **Where:** at the head of the tree that is measured (today `w2/integrate`). The measure resolves every source at
   the measured root, not at the question's `commit` (a source's own `commit` is not read by the measure), so the
   head is what counts.
2. **The measure's matching rule, which R6 and R7 follow** (`measure.py` lines 20 to 26): a source is `path`, with
   an optional `heading` and `lines: [first, last]`. A `heading` is one whole line of the file, found as the first
   line equal to it. Found, a Markdown `#` heading spans to the next heading of the same or a higher level; any other
   heading spans as many lines as `lines` state, starting at the line found. Not found, `lines` are used as written.
   A hit is any evidence item on the same path whose lines overlap the span. An entry is one piece of evidence the
   answer needs; a list inside an entry is alternatives, any one of which counts.
3. **Per question:** each item PASS or FAIL, a reason code from the item's list, and one sentence. A FAIL is
   **major** when it changes what is scored (a wrong or missing gold source, a span that misses the answer, a wrong
   answer) and **minor** when it does not (a stale detail in the gold answer's text, a category).
4. **A recommendation, never an edit:** re-label (sources or gold answer), re-anchor (same fact, new span),
   re-word (the question's text), mark as a keyword question, retire. A label changes only where it is wrong, never
   to fit a result; the old label is kept in `retired/` (DEC-1060's form, DEC-1067 (c)).
5. **R5 is judged on the set, not per question.**

## 2. The items

### R1 Correct today, from the governing source

*Source:* DEC-1060 (a question that rewards a replaced decision works against memory's design), DEC-1067 (c), W2-61
KPI 3 and failure line 4 (the governing source, never lens B's report), W2-61h KPI 3 (supersession questions).

**Pass test:**
1. Find the governing source of the asked fact. For a rule: the highest current record that states it, in the
   context packet's order (Charter, Contract, decision, specification, ticket). For a code fact: the code at the head.
2. A decision counts only with status ACCEPTED. A PROPOSED, SUPERSEDED, RETIRED, REJECTED or withdrawn entry is never
   a gold source, not even as an alternative; neither is a part of an entry that a later entry's "Changed by" line
   replaces. Read the entry's status line and search the register for later entries that name it.
3. Every alternative is the governing source, a faithful restatement of it (a generated Contract record, a ticket
   KPI line or brief line restating it) or, for a code fact, the code. None is in the `reports` tier
   (`tests/**`, `docs/assessment/**`, `docs/audit/**`, `docs/probes/**`).
4. Every factual claim of `gold_answer` holds at the head: names, values, counts, lists, file names. A line number or
   a count in the gold answer is a claim unless the answer itself says "as of <commit>"; a comment above the YAML
   does not count.
5. A supersession question names the superseded record as the naive answer, never as gold.

**Codes:** `R1-SUPERSEDED`, `R1-NOT-GOVERNING` (a PROPOSED entry or a report as gold), `R1-WRONG` (the substance is
false today: major), `R1-INCOMPLETE` (the head adds a case the answer omits), `R1-DETAIL` (a stale line number, file
name or similar detail: minor).

### R2 Searchable by meaning, or marked as a keyword question

*Source:* DEC-1068 (the audit, item (1)); D-7's M-4 path map; DEC-1066 (3) G4 (the evaluation's own documents in
neither index).

**Pass test:** place every alternative of every entry in its namespace with the path map at the head (each tracked
path matches exactly one namespace).

| Class | Namespaces at `8284fb408bd4` |
|---|---|
| Embedded (by meaning and by keyword) | `root-files` (`*`), `tickets` (`.tickets/**`), `docs` (the listed `docs/` paths), `project-overlay` (`governance/*`, `governance/project/*`, briefs, prompts, orchestration's `*`, packages, tools, the CHECKPOINT and PR records), `kernel-template`, `gov-source` (`src/**`), `carried-schemas` (`schemas/**`) |
| Keyword-only (not embedded, lexically indexed) | `agent-settings` (`.claude/**`, `.rulesync/**`), `ci` (`.github/**`), `doc-records` (`docs/close/**`, `docs/checkpoints/**`, `docs/probes/**`), `orchestration-records` (orchestration's `closes/`, `nightly/`, `sessions/`, `reviews/`), `kernel-vendored`, `kernel-adapter-copies`, `tests` (`tests/**`), `fixtures` (brownfield, greenfield, migration, README), `carried-code` (`cli/**`) |
| In neither index | `evaluation-sources` (lens B's report, W2-15a's `raw/**`), `evaluation-fixtures` (`fixtures/evaluation/**`, `fixtures/memory-quality/**`) |

An entry is **keyword-only** when none of its alternatives is embedded. The question passes when every entry has an
embedded alternative, or when the question is marked as a keyword question (proposed form: a field
`keyword: true` with a comment naming the keyword-only namespace; the measure ignores unknown fields). An entry with
an alternative only in neither index fails whatever the marking: no route can find it. Re-check the table against the
path map at the head each time: it is the path map, not this table, that decides.

**Counts reported for the set:** questions with **any** entry keyword-only, and questions with **all** entries
keyword-only (the second is a subset of the first).

**Codes:** `R2-ANY-KW`, `R2-ALL-KW`, `R2-NO-INDEX`, `R2-NO-NAMESPACE` (a path no namespace holds).

### R3 Unambiguous and answerable as asked

*Source:* DEC-1068 (the audit, item (1)); DEC-1060 (q03 kept because it is answerable as asked); W2-61h KPI 1.

**Pass test:**
1. Read the question alone, without the gold. Write down every reading a working agent could take. Pass if every
   reading leads to the same gold sources; fail if two readings lead to different answers (for example a word that
   means two fields of the record, or two components of the same name).
2. The question presupposes nothing that is false at the head. A presupposition that the gold answer itself corrects
   ("no fixed figure any more") passes only if the gold sources state the correction.
3. It asks at most three facts, and each asked fact is a listed entry or is held by every alternative of one (R7).
4. A bare id, error code or symbol as the whole question passes; it is read as "what is X / where is X raised or
   defined", and the gold answer must answer that reading.
5. A question about something that exists nowhere (W2-61h's "an id that exists nowhere") passes only if its gold
   source is a line that settles the absence (for example the register's "Next free id" line, or the id's range) and
   the gold answer says "none"; otherwise it cannot be scored by hit@5 and is marked for separate scoring.

**Codes:** `R3-AMBIGUOUS`, `R3-PRESUPPOSES`, `R3-TOO-MANY`, `R3-NEGATIVE-UNSCORABLE`.

### R4 The kind of question agents really ask

*Source:* DEC-1068 (the audit, item (1)); DEC-836 (every worker uses `gov retrieve` for what it needs to know);
DEC-859, DEC-860; the briefs (`governance/project/briefs/LEAD-w2-common.md` lines 30 and 31,
`AUDITOR-common.md` line 8), the retrieval skill (`template/governance/kernel/skills/retrieval/SKILL.md`), the
discovery skill (`gov retrieve` before an experiment or a decision package), the role files.

**Pass test:**
1. Name a role (engineer, independent test designer, ticket lead, independent auditor, orchestrator, research,
   product-spec) and a task from its role file, a kernel skill or a brief during which it needs this fact. Examples
   that pass: an engineer checking its allowed paths or the callers of a function it changes; a test designer
   checking a KPI's governing rule; a lead checking a ticket's dependencies; an auditor checking the finding format;
   anyone pasting an error code or a decision id it met.
2. The wording is one that role would type: a question, an id, an error code or a symbol. It fails if it is built
   from the gold source's own distinctive phrasing, so that it rewards matching the text rather than finding the
   fact.
3. The fact is one memory is the right place for (not one an agent would always get from `tk show` or one command,
   unless the question is a ticket question by design, per W2-61h's spread).

**Codes:** `R4-NO-ROLE`, `R4-PHRASED-FROM-ANSWER`.

### R5 The set spreads across code, decisions, tickets, the plan and the Contract (set level)

*Source:* DEC-1068 (the audit, item (1)); W2-61h KPI 3 (the 28 new questions' category quotas, DEC-954 Q9c);
the retrieval skill (failure and lesson records come ahead: CAP-14).

**Pass test** (thresholds proposed by this draft; the owner may set others):
1. Give each question its **governing domain**: the domain of the governing source of its main entry: code
   (`src/**`, the kernel hooks), decisions (the register), tickets (`.tickets/**`), the plan (`docs/plan/**`), the
   Contract and Charter (`docs/contract/**`, `docs/charter/**`). Count also the kernel template (roles, skills,
   hooks) and failure or lesson memory (`docs/lessons/**`, failure records) as cross-cutting tags.
2. On each half and on the 48: each of the five domains governs at least 10 % of the questions (3 of 24, 5 of 48);
   the kernel template is in at least 2 per half; failure or lesson memory in at least 1 per half.
3. No one subsystem (for example retrieval and the context packet, the guard, the close, checkpoints, rebuild) is the
   subject of more than 25 % of a half.
4. At least 2 per half are supersession questions whose naive answer is superseded (W2-61h KPI 3).
5. For the 28 new questions, W2-61h KPI 3's category quotas hold, read from each question's `category`.

**Codes:** `R5-DOMAIN-THIN` (name the domain), `R5-TOPIC-HEAVY` (name the subsystem), `R5-QUOTA`.

### R6 Every gold source holds its answer at the head (added: W2-61h KPI 4, its failure line 3; the measure's rule)

**Pass test:** for each alternative, resolve its span with the measure's rule (section 1, item 2) at the head and
read it.
1. The path exists; a `heading`, if given, is found; if not found, the stated `lines` still hold the answer.
2. The span holds the part of the answer its entry stands for: the deciding line (the check, the constant, the
   list) is inside it, not just next to it.
3. The span does not run into unrelated fields or sections (for example past a ticket's list into its next field),
   which would count a hit on text that does not hold the answer.
4. Advisory, not a fail: a lines-only anchor where a unique line exists to anchor on (it breaks silently on the next
   edit above it); a non-unique heading line that resolves to its first occurrence.

**Codes:** `R6-NOT-FOUND`, `R6-NO-ANSWER` (the span holds none of it), `R6-SPAN-MISSES`, `R6-SPAN-OVERRUNS`,
`R6-LINES-ONLY` (advisory).

### R7 Entries and alternatives are well formed (added: the measure's form; full evidence, DEC-833 item 3; DEC-860)

**Pass test:**
1. Each entry is one piece of evidence the answer needs; **each alternative in it holds that whole piece on its
   own** (otherwise a hit on a partial alternative is scored as the piece).
2. Every piece the gold answer needs is an entry (otherwise full evidence is scored without it). A list answer has
   one entry per member, or one alternative that holds the whole list.
3. Two entries that are the same evidence in two places are alternatives of one entry, not two entries.
4. The needed evidence fits the stacked budget: one alternative per entry, their spans' sizes added (characters / 4),
   is within the measure's stack budget (24,000 tokens by default, DEC-860).

**Codes:** `R7-PARTIAL-ALTERNATIVE`, `R7-MISSING-PIECE`, `R7-SPLIT` (alternatives listed as separate entries),
`R7-OVER-BUDGET`.

### R8 Never from the evaluation's own documents (added: W2-61 failure line 4; DEC-1066 (3) G4)

**Pass test:** no alternative is lens B's report, W2-15a's `raw/**` or anything under `fixtures/evaluation/` or
`fixtures/memory-quality/`, and the gold answer is not taken from them (the measure drops such an alternative
silently; an entry left with none could never be hit).

**Codes:** `R8-EVALUATION-SOURCE`.

### R9 Distinct (added: W2-61h failure line 2)

**Pass test:** no two of the 48 ask the same fact with the same governing source. Allowed: one pair per record of an
id-form question and a paraphrase of the same record (two routes to one fact). A new question must not copy or
paraphrase one of lens B's 20 (W2-61h failure line 2). The weaker-labelled question of a duplicate pair is the one
marked FAIL.

**Codes:** `R9-DUPLICATE` (name the other id), `R9-PARAPHRASE`.

### R10 The label's record and form (added: DEC-1060's form, DEC-1067 (c), W2-61h KPI 1)

**Pass test:**
1. The `category` matches the governing domain or W2-61h's category list (the stratified draw and R5 read it).
2. The file has `question`, `gold_answer`, `sources`, `commit`, and an `id` in the set's form.
3. Every label change since the set was fixed names the decision or order under which it was made, says why, was
   decided blind (from the question, the gold answer and the repository, never a run), and keeps the old label in
   `retired/`. A re-anchor (same fact, new span) needs the reason and the git history only.

**Codes:** `R10-CATEGORY`, `R10-FORM`, `R10-RECORD`.

## 3. Applying it to the hidden half (W2-61h's role, DEC-1068 (2))

1. Read-only, in the sets root (`~/gov-os-eval/.../hidden/`), by W2-61h's role only, under the hidden-half rule:
   no question, gold answer or source path is written, quoted or returned.
2. Apply R1 to R10 exactly as above, at the head of `w2/integrate`, with the path map there.
3. **Report per question:** its id, each item PASS or FAIL, the reason code, and a reason in general terms (for
   example "R6-SPAN-MISSES: the anchor's span ends before the deciding line"; never the line, the file or the fact).
4. **Report for the half:** R2's two counts (any keyword-only, all keyword-only) and, for those, the keyword-only
   namespaces as counts summed over the half (never per question); R5's counts per governing domain, tag and
   category; the number of FAILs per item, major and minor apart.
5. Recommendations in the same five words (re-label, re-anchor, re-word, mark as a keyword question, retire), per id.
   The corrections themselves are made only after the owner decides, by the checker the owner names (h02 and h24
   are the operator's, DEC-1068 (c)).

## 4. What this rubric does not decide

- It sets no threshold the owner has not approved: R5's numbers are proposals.
- It never judges a question by its score. A question retrieval misses is not wrong for that; a question it hits is
  not right for that.
