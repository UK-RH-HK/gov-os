"""W1-38 — rulesync adapters and .claude ownership.

Tests for ticket DAEO-3ef2 (profile STANDARD). Each test builds a temporary
project under pytest's ``tmp_path``, populates a ``.rulesync/`` source tree,
runs ``rulesync generate``, and asserts the output.

Nothing is run in this worktree. No file in this worktree is read as an
assertion target — only the generated files in the temporary project.
"""

from __future__ import annotations

import json

import pytest

import w1_38_support as support


# ---------------------------------------------------------------------------
# Success 1: rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens)
# and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and
# vendored skills are registered sources [CAP-52.a, CAP-52.b]
# ---------------------------------------------------------------------------

class TestSuccess1Generation:
    """Success 1: generation produces CLAUDE.md, AGENTS.md and .claude/."""

    def test_generate_produces_claude_md(self, project, rulesync_version):
        """CLAUDE.md exists at the project root after ``rulesync generate``."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        claude_md = project / "CLAUDE.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        content = claude_md.read_text(encoding="utf-8")
        assert len(content) > 0, "CLAUDE.md is empty"

    def test_generate_produces_agents_md_within_token_limit(self, project, rulesync_version):
        """AGENTS.md exists and is <= 1500 tokens (ceiling(chars/4))."""
        result = support.run_rulesync_generate(project, targets="claudecode,agentsmd")
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        agents_md = project / "AGENTS.md"
        assert agents_md.is_file(), "AGENTS.md was not generated"
        content = agents_md.read_text(encoding="utf-8")
        tokens = support._tokens(content)
        assert tokens <= support.AGENTS_MD_TOKEN_LIMIT, (
            f"AGENTS.md is {tokens} tokens (ceiling(chars/4)); "
            f"limit is {support.AGENTS_MD_TOKEN_LIMIT}"
        )

    def test_generate_produces_settings_with_hooks(self, project, rulesync_version):
        """.claude/settings.json contains hooks from the source tree."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        settings = support.load_generated_settings(project)
        hooks = settings.get("hooks", {})
        assert hooks, ".claude/settings.json has no hooks"
        events = set(hooks.keys())
        assert "PreToolUse" in events, (
            f"PreToolUse hook not found in settings; events: {sorted(events)}"
        )
        assert "PostToolUse" in events, (
            f"PostToolUse hook not found in settings; events: {sorted(events)}"
        )

    def test_generate_produces_settings_with_deny_rules(self, project, rulesync_version):
        """.claude/settings.json contains deny rules from permissions.jsonc."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        settings = support.load_generated_settings(project)
        permissions = settings.get("permissions", {})
        deny = permissions.get("deny", [])
        assert deny, ".claude/settings.json has no deny rules under permissions.deny"

    def test_generate_produces_role_agents(self, project, rulesync_version):
        """.claude/agents/ contains role definition files."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        agents_dir = project / ".claude" / "agents"
        assert agents_dir.is_dir(), ".claude/agents/ was not generated"
        agent_files = sorted(p.name for p in agents_dir.glob("*.md"))
        assert agent_files, ".claude/agents/ has no .md files"
        assert "engineer.md" in agent_files, (
            f"engineer.md not found in .claude/agents/; files: {agent_files}"
        )

    def test_generate_produces_skills(self, project, rulesync_version):
        """.claude/skills/ exists and has generated skill content."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        skills_dir = project / ".claude" / "skills"
        assert skills_dir.is_dir(), ".claude/skills/ was not generated"
        skill_dirs = [p.name for p in skills_dir.iterdir() if p.is_dir()]
        assert skill_dirs, ".claude/skills/ has no skill directories"

    def test_openspec_commands_are_registered(
            self, project_with_openspec_and_vendored, rulesync_version):
        """OpenSpec commands appear as generated Claude Code commands (DEC-074 Q7)."""
        project = project_with_openspec_and_vendored
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        commands_dir = project / ".claude" / "commands"
        assert commands_dir.is_dir(), (
            ".claude/commands/ was not generated; OpenSpec commands are not registered"
        )
        cmd_files = sorted(p.name for p in commands_dir.glob("*.md"))
        assert cmd_files, ".claude/commands/ has no .md files"

    def test_vendored_skills_are_registered(
            self, project_with_openspec_and_vendored, rulesync_version):
        """The three vendored superpowers skills are generated (DEC-074 Q7)."""
        project = project_with_openspec_and_vendored
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        skills_dir = project / ".claude" / "skills"
        assert skills_dir.is_dir(), ".claude/skills/ was not generated"
        skill_dirs = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
        for skill_name in support.SUPERPOWERS_SKILLS:
            assert skill_name in skill_dirs, (
                f"vendored skill {skill_name} not found under .claude/skills/; "
                f"found: {skill_dirs}"
            )


# ---------------------------------------------------------------------------
# Success 2: Hook-script stubs referenced by generated settings exist;
# rulesync generate --check is clean in CI
# ---------------------------------------------------------------------------

class TestSuccess2HooksAndCheck:
    """Success 2: hook stubs exist and --check is clean."""

    def test_hook_script_stubs_exist(self, project, rulesync_version):
        """Every command path in the generated settings resolves to a file."""
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        settings = support.load_generated_settings(project)
        commands = support.extract_hook_commands(settings)
        assert commands, "no hook commands found in generated settings"
        missing = []
        for cmd_path in commands:
            resolved = project / cmd_path.lstrip("./")
            if not resolved.is_file():
                missing.append(cmd_path)
        assert missing == [], (
            f"hook scripts referenced in .claude/settings.json do not exist: {missing}"
        )

    def test_generate_check_is_clean(self, project, rulesync_version):
        """``rulesync generate --check`` exits 0 after a clean generation."""
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        check = support.run_rulesync_generate_check(project)
        assert check.returncode == 0, (
            f"rulesync generate --check failed (exit {check.returncode}): "
            f"generated files differ from source.\n{check.stderr}"
        )

    def test_generate_check_fails_when_stale(self, project, rulesync_version):
        """``rulesync generate --check`` exits non-zero when a generated file is stale."""
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        claude_md = project / "CLAUDE.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        claude_md.write_text("# hand-edited\n", encoding="utf-8")
        check = support.run_rulesync_generate_check(project)
        assert check.returncode != 0, (
            "rulesync generate --check should fail after hand-editing CLAUDE.md"
        )


# ---------------------------------------------------------------------------
# Success 3: Registers the adapter/model-portability family check: generated
# adapters match their source for Claude Code and AGENTS.md [CAP-38.b]
# ---------------------------------------------------------------------------

class TestSuccess3PortabilityCheck:
    """Success 3: the adapter/model-portability check."""

    def test_check_declaration_exists(self):
        """A YAML file at template/governance/kernel/checks/adapter-portability*.yaml exists."""
        checks_dir = support.REPO_ROOT / support.KERNEL_CHECKS_REL
        assert checks_dir.is_dir(), f"{support.KERNEL_CHECKS_REL}/ does not exist"
        decl = support.find_adapter_portability_check(checks_dir)
        assert decl is not None, (
            f"no adapter-portability check declaration found under "
            f"{support.KERNEL_CHECKS_REL}/; W1-38 has not registered the "
            f"adapter/model portability family check"
        )

    def test_check_declaration_fields(self):
        """The check declaration has the required 5 fields."""
        checks_dir = support.REPO_ROOT / support.KERNEL_CHECKS_REL
        decl = support.find_adapter_portability_check(checks_dir)
        assert decl is not None, "no adapter-portability check declaration"
        required = {"id", "family", "tier", "severity", "command"}
        missing = required - set(decl.keys())
        assert missing == set(), (
            f"adapter-portability check declaration missing fields: {sorted(missing)}"
        )
        assert (support.normalise_family(decl["family"])
                == support.PORTABILITY_FAMILY_NORMALISED), (
            f"check family normalises to "
            f"{support.normalise_family(decl['family'])!r}, "
            f"expected {support.PORTABILITY_FAMILY_NORMALISED!r}"
        )

    def test_check_command_module_exists(self):
        """The check command module at src/gov/adapters/ exists."""
        assert support.portability_module_exists(), (
            "src/gov/adapters/ portability module does not exist: "
            "W1-38 has not created the portability check"
        )

    def test_portability_check_green_when_matching(self, project, rulesync_version):
        """When generated files match source: GREEN, no findings."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        result = support.run_rulesync_generate(project)
        assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
        check = support.run_portability_check(project)
        assert check.returncode == 0, (
            f"portability check should be GREEN when files match source, "
            f"but exited {check.returncode}.\n"
            f"stdout: {check.stdout}\nstderr: {check.stderr}"
        )
        if check.stdout.strip():
            data = json.loads(check.stdout)
            findings = data if isinstance(data, list) else data.get("findings", [])
            assert findings == [], (
                f"expected no findings when files match, got: {findings}"
            )

    def test_portability_check_fails_when_file_hand_edited(
            self, project, rulesync_version):
        """When a generated file is hand-edited: findings naming the file."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        claude_md = project / "CLAUDE.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        claude_md.write_text("# hand-edited content\n", encoding="utf-8")
        check = support.run_portability_check(project)
        assert check.returncode != 0, (
            "portability check should fail when a generated file is hand-edited"
        )
        output = check.stdout.strip()
        assert output, "portability check produced no output on failure"
        assert "CLAUDE.md" in output, (
            f"portability check findings should name the edited file "
            f"(CLAUDE.md), got: {output}"
        )

    def test_portability_check_fails_when_file_missing(
            self, project, rulesync_version):
        """When a generated file is missing: failure naming the missing file."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        claude_md = project / "CLAUDE.md"
        assert claude_md.is_file(), "CLAUDE.md was not generated"
        claude_md.unlink()
        check = support.run_portability_check(project)
        assert check.returncode != 0, (
            "portability check should fail when a generated file is missing"
        )

    def test_portability_check_unmeasured_when_rulesync_absent(
            self, project, rulesync_version):
        """When rulesync is absent: unmeasured, never green (DEC-425)."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0
        env = {"PATH": "/usr/bin:/bin", "RULESYNC_BIN": "/nonexistent/rulesync"}
        check = support.run_portability_check(project, env_override=env)
        assert check.returncode != 0, (
            "portability check must not be GREEN when rulesync is absent"
        )

    def test_portability_check_fails_when_rulesync_wrong_version(
            self, project, rulesync_version):
        """When rulesync is of another version: failure with the reason."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0
        env = {"RULESYNC_EXPECTED_VERSION": "99.99.99"}
        check = support.run_portability_check(project, env_override=env)
        assert check.returncode != 0, (
            "portability check must not be GREEN when rulesync version is wrong"
        )
        output = (check.stdout + check.stderr).strip()
        assert "version" in output.lower(), (
            f"portability check should mention version in its failure reason, "
            f"got: {output}"
        )

    def test_portability_check_fails_when_source_empty(
            self, tmp_path, rulesync_version):
        """When the source folder is empty: never green."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        support.init_git(tmp_path)
        (tmp_path / ".rulesync").mkdir()
        check = support.run_portability_check(tmp_path)
        assert check.returncode != 0, (
            "portability check must not be GREEN when the source folder is empty"
        )


# ---------------------------------------------------------------------------
# Failure 1: generate --delete removes OpenSpec or vendored skills
# ---------------------------------------------------------------------------

class TestFailure1DeleteProtection:
    """Failure 1: --delete must not remove OpenSpec commands or vendored skills."""

    def test_delete_preserves_openspec_commands(
            self, project_with_openspec_and_vendored, rulesync_version):
        """Running ``rulesync generate --delete`` keeps OpenSpec command files."""
        project = project_with_openspec_and_vendored
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        commands_dir = project / ".claude" / "commands"
        pre_files = (sorted(p.name for p in commands_dir.glob("*.md"))
                     if commands_dir.is_dir() else [])
        assert pre_files, ".claude/commands/ is empty before --delete"
        delete = support.run_rulesync_generate_delete(project)
        assert delete.returncode == 0, (
            f"rulesync generate --delete failed: {delete.stderr}"
        )
        post_files = (sorted(p.name for p in commands_dir.glob("*.md"))
                      if commands_dir.is_dir() else [])
        assert post_files, (
            ".claude/commands/ is empty after --delete: "
            "OpenSpec commands were removed"
        )
        missing = set(pre_files) - set(post_files)
        assert missing == set(), (
            f"OpenSpec command files removed by --delete: {sorted(missing)}"
        )

    def test_delete_preserves_vendored_skills(
            self, project_with_openspec_and_vendored, rulesync_version):
        """Running ``rulesync generate --delete`` keeps the three vendored skills."""
        project = project_with_openspec_and_vendored
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        skills_dir = project / ".claude" / "skills"
        pre_content = {}
        for skill_name in support.SUPERPOWERS_SKILLS:
            skill_md = skills_dir / skill_name / "SKILL.md"
            assert skill_md.is_file(), (
                f".claude/skills/{skill_name}/SKILL.md missing before --delete"
            )
            pre_content[skill_name] = skill_md.read_bytes()
        delete = support.run_rulesync_generate_delete(project)
        assert delete.returncode == 0, (
            f"rulesync generate --delete failed: {delete.stderr}"
        )
        for skill_name in support.SUPERPOWERS_SKILLS:
            skill_md = skills_dir / skill_name / "SKILL.md"
            assert skill_md.is_file(), (
                f".claude/skills/{skill_name}/SKILL.md removed by --delete"
            )
            assert skill_md.read_bytes() == pre_content[skill_name], (
                f".claude/skills/{skill_name}/SKILL.md changed by --delete"
            )


# ---------------------------------------------------------------------------
# Failure 2: A generated file is hand-edited
# (Also covered by Success 3 portability tests and Success 2 --check test)
# ---------------------------------------------------------------------------

class TestFailure2HandEdited:
    """Failure 2: the portability check detects hand-edited generated files."""

    def test_agents_md_hand_edited_is_detected(self, project, rulesync_version):
        """Hand-editing AGENTS.md is detected by the portability check."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project, targets="claudecode,agentsmd")
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        agents_md = project / "AGENTS.md"
        assert agents_md.is_file(), "AGENTS.md was not generated"
        agents_md.write_text("# hand-edited AGENTS.md\n", encoding="utf-8")
        check = support.run_portability_check(project)
        assert check.returncode != 0, (
            "portability check should fail when AGENTS.md is hand-edited"
        )

    def test_settings_hand_edited_is_detected(self, project, rulesync_version):
        """Hand-editing .claude/settings.json is detected by the portability check."""
        assert support.portability_module_exists(), (
            "portability module does not exist"
        )
        gen = support.run_rulesync_generate(project)
        assert gen.returncode == 0, f"rulesync generate failed: {gen.stderr}"
        settings_path = project / ".claude" / "settings.json"
        assert settings_path.is_file(), ".claude/settings.json was not generated"
        settings_path.write_text('{"hand": "edited"}', encoding="utf-8")
        check = support.run_portability_check(project)
        assert check.returncode != 0, (
            "portability check should fail when .claude/settings.json is hand-edited"
        )


# ---------------------------------------------------------------------------
# Source tree structure: the .rulesync/ directories exist in this project
# ---------------------------------------------------------------------------

class TestSourceTreeStructure:
    """The .rulesync/ source tree exists in the project and template."""

    def test_template_rulesync_dir_exists(self):
        """template/.rulesync/ exists with the kernel sources."""
        template_rs = support.REPO_ROOT / "template" / ".rulesync"
        assert template_rs.is_dir(), (
            "template/.rulesync/ does not exist: "
            "W1-38 has not created the template source tree"
        )

    def test_project_rulesync_dir_exists(self):
        """.rulesync/ exists at the project root."""
        project_rs = support.REPO_ROOT / ".rulesync"
        assert project_rs.is_dir(), (
            ".rulesync/ does not exist: "
            "W1-38 has not created the project source tree"
        )

    def test_template_rulesync_has_hooks(self):
        """template/.rulesync/hooks.jsonc exists."""
        hooks = support.REPO_ROOT / "template" / ".rulesync" / "hooks.jsonc"
        assert hooks.is_file(), "template/.rulesync/hooks.jsonc does not exist"

    def test_template_rulesync_has_permissions(self):
        """template/.rulesync/permissions.jsonc exists."""
        perms = support.REPO_ROOT / "template" / ".rulesync" / "permissions.jsonc"
        assert perms.is_file(), (
            "template/.rulesync/permissions.jsonc does not exist"
        )

    def test_template_rulesync_has_rules(self):
        """template/.rulesync/rules/ exists with at least one rule."""
        rules = support.REPO_ROOT / "template" / ".rulesync" / "rules"
        assert rules.is_dir(), "template/.rulesync/rules/ does not exist"
        md_files = list(rules.glob("*.md"))
        assert md_files, "template/.rulesync/rules/ has no .md files"

    def test_template_rulesync_has_subagents(self):
        """template/.rulesync/subagents/ exists with role definitions."""
        subagents = support.REPO_ROOT / "template" / ".rulesync" / "subagents"
        assert subagents.is_dir(), (
            "template/.rulesync/subagents/ does not exist"
        )
        md_files = sorted(p.stem for p in subagents.glob("*.md"))
        for role_name in support.ROLE_NAMES:
            assert role_name in md_files, (
                f"template/.rulesync/subagents/{role_name}.md does not exist; "
                f"found: {md_files}"
            )

    def test_template_rulesync_has_skills(self):
        """template/.rulesync/skills/ exists with kernel skill sources."""
        skills = support.REPO_ROOT / "template" / ".rulesync" / "skills"
        assert skills.is_dir(), "template/.rulesync/skills/ does not exist"
        skill_dirs = sorted(p.name for p in skills.iterdir() if p.is_dir())
        assert skill_dirs, "template/.rulesync/skills/ has no skill directories"

    def test_template_rulesync_has_commands(self):
        """template/.rulesync/commands/ exists with OpenSpec command sources."""
        commands = support.REPO_ROOT / "template" / ".rulesync" / "commands"
        assert commands.is_dir(), (
            "template/.rulesync/commands/ does not exist: "
            "OpenSpec commands are not registered as rulesync sources"
        )
        md_files = list(commands.glob("*.md"))
        assert md_files, "template/.rulesync/commands/ has no .md files"
