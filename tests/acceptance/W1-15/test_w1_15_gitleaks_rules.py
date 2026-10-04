"""KPI success 1: ``.gitleaks.toml`` extends the defaults with token and canary rules, and the canary is detected.

Two files hold the rules (README, package DP-4): ``.gitleaks.toml`` is this
repository's configuration, ``template/.gitleaks.toml`` is the one the kernel
ships to an adopting project. Both extend the gitleaks defaults and add the
token and canary rules. The tests that run the binary are ``local_only``.
"""

from __future__ import annotations

import pytest

import w1_15_support as support

BOTH = pytest.mark.parametrize("config", list(support.CONFIGS), indirect=True)
WHICH = pytest.mark.parametrize("which", list(support.CONFIGS))


def _plant(tmp_path, text, rel="notes/page.md"):
    tree = tmp_path / "tree"
    path = tree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return tree


def _load(which):
    reason = None
    try:
        return support.load_config(which)
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


# --------------------------------------------------------------------------
# The files themselves
# --------------------------------------------------------------------------

@WHICH
def test_the_configuration_extends_the_gitleaks_defaults(which):
    document = _load(which)
    extend = document.get("extend")
    assert isinstance(extend, dict) and extend.get("useDefault") is True, \
        f"{support.CONFIGS[which]} does not extend the gitleaks defaults ([extend] useDefault = true)"


@WHICH
def test_the_configuration_adds_rules_of_its_own(which):
    """The token and canary rules are rules of this file, next to the defaults it extends."""
    document = _load(which)
    rules = document.get("rules")
    assert isinstance(rules, list) and rules, f"{support.CONFIGS[which]} adds no [[rules]] to the defaults"
    for rule in rules:
        assert isinstance(rule, dict) and isinstance(rule.get("id"), str) and rule["id"].strip(), \
            f"{support.CONFIGS[which]}: a rule has no id: {rule!r}"


def test_the_template_configuration_allowlists_no_path():
    """This repository's allowlist names its own fixtures; a configuration shipped to another project carries none."""
    document = _load("template")
    entries = list(document.get("allowlists") or [])
    if isinstance(document.get("allowlist"), dict):
        entries.append(document["allowlist"])
    for rule in document.get("rules") or []:
        entries.extend(rule.get("allowlists") or [])
    with_paths = [entry for entry in entries if isinstance(entry, dict) and entry.get("paths")]
    assert not with_paths, f"{support.TEMPLATE_CONFIG_REL} allowlists paths: {with_paths}"


# --------------------------------------------------------------------------
# Detection, with the binary
# --------------------------------------------------------------------------

@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("form", list(support.FORMS))
def test_the_canary_is_detected(gitleaks, config, form, tmp_path, sandbox):
    """The canary stands in ordinary text, with no key name beside it."""
    tree = _plant(tmp_path, support.in_prose(support.FORMS[form]))
    findings = support.scan(tree, config, sandbox)
    assert "notes/page.md" in [file for file, _ in findings], \
        f"gitleaks with {config} does not detect the canary ({form}); findings: {findings}"


@pytest.mark.local_only
@pytest.mark.parametrize("form", list(support.FORMS))
def test_the_gitleaks_defaults_alone_miss_the_canary(gitleaks, form, tmp_path, sandbox):
    """Why the rules are needed (CAP-03 acceptance): the defaults do not find this canary. Passes before W1-15."""
    defaults = tmp_path / "defaults.toml"
    defaults.write_text("[extend]\nuseDefault = true\n", encoding="utf-8")
    tree = _plant(tmp_path, support.in_prose(support.FORMS[form]))
    assert support.scan(tree, defaults, sandbox) == []


@pytest.mark.local_only
@BOTH
@pytest.mark.parametrize("kind", list(support.DEFAULT_SECRETS))
def test_a_secret_the_defaults_find_is_still_detected(gitleaks, config, kind, tmp_path, sandbox):
    """The file extends the defaults: adding rules does not switch the default rules off."""
    tree = _plant(tmp_path, f"# Notes\n\n{support.DEFAULT_SECRETS[kind]}\n")
    findings = support.scan(tree, config, sandbox)
    assert "notes/page.md" in [file for file, _ in findings], \
        f"gitleaks with {config} does not detect a {kind}; findings: {findings}"


@pytest.mark.local_only
@BOTH
def test_text_about_canaries_and_tokens_is_not_a_finding(gitleaks, config, tmp_path, sandbox):
    """The rules find canary and token strings, not the words: governance text speaks of both."""
    tree = _plant(tmp_path, support.CLEAN_PROSE)
    findings = support.scan(tree, config, sandbox)
    assert findings == [], f"gitleaks with {config} reports ordinary text: {findings}"


@pytest.mark.local_only
@BOTH
def test_the_token_canary_file_of_the_dev_tier_is_reported(gitleaks, config, tmp_path, sandbox):
    """The canary where it really stands: a clone of the b-dev tier, never the tier itself."""
    clone = support.clone_tier("b-dev", tmp_path / "tier")
    if clone is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / 'b-dev'} (GOV_DEV_TIERS)")
    assert support.DEV_TOKEN_FILE in support.files_holding(clone, [support.TIER_FORM]), \
        f"the b-dev tier no longer holds the token canary in {support.DEV_TOKEN_FILE}"
    findings = support.scan(clone, config, sandbox)
    assert support.DEV_TOKEN_FILE in [file for file, _ in findings], \
        f"gitleaks with {config} does not report {support.DEV_TOKEN_FILE}; findings: {findings}"
