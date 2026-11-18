"""W2-185 (DAEO-qyt2): adopted projects get the context watch, and portability's lift is per hook.

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. S1 no longer asks for the template's
posttooluse.py entry (retired), and the kernel's hook scripts are five.

S1 reads the template's hooks source; S2 and F1 call portability's hooks comparison over stand-in roots built in
``tmp_path``; S3 reads W1-38's fixture. Behaviour and files only, no network, no model.
"""
import w2_185_support as support
from w2_185_support import entry


# ---------------------------------------------------------------------------
# S1: the template wires context_watch.py in postToolUse, in the root's form with the adopted path
# ---------------------------------------------------------------------------

def test_s1_the_template_wires_context_watch_in_post_tool_use_beside_posttooluse():
    template = support.read_source(support.TEMPLATE_HOOKS)
    root_entry = support.adopted_context_watch()
    post = support.entries(template, "postToolUse")
    watch = [e for e in post if support.names_script(e["command"], "context_watch.py")]
    assert len(watch) == 1, f"template postToolUse has {len(watch)} entries for context_watch.py; one is expected"
    assert watch[0].get("matcher") == "Bash" and watch[0].get("timeout") == 10, watch[0]
    assert watch[0]["command"] == root_entry["command"], (
        "the command is the root's context_watch.py command with the adopted path governance/kernel/hooks/:\n"
        f"expected {root_entry['command']!r}\nfound    {watch[0]['command']!r}")
    assert "template/governance" not in watch[0]["command"]


def test_s1_every_kernel_hook_script_is_named_by_a_command_of_the_template_hooks_source():
    scripts = sorted(path.name for path in support.KERNEL_HOOKS.glob("*.py"))
    assert len(scripts) >= 5 and "context_watch.py" in scripts, scripts   # five since EMERGENCY-2 6.1 (DAEO-gr7t)
    named = support.commands(support.read_source(support.TEMPLATE_HOOKS))
    unwired = [name for name in scripts if not any(support.names_script(command, name) for command in named)]
    assert not unwired, f"no command of template/.rulesync/hooks.jsonc runs: {unwired}"


# ---------------------------------------------------------------------------
# S2: the comparison exempts the template's posttooluse.py entry, not the whole postToolUse event
# ---------------------------------------------------------------------------

def test_s2_the_repository_s_two_sources_as_s1_makes_them_give_no_finding(tmp_path):
    template = support.read_source(support.TEMPLATE_HOOKS)["hooks"]
    post = template["postToolUse"]
    if not any(support.names_script(e["command"], "context_watch.py") for e in post):
        post.append(support.adopted_context_watch())   # S1's line, whether or not the tree already has it
    root = support.plant_root(tmp_path, template, support.read_source(support.ROOT_HOOKS)["hooks"])
    findings = support.hooks_findings(root)
    assert findings == [], f"the root's and the template's sources, as S1 makes them, drift:\n{support.describe(findings)}"


def test_s2_the_posttooluse_entry_beside_the_root_s_one_entry_is_no_finding(tmp_path):
    template = {"postToolUse": [entry("posttooluse.py", "Bash"), entry("context_watch.py", "Bash", 10)],
                "stop": [entry("stop.py")]}
    root_hooks = {"postToolUse": [entry("context_watch.py", "Bash", 10, adopted=False)],
                  "stop": [entry("stop.py", adopted=False)]}
    findings = support.hooks_findings(support.plant_root(tmp_path, template, root_hooks))
    assert findings == [], f"the exempt posttooluse.py entry counted as drift:\n{support.describe(findings)}"


def test_s2_post_tool_use_failure_carrying_only_posttooluse_is_no_finding(tmp_path):
    template = {"postToolUse": [entry("context_watch.py", "Bash", 10)],
                "postToolUseFailure": [entry("posttooluse.py", "Bash")]}
    root_hooks = {"postToolUse": [entry("context_watch.py", "Bash", 10, adopted=False)]}
    findings = support.hooks_findings(support.plant_root(tmp_path, template, root_hooks))
    assert findings == [], f"postToolUseFailure with the exempt entry alone counted as drift:\n{support.describe(findings)}"


def test_s2_a_template_with_only_the_posttooluse_entries_and_no_root_event_is_no_finding(tmp_path):
    template = {"postToolUse": [entry("posttooluse.py", "Bash")], "postToolUseFailure": [entry("posttooluse.py", "Bash")],
                "stop": [entry("stop.py")]}
    root_hooks = {"stop": [entry("stop.py", adopted=False)]}
    findings = support.hooks_findings(support.plant_root(tmp_path, template, root_hooks))
    assert findings == [], f"DEC-971 item 3's lift no longer holds for the posttooluse.py entries:\n{support.describe(findings)}"


# ---------------------------------------------------------------------------
# F1: a hook that really drifts is still a finding
# ---------------------------------------------------------------------------

def _drift(findings, event, code=None):
    named = [f for f in findings if support.names_event(f, event)]
    assert named, f"no hooks finding names {event}:\n{support.describe(findings)}"
    assert all(f["code"] in support.HOOKS_CODES for f in named), support.describe(named)
    if code:
        assert any(f["code"] == code for f in named), f"expected {code}:\n{support.describe(named)}"


def _s1_template():
    return {"postToolUse": [entry("posttooluse.py", "Bash"), entry("context_watch.py", "Bash", 10)],
            "postToolUseFailure": [entry("posttooluse.py", "Bash")], "stop": [entry("stop.py")]}


def _s1_root():
    return {"postToolUse": [entry("context_watch.py", "Bash", 10, adopted=False)], "stop": [entry("stop.py", adopted=False)]}


def test_f1_an_extra_matcher_on_the_root_s_post_tool_use_is_a_finding(tmp_path):
    root_hooks = _s1_root()
    root_hooks["postToolUse"].append(entry("context_watch.py", "Edit", 10, adopted=False))
    findings = support.hooks_findings(support.plant_root(tmp_path, _s1_template(), root_hooks))
    _drift(findings, "postToolUse", "HOOKS_MATCHER_DIFFERS")


def test_f1_a_second_template_stop_entry_with_a_matcher_is_a_finding(tmp_path):
    template = _s1_template()
    template["stop"].append(entry("stop.py", "Bash"))
    findings = support.hooks_findings(support.plant_root(tmp_path, template, _s1_root()))
    _drift(findings, "stop", "HOOKS_MATCHER_DIFFERS")


def test_f1_an_event_only_the_template_has_is_a_finding(tmp_path):
    template = _s1_template()
    template["userPromptSubmit"] = [entry("userpromptsubmit.py")]
    findings = support.hooks_findings(support.plant_root(tmp_path, template, _s1_root()))
    _drift(findings, "userPromptSubmit", "HOOKS_EVENT_DIFFERS")


def test_f1_a_template_post_tool_use_entry_other_than_posttooluse_with_no_root_event_is_a_finding(tmp_path):
    template = {"postToolUse": [entry("posttooluse.py", "Bash"), entry("context_watch.py", "Bash", 10)]}
    findings = support.hooks_findings(support.plant_root(tmp_path, template, {"stop": [entry("stop.py", adopted=False)]}))
    _drift(findings, "postToolUse")


def test_f1_a_template_post_tool_use_failure_entry_other_than_posttooluse_with_no_root_event_is_a_finding(tmp_path):
    template = {"postToolUseFailure": [entry("posttooluse.py", "Bash"), entry("context_watch.py", "Bash", 10)]}
    findings = support.hooks_findings(support.plant_root(tmp_path, template, {"stop": [entry("stop.py", adopted=False)]}))
    _drift(findings, "postToolUseFailure")


# ---------------------------------------------------------------------------
# S3: W1-38's fixture copies the seven kernel hooks
# ---------------------------------------------------------------------------

def test_s3_the_w1_38_fixture_copies_exactly_the_kernel_hooks(tmp_path):
    import sys
    if str(support.W1_38) not in sys.path:
        sys.path.insert(0, str(support.W1_38))
    import w1_38_support as fixture
    kernel = sorted(path.name for path in support.KERNEL_HOOKS.glob("*.py"))
    assert sorted(fixture.HOOK_SCRIPTS) == kernel, f"HOOK_SCRIPTS {sorted(fixture.HOOK_SCRIPTS)} is not the kernel's {kernel}"
    project = tmp_path / "project"
    fixture.build_project_from_template(project)
    copied = sorted(path.name for path in (project / "governance" / "kernel" / "hooks").glob("*.py"))
    assert copied == kernel, f"the adopted-project fixture holds {copied}, the kernel has {kernel}"


# ---------------------------------------------------------------------------
# The map is whole
# ---------------------------------------------------------------------------

def test_the_readme_maps_every_case_of_this_folder():
    import ast
    tree = ast.parse(support.HERE.joinpath("test_w2_185_hooks.py").read_text(encoding="utf-8"))
    defined = sorted(f"{support.OWN_PREFIX}test_w2_185_hooks.py::{n.name}" for n in tree.body
                     if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    assert defined == sorted(support.own_node_ids()), "README map and this file's cases differ"
