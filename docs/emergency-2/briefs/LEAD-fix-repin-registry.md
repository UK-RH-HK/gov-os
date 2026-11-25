# Lead brief: the automatic re-pin rolls back because it never writes gov's tool-registry entry (I-31 corrected; a fix under W2-209)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-25. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies** (read your bundle whole, never cut a `gov retrieve` result, list your retrieves, one trailer paragraph with no blank line before `Co-Authored-By`). Decide, never ask (I-10). Use `systematic-debugging`. Small and fast: the machine-wide re-pin waits on it.

## The fault
Read row "I-31 (corrected)" of `docs/emergency-2/integration/FINDINGS.md`. `gov release <v> --patch` (W2-209, `.tickets/DAEO-a2h5.md`; code `src/gov/release/repin.py`, `cut.py`) cut 0.1.6 and 0.1.7, then switched `~/.local/bin/gov` to the new pin and ran `gov doctor`, which found `tools` newly unhealthy, and rolled back: `governance/project/tool-registry.yaml:236` pins the tool `gov` at 0.1.5 with the 0.1.5 wheel's sha256, and the re-pin never writes the new pin's entry before its check. The owner's manual re-pin of 0.1.5 wrote and committed that entry itself (commit `8346b9a30`, read it).

## What (a K-line RP-1 in the `## Fix:` section of `.tickets/DAEO-a2h5.md`; the CTO approves it by this brief)
- **RP-1** The automatic re-pin writes the new pin's `gov` entry in the tool registry (version, sha256 of the release wheel, the install and uninstall lines in the form of the 0.1.5 entry, the date, the approving decision) before its post-pin checks, so `gov doctor`'s `tools` part reads the new gov as pinned; it commits that entry with the re-pin's record (as the owner's re-pin did), and a rollback restores the previous entry and commits nothing (or reverts it). Prove it on a planted machine (a temporary HOME, a planted registry and two planted pins): the switch passes the doctor check with the entry written, and a planted genuine tool mismatch still rolls back. Failing test first (the test designer), then the engineer.
- Say whether anything else the post-pin checks read is pinned to the old release in the same way (hooks, the facts file, the role table), and fix any you find under RP-1.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-repin-registry`, branch `e2/fix-repin-registry` from `w2/integrate`. Code area: `src/gov/release/` (re-pin and cut), the registry writer if one exists. Never touch the real `~/.local/bin/gov`, `~/.local/share/gov-os/` or the real registry entry: tests use planted homes.

## Green
RP-1 red on the base, green after; `tests/unit/release`, W2-209 and W2-16 green; then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-a2h5=e2/fix-repin-registry --onto w2/integrate --select`), through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; the cause confirmed (file:line); RP-1 with tests and result; anything else pinned to the old release; the selected suites' summary; your retrieves.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
Query: How does the automatic re-pin (gov release --patch, repin.py) switch the gov link, run its post-pin checks and roll back, and how is the gov entry of the tool registry written in a re-pin? Code locations, conventions, earlier fixes and findings.

```
store: 579d32de7c85 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "579d32de7c85fe3396d80e54f7b0db188b405d2a",
    "head": "579d32de7c85fe3396d80e54f7b0db188b405d2a",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-a2h5",
      "sha256": "7fccd87cb7dd6769c27a989dcd2c1c37b579427bed8d06672a36cd8c31c59391",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 42,
      "end_line": 42,
      "text": "  - 'S8 The general re-pin: `gov.release.repin.repin(repo, version, home, ...)` makes the machine''s `gov` the release''s, reading the version from the tag and writing none in, in the order of `docs/emergency-2/release-0.1.4/repin.sh`: the tag is annotated and its parent is C; only the record''s files differ between C and the tag; the manifest matches its hash and names the version and commit; the wheel built twice from C equals the record''s sha256; the environment `pin-<C>` is made beside the live one under `<home>/.local/share/gov-os` and its `gov --version` says the release. Each of these stops before the switch, changing nothing (the link `<home>/.local/bin/gov` and the pin folders are as before). The switch is one rename of the link; then the post-pin check through the new link: `gov --help`; `gov launch --help`; a search of the memory store with both facets; the five hook programs of the repository''s settings, each run with an empty event, each exiting 0 (the subagentstop hook''s contract answer for an empty event counts as its pass, as the 0.1.4 script has it); and `gov doctor` shows no part unhealthy that was healthy in a reading taken before the switch. On a pass: the registry entry of `governance/project/tool-registry.yaml` is committed (`Role: orchestrator`, `Decided-by: owner (standing, <decision>)`), `<home>/.local/share/gov-os/repin.json` says `ok`, and `rollback.sh` is written. Verify: a scratch home with a pin folder and a link, a scratch clone of the repository with a planted release; each early stop planted once (an unannotated tag, a record with an extra changed file, a manifest hash mismatch, a wheel hash mismatch, a `gov --version` that names another release) leaves the link and folders as before; a green re-pin switches the link to `pin-<C>`, commits the registry entry with the trailers, writes `repin.json` with `ok` and the script. [RELEASE-ON-BEHALF K4, K6; DEC-1224 (3)]'\n",
      "chunk_id": "2761a9739aa3276074a6484b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "5f0eb7b037c9459f4caad8c9",
      "sha256": "330a68b8b3225fa3b0c6a0df2c04530331da8219a9fcd2a5b7833bab43a5060f",
      "path": "src/gov/release/repin.py",
      "start_line": 1,
      "end_line": 12,
      "text": "\"\"\"The general re-pin of the machine's ``gov`` (W2-209, RELEASE-ON-BEHALF \"Re-pin and its rollback\"; DEC-1223).\n\n``repin(repo, version, home)`` is ``docs/emergency-2/release-0.1.4/repin.sh`` made general: the version is read from\nthe tag ``v<version>``, none is written in. Each of these stops before the switch, changing neither the link\n``<home>/.local/bin/gov`` nor the pin folders (a folder made for the new pin is removed): the version is not burned;\nthe tag is annotated and its commit's only parent is C; only the record's files differ between C and the tag; the\nmanifest matches its hash and names the version and C; the wheel built twice from C equals the record's sha256; the\nenvironment ``pin-<C12>`` is made beside the live one and its ``gov --version`` says the release.\n\nThe switch is one rename of the link. Then the post-pin checks run through the new link: ``gov --help``,\n``gov launch --help``, a search of the memory store with both facets, the five hook programs of the repository's\nsettings with an empty event, and ``gov doctor`` (no part unhealthy that was healthy before the switch). A pass commits\n",
      "chunk_id": "5f0eb7b037c9459f4caad8c9",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4ca4eeef42b7eec076939d91",
      "sha256": "7b1f1708992b9bede187657ae27743ad00550d7e0e9d71c908028f8213db6376",
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "start_line": 116,
      "end_line": 126,
      "text": "## Re-pin and its rollback\n\nThe re-pin is `docs/emergency-2/release-0.1.3/repin.sh` made general: the version is read from the tag, not written in. Steps, each stopping before the switch on failure (nothing changed for sessions): the tag is annotated and its parent is C; only the record's files differ between C and the tag; the manifest matches its hash and names the version and commit; the wheel built twice from C equals the record's sha256; the new environment `pin-<C>` is made beside the live one and its `gov --version` says the release.\n\nThen the switch (one rename of `~/.local/bin/gov`) and the **post-pin check**, through the new link: `gov --help`; `gov launch --help`; a search of the memory store with both its facets; **the five hook programs of this repository's settings, run with an empty event, each exiting 0** (every session runs them; today's script does not); `gov doctor` here shows no part unhealthy that was healthy in a reading taken just before the switch.\n\n- **Pass:** the registry entry is committed (`Role: orchestrator`, `Decided-by: owner (standing)`), `repin.json` says `ok`, `rollback.sh` is written, the push goes out.\n- **Fail:** the link goes back to the old pin by one rename, `repin.json` says `rolled_back` and why, the release is **burned** (its tag and record stay; an immutable release is never deleted), the owner is pushed, the CTO fixes and cuts the next patch. Adopted repositories never update to a burned release.\n\n**The rollback line the owner pastes** is `bash ~/.local/share/gov-os/rollback.sh`. It is plain shell, not `gov`, because the new `gov` is the thing in doubt. It holds exactly the line of 0.1.3's re-pin (`ln -sfn <old pin>/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r`) and adds the release to `~/.local/share/gov-os/burned`, which the update pass reads. It restores what every session sees. It leaves the new pin folder, the tag and the registry commit (the CTO reverts that commit in its next work).\n\n",
      "chunk_id": "4ca4eeef42b7eec076939d91",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-a2h5",
      "sha256": "4ed3cb6843fff8cef2c141db2753168ed0b480581485f507f39b1927f319fb48",
      "path": ".tickets/DAEO-a2h5.md",
      "start_line": 43,
      "end_line": 43,
      "text": "  - 'S9 A failed check after the switch puts the previous gov back, burns the release and tells the owner once (K4): on any failing post-pin check (a planted hook that exits non-zero or crashes, a missing facet, a doctor part newly unhealthy) the link names the old pin again by one rename within 60 seconds, `repin.json` says `rolled_back` with the failing check, the release is added to `<home>/.local/share/gov-os/burned` (one version per line; its tag and record stay), one push is made (S10), no registry commit is made, and `gov.release.repin.burned(home)` lists the release; the update machinery of W2-17 never offers a burned release (`gov.update.pending` shows no pending update to a burned release, and `held` states why). Verify: the re-pin with each of the three failures planted in the new pin''s environment: the link, `repin.json`, `burned` and the one recorded push are as stated, and a second re-pin of the same release is refused as burned; `pending.pending` on a repository one release behind a burned patch release answers `pending: false` with the burned reason. [RELEASE-ON-BEHALF K4; DEC-1223]'\n",
      "chunk_id": "95175906d0b5ca075d76d50f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ADR-0002",
      "sha256": "a384679d07807c21edf67dea09e5609ac7733f2d090e14667442fa136d6e9cf5",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "start_line": 156,
      "end_line": 167,
      "text": "  the repository (`~/.local/bin`, `~/.config`, `~/.ollama`, the crontab, services) as a rehearsed ACT, is retired:\n  control files change by ordinary commits (EMERGENCY-2 \u00a72.10; DEC-1038 (1), DEC-1057, DEC-1058 as they stood).\n  `gov doctor` compares these pins with what it finds.\n- **The `gov` CLI:**\n  - It is a Python 3.12 package in the Gov OS repository (`src/gov/`). Every session runs the pinned wheel. Releases and\n    re-pins are the owner's (EMERGENCY-2 \u00a72.5, \u00a78.3). A re-pin runs its checks before the switch, installs the new pin\n    beside the old one and switches by one rename, the old pin kept for an instant rollback (DEC-1037 (1)); each\n    release's wheel is built twice from a clean export and the two builds match. A release is pinned and hash-verified,\n    with no signature until friction asks for it (DEC-1214 L3; CAP-02, CAP-43.b). The kernel records the `gov` version\n    pin. Its pinned install (W2-18) and `gov update` (W2-17) are built for the release (EMERGENCY-2 \u00a76.1, \u00a76.2 A-4,\n    \u00a77.6; CAP-45), which changes DEC-1089 (2)'s placement in Wave 3.\n  - Its core needs only the standard library, PyYAML and sqlite-vec.\n",
      "chunk_id": "a54d40947ef7d57e1f5d3b05",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "905f887c5a237587cc5b3b4f",
      "sha256": "48417f25ee0df728009cf1cc320ce58f727734bb524568879590384932c9313d",
      "path": "docs/research/W2-130-link-cleanup.md",
      "start_line": 2290,
      "end_line": 2292,
      "text": "+- **Status:** ACCEPTED (owner, 2026-11-02 ~15:50; recorded by the orchestrator, DEC-861) \u00b7 **Under:** DEC-1033, DEC-1032, DEC-105, DEC-1003 \u00b7 **Changes:** DEC-954 Q8 (b) (\"ACT 2, one re-pin\"; P-W2-110-4 item 6): apply now \u00b7 **Changed by:** DEC-1039 (3)\n - **Decision:** (1) P1-REPIN-EMERGENCY (`governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md`) option (a): an emergency re-pin of the gov every session runs (`~/.local/bin/gov`, today `pin-5c401220` of 28 October) from `w2/integrate`, in two windows: window 1 after W2-122 and W2-123 land, then ACT-QUERY-GPU-2 in the same window once no process of the old pin runs; window 2 after W2-112 lands (with W2-126 if landed). Every check before the switch as the P1 lists, the guard's included (W2-84's reads); the old pin kept for an instant rollback (one rename); any failed check, or a broken search after the switch, means switching straight back to the old pin and telling the owner.\n (2) The full suite runs on the re-pinned head as soon as window 1 is done, not at night, while the freeze keeps the machine free; the CTO gives its expected time.\n",
      "chunk_id": "905f887c5a237587cc5b3b4f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-sdhj",
      "sha256": "ac342fc956f11a3e4dc52b50584ac86d28df9e204f5cb9b9db50c4e01b0410dd",
      "path": ".tickets/DAEO-sdhj.md",
      "start_line": 137,
      "end_line": 146,
      "text": "    `no_previous_pin` before anything changes where it does not. It reverts the update commit with `git revert` (a\n    new commit; one commit holds the revert and the record below; history keeps the update commit and the revert);\n    where later commits make the revert conflict it stops, runs nothing else, leaves HEAD, the tree and the pin as\n    before and refuses with reason `rollback_conflict` naming the conflicting paths; it puts the pin's link and\n    `pin.json` back to A (or removes them where the project held no pin before); runs `gov rebuild` with the restored\n    pin's gov (the running gov where there is no pin), a failed rebuild leaving the rollback committed and exit\n    non-zero as `UPDATE_STORE_FAILED` saying `gov rebuild` is to run; and writes\n    `governance/updates/<B>.rolled-back.json` (`from` B, `to` A, `update_commit`, `pin`: the pin restored, in the shape\n    of `pin_before`) in that commit (a commit cannot name itself, so no key names the revert commit).\n    It leaves B's environment folder `<common>/gov/envs/<B>`. **Which gov runs it (W2-18's dispatch):** in a repository\n",
      "chunk_id": "57d19219d2986abddf9ac9f5",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "da3791cea0e888f504549b3e",
      "sha256": "7aa3be6d35ea88e5431c5f240529160feaed4d9a31c148355d2139b28e3d414f",
      "path": "docs/emergency-2/release-0.1.2/STEPS.md",
      "start_line": 41,
      "end_line": 49,
      "text": "## 4. Re-pin\n```\nbash docs/emergency-2/release-0.1.2/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.2.log\n```\nIt checks the tag and the record, builds the wheel twice and compares it with the record's sha256, installs\n`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks `gov --help`, `gov launch --help` and a\nsearch through the new link, rolls back by itself on a failed check, and commits the registry entry as yours. It ends\nwith `RE-PIN DONE` and prints the one-line rollback.\n\n",
      "chunk_id": "da3791cea0e888f504549b3e",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "a6326571d3fbe6270eb2db26",
      "sha256": "92d338b212ac73690b59cefbae5035e922545a5ec9ea64de27d2a56906249f73",
      "path": "docs/emergency-2/release-0.1.5/STEPS.md",
      "start_line": 52,
      "end_line": 61,
      "text": "## 4. Re-pin\n```\nbash docs/emergency-2/release-0.1.5/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.5.log\n```\nAs for 0.1.3: it checks the tag and the record, builds the wheel twice against the record's sha256, installs\n`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it (now also the five hooks through the\nnew pin), rolls back by itself on a failed check, commits the registry entry as yours, then rebuilds the two stores\nthrough the new link (a failed rebuild keeps the pin and says so). It ends with `RE-PIN DONE` and prints the one-line\nrollback.\n\n",
      "chunk_id": "a6326571d3fbe6270eb2db26",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "72d5ac0aae72a928ca61d15f",
      "sha256": "682a4d9231e48d774998c14cc50cdf164438da2a56c1004e81959247c7be267e",
      "path": "docs/emergency-2/release-0.1.4/STEPS.md",
      "start_line": 50,
      "end_line": 59,
      "text": "## 4. Re-pin\n```\nbash docs/emergency-2/release-0.1.4/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.4.log\n```\nAs for 0.1.3: it checks the tag and the record, builds the wheel twice against the record's sha256, installs\n`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it (now also the five hooks through the\nnew pin), rolls back by itself on a failed check, commits the registry entry as yours, then rebuilds the two stores\nthrough the new link (a failed rebuild keeps the pin and says so). It ends with `RE-PIN DONE` and prints the one-line\nrollback.\n\n",
      "chunk_id": "72d5ac0aae72a928ca61d15f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2a7600cee2ffe165cd0ad6ca",
      "sha256": "7db76494ec414fccaa5fba798b2657b3ea9816a94334860bb49a49d310a02d72",
      "path": "docs/emergency-2/release-0.1.3/STEPS.md",
      "start_line": 45,
      "end_line": 52,
      "text": "## 4. Re-pin\n```\nbash docs/emergency-2/release-0.1.3/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.3.log\n```\nAs for 0.1.2: it checks the tag and the record, builds the wheel twice against the record's sha256, installs\n`pin-<C>` beside the live pin, switches `~/.local/bin/gov` atomically, checks it, rolls back by itself on a failed\ncheck, and commits the registry entry as yours. It ends with `RE-PIN DONE` and prints the one-line rollback.\n\n",
      "chunk_id": "2a7600cee2ffe165cd0ad6ca",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "e3b701d07f869be2ab7c16b2",
      "sha256": "67edbff4f73005a3b7b949448d97c09fda9182f09dfffb74008afba2b17e188b",
      "path": "docs/emergency-2/release-0.1.2/repin.sh",
      "start_line": 78,
      "end_line": 91,
      "text": "[ \"$(readlink -f \"$BIN/gov\")\" = \"$(readlink -f \"$N/bin/gov\")\" ] || rollback \"the link does not name pin-$C\"\n\"$BIN/gov\" --help > /dev/null 2>&1 || rollback \"gov --help through the new pin failed\"\n(cd \"$STORE\" && \"$BIN/gov\" retrieve \"what decides a close\" --json > \"$X/search.json\") || rollback \"a search through the new pin failed\"\npython3 -c \"import json,sys; r=json.load(open(sys.argv[1]))['result']; f=r['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) else 1)\" \"$X/search.json\" \\\n  || rollback \"a search through the new pin lost a facet\"\n\"$BIN/gov\" launch --help > /dev/null 2>&1 || rollback \"gov launch --help through the new pin failed\"\necho \"ok: $BIN/gov -> $(readlink -f \"$BIN/gov\"); gov --help, gov launch --help and a search (both facets) work\"\n\necho \"== E. the registry entry, committed as the owner's\"\npython3 - \"$REPO/governance/project/tool-registry.yaml\" \"$C\" \"$SHA\" \"$VERSION\" \"$CLI\" \"$OLDPIN\" \"$(sha256sum < \"$N/bin/gov\" | cut -d' ' -f1)\" <<'PY'\nimport datetime, re, sys\npath, c, sha, version, cli, oldpin, script = sys.argv[1:8]\ntext = open(path, encoding=\"utf-8\").read()\nstart = text.index(\"  - name: gov\\n\")\n",
      "chunk_id": "e3b701d07f869be2ab7c16b2",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "71f8fd3bf131d8e1712e0033",
      "sha256": "5e5184b036b54f4f3fe894e27f55ce8c5488d69b00c7dd5a1d35a30d9a320aa4",
      "path": "docs/emergency-2/release-0.1.4/repin.sh",
      "start_line": 1,
      "end_line": 13,
      "text": "#!/usr/bin/env bash\n# Re-pin gov from release 0.1.4 (EMERGENCY-2.md 8.2, 8.3: the memory measure for EXAMIN's fresh 80, W2-204): the owner's act,\n# in a plain terminal, after the owner made release 0.1.4 (gov release 0.1.4 at the version commit C, the record\n# committed, the annotated tag v0.1.4 on the record commit). As 0.1.3's script, with two additions:\n# (F) the five hook programs of this repository's settings are run with an empty event through the new pin's interpreter\n#     (every session runs them), and a crash rolls back;\n# (G) the stores are rebuilt through the new link after the registry commit (0.1.4 changes the store loader: W2-203 keeps\n#     the archived register out of memory's index); a failed rebuild does not roll back the pin (the pin is good), it\n#     says so for the CTO. The reranker is not restarted (its bytes are unchanged since 0.1.3; checked below).\n#     bash docs/emergency-2/release-0.1.4/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.4.log\n# Stops at the first failure before the switch (nothing changed for sessions); after the switch a failed check switches\n# straight back to the old pin and prints ROLLED BACK.\nset -euo pipefail\n",
      "chunk_id": "71f8fd3bf131d8e1712e0033",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "20e54113dba13d763af7a4c8",
      "sha256": "361df812966940db6bdc5dc99fe6fa3a52ff5edc1d3c4be3a359b0fe25c6f588",
      "path": "governance/project/orchestration/packages/P-RELEASE-2.md",
      "start_line": 114,
      "end_line": 122,
      "text": "## 5. The re-pin (your operator, plain terminal, about 5 minutes)\nAt \"released\" I run `fill_release.sh --c <C> --repo /home/usain/Dynamic-Agentic-Engineering-OS --dec DEC-1198` (it\nrefuses unless the tag, the record and the record commit's message all agree), rehearse the filled script at the real C\non a mirror, have the filled bytes reviewed, then give your operator one line: the bundle's sha256 check first, then the\nscript with both targets named (`--home /home/usain --repo /home/usain/Dynamic-Agentic-Engineering-OS`; DEC-1196 (5)).\nIt installs `pin-<C>` beside pin-076cded14882, rebuilds the store, runs the checks, switches `~/.local/bin/gov`\natomically and rolls back by itself on a failed check. Rollback line (yours, if anything goes wrong after the switch):\n`ln -sfn ~/.local/share/gov-os/pin-076cded14882/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r`\n\n",
      "chunk_id": "20e54113dba13d763af7a4c8",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "814791c7311504170d11118d",
      "sha256": "67edbff4f73005a3b7b949448d97c09fda9182f09dfffb74008afba2b17e188b",
      "path": "docs/emergency-2/release-0.1.3/repin.sh",
      "start_line": 78,
      "end_line": 91,
      "text": "[ \"$(readlink -f \"$BIN/gov\")\" = \"$(readlink -f \"$N/bin/gov\")\" ] || rollback \"the link does not name pin-$C\"\n\"$BIN/gov\" --help > /dev/null 2>&1 || rollback \"gov --help through the new pin failed\"\n(cd \"$STORE\" && \"$BIN/gov\" retrieve \"what decides a close\" --json > \"$X/search.json\") || rollback \"a search through the new pin failed\"\npython3 -c \"import json,sys; r=json.load(open(sys.argv[1]))['result']; f=r['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) else 1)\" \"$X/search.json\" \\\n  || rollback \"a search through the new pin lost a facet\"\n\"$BIN/gov\" launch --help > /dev/null 2>&1 || rollback \"gov launch --help through the new pin failed\"\necho \"ok: $BIN/gov -> $(readlink -f \"$BIN/gov\"); gov --help, gov launch --help and a search (both facets) work\"\n\necho \"== E. the registry entry, committed as the owner's\"\npython3 - \"$REPO/governance/project/tool-registry.yaml\" \"$C\" \"$SHA\" \"$VERSION\" \"$CLI\" \"$OLDPIN\" \"$(sha256sum < \"$N/bin/gov\" | cut -d' ' -f1)\" <<'PY'\nimport datetime, re, sys\npath, c, sha, version, cli, oldpin, script = sys.argv[1:8]\ntext = open(path, encoding=\"utf-8\").read()\nstart = text.index(\"  - name: gov\\n\")\n",
      "chunk_id": "814791c7311504170d11118d",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f68d2084e13345eff079c4ba",
      "sha256": "429c9ad7417996af4671659e17e441ef0f848865f2f918ff2c44cdd8bf2ee942",
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "start_line": 11,
      "end_line": 31,
      "text": "## 2. What happened\n\nThe full regression had 16,199 passed, 32 skipped and 9 failed. One red is already fixed; eight remain. None is W2-70's work.\n\n| Reds | Cause | Fix |\n|---|---|---|\n| W1-01 `test_docs_source_deny_rules_survive_the_change` \u00d74; W1-47 `test_the_other_deny_rules_are_in_place[Read(./docs/source/**)]`, `[Edit(./docs/source/**)]` | They enforce the two `docs/source` deny rules that the regeneration removed (P-I1-2, DEC-899, done in DEC-922 Part B). The DEC-866 sweep before the ACT missed them; that miss is the orchestrator's. | A test designer retires the six `docs/source` cases: the folder left the tree on 2026-10-01. Retiring a test is the owner's decision. |\n| W1-49 `test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH]` | The test's sandbox has neither tk nor gov. The new lifecycle hook line (DEC-917, W2-65) ends with 1 when it finds no pinned gov, and the test expects 0. | The test designer gives the sandbox a gov (a link to the pinned one), so only tk is missing (`Rewrite-Reason: DEC-917`). |\n| W1-06 `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` | The re-pin's registry entry for `gov` cites `approved_by: DEC-921`, whose text does not name gov. The orchestrator's `repin_registry.py` wrote it before DEC-922 existed. | One line: `approved_by: \"DEC-922\"` (DEC-922 records the re-pin of gov). |\n| W2-69 `test_the_unit_folder_named_secrets_is_gone` | A leftover `tests/unit/secrets/` that held only git-ignored `__pycache__` files. | **Done:** removed on 2026-10-27. |\n\n**Also found, and fixed in the orchestrator's own tools:**\n- **The skip guard** compared test ids in two forms (the known list is dotted, the pinned close's evidence uses paths), so it would have stopped after every passing close. It now reads both forms.\n- **Two skips added to the known list** (DEC-915 item 2), both effects of the pinned interpreter:\n  - W1-03 `[the-gov-package-is-missing]`;\n  - the govbridge parity case, whose message is now longer.\n  The guard now passes on this close's 32 skips.\n- **The queue's collection log** now keeps only errors and the summary.\n\n**Still open, for the owner:** one of W2-69's acceptance cases has row W2-L423's keyword in its own name. So every full run's JUnit XML holds it, with no hash beside it. The close writes that XML under `.gov-runtime/close/`, and the warning (DEC-923) would stop the next queue on it.\n\n",
      "chunk_id": "f68d2084e13345eff079c4ba",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "be14cb1c9792bcb51d8e7f14",
      "sha256": "f43443a179063e974593f60ea8647dae82b51f5ac7a45cd3bba00fe8f495a3cd",
      "path": "governance/project/orchestration/packages/P-REPIN-2.md",
      "start_line": 11,
      "end_line": 27,
      "text": "## 2. The proposal\n\n- **Re-pin 2:** the merge of W2-07 round 2 on `w2/integrate`, carrying W2-57 and W2-07 round 2.\n- **Re-pin 3:** W2-68 and W2-71, when they land.\n- **Cadence from now (owner, standing, if accepted):** a re-pin as each judge improvement lands, at a quiet moment, never during a close queue or a close's quiet window.\n- **The ladder before the ACT, as for ACT-REPIN-1:**\n  - W2-07 round 2 merged, with `tools/probe_impact.py` after it;\n  - the full regression in the close's form on a fresh clone of the head to be pinned, with that head's own code (the code the pin will be);\n  - two wheel builds from clean exports of that head with the same sha256;\n  - clean history: the trailer gate and containment find nothing, and W1-01's history cases pass;\n  - a sweep for every test or tool that names `pin-6a4696eb` (the hooks and the declared checks follow `~/.local/bin/gov`; my tools name the pin's path, so they move with it, as after ACT-REPIN-1).\n- **The ACT:** Part A of ACT-REPIN-1 only (export, build, check the sha256, install in `pin-<sha>`, link `~/.local/bin/gov`, verify, commit the registry entry `Role: owner`), in `packages/ACT-REPIN-2.md` and a commands file, in a plain terminal (DEC-928 item 3: it reinstalls gov). `pin-6a4696eb` stays for the rollback.\n- **After it, in order:**\n  1. my smoke test (the pinned `gov check`, one guard decision allowed and one refused, the declared checks and hooks on the new pin);\n  2. ACT-W2-57-LS-2 (W1-46's 23 and W1-19's warm p95 leave `load_sensitive`), validated by a full run in the close's form with the new pin (DEC-931 item 2);\n  3. a close queue: W2-58, W2-63, W2-07, W2-57 (and W2-67 after its merge-back and re-probe).\n\n",
      "chunk_id": "be14cb1c9792bcb51d8e7f14",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "6350e9c4e46d76f009898705",
      "sha256": "d025af365fb63b9c28032d074d3df5fe881b286e8441b48ac4159abc03c2d03a",
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "start_line": 1,
      "end_line": 11,
      "text": "#!/usr/bin/env bash\n# Re-pin gov from release 0.1.5 (DEC-1226: the owner's last manual cut; DEC-1225's model rubric in code, W2-209's patch\n# release, the strict memory grading for EXAMIN's fresh 80): the owner's act,\n# in a plain terminal, after the owner made release 0.1.5 (gov release 0.1.5 at the version commit C, the record\n# committed, the annotated tag v0.1.5 on the record commit). As 0.1.4's script (same steps; 0.1.5 changes no store loader, the rebuild in G only refreshes):\n# (F) the five hook programs of this repository's settings are run with an empty event through the new pin's interpreter\n#     (every session runs them), and a crash rolls back;\n# (G) the stores are rebuilt through the new link after the registry commit (a refresh: 0.1.5 changes no loader; W2-203 keeps\n#     the archived register out of memory's index); a failed rebuild does not roll back the pin (the pin is good), it\n#     says so for the CTO. The reranker is not restarted (its bytes are unchanged since 0.1.3; checked below).\n#     bash docs/emergency-2/release-0.1.5/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.5.log\n",
      "chunk_id": "6350e9c4e46d76f009898705",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "2223d0ac225d36f9ee8613e4",
      "sha256": "dbeb97be81c7c6e097e46e3f40ce8c9b26b8d74f160022ba361dd5d5781e3e00",
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "start_line": 184,
      "end_line": 220,
      "text": "      \"what\": \"rollback.sh run in a plain shell with no gov on its path puts the previous link back and burns the release\",\n      \"link\": \"/tmp/tmp.jz3CjUAQRN/w2-209-rehearsal-6756b0fq/home/.local/share/gov-os/pin-30438fd9397e/bin/gov\",\n      \"burned\": [\n        \"0.9.1\"\n      ]\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"a planted failing hook rolls the re-pin back\",\n      \"check\": \"hooks\",\n      \"stderr\": \"\"\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"the scratch link names the old pin again\",\n      \"link\": \"/tmp/tmp.jz3CjUAQRN/w2-209-rehearsal-6756b0fq/d/home/.local/share/gov-os/pin-30438fd9397e/bin/gov\",\n      \"seconds\": 29.9\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"the release is burned (its tag and record stay)\",\n      \"tag\": \"v0.9.1\"\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"one failure push, at most 190 characters\",\n      \"pushes\": [\n        \"Gov OS 0.9.1 NOT pinned: post-pin check failed (hooks). Rolled back, old gov live, nothing for you to do. Release burned; CTO cuts the next patch.\"\n      ]\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n",
      "chunk_id": "2223d0ac225d36f9ee8613e4",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d86bc4f67c99c232430ceafe",
      "sha256": "9d6d083c475043c864debf223992b190b0f4674084a1b92a5d7311caf11a1624",
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "start_line": 215,
      "end_line": 247,
      "text": "        \"Gov OS 0.9.1 NOT pinned: post-pin check failed (hooks). Rolled back, old gov live, nothing for you to do. Release burned; CTO cuts the next patch.\"\n      ]\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"no registry commit was made\"\n    },\n    {\n      \"case\": \"D\",\n      \"ok\": true,\n      \"what\": \"a second re-pin of the burned release is refused (stopped at `burned`), the link unchanged\",\n      \"answer\": {\n        \"status\": \"stopped\",\n        \"version\": \"0.9.1\",\n        \"commit\": null,\n        \"step\": \"burned\",\n        \"check\": null,\n        \"pin\": null,\n        \"old_pin\": null,\n        \"push_text\": null,\n        \"reason\": \"release 0.9.1 is burned: it is never pinned\"\n      },\n      \"link\": \"/tmp/tmp.jz3CjUAQRN/w2-209-rehearsal-6756b0fq/d/home/.local/share/gov-os/pin-30438fd9397e/bin/gov\"\n    },\n    {\n      \"case\": \"Z\",\n      \"ok\": true,\n      \"what\": \"the real ~/.local/bin/gov link is as before\",\n      \"link\": \"/home/usain/.local/share/gov-os/pin-961db6546490/bin/gov\"\n    }\n  ]\n}\n",
      "chunk_id": "d86bc4f67c99c232430ceafe",
      "routes": [
        "semantic"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 0,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "4ca4eeef42b7eec076939d91",
      "parent_id": "928c901376a0e757a3943fd7",
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "start_line": 116,
      "end_line": 126
    },
    {
      "chunk_id": "f68d2084e13345eff079c4ba",
      "parent_id": "5d62dba2820ccbde0512bca6",
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "start_line": 11,
      "end_line": 31
    },
    {
      "chunk_id": "be14cb1c9792bcb51d8e7f14",
      "parent_id": "1aab5b1f43bd171e11257446",
      "path": "governance/project/orchestration/packages/P-REPIN-2.md",
      "start_line": 11,
      "end_line": 27
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "5fbd2cd6062591b55ef8d6b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "8a6e46f4154e615748350033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cc22f8ec310fe1d07afc7ff9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1bf642f128c3a3738d7c2db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "70eb80cab27469a298a9e078",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e3f050f7c7f6d3f33560cf2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "213f0c02b7aaa40127bbd43f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63ba33081f31cfb82cce61bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4e433d38c9370738dec705d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1f4fb10e2c09ba11e7666302",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9f78a531a985c7c40ff3b892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cf99cd773ecf6cf6e1ed0830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "c941ec1c25ffb656afea885c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1879d875a44a02135a1da4b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abc74248c32273f1c022bc7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ccd2f7a9ecfe2fee02880502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.2/repin.sh",
      "chunk_id": "ab9755fde1d644d4794204a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4364c134b7f98007ccbc3386",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "afc358a3cca9d588847e6fb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "46fceeb40f98e5bccf1f6794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.3/repin.sh",
      "chunk_id": "01e3299b7da54f2a4b708625",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "22703223eb3e7b9382b7c76c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "ae02a78287148d71db59f621",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "b19275fc1197d0c0783bd0c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/rehearse.py",
      "chunk_id": "c3c9681d1dd3bd4b968809e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fd2bb734568e19eda709960a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "5c40344b9d63487c3d0d6ed8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4d2d97f055b7b79b0349af8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "d04c4e12ef53132f1064cbd1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fa33b9709e40bdc766fabd24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.4/repin.sh",
      "chunk_id": "087404d47674bb1f7c5c864c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "1d4ca6b570cd8d2e84171d97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "24d40c55c7f7fabdeb7f5b5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "99c850e7e5ed7eed01e32d7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "1361dad6061574f80bdbdecc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "5a2123c2fd7e3a5ec23f6dbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.2/repin.sh",
      "chunk_id": "f2140e6c91b8cc147ec1d0cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "9d94c9310596909f3fe4fa9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "721768d726a495736a21a5e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "11a46fe1caf95f21845aafd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.3/repin.sh",
      "chunk_id": "70d93f5e05be683ebea60be7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "246301269d8e38952c4e0dc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "56fe93b1958a140b1c0f6a7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.2/repin.sh",
      "chunk_id": "9c1511ec9b97d7dd8c508485",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c98ea5b49644c81cc3c3f9ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.3/repin.sh",
      "chunk_id": "b17b7007fb1970d1c21b4f61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "e2429f455da4a808eb0e40d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "73a0a9c35f9197fa162c1ea9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "636605eb68617e5eea5e0603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.4/repin.sh",
      "chunk_id": "0952f70a545b7c9c058d1428",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "25a5df5b951c747b4c3684f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "9ca7cd30273574c0e779b0c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "b16700fd124eab81de1a188e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "edcfd6d3bc0a08ce64de7e49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c96a2d2e3357243e414ae26b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.4/repin.sh",
      "chunk_id": "ec59b0d6fd75bedeaa3832f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "45485f969662ed32b4363667",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "44e64fbc611f71d19ce5470d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d31243234d1ce38230e850f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "chunk_id": "6c46c62f3d81766df51bf025",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "143ff4a3e591a6b046c96122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/results.json",
      "chunk_id": "e6bd0101688095a328501de2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "18ab62a513892f4edc12ca1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "994d6cc31b010d4737957753",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "8d4789f10211a38a5255e45e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "d755fcfc0ce91fdd8ef5c53c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "46ad0b64a2a490dd61b442e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "c9124cb528be516c48349853",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "342b564afdf6ebff8cd22b79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "540f739f657eecec2ed10749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "3459e54c5e11f661c4c92e4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "ca3b2239598cb585a8a7c78d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "4726a9fe271c5d81c6122538",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "49d4071bb90494913cf695e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fbb87d3428c4a8f1a58ac847",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.4/repin.sh",
      "chunk_id": "7b597fbf3c0fa53a1ad2e6c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c3ed2f075e63c31d29b55d72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "c8a6ff9ad4c54d315242cbfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "19ad1f4d4f51784760c0b872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/rehearse.py",
      "chunk_id": "75d7462a84e760272a57d818",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "b9ccc4dd20459739f9bdfff7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-209-rehearsal/push-text.0.9.1.failed.scratch.txt",
      "chunk_id": "e4eb5cabab292564311cb3ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d9fff3e35fdaa4673e82d71b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "2e26a17899db2d617a2fc95e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "91c433d34ab0f87811570d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-59-CIT-P.md",
      "chunk_id": "31ab7a3b1b9545c900248717",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "f7fb064a036be063fd816ac4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "5837412cd26aa8ee9c189e9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "e48bf87b739ca3ebce4b1487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.5/repin.sh",
      "chunk_id": "dc0ec6d285abeea505e8f6c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "5e17ee4e1d7bf08157ac77dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md",
      "chunk_id": "88c90996599b18dab17a3b6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "bb83644e0cd4366ecd463298",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "6dfcb515e705fc84619389a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/install/dispatch.py",
      "chunk_id": "61f9aa65b68bf0fa81ed3506",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.3/repin.sh",
      "chunk_id": "1210de37d65b5abd47130157",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "e908da04f9cdd06a6e65c7da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.2/repin.sh",
      "chunk_id": "094ec07c26f8ff9b90fbc807",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "50d33a8d64c3696873ddc05a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/OWNER-GLOSSARY.md",
      "chunk_id": "db62e2964314ad01ce3208b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/release/repin.py",
      "chunk_id": "709ebf408541624a94daf32c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-209/README.md",
      "chunk_id": "7c61e6eb41e6c2fbe5bc3486",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5863
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWEyaDUubWQiLDQyLDQyLCIyNzYxYTk3MzlhYTMyNzYwNzRhNjQ4NGIiXSxbIi50aWNrZXRzL0RBRU8tYTJoNS5tZCIsNDMsNDMsIjk1MTc1OTA2ZDBiNWNhMDc1ZDc2ZDUwZiJdLFsiLnRpY2tldHMvREFFTy1zZGhqLm1kIiwxMzcsMTQ2LCI1N2QxOTIxOWQyOTg2YWJkZGY5YWM5ZjUiXSxbImRvY3MvYWRyL0FEUi0wMDAyLWFyY2hpdGVjdHVyZS1hbmQtc3RhY2subWQiLDE1NiwxNjcsImE1NGQ0MDk0N2VmN2Q1N2UxZjVkM2IwNSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9yZWxlYXNlLTAuMS4yL1NURVBTLm1kIiw0MSw0OSwiZGEzNzkxY2VhMGU4ODhmNTA0NTQ5YjNlIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3JlbGVhc2UtMC4xLjIvcmVwaW4uc2giLDc4LDkxLCJlM2I3MDFkMDdmODY5YmUyYWI3YzE2YjIiXSxbImRvY3MvZW1lcmdlbmN5LTIvcmVsZWFzZS0wLjEuMy9TVEVQUy5tZCIsNDUsNTIsIjJhNzYwMGNlZTJmZmUxNjVjZDBhZDZjYSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9yZWxlYXNlLTAuMS4zL3JlcGluLnNoIiw3OCw5MSwiODE0NzkxYzczMTE1MDQxNzBkMTExMThkIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3JlbGVhc2UtMC4xLjQvU1RFUFMubWQiLDUwLDU5LCI3MmQ1YWMwYWFlNzJhOTI4Y2E2MWQxNWYiXSxbImRvY3MvZW1lcmdlbmN5LTIvcmVsZWFzZS0wLjEuNC9yZXBpbi5zaCIsMSwxMywiNzFmOGZkM2JmMTMxZDhlMTcxMmUwMDMzIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3JlbGVhc2UtMC4xLjUvU1RFUFMubWQiLDUyLDYxLCJhNjMyNjU3MWQzZmJlNjI3MGViMmRiMjYiXSxbImRvY3MvZW1lcmdlbmN5LTIvcmVsZWFzZS0wLjEuNS9yZXBpbi5zaCIsMSwxMSwiNjM1MGU5YzRlNDZkNzZmMDA5ODk4NzA1Il0sWyJkb2NzL3BsYW4vd2F2ZS0yL3cyLTIwOS1yZWhlYXJzYWwvcmVzdWx0cy5qc29uIiwxODQsMjIwLCIyMjIzZDBhYzIyNWQzNmY5ZWU4NjEzZTQiXSxbImRvY3MvcGxhbi93YXZlLTIvdzItMjA5LXJlaGVhcnNhbC9yZXN1bHRzLmpzb24iLDIxNSwyNDcsImQ4NmJjNGY2N2M5OWMyMzI0MzBjZWFmZSJdLFsiZG9jcy9yZXNlYXJjaC9XMi0xMzAtbGluay1jbGVhbnVwLm1kIiwyMjkwLDIyOTIsIjkwNWY4ODdjNWEyMzc1ODdjYzViM2I0ZiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1SRUxFQVNFLTIubWQiLDExNCwxMjIsIjIwZTU0MTEzZGJhMTNkNzYzYWY3YTRjOCJdLFsic3JjL2dvdi9yZWxlYXNlL3JlcGluLnB5IiwxLDEyLCI1ZjBlYjdiMDM3Yzk0NTlmNGNhYWQ4YzkiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWIiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6ImE2ZmU3MGJlNWY0MmE2ODkiLCJvIjpbOSwxMywyMywzOSwwLDE1LDM1LDIsNCw2LDE3LDExLDI5LDMzLDE5LDM3LDIxLDMxLDI3LDI1LDMyLDE0LDgsNyw1LDM0LDMsMjYsMjQsMSwxMiwyOCwyMCwzNiwyMiwxOCwxMCwzOCwzMCwxNl19LCJxIjoiSG93IGRvZXMgdGhlIGF1dG9tYXRpYyByZS1waW4gKGdvdiByZWxlYXNlIC0tcGF0Y2gsIHJlcGluLnB5KSBzd2l0Y2ggdGhlIGdvdiBsaW5rLCBydW4gaXRzIHBvc3QtcGluIGNoZWNrcyBhbmQgcm9sbCBiYWNrLCBhbmQgaG93IGlzIHRoZSBnb3YgZW50cnkgb2YgdGhlIHRvb2wgcmVnaXN0cnkgd3JpdHRlbiBpbiBhIHJlLXBpbj8gQ29kZSBsb2NhdGlvbnMsIGNvbnZlbnRpb25zLCBlYXJsaWVyIGZpeGVzIGFuZCBmaW5kaW5ncy4iLCJyIjowLCJzIjoiNTc5ZDMyZGU3Yzg1ZmUzMzk2ZDgwZTU0ZjdiMGRiMTg4YjQwNWQyYSIsInQiOm51bGwsIngiOlsiMWFhYjViMWY0M2JkMTcxZTExMjU3NDQ2IiwiNWQ2MmRiYTI4MjBjY2JkZTA1MTJiY2E2IiwiOTI4YzkwMTM3NmEwZTc1N2EzOTQzZmQ3Il19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "How does the automatic re-pin (gov release --patch, repin.py) switch the gov link, run its post-pin checks and roll back, and how is the gov entry of the tool registry written in a re-pin? Code locations, conventions, earlier fixes and findings.",
      "automatic re-pin gov release --patch repin.py switch gov link run post-pin checks roll back gov entry tool registry written re-pin Code locations conventions earlier fixes findings."
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": []
  }
}
```
