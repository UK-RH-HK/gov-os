"""W1-38 -- rulesync adapters and .claude ownership.

Acceptance tests for ticket DAEO-3ef2 (profile STANDARD). Each test builds a
temporary project under pytest's ``tmp_path``, copies sources from the kernel
template, runs ``rulesync generate``, and asserts the output against the KPI
lines and governing decisions.

Tests are written from the KPIs and decisions, never from the implementation
code in ``src/gov/adapters/`` or ``template/.rulesync/``.
"""

from __future__ import annotations

import subprocess

import pytest

import w1_38_support as support

needs_rulesync = pytest.mark.needs_rulesync


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
    """Every kernel method skill appears in the generated output, body
    byte for byte matching the source SKILL.md."""

    @needs_rulesync
    @pytest.mark.parametrize("skill", support.KERNEL_METHOD_SKILLS)
    def test_skill_body_matches_source(self, generated_project, skill):
        kernel_body = support.read_kernel_skill_body(skill)
        assert kernel_body.strip(), (
            f"kernel skill {support.KERNEL_SKILLS_REL}/{skill}/SKILL.md has no body"
        )

        gen_skill = generated_project / ".claude" / "skills" / skill / "SKILL.md"
        assert gen_skill.is_file(), (
            f".claude/skills/{skill}/SKILL.md was not generated; "
            f"the kernel method skill '{skill}' is missing from the rulesync sources"
        )
        gen_body = support.body(gen_skill.read_text(encoding="utf-8"))
        assert gen_body == kernel_body, (
            f".claude/skills/{skill}/SKILL.md body does not match the kernel "
            f"source byte for byte (kernel {len(kernel_body)} bytes, "
            f"generated {len(gen_body)} bytes)"
        )


# ===================================================================
# KPI Success 1 — vendored skill registration (DEC-244, DEC-074 Q5)
# ===================================================================

class TestVendoredSkillRegistration:
    """The three vendored superpowers skills appear in the generated output."""

    @needs_rulesync
    def test_vendored_skills_present(self, generated_project):
        skills_dir = generated_project / ".claude" / "skills"
        assert skills_dir.is_dir(), ".claude/skills/ was not generated"
        for skill_name in support.SUPERPOWERS_SKILLS:
            skill_md = skills_dir / skill_name / "SKILL.md"
            assert skill_md.is_file(), (
                f"vendored skill '{skill_name}' not found at "
                f".claude/skills/{skill_name}/SKILL.md"
            )


# ===================================================================
# KPI Success 1 — CLAUDE.md and AGENTS.md generated (CAP-52.a)
# ===================================================================

class TestClaudeMdAndAgentsMd:
    """Both CLAUDE.md and AGENTS.md exist after generation and AGENTS.md
    is within the token limit."""

    @needs_rulesync
    def test_both_files_exist(self, generated_project):
        claude_md = generated_project / "CLAUDE.md"
        agents_md = generated_project / "AGENTS.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        assert agents_md.is_file(), "AGENTS.md was not generated"
        assert claude_md.read_text(encoding="utf-8").strip(), "CLAUDE.md is empty"
        assert agents_md.read_text(encoding="utf-8").strip(), "AGENTS.md is empty"

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
# KPI Success 3 — check declaration (CAP-38.b, DEC-438)
# ===================================================================

class TestCheckDeclaration:
    """The adapter-portability family check is registered in the kernel."""

    def test_declaration_file_exists(self):
        path = support.REPO_ROOT / support.CHECK_DECL_REL
        assert path.is_file(), (
            f"{support.CHECK_DECL_REL} does not exist: the adapter/model "
            f"portability family check is not registered"
        )

    def test_declaration_has_required_fields(self):
        decl = support.load_check_declaration()
        assert decl is not None, "check declaration could not be loaded"
        required = {"id", "family", "tier", "severity", "command"}
        missing = required - set(decl.keys())
        assert not missing, (
            f"check declaration missing fields: {sorted(missing)}"
        )

    def test_declaration_family_is_correct(self):
        decl = support.load_check_declaration()
        assert decl is not None, "check declaration could not be loaded"
        assert support.normalise_family(decl.get("family", "")) == support.PORTABILITY_FAMILY_NORMALISED, (
            f"check family normalises to "
            f"{support.normalise_family(decl.get('family', ''))!r}, "
            f"expected {support.PORTABILITY_FAMILY_NORMALISED!r}"
        )

    def test_declaration_command_is_correct(self):
        decl = support.load_check_declaration()
        assert decl is not None, "check declaration could not be loaded"
        assert decl.get("command") == "python3 -m gov.adapters.portability", (
            f"check command is {decl.get('command')!r}, "
            f"expected 'python3 -m gov.adapters.portability'"
        )

    def test_portability_module_exists(self):
        assert support.portability_module_exists(), (
            "src/gov/adapters/portability module does not exist"
        )


# ===================================================================
# KPI Failure 1 — generate --delete must NOT remove OpenSpec or
# vendored skills
# ===================================================================

class TestDeleteProtection:
    """--delete must not remove OpenSpec commands or vendored skills."""

    @needs_rulesync
    def test_delete_preserves_openspec_commands(self, project):
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"

        cmd_names = support.place_openspec_commands(project)
        opsx_dir = project / ".claude" / "commands" / "opsx"
        assert all((opsx_dir / n).is_file() for n in cmd_names)

        delete = support.run_rulesync_delete(project)
        assert delete.returncode == 0, f"--delete failed: {delete.stderr}"

        missing = [n for n in cmd_names if not (opsx_dir / n).is_file()]
        assert not missing, (
            f"OpenSpec command files removed by --delete: {missing}"
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
    """The check detects hand-edited generated files."""

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
# Missing generated file must fail (KPI 11, 18)
# ===================================================================

class TestMissingFileDetected:
    """Deleting a generated file is detected by --check and the
    portability check."""

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
        if not support.portability_module_exists():
            pytest.skip("portability module not yet implemented")
        agents_md = generated_project / "AGENTS.md"
        if agents_md.is_file():
            agents_md.unlink()
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            "portability check must fail when AGENTS.md is deleted, "
            "not silently pass; the agentsmd target must always be checked"
        )


# ===================================================================
# Source change without regeneration detected (KPI 12)
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
# Portability check edge cases (KPI 13-19)
# ===================================================================

class TestPortabilityCheckEdgeCases:
    """Edge cases for the adapter/model-portability check."""

    def _require_portability(self):
        if not support.portability_module_exists():
            pytest.skip("portability module not yet implemented")

    @needs_rulesync
    def test_rulesync_absent_not_green(self, generated_project):
        """DEC-425: unmeasured is never green."""
        self._require_portability()
        env = {
            "PATH": "/usr/bin:/bin",
            "RULESYNC_BIN": "/nonexistent/rulesync",
        }
        result = support.run_portability_check(generated_project, env_override=env)
        assert result.returncode != 0, (
            "portability check must not be GREEN when rulesync is absent (DEC-425)"
        )
        output = (result.stdout + result.stderr).lower()
        assert "not found" in output or "missing" in output or "absent" in output, (
            f"check should mention that rulesync was not found, "
            f"got: {result.stdout + result.stderr}"
        )

    @needs_rulesync
    def test_rulesync_bin_missing_file(self, generated_project):
        """RULESYNC_BIN pointing at a missing file: reported as 'not found'."""
        self._require_portability()
        result = support.run_portability_check(
            generated_project,
            env_override={"RULESYNC_BIN": "/tmp/no-such-rulesync-binary"},
        )
        assert result.returncode != 0, (
            "portability check must fail when RULESYNC_BIN points at a missing file"
        )
        output = (result.stdout + result.stderr).lower()
        assert "not found" in output or "missing" in output, (
            f"check should say 'rulesync not found', "
            f"got: {result.stdout + result.stderr}"
        )

    @needs_rulesync
    def test_version_from_project_pin_not_env(self, generated_project):
        """The expected version comes from the project's registered pin,
        not from RULESYNC_EXPECTED_VERSION."""
        self._require_portability()
        support.write_rulesync_config(
            generated_project, version=support.RULESYNC_VERSION,
        )
        mock = support.write_mock_rulesync(generated_project, (
            'if [[ "$1" == "--version" ]]; then echo "99.0.0"; exit 0; fi\n'
            'if [[ "$*" == *"--check"* ]]; then exit 0; fi\n'
            'exit 0'
        ))
        result = support.run_portability_check(
            generated_project,
            env_override={
                "RULESYNC_BIN": str(mock),
                "RULESYNC_EXPECTED_VERSION": "",
            },
        )
        assert result.returncode != 0, (
            "portability check must validate the rulesync version against the "
            "project's registered pin (24.0.0 in rulesync.jsonc), not skip "
            "validation when RULESYNC_EXPECTED_VERSION is unset. "
            "A mock reporting 99.0.0 should fail against expected 24.0.0."
        )
        output = (result.stdout + result.stderr).lower()
        assert "version" in output, (
            f"check should mention version in its failure, "
            f"got: {result.stdout + result.stderr}"
        )

    @needs_rulesync
    def test_timeout_handling(self, generated_project):
        """A hanging rulesync does not cause an unhandled exception."""
        self._require_portability()
        mock = support.write_mock_rulesync(generated_project, "sleep 3600")
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

    @needs_rulesync
    def test_agents_md_always_checked(self, generated_project):
        """The agentsmd target is always checked even when AGENTS.md is
        deleted; targets come from the project's rulesync configuration."""
        self._require_portability()
        agents_md = generated_project / "AGENTS.md"
        if agents_md.is_file():
            agents_md.unlink()
        result = support.run_portability_check(generated_project)
        assert result.returncode != 0, (
            "portability check must not pass when AGENTS.md is missing; "
            "the agentsmd target must always be included, "
            "read from the project's rulesync configuration"
        )

    @needs_rulesync
    def test_no_invented_findings(self, generated_project):
        """When --check fails with no recognisable file names, the check
        reports what rulesync said verbatim, not invented file names."""
        self._require_portability()
        mock = support.write_mock_rulesync(generated_project, (
            'if [[ "$*" == *"--check"* ]]; then\n'
            '    echo "xyzzy_no_recognisable_filename_here" >&2\n'
            '    exit 1\n'
            'fi\n'
            'if [[ "$1" == "--version" ]]; then echo "24.0.0"; exit 0; fi\n'
            'exit 0'
        ))
        result = support.run_portability_check(
            generated_project,
            env_override={"RULESYNC_BIN": str(mock)},
        )
        assert result.returncode != 0, (
            "portability check should fail when rulesync --check fails"
        )
        combined = result.stdout + result.stderr
        for name in ("CLAUDE.md", "AGENTS.md", "settings.json"):
            assert name not in combined, (
                f"portability check mentioned {name!r} but rulesync only said "
                f"'xyzzy_no_recognisable_filename_here'; the check invented "
                f"a finding instead of reporting what rulesync said"
            )
