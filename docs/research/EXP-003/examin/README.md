---
id: EXP-003-examin
type: research
status: ACTIVE
state_class: EVIDENCE
title: EXAMIN profile on a clone of the owner's copy at a7cf346 (EXP-003's EXAMIN leg, W2-26)
---

# EXP-003-examin — EXAMIN profile on a clone of the owner's copy at a7cf346

- **Ticket:** `DAEO-2ds6` (W2-26, STANDARD, research). **Sources:** DEC-728, DEC-078, DEC-727; DEC-719, DEC-723, DEC-725, DEC-673, DEC-732.
- **Run:** 2026-10-16, 17:27 to about 17:55 UTC, by one headless research session, on this machine. Raw outputs are in [`raw/`](raw/).

## Question

What does EXAMIN's committed tree look like for adoption, measured on a clone of the owner's copy? This covers its size, its languages, its test runner(s) and their commands, and its suite's wall time. It also covers each index's time and peak RSS as this repository's `gov` builds them, against DEC-078's envelope, and whether a path with a space breaks any command (W2-I041). Two consequences are reported, not decided: W2-19 joins W2-27 if EXAMIN's tests are not pytest (DEC-727), and W2-45 joins W2-27 if something exceeds its budget at EXAMIN's size.

## Method

1. **The clone (DEC-723, DEC-728).** The owner's copy was read by one command only. No other command listed, read or wrote the workbench, and none touched EXAMIN's real repository:
   `/usr/bin/time -v git clone --no-hardlinks /home/usain/gov-os-workbench/examin /tmp/gov-os-W2-26/examin` (exit 0, 0.12 s). Its head is `a7cf346` (`a7cf346c28d7ba7b9edf8a18e1bb6e20ab1b19ca`).
2. **The uncommitted entries.** The owner's copy carries 9 uncommitted entries (6 modified, 3 untracked), and a clone does not see them. This profile measures the committed tree at `a7cf346`. The owner is to give the entries' paths for Q-16 (W2-29). By the orchestrator's decision, which is stricter than the ticket's O-1 section, no `git status` or other command ran in the copy, so this record does not name them.
3. **Size and languages**, all with `git -C <clone> ...`: `ls-files | wc -l`, `rev-list --count HEAD`, tracked bytes (`stat` over `ls-files`, and blob sizes from `ls-tree -l`), and lines from `git diff --numstat <empty tree> HEAD`. That diff uses git's own binary detection (a binary shows `-`), so binaries count as files and bytes but not as lines. The extension table is grouped from the same numstat. Commands are in [`raw/size.txt`](raw/size.txt) and [`raw/languages.tsv`](raw/languages.tsv).
4. **Test runners.** Test configuration and documentation were found by name over `git ls-files` and read; only their test command lines are quoted ([`raw/test-runners.txt`](raw/test-runners.txt)).
5. **Suite wall time.** A suite was run only if it needed no install, network service, container, database or credential. The **governance suite** qualified and ran on each clone with EXAMIN's runner's own pytest line, `/usr/bin/time -v` and `timeout 1800`, in the background. It used `/usr/bin/python3` 3.12.3, and `PYTHONPATH` was removed for it (DEC-732 does not apply to EXAMIN's suite). The **product suite** did not qualify and was not started ([`raw/product-suite-needs.txt`](raw/product-suite-needs.txt)).
6. **Indexing (DEC-732, DEC-719).**
   - The code under test is this worktree's `src/`. Every `gov` command and direct call carried the absolute prefix `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src`.
   - The primary run was the full rebuild (never `--no-embeddings`), `--root` on the clone, under `/usr/bin/time -v`.
   - A sampler wrote the pid, ppid, RSS and command of every `codebase-memory-mcp`, `gitleaks` and gov process every 2 s, so that the tool's daemon and worker would be counted if they ran.
   - Then gov's three index functions were timed as **direct calls**, unmodified and one at a time.
   - No path map, `.gitleaks.toml` or other governance file was written into either clone, and neither was adopted.
7. **The path with a space (W2-I041).** A second clone was made **from the first clone**: `git clone --no-hardlinks /tmp/gov-os-W2-26/examin "/tmp/gov-os-W2-26/EXAMIN APP"`. Every measure above ran there again, with the path quoted, and its outputs were compared with the first clone's.

Every long run went in the background with an exit-code file under `/tmp/gov-os-W2-26/runs/`, one run at a time.

## Sources

- `.tickets/DAEO-2ds6.md` (KPIs, allowed path, Consequences, the O-1 section); `docs/plan/WAVE_2_WBS.md` §2, cards W2-26, W2-27 and W2-45; the W2-I041 rows of `docs/plan/WAVE_2_TRIAGE.md` and `docs/plan/WAVE_2_LIST.md`; the W2-H018 row of `docs/plan/WAVE_2_LIST.md`.
- `docs/DECISION_REGISTER.md`: DEC-078 (the envelope: ≈ 80k nodes / 270k edges at ≈ 2.2 GB peak, and the daemon-and-worker correction), DEC-595 (the runner's 60 s default check limit), DEC-673, DEC-719, DEC-723, DEC-725, DEC-727, DEC-728.
- This repository's code, read-only:
  - `src/gov/rebuild/command.py` (the lexical index only with a path map; semantic always asked; codeintel always tried).
  - `src/gov/retrieval/lexical.py` and `src/gov/retrieval/semantic.py` (the semantic step runs the lexical refresh first).
  - `src/gov/codeintel/__init__.py` (daemon folder `/tmp/gov-cbm-<uid>/<hash>`).
  - `src/gov/secrets/__init__.py` (`indexable()` reads `.gitleaks.toml`, then the path map's namespaces).
  - `src/gov/config/loader.py`, `src/gov/check/runner.py` (`TIMEOUT_S = 60`).

## Environment

| Item | Value |
|---|---|
| Machine | `Linux Usain 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64`; `nproc` 20; `free -g`: 23 GiB memory (19 free), 8 GiB swap |
| git | 2.43.0 |
| Python | 3.12.3 (`/usr/bin/python3`) |
| Code-intelligence tool | `codebase-memory-mcp 0.11.0` |
| gitleaks | 8.30.1 |
| Ollama | endpoint `127.0.0.1:11434` answers `{"version":"0.35.0"}` with `qwen3-embedding:0.6b` (digest `ac6da0dfba84…`); no `ollama` binary on this PATH; nothing was started |
| This worktree | branch `w2/W2-26`, head `af445b6f3562249c7a766af2f5333ab9f111c383` |
| The clone | `a7cf346c28d7ba7b9edf8a18e1bb6e20ab1b19ca`, both clones |
| DEC-732 | `PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -c "import gov; print(gov.__file__)"` → `/home/usain/gov-os-worktrees/W2-26/src/gov/__init__.py` |

## Commands, as run

```
git clone --no-hardlinks /home/usain/gov-os-workbench/examin /tmp/gov-os-W2-26/examin          # under /usr/bin/time -v
git clone --no-hardlinks /tmp/gov-os-W2-26/examin "/tmp/gov-os-W2-26/EXAMIN APP"              # under /usr/bin/time -v
git -C <clone> ls-files | wc -l ; git -C <clone> rev-list --count HEAD
git -C <clone> diff --numstat 4b825dc642cb6eb9a060e54bf8d69288fbee4904 HEAD
cd <clone> && env -u PYTHONPATH timeout 1800 /usr/bin/time -v python3 -m pytest governance/scripts/tests -q --no-header -p no:cacheprovider -p no:randomly -n 8 --dist=loadgroup
PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -m gov.cli.main rebuild --root /tmp/gov-os-W2-26/examin --json
PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -m gov.cli.main rebuild --root "/tmp/gov-os-W2-26/EXAMIN APP" --json
PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -c "from pathlib import Path; from gov.retrieval.lexical import refresh; print(len(refresh(Path('<clone>'))['indexed']))"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -c "from pathlib import Path; from gov.retrieval.semantic import refresh; print(refresh(Path('<clone>')))"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src /usr/bin/time -v python3 -c "from pathlib import Path; from gov.codeintel import index; index(Path('<clone>'))"
```

`gov` ran from this worktree's root (`cd /home/usain/gov-os-worktrees/W2-26`). Each exact line, with its output, is in `raw/`.

## Measurements

### Size and languages (committed tree at `a7cf346`; identical on both clones)

| Measure | Value |
|---|---|
| Tracked files | **1,442** (no submodule, no symbolic link, no LFS file) |
| Lines of tracked text files | **382,795** in 1,437 text files; the 5 binary files (git's detection: 1 `.jpeg`, 1 `.png`, 1 `.pptx` and 2 `.md`) are excluded. For comparison, `wc -l` over every tracked file gives 384,108 |
| Tracked bytes | **24,667,921** in the working tree (24,667,813 as blob bytes at HEAD; 108 bytes apart, which fits end-of-line conversion under `.gitattributes`) |
| Commits | **392** |
| Clone on disk | 41 MB after the clone (`.git` 14 MB); 47 MB at the end. The owner's copy is 3.3 GB (O-1), so almost all of it is outside the committed tree |

| Extension | Files | Lines |
|---|---:|---:|
| `.py` | 542 | 209,570 |
| `.md` | 848 | 154,605 |
| `.json` | 16 | 10,945 |
| `.sql` | 1 | 2,726 |
| `.html` | 3 | 2,360 |
| rest (`.txt` 5, `.jsonl` 15, no extension 4, `.css`, `.js`, `.bat`, `.toml`, `.example`, `.jpeg`, `.png`, `.pptx`: 1 each) | 32 | 2,589 |
| **Total** | **1,442** | **382,795** |

EXAMIN is a Python project: 542 Python files hold 55 % of the lines, and Markdown holds 40 %.

### Test runners and the suite's wall time

| Suite | Runner and command (where found) | Run? | Wall time | Result |
|---|---|---|---|---|
| Product, `product/tests/` (180 test files) | **pytest**: `.venv/Scripts/python.exe -m pytest product/tests -q -p no:randomly -m "not live"` (root `CLAUDE.md`); `[tool.pytest.ini_options]` in `product/pyproject.toml` (testpaths, `addopts = "-m 'not live'"`, markers `live` and `slow`); also `product/app/README.md` | **No** | — | It needs 10 absent packages (respx, anthropic, python-docx, pypdf, python-multipart, pgserver, psycopg, pytesseract, pdf2image, fastembed) and a database (pgserver's bundled Postgres; the `slow` marker boots one) |
| Governance, `governance/scripts/tests/` (101 files) | **pytest + pytest-xdist**: `<python> -m pytest governance/scripts/tests -q --no-header -p no:cacheprovider -p no:randomly -n <WORKERS> --dist=loadgroup` (`governance/scripts/run_gov_suite.py`, WORKERS default 8) | **Yes**, both clones | **1:13.3** (pytest 67.46 s); spaced clone 1:15.7 (69.38 s); peak RSS of the controller 61 MB | **828 passed, 15 failed, 165 errors**, exit 1, the same on both clones |

The suite's 180 failures and errors are all `AssertionError`; there is no `ModuleNotFoundError` or `ImportError`, so nothing failed on a missing package. Most of them (169) come from fixtures that run EXAMIN's `governance/framework/kit/bootstrap.py` into a temporary tree, and that tree's own `check.py` exits 1. One test runs `graph.py check` on the repository and gets "1 hard errors". Their cause was not diagnosed: EXAMIN's documented interpreter is a Windows virtual environment, and the committed tree lacks the copy's 9 uncommitted entries. Either may matter (see Uncertainty).

### Indexing against DEC-078's envelope

| Index | How built | Built? | Time | Peak RSS | What stopped it (gov's own message) | DEC-078 envelope (≈ 80k nodes / 270k edges, ≈ 2.2 GB) |
|---|---|---|---|---|---|---|
| Record store (not an index; for reference) | CLI `gov rebuild` | yes: 392 commits, 5,712 commit paths, 0 records; 18 Markdown files reported as invalid front matter | within the 0.51 s run | within 58.9 MB | — | — |
| Lexical | CLI `gov rebuild` | **no** | 0.0 s (`timing.lexical_s`) | — | `no path map: nothing is classified as indexable` | **not measurable** |
| Lexical | direct call `gov.retrieval.lexical.refresh` | **no** | 0.14 s, exit 1 | 33.6 MB | `RuntimeError: .gitleaks.toml cannot be read: [Errno 2] No such file or directory: '/tmp/gov-os-W2-26/examin/.gitleaks.toml'` | — |
| Semantic | CLI `gov rebuild` (full, with embeddings) | **no** | within the 0.51 s run | within 58.9 MB | `.gitleaks.toml cannot be read: [Errno 2] No such file or directory: '/tmp/gov-os-W2-26/examin/.gitleaks.toml'` (raised in its lexical refresh; Ollama was never asked) | **not measurable** |
| Semantic | direct call `gov.retrieval.semantic.refresh` | **no** | 0.16 s, exit 1 | 36.0 MB | the same `RuntimeError` | — |
| Code graph | CLI `gov rebuild` | **no** | within the 0.51 s run | CLI 58.9 MB (whole `gov rebuild`); daemon and worker: **none ran** | `.gitleaks.toml cannot be read: [Errno 2] No such file or directory: '/tmp/gov-os-W2-26/examin/.gitleaks.toml'` | **not measurable**: no nodes, no edges |
| Code graph | direct call `gov.codeintel.index` | **no** | 0.06 s, exit 1 | 32.9 MB | the same `RuntimeError` | — |

The whole `gov rebuild` took **0.51 s** wall, with a 58.9 MB peak RSS (`/usr/bin/time -v`). It exited **0** with `"ok": true`, though none of the three indexes was recreated. The RSS sampler saw only the gov CLI process (8.7 MB at its one sample), with no `codebase-memory-mcp` or `gitleaks` process. gov made no daemon folder for these clones (`/tmp/gov-cbm-1000/40258c8d5975c146` and `/tmp/gov-cbm-1000/de3654f2e4ec8811` do not exist), and nothing under `/tmp/gov-cbm-1000/` was deleted. The clone's `.gov-runtime/` holds `store.db` only, 1.1 MB, with empty lexical tables and no vector table.

**The nearest known figure, not measured here:** DEC-078 records `~/EXAMIN APP` (the real repository, on 2026-09-30, by the tool directly) at 1,378 files indexed, 24,665 nodes / 81,356 edges, 6.1 s and 57 MB peak RSS. That is about 31 % of the envelope's nodes and 30 % of its edges. Today's committed tree has 1,442 tracked files, 5 % more than DEC-078's file count.

### The path with a space (W2-I041)

| Command on `"/tmp/gov-os-W2-26/EXAMIN APP"` | Exit | Same as on `/tmp/gov-os-W2-26/examin`? |
|---|---|---|
| `git clone --no-hardlinks /tmp/gov-os-W2-26/examin "/tmp/gov-os-W2-26/EXAMIN APP"` | 0 (0.12 s) | — |
| size and language measures (`ls-files`, `rev-list`, `stat`, `diff --numstat`) | 0 | yes: identical numbers; `cmp` of the two numstat files finds no difference |
| governance suite | 1 (1:15.7) | yes: 828 / 15 / 165, the identical set of failing test ids (`comm` finds none in only one run) |
| `gov rebuild --root "…EXAMIN APP" --json` | 0 (0.50 s, 58.9 MB) | yes: the same three `not_recreated` reasons, the path in the message carrying the space |
| the three direct calls | 1 each | yes: the same `RuntimeError`, the spaced path in its text |

**No command broke on the space.** The space did change one thing: in gov's messages, the path with a space is printed inside quotes, unescaped.

### Sizes of the folders left under `/tmp/gov-os-W2-26/`

`/tmp/gov-os-W2-26/examin` 47 MB · `/tmp/gov-os-W2-26/EXAMIN APP` 47 MB · `/tmp/gov-os-W2-26/runs` 1.1 MB · total 94 MB. The clones stay; they are throwaway (DEC-728).

## Findings

1. **EXAMIN's tests are pytest.** Both suites use it: the product suite through `product/pyproject.toml`, and the governance suite through `run_gov_suite.py`, under pytest-xdist.
2. **On an unadopted clone, `gov rebuild` builds no index, but reports `"ok": true` and exits 0.**
   - The lexical index needs the path map.
   - The semantic index and the code graph go through `gov.secrets.indexable()`, which first needs `.gitleaks.toml`. Neither `.gitleaks.toml` nor `governance/project/path-map.yaml` is tracked in EXAMIN at `a7cf346`.
   - So DEC-078's KPI (each index's time and peak RSS) cannot be met before adoption writes those two files (W2-27's A-steps). A rebuild's "ok" is no evidence that an index exists.
3. **The record store reports 18 Markdown files with invalid YAML front matter.** These are in `.claude/commands/`, the kit's `.claude/` templates and `spec/5-REPORTS/attempts/`, each a "mapping values are not allowed here" error. An adoption will meet them.
4. **The product suite cannot run here without installs and a database.** Its wall time is unknown.
5. **The governance suite runs on this machine's Python, but not green:** 15 failed and 165 errors, all assertions, the same on both clones.
6. **The owner's copy is 3.3 GB, while its committed tree is 24.7 MB in 1,442 files.** Almost all of the copy's size is therefore content a clone does not carry. By inference, not measured, since nothing in the copy was listed, that content is ignored or untracked files: EXAMIN's `CLAUDE.md` names `product/data/` as git-ignored runtime data, and its documents name a `.venv`. The 9 uncommitted entries (Q-16) are part of what the clone lacks.

## The two consequences, as found (decided by neither this record nor its author)

- **Are EXAMIN's tests pytest?** **Yes**, both suites. By DEC-727's rule, W2-19 does **not** join W2-27's dependencies on this evidence.
- **Does anything exceed its budget at EXAMIN's size?**
  - **Indexing:** not measured, so it is unknown against DEC-078's envelope. The nearest figure (DEC-078's own probe of `~/EXAMIN APP`: 24,665 nodes, 81,356 edges, 57 MB) is about 30 % of the envelope, and the tracked tree has grown only 5 % in files since.
  - **The `gov check` budget:** W2-45's card names "the `gov check` budget" without a figure. The figure stated in this repository is the runner's default limit of **60 s per check** (`src/gov/check/runner.py`, `TIMEOUT_S = 60`, DEC-595); W2-H018 sizes the decision checker against a 200-decision, 20k-commit repository. `gov check` was not run, because its help says "running them is not built yet". EXAMIN's history is **392 commits**, under 2 % of W2-H018's 20k, and gov's record store loaded those 392 commits in about 0.5 s.
  - **Measured:** nothing exceeded a budget. On this evidence, W2-45 has no measured reason to join W2-27. The question stays open until an index is built on an adopted copy.

## Raw files and what was dropped

| File | Holds |
|---|---|
| [`raw/environment.txt`](raw/environment.txt) | machine, versions, heads, the DEC-732 line |
| [`raw/clone.txt`](raw/clone.txt) | both clones' time output and the folder sizes |
| [`raw/size.txt`](raw/size.txt) | the size commands and outputs |
| [`raw/languages.tsv`](raw/languages.tsv) | the whole extension table |
| [`raw/test-runners.txt`](raw/test-runners.txt) | runners, commands and the files they were found in |
| [`raw/product-suite-needs.txt`](raw/product-suite-needs.txt) | why the product suite was not run |
| [`raw/governance-suite.txt`](raw/governance-suite.txt) | both suite runs: summaries, time, failures per test file |
| [`raw/gov-rebuild.txt`](raw/gov-rebuild.txt) | both CLI rebuild envelopes and the store's row counts |
| [`raw/direct-calls.txt`](raw/direct-calls.txt) | the six direct calls |
| [`raw/rss-samples.txt`](raw/rss-samples.txt) | every RSS sample, and gov's daemon folders |

**Dropped, and why:**
- **The suite's tracebacks, captured output and assertion texts:** they quote EXAMIN's source lines and the generated trees' check reports, which are file contents.
- **`result.store.invalid`'s 18 entries** in the rebuild envelope: each quotes a fragment of an EXAMIN file's front matter. Only the count and the error kind are kept, and Finding 3 names the three folders.
- **Traceback frame lines** of the direct calls: these are gov's own source, so they carry no secret, but they add nothing.

No secret, key, token, password or connection string was seen in the kept outputs. No EXAMIN file and no content of one is copied here; EXAMIN paths appear only as test configuration files, test files counted per file, and folders named in a finding.

## Uncertainty

- **No index was built, so the indexing KPI is unmet.** Time, RSS, node and edge counts for gov's lexical, semantic and code indexes on EXAMIN remain unknown until a clone has `.gitleaks.toml` and a path map, which is adoption (W2-27). The DEC-078 figure above is the real repository's, a fortnight old, measured by the tool directly, not through gov's pre-index copy and filter.
- **The committed tree is not the owner's working tree:** 9 entries are missing (Q-16). gov's code index lists untracked files too (`ls-files --others --exclude-standard`) and would include the 3 untracked entries on the real repository.
- **The governance suite's failures are not explained.** They may come from this interpreter (Linux `python3` and not EXAMIN's Windows `.venv`), from the missing uncommitted entries, from today's date (EXAMIN's checks carry dated `FATAL since` sunsets), or from EXAMIN's own state at `a7cf346`. The run was on a shared machine with `-n 8`, so its wall time may vary by a few seconds (the two runs differ by 2.4 s).
- **The product suite's wall time is unknown.**
- **The space test covered every command that ran.** The code-intelligence tool itself never started, so a space in its staged-files path (`<root>/.gov-runtime/codeintel/files`) is untested. Its daemon folder is a hash and holds no space. W2-I041's own text (the harness refusing a clone's local exclude file and `git init` inside its git folder) concerns exit-run clones and was not exercised here; nothing in this ticket needed either.
- `/usr/bin/time -v` counts the measured process and its waited-for children. The suite's 61 MB peak is the pytest controller's; its xdist workers are not counted.

## Conclusion

EXAMIN at `a7cf346` is a small Python repository:

- **Size:** 1,442 tracked files, 382,795 lines, 24.7 MB tracked and 392 commits.
- **Tests:** pytest in both suites, so W2-19 does not join W2-27 (DEC-727).
- **Governance suite:** runs here without installs in 1 min 13 s, with 828 passed, 15 failed and 165 errors.
- **Product suite:** needs 10 package installs and a bundled Postgres, so it was not run.

None of gov's three indexes can be built before adoption. `gov rebuild` stops in the pre-index filter for want of `.gitleaks.toml` (semantic, code) and a path map (lexical), yet it reports `"ok": true`. So EXAMIN's indexing against DEC-078's envelope is not measured. The nearest figure, about 30 % of the envelope, and 392 commits against W2-H018's 20k give no measured reason for W2-45 to join W2-27. That stays open until an adopted copy is indexed. A path with a space broke no command that ran.
