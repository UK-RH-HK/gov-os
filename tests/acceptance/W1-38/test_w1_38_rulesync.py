"""W1-38 -- rulesync adapters and .claude ownership.

Acceptance tests for ticket DAEO-3ef2 (profile STANDARD). Each test builds an
adopted project under pytest's ``tmp_path`` (the template's ``.rulesync/``
sources, the kernel, the tool registry, the check's declaration), runs
``rulesync generate`` there, and asserts the outcome against the KPI lines and
the governing decisions.

Tests are written from the KPIs and decisions, never from the implementation
code in ``src/gov/adapters/`` or ``template/.rulesync/``. Two rules hold for
every case: nothing is called a match that was not compared, and no source text
is a stand-in written for the test (the only stand-ins are for the rulesync
*binary*: absent, hanging, failing, or of another version).
"""

from __future__ import annotations

import json
import subprocess

import pytest

import w1_38_support as support

needs_rulesync = pytest.mark.needs_rulesync

HAND_EDITED = (
    "CLAUDE.md",
    "AGENTS.md",
    ".claude/agents/engineer.md",
    ".claude/skills/planning/SKILL.md",
)
KERNEL_ROLE = "engineer"
KERNEL_SKILL = "planning"
RULESYNC_REASON = "xyzzy: rulesync stopped before it compared anything"


def _hand_edit(project, rel):
    path = project / rel
    assert path.is_file(), f"{rel} was not generated"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nA line added by hand.\n", encoding="utf-8",
    )


def _gov_check(project, sandbox):
    """``(check entry, family entry, run)`` of the family after ``gov check --json``."""
    run = support.run_gov(project, sandbox, "check", "--json")
    entry, family = support.portability_entries(support.check_result(run))
    return entry, family, run


# ===================================================================
# KPI Success 1 — role field-by-field agreement (DEC-352 P-2)
# ===================================================================

class TestRoleFieldAgreement:
    """Generated .claude/agents/<role>.md agrees field by field with the
    kernel role file at template/governance/kernel/roles/<role>.md."""

    @needs_rulesync
    @pytest.mark.parametrize("role", support.ROLE_NAMES)
    def test_role_fields_match_kernel(self, generated_project, role):
        kernel_text = support.read_kernel_role(role)
        kernel_fields = support.parse_fields(kernel_text)
        assert kernel_fields, (
            f"kernel role file {support.KERNEL_ROLES_REL}/{role}.md has no labelled fields"
        )

        agent_path = generated_project / ".claude" / "agents" / f"{role}.md"
        assert agent_path.is_file(), (
            f".claude/agents/{role}.md was not generated"
        )
        agent_text = agent_path.read_text(encoding="utf-8")
        agent_fields = support.parse_fields(agent_text)

        for field_label, kernel_value in kernel_fields.items():
            assert field_label in agent_fields, (
                f".claude/agents/{role}.md is missing the '{field_label}' field "
                f"that the kernel role file has"
            )
            assert support.normalise(agent_fields[field_label]) == support.normalise(kernel_value), (
                f".claude/agents/{role}.md field '{field_label}' does not match "
                f"the kernel role file (whitespace collapsed).\n"
                f"  kernel:    {kernel_value[:200]}\n"
                f"  generated: {agent_fields[field_label][:200]}"
            )

        extra = set(agent_fields) - set(kernel_fields)
        assert not extra, (
            f".claude/agents/{role}.md has labelled fields not in the kernel "
            f"role file: {sorted(extra)}"
        )


# ===================================================================
# KPI Success 1 — 8 kernel method skills, body byte for byte
# ===================================================================

class TestSkillGeneration:
    """Every kernel method skill appears in the generated output, its body
    byte for byte the kernel's. The kernel file stays as its own ticket left
    it; the one tolerated difference is the blank lines between the
    frontmatter and the first line of the body, which rulesync drops."""

    @needs_rulesync
    @pytest.mark.parametrize("skill", support.KERNEL_METHOD_SKILLS)
    def test_skill_body_matches_source(self, generated_project, skill):
        kernel_body = support.generated_body(support.read_kernel_skill(skill))
        assert kernel_body.strip(), (
            f"kernel skill {support.KERNEL_SKILLS_REL}/{skill}/SKILL.md has no body"
        )

        gen_skill = generated_project / ".claude" / "skills" / skill / "SKILL.md"
        assert gen_skill.is_file(), (
            f".claude/skills/{skill}/SKILL.md was not generated; "
            f"the kernel method skill '{skill}' is missing from the rulesync sources"
        )
        gen_body = support.generated_body(gen_skill.read_text(encoding="utf-8"))
        assert gen_body == kernel_body, (
            f".claude/skills/{skill}/SKILL.md body does not match the kernel "
            f"file byte for byte (kernel {len(kernel_body)} bytes, "
            f"generated {len(gen_body)} bytes)"
        )


# ===================================================================
# KPI Success 1 — vendored skills are registered sources (DEC-244)
# ===================================================================

class TestVendoredSkillRegistration:
    """DEC-244: the kernel's ``skills/superpowers/<skill>/`` folder (SKILL.md
    and its supporting files) is the path this ticket registers. What is
    compared: every file of that folder against the file of the same name
    under ``.claude/skills/<skill>/`` (SKILL.md by body, the others by bytes)."""

    @needs_rulesync
    @pytest.mark.parametrize("skill", support.SUPERPOWERS_SKILLS)
    def test_vendored_skill_is_the_kernel_copy(self, generated_project, skill):
        kernel_dir = support.REPO_ROOT / support.SUPERPOWERS_REL / skill
        kernel_files = sorted(p for p in kernel_dir.rglob("*") if p.is_file())
        assert kernel_files, f"{support.SUPERPOWERS_REL}/{skill}/ holds no file"
        generated_dir = generated_project / ".claude" / "skills" / skill

        differing = []
        for kernel_file in kernel_files:
            rel = kernel_file.relative_to(kernel_dir)
            generated = generated_dir / rel
            if not generated.is_file():
                differing.append(f"{rel}: not generated")
            elif rel.name == "SKILL.md":
                if (support.generated_body(generated.read_text(encoding="utf-8"))
                        != support.generated_body(kernel_file.read_text(encoding="utf-8"))):
                    differing.append(f"{rel}: body differs")
            elif generated.read_bytes() != kernel_file.read_bytes():
                differing.append(f"{rel}: bytes differ")
        assert not differing, (
            f".claude/skills/{skill}/ is not the kernel's vendored skill folder: {differing}"
        )


# ===================================================================
# KPI Success 1 — CLAUDE.md and AGENTS.md from one source (CAP-52.a)
# ===================================================================

class TestClaudeMdAndAgentsMd:
    """CLAUDE.md and AGENTS.md carry the one root rule of the sources, and
    AGENTS.md is within the token limit."""

    @needs_rulesync
    def test_claude_md_is_the_root_rule(self, generated_project):
        """Compared: CLAUDE.md, byte for byte, with the body of the rule
        source marked ``root: true``."""
        expected = support.root_rule_body(generated_project)
        claude_md = generated_project / "CLAUDE.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        assert claude_md.read_text(encoding="utf-8") == expected, (
            "CLAUDE.md is not the body of the root rule under .rulesync/rules/"
        )

    @needs_rulesync
    def test_agents_md_carries_the_root_rule(self, generated_project):
        """Compared: the end of AGENTS.md, byte for byte, with the body of
        the same root rule (rulesync puts its own preamble before it)."""
        expected = support.root_rule_body(generated_project)
        agents_md = generated_project / "AGENTS.md"
        assert agents_md.is_file(), "AGENTS.md was not generated"
        assert agents_md.read_text(encoding="utf-8").endswith(expected), (
            "AGENTS.md does not end with the body of the root rule under .rulesync/rules/"
        )

    @needs_rulesync
    def test_agents_md_token_limit(self, generated_project):
        agents_md = generated_project / "AGENTS.md"
        assert agents_md.is_file(), "AGENTS.md was not generated"
        text = agents_md.read_text(encoding="utf-8")
        tok = support.tokens(text)
        assert tok <= support.AGENTS_MD_TOKEN_LIMIT, (
            f"AGENTS.md is {tok} tokens (ceil(len/4)); "
            f"limit is {support.AGENTS_MD_TOKEN_LIMIT}"
        )


# ===================================================================
# KPI Success 1 — OpenSpec commands are registered sources (DEC-074 Q7)
# ===================================================================

class TestOpenSpecCommands:
    """rulesync owns ``.claude/`` and holds the OpenSpec commands as sources
    (DEC-074 Q7). The registered source of a command is the text OpenSpec
    ships: what ``openspec init --tools claude`` of the registered version
    writes. A command text written for this ticket is a stand-in and fails."""

    @needs_rulesync
    @pytest.mark.parametrize("name", support.OPENSPEC_COMMANDS)
    def test_generated_command_is_the_one_openspec_ships(
        self, generated_project, openspec_shipped, name,
    ):
        """Compared: the body byte for byte, and the frontmatter as a mapping."""
        generated = generated_project / support.OPSX_REL / f"{name}.md"
        assert generated.is_file(), (
            f"{support.OPSX_REL}/{name}.md is not generated: the command OpenSpec "
            f"ships is not a registered rulesync source"
        )
        text = generated.read_text(encoding="utf-8")
        shipped = openspec_shipped[name]
        assert support.generated_body(text) == support.generated_body(shipped), (
            f"{support.OPSX_REL}/{name}.md does not have the body of the command "
            f"OpenSpec ships under that name"
        )
        assert support.frontmatter(text) == support.frontmatter(shipped), (
            f"{support.OPSX_REL}/{name}.md does not have the frontmatter of the command "
            f"OpenSpec ships: {support.frontmatter(text)} != {support.frontmatter(shipped)}"
        )

    @needs_rulesync
    def test_no_opsx_command_that_openspec_does_not_ship(
        self, generated_project, openspec_shipped,
    ):
        generated = {p.stem for p in (generated_project / support.OPSX_REL).glob("*.md")}
        extra = sorted(generated - set(openspec_shipped))
        assert not extra, (
            f"{support.OPSX_REL}/ holds commands OpenSpec does not ship: {extra}"
        )


# ===================================================================
# KPI Success 2 — hook-script stubs exist
# ===================================================================

class TestHookStubs:
    """Every command path in generated settings resolves to a file."""

    @needs_rulesync
    def test_hook_stubs_exist(self, generated_project):
        settings = support.load_settings(generated_project)
        script_paths = support.extract_hook_script_paths(settings)
        assert script_paths, (
            "no hook script paths found in .claude/settings.json; "
            "hooks were not generated"
        )
        missing = [p for p in script_paths
                   if not (generated_project / p).is_file()]
        assert not missing, (
            f"hook scripts in .claude/settings.json do not exist: {missing}"
        )


# ===================================================================
# KPI Success 2 — rulesync generate --check is clean
# ===================================================================

class TestGenerateCheck:
    """``rulesync generate --check`` exits 0 after a fresh generation."""

    @needs_rulesync
    def test_check_clean_after_generate(self, generated_project):
        check = support.run_rulesync_check(generated_project)
        assert check.returncode == 0, (
            f"rulesync generate --check failed (exit {check.returncode}) "
            f"after a fresh generation: {check.stderr}"
        )


# ===================================================================
# KPI Success 3 — the family check is registered: gov check runs it
# (CAP-38.b, DEC-186, DEC-438)
# ===================================================================

class TestRegisteredFamilyCheck:
    """``gov check`` in a project lists the declared check under the family
    adapter/model portability and shows the result the check really gave."""

    @needs_rulesync
    def test_gov_check_lists_the_check_under_the_family(self, generated_project, sandbox):
        run = support.run_gov(generated_project, sandbox, "check", "--list", "--json")
        listed = support.listed_portability_checks(run)
        assert len(listed) == 1, (
            f"gov check --list names {len(listed)} checks of the family "
            f"{support.PORTABILITY_FAMILY!r}; one is expected\n{run.describe()}"
        )

    @needs_rulesync
    def test_gov_check_is_green_on_a_clean_generated_project(self, generated_project, sandbox):
        direct = support.run_portability_check(generated_project)
        assert direct.returncode == 0, (
            f"the declared command is not clean on a freshly generated project: "
            f"{support.output_of(direct)}"
        )
        entry, family, run = _gov_check(generated_project, sandbox)
        assert (entry.get("status"), family.get("status")) == (support.GREEN, support.GREEN), (
            f"the check ended clean, but gov check shows the check as "
            f"{entry.get('status')!r} and the family as {family.get('status')!r}\n{run.describe()}"
        )

    @needs_rulesync
    def test_gov_check_is_red_after_a_hand_edit(self, generated_project, sandbox):
        _hand_edit(generated_project, "CLAUDE.md")
        direct = support.run_portability_check(generated_project)
        assert direct.returncode != 0, (
            "the declared command ends clean although CLAUDE.md was edited by hand"
        )
        entry, family, run = _gov_check(generated_project, sandbox)
        assert (entry.get("status"), family.get("status")) == (support.RED, support.RED), (
            f"the check failed, but gov check shows the check as "
            f"{entry.get('status')!r} and the family as {family.get('status')!r}\n{run.describe()}"
        )


# ===================================================================
# KPI Success 1 — the rulesync version the project expects (DEC-127)
# ===================================================================

class TestRulesyncVersion:
    """A project records the rulesync version it expects in the rulesync
    entry of ``governance/project/tool-registry.yaml``. The check compares
    the installed rulesync with it and is never green without having done so."""

    @needs_rulesync
    def test_registry_file_absent_is_not_green(self, generated_project):
        (generated_project / support.TOOL_REGISTRY_REL).unlink()
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            "the check is green although the project has no tool registry: "
            "the rulesync version was not looked at"
        )
        assert "tool-registry.yaml" in support.output_of(result), (
            f"the check does not give the unreadable tool registry as its reason: "
            f"{support.output_of(result)}"
        )

    @needs_rulesync
    def test_registry_without_a_rulesync_entry_is_not_green(self, generated_project):
        support.write_tool_registry(generated_project, names=("uv",))
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            "the check is green although the tool registry has no rulesync entry: "
            "the rulesync version was not looked at"
        )
        assert "tool-registry.yaml" in support.output_of(result), (
            f"the check does not give the tool registry without a rulesync entry "
            f"as its reason: {support.output_of(result)}"
        )

    @needs_rulesync
    def test_project_expecting_another_version_is_not_green(self, generated_project):
        installed = support.rulesync_version()
        support.write_tool_registry(generated_project, rulesync_version="23.0.0")
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            f"the check is green although the project expects rulesync 23.0.0 "
            f"and {installed} is installed"
        )
        output = support.output_of(result)
        assert "23.0.0" in output and installed in output, (
            f"the check does not name the expected (23.0.0) and the installed "
            f"({installed}) version: {output}"
        )

    @needs_rulesync
    def test_installed_rulesync_of_another_version_is_not_green(self, generated_project, mock_dir):
        expected = support.registered_rulesync_version()
        other = support.write_mock_rulesync(mock_dir, (
            'if [[ "$1" == "--version" ]]; then echo "99.0.0"; exit 0; fi\n'
            'exec "$REAL" "$@"'
        ))
        result = support.run_portability_check(
            generated_project, env_override={"RULESYNC_BIN": str(other)},
        )
        assert result.returncode != 0, (
            f"the check is green although the installed rulesync reports 99.0.0 "
            f"and the project expects {expected}"
        )
        output = support.output_of(result)
        assert "99.0.0" in output and expected in output, (
            f"the check does not name the installed (99.0.0) and the expected "
            f"({expected}) version: {output}"
        )

    @needs_rulesync
    def test_gov_check_is_red_when_the_version_cannot_be_read(self, generated_project, sandbox):
        (generated_project / support.TOOL_REGISTRY_REL).unlink()
        entry, family, run = _gov_check(generated_project, sandbox)
        assert (entry.get("status"), family.get("status")) == (support.RED, support.RED), (
            f"the project records no expected rulesync version, but gov check shows the "
            f"check as {entry.get('status')!r} and the family as {family.get('status')!r}\n"
            f"{run.describe()}"
        )


# ===================================================================
# KPI Success 3 — "generated adapters match their source": the kernel
# is the authority of roles and skills, the rulesync sources derive
# from it (DEC-066, W1-33, W1-35)
# ===================================================================

class TestKernelAgainstAdapterSource:
    """A kernel role or skill changed without its rulesync source, or the
    reverse, makes the check not green. rulesync's own comparison stays
    clean in all four cases, so only this comparison can find it.

    Compared by the check: ``governance/kernel/roles/<role>.md`` with
    ``.rulesync/subagents/<role>.md``, and
    ``governance/kernel/skills/<skill>/SKILL.md`` with
    ``.rulesync/skills/<skill>/SKILL.md``. The finding names the rulesync
    source (the derived file) and no file outside that pair."""

    ROLE_KERNEL = f"{support.PROJECT_KERNEL_REL}/roles/{KERNEL_ROLE}.md"
    ROLE_SOURCE = f".rulesync/subagents/{KERNEL_ROLE}.md"
    SKILL_KERNEL = f"{support.PROJECT_KERNEL_REL}/skills/{KERNEL_SKILL}/SKILL.md"
    SKILL_SOURCE = f".rulesync/skills/{KERNEL_SKILL}/SKILL.md"

    def _assert_found(self, project, sandbox, kernel, source, what):
        entry, family, run = _gov_check(project, sandbox)
        assert (entry.get("status"), family.get("status")) == (support.RED, support.RED), (
            f"{what}, but gov check shows the check as {entry.get('status')!r} and the "
            f"family as {family.get('status')!r}\n{run.describe()}"
        )
        named = support.named_files(project, json.dumps(entry.get("findings")))
        assert source in named and named <= {source, kernel}, (
            f"{what}: the findings must name {source} and no file outside the pair "
            f"({kernel}); they name {sorted(named)}"
        )

    @needs_rulesync
    def test_kernel_role_changed_without_its_source(self, generated_project, sandbox):
        support.change_first_labelled_field(generated_project / self.ROLE_KERNEL)
        self._assert_found(generated_project, sandbox, self.ROLE_KERNEL, self.ROLE_SOURCE,
                           "a kernel role file was changed without its rulesync source")

    @needs_rulesync
    def test_role_source_changed_without_its_kernel_role(self, generated_project, sandbox):
        support.change_first_labelled_field(generated_project / self.ROLE_SOURCE)
        support.regenerate(generated_project)
        self._assert_found(generated_project, sandbox, self.ROLE_KERNEL, self.ROLE_SOURCE,
                           "a role's rulesync source was changed without its kernel role file")

    @needs_rulesync
    def test_kernel_skill_changed_without_its_source(self, generated_project, sandbox):
        support.append_line(generated_project / self.SKILL_KERNEL)
        self._assert_found(generated_project, sandbox, self.SKILL_KERNEL, self.SKILL_SOURCE,
                           "a kernel skill file was changed without its rulesync source")

    @needs_rulesync
    def test_skill_source_changed_without_its_kernel_skill(self, generated_project, sandbox):
        support.append_line(generated_project / self.SKILL_SOURCE)
        support.regenerate(generated_project)
        self._assert_found(generated_project, sandbox, self.SKILL_KERNEL, self.SKILL_SOURCE,
                           "a skill's rulesync source was changed without its kernel skill file")


# ===================================================================
# KPI Failure 1 — generate --delete must NOT remove OpenSpec or
# vendored skills
# ===================================================================

class TestDeleteProtection:
    """--delete must not remove OpenSpec commands or vendored skills."""

    @needs_rulesync
    def test_delete_preserves_openspec_commands(self, generated_project, openspec_shipped):
        """After ``--delete`` every command OpenSpec ships is still there
        with OpenSpec's body."""
        delete = support.run_rulesync_delete(generated_project)
        assert delete.returncode == 0, f"--delete failed: {delete.stderr}"

        lost = []
        for name, shipped in sorted(openspec_shipped.items()):
            path = generated_project / support.OPSX_REL / f"{name}.md"
            if not path.is_file() or (
                support.generated_body(path.read_text(encoding="utf-8"))
                != support.generated_body(shipped)
            ):
                lost.append(name)
        assert not lost, (
            f"after generate --delete these OpenSpec commands are missing from "
            f"{support.OPSX_REL}/ or no longer OpenSpec's: {lost}"
        )

    @needs_rulesync
    def test_delete_preserves_vendored_skills(self, project):
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"

        skills_dir = project / ".claude" / "skills"
        for skill_name in support.SUPERPOWERS_SKILLS:
            skill_md = skills_dir / skill_name / "SKILL.md"
            assert skill_md.is_file(), (
                f"vendored skill {skill_name} not generated before --delete"
            )

        delete = support.run_rulesync_delete(project)
        assert delete.returncode == 0, f"--delete failed: {delete.stderr}"

        for skill_name in support.SUPERPOWERS_SKILLS:
            assert (skills_dir / skill_name / "SKILL.md").is_file(), (
                f"vendored skill {skill_name} removed by --delete"
            )


# ===================================================================
# KPI Failure 2 — hand-edited generated file detected
# ===================================================================

class TestHandEditDetected:
    """``rulesync generate --check`` (the CI step) detects a hand edit."""

    @needs_rulesync
    def test_hand_edit_claude_md(self, generated_project):
        path = generated_project / "CLAUDE.md"
        assert path.is_file()
        path.write_text("# hand-edited\n", encoding="utf-8")
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            "--check should fail after hand-editing CLAUDE.md"
        )

    @needs_rulesync
    def test_hand_edit_agents_md(self, generated_project):
        path = generated_project / "AGENTS.md"
        assert path.is_file()
        path.write_text("# hand-edited\n", encoding="utf-8")
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            "--check should fail after hand-editing AGENTS.md"
        )

    @needs_rulesync
    def test_hand_edit_role_file(self, generated_project):
        agents_dir = generated_project / ".claude" / "agents"
        assert agents_dir.is_dir(), ".claude/agents/ not generated"
        role_files = sorted(agents_dir.glob("*.md"))
        assert role_files, ".claude/agents/ has no .md files"
        role_files[0].write_text("# hand-edited role\n", encoding="utf-8")
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            f"--check should fail after hand-editing {role_files[0].name}"
        )

    @needs_rulesync
    def test_hand_edit_skill_file(self, generated_project):
        skills_dir = generated_project / ".claude" / "skills"
        assert skills_dir.is_dir(), ".claude/skills/ not generated"
        skill_md = None
        for d in sorted(skills_dir.iterdir()):
            candidate = d / "SKILL.md"
            if candidate.is_file():
                skill_md = candidate
                break
        assert skill_md is not None, "no SKILL.md found in .claude/skills/"
        skill_md.write_text("# hand-edited skill\n", encoding="utf-8")
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            f"--check should fail after hand-editing {skill_md.parent.name}/SKILL.md"
        )


# ===================================================================
# KPI Failure 2 — the check's findings after a hand edit
# ===================================================================

class TestFindings:
    """After one hand edit the findings of the check, as ``gov check``
    reports them, name that file and nothing else."""

    @needs_rulesync
    @pytest.mark.parametrize("rel", HAND_EDITED)
    def test_findings_name_exactly_the_edited_file(self, generated_project, sandbox, rel):
        _hand_edit(generated_project, rel)
        entry, _family, run = _gov_check(generated_project, sandbox)
        named = support.named_files(generated_project, json.dumps(entry.get("findings")))
        assert named == {rel}, (
            f"{rel} was edited by hand; the findings name {sorted(named)}\n{run.describe()}"
        )

    @needs_rulesync
    def test_one_hand_edit_is_one_finding(self, generated_project, sandbox):
        _hand_edit(generated_project, "AGENTS.md")
        entry, _family, run = _gov_check(generated_project, sandbox)
        findings = entry.get("findings")
        assert isinstance(findings, list) and len(findings) == 1, (
            f"one file was edited by hand; the check reports "
            f"{len(findings) if isinstance(findings, list) else findings!r} findings\n"
            f"{run.describe()}"
        )

    @needs_rulesync
    def test_rulesync_failure_without_a_file_is_reported_with_its_reason(
        self, generated_project, mock_dir,
    ):
        """rulesync fails and names no file: the check fails with rulesync's
        own reason and names no file of the project."""
        failing = support.write_mock_rulesync(mock_dir, (
            'if [[ "$1" == "--version" ]]; then exec "$REAL" --version; fi\n'
            f'echo "{RULESYNC_REASON}" >&2\n'
            'exit 1'
        ))
        result = support.run_portability_check(
            generated_project, env_override={"RULESYNC_BIN": str(failing)},
        )
        assert result.returncode != 0, (
            "the check is green although rulesync failed"
        )
        output = support.output_of(result)
        assert RULESYNC_REASON in output, (
            f"the check does not report rulesync's reason ({RULESYNC_REASON!r}): {output}"
        )
        named = support.named_files(generated_project, output)
        assert not named, (
            f"rulesync named no file, but the check names {sorted(named)}: "
            f"a finding was guessed, not measured"
        )


# ===================================================================
# A generated file that is missing
# ===================================================================

class TestMissingFileDetected:
    """Deleting a generated file is detected by --check and by the check."""

    @needs_rulesync
    def test_missing_agents_md_fails_check(self, generated_project):
        agents_md = generated_project / "AGENTS.md"
        assert agents_md.is_file()
        agents_md.unlink()
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            "--check should fail when AGENTS.md is deleted, not silently pass"
        )

    @needs_rulesync
    def test_portability_check_fails_on_missing_agents_md(self, generated_project):
        """The AGENTS.md target is compared even when its file is gone."""
        (generated_project / "AGENTS.md").unlink()
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            "the check is green although AGENTS.md is deleted: "
            "the AGENTS.md target was not compared"
        )
        assert "AGENTS.md" in support.output_of(result), (
            f"the check does not name the missing AGENTS.md: {support.output_of(result)}"
        )


# ===================================================================
# Source change without regeneration detected
# ===================================================================

class TestSourceChangeDetected:
    """Changing a source without regenerating is detected by --check."""

    @needs_rulesync
    def test_source_change_fails_check(self, generated_project):
        rules_dir = generated_project / ".rulesync" / "rules"
        rule_files = sorted(rules_dir.glob("*.md"))
        assert rule_files, ".rulesync/rules/ has no .md files"
        original = rule_files[0].read_text(encoding="utf-8")
        rule_files[0].write_text(
            original + "\n\nAdded line to trigger staleness.\n",
            encoding="utf-8",
        )
        check = support.run_rulesync_check(generated_project)
        assert check.returncode != 0, (
            "--check should fail after modifying a source file without regenerating"
        )


# ===================================================================
# The absent tool and the time limit (DEC-425)
# ===================================================================

class TestToolAbsentOrHanging:
    """An unmeasured result is never green."""

    @needs_rulesync
    def test_rulesync_absent_not_green(self, generated_project):
        """Measures: with no rulesync anywhere, the check is not green and says so."""
        env = {
            "PATH": "/usr/bin:/bin",
            "RULESYNC_BIN": "/nonexistent/rulesync",
        }
        result = support.run_portability_check(generated_project, env_override=env)
        assert result.returncode != 0, (
            "portability check must not be GREEN when rulesync is absent (DEC-425)"
        )
        output = support.output_of(result).lower()
        assert "not found" in output or "missing" in output or "absent" in output, (
            f"check should mention that rulesync was not found, "
            f"got: {support.output_of(result)}"
        )

    @needs_rulesync
    def test_rulesync_bin_missing_file(self, generated_project):
        """Measures: a named rulesync path that holds no file is not green and says so."""
        result = support.run_portability_check(
            generated_project,
            env_override={"RULESYNC_BIN": "/tmp/no-such-rulesync-binary"},
        )
        assert result.returncode != 0, (
            "portability check must fail when RULESYNC_BIN points at a missing file"
        )
        output = support.output_of(result).lower()
        assert "not found" in output or "missing" in output, (
            f"check should say 'rulesync not found', "
            f"got: {support.output_of(result)}"
        )

    @needs_rulesync
    def test_timeout_handling(self, generated_project, mock_dir):
        """Measures: a rulesync that never answers ends the check, not green,
        within the check's own time limit (no traceback, no endless wait)."""
        mock = support.write_mock_rulesync(mock_dir, "sleep 3600")
        try:
            result = support.run_portability_check(
                generated_project,
                env_override={"RULESYNC_BIN": str(mock)},
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            pytest.fail(
                "portability check did not handle a hanging rulesync binary: "
                "subprocess.TimeoutExpired raised instead of a graceful error"
            )
        assert result.returncode != 0, (
            "portability check must not be GREEN when rulesync hangs"
        )
