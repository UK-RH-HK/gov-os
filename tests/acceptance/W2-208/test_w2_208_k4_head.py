"""K4: the head of CLAUDE.md and AGENTS.md in an adopted repository is the brief's head text, generated from the kit's
``.rulesync/rules/governance.md`` at adoption and at update, followed by the nine kernel roles; the old text is gone
(DEC-1217 (7))."""

from __future__ import annotations

import re

import w2_208_support as support


def _after_head(text):
    """The text after the head (whitespace collapsed), or fails naming the first place the head's words part."""
    found, head = support.normalise(text), support.normalise(support.HEAD_TEXT)
    if not found.startswith(head):
        same = next((i for i, (a, b) in enumerate(zip(found, head)) if a != b), min(len(found), len(head)))
        raise AssertionError(f"the text does not begin with the head's words; they part at: {found[same:same + 160]!r}"
                             f" (the head reads: {head[same:same + 160]!r})")
    return text, found[len(head):]


def assert_head(text, what, marker=False):
    """``text`` (a generated block from its ``# Governance`` line, or the head source's body) holds the head as the
    brief writes it, the golden-rule bullets and sections, then the nine roles, and none of the old text."""
    assert text is not None and text.startswith("# Governance"), f"{what} does not begin with `# Governance`"
    _, rest = _after_head(text)
    missing = [bullet for bullet in (*support.GOLDEN_BULLETS, *support.JUDGED_SUBBULLETS) if bullet not in text]
    sections = [name for name in ("## The golden rules", "## How we work", "## Roles") if name not in text]
    assert not missing and not sections, f"{what} lacks golden-rule bullets {missing} or sections {sections}"
    roles = [role for role in support.ROLES if not re.search(rf"\*\*{re.escape(role)}\*\*", rest)]
    assert not roles, f"{what} does not list the roles {roles} after the head"
    old = [item for item in support.OLD_STRINGS if item in text]
    assert not old and not support.GUARD_HEADING.search(text), (
        f"{what} still holds the old text: {old}{' and a Guard section' if support.GUARD_HEADING.search(text) else ''}")
    if marker:
        assert support.B_HEAD_MARKER in text, f"{what} is not release B's head (its marker line is absent)"


def assert_generated(project, what, marker=False):
    blocks = {}
    for rel in support.TEXTS:
        generated = support.block((project / rel).read_text(encoding="utf-8"))
        assert generated is not None, f"{rel} holds no generated block ({what})"
        blocks[rel] = support.head_part(generated)
        assert_head(blocks[rel], f"the generated block of {rel} ({what})", marker)
    assert blocks["CLAUDE.md"] == blocks["AGENTS.md"], f"the two files' blocks differ ({what})"


def test_k4_the_head_source_keeps_its_front_matter_and_holds_the_heads_text_then_the_roles():
    path = support.TEMPLATE / support.HEAD_REL
    front, body = support.split_front(path.read_text(encoding="utf-8"))
    assert front.get("root") is True and {"claudecode", "agentsmd"} <= set(front.get("targets") or []), (
        f"template/{support.HEAD_REL} lost its front matter (root: true, targets claudecode and agentsmd): {front}")
    assert_head(body, f"template/{support.HEAD_REL}")


def test_k4_adoption_generates_the_head_into_both_files_and_keeps_the_projects_own_lines(tmp_path, sandbox):
    project = support.template_project(tmp_path / "product")
    for rel, top in support.OWN_TOP.items():
        support.write(project, rel, top)
    support.w216.commit_all(project, "the project's own CLAUDE.md and AGENTS.md")
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"`gov adapters generate` failed\n{done.describe()}"
    assert_generated(project, "after adoption")
    for rel, top in support.OWN_TOP.items():
        before, _after = support.outside_block((project / rel).read_text(encoding="utf-8"))
        assert before.startswith(top) and not before[len(top):].strip(), (
            f"the project's own lines of {rel} are not byte-identical above the block: {before!r}")


def test_k4_a_project_adopted_by_copier_at_release_b_carries_bs_head(adopted_at_b):
    assert_generated(adopted_at_b, "adopted by copier at B", marker=True)


def test_k4_after_the_update_the_block_is_bs_and_the_projects_own_lines_are_unchanged(updated_013, examin_013):
    done = updated_013["run"]
    assert done.returncode == 0, f"`gov update {support.B} --json` did not exit 0\n{done.describe()}"
    project = updated_013["project"]
    assert_generated(project, "after the update to B", marker=True)
    for rel in support.TEXTS:
        before = support.outside_block((examin_013 / rel).read_text(encoding="utf-8"))
        after = support.outside_block((project / rel).read_text(encoding="utf-8"))
        assert after == before, f"the project's own lines of {rel} outside the block changed: {before!r} -> {after!r}"
