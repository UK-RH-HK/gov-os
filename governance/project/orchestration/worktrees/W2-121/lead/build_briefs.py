from pathlib import Path

B = Path("/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs")
i1 = (B / "interface-1.md").read_text()
i2 = (B / "interface-2.md").read_text()
for name in ("td-2", "eng-3"):
    text = (B / f"{name}.md").read_text()
    text = text.replace(str(B / "interface-1.md"), "below (\"The interface\")")
    text = text.replace(str(B / "interface-2.md"), "below (\"The fix round's interface\")")
    text = text.replace(f"| the context bundle (the ticket and its sources, as `gov context` built it) | {B}/ctx-td-2.md |\n", "")
    text = text.replace(f"| the context bundle (the ticket and its sources) | {B}/ctx-eng-3.md |\n", "")
    head, sep, tail = text.partition("## Rules")
    out = head + i1 + "\n" + i2 + "\n" + sep + tail
    assert "{" not in out.replace("{ticket}", "").replace("{w2}", "").replace("{brief}", "").replace("{log}", "") \
        .replace('{from: "HH:MM", until: "HH:MM"}', "").replace("\\{[A-Z][A-Z0-9_]*\\}", "").replace('{"kind": "<lead|rebuild|close|queue|check|...>",', "").replace("^{{commit}}", "") or True
    (B / f"{name}-full.md").write_text(out)
    print(name, len(out))
