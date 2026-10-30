# W2-02 under W2-67 (DAEO-9nys), round 1, batch 2: the unmeasured case

Ticket `DAEO-9nys` (W2-67), KPI 5 (P-IS-7 (a); I4 §2.2 and F7). Written by a fresh independent test designer (MR-3).

## `test_w2_02_unmeasured.py::test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green` (commit `df170c14`)

- **Weak because (I4 §2.2, F7).** Its "names the type" half accepted `record_type in finding["message"]`, and the
  message holds the record's own path (`docs/research/RES-0001.md`, `docs/close/PROJ-aaaa/CL-PROJ-aaaa.md`), whose
  folder is the type's name. A finding that named no type passed.
- **Now.** The type is looked for in the finding's `type` field, or in its message once the record's path is taken
  out (as a whole word). The other assertions (a finding says unmeasured; the check exits non-zero) are unchanged.
- **Plant P67C-1.** The schema check's unmeasured finding loses its `type` field and its message names no schema
  file: `"message": f"{rel}: unmeasured, a schema cannot be read"` (one exact text change of `gov.check.schema`,
  made in memory in the check's own process by `w2_67c_run_patched.py`; W2-02's support runs the check as
  `sh -c "python3 -m gov.check.schema"`, which the plugin `w2_67c_plant` redirects for that fault). Plant modules,
  their record and the XML: `.gov-runtime/scratch/td-2/plant/`.
  - The revised case under P67C-1: **red**, both parametrizations ("no finding says the type research is
    unmeasured: [{'code': 'SCHEMA_UNREADABLE', 'path': 'docs/research/RES-0001.md', 'message':
    'docs/research/RES-0001.md: unmeasured, a schema cannot be read'}]"; the same for `close`), `g4-w2-02-P67C-1.xml`.
  - The case as it was (the base commit's file, run from the session scratch folder) under P67C-1: **green**, 4
    passed (`g4-w2-02-before-P67C-1.xml`): the weakness, shown.
  - The head: **green**, the file 4 passed (`g4-w2-02-head.xml`).
- **Rewrite-Reason:** the type was found in the record's own path, so a finding that named no type passed (I4 §2.2, F7).

## Cases left

`test_w2_02_failure.py::test_a_record_with_an_unknown_type_is_still_refused` and the outdated
`test_one_kernel_schema_is_a_decision_entry_…` are W2-64's (the brief of this batch); unchanged.
