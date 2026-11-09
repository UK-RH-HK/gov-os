"""ACT-INDEP-WALLS-1: the guard check cases, by class of action (never a worked bypass).

  python3 walls_check.py repo <tree> [hook]        the tree's hook (default <tree>/.claude/hooks/pretooluse.py) under
                                                   the pinned judge, with event JSON, as guard4_check.py does
  python3 walls_check.py wall <sets root>          template/wall_hook.py on the walls built under <sets root>/indep-walls
                                                   (writer/R1, checker/R1, labeller/R1 by build_wall.py), and checks
                                                   on each built wall's files

repo: (W) the walls under the sets root are refused to the six roles, their subagents, a lead and the tuner, for reads,
writes and the line rule, while the launch script's own line (only --sets-root <root>), the open neighbours and the
sessions no rule names stay allowed; (T) SANDBOX-GUARD-EXP-1's tuner (an engineer on W2-56, its subagents included) is
refused ~/.claude/projects and the sealed folder, while every other session (the CTO's tools, an engineer on another
ticket, the CTO's engineer subagent) is not. WALLS_EXPECT=before expects the answers before the ACT. SETS_PLANTED=1 runs
the R cases (planted files). A case naming ~ or $HOME for the sets root runs only when the block's root is ~/gov-os-eval
as this HOME expands it. The ~/.claude/projects cases name only files that do not exist (L).
wall: the wall hook's classes (reads in and out of the wall, climbing out, links, writes, tools, fail closed) and the
built walls' settings, tree, seed and manifest.
Prints one line per case and a last line PASS or FAIL. Reads no file under the real sets root or ~/.claude/projects.
"""
import fnmatch
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1] if len(sys.argv) > 1 else ""
PY = os.environ.get("GOV_PIN_PY") or open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
BEFORE = os.environ.get("WALLS_EXPECT") == "before"
PLANTED = os.environ.get("SETS_PLANTED") == "1"
HOME_NOW = os.path.realpath(os.path.expanduser("~"))
CASES = []


def case(cid, roles, tool, tins, want, tag, before=None, **extra):
    b = before or ("allow" if want == "deny" else want)
    for label, role, agent in roles:
        for tin in tins:
            form = tin.get("command") or tin.get("file_path") or f"{tin.get('path')} {tin.get('pattern', '')}"
            CASES.append((f"{cid} {label} {tool}: {form}", role, tool, tin, b if BEFORE else want,
                          dict(extra, tag=tag, agent=agent)))


def R_(p):
    return {"file_path": p}


def B_(c):
    return {"command": c}


# -- repo: the repository's guard ---------------------------------------------------------------------------------
def repo_cases(tree):
    import yaml
    block = yaml.safe_load(open(tree + "/governance/project/path-map.yaml")).get("sets_root_hidden") or {}
    sr = os.path.realpath(os.path.expanduser(block.get("root", "~/gov-os-eval")))
    same_home = sr == os.path.realpath(os.path.expanduser("~/gov-os-eval"))
    W = sr + "/indep-walls"
    w1 = W + "/writer/R1"
    NX = "zz-walls-none.txt"
    P = HOME_NOW + "/.claude/projects"
    PX = P + "/zz-walls-none-project/zz-walls-none.jsonl"
    X = sr + "/fixtures/evaluation/sandbox-guard-exp-1/hidden"
    LX = "tools/indep_launch.py"  # the launch script, named only
    M = [("engineer", "engineer", None), ("research", "research", None), ("orchestrator (the CTO)", "orchestrator", None),
         ("lead", "orchestrator@DAEO-0uhh", None), ("product-spec", "product-spec", None),
         ("test designer", "independent-test-designer", None), ("auditor", "independent-auditor", None),
         ("CTO's engineer subagent", "orchestrator", "engineer"),
         ("CTO's general-purpose subagent", "orchestrator", "general-purpose"),
         ("the tuner (engineer@DAEO-wnnz)", "engineer@DAEO-wnnz", None)]
    U = [("no GOV_ROLE", "", None), ("ticket-lead", "ticket-lead", None)]
    pick = lambda *names: [r for r in M if r[0] in names]
    ERO = pick("engineer", "research", "orchestrator (the CTO)", "the tuner (engineer@DAEO-wnnz)")
    OL = pick("orchestrator (the CTO)", "lead")
    TUNER = [("the tuner (engineer@DAEO-wnnz)", "engineer@DAEO-wnnz", None),
             ("the tuner by WBS id (engineer@W2-56)", "engineer@W2-56", None),
             ("the tuner's subagent", "engineer@DAEO-wnnz", "general-purpose")]
    NOT_TUNER = [("engineer on another ticket", "engineer@DAEO-sdxk", None),
                 ("orchestrator (the CTO)", "orchestrator@DAEO-sdxk", None), ("lead on W2-56", "orchestrator@DAEO-wnnz", None),
                 ("CTO's engineer subagent", "orchestrator@DAEO-sdxk", "engineer"),
                 ("research on W2-56", "research@DAEO-wnnz", None), ("auditor", "independent-auditor", None),
                 ("test designer on W2-56", "independent-test-designer@DAEO-wnnz", None)] + U
    # W1-W4: the walls' contents refused to every measured role, the CTO, a lead, the subagents and the tuner
    case("W1", M, "Read", [R_(f"{w1}/{NX}"), R_(f"{w1}/out/{NX}"), R_(f"{W}/checker/R9/input/{NX}"), R_(f"{W}/APPROVED")],
         "deny", "L")
    case("W1r", M, "Read", [R_(f"{w1}/brief.md"), R_(f"{w1}/seed.txt"), R_(f"{w1}/WALL.json"),
                            R_(f"{w1}/.claude/settings.json"), R_(f"{w1}/input/selection.json")], "deny", "R")
    case("W2", ERO, "Bash", [B_(f"cat {w1}/{NX}"), B_(f"head -5 {W}/labeller/R1/out/{NX}"), B_(f"ls {w1}/out")],
         "deny", "L")
    case("W2r", ERO, "Bash", [B_(f"cat {w1}/seed.txt"), B_(f"ls {W}"), B_(f"grep -rn x {W}"),
                              B_(f"wc -l {w1}/brief.md"),
                              B_(f"python3 -c \"print(open('{w1}/WALL.json').read())\"")], "deny", "R")
    case("W3", ERO, "Grep", [{"pattern": "x", "path": w1}, {"pattern": "x", "path": W}], "deny", "R")
    case("W3l", ERO, "Glob", [{"path": W, "pattern": "**/*.md"}, {"path": f"{w1}/out", "pattern": "*"}], "deny", "R")
    case("W4", [r for r in M if r[0] != "auditor"], "Write", [{"file_path": f"{w1}/out/{NX}", "content": "x"},
                                                              {"file_path": f"{W}/APPROVED", "content": "x"}], "deny", "L")
    case("W4a", pick("auditor"), "Write", [{"file_path": f"{w1}/out/{NX}", "content": "x"}], "deny", "L", before="deny")
    case("W4b", pick("engineer", "orchestrator (the CTO)"), "Bash",
         [B_(f"echo x > {w1}/out/{NX}"), B_(f"cp /tmp/zz-walls-a {W}/APPROVED")], "deny", "L")
    # W5: the line rule: the root with indep-walls/ in every spelling, refused to the CTO and a lead
    case("W5", OL, "Bash", [B_(f"python3 {LX} --sets-root ~/gov-os-eval --wall ~/gov-os-eval/indep-walls/writer/R1"),
                            B_("cat ~/gov-os-eval/indep-walls/APPROVED"), B_('ls "$HOME/gov-os-eval/indep-walls/writer"')],
         "deny", "L", home=True)
    case("W5a", OL, "Bash", [B_(f"python3 {LX} --sets-root {sr} --out {W}/writer/R1/out")], "deny", "L")
    case("W5b", OL, "Bash", [B_(f"D={sr}; cat $D/indep-walls/writer/R1/out/{NX}"), B_(f"cd {sr} && ls indep-walls")],
         "deny", "L", before="deny")
    # W6: the launch script's own lines: only --sets-root <root>; allowed to the CTO and a lead, before and after
    case("W6", OL, "Bash", [B_(f"python3 {LX} --sets-root ~/gov-os-eval --kind writer --brief "
                               "governance/project/indep-briefs/writer.md --commit 6ff398a28 --seed new"),
                            B_(f"python3 {LX} --sets-root ~/gov-os-eval --kind labeller --run L2 --counts-only "
                               "> /tmp/zz-walls-counts.json 2>&1")], "allow", "L", home=True)
    case("W6a", OL, "Bash", [B_(f"python3 {LX} --sets-root {sr} --kind checker --commit 6ff398a28"),
                             B_(f"python3 {LX} --sets-root={sr} --kind auditor --dry")], "allow", "L")
    # W5c: prose about walls in a heredoc body or a word from a tree root: allowed (the replay's one false refusal
    # with the folder named walls/, 2026-11-09, is why the folder is indep-walls/)
    case("W5c", OL, "Bash", [B_("cat > /tmp/zz-walls-note.md <<'EOF'\nthe walls\nwalls\nEOF"), B_("echo walls"),
                             B_("grep -rn walls docs/contract")], "allow", "L")
    # W7: the sessions no rule names (the operator's own sessions run outside the guard altogether)
    case("W7", U, "Read", [R_(f"{w1}/{NX}")], "allow", "L")
    # W8: open neighbours: the counts the CTO reads, an open run folder, a repository path named walls deeper down, and
    # the walls' plain trees (the repository's own content, outside the sets root)
    case("W8", M, "Read", [R_(f"{HOME_NOW}/gov-os-runs/indep/writer/R1/{NX}"), R_(f"{sr}/runs/e0/{NX}"),
                           R_(f"{tree}/docs/walls/{NX}"), R_(f"{HOME_NOW}/gov-os-wall-trees/writer-R1/{NX}")],
         "allow", "L")
    # T1-T6: the tuner and ~/.claude/projects
    case("T1", TUNER, "Read", [R_(PX), R_(P + "/" + NX)], "deny", "L")
    case("T2", TUNER, "Grep", [{"pattern": "x", "path": P}, {"pattern": "x", "path": HOME_NOW + "/.claude"},
                               {"pattern": "x", "path": P + "/zz-walls-none-project"}], "deny", "L")
    case("T2g", TUNER, "Glob", [{"pattern": P + "/**/*.jsonl"}, {"path": HOME_NOW + "/.claude", "pattern": "projects/**"},
                                {"path": P, "pattern": "*"}], "deny", "L")
    case("T3", TUNER, "Bash", [B_(f"cat {PX}"), B_("ls ~/.claude/projects"), B_("cd ~/.claude && cat projects/zz.jsonl"),
                               B_("D=~/.claude; cat $D/projects/zz.jsonl"), B_("grep -rn x $HOME/.claude/projects"),
                               B_("find ~/.claude -name '*.jsonl'"), B_("ls ~/.claude/*/"),
                               B_(f"python3 -c \"print(open('{PX}').read())\""),
                               B_("tail -1 \"$HOME/.claude/projects/zz/zz.jsonl\"")], "deny", "L")
    case("T4", TUNER, "Write", [{"file_path": PX, "content": "x"}], "deny", "L")
    case("T4b", TUNER, "Bash", [B_(f"echo x >> {PX}")], "deny", "L")
    # T5: the tuner and the sealed folder (the seal: the engineer is a role the set measures)
    case("T5", TUNER, "Read", [R_(f"{X}/{NX}"), R_(f"{X}/corpus/{NX}")], "deny", "L")
    case("T5b", TUNER, "Bash", [B_(f"cat {X}/{NX}")], "deny", "L")
    # T6: the tuner's open work: its tree, the tuning folder, its own Claude Code files outside projects, a script
    # that opens the transcripts in its own code (a known limit: the sandbox's job; the brief forbids it)
    case("T6", TUNER, "Read", [R_(f"{tree}/README.md"), R_(f"{HOME_NOW}/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning/{NX}"),
                               R_(f"{HOME_NOW}/.claude/settings.json")], "allow", "L")
    case("T6b", TUNER, "Bash", [B_("ls ~/.claude/skills"), B_("cat ~/.claude/settings.json"),
                                B_("python3 tools/guard_refusals.py --since 2026-11-08")], "allow", "L")
    # T7: every other session reads the transcripts as before: the CTO's tools, other tickets' engineers, a lead
    case("T7", NOT_TUNER, "Read", [R_(PX)], "allow", "L")
    case("T7b", [r for r in NOT_TUNER if r[1].startswith("orchestrator")], "Bash",
         [B_("python3 tools/guard_refusals.py --since 2026-11-08"), B_("ls ~/.claude/projects"), B_(f"tail -1 {PX}")],
         "allow", "L")
    return same_home


def repo_main(tree, hook):
    same_home = repo_cases(tree)

    def decide(role, tool, tin, agent=None):
        event = {"tool_name": tool, "tool_input": tin, "cwd": tree, "session_id": "walls-check", "agent_type": agent}
        role, _, ticket = role.partition("@")
        env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "W2-00", CLAUDE_PROJECT_DIR=tree)
        env.pop("PYTHONPATH", None)
        if not role:
            env.pop("GOV_ROLE")
        p = subprocess.run([PY, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
        if p.returncode == 2:
            return "deny(exit 2)", p.stderr
        if p.stdout.strip():
            out = json.loads(p.stdout)["hookSpecificOutput"]
            return out["permissionDecision"], out["permissionDecisionReason"]
        return "allow", p.stderr

    return run(decide, same_home)


def run(decide, same_home=True):
    ok, fails, runs, skipped = True, 0, 0, {}
    for name, role, tool, tin, want, x in CASES:
        if x["tag"] == "R" and not PLANTED:
            skipped["R"] = skipped.get("R", 0) + 1
            continue
        if x.get("home") and not same_home:
            skipped["~ forms"] = skipped.get("~ forms", 0) + 1
            continue
        runs += 1
        got, why = decide(role, tool, tin, x.get("agent"))
        good = got == want or (want == "deny" and got.startswith("deny"))
        ok &= good
        fails += not good
        print(("ok   " if good else "FAIL ") + f"[{x['tag']}] {name}: want {want}, got {got}"
              + ("" if good else f" | {(why or '')[-200:]}"))
    print(f"{MODE} cases: {len(CASES)}, run: {runs}, failed: {fails}, expect: {'before' if BEFORE else 'after'}, "
          "skipped: " + (", ".join(f"{k}: {v}" for k, v in skipped.items()) or "none"))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


# -- wall: the wall hook and the built walls ----------------------------------------------------------------------
def wall_main(sr):
    sr = os.path.realpath(sr)
    W = sr + "/indep-walls"
    w = W + "/writer/R1"
    c = W + "/checker/R1"
    hook = os.path.join(HERE, "template", "wall_hook.py")
    S = [("writer R1", w, None)]
    NX = "zz-walls-none.txt"
    wt = json.load(open(w + "/WALL.json"))["tree"]
    ct = json.load(open(c + "/WALL.json"))["tree"]
    tf = next(os.path.join(dp, n) for dp, _d, ns in os.walk(wt) for n in ns)
    # H1: reads inside its own wall
    case("H1", S, "Read", [R_(f"{w}/brief.md"), R_("seed.txt"), R_(f"{w}/WALL.json"), R_(tf), R_(wt + "/README.md"),
                           R_("input/selection.json"), R_(f"{w}/out/{NX}")], "allow", "W")
    case("H1g", S, "Grep", [{"pattern": "x"}, {"pattern": "x", "path": wt}, {"pattern": "x", "path": w}],
         "allow", "W")
    case("H1b", S, "Glob", [{"pattern": wt + "/**/*.md"}, {"pattern": "**/*.py", "path": wt}], "allow", "W")
    # H2: reads outside it: another wall of its kind and of another kind, the rest of the sets root, the approved
    # list, the repository, the worktrees, the run outputs, the transcripts, the system
    outside = [f"{W}/writer/R2/brief.md", f"{c}/brief.md", f"{ct}/README.md", os.path.dirname(wt) + "/zz-other/x", f"{c}/out/{NX}", f"{W}/labeller/R1/seed.txt",
               f"{W}/APPROVED", f"{sr}/fixtures/evaluation/memory-verdict-2/hidden/p01.yaml", f"{sr}/runs/e0/counts.txt",
               f"{sr}/transcripts/t01.md", "/home/usain/Dynamic-Agentic-Engineering-OS/CLAUDE.md",
               "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/RESUME.md",
               f"{HOME_NOW}/gov-os-worktrees/W2-56/README.md", f"{HOME_NOW}/gov-os-runs/indep/SEEDS.log",
               f"{HOME_NOW}/.claude/projects/zz/zz.jsonl", "/etc/hostname"]
    case("H2", S, "Read", [R_(p) for p in outside], "deny", "W")
    case("H2g", S, "Grep", [{"pattern": "x", "path": W}, {"pattern": "x", "path": c}, {"pattern": "x", "path": sr},
                            {"pattern": "x", "path": os.path.dirname(wt)}, {"pattern": "x", "path": ct},
                            {"pattern": "x", "path": HOME_NOW}], "deny", "W")
    case("H2b", S, "Glob", [{"pattern": f"{W}/**"}, {"pattern": "*", "path": c}], "deny", "W")
    # H3: climbing out by .. (a path, a Grep start, a Glob head or a Glob tail after a wildcard)
    case("H3", S, "Read", [R_("input/../../R2/brief.md"), R_("../../checker/R1/brief.md"), R_(wt + "/../" + os.path.basename(ct) + "/README.md")],
         "deny", "W")
    case("H3g", S, "Grep", [{"pattern": "x", "path": ".."}], "deny", "W")
    case("H3b", S, "Glob", [{"pattern": "../**"}, {"pattern": "input/*/../../../**"}, {"pattern": "**/../../*"},
                            {"pattern": "*/../../*", "path": wt}],
         "deny", "W")
    # H4: links (planted by the rehearsal in out/: out/link-out -> the checker's wall, out/link-in -> its own brief)
    case("H4", S, "Read", [R_(f"{w}/out/link-out/brief.md")], "deny", "W")
    case("H4a", S, "Read", [R_(f"{w}/out/link-in")], "allow", "W")
    case("H4w", S, "Write", [{"file_path": f"{w}/out/link-out/x", "content": "x"},
                             {"file_path": f"{w}/out/link-in", "content": "x"}], "deny", "W")
    # H5: writes: only into out/
    case("H5", S, "Write", [{"file_path": f"{w}/out/result.json", "content": "{}"},
                            {"file_path": "out/set/q01.yaml", "content": "x"}], "allow", "W")
    case("H5e", S, "Edit", [{"file_path": f"{w}/out/result.json", "old_string": "a", "new_string": "b"}], "allow", "W")
    case("H5d", S, "Write", [{"file_path": p, "content": "x"} for p in
                             [tf, wt + "/zz-new.txt", f"{w}/.claude/settings.json", f"{w}/.claude/wall_hook.py", f"{w}/brief.md",
                              f"{w}/seed.txt", f"{w}/WALL.json", f"{w}/CLAUDE.md", f"{w}/input/selection.json",
                              f"{w}/out", f"{w}/x.txt", f"{c}/out/x", f"{W}/APPROVED", "/tmp/zz-walls-x",
                              "out/../x.txt"]], "deny", "W")
    case("H5m", S, "MultiEdit", [{"file_path": f"{w}/.claude/settings.json", "edits": []}], "deny", "W")
    # H6: tools: no shell, web, subagent, notebook, skill, MCP or unnamed tool
    for t, tin in [("Bash", B_("ls")), ("Bash", B_("cat brief.md")), ("WebFetch", {"url": "https://example.com"}),
                   ("WebSearch", {"query": "x"}), ("Task", {"prompt": "x"}), ("Agent", {"prompt": "x"}),
                   ("NotebookEdit", {"notebook_path": f"{w}/out/x.ipynb"}), ("Skill", {"skill": "x"}),
                   ("mcp__docs__read", {"id": "x"}), ("ZzUnknown", {})]:
        case("H6", S, t, [tin], "deny", "W")
    case("H6t", S, "TodoWrite", [{"todos": []}], "allow", "W")
    # H7: fail closed
    case("H7", S, "Read", [{"file_path": 7}, {"file_path": ""}], "deny", "W")
    case("H7c", [("writer R1, cwd outside the wall", w, "cwd:/tmp")], "Read", [R_(f"{w}/brief.md")], "deny", "W")
    case("H7m", [("writer R1, no input", w, "malformed")], "Read", [R_(f"{w}/brief.md")], "deny", "W")
    case("H7a", [("writer R1, no wall argument", w, "noarg")], "Read", [R_(f"{w}/brief.md")], "deny", "W")

    def decide(wall, tool, tin, how=None):
        cwd = "/tmp" if how == "cwd:/tmp" else wall
        event = {"tool_name": tool, "tool_input": tin, "cwd": cwd}
        text = "{not json" if how == "malformed" else json.dumps(event)
        args = ["python3", "-I", hook] + ([] if how == "noarg" else [wall, wt])
        p = subprocess.run(args, input=text, capture_output=True, text=True, timeout=30, env={"PATH": "/usr/bin:/bin"})
        if p.returncode == 2:
            return "deny(exit 2)", p.stderr
        if p.returncode != 0:
            return f"error({p.returncode})", p.stderr
        if p.stdout.strip():
            out = json.loads(p.stdout)["hookSpecificOutput"]
            return out["permissionDecision"], out["permissionDecisionReason"]
        return "allow", ""

    rc = run(decide)
    return built_checks(sr) or rc


def built_checks(sr):
    """F: each built wall's files: the settings, the tree, the seed and the manifest."""
    W = sr + "/indep-walls"
    tmpl = os.path.join(HERE, "template")
    ex = [l.strip() for l in open(os.path.join(tmpl, "tree-exclude.txt")) if l.strip() and not l.startswith("#")]
    fails, n = 0, 0
    home = HOME_NOW

    def check(name, cond):
        nonlocal fails, n
        n += 1
        fails += not cond
        print(("ok   " if cond else "FAIL ") + "[F] " + name)

    def sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()

    for kind in sorted(os.listdir(W)):
        if kind == "APPROVED":
            continue
        if not os.path.isdir(os.path.join(W, kind)):
            continue
        for run_id in sorted(os.listdir(os.path.join(W, kind))):
            w = os.path.join(W, kind, run_id)
            tag = f"{kind}/{run_id}"
            s = json.load(open(w + "/.claude/settings.json"))
            m = json.load(open(w + "/WALL.json"))
            deny, allow = s["permissions"]["deny"], s["permissions"].get("allow", [])
            check(f"{tag}: settings' sha256 is the manifest's", sha(w + "/.claude/settings.json") == m["settings_sha256"])
            check(f"{tag}: the hook's sha256 is the template's", sha(w + "/.claude/wall_hook.py") == sha(tmpl + "/wall_hook.py"))
            check(f"{tag}: the brief's sha256 is the manifest's", sha(w + "/brief.md") == m["brief_sha256"])
            check(f"{tag}: no allow rule opens a shell, the web or a path outside the wall and its tree; writes out/ only",
                  all(not a.startswith(("Bash", "WebFetch", "WebSearch")) and (f"/{w}/" in a or f"/{m['tree']}/" in a)
                      for a in allow) and all(f"/{w}/out/" in a for a in allow if a.startswith(("Edit", "Write"))))
            need = ["Bash", "WebFetch", "WebSearch", "Task", "Bash(gov retrieve *)", "Bash(gov context *)", "Bash(git *)",
                    f"Read(/{m['runs']}/**)", f"Read(/{m['home']}/.claude/**)", f"Read(/{m['repo']}/**)",
                    f"Read(/{sr}/runs/**)", f"Read(/{sr}/transcripts/**)", f"Read(/{sr}/fixtures/**)",
                    f"Read(/{W}/APPROVED)", f"Edit(/{w}/.claude/**)", f"Edit(/{m['tree']}/**)"]
            need += [f"Read(/{W}/{k}/**)" for k in ("writer", "checker", "auditor", "labeller") if k != kind]
            need += [f"Read(/{W}/{kind}/{r}/**)" for r in sorted(os.listdir(os.path.join(W, kind)))
                     if r != run_id and os.stat(os.path.join(W, kind, r)).st_mtime <= os.stat(w + "/WALL.json").st_mtime]
            missing = [x for x in need if x not in deny]
            check(f"{tag}: the deny list holds every required class ({len(need)}){' missing ' + str(missing) if missing else ''}",
                  not missing)
            hooks = s["hooks"]["PreToolUse"]
            check(f"{tag}: the one hook is the wall's own, on every tool",
                  len(hooks) == 1 and hooks[0]["matcher"] == "*" and
                  hooks[0]["hooks"][0]["command"] == f"python3 -I {w}/.claude/wall_hook.py {w} {m['tree']}")
            links, present, writable = 0, [], 0
            for dp, dn, fn in os.walk(m["tree"]):
                for x in dn + fn:
                    fp = os.path.join(dp, x)
                    rel = fp[len(m["tree"]) + 1:]
                    links += os.path.islink(fp)
                    writable += os.access(fp, os.W_OK)
                    if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in ex):
                        present.append(rel)
            check(f"{tag}: the tree holds no link", links == 0)
            check(f"{tag}: the tree holds no excluded path ({len(present)})", not present)
            check(f"{tag}: the tree is read-only ({writable} writable)", writable == 0)
            check(f"{tag}: the seed was written before the content", m["seeded_before_content"] is True and
                  os.stat(w + "/seed.txt").st_mtime <= os.stat(w + "/input/selection.json").st_mtime)
            check(f"{tag}: the seed's sha256 is the manifest's", sha(w + "/seed.txt") == m["seed_sha256"])
            check(f"{tag}: the tree lies outside the sets root and outside the wall",
                  not m["tree"].startswith(sr + "/"))
            check(f"{tag}: the wall itself holds few files ({sum(len(f) for _a, _b, f in os.walk(w))})",
                  sum(len(f) for _a, _b, f in os.walk(w)) <= 50)
            check(f"{tag}: the wall's root, .claude and input are read-only",
                  not any(os.access(p, os.W_OK) for p in (w, w + "/.claude", w + "/input")))
    print(f"built-wall checks: {n}, failed: {fails}")
    print("PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    if MODE == "repo" and len(sys.argv) >= 3:
        t = os.path.realpath(sys.argv[2])
        sys.exit(repo_main(t, sys.argv[3] if len(sys.argv) > 3 else t + "/.claude/hooks/pretooluse.py"))
    if MODE == "wall" and len(sys.argv) == 3:
        sys.exit(wall_main(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
