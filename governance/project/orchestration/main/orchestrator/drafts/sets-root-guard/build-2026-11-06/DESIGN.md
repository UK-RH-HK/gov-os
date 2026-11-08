# The sets-root guard: the build spec (DEC-1082 (3)), from the read-only design of 2026-11-06

The design was written by a read-only session and restated in full. The CTO accepts its two corrections to the CTO's
defaults; both are stated in the ACT for the owner:
- **(1) Six refused roles, not three.** The verdict sets also measure product-spec, the independent test designer and
  the independent auditor. Leaving them out would let them read `memory-verdict-2/retired/` (old copies of the
  questions) and `XCHECK.md` (the checker's report, which may quote them).
- **(2) Also `transcripts/**`.** It holds the writer's transcript of the hidden questions (`ACT-D8.md:46-48`), and
  refusing it costs the measure nothing. `runs/**` stays open: the CTO writes its results there, and no question text
  is kept there (`measure_verdict.sh:22`).

## Why
- The hook builds its hidden parts only for the tree roots (`pretooluse.py:364-367`, `119-151`).
- A path counts only when it lies under a root (`reads.py:179-183`).
- So `~/gov-os-eval/.../hidden/...` is never judged, for any role.

Do not add orchestrator to the sets root's `measures.roles`. The measure refuses itself for a role in that list
(`measure.py:68-73`, `246-251`), so the change would break every CTO measure.

## A. The path-map block
Put it in `governance/project/path-map.yaml` between line 544 (`    reads_denied: ["{ticket_impl}"]`, the end of
`role_paths:`) and line 545 (`# The retrieval authority order …`). An unknown top-level key is allowed: `validate`
checks only the keys it knows (`loader.py:228-244`).
```yaml
# DEC-1082 (3): the sets root outside the repository, where the hidden halves are kept since ACT-D8 (the measure's
# --sets-root). The guard (.claude/hooks/pretooluse.py) refuses these globs, under the root and in every tree, to the
# roles named here, and to each role a set in evaluation_sets measures (that set's hidden globs). It reads this block
# from the main tree's copy only. Reads and the writes the guard can resolve are refused alike. The measure is
# unaffected: its command names only the root, and it reads the sets root's own map, which does not change. The
# writer, checker and operator sessions run outside this guard (ACT-MSET-3, ACT-MSET-4, ACT-HLABEL-2, ACT-HNEW-1).
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/evaluation/memory-retrieval/hidden/**", "fixtures/evaluation/memory-verdict/**",
           "fixtures/evaluation/memory-verdict-2/**", "transcripts/**"]
  refused_roles: [orchestrator, engineer, research, product-spec, independent-test-designer, independent-auditor]
```
Leave the sets root's own map (`~/gov-os-eval/governance/project/path-map.yaml`) unchanged.

## B. The hook change (`.claude/hooks/pretooluse.py`)
**How the main tree is found from a worktree.**
- `main_tree(root)` (lines 182-194) uses `git rev-parse --git-common-dir`. G-14 already reads its block this way
  (line 382).
- A run clone has its own `.git`, so it reads its own map.
- Each tree runs its own copy of the hook. A worktree therefore gets the change only when `w2/integrate` is merged
  into it.

**B.1 New code, added after `main_tree` (after line 194):**
```python
SETS_BLOCK = "sets_root_hidden"  # DEC-1082 (3)
PATH_MAP = os.path.join("governance", "project", "path-map.yaml")
SETS_WRITE_REFUSAL = ("the call writes into the hidden part of an evaluation set, which is refused to this session "
                      "(DEC-1082 (3))")


def sets_root_rule(main):
    """DEC-1082 (3): the main tree's sets_root_hidden block (a branch cannot weaken it): the sets root as a real path,
    its hidden globs (project-relative, from the root) and the roles refused them; None with no block. A block not of
    that shape raises, and the hook refuses (fail closed)."""
    try:
        with open(os.path.join(main, PATH_MAP), encoding="utf-8") as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return None
    at = [i for i, line in enumerate(lines) if re.match(SETS_BLOCK + r"\s*:", line)]
    if not at:
        return None
    if len(at) > 1:
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    from gov.guard.heldout import load_yaml_unique
    from gov.guard.reads import _paths_ok
    data = load_yaml_unique("".join(lines[at[0]:end]))
    block = data.get(SETS_BLOCK) if isinstance(data, dict) else None
    if not isinstance(block, dict):
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is not a map")
    top, globs, roles = block.get("root"), block.get("hidden"), block.get("refused_roles")
    top = os.path.expanduser(top) if isinstance(top, str) else ""
    if (not os.path.isabs(top) or os.path.realpath(top) in ("/", HOME) or not _paths_ok(globs, True)
            or not isinstance(roles, list) or not roles or not all(isinstance(r, str) and r for r in roles)):
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is not a root, a list of hidden globs and a list of roles")
    return os.path.realpath(top), list(globs), list(roles)


_CLASSES = []


def classes():
    """SetsRoot and Judge (DEC-1082 (3)), made once the pinned judge is imported (inside main's fail-closed try)."""
    if _CLASSES:
        return _CLASSES[0]
    from gov.guard import reads

    class SetsRoot(reads._Part):
        """The sets root's hidden part. The guard walks it for file names only, never their text."""

    class Judge(reads._Judge):
        def listing(self, stages, cwd):
            """A listing the guard cannot place is refused as before, but for one case: only the sets root's part
            holds files, the listing is a real feed (not the stand-in for names read from a file: xargs -a, a while
            loop fed by a redirect), it starts outside the sets root, and none of its words names the sets root or
            a folder above it (~, /). Then the sets root cannot be what it lists, and the call is not refused for it."""
            why = super().listing(stages, cwd)
            if why != reads.RUNTIME_REFUSAL or cwd is None or stages == [["cat", "--"]]:
                return why
            tops = [p.root for p in self.parts if isinstance(p, SetsRoot)]
            if not tops or any(p.held() for p in self.parts if not isinstance(p, SetsRoot)):
                return why
            if any(reads._related(os.path.realpath(cwd), t) for t in tops):
                return why
            for words in stages:
                for w in words:
                    exp = reads._expand_token(w) or w
                    if not exp or (exp.startswith("-") and exp != "-"):
                        continue
                    full = os.path.realpath(os.path.join(cwd, exp))
                    if any(reads._related(full, t) for t in tops):
                        return why
            return ""

    _CLASSES.append((SetsRoot, Judge))
    return _CLASSES[0]
```
It relies on these pin lines: `RUNTIME_REFUSAL` (`reads.py:101`), the `[["cat", "--"]]` stand-in (`reads.py:1327`,
`1332`), `listing()` (`reads.py:1365-1385`) and `_related` (`reads.py:283-285`).

**B.2 In `main()`, replace lines 363-375** (from `# Rules 2 and 3, …` through its `answer("deny", why)`):
```python
    # Rules 2 and 3, the hidden half and secrets: the product's read judge with only these parts.
    SetsRoot, Judge = classes()
    mine = list(dict.fromkeys((role, acting)))
    hidden = []
    for r in mine:
        hidden += reads._hidden(root, r, ticket)
    parts = [reads._Part(t, hidden, reads.HIDDEN_REFUSAL) for t in tree_roots(root)] if hidden else []
    # DEC-1082 (3): the sets root outside the repository. The main tree's block names the root, its globs and the roles
    # refused them. To those globs are added the hidden globs of each set that measures the role, from the main tree's
    # map (an older branch's map cannot drop a set). They are refused under the sets root and in every tree.
    main = main_tree(root)
    rule = sets_root_rule(main)
    sets_parts = []
    if rule:
        top, globs, refused = rule
        outside = list(globs) if any(r in refused for r in mine if r) else []
        for r in mine:
            outside += reads._hidden(main, r, ticket)
        outside = list(dict.fromkeys(outside))
        if outside:
            sets_parts = [SetsRoot(top, outside, reads.HIDDEN_REFUSAL)] + \
                         [reads._Part(t, outside, reads.HIDDEN_REFUSAL) for t in tree_roots(root)]
    parts += sets_parts
    seen = tin
    if command is not None:
        # ACT-GUARD-FIX-3: a heredoc that cat or tee takes as data is no read; $((n+6)) is no listing.
        import bash_writes
        seen = dict(tin, command=bash_writes.reads_view(command))
    why = Judge(root, parts).tool(tool, seen, cwd)
    if why:
        answer("deny", why)

    # DEC-1082 (3): no write into those hidden folders by the roles refused them. Only a write whose target the guard
    # works out is judged; one it cannot work out is let through, as for rules 1 and 5 (G-1, G-2).
    if sets_parts:
        targets = []
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif command is not None:
            shell, code = bash_writes_of(command, cwd)
            targets = shell + code
        for t in targets:
            if isinstance(t, str) and t:
                full = os.path.realpath(os.path.join(cwd, os.path.expanduser(t)))
                if any(p.inside(full) for p in sets_parts):
                    answer("deny", SETS_WRITE_REFUSAL)
```
- **B.3 Line 382:** `role_reads.refusal(main_tree(root), …` becomes `role_reads.refusal(main, …`. It reuses the
  value only.
- **B.4 The docstring (lines 2-24):** add rule "2b (DEC-1082 (3))": the sets root's hidden folders, read from the main
  tree's `sets_root_hidden`, refused for reads and resolved writes to the named and measured roles, under the sets
  root and in every tree.
- **Unchanged:** `bash_writes.py`, `role_reads.py` and every pin file.
- **Before relying on any name:** check each one the code uses, against the hook and the pin as they are, and adapt
  where a line has moved: `reads._hidden`, `reads._Part`, `held()`, `inside()`, `tree_roots`, `WRITE_TOOLS`,
  `bash_writes_of`, `HOME`, `_paths_ok`, `load_yaml_unique`.

## C. The guard4_check cases
**Script changes.**
- After line 37, add:
  ```python
  BLOCK = yaml.safe_load(open(PROJECT + "/governance/project/path-map.yaml")).get("sets_root_hidden") or {}
  SR = os.path.realpath(os.path.expanduser(BLOCK.get("root", "~/gov-os-eval")))
  PLANTED = os.environ.get("SETS_PLANTED") == "1"
  NX = "zz-guard4-none.yaml"
  E = SR + "/fixtures/evaluation"
  ```
- Allow an optional 6th element per case: `{"cwd": …, "project": …}`.
- R cases run only when `PLANTED` is set.
- `GUARD4_ONLY=sets` runs only these cases. Use it for R2, which runs with `HOME` substituted and `GOV_PIN_PY` set.

**Notation.**
- **L** cases are safe on the live tree: they name paths that do not exist, or the root itself, and make the guard walk
  nothing.
- **R** cases run against the planted root only.
- **M** means each of: engineer, research, orchestrator (the CTO, `DAEO-sdxk`), `orchestrator@DAEO-0uhh` (a lead),
  product-spec, independent-test-designer, independent-auditor, the CTO's engineer subagent and the CTO's
  general-purpose subagent.
- **U** means each of: no `GOV_ROLE`, ticket-lead and independent-reviewer.
- **e/r/o** means engineer, research and orchestrator.

| # | Role | Form | Want |
|---|---|---|---|
| S1 | M | Read `E/memory-retrieval/hidden/NX` (L) | deny |
| S2 | M | Read `E/memory-verdict/hidden/NX` (L) | deny |
| S3 | M | Read `E/memory-verdict-2/hidden/NX` (L) | deny |
| S4 | M | Read `E/memory-verdict-2/retired/NX` (L) | deny |
| S5 | M | Read `E/memory-verdict/NX` (L) | deny |
| S6 | M | Read `SR/transcripts/NX` (L) | deny |
| S7 | engineer, orchestrator | Read `E/memory-verdict-2/XCHECK.md` (R) | deny |
| S8 | U | Read `E/memory-verdict-2/hidden/NX` (L) | allow |
| S9 | M | Read `E/memory-retrieval/visible/NX`; Read `SR/runs/NX` (L) | allow |
| S10 | orchestrator | Read `SR/governance/project/path-map.yaml` (R) | allow |
| G1 | e/r/o | Grep `x`, path `E/memory-verdict-2/hidden/NXdir` (L) | deny |
| G2 | e/r/o | Grep path `SR` (R) | deny |
| G3 | orchestrator | Grep path `$HOME` (R2) | deny |
| G4 | e/r/o | Grep path `E/memory-retrieval/visible` (R) | allow |
| G5 | e/r/o | Grep path the repository root (L) | allow |
| G6 | e/r/o | Glob path `E/memory-verdict-2/hidden/NXdir`, pattern `*` (L) | deny |
| G7 | e/r/o | Glob path `SR`, pattern `fixtures/evaluation/memory-verdict-2/hidden/*.yaml` (L) | deny |
| G8 | e/r/o | Glob path `SR`, pattern `**/*.yaml` (L) | allow (by design: names only, `reads.py:868-869`) |
| B1 | e/r/o | `cat E/memory-retrieval/hidden/NX` (L) | deny |
| B2 | e/r/o | `cat ~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/NX` (L; R2) | deny |
| B3 | e/r/o | `cat "$HOME/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden/NX"` (L; R2) | deny |
| B4 | e/r/o | `cd SR && cat fixtures/evaluation/memory-verdict-2/hidden/NX` (L) | deny |
| B5 | e/r/o | `head -5 E/memory-verdict-2/retired/NX` (L) | deny |
| B6 | e/r/o | `ls E/memory-verdict-2/hidden/NXdir` (L) | deny |
| B7 | e/r/o | `ls E/memory-verdict-2/hidden` (R) | deny |
| B8 | e/r/o | `ls SR`; `ls E/memory-retrieval/visible` (R) | allow |
| B9 | e/r/o | `grep -rn x SR` (R) | deny |
| B10 | e/r/o | `grep -rn x E/memory-retrieval/visible` (R) | allow |
| B11 | e/r/o | `find SR -name '*.yaml' -exec cat {} +` (R) | deny |
| B12 | e/r/o | `sed -n 1,5p E/memory-verdict-2/XCHECK.md` (R) | deny |
| B13 | e/r/o | `python3 -c "print(open('E/memory-verdict/hidden/p01.yaml').read())"`, planted file (R) | deny |
| B14 | e/r/o | the same with `NX` (L) | allow (known limit: code is checked only for paths that exist, `reads.py:830-837`) |
| B15 | U | `cat E/memory-verdict-2/hidden/NX` (L) | allow |
| M1 | orchestrator, lead | `python3 -m gov.retrieval.measure memory-verdict-2 --sets-root ~/gov-os-eval --part hidden` (L; R2) | allow |
| M2 | orchestrator | `env -u GOV_TICKET GOV_ROLE=orchestrator TMPDIR=/tmp/gov-guard4-t PYTHONPATH=/tmp/gov-guard4-clone/src python3 -m gov.retrieval.measure memory-verdict --root /tmp/gov-guard4-clone --sets-root "$HOME/gov-os-eval" --part hidden --out /tmp/gov-guard4-m --gov /tmp/gov-guard4-gov > /tmp/gov-guard4-m.txt 2> /tmp/gov-guard4-m.err` (L) | allow |
| M3 | orchestrator | `python3 -m gov.retrieval.measure memory-verdict --sets-root=SR --part hidden` (L) | allow |
| M4 | orchestrator | `cd SR && python3 -m gov.retrieval.measure memory-retrieval --root /tmp/gov-guard4-clone --sets-root . --part all` (L) | allow |
| M5 | orchestrator | `bash .gov-runtime/scratch/orchestrator/drafts/score-once/so_measure.sh p n r60 '{}' /tmp/gov-guard4-c` (L) | allow |
| M6 | orchestrator | `python3 -m gov.retrieval.measure memory-verdict-2 --sets-root ~/gov-os-eval --part hidden --out "$(mktemp -d)"` (R) | allow (the override; deny without it) |
| M7 | orchestrator | `python3 -m gov.retrieval.measure memory-verdict --sets-root ~/gov-os-eval --part hidden --gov "$(command -v gov)"` (R) | allow (the override) |
| X1 | engineer, orchestrator | `git diff --name-only w2/integrate \| xargs grep -n TODO` (R) | allow (the override; deny without it) |
| X2 | engineer, orchestrator | `cat $(git diff --name-only HEAD~1)` (R) | allow (the override) |
| X3 | engineer, orchestrator | `ls E/memory-verdict-2/hidden \| xargs cat` (R) | deny |
| X4 | engineer, orchestrator | `cat $(find SR -name '*.yaml')` (R) | deny |
| X5 | engineer, orchestrator | `find ~ -name 'p01.yaml' \| xargs cat` (R2) | deny |
| X6 | engineer, orchestrator | `cd SR && git diff --name-only \| xargs cat` (R) | deny (the listing starts in the sets root) |
| X7 | engineer, orchestrator | `xargs -a SR/runs/list cat` (R) | deny (names read from a file) |
| X8 | engineer, orchestrator | `while read f; do cat "$f"; done < /tmp/gov-guard4-list` (R) | deny |
| W1 | M | Write `E/memory-verdict-2/hidden/NX` (L) | deny |
| W2 | engineer | Bash `echo x > E/memory-retrieval/hidden/NX` (L) | deny |
| W3 | orchestrator | Bash `cp /tmp/gov-guard4-a E/memory-verdict/hidden/NX` (L) | deny |
| W4 | orchestrator | Write `<repo>/fixtures/evaluation/memory-verdict-2/hidden/NX` (L) | deny |
| W5 | orchestrator | Write `SR/runs/zz-guard4/.n` (L) | allow |
| W6 | orchestrator | Bash `mkdir -p SR/runs/zz-guard4 && : > SR/runs/zz-guard4/.n` (L) | allow |
| W7 | orchestrator | Edit `SR/governance/project/path-map.yaml` (L) | allow |
| W8 | U | Write `E/memory-verdict-2/hidden/NX` (L) | allow |
| W9 | orchestrator | Bash `mkdir -p $D/t` (L) | allow (target not resolved) |
| T1 | orchestrator | Read `<repo>/fixtures/evaluation/memory-retrieval/hidden/NX` (L) | deny (new; allowed today) |
| T2 | orchestrator | Read `/home/usain/gov-os-worktrees/W2-13/fixtures/evaluation/memory-verdict-2/hidden/NX` (L) | deny |
| T3 | engineer, with project and cwd an old-map worktree, candidate hook in direct mode | Read `E/memory-verdict-2/hidden/NX` (L; in the rehearsal, a clone worktree on an old-map branch) | deny |
| T4 | — | the 70 existing cases | unchanged, PASS |

## D. The rehearsal
- **Clone.** Make a `--no-hardlinks` clone at `~/gov-os-runs/SETS-rehearsal/Dynamic-Agentic-Engineering-OS` and run
  from a fresh `env -i` shell, as ACT-G14 did (`ACT-G14.md:341-363`).
- **Planted sets root.** Put it at `~/gov-os-runs/SETS-rehearsal/home/gov-os-eval`, outside the clone's folder. Fill the
  three hidden folders, `retired/`, `XCHECK.md`, `transcripts/`, `visible/` and `runs/` with dummy files, and add a
  stub path map.
- **R1:** the block's `root` is the planted absolute path. **R2:** `HOME=~/gov-os-runs/SETS-rehearsal/home`, with
  `GOV_PIN_PY` and `GUARD4_ONLY=sets`.
- **Existing tests:** `test_guard_fix_4.py` (467) and `drafts/g14/test_g14.py` (146), run against the candidate hook.
- **Replay** recent events with every `gov-os-eval` path rewritten to the planted root.
- **Measure check:** `_measured(entry, planted_root)` with `GOV_ROLE=orchestrator` must be False.
- **Writer-session check:** a headless `claude -p` session in a scratch writer folder, with the clone as an additional
  directory. Its Read of a planted hidden file must be allowed.
- **Safety:** never point the hook at the real `~/gov-os-eval`. After the ACT is applied, only the L cases run on the
  live tree.
