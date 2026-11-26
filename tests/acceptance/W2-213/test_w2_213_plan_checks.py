"""SL-7 to SL-10: exactly once, valid, where the standard puts it, coherent."""

from __future__ import annotations

import pytest

import w2_213_support as support

# --- SL-7: exactly once ----------------------------------------------------------------------------------------------

# the items a rule decides alone (rubric section 4), and the class it gives each
RULE_DECIDED = {
    "README.md": "docs", "CLAUDE.md": "governance", "AGENTS.md": "governance", ".gitignore": "config",
    ".gitleaks.toml": "config", "pyproject.toml": "config", ".github/workflows/ci.yml": "config",
    ".claude/settings.json": "config", ".rulesync/rules/main.md": "governance", ".tickets/PLT-1.md": "governance",
    "openspec/specs/billing/spec.md": "spec", support.KIT_COPY: "kit",
    "governance/kernel/skills/retrieval.md": "kit", "governance/framework.lock": "kit", ".copier-answers.yml": "kit",
    support.MAP_REL: "governance", "governance/adoption/A1-inventory.md": "record", "docs/close/PLT-1.md": "record",
    "eval/visible/cases.jsonl": "evaluation", ".env": "secret", "node_modules": "generated", "build": "generated",
    "src/meadow/__pycache__": "generated",
}
JUDGED = ("notes/handbook.md", "experiments/cache-study.md", "reports/audit-2025-03-02.md",
          "fixtures/sample-orders.csv", "misc/oddity.txt", "todo.md", "scratch-notes/a.txt",
          "plans/roadmap-2024.md")


def test_sl7_an_empty_plan_lists_every_item_once_the_rule_decided_ones_with_their_class(clean_repo, work):
    run, _ = support.check_lines(work, clean_repo, [])
    result = support.result_of(run, 1)
    gaps = support.findings(result, "LAYOUT_GAP")
    paths = sorted(f["path"] for f in gaps)
    expected = support.items_of(clean_repo)
    assert paths == expected, (
        f"gaps not listed: {sorted(set(expected) - set(paths))}\nextra: {sorted(set(paths) - set(expected))}\n"
        f"twice: {sorted({p for p in paths if paths.count(p) > 1})}")
    of = {f["path"]: f for f in gaps}
    wrong = {p: of[p].get("rule_class") for p, cls in RULE_DECIDED.items() if of[p].get("rule_class") != cls}
    assert not wrong, f"rule-decided items without their class: {wrong}"
    claimed = {p: of[p]["rule_class"] for p in JUDGED if of[p].get("rule_class")}
    assert not claimed, f"items an agent judges are stated as rule-decided: {claimed}"
    assert all(f.get("line") is None for f in gaps), "a gap states a plan line"


def test_sl7_a_registered_hidden_set_path_is_a_rule_decided_gap_or_stopper(dirty_repo, work):
    run, _ = support.check_lines(work, dirty_repo, support.clean_lines())
    result = support.result_of(run, 1)
    gaps = {f["path"]: f for f in support.findings(result, "LAYOUT_GAP")}
    stopped = {s.get("path") for s in result["stoppers"]}
    for rel in ("eval/hidden/answers.txt", "vault-sets/q1.txt", "eval/hidden/more.txt"):
        assert rel in stopped, f"{rel} is in the tree and is no stopper: {result['stoppers']}"
        assert rel not in gaps or gaps[rel].get("rule_class") == "hidden-set", f"gap of {rel}: {gaps[rel]}"
    assert "id_rsa" in gaps and gaps["id_rsa"].get("rule_class") == "secret", f"the ignored key file: {gaps}"


REMOVALS = {
    "a-tracked-file": ("docs/guide/ops.md", ["docs/guide/ops.md"]),
    "a-folder-line": ("seedpack", ["seedpack/regions.csv", "seedpack/units.csv"]),
    "an-untracked-folder": ("scratch-notes", ["scratch-notes/a.txt", "scratch-notes/b.txt"]),
    "an-untracked-file": ("todo.md", ["todo.md"]),
    "an-ignored-root": ("node_modules", ["node_modules"]),
    "a-submodule": ("external/widgets", ["external/widgets"]),
    "a-declared-line": ("../solar-sketch", ["../solar-sketch"]),
}


@pytest.mark.parametrize("case", sorted(REMOVALS))
def test_sl7_a_removed_line_is_a_gap_naming_each_uncovered_item(clean_repo, work, case):
    removed, uncovered = REMOVALS[case]
    run, _ = support.check_lines(work, clean_repo, support.without(support.clean_lines(), removed))
    result = support.result_of(run, 1)
    got = sorted(f["path"] for f in support.findings(result, "LAYOUT_GAP"))
    assert got == uncovered, f"gaps {got}, expected {uncovered}\n{run.describe()}"


@pytest.mark.parametrize("path", ["docs/guide/ops.md", "seedpack", "node_modules", "external/widgets",
                                  "../solar-sketch", "todo.md"])
def test_sl7_a_doubled_line_is_a_double(clean_repo, work, path):
    lines = support.clean_lines()
    again = {**support.by_path(lines, path), "reason": "a second answer on the same item"}
    run, numbers = support.check_lines(work, clean_repo, lines + [again])
    result = support.result_of(run, 1)
    found = support.findings(result, "LAYOUT_DOUBLE")
    both = {numbers[lines.index(support.by_path(lines, path))], numbers[len(lines)]}
    assert any(f.get("line") in both and path in support.text_of(f) for f in found), (
        f"no LAYOUT_DOUBLE for {path} on line {sorted(both)}: {found}")


@pytest.mark.parametrize("folder,below,cls", [("seedpack", "seedpack/units.csv", "data"),
                                              ("scratch-notes", "scratch-notes/a.txt", "data"),
                                              ("vendor/jsonlib", "vendor/jsonlib/jsonlib.py", "import-use")])
def test_sl7_a_file_line_below_a_folder_line_is_a_double(clean_repo, work, folder, below, cls):
    lines = support.clean_lines()
    parent = support.by_path(lines, folder)
    extra = support.line(below, cls, parent["destination"] + below[len(folder):],
                         "untracked" if parent["kind"] == "untracked" else "file", imp=parent["import"])
    run, _ = support.check_lines(work, clean_repo, lines + [extra])
    result = support.result_of(run, 1)
    support.one_finding(result, "LAYOUT_DOUBLE", names=(below,))


def test_sl7_a_line_that_names_nothing_is_a_finding(clean_repo, work):
    lines = support.clean_lines() + [support.line("docs/guide/ghost.md", "docs")]
    run, numbers = support.check_lines(work, clean_repo, lines)
    support.one_finding(support.result_of(run, 1), "LAYOUT_NO_ITEM", line=numbers[len(lines) - 1],
                        path="docs/guide/ghost.md")


MISCLASSED = [
    ("governance/kernel/skills/retrieval.md", "docs", "kit"), ("CLAUDE.md", "docs", "governance"),
    (".github/workflows/ci.yml", "docs", "config"), ("eval/visible/cases.jsonl", "data", "evaluation"),
    ("docs/close/PLT-1.md", "docs", "record"), (".env", "config", "secret"), ("node_modules", "data", "generated"),
]


@pytest.mark.parametrize("path,planted,rule", MISCLASSED)
def test_sl7_a_rule_decided_item_under_another_class_is_a_finding(clean_repo, work, path, planted, rule):
    lines = support.clean_lines()
    item = support.by_path(lines, path)
    item["class"] = planted
    run, numbers = support.check_lines(work, clean_repo, lines)
    result = support.result_of(run, 1)
    found = support.one_finding(result, "LAYOUT_RULE_CLASS", line=numbers[lines.index(item)], path=path)
    assert found.get("rule_class") == rule, f"the rule's class is not stated as {rule}: {found}"


# --- SL-8: valid -------------------------------------------------------------------------------------------------------

def _set(**values):
    return lambda item: item.update(values)


def _drop(key):
    return lambda item: item.pop(key)


ASK = {"question": support.QUESTION, "recommended": "docs"}

# fault -> (the plan line changed, the change, the field the finding names)
INVALID = {
    "class-outside-the-list": ("docs/guide/ops.md", _set(**{"class": "manual"}), "class"),
    "missing-path": ("README.md", _drop("path"), "path"),
    "missing-class": ("web/app/main.js", _drop("class"), "class"),
    "missing-destination": ("web/GUIDE.md", _drop("destination"), "destination"),
    "missing-reason": ("tools/gen.py", _drop("reason"), "reason"),
    "missing-kind": ("data/prices.csv", _drop("kind"), "kind"),
    "missing-stale-class-key": ("docs/specs/search.md", _drop("stale_class"), "stale_class"),
    "missing-import-key": ("AGENTS.md", _drop("import"), "import"),
    "missing-sign": ("pyproject.toml", _drop("sign"), "sign"),
    "missing-ask-key": (".gitignore", _drop("ask"), "ask"),
    "unknown-field": ("web/package.json", _set(colour="red"), "colour"),
    "kind-outside-the-list": ("tests/test_core.py", _set(kind="directory"), "kind"),
    "kind-file-as-ignored-root": ("src/meadow/__init__.py", _set(kind="ignored-root"), "kind"),
    "kind-file-as-submodule": ("src/meadow/NOTES.md", _set(kind="submodule"), "kind"),
    "kind-submodule-as-file": ("external/widgets", _set(kind="file"), "kind"),
    "kind-untracked-as-folder": ("scratch-notes", _set(kind="folder"), "kind"),
    "sign-outside-the-list": ("src/meadow/schema.json", _set(sign="vibes"), "sign"),
    "stale-class-missing-on-archive": ("plans/roadmap-2024.md", _set(stale_class=None), "stale_class"),
    "stale-class-on-docs": ("docs/guide/setup.md", _set(stale_class="legacy"), "stale_class"),
    "stale-class-not-one-of-three": ("journal/2023-retro.md", _set(stale_class="obsolete"), "stale_class"),
    "import-missing-on-an-import": ("vendor/jsonlib", _set(**{"import": None}), "import"),
    "import-on-docs": ("docs/research/old-study/notes.md", _set(**{"import": "stray"}), "import"),
    "ask-line-without-ask": ("misc/oddity.txt", _set(ask=None), "ask"),
    "ask-without-a-question": ("misc/oddity.txt", _set(ask={"recommended": "docs"}), "ask"),
    "ask-with-an-empty-question": ("misc/oddity.txt", _set(ask={"question": "", "recommended": "docs"}), "ask"),
    "ask-without-a-recommendation": ("misc/oddity.txt", _set(ask={"question": support.QUESTION}), "ask"),
    "ask-recommending-no-class": ("misc/oddity.txt", _set(ask={**ASK, "recommended": "manual"}), "ask"),
    "ask-value-on-another-class": ("data/prices.csv", _set(ask=ASK), "ask"),
    "empty-reason": (".tickets/PLT-1.md", _set(reason=""), "reason"),
}


@pytest.mark.parametrize("fault", sorted(INVALID))
def test_sl8_one_planted_invalid_line_is_a_finding_naming_the_field(clean_repo, work, fault):
    path, change, field = INVALID[fault]
    lines = support.clean_lines()
    item = support.by_path(lines, path)
    index = lines.index(item)
    change(item)
    run, numbers = support.check_lines(work, clean_repo, lines, blank_before=(2,))
    result = support.result_of(run, 1)
    found = [f for f in support.findings(result, "LAYOUT_INVALID")
             if f.get("line") == numbers[index] and f.get("field") == field]
    assert found, (f"no LAYOUT_INVALID on line {numbers[index]} naming the field {field!r}: "
                   f"{result['findings'][:20]}")
    elsewhere = [f for f in support.findings(result, "LAYOUT_INVALID") if f.get("line") != numbers[index]]
    assert not elsewhere, f"valid lines are reported: {elsewhere}"


@pytest.mark.parametrize("count", [10, 11])
def test_sl8_one_reason_on_ten_paths_passes_and_on_an_eleventh_is_a_finding(clean_repo, work, count):
    lines = support.clean_lines()
    chosen = [item for item in lines if item["kind"] == "file" and item["class"] != "ask"][:count]
    for item in chosen:
        item["reason"] = "copied template reason"
    run, numbers = support.check_lines(work, clean_repo, lines)
    if count == 10:
        support.assert_clean(run)
        return
    result = support.result_of(run, 1)
    used = {numbers[lines.index(item)] for item in chosen}
    found = [f for f in support.findings(result, "LAYOUT_INVALID") if f.get("field") == "reason"]
    assert found and {f.get("line") for f in found} <= used, (
        f"eleven copies of one reason give no LAYOUT_INVALID on its lines: {result['findings'][:20]}")


# --- SL-9: where the standard puts it ----------------------------------------------------------------------------------

# plan line -> (a wrong destination, the expected one; None: the agent chooses a folder, so only its shape is held)
WRONG = {
    "src/meadow/core.py": ("lib/core.py", "src/meadow/core.py"),                     # code moved
    "tools/gen.py": ("src/tools/gen.py", "tools/gen.py"),                            # code outside a package root
    "tests/test_core.py": ("src/meadow/test_core.py", "tests/test_core.py"),         # a test moved
    "src/meadow/schema.json": ("data/schema.json", "src/meadow/schema.json"),        # under the package root
    "src/meadow/NOTES.md": ("docs/NOTES.md", "src/meadow/NOTES.md"),                 # under the package root
    "web/GUIDE.md": ("docs/GUIDE.md", "web/GUIDE.md"),                               # under a subfolder's root
    "CLAUDE.md": ("docs/CLAUDE.md", "CLAUDE.md"),                                    # tool-fixed
    "openspec/specs/billing/spec.md": ("docs/specs/spec.md", "openspec/specs/billing/spec.md"),
    "docs/close/PLT-1.md": ("docs/records/close/PLT-1.md", "docs/close/PLT-1.md"),   # tool-written
    "README.md": ("docs/README.md", "README.md"),
    ".tickets/PLT-1.md": ("governance/PLT-1.md", ".tickets/PLT-1.md"),               # governance
    "governance/kernel/skills/retrieval.md": ("docs/retrieval.md", "governance/kernel/skills/retrieval.md"),
    ".github/workflows/ci.yml": ("ci/ci.yml", ".github/workflows/ci.yml"),           # config
    "config/.env.example": ("data/.env.example", "config/.env.example"),
    "views/index.generated.md": ("docs/index.generated.md", "views/index.generated.md"),
    "eval/visible/cases.jsonl": ("data/cases.jsonl", "eval/visible/cases.jsonl"),
    ".env": ("data/.env", ".env"),                                                   # secret, ignored
    "node_modules": ("data/node_modules", "node_modules"),                           # generated, ignored
    "misc/oddity.txt": ("docs/oddity.txt", "misc/oddity.txt"),                       # ask
    "../solar-sketch": ("imports/solar", "../solar-sketch"),                         # declared
    "docs/guide/setup.md": ("docs/setup.md", "docs/guide/setup.md"),                 # already in its place
    "docs/specs/search.md": ("docs/specs/search/search.md", "docs/specs/search.md"),
    "docs/research/old-study/notes.md": ("docs/research/notes/notes.md", "docs/research/old-study/notes.md"),
    "docs/records/measures/2025-01-05.md": ("docs/records/2025-01-05.md", "docs/records/measures/2025-01-05.md"),
    "data/prices.csv": ("data/tables/prices.csv", "data/prices.csv"),
    "archive/superseded/docs/prior.md": ("archive/superseded/archive/superseded/docs/prior.md",
                                         "archive/superseded/docs/prior.md"),
    "notes/handbook.md": ("docs/notes/handbook.md", "docs/handbook.md"),             # docs
    "design/checkout-spec.md": ("docs/checkout-spec.md", "docs/specs/checkout-spec.md"),
    "experiments/cache-study.md": ("docs/research/cache-study.md", None),            # no folder
    "reports/audit-2025-03-02.md": ("docs/reports/audit-2025-03-02.md", None),
    "fixtures/sample-orders.csv": ("data/fixtures/sample-orders.csv", "data/sample-orders.csv"),
    "seedpack": ("data/seed", "data/seedpack"),
    "plans/roadmap-2024.md": ("archive/legacy/plans/roadmap-2024.md",
                              "archive/superseded/plans/roadmap-2024.md"),
    "legacy-queue": ("archive/legacy-queue", "archive/legacy/legacy-queue"),
    "journal/2023-retro.md": ("archive/historical/2023-retro.md", "archive/historical/journal/2023-retro.md"),
    "archive/old/ancient.md": ("archive/historical/archive/old/ancient.md", "archive/historical/old/ancient.md"),
    "vendor/jsonlib": ("imports/vendor/jsonlib", "imports/jsonlib"),
    "borrowed/ratelimit/limit.py": ("src/ratelimit/limit.py", "imports/ratelimit/limit.py"),
    "study/notebook": ("docs/research/notebook", "imports/notebook"),
    "external/widgets": ("vendor/widgets", "imports/widgets"),
    "todo.md": ("todo.md", "docs/todo.md"),                                          # left where it is
    "scratch-notes": ("data/notes", "data/scratch-notes"),
}


@pytest.fixture(scope="module")
def wrong_destinations(clean_repo, tmp_path_factory):
    """One run on the clean plan with every destination of ``WRONG`` planted."""
    lines = support.clean_lines()
    for path, (wrong, _expected) in WRONG.items():
        support.by_path(lines, path)["destination"] = wrong
    run, numbers = support.check_lines(tmp_path_factory.mktemp("w2-213-wrong"), clean_repo, lines)
    return run, {item["path"]: numbers[n] for n, item in enumerate(lines)}


@pytest.mark.parametrize("path", sorted(WRONG))
def test_sl9_a_wrong_destination_is_a_finding_stating_the_expected_one(wrong_destinations, path):
    run, numbers = wrong_destinations
    result = support.result_of(run, 1)
    found = support.one_finding(result, "LAYOUT_DESTINATION", line=numbers[path], path=path)
    expected = WRONG[path][1]
    stated = str(found.get("expected") or "")
    if expected is None:
        folder = "docs/research/" if path.startswith("experiments/") else "docs/records/"
        assert folder in stated and path.rsplit("/", 1)[-1] in stated, f"no expected place stated: {found}"
    else:
        assert stated == expected, f"expected {expected!r}, the finding states {found.get('expected')!r}"


def test_sl9_no_correct_destination_is_reported(wrong_destinations):
    run, numbers = wrong_destinations
    result = support.result_of(run, 1)
    wrong_lines = {numbers[path] for path in WRONG}
    other = [f for f in support.findings(result, "LAYOUT_DESTINATION") if f.get("line") not in wrong_lines]
    assert not other, f"correct destinations are reported: {other}"


def test_sl9_the_agents_choice_of_a_research_or_record_folder_is_accepted(clean_repo, work):
    lines = support.clean_lines()
    support.by_path(lines, "experiments/cache-study.md")["destination"] = "docs/research/caching/cache-study.md"
    support.by_path(lines, "reports/audit-2025-03-02.md")["destination"] = (
        "docs/records/reviews/audit-2025-03-02.md")
    run, _ = support.check_lines(work, clean_repo, lines)
    support.assert_clean(run)


# --- SL-10: coherent, and the stoppers ---------------------------------------------------------------------------------

def test_sl10_two_import_classes_in_one_import_are_a_finding_naming_both_paths(clean_repo, work):
    lines = support.clean_lines()
    support.by_path(lines, "borrowed/ratelimit/limit.py")["class"] = "import-use"
    run, _ = support.check_lines(work, clean_repo, lines)
    found = support.findings(support.result_of(run, 1), "LAYOUT_IMPORT")
    assert any(f.get("path") and f.get("other") and "borrowed/ratelimit/limit.py" in support.text_of(f)
               and support.text_of(f).count("borrowed/ratelimit/") >= 2 for f in found), (
        f"no LAYOUT_IMPORT naming both paths: {found}\n{run.describe()}")


@pytest.mark.parametrize("destination", ["imports/ratelimit/x.py", "imports/elsewhere/sub/x.py"])
def test_sl10_an_import_that_would_move_other_than_whole_is_a_finding(clean_repo, work, destination):
    lines = support.clean_lines()
    support.by_path(lines, "borrowed/ratelimit/sub/x.py")["destination"] = destination
    run, _ = support.check_lines(work, clean_repo, lines)
    found = support.findings(support.result_of(run, 1), "LAYOUT_IMPORT")
    assert any(f.get("path") and f.get("other") and "borrowed/ratelimit/sub/x.py" in support.text_of(f)
               for f in found), f"no LAYOUT_IMPORT naming both paths: {found}\n{run.describe()}"


def test_sl10_two_items_with_one_destination_are_a_finding_naming_both(own_repo, work):
    support.add_commit(own_repo, {"manuals/handbook.md": "# Another handbook\n"})
    lines = support.clean_lines() + [support.line("manuals/handbook.md", "docs", "docs/handbook.md")]
    run, _ = support.check_lines(work, own_repo, lines)
    support.one_finding(support.result_of(run, 1), "LAYOUT_TARGET_TAKEN",
                        names=("notes/handbook.md", "manuals/handbook.md"))


def test_sl10_a_destination_that_already_exists_is_a_finding_naming_both(own_repo, work):
    support.add_commit(own_repo, {"docs/handbook.md": "# The handbook already there\n"})
    lines = support.clean_lines() + [support.line("docs/handbook.md", "docs")]
    run, _ = support.check_lines(work, own_repo, lines)
    support.one_finding(support.result_of(run, 1), "LAYOUT_TARGET_TAKEN",
                        names=("notes/handbook.md", "docs/handbook.md"))


@pytest.fixture(scope="module")
def stopped(dirty_repo, tmp_path_factory):
    """The dirty repository with a plan whose only faults are its stoppers."""
    run, _ = support.check_lines(tmp_path_factory.mktemp("w2-213-stopped"), dirty_repo, support.dirty_lines())
    return run


@pytest.mark.parametrize("path", [*support.TRACKED_STOPPERS, "eval/hidden/more.txt"])
def test_sl10_a_hidden_set_path_or_tracked_secret_is_a_stopper(stopped, path):
    result = support.result_of(stopped, 1)
    found = [s for s in result["stoppers"] if s.get("path") == path]
    assert found and all(s.get("code") == "LAYOUT_STOPPER" and s.get("message") for s in found), (
        f"{path} is no stopper: {result['stoppers']}")


def test_sl10_stoppers_are_listed_apart_and_ignored_secrets_are_none(stopped):
    result = support.result_of(stopped, 1)
    assert result["findings"] == [], f"a stopper is an ordinary finding, or a line is reported: {result['findings']}"
    paths = {s.get("path") for s in result["stoppers"]}
    wanted = {*support.TRACKED_STOPPERS, "eval/hidden/more.txt"}
    assert paths == wanted, f"stoppers {sorted(paths)}; missing {sorted(wanted - paths)}"


def test_sl10_stoppers_are_reported_even_for_lines_not_written_or_classed_otherwise(dirty_repo, work):
    lines = support.clean_lines() + [support.line("vault-sets/q1.txt", "docs", "docs/q1.txt"),
                                     support.line("deploy/server.pem", "config")]
    run, _ = support.check_lines(work, dirty_repo, lines)
    result = support.result_of(run, 1)
    paths = {s.get("path") for s in result["stoppers"]}
    missing = {*support.TRACKED_STOPPERS, "eval/hidden/more.txt"} - {"notes/vault-login.txt"} - paths
    assert not missing, f"no stopper for {sorted(missing)}: {result['stoppers']}"
    assert not {".env", "id_rsa", "config/.env.example"} & paths, f"an ignored secret file is a stopper: {paths}"


def test_sl10_the_text_form_prints_the_stoppers_first(dirty_repo, work):
    lines = support.dirty_lines()
    support.by_path(lines, "notes/handbook.md")["destination"] = "guides/handbook.md"
    plan, _ = support.write_plan(work / "plan.jsonl", lines)
    run = support.run_check(work, dirty_repo, plan, json_form=False)
    assert run.returncode == 1, run.describe()
    codes = [row.split()[3] for row in run.stdout.splitlines()
             if row.startswith("gov layout check: LAYOUT_") and len(row.split()) > 3]
    stoppers = codes.count("LAYOUT_STOPPER")
    assert stoppers >= 6 and codes[:stoppers] == ["LAYOUT_STOPPER"] * stoppers and len(codes) > stoppers, (
        f"the stoppers are not printed first: {codes}\n{run.describe()}")
