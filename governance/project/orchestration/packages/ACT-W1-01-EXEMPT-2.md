# ACT-W1-01-EXEMPT-2: three merge commits listed in `acceptance_exemptions` (DEC-1123 item 3)

For the owner's operator, in the main tree: your own `Role: owner` commit, as ACT-W1-01-EXEMPT-1's was.

## What and why
Three merges on `w2/integrate` settled a README conflict under `tests/acceptance/**` in the merge commit itself, as
the test designer had; each carries a role other than `independent-test-designer`, so W1-01's DEC-253 rule refuses
them and two W1-01 cases are red. DEC-1123 (3) (owner, 2026-11-10) lists them in `governance/project/path-map.yaml`
`acceptance_exemptions`, by full id:
- `cade65dfe0454bb1b34c6a44bd475a9d67c5e45e`: Merge w2/integrate into w2/W2-20-d10c-tests (W1-32's README)
- `04460404ea8a07bfb3f3f0019d3384e30c7f9466`: Merge w2/integrate into w2/W2-145-d10-tests (W1-19's README)
- `8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a`: Merge w2/W2-32-index-tests into w2/W2-32-tests (W2-32's README, 11-04)

## Class (O), and why
`class-rules.yaml` rule `path-map`: a ratchet list such as `acceptance_exemptions` is read only from the owner's
commits, so the commit is the owner's (`Role: owner`). The CTO does not commit it.

## The diff (`governance/project/path-map.yaml`; `git apply --check` clean at c9742b089)
```
@@ -397,6 +397,12 @@
     decision: DEC-900
   - commit: "0568d91baf566b4d8f3ccb448e51af41cbb46d03"
     decision: DEC-1031
+  - commit: "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "04460404ea8a07bfb3f3f0019d3384e30c7f9466"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
```
The `decision` value must be the bare `DEC-1123`: W1-01's reader (`w1_01_support.py`) accepts only `DEC-<n>` and
drops anything else, so the item and DEC-253 go in the trailing comment.

## The commands
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short -- governance/project/path-map.yaml
python3 - <<'EOF'
p = 'governance/project/path-map.yaml'
s = open(p).read()
a = '''  - commit: "0568d91baf566b4d8f3ccb448e51af41cbb46d03"
    decision: DEC-1031
'''
c = '    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)\n'
b = a + '''  - commit: "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e"
''' + c + '''  - commit: "04460404ea8a07bfb3f3f0019d3384e30c7f9466"
''' + c + '''  - commit: "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a"
''' + c
assert s.count(a) == 1
open(p, 'w').write(s.replace(a, b))
EOF
git diff --stat -- governance/project/path-map.yaml
python3 -c "import yaml; yaml.safe_load(open('governance/project/path-map.yaml'))"
git add governance/project/path-map.yaml
git commit -m "Owner decision DEC-1123 item 3: acceptance_exemptions lists cade65dfe045, 04460404ea8a, 8c512d7e7921 (W1-01's merge rule, DEC-253)" --trailer "Task: decision-record" --trailer "Role: owner"
```
The trailers are the ones of the DEC-1031 commit (`2acc8a314`); it had no `Co-Authored-By`, so this has none.

## Expected output
- The `git status` line shows nothing; the diff stat shows `1 file changed, 6 insertions(+)`; the YAML line prints nothing.
- Rehearsal (throwaway clone of HEAD c9742b089, `PYTHONPATH=<clone>/src`, `tests/acceptance/W1-01/test_w1_01_history.py`
  and `test_w1_01_integration_merges.py`): before, 2 failed, 39 passed (red on the three ids and on two more below);
  after the three entries, still 2 failed, 39 passed, the three ids gone.

## NOT GREEN with these three alone: two more ids stay red (owner to decide)
After the three entries the same two cases name:
- `ab169d051b82072f0db4350b2066eabf6919ffa0`: a merge of 11-04 (w2/integrate into w2/W2-32-index-tests, `Role:
  orchestrator`) that also changes `tests/acceptance/W2-32/README.md`; not `8c512d7e7`.
- `15952bbfa576dcfabb7d36d95912a848077e5c3c`: a non-merge `Role: owner` commit of 11-08 (ACT-GUARD-SETS-1, deletes W2-84's
  hidden-half cases under `tests/acceptance/`).
With those two also listed (a second rehearsal, `rehearsal-five.log`) the two cases are green: 41 passed. Listing them
needs the owner's word; this package lists only the three DEC-1123 (3) names.

Note: the path map's comment line above `acceptance_exemptions` says the ratchet lists are frozen by DEC-1052 Q-10 (no
new entry). DEC-1123 (3) is the later owner decision and holds; the comment is left as it is.

## The undo and the landing check
```
git revert <the commit>        # rehearsed: path-map.yaml returns to its prior content
cd /home/usain/Dynamic-Agentic-Engineering-OS && PYTHONPATH=$PWD/src python3 -m pytest \
  tests/acceptance/W1-01/test_w1_01_history.py tests/acceptance/W1-01/test_w1_01_integration_merges.py \
  -q -p no:cacheprovider --tb=line
```
Landing check: the three ids are no longer named; green (41 passed) only when the two further ids are also listed.
Rehearsal files: `.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-2/` (`rehearsal.log`, `path-map.diff`, `apply.py`).
