"""Writes checks.json: the manifest's checks for ACT-GUARD-FIX-5 (none names a live HOME or repository path)."""
import json

H = ".claude/hooks/bash_writes.py"

parse = f"python3 -B -I -c 'import ast; ast.parse(open(\"{H}\").read())'"

shape = f'''python3 -B -I -c 'import re, sys
t = open("{H}").read()
kind = t[t.index("\\ndef _kind(words):"):t.index("\\n_SHELL_FLAGS")]
new = t[t.index("\\n_SHELL_FLAGS"):t.index("\\n_PARAM = ")]
ok = (t.count("\\ndef _shell_kind(args):\\n") == 1 and t.count("_shell_kind(") == 2
      and "    if name in _SHELLS:\\n        return _shell_kind(args)\\n    return \\"data\\" if name in _DATA else \\"code\\"\\n" in kind
      and "\\"/dev/stdin\\"" in new and "\\"/dev/fd/0\\"" in new and "\\"--rcfile\\"" in new and "\\"--init-file\\"" in new
      and t.count("                        if kind in (\\"data\\", \\"shell\\"):\\n") == 1
      and "        elif kind == \\"shell\\" and (body[\\"quoted\\"] or not (_EXPANSION.search(body[\\"text\\"]) or \\"\\\\\\\\\\" in body[\\"text\\"])):\\n" in t
      and t.index("\\ndef _kind(") < t.index("\\n_SHELL_FLAGS") < t.index("\\ndef _shell_kind(") < t.index("\\n_PARAM = ")
      and not any(b in new for b in ("subprocess", "open(", "write", "os.", "import ")))
sys.exit(0 if ok else 1)'
'''

bed = '''python3 -B -I - <<'EOF'
import importlib.util, random, sys
spec = importlib.util.spec_from_file_location("bash_writes_bed", ".claude/hooks/bash_writes.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
SHELL, DATA = "shell", "data"
TABLE = (
    ("bash -euo pipefail", SHELL), ("bash -o pipefail", SHELL), ("bash -O extglob", SHELL), ("bash +o history", SHELL),
    ("bash +O extglob", SHELL), ("bash -oe pipefail", SHELL), ("bash --rcfile f", SHELL), ("bash --init-file f", SHELL),
    ("zsh -o pipefail", SHELL), ("bash -o a -O b", SHELL), ("bash -oo a b", SHELL), ("bash -", SHELL),
    ("bash /dev/stdin", SHELL), ("bash /dev/fd/0", SHELL), ("bash -eu -", SHELL), ("bash -s", SHELL), ("bash", SHELL),
    ("bash --nosuchoption", SHELL), ("bash --nosuchoption script.sh", SHELL), ("bash -Z script.sh", SHELL),
    ("bash -c x", DATA), ("bash -ec x", DATA), ("bash -euo pipefail -c x", DATA), ("bash -Z -c x", DATA),
    ("bash script.sh", DATA), ("bash -x script.sh", DATA), ("bash -o pipefail script.sh", DATA),
    ("bash -euo pipefail script.sh", DATA), ("bash -O extglob script.sh", DATA), ("bash --rcfile f script.sh", DATA),
    ("bash --norc script.sh", DATA), ("sh script.sh", DATA), ("cat", DATA), ("tee x", DATA))
bad = []
for words, want in TABLE:
    got = bw._kind(words.split())
    if got != want:
        bad.append(f"{words!r}: {got}, not {want}")


def old_kind(args):
    opts = [a for a in args if a.startswith("-")]
    operands = [a for a in args if not a.startswith("-")]
    if any("c" in o.lstrip("-") for o in opts if not o.startswith("--")):
        return DATA
    return SHELL if not operands or "-s" in opts else DATA


# stricter only: a shell the old reading took as reading its input is still read so (2,000 seeded random argument lists)
rng = random.Random(5)
words = ["-e", "-u", "-x", "-euo", "-o", "-O", "+o", "+O", "-c", "-s", "-ec", "-es", "-i", "-l", "-", "--", "--norc",
         "--rcfile", "--init-file", "--posix", "--login", "--zzz", "-Z", "pipefail", "extglob", "f", "script.sh",
         "/dev/stdin", "/dev/fd/0", "a b"]
for _ in range(2000):
    args = [rng.choice(words) for _ in range(rng.randint(0, 5))]
    if old_kind(args) == SHELL and bw._kind(["bash"] + args) != SHELL:
        bad.append(f"stricter-only broken by {args}")
        break
print("; ".join(bad) or "bash_writes: a shell's option values are not its script; standard input and unknown options read as shell; -c is data; never less strict")
sys.exit(1 if bad else 0)
EOF
'''

hook = """python3 -B -I - <<'EOF'
import json, os, subprocess, sys, tempfile
root = os.getcwd()
calls = tempfile.mkdtemp()
T = "tests/acceptance/X/zz.py"
E, TD = "engineer", "independent-test-designer"
CASES = [
    # refused: every spelling, quoted and unquoted, as an engineer writing under tests/acceptance/
    (E, f"bash -euo pipefail <<'EOT'\\necho x > {T}\\nEOT", "deny"),
    (E, f"bash -o pipefail <<'EOT'\\necho x > {T}\\nEOT", "deny"),
    (E, f"bash --rcfile /dev/null <<'EOT'\\necho x > {T}\\nEOT", "deny"),
    (E, f"cat <<'EOF' | bash -o pipefail\\necho x > {T}\\nEOF", "deny"),
    (E, f"bash /dev/stdin <<'EOT'\\necho x > {T}\\nEOT", "deny"),
    (E, f"bash -eu -o pipefail <<EOF\\ntouch {T}\\nEOF", "deny"),
    (E, f"bash <<EOF\\ntouch {T}\\nEOF", "deny"),
    (E, f"bash -o pipefail <<EOF\\necho $(touch {T})\\nEOF", "deny"),
    (E, f"bash -euo pipefail <<EOF\\necho `touch {T}`\\nEOF", "deny"),
    (E, "bash -o pipefail <<EOF\\necho $(rm -rf tests/acceptance/X)\\nEOF", "deny"),
    (E, f"cat <<EOF | bash -o pipefail\\necho $(touch {T})\\nEOF", "deny"),
    (E, f"bash -o pipefail > s.sh <<EOF\\ntouch {T} $(date +%s)\\nEOF\\nbash s.sh", "deny"),
    (E, f"tee s.sh <<EOF | bash -o pipefail\\ntouch {T} $(date +%s)\\nEOF\\nbash s.sh", "deny"),
    # allowed, as before
    (TD, f"bash -euo pipefail <<'EOT'\\necho x > {T}\\nEOT", "allow"),
    (E, f"cat <<EOF\\ntouch {T}\\nEOF", "allow"),
    (E, f"bash script.sh <<EOF\\ntouch {T}\\nEOF", "allow"),
    (E, f"bash -o pipefail script.sh <<EOF\\ntouch {T}\\nEOF", "allow"),
    (E, f"bash -c 'echo hi' <<EOF\\ntouch {T}\\nEOF", "allow"),
    (E, "bash -o pipefail <<EOF\\necho $(date)\\nEOF", "allow"),
    (E, "bash -o pipefail <<'EOF'\\necho hi\\nEOF", "allow"),
]
bad = []
for role, command, want in CASES:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON") and not k.startswith("GOV_")}
    env.update(PYTHONPATH=os.path.join(root, "src"), PYTHONDONTWRITEBYTECODE="1", GOV_ROLE=role, GOV_TICKET="DAEO-03ub",
               CLAUDE_PROJECT_DIR=root, GOV_GUARD_CALLS_DIR=calls)
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": root, "session_id": "check"}
    p = subprocess.run([sys.executable, "-B", ".claude/hooks/pretooluse.py"], input=json.dumps(event),
                       capture_output=True, text=True, env=env, timeout=120, cwd=root)
    if p.returncode == 2:
        got = "deny"
    elif p.returncode:
        got = "error"
    else:
        got = json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow"
    if got != want:
        bad.append(f"{role}: {command.splitlines()[0][:50]}: {got}, not {want}")
print("; ".join(bad) or "the hook, as an engineer writing under tests/acceptance/: every shell spelling, quoted or not, a substitution in an unquoted body, and a body written to a file and run are refused; the controls pass")
sys.exit(1 if bad else 0)
EOF
"""
json.dump([parse, shape, bed, hook], open("checks.json", "w"), indent=1)
print("ok")
