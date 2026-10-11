"""Operator step of the Wave 1 exit (DEC-635): write this repository's rulesync permissions source from the deny
rules the harness settings hold now, and print counts only.

Run by the operator from the repository's root, never by an agent session:

    python3 docs/plan/wave-1-exit/write_permissions_source.py

What it does:
1. reads the deny rules of the settings of this repository and the held-out paths of the held-out file;
2. leaves out the Read deny rules the held-out generator writes (``python3 -m gov.guard.heldout``): they are added
   after generation and are never written into a rulesync source;
3. refuses, writing nothing, if any other rule names a held-out path, or has a form it cannot carry;
4. writes ``.rulesync/permissions.jsonc`` with every remaining rule;
5. generates into a temporary folder, applies the held-out step there, and compares the deny rules of the result
   with the ones the settings hold now.

It prints numbers and tool names. It never prints a rule, a path of a rule or a held-out path.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from gov.guard import heldout  # noqa: E402

GENERATE = ("generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots")
SOURCE = ROOT / ".rulesync" / "permissions.jsonc"


def by_tool(rules):
    tools = sorted({rule.split("(")[0] for rule in rules})
    return {tool: sum(1 for rule in rules if rule.split("(")[0] == tool) for tool in tools}


def main() -> int:
    if Path.cwd().resolve() != ROOT:
        print("run it from the repository's root:", ROOT)
        return 2
    settings_path = ROOT / heldout.SETTINGS_REL
    live = (json.loads(settings_path.read_text(encoding="utf-8")).get("permissions") or {}).get("deny") or []
    held = heldout.load_held_out(str(ROOT))
    if not held:
        print("the held-out file gives no path: nothing written")
        return 1
    generated_later = {f"Read(/{path}/**)" for path in held}  # the generator's own form
    kept = [rule for rule in live if rule not in generated_later]
    print("deny rules now:", len(live), by_tool(live))
    print("of them written after generation by the held-out step:", len(live) - len(kept), "of", len(generated_later))
    naming = sum(1 for rule in kept if any(path.strip("/") in rule for path in held))
    if naming:
        print(f"REFUSED: {naming} other rule(s) name a held-out path; nothing written. Tell the owner.")
        return 1
    blocks, odd = {}, 0
    for rule in kept:
        tool, opened, rest = rule.partition("(")
        if not opened or not rest.endswith(")") or not tool.isalpha():
            odd += 1
            continue
        blocks.setdefault(tool.lower(), {})[rest[:-1]] = "deny"
    if odd:
        print(f"REFUSED: {odd} rule(s) are not of the form Tool(pattern); nothing written. Tell the owner.")
        return 1
    before = SOURCE.read_text(encoding="utf-8") if SOURCE.is_file() else None
    SOURCE.write_text(json.dumps({"permission": blocks}, indent=2) + "\n", encoding="utf-8")
    print("written: .rulesync/permissions.jsonc with", len(kept), "rule(s)", {tool: len(v) for tool, v in blocks.items()})

    binary = shutil.which("rulesync")
    if not binary:
        print("rulesync is not on PATH: the source is written, the comparison was not made")
        return 1
    with tempfile.TemporaryDirectory() as fresh:
        done = subprocess.run([binary, *GENERATE, str(ROOT / ".rulesync")], cwd=fresh, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=120)
        made = Path(fresh) / heldout.SETTINGS_REL
        if done.returncode != 0 or not made.is_file():
            print("rulesync generate failed in the temporary folder, exit", done.returncode)
            return 1
        added = heldout.write_read_rules(str(ROOT), str(made))
        after = (json.loads(made.read_text(encoding="utf-8")).get("permissions") or {}).get("deny") or []
    lost, new = set(live) - set(after), set(after) - set(live)
    print("held-out step added in the temporary folder:", added)
    print("deny rules after generation and the step:", len(after), by_tool(after))
    print("rules now that would be lost:", len(lost), by_tool(lost))
    print("rules that would be new:", len(new), by_tool(new))
    if lost or new:
        if before is not None:
            SOURCE.write_text(before, encoding="utf-8")
        print("NOT EXACT: the source is put back as it was. Tell the orchestrator these numbers.")
        return 1
    print("EXACT: the same deny rules before and after. The source stays written; it is not committed by this script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
