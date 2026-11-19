"""W2-188, success 4 and failures 1 and 2 -- the three copies, the four places, the guards.

The base is `5336a6fca` (the skill there: sha256 `16fd341f...0a0`, 74 lines, three byte-equal copies). A hunk is a hunk of
`git diff --unified=0 <base> -- <kernel skill>` (no context lines, so step 6 and the new paragraph, which stand one line
apart, are two hunks, not one).
"""

from __future__ import annotations

import re

import w2_188_support as support


def test_s4_the_base_pin_is_the_sha256_of_the_skill_at_5336a6fca():
    """Guard (holds on the base): the pinned value is the sha256 of `git show 5336a6fca:<kernel skill>`, in all three paths."""
    for rel in support.ALL_REL:
        assert support.sha256_of(support.base_blob(rel)) == support.BASE_SHA256, rel


def test_s4_the_three_copies_are_byte_equal():
    """Guard (holds on the base): it goes red if one copy is edited alone."""
    kernel = support.read_bytes(support.KERNEL_REL)
    differing = [rel for rel in support.COPIES_REL if support.read_bytes(rel) != kernel]
    assert not differing, (f"{' and '.join(differing)} differ from {support.KERNEL_REL} "
                           f"(sha256 {support.sha256_of(kernel)[:12]}...)")


def test_s4_the_copies_carry_a_kernel_skill_changed_from_the_base():
    kernel = support.read_bytes(support.KERNEL_REL)
    assert support.sha256_of(kernel) != support.BASE_SHA256, (
        f"{support.KERNEL_REL} is byte-equal to the base's (sha256 {support.BASE_SHA256[:12]}...): nothing changed")
    stale = [rel for rel in support.COPIES_REL if support.read_bytes(rel) != kernel]
    assert not stale, f"{' and '.join(stale)} do not carry the changed kernel skill"


# Rewrite-Reason: W2-192 (commit e64430373, DAEO-mpq2: stage AS, CIT-P part A's bytes) moved the adopt skill's version
# from 1.1.0 (W2-188) to 1.2.0; the pins follow the skill as it stands, and W2-188 reopens at the lift (DEC-1210 (8)).
SKILL_VERSION = "1.2.0"


def test_s4_the_version_is_1_1_0_in_the_front_matter_of_each_copy():
    """The case keeps its W2-188 id. It pins the version the three copies carry now: `1.2.0`, not W2-188's `1.1.0`,
    because W2-192 (commit e64430373) added stage AS and raised the version again."""
    problems = []
    for rel in support.ALL_REL:
        lines = support.front_matter(support.read(rel))
        if not any(re.fullmatch(rf'version:\s*"{re.escape(SKILL_VERSION)}"\s*', line) for line in lines):
            found = next((line for line in lines if line.startswith("version:")), "no version line")
            problems.append(f'{rel}: `{found}`, not `version: "{SKILL_VERSION}"`')
    assert not problems, "; ".join(problems)


# Rewrite-Reason: W2-192 (commit e64430373, DAEO-mpq2) changed the same skill after W2-188: stage AS, a 10-line
# insertion after base line 29, and step 6's 2-line insertion after base line 60 are W2-192's; the four hunks of
# W2-188 keep their positions; DEC-1210 (8). Then Charter v6 / Contract v5 (DEC-1219, commit d515d0430) re-worded one
# sentence of the "Independent gates" section ("Contract v4.2 brings A7 and A10 into Wave 2 in a lite form" became
# "Contract v5 has A7 and A10 in Wave 2 in a lite form"), a one-line replacement at base line 41: a sixth hunk the
# case now names and sets aside by what it changes, as it holds the four places W2-188 changed, not the skill's byte
# count or hunk count.
DEC_1219_OLD, DEC_1219_NEW = "Contract v4.2 brings A7 and A10 into Wave 2", "Contract v5 has A7 and A10 in Wave 2"


def test_s4_the_kernel_diff_against_the_base_has_exactly_four_hunks_in_the_four_places():
    """The case keeps its W2-188 id. Against W2-188's base, the diff has five hunks of the ticket's and the later
    tickets' work: W2-188's four (line 4 the version, line 58 step 6, an insertion after base line 59 or 60 the
    paragraph, line 74 the sources line) and W2-192's stage AS insertion between them (a pure insertion after base
    line 29, 10 lines). Besides them, exactly one hunk is DEC-1219's re-wording of the Contract's name in the
    "Independent gates" sentence (base line 41, one line replaced by one line, `Contract v4.2` out, `Contract v5`
    in); it is set aside and counted nowhere else. Any other extra hunk, or a moved one, is red."""
    bodies = support.kernel_hunk_bodies()
    renames = [(hunk, body) for hunk, body in bodies
               if hunk[:2] == (41, 1) and hunk[3] == 1 and len(body) == 2
               and DEC_1219_OLD in body[0] and body[0].startswith("-")
               and DEC_1219_NEW in body[1] and body[1].startswith("+")]
    assert len(renames) == 1, (
        f"the diff has no one-line hunk at base line 41 re-wording `{DEC_1219_OLD}` to `{DEC_1219_NEW}` (DEC-1219): "
        f"{[hunk for hunk, _ in bodies]}")
    hunks = [hunk for hunk, _ in bodies if hunk != renames[0][0]]
    assert len(hunks) == 5, f"`git diff --unified=0 <base>` of the kernel skill has {len(hunks)} hunks besides DEC-1219's, not 5: {hunks}"
    (v_old, v_len, _, _), (as_old, as_len, _, as_new), (s_old, s_len, _, _), (p_old, p_len, _, p_new), (g_old, g_len, _, _) = hunks
    assert (v_old, v_len) == (4, 1), f"hunk 1 is not the version line (base line 4): base lines {v_old}+{v_len}"
    assert (as_old, as_len, as_new) == (29, 0, 10), (
        f"hunk 2 is not W2-192's stage AS insertion (10 lines after base line 29): base {as_old}+{as_len}, {as_new} added")
    assert (s_old, s_len) == (58, 1), f"hunk 3 is not step 6 (base line 58): base lines {s_old}+{s_len}"
    assert p_len == 0 and p_old in (59, 60) and p_new > 0, (
        f"hunk 4 is not a pure insertion after step 7 (base line 59 or 60): base {p_old}+{p_len}, {p_new} lines added")
    assert (g_old, g_len) == (74, 1), f"hunk 5 is not the sources line (base line 74): base lines {g_old}+{g_len}"


def test_s4_the_sources_line_gains_dec_1101_dec_1125_and_dec_1179_in_numeric_order_and_keeps_every_id():
    base_ids = support.governing_sources_ids(support.base_blob().decode("utf-8"))
    new_ids = support.governing_sources_ids(support.read(support.KERNEL_REL))
    assert new_ids is not None, "the kernel skill has no `## Governing sources` section"
    missing = [i for i in ["DEC-1101", "DEC-1125", "DEC-1179"] if i not in new_ids]
    lost = [i for i in base_ids if i not in new_ids]
    assert not missing, f"the sources line lacks {missing}"
    assert not lost, f"the sources line lost ids it had: {lost}"
    assert new_ids == sorted(new_ids, key=support.sources_order_key), (
        f"the sources line is not in numeric order (DEC ids, then CAP ids): {new_ids}")
    assert len(new_ids) == len(set(new_ids)), f"the sources line repeats an id: {new_ids}"


def test_s4_a9_steps_1_to_5_and_7_and_the_verify_section_are_unchanged_from_the_base():
    """Guard (holds on the base): the parts the ticket leaves alone, copy by copy."""
    def parts(text):
        a9 = support.a9_text(text)
        steps = [line for line in a9.splitlines() if re.match(r"^\s*[1-57]\.\s", line)]
        verify = support.heading_section(text, support.VERIFY_HEADING_PATTERN, levels=(2, 3))
        return steps, verify

    base_steps, base_verify = parts(support.base_blob().decode("utf-8"))
    assert len(base_steps) == 6 and len(base_verify) == 1, "the base is not as pinned (six step lines, one Verify section)"
    problems = []
    for rel in support.ALL_REL:
        steps, verify = parts(support.read(rel))
        if steps != base_steps:
            problems.append(f"{rel}: A9's steps 1 to 5 or 7 differ from the base")
        if verify != base_verify:
            problems.append(f"{rel}: the Verify clauses section differs from the base")
    assert not problems, "; ".join(problems)


def test_s4_the_skills_check_exits_0_on_both_layouts():
    """Guard (holds on the base): it catches a body over the skills check's size limit and a bad front matter."""
    code, output = support.run_skill_validator()
    assert code == 0, f"python3 -m gov.check.skill_validator --both-layouts exited {code}: {output[-400:]}"


def test_f1_no_copy_names_a_memaudit_subcommand_or_standing_declare():
    """Guard (holds on the base); F1's other half is the four-hunk test above."""
    problems = []
    for rel in support.ALL_REL:
        text = support.read(rel)
        for needle in ("gov.memaudit", "standing declare"):
            if needle in text:
                problems.append(f"{rel} holds `{needle}`")
    assert not problems, "; ".join(problems)


# The copies ACT ACT-CLAUDE-COPIES-12's after-bytes of `.claude/skills/adopt/SKILL.md`, generated from the kernel skill
# the owner approved (sha256 6a884cf1...9489, DEC-1181 (1)); P-C12-1 (a), DEC-1156 (7).
ACT_CLAUDE_COPY_SHA256 = "65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc"
ACT_SUBJECT_MARK = "ACT-CLAUDE-COPIES-"
# Rewrite-Reason: W2-192 (commit e64430373, DAEO-mpq2) regenerated the `.claude` copy again, from the kernel skill with
# stage AS (CIT-P part A's bytes, version 1.2.0): the later copies ACT's after-bytes. DEC-1210 (8).
ACT_CLAUDE_COPY_SHA256_W2_192 = "93b04fc62be1fe6d0e125ff47a2d890367284f1970b7d34dfd0f4366c987dc5d"


# Rewrite-Reason: Charter v6 / Contract v5 (DEC-1219, commit d515d0430) re-worded one sentence in the `.claude` copy
# as in the kernel skill, so its bytes are W2-192's after-bytes (commit e64430373) with that one sentence changed; the
# case holds that, derived from the pinned commit, not a third byte hash.
W2_192_COMMIT = "e64430373"
DEC_1219_SENTENCE = (b"Contract v4.2 brings A7 and A10 into Wave 2 in a lite form",
                     b"Contract v5 has A7 and A10 in Wave 2 in a lite form")


def test_f2_the_claude_copy_of_the_skill_equals_the_base_or_the_copies_acts_after_bytes():
    """Guard (holds on the base): the `.claude` copy is the base's bytes, or exactly the copies ACT's after-bytes
    (sha256 `65d6abd9...dbc`, the ACT's regeneration after the owner's approval), or exactly the later copies ACT's
    after-bytes (sha256 `93b04fc6...c5d`, commit e64430373, W2-192's stage AS), or those bytes with the one sentence
    DEC-1219 re-worded (`Contract v4.2 brings A7 and A10 into Wave 2 in a lite form` to `Contract v5 has A7 and A10
    in Wave 2 in a lite form`, commit d515d0430); any other bytes mean the ticket wrote it."""
    now = support.read_bytes(support.CLAUDE_COPY_REL)
    then = support.base_blob(support.CLAUDE_COPY_REL)
    if now == then:
        return
    found = support.sha256_of(now)
    if found in (ACT_CLAUDE_COPY_SHA256, ACT_CLAUDE_COPY_SHA256_W2_192):
        return
    w2_192 = support.git("show", f"{W2_192_COMMIT}:{support.CLAUDE_COPY_REL}").stdout
    assert support.sha256_of(w2_192) == ACT_CLAUDE_COPY_SHA256_W2_192, f"{W2_192_COMMIT}'s copy is not W2-192's bytes"
    assert w2_192.count(DEC_1219_SENTENCE[0]) == 1
    assert now == w2_192.replace(*DEC_1219_SENTENCE), (
        f"{support.CLAUDE_COPY_REL} has sha256 {found}: neither the base's ({support.sha256_of(then)}) "
        f"nor a copies ACT's after-bytes ({ACT_CLAUDE_COPY_SHA256}, {ACT_CLAUDE_COPY_SHA256_W2_192}) "
        f"nor W2-192's with DEC-1219's one sentence")


def test_f2_no_commit_of_the_ticket_outside_the_test_designer_or_the_copies_act_touches_claude_or_tests():
    """Guard (holds on the base): a commit after the base with `Task: DAEO-zlog` whose `Role:` is not
    `independent-test-designer` (or that has no Role) names no `.claude/` path and no `tests/` path. The one excuse:
    a commit whose trailers carry `Role: owner` and whose subject names `ACT-CLAUDE-COPIES-` (the copies ACT) may
    touch `.claude/` paths; its `tests/` paths still count."""
    done = support.git("log", "--no-merges", "--name-only",
                       "--format=%x1e%H%x1f%(trailers:key=Task,valueonly,separator=%x2c)%x1f"
                       "%(trailers:key=Role,valueonly,separator=%x2c)%x1f%s%x1f", f"{support.BASE}..HEAD")
    problems = []
    for entry in done.stdout.decode("utf-8", "replace").split("\x1e"):
        if "\x1f" not in entry:
            continue
        commit, tasks, roles, subject, files = entry.split("\x1f", 4)
        if support.TICKET not in [task.strip() for task in tasks.split(",")]:
            continue
        role_list = [role.strip() for role in roles.split(",")]
        if "independent-test-designer" in role_list:
            continue
        copies_act = "owner" in role_list and ACT_SUBJECT_MARK in subject
        prefixes = ("tests/",) if copies_act else (".claude/", "tests/")
        touched = [name for name in files.split() if name.startswith(prefixes)]
        if touched:
            problems.append(f"{commit[:12]} (Role: {roles.strip() or 'none'}; subject: {subject[:60]!r}) "
                            f"touches {touched[:3]}")
    assert not problems, "; ".join(problems)
