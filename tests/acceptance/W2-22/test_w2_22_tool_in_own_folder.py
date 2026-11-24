"""W2-22 fix F2 (audit 3, M-04; DEC-1232, DEC-1233): ``gov doctor`` finds and reads the version of a tool installed in
its own folder, with no schema change, and a ``PATH=`` prefix from one tool's install line never answers for another
tool of the same binary at another version.

Observable: ``gov doctor --json``'s ``tools`` part, each entry's ``ok``, ``found_version`` and ``pinned_version``.
Every case runs with HOME set to a folder of its own and a registry of its own; stand-ins are shell scripts.
``real``: the install lines as the real registry writes them (``~``, ``$HOME``); ``abs``: the same places spelled out.
"""

from __future__ import annotations

import pytest

import w2_22_tools_support as t

FORMS = ["real", "abs"]
# registry order x spelling of the places x whether an ``openspec`` entry carrying the v22.23.3 prefix is in the
# registry: the prefix of rea-agents' install line (v22.23.5) comes before node's own place in one order, after it in
# the real one; without ``openspec`` the only prefix any install line carries is the v22.23.5 one
LAYOUTS = [("rea-first", "abs", False), ("real-order", "abs", False), ("real-order", "abs", True),
           ("rea-first", "abs", True), ("real-order", "real", False)]
CASES = ["both-installed", "only-22.23.5", "only-22.23.3"]


# --- success-3: a second Node, in its own nvm folder ------------------------------------------------------------

@pytest.mark.parametrize("form", FORMS)
def test_a_second_node_in_its_own_nvm_folder_is_found_and_read(tmp_path, sandbox, monkeypatch, form):
    t.write_stand_in(t.node_bin(sandbox, "v22.23.5") / "node", "v22.23.5")
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, [t.node_entry(sandbox, form, "v22.23.5", "node-22.23.5")])
    got = t.tool(run, tools, "node-22.23.5")
    assert got.get("ok") is True, f"node-22.23.5 at <HOME>/.nvm/versions/node/v22.23.5/bin is not ok: {got}\n{run.describe()}"
    assert t.number(got) == "22.23.5", f"found_version should read v22.23.5: {got}"
    assert got.get("pinned_version") == "v22.23.5", got


# --- success-4: rea-agents, installed in the folder of its install line -----------------------------------------

@pytest.mark.parametrize("form", FORMS)
def test_rea_agents_in_its_folders_node_modules_bin_is_found_and_read(tmp_path, sandbox, monkeypatch, form):
    t.write_stand_in(t.rea_binary(sandbox), "6.10.1")
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, [t.rea_entry(sandbox, form)])
    got = t.tool(run, tools, "rea-agents")
    assert got.get("ok") is True, f"rea-agents at <folder>/node_modules/.bin/rea is not ok: {got}\n{run.describe()}"
    assert t.number(got) == "6.10.1", f"found_version should read 6.10.1: {got}"
    assert got.get("pinned_version") == "6.10.1", got


# --- success-5: a wrong version or an absent binary still fails -------------------------------------------------

@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("found", ["v22.23.4", "v22.23.3"])
def test_a_second_node_at_another_version_still_fails(tmp_path, sandbox, monkeypatch, form, found):
    t.write_stand_in(t.node_bin(sandbox, "v22.23.5") / "node", found)
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, [t.node_entry(sandbox, form, "v22.23.5", "node-22.23.5")])
    got = t.tool(run, tools, "node-22.23.5")
    assert got.get("ok") is False, f"a node printing {found} passed for the pin v22.23.5: {got}\n{run.describe()}"


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("found", ["6.10.0", "6.11.0"])
def test_rea_agents_at_another_version_still_fails(tmp_path, sandbox, monkeypatch, form, found):
    t.write_stand_in(t.rea_binary(sandbox), found)
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, [t.rea_entry(sandbox, form)])
    got = t.tool(run, tools, "rea-agents")
    assert got.get("ok") is False, f"a rea printing {found} passed for the pin 6.10.1: {got}\n{run.describe()}"


@pytest.mark.parametrize("form", FORMS)
def test_tools_whose_binary_is_absent_still_fail(tmp_path, sandbox, monkeypatch, form):
    entries = [t.node_entry(sandbox, form, "v22.23.5", "node-22.23.5"), t.rea_entry(sandbox, form)]
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, entries)
    for name in ("node-22.23.5", "rea-agents"):
        got = t.tool(run, tools, name)
        assert got.get("ok") is False, f"{name} has no binary anywhere and still passed: {got}\n{run.describe()}"


# --- success-6: a prefix never answers for another tool of the same binary at another version -------------------

def _layout(sandbox, order: str, form: str, with_openspec: bool) -> list[str]:
    node = t.node_entry(sandbox, form, "v22.23.3", "node")
    node_2 = t.node_entry(sandbox, form, "v22.23.5", "node-22.23.5")
    rea = t.rea_entry(sandbox, form)
    openspec = [t.openspec_entry(sandbox, form)] if with_openspec else []   # carries the v22.23.3 prefix, as the real one
    return [rea, *openspec, node, node_2] if order == "rea-first" else [node, *openspec, node_2, rea]


@pytest.mark.parametrize("order,form,with_openspec", LAYOUTS)
@pytest.mark.parametrize("case", CASES)
def test_each_node_is_judged_against_its_own_pin_only(tmp_path, sandbox, monkeypatch, order, form, with_openspec, case):
    """``node`` (v22.23.3, no prefix of its own) and ``node-22.23.5``, the v22.23.5 prefix in rea-agents' install line
    and, with ``openspec``, the v22.23.3 prefix in its install line, a stand-in ``node`` printing v18.20.8 first on the PATH."""
    if case != "only-22.23.5":
        t.write_stand_in(t.node_bin(sandbox, "v22.23.3") / "node", "v22.23.3")
    if case != "only-22.23.3":
        t.write_stand_in(t.node_bin(sandbox, "v22.23.5") / "node", "v22.23.5")
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, _layout(sandbox, order, form, with_openspec))
    node, node_2 = t.tool(run, tools, "node"), t.tool(run, tools, "node-22.23.5")
    note = f"\nnode: {node}\nnode-22.23.5: {node_2}\n{run.describe()}"
    if case == "both-installed":
        assert node.get("ok") is True and t.number(node) == "22.23.3", f"node is judged against v22.23.3 only{note}"
        assert node_2.get("ok") is True and t.number(node_2) == "22.23.5", f"node-22.23.5 against v22.23.5 only{note}"
    elif case == "only-22.23.5":
        assert node.get("ok") is False and t.number(node) != "22.23.5", f"the v22.23.5 binary answered for node{note}"
        assert node_2.get("ok") is True and t.number(node_2) == "22.23.5", f"node-22.23.5 is not found{note}"
    else:
        assert node_2.get("ok") is False and t.number(node_2) != "22.23.3", f"the v22.23.3 binary answered for 22.23.5{note}"
        assert node.get("ok") is True and t.number(node) == "22.23.3", f"node is not found{note}"


# --- success-7: DEC-452 stays: a tool with no prefix of its own is found under another entry's prefix ------------

def test_a_tool_without_a_prefix_is_still_found_under_another_entrys_prefix(tmp_path, sandbox, monkeypatch):
    """``openspec`` and ``ccusage`` as the real registry has them under Node's prefix: ``ccusage`` carries it,
    ``openspec`` carries none, a decoy ``openspec`` (another version) is on the PATH, the real one is under the prefix."""
    prefix = t.node_bin(sandbox, "v22.23.3")
    t.write_stand_in(prefix / "ccusage", "20.0.26")
    t.write_stand_in(prefix / "openspec", "1.13.2")
    t.write_stand_in(sandbox.bin / "openspec", "9.9.9")
    ccusage_line = f"PATH=$HOME/{t.NVM}/v22.23.3/bin:$PATH $HOME/{t.NVM}/v22.23.3/bin/npm install -g ccusage@20.0.26"
    ccusage = t.entry("ccusage", "20.0.26", t.stand_in_sha("20.0.26"), t._form(ccusage_line, sandbox, "abs"))
    openspec = t.entry("openspec", "1.13.2", t.stand_in_sha("1.13.2"), "npm install -g @fission-ai/openspec@1.13.2")
    run, tools = t.doctor_tools(tmp_path, sandbox, monkeypatch, [ccusage, openspec])
    for name, version in (("ccusage", "20.0.26"), ("openspec", "1.13.2")):
        got = t.tool(run, tools, name)
        assert got.get("ok") is True and t.number(got) == version, f"{name} not found under Node's prefix: {got}\n{run.describe()}"
