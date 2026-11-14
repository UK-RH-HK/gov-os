"""W2-60a, KPI success 2 -- the skills the session can load are recorded; a role's named skills are loaded.

KPI success 2 [DEC-826 Q1, DEC-832 item 1, lens E F15]: "The skills the
session can load are in the launch record, each with its name, version and
content hash, taken from the copy the session loads; a role file that names its
skills gets those, so the engineer's skill packs load with no code change once
W2-33 writes them; a named skill that is missing refuses the launch". KPI
failure 1: "A launch that starts with ... an unrecorded skill".

From the design (Behaviour 2): the skills the session can load are the folders
directly under ``.claude/skills/`` that hold a ``SKILL.md``; each is recorded
from that copy (never the kernel's): its name (front matter ``name``, else the
folder's), its path, its version (front matter ``version`` as written, else
``no version``), the sha256 of its ``SKILL.md``, the sha256 of its folder, and
whether the role names it. A role file names its skills in one line,
``- **Skills:** <name>, <name>``; each named skill must be at
``.claude/skills/<name>/SKILL.md`` with a version, and its ``SKILL.md`` text is
appended after the role's text, in the order named. Refused: a named skill
missing, unreadable or without a version; a malformed skills line; a skill
folder that is a link or holds one, or whose front matter is not YAML. An
absent ``.claude/skills/`` is an empty list unless the role names a skill.

The folder hash's exact serialisation is the design's; these tests hold it to
what can be seen without it: a sha256, the same for the same folder, and moved
by a change to any file of the folder.
"""

from __future__ import annotations

import os
import shutil

import pytest

import w2_60a_support as s

SKILL_PATH_FORMS = ("{rel}/{folder}/SKILL.md", "{rel}/{folder}", "{rel}/{folder}/")


def _by_name(record):
    skills = record.get("skills")
    assert isinstance(skills, list), f"the record's skills is not a list: {skills!r}"
    found = {}
    for entry in skills:
        assert isinstance(entry, dict) and "name" in entry, f"a skills entry without a name: {entry!r}"
        assert entry["name"] not in found, f"the skill {entry['name']} is recorded twice"
        found[entry["name"]] = entry
    return found


def _path_names(entry, project, folder):
    forms = {form.format(rel=s.SKILLS_REL, folder=folder) for form in SKILL_PATH_FORMS}
    forms |= {os.path.join(os.path.realpath(project), form) for form in set(forms)}
    return str(entry.get("path")) in forms


def test_every_skill_the_session_can_load_is_recorded_from_the_loaded_copy(project, launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    found = _by_name(result.record())
    expected = {skill.recorded_name for skill in s.SKILLS}
    assert set(found) == expected, (
        f"the record's skills are not the skills under {s.SKILLS_REL}/: recorded {sorted(found)}, "
        f"loadable {sorted(expected)}")
    for skill in s.SKILLS:
        entry = found[skill.recorded_name]
        assert entry.get("version") == skill.recorded_version, (
            f"{skill.folder}: version {entry.get('version')!r}, not the loaded copy's {skill.recorded_version!r} "
            f"(the kernel copy says {s.KERNEL_VERSIONS.get(skill.folder)!r})")
        assert entry.get("sha256") == s.sha256_file(project / s.SKILLS_REL / skill.folder / "SKILL.md"), (
            f"{skill.folder}: sha256 is not the loaded SKILL.md's")
        assert isinstance(entry.get("folder_sha256"), str) and s.SHA256.fullmatch(entry["folder_sha256"]), (
            f"{skill.folder}: folder_sha256 is not a sha256: {entry.get('folder_sha256')!r}")
        assert entry.get("named") is False, f"{skill.folder} is recorded as named; the engineer's file names none"
        assert _path_names(entry, project, skill.folder), (
            f"{skill.folder}: the recorded path {entry.get('path')!r} is not the loaded copy's")
    assert s.USER_SKILL not in found, "a user-level skill of the test home is recorded as one the session can load"


def test_a_skill_folder_s_hash_follows_every_file_of_the_folder(project, launch):
    first = launch(s.ENGINEER)
    s.assert_launched(first)
    again = launch(s.ENGINEER)
    s.assert_launched(again)
    s.write(project / s.SKILLS_REL / s.BACKEND.folder / "reference.md", "Backend reference, changed.\n")
    changed = launch(s.ENGINEER)
    s.assert_launched(changed)
    one, two, three = (_by_name(r.record()) for r in (first, again, changed))
    backend, security = s.BACKEND.recorded_name, s.SECURITY.recorded_name
    assert one[backend]["folder_sha256"] == two[backend]["folder_sha256"], "the same folder gave two folder hashes"
    assert three[backend]["sha256"] == one[backend]["sha256"], "SKILL.md did not change, but its sha256 did"
    assert three[backend]["folder_sha256"] != one[backend]["folder_sha256"], (
        "a changed file of the skill's folder left its folder_sha256 as it was")
    assert three[security]["folder_sha256"] == one[security]["folder_sha256"], (
        "another skill's folder_sha256 moved with a file it does not hold")


def test_the_skills_a_role_names_are_appended_after_its_text_in_the_order_named(project, launch):
    named = (s.SECURITY.folder, s.BACKEND.folder)
    s.write_role(project, s.ENGINEER, skills=named)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    text = result.appended()["text"]
    role = s.role_path(project, s.ENGINEER).read_text(encoding="utf-8")
    assert text.startswith(role), "the appended file does not begin with the role file's text"
    places = []
    for folder in named:
        skill_text = (project / s.SKILLS_REL / folder / "SKILL.md").read_text(encoding="utf-8")
        place = text.find(skill_text, len(role))
        assert place >= 0, f"the named skill {folder}'s SKILL.md text is not appended after the role's text"
        places.append(place)
    assert places == sorted(places), f"the named skills are not appended in the order named: {named}"
    for skill in (s.UNVERSIONED, s.FOLDER_NAMED):
        assert skill.word not in text, f"the unnamed skill {skill.folder} was appended to the session's start"
    found = _by_name(result.record())
    for skill in s.SKILLS:
        assert found[skill.recorded_name].get("named") is (skill.folder in named), (
            f"{skill.folder}: named is {found[skill.recorded_name].get('named')!r}")


def test_a_new_skill_pack_the_role_names_loads_with_no_code_change(project, launch):
    """DEC-832 item 1: the engineer's skill packs load once W2-33 writes them and the role file names them."""
    pack = s.Skill("w260a-database", "w260a-database", "1.0.0")
    s.write(project / s.SKILLS_REL / pack.folder / "SKILL.md", pack.text())
    s.write_role(project, s.ENGINEER, skills=(pack.folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert pack.word in result.appended()["text"], "the new pack's text is not in the session's start"
    entry = _by_name(result.record()).get(pack.name)
    assert entry is not None and entry.get("named") is True and entry.get("version") == "1.0.0", (
        f"the new pack is not recorded as named, version 1.0.0: {entry!r}")


# --------------------------------------------------------------------------
# Refusals
# --------------------------------------------------------------------------

NAMED_REFUSALS = {
    "named-skill-missing": (("w260a-missing",), "w260a-missing", None),
    "named-skill-without-version": ((s.UNVERSIONED.folder,), s.UNVERSIONED.folder, None),
    "named-skill-folder-without-skill-md": ((s.SECURITY.folder,), s.SECURITY.folder, "remove-skill-md"),
    "skills-line-malformed": (None, "skills", "malformed-line"),
}


@pytest.mark.parametrize("case", sorted(NAMED_REFUSALS))
def test_a_named_skill_that_cannot_be_loaded_refuses_the_launch(project, launch, case):
    named, word, change = NAMED_REFUSALS[case]
    if change == "malformed-line":
        s.write_role(project, s.ENGINEER, skills=None)
        path = s.role_path(project, s.ENGINEER)
        path.write_text(path.read_text(encoding="utf-8") + f"- **Skills:** {s.BACKEND.folder},, {s.SECURITY.folder}\n",
                        encoding="utf-8")
    else:
        s.write_role(project, s.ENGINEER, skills=named)
    if change == "remove-skill-md":
        (project / s.SKILLS_REL / s.SECURITY.folder / "SKILL.md").unlink()
    s.assert_refused(launch(s.ENGINEER), word)


def _folder_is_a_link(project, sandbox):
    target = sandbox.elsewhere / "linked-skill"
    s.write(target / "SKILL.md", s.Skill("w260a-linked", "w260a-linked", "1.0.0").text())
    os.symlink(target, project / s.SKILLS_REL / "w260a-linked")


def _folder_holds_a_link(project, sandbox):
    outside = s.write(sandbox.elsewhere / "outside.md", "outside\n")
    os.symlink(outside, project / s.SKILLS_REL / s.BACKEND.folder / "linked.md")


def _front_matter_not_yaml(project, sandbox):
    s.write(project / s.SKILLS_REL / "w260a-broken" / "SKILL.md",
            "---\nname: w260a-broken\nversion: [1.0.0\ndescription: : :\n---\n\nbroken\n")


UNDESCRIBABLE = {
    "skill-folder-is-a-link": _folder_is_a_link,
    "skill-folder-holds-a-link": _folder_holds_a_link,
    "front-matter-not-yaml": _front_matter_not_yaml,
}


@pytest.mark.parametrize("case", sorted(UNDESCRIBABLE))
def test_a_skills_folder_the_record_could_not_describe_refuses_the_launch(sandbox, project, launch, case):
    """Behaviour 2: the record could not say what the session may load. The role names no skill."""
    UNDESCRIBABLE[case](project, sandbox)
    s.assert_refused(launch(s.ENGINEER), "skill")


# --------------------------------------------------------------------------
# The kernel's generated copies: the version under ``metadata:`` (KPI S2, F3)
# --------------------------------------------------------------------------

def _metadata_skill_text(folder, metadata_version, top_version=None):
    """A ``SKILL.md`` in the form the kernel's generated copies take today (``.claude/skills/test-design/SKILL.md``):
    the version only as ``metadata: version: <x.y.z>``, unquoted; with ``top_version``, a top-level ``version`` too."""
    head = ["---", f"name: {folder}", "description: >-", f"  The W2-60a fixture skill {folder}."]
    if top_version is not None:
        head.append(f"version: {top_version}")
    head += ["metadata:", f"  version: {metadata_version}", "---", ""]
    body = [f"# {folder}", "", f"This skill's method text carries the marker zq60a-skill-{folder}.", ""]
    return "\n".join(head + body)


def test_a_named_skill_versioned_only_under_metadata_launches_and_is_recorded_with_that_version(project, launch):
    """KPI S2: the version is taken from the copy the session loads; F3: today's generated copies, which carry their
    version only as ``metadata: version:``, are not refused as carrying no version. Red today: "carries no version"."""
    folder = "w260a-metadata-only"
    path = s.write(project / s.SKILLS_REL / folder / "SKILL.md", _metadata_skill_text(folder, "1.4.0"))
    s.write_role(project, s.ENGINEER, skills=(folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert f"zq60a-skill-{folder}" in result.appended()["text"], (
        f"the named skill {folder}'s text is not in the session's start")
    entry = _by_name(result.record()).get(folder)
    assert entry is not None, f"the named skill {folder} is not in the launch record: {result.record().get('skills')}"
    assert entry.get("version") == "1.4.0", (
        f"{folder}: version {entry.get('version')!r}, not the loaded copy's metadata.version '1.4.0'")
    assert entry.get("sha256") == s.sha256_file(path), f"{folder}: sha256 is not the loaded SKILL.md's"
    assert entry.get("named") is True, f"{folder} is named by the role but recorded as named={entry.get('named')!r}"


def test_a_skill_with_a_top_level_version_and_a_metadata_version_is_recorded_with_the_top_level_one(project, launch):
    """KPI S2: a top-level ``version`` stays the recorded one when ``metadata.version`` is there as well."""
    folder = "w260a-both-versions"
    path = s.write(project / s.SKILLS_REL / folder / "SKILL.md", _metadata_skill_text(folder, "9.0.0", "2.2.0"))
    s.write_role(project, s.ENGINEER, skills=(folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    entry = _by_name(result.record()).get(folder)
    assert entry is not None, f"the named skill {folder} is not in the launch record: {result.record().get('skills')}"
    assert entry.get("version") == "2.2.0", (
        f"{folder}: version {entry.get('version')!r}, not the top-level '2.2.0' (metadata.version is '9.0.0')")
    assert entry.get("sha256") == s.sha256_file(path), f"{folder}: sha256 is not the loaded SKILL.md's"


def test_no_skills_folder_is_an_empty_list(project, launch):
    shutil.rmtree(project / s.SKILLS_REL)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert result.record().get("skills") == [], f"no {s.SKILLS_REL}/, but skills recorded: {result.record()}"


def test_no_skills_folder_and_a_named_skill_refuses_the_launch(project, launch):
    shutil.rmtree(project / s.SKILLS_REL)
    s.write_role(project, s.ENGINEER, skills=(s.BACKEND.folder,))
    s.assert_refused(launch(s.ENGINEER), s.BACKEND.folder)


# --------------------------------------------------------------------------
# A vendored skill's version from its manifest (P-7 (a), the CTO, recorded in the ticket)
# --------------------------------------------------------------------------
# The vendored Superpowers copies (``.claude/skills/<name>/SKILL.md``) carry no version; it is in the manifest
# ``template/governance/kernel/skills/superpowers/vendored.yaml`` (``governance/kernel/skills/...`` in the adopted
# layout): a top-level ``version`` and the skills as the keys of ``token_sizes``. A loadable copy with no version (no
# top-level ``version``, no ``metadata.version``) whose name is a key of ``token_sizes`` is recorded with the manifest's
# version and ``version_source``, the manifest's repository-relative path; its ``sha256`` stays the copy's, and a named
# one launches. A copy with its own version keeps it, with no ``version_source``. Not listed, no manifest, or a
# manifest not a YAML mapping: ``no version`` as today, and a named one refuses ("carries no version").

MANIFEST_REL = f"{s.KERNEL_SKILLS_REL}/superpowers/vendored.yaml"
ADOPTED_MANIFEST_REL = "governance/kernel/skills/superpowers/vendored.yaml"
VENDORED = s.Skill("w260a-vendored", "w260a-vendored", None)
VENDORED_VERSION = "v6.4.2"


def _manifest_text(names, version=VENDORED_VERSION):
    """The manifest in this repository's form (template/governance/kernel/skills/superpowers/vendored.yaml)."""
    sizes = "".join(f"  {name}: {100 + index}\n" for index, name in enumerate(names))
    return (f"# W2-60a fixture vendored-skills manifest.\nversion: \"{version}\"\n"
            f"source_sha256: \"{'a' * 64}\"\nsha256: \"{'b' * 64}\"\ntoken_sizes:\n{sizes}")


def _plant_vendored(project, names=(VENDORED.folder, "w260a-other-vendored"), manifest_rel=MANIFEST_REL, text=None):
    """``VENDORED``'s unversioned copy under ``.claude/skills/``, and the manifest listing ``names`` (or ``text``)."""
    copy = s.write(project / s.SKILLS_REL / VENDORED.folder / "SKILL.md", VENDORED.text())
    if manifest_rel is not None:
        s.write(project / manifest_rel, _manifest_text(names) if text is None else text)
    return copy


def _assert_from_manifest(entry, copy, named, manifest_rel=MANIFEST_REL):
    assert entry is not None, f"the vendored skill {VENDORED.folder} is not in the launch record"
    assert entry.get("version") == VENDORED_VERSION, (
        f"{VENDORED.folder}: version {entry.get('version')!r}, not the manifest's {VENDORED_VERSION!r}")
    assert entry.get("version_source") == manifest_rel, (
        f"{VENDORED.folder}: version_source {entry.get('version_source')!r}, not the manifest's path {manifest_rel!r}")
    assert entry.get("sha256") == s.sha256_file(copy), f"{VENDORED.folder}: sha256 is not the loaded copy's"
    assert entry.get("named") is named, f"{VENDORED.folder}: named is {entry.get('named')!r}, not {named}"


def test_p7_a_named_listed_unversioned_skill_launches_with_the_manifest_s_version(project, launch):
    copy = _plant_vendored(project)
    s.write_role(project, s.ENGINEER, skills=(VENDORED.folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert VENDORED.word in result.appended()["text"], f"the named skill {VENDORED.folder}'s text is not appended"
    _assert_from_manifest(_by_name(result.record()).get(VENDORED.name), copy, named=True)


def test_p7_an_unnamed_listed_unversioned_skill_is_recorded_with_the_manifest_s_version(project, launch):
    """The same skill, unnamed: recorded the same way. The others keep their own: the versioned ones (from their
    copy) and the unlisted unversioned one (``no version``) carry no ``version_source``."""
    copy = _plant_vendored(project)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    found = _by_name(result.record())
    _assert_from_manifest(found.get(VENDORED.name), copy, named=False)
    for skill in s.SKILLS:
        entry = found[skill.recorded_name]
        assert entry.get("version") == skill.recorded_version, (
            f"{skill.folder}: version {entry.get('version')!r}, not {skill.recorded_version!r}")
        assert "version_source" not in entry, f"{skill.folder} carries a version_source: {entry!r}"


@pytest.mark.parametrize("form", ("top-level", "metadata"))
def test_p7_a_listed_skill_whose_copy_has_its_own_version_keeps_the_copy_s(project, launch, form):
    folder = "w260a-versioned-vendored"
    if form == "top-level":
        text = s.Skill(folder, folder, "1.2.3").text()
    else:
        text = _metadata_skill_text(folder, "1.2.3")
    copy = s.write(project / s.SKILLS_REL / folder / "SKILL.md", text)
    s.write(project / MANIFEST_REL, _manifest_text((folder, VENDORED.folder)))
    s.write_role(project, s.ENGINEER, skills=(folder,))
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    entry = _by_name(result.record()).get(folder)
    assert entry is not None, f"the named skill {folder} is not in the launch record"
    assert entry.get("version") == "1.2.3", f"{folder}: version {entry.get('version')!r}, not the copy's '1.2.3'"
    assert "version_source" not in entry, f"{folder}'s version is its copy's, but it carries a version_source: {entry!r}"
    assert entry.get("sha256") == s.sha256_file(copy), f"{folder}: sha256 is not the loaded copy's"


NOT_FROM_THE_MANIFEST = {
    "not-listed": dict(names=("w260a-other-vendored",)),
    "no-manifest": dict(manifest_rel=None),
    "manifest-a-list": dict(text=f"- {VENDORED.folder}\n- w260a-other-vendored\n"),
    "manifest-a-string": dict(text=f"version {VENDORED_VERSION}, token_sizes {VENDORED.folder}\n"),
}


@pytest.mark.parametrize("case", sorted(NOT_FROM_THE_MANIFEST))
def test_p7_a_named_unversioned_skill_the_manifest_does_not_version_still_refuses(project, launch, case):
    _plant_vendored(project, **NOT_FROM_THE_MANIFEST[case])
    s.write_role(project, s.ENGINEER, skills=(VENDORED.folder,))
    s.assert_refused(launch(s.ENGINEER), "LAUNCH_REFUSED", VENDORED.folder, "carries no version")


@pytest.mark.parametrize("case", sorted(NOT_FROM_THE_MANIFEST))
def test_p7_an_unnamed_unversioned_skill_the_manifest_does_not_version_is_no_version(project, launch, case):
    _plant_vendored(project, **NOT_FROM_THE_MANIFEST[case])
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    entry = _by_name(result.record()).get(VENDORED.name)
    assert entry is not None and entry.get("version") == "no version", (
        f"{VENDORED.folder} ({case}): recorded {entry!r}, not version 'no version'")
    assert "version_source" not in entry, f"{VENDORED.folder} ({case}) carries a version_source: {entry!r}"


def test_p7_this_repository_s_vendored_copies_are_recorded_with_its_manifest_s_version(sandbox, project, launch):
    """This repository's own manifest and its own vendored copies (``.claude/skills/<name>/SKILL.md``, no version),
    planted byte for byte: each listed skill launches named and is recorded with the manifest's version."""
    source = s.REPO_ROOT / MANIFEST_REL
    s.write(project / MANIFEST_REL, source.read_text(encoding="utf-8"))
    names = ("test-driven-development", "systematic-debugging", "verification-before-completion")
    copies = {}
    for name in names:
        copies[name] = s.write(project / s.SKILLS_REL / name / "SKILL.md",
                               (s.REPO_ROOT / s.SKILLS_REL / name / "SKILL.md").read_text(encoding="utf-8"))
    s.write_role(project, s.ENGINEER, skills=names)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    found = _by_name(result.record())
    for name in names:
        entry = found.get(name)
        assert entry is not None, f"the vendored skill {name} is not in the launch record"
        got = {key: entry.get(key) for key in ("version", "version_source", "sha256", "named")}
        assert got == {"version": VENDORED_VERSION, "version_source": MANIFEST_REL,
                       "sha256": s.sha256_file(copies[name]), "named": True}, f"{name}: {got}"


def test_p7_an_adopted_tree_s_manifest_versions_its_vendored_copy(sandbox, cli):
    """The adopted layout (no ``template/``): the manifest at ``governance/kernel/skills/superpowers/vendored.yaml``,
    and ``version_source`` names that path."""
    project = s.make_project(sandbox, roles=(), kernel_skills=False, commit=False)
    shutil.move(project / "template/governance/kernel/launch", project / "governance/kernel/launch")
    shutil.rmtree(project / "template")
    s.write(project / "governance/kernel/roles" / f"{s.ENGINEER}.md",
            s.role_text(s.ENGINEER, skills=(VENDORED.folder,)))
    copy = _plant_vendored(project, manifest_rel=ADOPTED_MANIFEST_REL)
    s.git(project, "init", "-q", "-b", "main")
    s.git(project, "add", "-A")
    s.git(project, "commit", "-q", "-m", "W2-60a adopted fixture project")
    result = s.launch(sandbox, cli, s.ENGINEER, s.T)
    s.assert_launched(result)
    _assert_from_manifest(_by_name(result.record()).get(VENDORED.name), copy, named=True,
                          manifest_rel=ADOPTED_MANIFEST_REL)
