# ACT-W1-01-EXEMPT-2: five commits listed in `acceptance_exemptions` (DEC-1123 item 3)

For the owner's operator, in the main tree: your own `Role: owner` commit, as ACT-W1-01-EXEMPT-1's was.

## What and why
W1-01's DEC-253 rule refuses a merge commit that itself changes `tests/acceptance/**` without `Role:
independent-test-designer`, and a non-merge commit under `tests/acceptance/**` without that role. Five commits on
`w2/integrate` offend, so two W1-01 cases are red. The owner decided (DEC-1123 item 3; five ids confirmed in chat,
2026-11-10) to list them in `governance/project/path-map.yaml` `acceptance_exemptions`, by full id:
- `cade65dfe0454bb1b34c6a44bd475a9d67c5e45e`: merge w2/integrate into w2/W2-20-d10c-tests (W1-32's README)
- `04460404ea8a07bfb3f3f0019d3384e30c7f9466`: merge w2/integrate into w2/W2-145-d10-tests (W1-19's README)
- `8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a`: merge w2/W2-32-index-tests into w2/W2-32-tests (W2-32's README, 11-04)
- `ab169d051b82072f0db4350b2066eabf6919ffa0`: the second 11-04 merge of W2-32's README (w2/integrate into w2/W2-32-index-tests)
- `15952bbfa576dcfabb7d36d95912a848077e5c3c`: the owner's ACT-GUARD-SETS-1 commit, which deleted W2-84's hidden-half
  cases (DEC-1061, DEC-1097)

Each of the first four settled a README conflict as the test designer had. The `decision` value is the bare `DEC-1123`
on all five (W1-01's reader accepts only one `DEC-<n>`); the item, DEC-253, DEC-1061 and DEC-1097 are in each
entry's trailing comment.

## Class (O), and why
`class-rules.yaml` rule `path-map`: a ratchet list such as `acceptance_exemptions` is read only from the owner's
commits, so the commit is the owner's (`Role: owner`). The CTO does not commit it.

## The diff (`governance/project/path-map.yaml`; sha256 of the diff file 7c1863ca0e93...cd48c; 1 file, 10 insertions)
```
@@ -397,6 +397,16 @@ acceptance_exemptions:
     decision: DEC-900
   - commit: "0568d91baf566b4d8f3ccb448e51af41cbb46d03"
     decision: DEC-1031
+  - commit: "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "04460404ea8a07bfb3f3f0019d3384e30c7f9466"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "ab169d051b82072f0db4350b2066eabf6919ffa0"
+    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)
+  - commit: "15952bbfa576dcfabb7d36d95912a848077e5c3c"
+    decision: DEC-1123  # item (3); the owner's ACT-GUARD-SETS-1 commit deleted W2-84's hidden-half cases (DEC-1061, DEC-1097)
```
The path map is unchanged between `adeba3758` and the rehearsal base, so `git apply --check` of this diff is clean
there. If `path-map.yaml` has moved when you run it, the script below still works (it anchors on the DEC-1031 entry).

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
m = '    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)\n'
b = a + '''  - commit: "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e"
''' + m + '''  - commit: "04460404ea8a07bfb3f3f0019d3384e30c7f9466"
''' + m + '''  - commit: "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a"
''' + m + '''  - commit: "ab169d051b82072f0db4350b2066eabf6919ffa0"
''' + m + '''  - commit: "15952bbfa576dcfabb7d36d95912a848077e5c3c"
    decision: DEC-1123  # item (3); the owner's ACT-GUARD-SETS-1 commit deleted W2-84's hidden-half cases (DEC-1061, DEC-1097)
'''
assert s.count(a) == 1
open(p, 'w').write(s.replace(a, b))
EOF
git diff --stat -- governance/project/path-map.yaml
python3 -c "import yaml; yaml.safe_load(open('governance/project/path-map.yaml'))"
git add governance/project/path-map.yaml
git commit -m "Owner decision DEC-1123 item 3: acceptance_exemptions lists five merges and commits W1-01's rule refuses (cade65dfe045, 04460404ea8a, 8c512d7e7921, ab169d051b82, 15952bbfa576; DEC-253, DEC-1061, DEC-1097)" --trailer "Task: decision-record" --trailer "Role: owner"
```
The trailers are those of the DEC-1031 commit (`2acc8a314`): `Task: decision-record`, `Role: owner`; it had no
`Co-Authored-By`, so this has none.

## Expected output
- `git status` line: nothing. Diff stat: `1 file changed, 10 insertions(+)`. The YAML line prints nothing.
- Rehearsal (throwaway clone of `adeba3758`, `PYTHONPATH=<clone>/src`, `test_w1_01_history.py` and
  `test_w1_01_integration_merges.py`): before, `2 failed, 39 passed` (the five ids named); after, `41 passed`.
  Undo rehearsed: `path-map.yaml` identical to its prior content, YAML loads.

## The undo and the landing check
```
git revert <the commit>
```
Landing check (on `w2/integrate` after the commit; about 1.5 minutes):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS && PYTHONPATH=$PWD/src python3 -m pytest \
  tests/acceptance/W1-01/test_w1_01_history.py tests/acceptance/W1-01/test_w1_01_integration_merges.py \
  -q -p no:cacheprovider --tb=line
```
Expect `41 passed`. A commit made after `adeba3758` that touches `tests/acceptance/**` without the test designer's
role would be named here as a new red; it is not one of the five.

## Note for later
The comment line above `acceptance_exemptions` in `path-map.yaml` still says the three ratchet lists are frozen by
DEC-1052 Q-10 (no new entry). DEC-1123 item 3 is the later owner decision and holds; this commit leaves the comment
as it is, to be amended separately.

Rehearsal files: `.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-2/` (`rehearsal.log`, `path-map.diff`, `apply.py`).
