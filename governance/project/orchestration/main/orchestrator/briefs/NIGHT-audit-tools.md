# Anti-drift audit (d): every emergency tool the kernel or an adopted repository needs, mapped to a ticket (DEC-1125 (3) (iii) d)

Read `NIGHT-common.md` first. Role: product-spec helper, Sonnet high, class C2.

## The task
1. Read `governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md` (71 rows, 7 groups before EXAMIN's copy, its
   §2 and §4 routes) and DECIDED-NOT-DONE row 107.
2. For each row the kernel or an adopted repository needs (the inventory says which; judge the rest by its text):
   find its home ticket (`.tickets/*.md`: grep the tool's name, its W2 id, its KPI). The mapping holds only if the
   ticket's `kpis.success` carries a line that specifies the tool (what it does, measurably). Mark each row: mapped
   (ticket, KPI line), mapped without a KPI line (the line to add, proposed), or missing.
3. **File a ticket where one is missing** with `tk create` then the fields in the form of `.tickets/DAEO-ar89.md` and
   `.tickets/DAEO-l4gf.md` (class, role, allowed_paths, kpis with S-lines and decision brackets, sources, profile,
   acceptance_tests, tags including `after-the-lift`). WBS ids **W2-156 to W2-169** only (another helper uses W2-170
   up); group small tools into one ticket where they share a home. For "mapped without a KPI line": do not edit the
   ticket (another helper is auditing tickets tonight); list the proposed line.
4. Mark the rows needed **before EXAMIN's copy** (the inventory's 7 groups, and P1-PLAN P1-14's closure).
5. Run the structural pass on your new tickets' links:
   `python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS`
   and resolve every UNLINKED_ID notice in your tickets (add the cited id to `sources`).

## Paths you may write
New `.tickets/*.md` files you create (W2-156 to W2-169), `governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md`
(a "home ticket" column or §, only), `governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md` (your
report). Nothing else.

## Return
The twelve fields, short: counts (rows needed, mapped, mapped without a KPI line, missing), the tickets filed (DAEO id,
W2 id, title, rows covered), the proposed KPI lines, the before-EXAMIN marks. Estimate 1.5 h.
