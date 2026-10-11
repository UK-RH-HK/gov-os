"""Apply the generated adapter output to this repository (DEC-635, DEC-640). Run by the operator, from the
repository's root, in a quiet window: ``python3 docs/plan/wave-1-exit/apply_adapter_output.py``.

rulesync generating over an existing settings file keeps keys and rules it has no source for, so the result
would not be what the adapter-portability check compares with. This script therefore does what the check does:
it generates into an empty temporary folder, applies the held-out step there (``gov.guard.heldout``), and
copies each generated file over the repository's. It prints file names and counts only: no permission rule,
no hook command and no env value. ``--dry-run`` copies nothing."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from gov.adapters import portability  # noqa: E402
from gov.guard import heldout  # noqa: E402


def main() -> int:
    dry = "--dry-run" in sys.argv[1:]
    with tempfile.TemporaryDirectory() as fresh:
        done = subprocess.run([portability._find_rulesync(), *portability.GENERATE, str(ROOT / ".rulesync")],
                              cwd=fresh, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
        if done.returncode != 0:
            print("refused: rulesync exit", done.returncode)
            return 1
        try:
            written = heldout.write_read_rules(str(ROOT), str(Path(fresh) / heldout.SETTINGS_REL))
        except Exception as exc:  # the type only: its text may quote the held-out file
            print("refused: the held-out step failed:", type(exc).__name__)
            return 1
        print("held-out step: rules written", written)
        made = {str(path.relative_to(fresh)): path.read_bytes()
                for path in sorted(Path(fresh).rglob("*")) if path.is_file()}
    # Nothing lost: the deny rules about to be written must be the deny rules in force now (compared as sets,
    # never printed). The first application needs write_permissions_source.py to have been run before it.
    live_path = ROOT / heldout.SETTINGS_REL
    if live_path.is_file():
        live = set((json.loads(live_path.read_text(encoding="utf-8")).get("permissions") or {}).get("deny") or [])
        fresh_deny = set((json.loads(made[heldout.SETTINGS_REL].decode("utf-8")).get("permissions") or {})
                         .get("deny") or [])
        print(f"deny rules: in force {len(live)}, generated {len(fresh_deny)}, "
              f"lost {len(live - fresh_deny)}, added {len(fresh_deny - live)}")
        if live != fresh_deny:
            print("refused: the generated deny rules are not the ones in force; nothing copied")
            return 1
    new = changed = same = 0
    for rel, content in made.items():
        target = ROOT / rel
        if not target.is_file():
            new += 1
        elif target.read_bytes() != content:
            changed += 1
        else:
            same += 1
            continue
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    print(f"generated files: {len(made)} (new {new}, changed {changed}, already the same {same})")
    print("nothing copied (dry run)" if dry else "copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
