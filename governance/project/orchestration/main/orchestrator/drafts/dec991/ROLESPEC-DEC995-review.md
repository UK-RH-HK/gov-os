task: Check ROLES-SPEC-1, ROLES-RESEARCH-1, the roles tickets, the kernel role files, the skills and `gov launch` against DEC-995, and propose KPI edits.

status: DONE (read-only; nothing written in the repository)

work_completed: Read ROLES-SPEC-1 in full and ROLES-RESEARCH-1 §1–2. Read the tickets for W2-33, W2-60a, W2-60b, W2-11 and W2-82 (`DAEO-4k3l`), the six kernel role files, the kernel and vendored skills' front matter, `launcher.py`, `role.py` on `w2/W2-60a`, `skill_validator.py`, `decide.py` and the stop hook.

files_changed: none

evidence: file:line references are given in the findings below.

tests: none run (analysis only)

discoveries: The launch sandbox depends only on the role and the ticket, so no skill widens it today. W2-60a's reader lets a session load every skill in `.claude/skills/`, not only the ones its role names. Six vendored openspec skills carry `allowed-tools`. The skill template does not exist yet. The stop hook (`subagentstop.py:33-34`) needs each field's value on the same line as its name, so the brief's "content on its own line" form is refused; this is a gap in the brief.

risks: Some vendored skills grant permissions, and every launched session can load any project skill.

lessons: A role's writes need to be machine-readable path classes. Without them, the Definition of Ready (DoR) cannot tell an engineer ticket from a product-spec ticket, because both write "the ticket's allowed_paths".

proposed_decisions: P-DEC995-1: a role's `Writes` are named path classes (`code`, `spec`, `acceptance-tests`, `findings`, `experiment`, `stream-scratch`), mapped to globs in the project's path map. P-DEC995-2: a skill's front matter is closed to `name`, `version`, `description` and `output` (a path class or `none`). P-DEC995-3: the six openspec skills are either stripped of `allowed-tools` or exempted by the owner.

unresolved: It is untested whether the CLI's `Skill(...)` deny rule works in headless launched sessions. W2-33's paths do not include `schemas/role.schema.json`, which ROLES-SPEC-1 §6.2 lists.

recommended_next_action: Record DEC-995 with P-DEC995-1 to 3, add the KPI lines below, move the validator to a child engineer ticket, and run a product-spec pass over ROLES-SPEC-1.

---

## Findings

**ROLES-SPEC-1**
1. §3.10 (line 521) treats frontend, DevOps/SRE and UX as Wave 3 *roles*. That contradicts DEC-957 Q5 (§10, line 864) and DEC-995. G23 (line 683) also lists UX as a role.
2. Skill packs are still listed as Wave 3 at §3.5 (line 434), G24 (line 684) and §6.2 (line 725). DEC-957 Q5 superseded that.
3. §5.2 (lines 600–615) has no `Reads` field. `Writes` is a free-text pattern used by "brief builder; documentation", which nothing enforces. `Skills` is optional and not a closed list. The §5.3 table (lines 622–632) and the example block (lines 636–648) have the same gaps.
4. §10 Q12 (line 866), echoed in RESEARCH §2.1 (line 79), says the CTO has "every other role's skills on demand". That would include `test-design`, whose output (`tests/acceptance/**`) the CTO may not write (rule 1).
5. §3.6 (lines 452–453): product-spec's reads say only "as the engineer", its writes are not separated from code, and `spec-writing` is not among its skills.
6. §3.10 (line 517): the CTO helper runs as `orchestrator`, whose writes are wide, and is narrowed only by its brief. Under DEC-995 a brief does not set permissions.
7. No section states that a skill never changes permissions; the only mention is CAP-24.b (line 75).
8. §6.3 (line 747): W2-82 gains only the lead id, with no role-scope condition.

**ROLES-RESEARCH-1**
- §2.7 (line 139) and §2.11–2.14 (lines 190, 197, 206) already follow DEC-995: an engineer plus a domain skill.
- Exception at line 197: the QA engineer "loads the same [security] skill" that engineers use. That skill's output is code, which the QA engineer may not write, so the QA engineer needs a review part whose output is findings.

**Code and files**
- `role.py` on `w2/W2-60a`: line 189 and lines 206–219 record every loadable skill, "named or not", and refuse none. Lines 114–120 read only `name` and `version` from a skill's front matter, so permission fields pass.
- `.claude/skills/openspec-*/SKILL.md` lines 7–10 carry `allowed-tools: Bash(openspec:*)`.
- The vendored superpowers skills and the kernel skills carry no permission field, and the kernel skills already say they grant nothing (CAP-24.b).
- `launcher.py` lines 37–40, 140–169 and 193: the settings (deny rules, sandbox, network) come from the role and the ticket alone, and skills never enter them. `decide.py:31` treats `Skill` as harmless. Both are sound only while skills carry no permission field.
- Role files: each states its allowed paths and permission classes, but none has a `Skills`, `Reads` or `Writes` line. `orchestrator.md:36–40` calls the lead "not a seventh role" even though its writes differ; W2-33's KPI at line 27 fixes this.
- The skill template `templates/skill.md` does not exist yet; it is in W2-11's paths (`k7hz:44`).
- W2-11 is a product-spec ticket that holds a code path (`k7hz:21`, `skill_validator.py`). That is exactly the kind of mixed ticket DEC-995 forbids; DEC-992 P-W2-11-2 moves the work to an engineer.
- W2-82's `PATHS_INVALID` (`4k3l:33`) checks only `tests/acceptance/**`.

## Proposed edits

### W2-33 (`DAEO-lrre`, open)
**success, replace line 28:**
```yaml
  - 'Machine-readable defaults per role in each role file, read by W2-60a''s launcher: model, effort, its reads (`- **Reads:**`), its writes (`- **Writes:**`, as path classes the project''s path map resolves, never this repository''s paths) and the closed list of skills it may load (`- **Skills:**`); each role file states that a role is its reads and writes and that no skill changes them; domain work sharing the engineer''s reads and writes (backend, frontend, API, data, security, DevOps, UI/UX) is a skill in the engineer''s list, never a role file; no role lists a skill whose `output` class its writes do not hold (spec-writing is product-spec''s, test-design the test designer''s; the CTO''s on-demand skills are only those its writes hold); effort high for the CTO and the Senior Engineers [DEC-954, DEC-839 item 5, DEC-957 Q5, DEC-995]'
```
**failure, replace line 36:**
```yaml
  - 'A role built other than as the approved roles spec states it; a role file placed by hand rather than generated; a role without its machine-readable defaults, its reads, its writes or its skills list; a role file listing a skill whose output class its writes do not hold; a domain specialist given a role file of its own [DEC-995]'
```

### W2-60a (`DAEO-cv58`, in_progress; lands in round 3 or later)
**success, replace line 32:**
```yaml
  - 'The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those and only those: a skill under .claude/skills/ or .claude/commands/ its `Skills` line does not name is not loadable in the session (the CLI''s own skill rule, or a package naming the gap) and is recorded as kept out; a named skill that is missing, or whose front matter carries a key outside the skill template''s list (allowed-tools or any other permission field), refuses the launch, naming the key [DEC-826 Q1, DEC-832 item 1, lens E F15, DEC-995]'
```
**failure, append to line 41:** `; a skill outside the role''s list loadable, or a named skill with a permission field in its front matter that still launches [DEC-995]`

### W2-60b (`DAEO-ecac`, open)
**success, replace line 34:**
```yaml
  - 'The launcher''s set of launchable roles (today the fixed WORKER_ROLES and OWN_TICKET_ROLES tuples in launcher.py) is read from the kernel''s role files, so a new role is a file, not a code change; a role file that is missing or unreadable refuses the launch; the five roles launch exactly as before; the session''s settings (deny rules, sandbox, network) come from the role file and the ticket alone: a planted skill naming wider tools, paths or hosts leaves them byte-identical [DEC-946 (W3-P09), DEC-826 Q1, DEC-995]'
```
**failure, replace line 39:** `- 'A fixed list of launchable roles left in code; a skill that changes the session''s settings, sandbox or network [DEC-995]'`

### W2-11 (`DAEO-k7hz`, in_progress; lands in its next round)
**success, amend line 62** by adding this after "Sources at the end": `; the front matter is closed to name, version, description and output (the path class its method writes, or none), with no permission field (no allowed-tools, permissions, paths, network, model or effort); a Never section stating that the skill changes no role''s reads or writes, and that work needing other writes goes back as a package for the role that holds them [DEC-959 item 5, ROLES-RESEARCH-1 §2, DEC-995]`
**failure, add:**
```yaml
  - 'A kernel skill, its generated copy or the skill template with a permission field in its front matter, or a step telling its role to write what its output class does not hold [DEC-995]'
```

### Child engineer ticket (validator code; DEC-992 P-W2-11-2; `skill_validator.py` leaves W2-11's paths)
**success:**
```yaml
  - 'gov check''s skill validator refuses a skill whose front matter has no output class or carries a key outside the skill template''s list (allowed-tools, permissions, paths, sandbox, network, model, effort or any other), naming the file and key; it reads the kernel skills and every generated copy, and names each vendored skill so found (today six openspec skills) for the owner [DEC-995, CAP-24.b, DEC-992 P-W2-11-2]'
```
**failure:** `- 'A skill with allowed-tools or another permission key in its front matter that the validator passes [DEC-995]'`

### W2-82 (`DAEO-4k3l`, open)
**success, add** (and change "The six conditions" to "The seven conditions" on line 33):
```yaml
  - 'ROLE_SCOPE, a seventh condition: a ticket whose allowed_paths, or a path one of its KPI lines names, fall outside its declared role''s writes (the role file''s `Writes` path classes, resolved through the path map) is NOT_READY, naming each path and the role whose writes hold it (a product-spec ticket naming src/**/*.py: engineer), so a mixed ticket is split before it starts; a role file without a readable Writes line is UNJUDGED [DEC-995, DEC-944 item 2]'
```
**failure, add:**
```yaml
  - 'gov claim or gov launch passes a ticket whose allowed_paths or KPI-named paths need another role''s writes, or refuses one without naming that role [DEC-995]'
```

### ROLES-SPEC-1, edits for a product-spec pass
1. **§3.0:** add the DEC-995 rule. A role is its reads and writes; a skill changes method only; work needing other permissions belongs to another role; a domain specialist is the engineer plus a skill.
2. **§3.1 and §10 Q12:** limit the CTO's on-demand skills to those whose output its writes hold, which excludes `test-design`.
3. **§3.5:** replace line 434 with the seven domain skills (DEC-957 Q5), each in the engineer's `Skills` list.
4. **§3.6:** state product-spec's reads explicitly; its writes are the `spec` class and never code; add `spec-writing` and `technical-writing` to its skills.
5. **§3.10:** line 521 becomes: frontend, DevOps and UI/UX are engineer skills; test execution and integration are tools (RESEARCH §2.15); architecture and performance stay Wave 3. Line 517: the helper's narrower writes are not a permission, so state that it holds the orchestrator's writes.
6. **§5.2 and §5.3:** make `Reads` required. Make `Writes` required as path classes, read by the DoR and the launcher. Make `Skills` required as a closed list, with unlisted skills denied. Close the skill front matter. Add Reads, Writes and Skills columns and update the example block.
7. **§6.1:** fix G23 and G24 as in items 3 and 5. Add G26 (skill permission fields and unlisted skills, filled by W2-60a and the child validator ticket) and G27 (role scope in the DoR, filled by W2-82).
8. **§6.2 and §6.3:** update the W2-33 KPI outline (lines 702–705 and 721–725) and the W2-82 line (747) to match the edits above.
9. **RESEARCH §2.12 (line 197):** give the QA engineer a security review part inside `qa-review` whose output is findings, instead of loading the engineer's `security` skill.