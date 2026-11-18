# Lead brief: reds-records (records, the path map, the schema check, lists)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/REDS-COMMON.md` first and follow it.
Branch `e2/reds-records` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-reds-records`. Task trailer:
`Task: emergency-2`, `Class: Q`.

**Your reds**
1. **The path map: `docs/emergency-2/briefs/**` is in no namespace.** W1-08 `test_every_tracked_path_matches_exactly_one_namespace`,
   W2-91 (acceptance and `tests/unit/retrieval/test_w2_91_full_embeddings.py`), W2-86
   `test_guard_outside_template_every_verdict_as_at_the_base`. (R): put the briefs folder in the namespace and with the
   embedding verdict the rest of `docs/emergency-2/` has in `governance/project/path-map.yaml`.
2. **W1-01 (2 cases): ten commits touch `tests/acceptance/**` without the test designer's trailer:** 6b0de1192,
   6a16c4b8a, 2631bde8c, 24a384ae8, b33eecd9e, 1c1a282bd, b9eb21d5d, 85710e6e6, 5849e19e8, bddad45b2. They are the
   outgoing CTO's fixes of 2026-11-17/18, updating tests to what EMERGENCY-2 retired or changed (§6.1's row "update or
   retire with what they assert"; §4.2). The CTO's decision: (R) list each by its full id in the path map's
   `acceptance_exemptions`, in the form and with the reason line the entries already there use.
3. **W2-130 (2 cases): new drift pairs from DEC-1211 and DEC-1212's `Changes:` marks** (DEC-313, DEC-314, DEC-820,
   DEC-1082, DEC-1128, DEC-1203, DEC-1205 to DEC-1211; DEC-1120, DEC-1183 to DEC-1212). They are real changes the owner
   approved. (R) or (T): record them where the test's set-aside list lives; if that list is in `tests/acceptance/`, (T).
4. **The core schema check is red on the archive:** W2-02 `test_core_schema_is_green_on_this_repository`, W2-54
   `test_w2_54_audit_report` and `test_w2_54_green_here`, W2-64 `test_core_schema_is_green_here_and_names_docs_imported`:
   107 findings in `docs/emergency-2/archive/memory-2026-11-16/*.md` (archived memory files whose front matter has no
   `type`). The archive is history (EMERGENCY-2 §11.1, §11.3). The CTO's decision: the check skips
   `docs/emergency-2/archive/**` the way it already skips other history; configuration over code. Leave the archived
   files' bytes as they are.
5. **W2-49 (5 cases): `cit-p-lines-applied` is FAIL: "CIT-P line with no change: CAP-44.m (W2-192-CIT-P.md, wave W2)".**
   Find whether CAP-44.m was meant to change the Contract with W2-192 and did not, or the record is wrong. The Contract
   is being re-baselined (audit 7, the owner's G5): do not edit the Contract's text; if that is the fix, stop and
   return it as one line with options.
6. **W1-32 `test_the_command_set_is_the_twelve_and_the_three_recorded_ones`: `gov spend` is not recorded.** Find who
   added `spend` and why (`git log -S`). A real command: the list records it ((T) if the list is in the test). A
   stray: return it.
7. **W2-69 `test_the_unit_folder_named_secrets_is_gone`: `tests/unit/secrets` exists again** (W2-88's unit tests,
   shadowing the standard library's `secrets`). (C, unit tests only): rename the folder to the name W2-69 gave it,
   imports updated; run the renamed folder.
8. **W1-30 r11 (2 cases):** the list names `tests/acceptance/W1-16/test_w1_16_ui_off.py`, which no longer collects,
   and the W1-16 fixture's counts are (91, 39) against I3 F7's (94, 67). Find what removed the cases (probably the
   guard's retirement); bring the list and the counts to what is there, (T) or (R) by where they live.
