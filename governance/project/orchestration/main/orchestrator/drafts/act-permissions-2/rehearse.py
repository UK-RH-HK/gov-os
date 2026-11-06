#!/usr/bin/env python3
"""ACT-PERMISSIONS-2's rehearsal (DEC-1057).

A, the file: the operator's steps exactly on a copy of the real settings file (only the path substituted); the real
file hashed before and after.
B, the behaviour: headless Claude Code sessions (Haiku, `claude -p`) in a stand-in project, with settings that
apply.py writes for stand-in folders (only the paths substituted). Planted dummy files only; nothing real is read.
  B1, the ACT's settings: a Read in an added folder is allowed; a Read in a hidden folder is denied.
  B2, the control (the stand-in sets root also added as a directory): a visible file reads, the three hidden ones are
      still denied (so the deny rule, not the missing directory, refuses them); a Bash python read of a hidden file
      works (the measure's own path: its code reads the files, not the Read tool).

    python3 rehearse.py <scratch folder>
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REAL = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json")
APPLY = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-PERMISSIONS-2/apply.py")
CLAUDE = Path.home() / ".local/bin/claude"
S = Path(sys.argv[1]).resolve()
shutil.rmtree(S, ignore_errors=True)
S.mkdir(parents=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
real_before = sha(REAL)
fails = 0


def ok(name, cond, detail=""):
    global fails
    fails += not cond
    print(f"{'ok  ' if cond else 'FAIL'} {name}{(': ' + str(detail)[:300]) if detail and not cond else ''}")


def apply(target, *args):
    return subprocess.run([sys.executable, "-I", str(APPLY), str(target), *args], capture_output=True, text=True)


# ---- A: the file
copy = S / "A" / "settings.local.json"
copy.parent.mkdir()
shutil.copy2(REAL, copy)
old = json.loads(copy.read_text())
r = apply(copy, "--check"); ok("A1 check before: missing (exit 1)", r.returncode == 1, r.stdout + r.stderr)
r = apply(copy); ok("A2 apply", r.returncode == 0 and "2 director(ies) and 3 deny rule(s) added" in r.stdout, r.stdout + r.stderr)
r = apply(copy, "--check"); ok("A3 check after: all present (exit 0)", r.returncode == 0, r.stdout + r.stderr)
r = apply(copy); ok("A4 apply again: nothing added", r.returncode == 0 and "0 director(ies) and 0 deny rule(s)" in r.stdout, r.stdout)
new = json.loads(copy.read_text())
p_old, p_new = old.get("permissions", {}), new["permissions"]
ok("A5 allow unchanged", p_new.get("allow") == p_old.get("allow"))
ok("A6 ask unchanged", p_new.get("ask") == p_old.get("ask"))
ok("A7 the old deny rules kept, in order, then the three", p_new["deny"][:len(p_old.get("deny", []))] == p_old.get("deny", [])
   and p_new["deny"][len(p_old.get("deny", [])):] == [
       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/**)",
       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/**)",
       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)"], p_new["deny"])
ok("A8 the two directories, and not the sets root",
   p_new.get("additionalDirectories") == ["/home/usain/gov-os-runs", "/home/usain/gov-os-worktrees"], p_new.get("additionalDirectories"))
ok("A9 the other keys unchanged", {k: v for k, v in new.items() if k != "permissions"} == {k: v for k, v in old.items() if k != "permissions"})
r = apply(copy, "--undo"); ok("A10 undo", r.returncode == 0, r.stderr)
ok("A11 after undo the copy equals the original byte for byte", sha(copy) == real_before)

# ---- B: the behaviour, on stand-ins
proj, runs, wt, ev = S / "B/proj", S / "B/runs", S / "B/wt", S / "B/eval"
files = {
    "runs": runs / "r.txt",
    "visible": ev / "fixtures/evaluation/memory-retrieval/visible/v.yaml",
    "hidden": ev / "fixtures/evaluation/memory-retrieval/hidden/h.yaml",
    "verdict": ev / "fixtures/evaluation/memory-verdict/m.yaml",
    "verdict2": ev / "fixtures/evaluation/memory-verdict-2/n.yaml",
}
for d in (proj, wt):
    d.mkdir(parents=True)
for name, f in files.items():
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"TOKEN-{name.upper()}-7Q\n")
sub = ["--runs", str(runs), "--worktrees", str(wt), "--eval", str(ev)]
b1, b2 = S / "B/b1.json", S / "B/b2.json"
b1.write_text("{}\n")
r = apply(b1, *sub); ok("B0 apply.py writes the stand-in settings", r.returncode == 0, r.stdout + r.stderr)
cfg = json.loads(b1.read_text())
cfg2 = json.loads(json.dumps(cfg))
cfg2["permissions"]["additionalDirectories"].append(str(ev))
b2.write_text(json.dumps(cfg2, indent=2))


def session(settings: Path, steps: list[tuple[str, str]]) -> tuple[str, list]:
    lines = "\n".join(f"{i}. {how}" for i, (_, how) in enumerate(steps, 1))
    prompt = (f"Do exactly these steps, nothing else, each as one tool call, and then answer with one line per step "
              f"in the form `<n>: <the file's text or the command's output, or DENIED if the tool call was refused>`.\n"
              f"{lines}")
    r = subprocess.run([str(CLAUDE), "-p", prompt, "--settings", str(settings), "--model", "claude-haiku-5-5",
                        "--output-format", "json", "--max-turns", str(len(steps) + 3)],
                       cwd=proj, capture_output=True, text=True, timeout=600)
    try:
        out = json.loads(r.stdout)
    except ValueError:
        return r.stdout + r.stderr, []
    return str(out.get("result", "")), out.get("permission_denials") or []


def denied_paths(denials):
    return {str((d.get("tool_input") or {}).get("file_path", "")) for d in denials if d.get("tool_name") == "Read"}


text1, den1 = session(b1, [("runs", f"Read the file {files['runs']} with the Read tool."),
                            ("hidden", f"Read the file {files['hidden']} with the Read tool.")])
print(f"     B1 answer: {text1.strip()[:200]!r}; Read denials: {sorted(denied_paths(den1))}")
ok("B1 the added folder reads without a prompt", "TOKEN-RUNS-7Q" in text1 and str(files["runs"]) not in denied_paths(den1), text1)
ok("B1b the hidden file is refused", "TOKEN-HIDDEN-7Q" not in text1, text1)

reader = S / "B/reader.py"  # the measure's form: given the sets root only, its own code opens the hidden files
reader_out = S / "B/reader.out"  # judged from this file, not from the session's answer (a model may withhold it)
reader.write_text("import sys, pathlib\nroot = pathlib.Path(sys.argv[1])\n"
                  "text = (root / 'fixtures/evaluation/memory-retrieval/hidden/h.yaml').read_text().strip()\n"
                  f"pathlib.Path({str(reader_out)!r}).write_text(text)\nprint('read', len(text), 'characters')\n")
steps2 = [("visible", f"Read the file {files['visible']} with the Read tool."),
          ("hidden", f"Read the file {files['hidden']} with the Read tool."),
          ("verdict", f"Read the file {files['verdict']} with the Read tool."),
          ("verdict2", f"Read the file {files['verdict2']} with the Read tool."),
          ("python", f"Run with the Bash tool: python3 {reader} {ev}"),
          ("literal", f"Run with the Bash tool: cat {files['verdict']}")]
text2, den2 = session(b2, steps2)
print(f"     B2 answer: {text2.strip()!r}")
print(f"     B2 denials: {json.dumps(den2)[:1200]}")
lit = [ln for ln in text2.splitlines() if ln.startswith("6:")]
print(f"     B2 information (not judged): a Bash cat naming a hidden file: {lit[0] if lit else 'no line'}")
ok("B2 control: with the sets root added, a visible file reads", "TOKEN-VISIBLE-7Q" in text2, text2)
ok("B2b control: memory-retrieval/hidden still refused by the deny rule",
   str(files["hidden"]) in denied_paths(den2), den2)
ok("B2c control: memory-verdict still refused", str(files["verdict"]) in denied_paths(den2) and "TOKEN-VERDICT-7Q" not in text2, den2)
ok("B2d control: memory-verdict-2 still refused", str(files["verdict2"]) in denied_paths(den2) and "TOKEN-VERDICT2-7Q" not in text2, den2)
bash_denied = [d for d in den2 if d.get("tool_name") == "Bash" and str(reader) in str((d.get("tool_input") or {}).get("command", ""))]
ok("B2e the measure's path (its own code given the sets root, through Bash) still reads the hidden file",
   not bash_denied and reader_out.is_file() and reader_out.read_text() == "TOKEN-HIDDEN-7Q", bash_denied or "no output file")
ok("B2f a Bash cat naming a hidden file is refused too (the deny rule reaches the shell's plain reads)",
   any(d.get("tool_name") == "Bash" and "cat " in str((d.get("tool_input") or {}).get("command", "")) for d in den2), den2)

ok("C the real settings file unchanged throughout (sha256 " + real_before[:12] + ")", sha(REAL) == real_before)
print("REHEARSAL PASS" if not fails else f"REHEARSAL FAILED {fails}")
sys.exit(1 if fails else 0)
