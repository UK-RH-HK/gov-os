"""KPI 4 (DEC-853, DEC-290, DEC-298, DEC-347; DEC-911 items 1 and 5): the matches are held in memory only, and every
file is still scanned with every rule set.

One project holds, in its runtime folder and its indexable folder, clean files and a store (each with a marker word),
commit hashes of its repository after the rule's keywords (with a marker word), and real findings. A ``gitleaks``
first on ``PATH`` hands every call to the real gitleaks and logs its arguments, its rule set and the marker words it
was given (never content). The check runs twice, the filter once:

- no gitleaks call is given a report path that is a file (only standard output or error, or a descriptor);
- after each run, the temp folder the check is given holds no file, and the project no new or changed file but the
  clean-result record;
- standard output and error hold no match (the hashes and tokens, in any case) and neither of the rule's keywords
  (the check's output is what a close's logs under ``.gov-runtime/`` hold, DEC-911 item 1);
- the clean-result record (DEC-853) holds the digest of no file or store with a finding, and no match, after either
  run; a finding is found again on the second run; a store whose hash cannot be verified (no git) is not recorded;
- every clean or exempt file is given to gitleaks with both rule sets (the project's file with gitleaks' defaults,
  and the project's rules alone, DEC-347); ``.gov-runtime/scratch/`` is still scanned (DEC-911 item 5);
- the branch changes neither gitleaks file (no allowlist is added, DEC-298).

Guards, green today, except the four exempt-file cases of "both rule sets": today the exempt hash is a finding of the
first rule set, after which today's check and filter do not run the second (README).
"""

from __future__ import annotations

import os
import re
import subprocess

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

V, P = support.VENDOR, support.PREFIX


def _mark(number):
    return f"w271mark{number:04d}"


class Scene:
    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.repo = support.make_repo(sandbox, "quiet-project", label="quiet")
        root, head = self.repo.root, self.repo.head
        token = P + support.hex_of("quiet-token")
        not_a_commit = support.hex_of("quiet-not-a-commit")
        other = support.token_digit("quiet-other-rule")
        self.secrets = [head, token, token[len(P):], not_a_commit, other]
        token_line = f"the deploy token is {token} for now\n"

        # {rel: (marker or None, text, kind)}; kind: clean, exempt or finding. A text value goes in a store.
        self.check_files = {
            ".gov-runtime/top.log": (1, "a plain log line\n", "clean"),
            ".gov-runtime/scratch/lead.log": (2, "a lead's log line\n", "clean"),
            ".gov-runtime/scratch/a/b/c/deep.log": (3, "a deep log line\n", "clean"),
            ".gov-runtime/stores/plain.db": (4, "a plain value", "clean"),
            ".gov-runtime/scratch/exempt.log": (5, support.vendor_line(V, head), "exempt"),
            ".gov-runtime/stores/exempt.db": (6, support.vendor_line(P, head), "exempt"),
            ".gov-runtime/scratch/token.log": (None, token_line, "finding"),
            ".gov-runtime/scratch/not-a-commit.log": (None, support.vendor_line(V, not_a_commit), "finding"),
            ".gov-runtime/stores/token.db": (None, token_line, "finding"),
            ".gov-runtime/stores/exempt-and-other.db":
                (None, support.vendor_line(V, head) + f"the key is {other} here\n", "finding"),
        }
        self.filter_files = {
            "docs/top.md": (11, "# A page\n", "clean"),
            "docs/deep/x/y.md": (12, "# A deep page\n", "clean"),
            "docs/plain.db": (13, "a plain value", "clean"),
            "docs/exempt.md": (14, support.vendor_line(V, head), "exempt"),
            "docs/exempt.db": (15, support.vendor_line(P, head), "exempt"),
            "docs/token.md": (None, token_line, "finding"),
            "docs/not-a-commit.md": (None, support.vendor_line(V, not_a_commit), "finding"),
            "docs/token.db": (None, token_line, "finding"),
            "docs/exempt-and-other.db": (None, support.vendor_line(V, head) + f"the key is {other} here\n", "finding"),
        }
        for rel, (marker, text, _) in {**self.check_files, **self.filter_files}.items():
            body = (f"{_mark(marker)} " if marker else "") + text
            if rel.endswith(".db"):
                support.sqlite_store(root / rel, [body])
            else:
                support.write(root / rel, body)

        folder, self.log = support.logging_gitleaks(sandbox)
        env = support.base_environment(sandbox)
        self.env = support.base_environment(sandbox, path=f"{folder}{os.pathsep}{env['PATH']}")
        self.before = self._digests()
        self.runs, self.calls, self.tmp_after, self.changed_after, self.record_after = {}, {}, {}, {}, {}
        for name in ("check-1", "check-2", "filter"):
            seen = len(support.read_log(self.log))
            if name == "filter":
                self.runs[name] = support.run_filter(sandbox, root, sorted(self.filter_files), env=self.env)
            else:
                self.runs[name] = support.run_check(sandbox, root, env=self.env)
            self.calls[name] = support.read_log(self.log)[seen:]
            self.tmp_after[name] = sorted(support.files_under(sandbox.tmpdir, skip=()))
            after = self._digests()
            self.changed_after[name] = sorted(rel for rel in set(after) | set(self.before)
                                              if after.get(rel) != self.before.get(rel) and rel != support.RECORD_REL)
            record = root / support.RECORD_REL
            self.record_after[name] = record.read_text(encoding="utf-8", errors="replace") if record.exists() else ""

    def _digests(self):
        root = self.repo.root
        return {rel: support.sha256_file(root / rel) for rel in support.files_under(root)}

    def rels(self, files, kinds):
        return [rel for rel, (_, _, kind) in files.items() if kind in kinds]


@pytest.fixture(scope="module")
def scene(module_sandbox):
    return Scene(module_sandbox)


RUNS = ["check-1", "check-2", "filter"]


def test_premise_every_run_went_through_the_logging_gitleaks_and_ended(scene):
    counts = {name: len(scene.calls[name]) for name in RUNS}
    ended = {name: scene.runs[name].ended for name in RUNS}
    assert all(counts.values()) and all(ended.values()), f"gitleaks calls logged: {counts}; ended: {ended}"


def test_premise_the_check_found_the_findings_and_the_filter_left_them_out(scene):
    check = scene.runs["check-1"]
    named = [check.names(rel) for rel in scene.rels(scene.check_files, ("finding",))]
    passed = [scene.runs["filter"].passes(rel) for rel in scene.rels(scene.filter_files, ("finding",))]
    assert all(named) and not any(passed), f"findings named by the check: {named}; let through by the filter: {passed}"


# ---- no report file ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("run", RUNS)
def test_no_gitleaks_call_is_given_a_report_file(scene, run):
    files = sorted({path for call in scene.calls[run] for path in support.report_paths(call)
                    if not support.in_memory(path)})
    assert not files, f"{run}: gitleaks was given a report file to write: {files}"


@pytest.mark.parametrize("run", RUNS)
def test_the_temp_folder_given_to_the_check_holds_no_file_after_the_run(scene, run):
    left = scene.tmp_after[run]
    assert not left, f"{run}: the temp folder the check is given holds files after the run: {left}"


@pytest.mark.parametrize("run", RUNS)
def test_the_project_holds_no_new_or_changed_file_but_the_clean_record(scene, run):
    changed = scene.changed_after[run]
    assert not changed, f"{run}: files written or changed in the project besides the clean record: {changed}"


# ---- nothing printed -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("stream", ["stdout", "stderr"])
@pytest.mark.parametrize("run", RUNS)
def test_no_match_and_no_keyword_is_printed(scene, run, stream):
    text = getattr(scene.runs[run], stream)
    leaked = support.leaks(text, scene.secrets)
    keyword = support.holds_keyword(text)
    assert not leaked, f"{run}: a match (a hash or a token of the case) is printed on standard {stream[3:]}"
    assert not keyword, f"{run}: one of row W2-L423's rule's keywords is printed on standard {stream[3:]}"


# ---- the clean-result record ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("run", ["check-1", "check-2"])
def test_the_clean_record_holds_no_file_or_store_with_a_finding_and_no_match(scene, run):
    text = scene.record_after[run]
    recorded = set(re.findall(r"[0-9a-f]{64}", text))
    findings = {rel: scene.before[rel] for rel in scene.rels(scene.check_files, ("finding",))}
    held = sorted(rel for rel, digest in findings.items() if digest in recorded)
    assert not held, f"after {run} the clean-result record holds the digest of files with a finding: {held}"
    leaked, keyword = support.leaks(text, scene.secrets), support.holds_keyword(text)
    assert not leaked and not keyword, f"after {run} the record holds a match: {leaked}, a keyword: {keyword}"


def test_a_finding_is_found_again_on_the_next_run(scene):
    second = scene.runs["check-2"]
    missed = [rel for rel in scene.rels(scene.check_files, ("finding",)) if not second.names(rel)]
    assert not missed and second.returncode == 1, (f"the second run does not find again: {missed}\n"
                                                   f"{second.describe()}")


def test_a_commit_hash_that_cannot_be_verified_is_not_recorded_clean(sandbox):
    repo = support.make_repo(sandbox, "unverified-project", label="unverified")
    rel = ".gov-runtime/stores/unverified.db"
    support.sqlite_store(repo.root / rel, [support.vendor_line(V, repo.head), support.vendor_line(P, repo.head)])
    digest = support.sha256_file(repo.root / rel)
    env = support.base_environment(sandbox, path=str(support.bin_without_git(sandbox)))
    run = support.run_check(sandbox, repo.root, env=env)
    assert run.ended, f"the check did not end\n{run.describe()}"
    record = repo.root / support.RECORD_REL
    recorded = record.exists() and digest in record.read_text(encoding="utf-8", errors="replace")
    assert not recorded, "with no git on PATH, a store whose commit hash cannot be verified is recorded clean"
    assert support.check_fails_closed(run, rel, [rel]), f"the unverified store passes as clean\n{run.describe()}"


# ---- every file still scanned with every rule set ------------------------------------------------------------------

def _sets_seen(calls, marker):
    return {call["rules"] for call in calls if marker in call.get("seen", [])}


CHECK_MARKED = [".gov-runtime/top.log", ".gov-runtime/scratch/lead.log", ".gov-runtime/scratch/a/b/c/deep.log",
                ".gov-runtime/stores/plain.db", ".gov-runtime/scratch/exempt.log", ".gov-runtime/stores/exempt.db"]
FILTER_MARKED = ["docs/top.md", "docs/deep/x/y.md", "docs/plain.db", "docs/exempt.md", "docs/exempt.db"]


@pytest.mark.parametrize("rel", CHECK_MARKED)
def test_the_check_gives_every_clean_or_exempt_file_to_both_rule_sets(scene, rel):
    marker, _, kind = scene.check_files[rel]
    seen = _sets_seen(scene.calls["check-1"], _mark(marker))
    assert {"extended", "alone"} <= seen, (f"the check gave {rel} ({kind}) to gitleaks with the rule sets "
                                           f"{sorted(seen)}, not both")


@pytest.mark.parametrize("rel", FILTER_MARKED)
def test_the_filter_gives_every_clean_or_exempt_file_to_both_rule_sets(scene, rel):
    marker, _, kind = scene.filter_files[rel]
    seen = _sets_seen(scene.calls["filter"], _mark(marker))
    assert {"extended", "alone"} <= seen, (f"the filter gave {rel} ({kind}) to gitleaks with the rule sets "
                                           f"{sorted(seen)}, not both")


# ---- no allowlist added ----------------------------------------------------------------------------------------------

def _base():
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), "merge-base", "HEAD", "w2/integrate"],
                          capture_output=True, text=True, timeout=60)
    return done.stdout.strip() if done.returncode == 0 else None


GITLEAKS_FILES = (".gitleaks.toml", "template/.gitleaks.toml")


def test_the_branch_changes_neither_gitleaks_file():
    base = _base()
    if base is None:
        pytest.skip("w2/integrate is not in this repository: no base to compare the gitleaks files with")
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), "diff", "--name-only", base, "--", *GITLEAKS_FILES],
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, "git diff did not run"
    assert not done.stdout.strip(), f"the branch changes a gitleaks file: {done.stdout.split()}"


@pytest.mark.parametrize("rel", GITLEAKS_FILES)
def test_no_gitleaks_file_shelters_a_match_by_content(rel):
    """The template holds no allowlist (DEC-288); the root file holds path allowlists only (DEC-290). Neither holds an
    allowlist by content (regexes, stopwords, commits), a rule's own allowlist, a disabled rule, or row W2-L423's
    rule's id or keywords."""
    import tomllib
    text = (support.REPO_ROOT / rel).read_text(encoding="utf-8")
    config = tomllib.loads(text)
    tables = [config.get("allowlist") or {}, *(config.get("allowlists") or [])]
    by_content = sorted({key for table in tables for key in table if key not in ("description", "paths")})
    per_rule = [rule.get("id") for rule in config.get("rules", []) if "allowlist" in rule or "allowlists" in rule]
    disabled = (config.get("extend") or {}).get("disabledRules") or []
    template_lists = rel.startswith("template/") and any(tables)
    facts = {"an allowlist by content": by_content, "a rule's own allowlist": per_rule,
             "a disabled rule": disabled, "an allowlist in the template": template_lists,
             "row W2-L423's rule's id or a keyword": support.holds_keyword(text)}
    assert not any(facts.values()), f"{rel} holds {[name for name, value in facts.items() if value]}"
