# ACT-GUARD-FIX-5 round 2: F1's reversal cases, run by the CTO (2026-11-13 17:31 UTC)

The reviewer's record `reviews/act-guard-fix-5-r2.md` gives F1 from reading the code, not from a run, and names four
reversal calls. I ran them as an engineer on DAEO-03ub, using the pinned interpreter (`~/.local/bin/gov`'s shebang) and
`pretooluse.py -E`. The hook copies were the live `.claude/hooks/` with the bundle's `before/` and `after/` copies of
bash_writes.py. The project was a depth-1 clone of w2/integrate in the scratchpad. The probe was
`scratchpad/f1probe/probe.py`. Nothing was written to any tree.

| case | before | after |
|---|---|---|
| (a) `bash -euo pipefail <<'EOF'` / `# don't overwrite` / `echo hi` / `EOF` / `echo x > tests/acceptance/X/zz.py` | deny | **allow** |
| (b) the same with `bash -o pipefail <<EOF` (unquoted) | deny | **allow** |
| (c) the same with plain `bash <<EOF` (unquoted) | deny | **allow** |
| (d) (a) with `python3 -c "open('tests/acceptance/X/zz.py','w').write('x')"` | deny | **allow** |
| control: (a) with `# do not overwrite` (no apostrophe) | deny | deny |

**F1 is confirmed.** The bundle at manifest ef9078eb is not stricter-only: an apostrophe in a comment inside a shell
heredoc body opens the whole call, including the plain `bash <<EOF` form, which is refused today. The bundle must not
be applied as it stands.
