"""W2-174 S5: ``gov adopt --facts`` writes the default facts file; an existing one is left byte for byte (README)."""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pytest
import yaml

import w2_174_support as s


def _schema_errors(instance) -> list[str]:
    import jsonschema

    schema = json.loads(s.FACTS_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in validator.iter_errors(instance)]


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _strings(key)
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def _adopt_facts(repo):
    """(result, the UTC dates the run may carry) of ``gov adopt --facts --root <repo>``."""
    before = s.utc_today()
    result = s.result_of(repo.adopt("--facts"))
    return result, {before, s.utc_today()}


def _check_default_file(repo, text: str, dates: set[datetime.date]) -> dict:
    """Every claim of the ticket's S5 line and the lead's L7 about the file written."""
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"the facts file is not a YAML mapping: {text[:200]!r}"
    errors = _schema_errors(data)
    assert not errors, f"the facts file does not validate against facts.schema.json: {errors[:5]}"
    quoted = re.findall(r"^\s*new_since:\s*(['\"])(\d{4}-\d{2}-\d{2})\1\s*(?:#.*)?$", text, re.MULTILINE)
    assert len(quoted) == 1, f"ready.new_since is not written as a quoted ISO string: {re.findall('new_since.*', text)}"
    assert isinstance(data["ready"]["new_since"], str)
    assert datetime.date.fromisoformat(data["ready"]["new_since"]) in dates, \
        f"ready.new_since {data['ready']['new_since']!r} is not the UTC date of the run {sorted(dates)}"
    for forbidden in (str(repo.root), repo.root.name, str(repo.tmp), "/home/"):
        assert forbidden not in text, f"the facts file names {forbidden!r}, which is of this repository or machine"
    commands = data["commands"]
    for name, entry in commands.items():
        placeholder = "{UNSET_" + name.upper() + "}"
        run = entry["run"]
        assert run.startswith("gov ") or run == placeholder, \
            f"command {name}: run {run!r} is neither a gov form nor the placeholder {placeholder}"
        if run == placeholder:
            assert entry["check"] == placeholder, f"command {name}: a placeholder's check is {entry['check']!r}"
    assert commands["lead_verify"]["run"] == "{UNSET_LEAD_VERIFY}", f"lead_verify is {commands['lead_verify']!r}"
    assert commands["wait_for"]["run"].startswith("gov wait"), f"wait_for is {commands['wait_for']['run']!r}"
    return data


def test_s5_a_repository_without_a_facts_file_gets_one_that_validates_and_is_a_product_default(repo):
    assert not (repo.root / s.FACTS_REL).exists()
    result, dates = _adopt_facts(repo)
    path = repo.root / s.FACTS_REL
    assert result.get("written") is True, f"result is {result!r}"
    assert Path(result.get("path", "")).resolve() == path.resolve(), f"result path is {result.get('path')!r}"
    assert path.is_file(), "no governance/project/facts.yaml was written"
    _check_default_file(repo, path.read_text(encoding="utf-8"), dates)


def test_s5_the_default_file_is_the_same_text_on_a_second_repository(repo, tmp_path_factory):
    """No value of the file comes from the repository it is written into: two repositories, two names, one text but
    for the date."""
    first, _ = _adopt_facts(repo)
    other = s.Repo(tmp_path_factory.mktemp("second"), name="another-folder-name-z9k")
    s.result_of(other.adopt("--facts"))
    a = yaml.safe_load((repo.root / s.FACTS_REL).read_text(encoding="utf-8"))
    b = yaml.safe_load((other.root / s.FACTS_REL).read_text(encoding="utf-8"))
    a["ready"] = b["ready"] = None
    assert a == b, "the default facts differ between two repositories"
    assert first.get("written") is True


def test_s5_gov_brief_there_no_longer_answers_facts_missing(repo):
    repo.kernel_templates()
    repo.ticket("DAEO-fx01", "W2-901", "in_progress", [s.verified("The widget prints its name [DEC-1].")],
                [s.verified("The widget prints nothing [DEC-1].")])
    before = repo.gov("brief", "engineer", "DAEO-fx01", json_out=True)
    assert "BRIEF_FACTS_MISSING" in before.stdout + before.stderr, \
        f"the fixture without a facts file is not refused as BRIEF_FACTS_MISSING: {s.describe(before)}"
    _adopt_facts(repo)
    after = repo.gov("brief", "engineer", "DAEO-fx01", json_out=True)
    for code in ("BRIEF_FACTS_MISSING", "BRIEF_FACTS_UNREADABLE"):
        assert code not in after.stdout + after.stderr, \
            f"gov brief answers {code} after the facts step: {s.describe(after)}"
    data = s.envelope(after)
    findings = [(f.get("code"), str(f.get("detail"))) for f in ((data.get("error") or {}).get("details") or {}).get("findings", [])]
    assert ("PLACEHOLDER_LEFT", "UNSET_LEAD_VERIFY") not in findings, \
        "the engineer's template does not name lead_verify, so its brief must not be refused for it"


def test_s5_gov_brief_lead_names_the_unset_lead_verify_placeholder_as_a_refusal(repo):
    repo.kernel_templates()
    repo.ticket("DAEO-fx01", "W2-901", "in_progress", [s.verified("The widget prints its name [DEC-1].")],
                [s.verified("The widget prints nothing [DEC-1].")])
    _adopt_facts(repo)
    done = repo.gov("brief", "lead", "DAEO-fx01", "--run", "build", json_out=True)
    assert done.returncode != 0, f"gov brief lead --run build built a brief with an unset command: {s.describe(done)}"
    data = s.envelope(done)
    error = data.get("error") or {}
    assert error.get("code") == "BRIEF_NOT_READY", f"the refusal is {error.get('code')!r}, not BRIEF_NOT_READY"
    findings = [(f.get("code"), str(f.get("detail"))) for f in (error.get("details") or {}).get("findings", [])]
    assert any(code == "PLACEHOLDER_LEFT" and "UNSET_LEAD_VERIFY" in detail for code, detail in findings), \
        f"no PLACEHOLDER_LEFT finding names UNSET_LEAD_VERIFY: {findings}"


def test_s5_a_repository_with_its_own_facts_file_keeps_it_byte_identical(repo):
    own = ("# the project's own facts, as its CTO wrote them\n"
           "paths: {main: '/srv/own/main'}   # a note\n"
           "commands:\n  accept: {run: 'make accept', check: 'make -n accept'}\n"
           "unknown_key: [1, 2, 3]\n")
    path = repo.file(s.FACTS_REL, own)
    before = s.snapshot(repo.tmp)
    result, _ = _adopt_facts(repo)
    assert result.get("written") is False, f"result is {result!r}"
    assert Path(result.get("path", "")).resolve() == path.resolve()
    assert path.read_bytes() == own.encode(), "an existing facts file was changed"
    assert s.snapshot(repo.tmp) == before, f"the step changed the tree: {s.changed_entries(before, s.snapshot(repo.tmp))}"


def test_s5_a_valid_facts_file_of_the_project_is_kept_too(repo):
    repo.filled_facts()
    path = repo.root / s.FACTS_REL
    before = path.read_bytes()
    result, _ = _adopt_facts(repo)
    assert result.get("written") is False and path.read_bytes() == before


def test_s5_running_the_step_twice_changes_nothing_the_second_time(repo):
    first, _ = _adopt_facts(repo)
    path = repo.root / s.FACTS_REL
    written = path.read_bytes()
    second, _ = _adopt_facts(repo)
    assert first.get("written") is True and second.get("written") is False
    assert path.read_bytes() == written


def test_s5_function_write_default_with_a_fixed_date(repo):
    module = s.facts_module()
    path = repo.root / s.FACTS_REL
    result = module.write_default(repo.root, datetime.date(2031, 2, 3))
    assert result.get("written") is True and Path(result.get("path", "")).resolve() == path.resolve(), f"{result!r}"
    text = path.read_text(encoding="utf-8")
    data = _check_default_file(repo, text, {datetime.date(2031, 2, 3)})
    assert data["ready"]["new_since"] == "2031-02-03"
    assert "'2031-02-03'" in text or '"2031-02-03"' in text


def test_s5_function_write_default_leaves_an_existing_file_alone(repo):
    module = s.facts_module()
    own = "# mine\npaths: {main: /x}\n"
    path = repo.file(s.FACTS_REL, own)
    result = module.write_default(repo.root, datetime.date(2031, 2, 3))
    assert result.get("written") is False and Path(result.get("path", "")).resolve() == path.resolve(), f"{result!r}"
    assert path.read_bytes() == own.encode()


@pytest.mark.parametrize("date", [datetime.date(2026, 1, 9), datetime.date(2026, 12, 31), datetime.date(2030, 2, 28)])
def test_s5_function_new_since_is_the_date_given(repo, date):
    s.facts_module().write_default(repo.root, date)
    data = yaml.safe_load((repo.root / s.FACTS_REL).read_text(encoding="utf-8"))
    assert data["ready"]["new_since"] == date.isoformat()
