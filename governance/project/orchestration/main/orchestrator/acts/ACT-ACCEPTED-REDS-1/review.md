## Round 3 (the owner's narrow check, P1-D (a), DEC-1144 (4))

# Review: path-map chain, round 3 (narrow check, the owner's P1-D (a), 2026-11-12)

Reviewer: fresh read-only independent reviewer (session `GOV_TICKET=DAEO-ktiw`, W2-176 worktree at `3b6c5cb79d39`). KPI: `pathmap-chain-r3`.

Bundles: ACT-EXAMIN-SETS-1 (`2f814211`), ACT-ACCEPTED-REDS-1 (`9c20e5e3`), ACT-PATHMAP-EXP-1 (`b26fe623`), each compared with its round 2 bundle (`e8020292`, `b8df21d8`, `9a945c99`).

1. **Entries byte-identical: pass.** The added lines hash the same in both rounds: EXAMIN `37e2465db5d5` (19 lines), REDS `ae208de8f751` (`accepted_reds: []` replaced by 9 lines), EXP `75f7830243f5` (1 line). Only the hunks' line numbers moved: by 2 for EXAMIN and REDS (the operator's two exemption lines at line 412), not at all for EXP (line 95).
2. **The chain: pass.** The live `w2/integrate` map hashes `30233a092a4b`, which is the EXAMIN before. EXAMIN after = REDS before = `1fe00f43d8ab`; REDS after = EXP before = `e4281125cf0e`; EXP after = `805bd918d467`. Round 3's end differs from round 2's end only by 6b8634d2c's two lines.
3. **Nothing else changed: pass.** `apply.sh` differs in comments only (round label, before hash and name, `build_r3.py`, and for EXP a rebuild hint naming `insert_exp.py`, which exists). `list.txt` differs in hashes only. Each manifest differs in hashes only, and its `checks` are identical. Every file hash and manifest sha256 was recomputed and matches.
4. **The rehearsal: pass.** `rehearsal.r3.log` ends `failures: 0` (193 checks; sha256 `52097d78c545`, the same as each bundle's log). In my own `--no-hardlinks` clone of `w2/integrate` (`1bc1893cc96d`), `check`, `apply`, `verify` and `PYTHONPATH=src python3 -m gov.check.pathmap` exited 0 for each ACT in order; the final map was `805bd918d467`.

Findings: none.

What would reverse this: a byte difference between the rounds' added lines; the live map moving off `30233a092a4b` before the ACTs are applied; a code line differing in `apply.sh`; a non-zero exit in the chain.

Note: one extra step (running the manifests' `checks` on the applied clone) was refused once by the guard (DEC-820 (c)/(d)). It is not one of the four checks and was not tried another way; the check commands were compared as text and are identical between rounds.

```verdict
{"kpis": [{"kpi": "pathmap-chain-r3", "verdict": "pass", "findings": []}]}
```
