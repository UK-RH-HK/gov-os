"""Tests for all four skills: form, versioning, token limit, authority (S3, S4).

S3: Each skill versioned, body <= 2,500 tokens [CAP-24.b].
S4: No skill grants a permission or states a rule as its own authority;
    a skill is a method, holds no tool permissions, and cites the policy
    or decision it follows [CAP-24.b].

Parametrised over the four skills via the ``skill`` fixture (conftest.py),
so each test function produces four cases — one per skill.
"""
from w1_36_support import ROLE_ONLY_KEYS, SOURCE_PATTERN, TOKEN_LIMIT, token_count


class TestSkillFrontmatter:
    """S3: each skill has name, description and version in frontmatter."""

    def test_has_name_in_frontmatter(self, skill):
        fm = skill["frontmatter"]
        assert "name" in fm, \
            f"{skill['skill_name']} skill must have 'name' in frontmatter"
        assert isinstance(fm["name"], str) and fm["name"].strip(), \
            f"{skill['skill_name']} skill 'name' must be a non-empty string"

    def test_has_description_in_frontmatter(self, skill):
        fm = skill["frontmatter"]
        assert "description" in fm, \
            f"{skill['skill_name']} skill must have 'description' in frontmatter"
        assert isinstance(fm["description"], str) and fm["description"].strip(), \
            f"{skill['skill_name']} skill 'description' must be a non-empty string"

    def test_has_version_in_frontmatter(self, skill):
        fm = skill["frontmatter"]
        assert "version" in fm, \
            f"{skill['skill_name']} skill must have 'version' in frontmatter"


class TestSkillTokenLimit:
    """S3: body <= 2,500 tokens."""

    def test_body_at_most_2500_tokens(self, skill):
        tokens = token_count(skill["body"])
        assert tokens <= TOKEN_LIMIT, (
            f"{skill['skill_name']} skill body is {tokens} tokens, "
            f"limit is {TOKEN_LIMIT}"
        )


class TestSkillAuthority:
    """S4: no skill grants permissions; each cites governing sources."""

    def test_no_permission_keys_in_frontmatter(self, skill):
        fm_keys = set(skill["frontmatter"].keys())
        found = ROLE_ONLY_KEYS & fm_keys
        assert not found, (
            f"{skill['skill_name']} skill frontmatter has role-only keys "
            f"{found}; a skill is a method and holds no tool permissions "
            f"(CAP-24.b)"
        )

    def test_cites_at_least_one_governing_source(self, skill):
        matches = SOURCE_PATTERN.findall(skill["body"])
        assert matches, (
            f"{skill['skill_name']} skill body must cite at least one "
            f"DEC, CAP or MR source"
        )
