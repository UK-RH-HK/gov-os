"""KPI success 4 and failure 1: the repaired token rule (DEC-324, DEC-325) [CAP-03.e].

The ``gov-token`` rule flags a prefixed string (``sk``, ``pk``, ``rk`` or
``tok``, then ``_`` or ``-``) only when the body after the prefix holds a
digit, or both an upper-case and a lower-case letter; the floor of 16
characters stays. The tests hold the behaviour, never the shape of the
expression: what the ``gitleaks`` binary reports with each of the two files,
what the pre-index filter lets through (it ignores every allowlist, DEC-298,
so a pass there proves the requirement is in the rule), and what reaches the
code index.
"""

from __future__ import annotations

import tomllib

import pytest

import w1_16_support as support

BOTH = pytest.mark.parametrize("config", list(support.CONFIGS), indirect=True)
WHICH = pytest.mark.parametrize("which", list(support.CONFIGS))
PAGE = "notes/page.md"

# The canary rule as W1-15 delivered it. DEC-325: it is unchanged.
CANARY_REGEX = (r"\b[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*[_-]" + "CAN" + "ARY"
                + r"[_-][A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*")

# Ordinary identifiers where code writes them: no line holds anything else a rule could find.
IDENTIFIER_FILES = {
    "tok-function": ("app/schedule.py",
                     "def {name}(settings):\n    return settings.get('{name}', 30)\n\n\n"
                     "def schedule_entry(settings):\n    return {name}(settings)\n"),
    "pk-column": ("db/schema.py",
                  "{name} = 'order_id'\n\n\ndef order_columns():\n    return [{name}]\n"),
    "rk-partition": ("web/partition.ts",
                     "export function {name}(rows: string[]): number {{\n  return rows.length;\n}}\n"),
    "sk-kebab": ("docs/pipeline.md",
                 "# Pipeline\n\nThe estimator lives in the package {name} and is loaded at start.\n"),
}


def _identifier(key):
    return support.prefixed(*support.IDENTIFIERS[key])


def _identifier_file(key):
    rel, text = IDENTIFIER_FILES[key]
    return rel, text.format(name=_identifier(key))


def _findings(tmp_path, config, sandbox, files):
    tree = support.plant_tree(tmp_path / "tree", files)
    return support.scan(tree, config, sandbox)


def _by_the_token_rule(findings):
    """The files the token rule reports. The rule may be written as several rules whose ids begin with ``gov-token``."""
    return sorted({file for file, rule in findings if rule.startswith(support.TOKEN_RULE)})


# --------------------------------------------------------------------------
# The two files
# --------------------------------------------------------------------------

@WHICH
def test_the_token_rule_carries_no_allowlist(which):
    """The requirement is in the rule itself: no rule of the file is repaired by an allowlist of its own."""
    document = tomllib.loads(support.config_path(which).read_text(encoding="utf-8"))
    rules = document.get("rules") or []
    assert [rule for rule in rules if str(rule.get("id", "")).startswith(support.TOKEN_RULE)], \
        f"{support.CONFIGS[which]} has no {support.TOKEN_RULE} rule"
    sheltered = [rule.get("id") for rule in rules if rule.get("allowlist") or rule.get("allowlists")]
    assert not sheltered, f"{support.CONFIGS[which]}: rules with an allowlist of their own: {sheltered}"


@WHICH
def test_the_canary_rule_is_unchanged(which):
    document = tomllib.loads(support.config_path(which).read_text(encoding="utf-8"))
    rules = [rule for rule in document.get("rules") or [] if rule.get("id") == "gov-canary"]
    assert len(rules) == 1, f"{support.CONFIGS[which]}: expected one gov-canary rule"
    assert rules[0].get("regex") == CANARY_REGEX and rules[0].get("keywords") == ["canary"], \
        f"{support.CONFIGS[which]}: the canary rule changed: {rules[0]}"


# --------------------------------------------------------------------------
# What gitleaks reports with each file
# --------------------------------------------------------------------------

@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("prefix", support.PREFIXES)
@pytest.mark.parametrize("separator", support.SEPARATORS)
def test_a_token_shaped_string_is_still_flagged(gitleaks, config, prefix, separator, tmp_path, sandbox):
    """Every prefix and both separators, with a body that holds digits and mixed case."""
    token = support.prefixed(prefix, separator, support.TOKEN_BODIES["digits-and-mixed-case"])
    findings = _findings(tmp_path, config, sandbox, {PAGE: support.in_prose(token)})
    assert _by_the_token_rule(findings) == [PAGE], \
        f"a token-shaped string is not flagged by the token rule: {findings}"


@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("body", list(support.TOKEN_BODIES))
def test_a_body_with_a_digit_or_with_mixed_case_is_flagged(gitleaks, config, body, tmp_path, sandbox):
    """One digit is enough, wherever it stands; so are one upper-case and one lower-case letter, in either order."""
    token = support.prefixed("tok", "_", support.TOKEN_BODIES[body])
    findings = _findings(tmp_path, config, sandbox, {PAGE: support.in_prose(token)})
    assert _by_the_token_rule(findings) == [PAGE], f"the body {body} is not flagged by the token rule: {findings}"


@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("body", list(support.ORDINARY_BODIES))
def test_a_body_without_a_digit_and_without_mixed_case_is_not_flagged(gitleaks, config, body, tmp_path, sandbox):
    """Lower-case words, however long and however separated, and upper-case words alone, are ordinary identifiers."""
    separator = "-" if body == "lower-kebab" else "_"
    name = support.prefixed("tok", separator, support.ORDINARY_BODIES[body])
    findings = _findings(tmp_path, config, sandbox, {PAGE: support.in_prose(name)})
    assert findings == [], f"an ordinary identifier ({body}) is flagged: {findings}"


@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("prefix", support.PREFIXES)
@pytest.mark.parametrize("separator", support.SEPARATORS)
def test_no_prefix_and_no_separator_flags_an_ordinary_identifier(gitleaks, config, prefix, separator, tmp_path,
                                                                 sandbox):
    body = support.ORDINARY_BODIES["lower-snake" if separator == "_" else "lower-kebab"]
    findings = _findings(tmp_path, config, sandbox, {PAGE: support.in_prose(support.prefixed(prefix, separator, body))})
    assert findings == [], f"an ordinary identifier with the prefix {prefix}{separator} is flagged: {findings}"


@pytest.mark.local_only
@BOTH
def test_ordinary_identifiers_in_code_are_not_flagged(gitleaks, config, tmp_path, sandbox):
    files = dict(_identifier_file(key) for key in IDENTIFIER_FILES)
    findings = _findings(tmp_path, config, sandbox, files)
    assert findings == [], f"ordinary identifiers in code are flagged: {findings}"


@pytest.mark.local_only
@BOTH
def test_the_length_floor_of_sixteen_characters_stays(gitleaks, config, tmp_path, sandbox):
    """A body of 15 characters is not a token, digits or not; the same body with one more character is."""
    short = "a1B2c3D4e5F6g7H"
    assert len(short) == 15
    files = {"notes/short.md": support.in_prose(support.prefixed("sk", "_", short)),
             "notes/floor.md": support.in_prose(support.prefixed("sk", "_", short + "8"))}
    flagged = _by_the_token_rule(_findings(tmp_path, config, sandbox, files))
    assert flagged == ["notes/floor.md"], f"the token rule flags {flagged}; expected only the 16-character body"


@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("tier", list(support.DEV_PLANTED))
def test_every_file_holding_a_dev_canary_is_still_reported(gitleaks, config, tier, tmp_path, sandbox):
    """The seven dev canaries (DEC-286): every file of a tier clone that holds one is reported with the new rule."""
    clone = support.clone_tier(tier, tmp_path / "tier")
    if clone is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
    holding = support.files_holding(clone, support.DEV_PLANTED[tier])
    found = {hit for hits in holding.values() for hit in hits}
    assert found == set(support.DEV_PLANTED[tier]), f"the {tier} tier no longer holds all its planted values"
    reported = {file for file, _ in support.scan(clone, config, sandbox)}
    missed = sorted(set(holding) - reported)
    assert not missed, f"files holding a dev canary are not reported: {missed}"


# --------------------------------------------------------------------------
# Through the pre-index filter, which ignores every allowlist (DEC-298)
# --------------------------------------------------------------------------

@pytest.mark.local_only
@WHICH
@pytest.mark.parametrize("key", list(IDENTIFIER_FILES))
def test_a_file_whose_only_match_is_an_ordinary_identifier_is_indexable(gitleaks, which, key, tmp_path, sandbox):
    """Failure 1, at the filter: with either file as the project's ``.gitleaks.toml`` the file is let through."""
    repo = support.Repo(tmp_path / "project", config=which)
    rel, text = _identifier_file(key)
    repo.write(rel, text)
    clean = repo.write("notes/clean.md", "# Notes\n\nOrdinary text.\n")
    allowed = support.indexable(repo.root, [rel, clean], sandbox)
    assert allowed == [rel, clean], f"the file with the identifier {key} is kept from the indexer: {allowed}"


@pytest.mark.local_only
@WHICH
@pytest.mark.parametrize("body", ["digit-last", "mixed-case-no-digit"])
def test_a_file_with_a_token_shaped_string_is_not_indexable(gitleaks, which, body, tmp_path, sandbox):
    repo = support.Repo(tmp_path / "project", config=which)
    token = support.prefixed("pk", "_", support.TOKEN_BODIES[body])
    planted = repo.write("app/credentials.py", f'CLIENT = "{token}"\n')
    clean = repo.write("notes/clean.md", "# Notes\n\nOrdinary text.\n")
    allowed = support.indexable(repo.root, [planted, clean], sandbox)
    assert allowed == [clean], f"a token-shaped string ({body}) is let through to the indexer: {allowed}"


# --------------------------------------------------------------------------
# Into the code index
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_a_file_whose_only_match_is_an_ordinary_identifier_reaches_the_index(module, cbm, sandbox, tmp_path):
    """Failure 1, at the index: the functions named like a prefixed token are defined and have their callers."""
    repo = support.Repo(tmp_path / "project")
    for key in ("tok-function", "pk-column", "rk-partition"):
        repo.write(*_identifier_file(key))
    repo.commit("first")
    function, partition = _identifier("tok-function"), _identifier("rk-partition")
    run = support.codeintel(repo.root, [("index", []), ("definitions", [function]), ("callers", [function]),
                                        ("definitions", [partition]), ("definitions", ["order_columns"])], sandbox)
    assert ("app/schedule.py", function) in support.entries(run.results[1], "definitions", repo.root), run.describe()
    assert ("app/schedule.py", "schedule_entry") in support.entries(run.results[2], "callers", repo.root), \
        run.describe()
    assert ("web/partition.ts", partition) in support.entries(run.results[3], "definitions", repo.root), run.describe()
    assert ("db/schema.py", "order_columns") in support.entries(run.results[4], "definitions", repo.root), \
        run.describe()


@pytest.mark.local_only
def test_a_file_with_a_token_shaped_string_stays_out_of_the_index(module, cbm, sandbox, tmp_path):
    repo = support.Repo(tmp_path / "project")
    token = support.prefixed("rk", "-", support.TOKEN_BODIES["digits-and-mixed-case"])
    repo.write("app/credentials.py", f'CLIENT = "{token}"\n\n\ndef credentials_helper():\n    return CLIENT\n')
    repo.write("app/clean.py", "def clean_helper(value):\n    return value + 1\n")
    repo.commit("first")
    run = support.codeintel(repo.root, [("index", []), ("definitions", ["credentials_helper"]),
                                        ("definitions", ["clean_helper"])], sandbox)
    assert run.results[1] == [], f"a file with a token-shaped string is in the code graph\n{run.describe()}"
    assert ("app/clean.py", "clean_helper") in support.entries(run.results[2], "definitions", repo.root)
    assert not support.files_holding(repo.root / support.RUNTIME_REL, [token]), \
        "the token-shaped string stands under .gov-runtime/"
