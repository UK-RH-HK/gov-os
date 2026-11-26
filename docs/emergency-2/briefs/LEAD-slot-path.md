# Lead brief: slot-path, the landing's test run sets the tools' PATH itself (plan item 1-13, I-6; a fix under W2-20, DAEO-r30l)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store`.

## Why
FINDINGS I-6: a test run without node's bin on `PATH` reads nine W1-30/W2-02 cases red on a green base (`openspec` absent); every brief
works around it by putting `$HOME/.nvm/versions/node/v22.23.3/bin` on `PATH` by hand. Plan row 1-13
(`docs/emergency-2/integration/INTEGRATION-PLAN.md`): "the product slot adds the registry's Node 22 prefix (W1-48's check), so a run
from a shell without node's bin is not red." Read I-6, row 1-13, `governance/project/tool-registry.yaml` (the node entry) and
`src/gov/resources/slots.py`.

## What (K-lines as a `## Fix:` section in `.tickets/DAEO-r30l.md`; the CTO approves them by this brief)
- **SP-1** The product's test run (the slot `gov queue` and `gov close` run their tests through) prepends the registry's pinned Node 22
  bin to `PATH` for the run, read from the tool registry, never a fixed path in code. Verify: the nine W1-30 and W2-02 cases pass from a
  shell whose `PATH` has no node.
- **SP-2** `gov doctor` names the Node prefix the slot uses, and says so by name when the registry's node is missing (never a silent
  red). Verify: planted registry without node: doctor names it.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-slot-path`, branch `e2/slot-path` from `w2/integrate`. Code area: `src/gov/resources/`, the
doctor part that reports tools, `tests/unit/resources/`, `tests/acceptance/W2-20/` (the independent test designer only),
`.tickets/DAEO-r30l.md`. Do not edit `tool-registry.yaml`'s entries (the CTO's). Another lead works on `src/gov/queue/` meanwhile;
`e2/bundle-a` and `e2/bundle-b` are held: do not edit their files.

## Green
SP-1 and SP-2 red on the base, green after; `gov accept W2-20` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-r30l=e2/slot-path --onto w2/integrate --select`) through the heavy slot.
Check the trailers (LEAD-COMMON).

## Return
Branch and head; where the PATH is set (file:line); SP-1 and SP-2 with tests and result; the selected run's summary; your retrieves
(count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: e45987702892 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "e45987702892d5d66992499eec8f90beb1cd4845",
    "head": "e45987702892d5d66992499eec8f90beb1cd4845",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-r30l",
      "sha256": "c27836f83b280201337243a73e6c6c2b4bae01af9ca8fa6f71e6279cb081663f",
      "path": ".tickets/DAEO-r30l.md",
      "start_line": 67,
      "end_line": 115,
      "text": "  - 'Any fixed ceiling on leads or sessions other than the heavy-job slots (DEC-983).'\n  - 'A value the gate uses not taken from the configuration file, or a reading that cannot be taken treated as met.'\n  - 'A worker''s memory charged twice (in its lead''s tree and as its own session).'\nprofile: STANDARD\nsources:\n- DEC-866\n- DEC-753\n- DEC-1109\n- DEC-729\n- DEC-742\n- DEC-747\n- DEC-898\n- DEC-941\n- DEC-942\n- DEC-947\n- DEC-950\n- DEC-954\n- DEC-983\n- DEC-1001\n- DEC-1003\n- DEC-1010\n- DEC-1017\n- DEC-1030\n- DEC-1031\n- DEC-1038\n- DEC-1039\n- DEC-1041\n- DEC-1045\n- DEC-1088\n- DEC-1037\n- DEC-1097\n- DEC-899\n- DEC-961\n- DEC-979\n- DEC-982\n- DEC-803\nest_loc: 320\nacceptance_tests:\n  path: tests/acceptance/W2-20/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\ncloses:\n- W2-M244\n- W2-M188\nlist_rows:\n- W2-M188\n- W2-M244\n- W2-M262\n---\n",
      "chunk_id": "a306b3db1d20725c6aab2973",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-r30l",
      "sha256": "bcf2bdb62145b7ec809b149d2bf36aa1c10d156c2f31353acc2d715eb259ea54",
      "path": ".tickets/DAEO-r30l.md",
      "start_line": 1,
      "end_line": 32,
      "text": "---\nid: DAEO-r30l\nstatus: closed\ndeps: [DAEO-g0ip]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-20\ntags: [wave-2, implementation, standard]\nwbs_id: W2-20\ntitle: Machine-wide resource gate\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\nallowed_paths:\n- src/gov/resources/**\n- src/gov/check/commands.py\n- src/gov/launch/gate*\n- tests/unit/resources/**\n- src/gov/rebuild/watch.py\n- tests/unit/rebuild/test_w2_20*\n- src/gov/secrets/__init__.py\n- src/gov/codeintel/__init__.py\n- tests/unit/secrets_check/test_w2_20_*\n- src/gov/retrieval/ollama.py  # the query embedder's automatic start, for the DEC-1037 line [added, DEC-1037; DEC-1097 (8)]\n- src/gov/launch/plan_check.py  # W2-136's F2 entry criterion [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- src/gov/launch/launcher.py  # the launch's call of the gate and its override (P-1) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- src/gov/launch/command.py  # gov launch's --gate-override and --gpu-need-mib options (P-1) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n",
      "chunk_id": "d857af5b6d9a8e0265b165d2",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DEC-452",
      "sha256": "8219296106017c8965ae7155d8be4da564673cfef95a5fec5b4ad9090107309b",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 682,
      "end_line": 693,
      "text": "### DEC-452 \u2014 Doctor looks under every registered PATH prefix before PATH, and a tool it cannot verify fails\n- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07) \u00b7 **Basis:** the orchestrator's reading of W1-27's code and of `gov doctor` run on this repository after DEC-448 was built: `openspec` and `ccusage` are found under the prefix their registry entries carry, Node is not (its entry's install command is the `nvm install` line and carries no prefix; the place is only in a free-text note), `socat` passes with no version read and no hash match, and one case asserted a key name \u00b7 **Under:** DEC-202, DEC-425, DEC-440, DEC-448 \u00b7 **Class:** kept\n- **Decision:**\n  - Doctor looks for a tool first under its own registry entry's PATH prefix, then under every PATH prefix that\n    any entry of the registry carries, in the registry's order, and only then on PATH. This is the reading of\n    DEC-448's \"the PATH prefix of DEC-202\" for a tool whose own entry carries none; with it Node 22 is found\n    where it is installed, and the registry is not changed.\n  - A tool passes only when the version read equals the pin, or, where no version can be read, when the file's\n    hash equals the pinned hash. A tool for which neither can be established fails, with the reason; so does a\n    version command that errors or times out (DEC-440: an error in a measurement is a failure).\n  - Both are fixed test-first (DEC-136) inside W1-27, without a further review round (DEC-413).\n\n",
      "chunk_id": "fd552be86eb57e1e3c600c5d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-452",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "2bdfab01fa9ca5244f596219",
      "sha256": "6fa0cebef345c5819079e0336aa98b4374f6bc86b20e73b1c5be9f4f62868324",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 74,
      "end_line": 75,
      "text": "| 1-12 | **A pairwise merge check in `--select`**, before the slot wait: two candidates that each merge alone but not together are told at once. [I-3] | W2-115b | fix S | 1-1 | W11 | Two planted branches edit one line differently: the landing says `CANDIDATE_NOT_ISOLATED`, naming both, within seconds and before any slot is taken (no slot-wait line in its log). |\n| 1-13 | **The landing's test run sets the tools' PATH itself:** the product slot adds the registry's Node 22 prefix (W1-48's check), so a run from a shell without node's bin is not red. [I-6; map row 46] | W2-20 (DAEO-r30l) | fix S | none | W11, W8 | Run the nine W1-30 and W2-02 cases from a shell whose PATH has no node: they pass, and `gov doctor` names the Node 22 prefix it used. |\n",
      "chunk_id": "2bdfab01fa9ca5244f596219",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2d46a19e273c58c690fcbaea",
      "sha256": "45d9de30525467f9d51bc2a0b1fcf6e47b89cdcffb7f37a7dc05099b3934d4b5",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 75,
      "end_line": 77,
      "text": "| 1-13 | **The landing's test run sets the tools' PATH itself:** the product slot adds the registry's Node 22 prefix (W1-48's check), so a run from a shell without node's bin is not red. [I-6; map row 46] | W2-20 (DAEO-r30l) | fix S | none | W11, W8 | Run the nine W1-30 and W2-02 cases from a shell whose PATH has no node: they pass, and `gov doctor` names the Node 22 prefix it used. |\n| 1-14 | **The landing proven on the scratch repository and in EXAMIN.** The scratch repository gets `governance/project/queue.yaml` (as EXAMIN has; the kit ships the default if it does not); it takes one green, one red and one dirty landing through `gov land`; EXAMIN lands its next real branch through it. Gov OS's own landings stay plain until Day M; the old landing tools retire on Day M (4-4). [A-1 as changed by DEC-1239 (3), (4); DEC-1217 L2-4; map rows 58 to 62] | W2-115b; the kit W2-208 | chore + proof, S | 1-1 to 1-13 | W11 | Three records exist in the scratch repository: green (a close record with its selection and impact list), red (the 1-6 record), dirty (`QUEUE_WORKTREE_DIRTY` naming files). EXAMIN's branch has a close record with a selection file and an impact list. |\n\n",
      "chunk_id": "2d46a19e273c58c690fcbaea",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-xm6l",
      "sha256": "cf63a44d2c572e76f8ad74f7d1b3a6e6269596af16b3d375a51d5d83ef73b2cf",
      "path": ".tickets/DAEO-xm6l.md",
      "start_line": 98,
      "end_line": 115,
      "text": "## Fix: `gov doctor` checks a tool installed in its own folder (audit 3, M-04; DEC-1232, DEC-1233)\n\nFound 2026-11-22 by the E2 audit 3 (`docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md`, M-04): the registry entries\n`node-22.23.5` and `rea-agents` read `ok: false` in doctor's `tools` part, because doctor found a binary only by\n`TOOL_BINARIES` or a `PATH=<prefix>:$PATH` in the install line. No test caught it. Required: both found and versioned with\nno schema change; a `PATH=` prefix from one tool's install line never answers for another tool of the same binary at\nanother version (v22.23.5 never for `node` v22.23.3, nor the reverse). Kind: a fix, no new ticket; the ticket stays\nclosed. Failing tests first: `tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py` (README ids success-3 to\nsuccess-7; 17 red, 13 guards on the base), `1015d60e8`; code `src/gov/doctor/command.py` (a `<binary>-<version>` name maps\nto its binary; a tool's places are its own `PATH=` prefix, a local install's `<cd folder>/node_modules/.bin` and a Node's\nnvm folder for its pinned version; a folder owned by an entry of the same binary at another pinned version is skipped;\nthe install line's `~` and `$HOME` read the process's HOME), `d21973e3c`; units `tests/unit/doctor/test_w2_22_own_folder.py`.\nLead `fixes-015b` (Sonnet), branch `e2/fixes-015b`. `gov accept W2-22` green (success-1 to success-7, 46 passed) on the\nfirst run after the engineer's commit; `tests/unit/doctor`, W1-27, W1-06, W1-48, W2-22: 229 passed. On the real machine\n`gov doctor --json` now reads `node` v22.23.3, `node-22.23.5` v22.23.5 and `rea-agents` 6.10.1, all `ok: true`; the\n`pytest-xdist`, `pytest-timeout` and `pytest-testmon` entries (Python packages with no binary, not in `NO_BINARY_TOOLS`)\nstill read `ok: false`, as on the base: not this fix's.\n\n",
      "chunk_id": "f1267d9087f4f3e7a64697ce",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "bcfbc0f8d0bc99df76b20952",
      "sha256": "894bdf72743fcce096b033cdddab659b1ac2ccbb667c6186fcbf95aa1486182d",
      "path": "docs/emergency-2/briefs/LEAD-COMMON.md",
      "start_line": 5,
      "end_line": 17,
      "text": "## Where you work\n- Your own worktree and branch: `git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree add -b e2/<name> /home/usain/gov-os-worktrees/E2-<name> w2/integrate` (or the existing ticket worktree your brief names: bring it up to date with `git merge w2/integrate` first). Work and commit only there.\n- **Never commit to `w2/integrate`** and never touch the main tree `/home/usain/Dynamic-Agentic-Engineering-OS`: the CTO works there and lands your branch.\n- Never `git push`, never `sudo`. Full permission otherwise in your worktree, its `-tests` worktree and `~/gov-os-runs/`.\n- **The machine rule.** Every test run goes through the machine-wide heavy slot (two slots today), one run at a time:\n  `T=$(mktemp -d); PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=$T PYTHONPATH=<worktree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -n auto; chmod -R u+w $T; rm -rf $T`\n  - Node's bin on `PATH`, as the command does (the CTO, 2026-11-22: without it `openspec` is absent, `gov close`'s check family turns RED and nine W1-30/W2-02 cases read red on a green base).\n  - Remove the run's temp folder when the run ends, as the command does (the CTO, 2026-11-19: 1,050 leftover `/tmp/tmp.*` folders took the free inodes under the resource gate's floor twice in one night, which shuts the gate and turns every close test red).\n  - Add `-n auto` to a pytest run of more than one file (the CTO, 2026-11-19: without it the run is one process; the slot caps `-n auto` at its workers, three today). Never `-n` with a number. `PYTHONPATH` absolute (tests start `gov` in subprocesses). The slot waits while taken; never bypass it.\n  - The slot also waits until the machine's 1-minute load is under 12, so the load stays inside the resource gate of 20 (the owner, 2026-11-18). A wait is the rule working: let it wait. Never run pytest outside the slot, and never with a number after `-n`.\n  - The smallest set that proves your change; no full suites (the CTO runs those); no rebuild and no memory measure without asking the CTO.\n  - Before starting a worker: `uptime` and `free -g`; over load 30 or under 3 GB available, wait.\n\n",
      "chunk_id": "bcfbc0f8d0bc99df76b20952",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "480cd7c247896c096c5c2505",
      "sha256": "7ae2c0c3ba4affad6f8ee28c82bf755d3661ac51e4f3f4fca99636fd57ae8f5d",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 1,
      "end_line": 15,
      "text": "# W2-20 \u2014 the machine-wide resource gate: evidence (DAEO-r30l, round 3: the review's findings; round 2: the interface)\n\nRound 1 (`8985180a3`) built every line but S16, but `gov accept W2-20` passed 39 of 164: the acceptance cases assume an\ninterface (the designer's README, \"The interface these tests assume\") round 1 could not see. Round 2 brings the product\nto that interface, handed to the engineer in its brief (the ticket's round-1 point (3)); the engineer read only the\ninterface and `gov accept`'s results and one-line failure messages, never the cases.\n\n**Where it lives:** `src/gov/resources/` (`config.py` the one file, `machine.py` the readings, `registry.py` the\nsessions, `gate.py` the conditions and `check_disk`, `slots.py` the slots, CPU sets, thread budgets and trip-wire,\n`measure.py` the sample and re-measure, `command.py` the command; `gov.resources.check_disk` for `gov close`);\n`src/gov/launch/gate.py` (the start check and the launch log); `launcher.py`, `command.py`, `plan_check.py` (the\nlaunch's enforcement and F2); `rebuild/watch.py` (each tree its own lock); `secrets` and `codeintel` (pools);\n`retrieval/ollama.py` (DEC-1037). Unit tests: `tests/unit/resources/` (150 cases), `tests/unit/rebuild/test_w2_20_*`,\n`tests/unit/secrets_check/test_w2_20_*`; planted machines only.\n\n",
      "chunk_id": "480cd7c247896c096c5c2505",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "1180baf27d8f36e2d4c21ec7",
      "sha256": "f1d2ae9a06ced7682bbad1a3c133a45216de147cbe39d565f8d72f352677e96a",
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "start_line": 15,
      "end_line": 17,
      "text": "## Green\nRP-1 red on the base, green after; `tests/unit/release`, W2-209 and W2-16 green; then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-a2h5=e2/fix-repin-registry --onto w2/integrate --select`), through the heavy slot. Check the trailers (LEAD-COMMON).\n\n",
      "chunk_id": "1180baf27d8f36e2d4c21ec7",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "8f581c572c4ebae606efdf0f",
      "sha256": "edacf878680353224ed86bda597773f2a3fc4e5245ed7dae04b882e81b8fd3c3",
      "path": "docs/changes/W2-156-evidence.md",
      "start_line": 90,
      "end_line": 106,
      "text": "## The runs (heavy slot, the sandbox's own `$TMPDIR`, `HOME` an empty folder, `-m \"not local_only\" -k \"not real and not green_here and not time_limit\"`)\n\n| run | result |\n|---|---|\n| `tests/unit/spend tests/unit/launch/test_w2_156*` | 43 passed |\n| `tests/unit/launch tests/unit/check` (whole) | 1033 passed, 219 deselected |\n| `tests/acceptance/W2-60a W2-60b W2-184` | 798 passed, 6 deselected |\n| `tests/acceptance/W1-07 W1-26 W1-32` | 264 passed, **1 failed**, 477 deselected |\n| `gov accept W2-156` | `\"outcome\": \"pass\"`, 34 passed, 0 failed (success-1..6, failure-1..3) |\n\n**The one red, outside the paths:** `tests/acceptance/W1-32/test_w1_32_command_set.py:118-120`\n(`test_the_command_set_is_the_twelve_and_the_three_recorded_ones`): `assert not extra` \u2014 \"gov has commands the command list does not\nrecord: ['spend']\". Its recorded set is `cli_support.RECORDED_GOV_COMMANDS` (`tests/acceptance/W1-07/w1_07_support.py:52-71`) plus its own\n`RECORDED_HERE` (`W1-32/test_w1_32_command_set.py:64`, `(\"adapters\", \"dispatch\", \"session-watch\", \"wait\")`), both held exact by other tickets;\n`spend` is in neither. The same precedent as W2-160's `wait` (added to `RECORDED_HERE`). Not edited: a path case for the lead. W1-07 and\nW1-26 pass. No command list document names `resources` or `wait` beside the others outside these two files and `src/gov/check/commands.py`\n(searched).\n",
      "chunk_id": "8f581c572c4ebae606efdf0f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-h4rh",
      "sha256": "d2cfaa0832c9bfaf3f4ecc59eb5cb7fc8374681cbd9417b76ce65c5f8ac3f236",
      "path": ".tickets/DAEO-h4rh.md",
      "start_line": 62,
      "end_line": 125,
      "text": "# The six below are on EXAMIN's copy's path (AUDIT-NIGHT-1 d-tools \u00a75): W2-42a, W2-116, W2-145, W2-153, W2-156, W2-157 [added, DEC-1112 (3), the CTO's delegated decision]\n- DAEO-03ub\n- DAEO-f58b\n- DAEO-2tfd\n- DAEO-8s85\n- DAEO-ozyt\nallowed_paths:\n- docs/plan/wave-2/examin-copy/**\n- docs/changes/W2-27-CIT-P.md  # [DEC-1089]\nkpis:\n  success:\n  - 'The pinned, hash-verified release is installed: W2-16''s release only. [re-scoped, DEC-1083]'\n  - gov adopt runs A0 to A6 and A8 with the A5 independent review, and the lite A7 and A10 gates of Contract v4.2.\n  - EXAMIN's own CLAUDE.md, settings and untracked files are preserved (W2-23).\n  - '`gov doctor` is green (the `gov check` families follow T-2, W2-45). [re-scoped, DEC-1083]'\n  - 'One LITE ticket goes through the full cycle: test designer, red, implement, green, then gov close at exit 0 with EXAMIN''s own test command.'\n  - Its governance share is measured and \u2264 15 %.\n  - At the first full gov rebuild after adoption, each index's time, peak RSS and node and edge counts on EXAMIN are measured with W2-26's method and RSS sampler, against DEC-078's envelope; a figure over the envelope stops the ticket, and W2-45 joins its dependencies [DEC-735].\n  - 'EXAMIN''s red tests are named in the close record, each with its cause (an environment red or a real one), with no ratchet baseline and no known-red list [DEC-736, DEC-745, W-4] [re-scoped, DEC-1083]'\n  - One pinned install package goes to the owner. It holds EXAMIN's 10 product-suite packages from EXAMIN's own lock file, installed into the clone's own virtual environment only. With the owner's approval,\n    the product suite is measured before W2-30's verdict. Until then it is \"needs environment\", reported UNMEASURED by name and never as passed [DEC-736].\n  - EXAMIN's governance kit stays in a legacy namespace, and its tests stay in the declared test command. The A5 review maps each of its checks to a Gov OS check family or to \"no equivalent\" [DEC-736].\n  - The path map marks the tool-configuration folders (.claude/commands/ and the kit's .claude/ templates) as not records. The files in spec/5-REPORTS/attempts/ get a mechanical quoting fix of their front\n    matter with no change of content, as an adoption commit. If the store cannot leave paths unread, all 18 files get the fix [DEC-736].\n  - EXAMIN's own CLAUDE.md, AGENTS.md and .claude/commands/ are never silently overwritten. Their content is migrated into EXAMIN's rulesync sources or kept in place, and the A5 review checks that nothing\n    of the owner's was lost [DEC-736].\n  - 'W2-16''s numbered, frozen release is the one installed, never this repository''s branch [DEC-954 Q8c]'\n  - 'A clean gov close of the LITE ticket on the copy, at exit 0, on that release, is exit criterion 1''s proof; gov doctor green on the copy is exit criterion 3''s [DEC-953, DEC-954]'\n  - 'W2-88''s tools run on the copy at adoption (the assessment, the refactoring plan as proposals, the full index and embeddings), and EXAMIN''s question set (W2-94) is measured with both figures, hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 % [DEC-954 Q9f, DEC-957]'\n  - 'The first numbered, frozen release is cut by the owner and hash-checked (two builds give the same bytes; the wheel and every file match the manifest), recorded in docs/plan/wave-2/examin-copy/release-check.md, before W2-81''s proving-ground run and this ticket''s adoption [DEC-1089, DEC-954 Q8c, DEC-772]'\n  - 'Exit criterion 7: CAP-45.a moved to Wave 3 by an approved CIT-P note (docs/changes/W2-27-CIT-P.md), or named as an exception the owner accepts [DEC-1089]'\n  - 'The copy''s `governance/project/facts.yaml` holds EXAMIN''s own commands (`launch_worker` = `gov launch`, `wait_for` = `gov wait`, `lead_verify` = EXAMIN''s own verify command, the rest from the adoption''s defaults), and every role''s brief (the five worker roles and the lead''s run kinds) builds with `gov brief` in the copy; the copy carries no `governance/project/secrets.yaml` or one with `scan: on`, so the secrets scan stays on there Verify: `gov brief <role> <ticket>` exits 0 in the copy for each worker role and each lead run kind on one of its tickets; `gov check` there shows the secrets-indexing check measured (not \"off by configuration\") [DEC-1148 (2), DEC-1045]'\n  - 'Before any scoped close in the copy, its suite runs once in full at the adoption commit (`gov close --full`); every red there is either fixed or listed in the copy''s `governance/project/path-map.yaml` `accepted_reds` (test, the owner''s decision, reason, fixed_by) by an ACT the owner approves, so the full close passes and its record (`docs/close/<id>/CL-*.md`, scope full) is the copy''s first green base; a red the owner does not accept blocks the adoption, not a later close Verify: the copy holds a full close record at the adoption commit before its first scoped close; that scoped close judges its reds against the record''s head; each `accepted_reds` entry names an owner''s decision that resolves [DEC-1151, DEC-1150 (2), DEC-757, DEC-1134]'\n  failure: []\nprofile: FULL\nsources:\n- DEC-727\n- DEC-728\n- DEC-735\n- DEC-736\n- DEC-741\n- DEC-745\n- DEC-953\n- DEC-954\n- DEC-957\n- DEC-772\n- DEC-1083\n- DEC-1089\n- DEC-1090\n- DEC-1112\n- DEC-1045\n- DEC-1134\n- DEC-1148\n- DEC-1150\n- DEC-1151\n- DEC-757\nest_loc: 0\nacceptance_tests:\n  judged_by: 'its class (WBS \u00a70 rule 1, W2-07): its named evidence files'\ntrack: B\ncloses:\n- Track B\nlist_rows: []\n---\n",
      "chunk_id": "f2ff83b9c1de2b1952e36003",
      "routes": [
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "48ca053bb7794ab0838a14ac",
      "sha256": "f310a7bf9c121a8e5885d2da5557ca5eeb724f717746e14fdd4f9c7af0d9c12f",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 24,
      "end_line": 35,
      "text": "\n**The interface's one disagreement, named:** the round-8 README computes the p95 from the kept (600 s) samples; S12\nand round 7 keep it over a week. As the brief rules, the p95 keeps round 7's week; the expiry rule applies to the\ncurrent use (and to when a server is sampled afresh).\n\n**Round 4's runs (inside the sandbox; `HOME` an empty scratch folder with only the user site's `lib` linked in):**\n\n- `gov accept W2-20`: **170 passed, 0 failed, 1 skipped (171)**; every line passes but S16, whose one case skips (the\n  CTO's run outside the sandbox).\n- Unit tests, `tests/unit/resources tests/unit/launch` with `-m \"not local_only\" -k \"not real and not green_here and\n  not time_limit\"`: **287 passed, 86 deselected**.\n\n",
      "chunk_id": "48ca053bb7794ab0838a14ac",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "cf89e8427a76f0c42f62a451",
      "sha256": "d96379a7440bc61e2e0d7d2a0cc7e376cc381eb45a1cde65e4b7d3c5e37f42b1",
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "start_line": 1,
      "end_line": 4,
      "text": "# P-W2-20-SCOPE \u2014 W2-20's built gate contradicts DEC-942 and DEC-947: re-scope it, merge it as built, or park it\n\nFrom: the W2 orchestrator, 2026-10-29, sent the day it arose (DEC-949). Your decision: it adds a lead run to a held ticket (DEC-817).\n\n",
      "chunk_id": "cf89e8427a76f0c42f62a451",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "eff945ad78eb9b07334fa418",
      "sha256": "19a7b11a4494b5cad48a2707e6df2c1dc379be73871a2f9434e0b336b919597b",
      "path": "governance/project/orchestration/closes/W2-20-DAEO-r30l.md",
      "start_line": 1,
      "end_line": 9,
      "text": "# W2-20 (DAEO-r30l) closed: by DEC-953's practices after the lift (DEC-1132 (1)); merged through round 4, left unclosed at the lift, found stuck 11-11 22:20\n\n- Head at close: d5cb07eb5 (w2/integrate); the accept ran at 865ea01e94dc, and nothing between touches W2-20's paths (W2-55's close record and ticket, ACT packages and reviews only: 6 files); profile STANDARD (no probe gate)\n- Evidence: `gov accept W2-20` (the pinned judge, pin-797495bdfc70) through `heavy_slot.sh` with `GOV_W2_20_MEASURE=1` (S16 measures the real machine: \"the CTO runs it with GOV_W2_20_MEASURE=1\"), at 865ea01e94dc, 2026-11-11 22:25:09-22:34:46 UTC: outcome pass, rc 0; 171 passed, 0 failed, 0 skipped. Log `.gov-runtime/scratch/orchestrator/log/close-w2-20-r2/`. The run without the opt-in (22:21:20) failed on success-16 alone, its only case skipped.\n- Branches: `w2/W2-20` and its test and D-10 branches fully merged. `w2/W2-20-1017` holds 10 commits of the first build (DEC-1017, four weeks old: gov resources and the gate, run 2's boundary), superseded by the rounds merged since; kept, not merged, not deleted (a sweep item after a look).\n- Lines met in part or by reading: none (every line passes in the acceptance run)\n- Why now: W2-121 (on W2-27's path) depends on it; one of the merged-not-closed tickets the lift's formal closes left, found by the CTO's free-slot sweep.\n- Route: `tk close` and this record (DEC-953 items 1 and 5); `gov close` and its gates are lifted here (DEC-953, DEC-1052 Q-8) and return through W2-115 on evidence (DEC-1128 (2), DEC-1132 (1)).\n- Closed: 2026-11-11, by the orchestrator (session b2f0511f).\n",
      "chunk_id": "eff945ad78eb9b07334fa418",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "720ac2cc2763c6b062957cb9",
      "sha256": "1c1f6b835fe71e082f083914a7d5c641391b9f5d41285baf7a683680850f2635",
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "start_line": 5,
      "end_line": 13,
      "text": "## 1. Context\n- **The ticket:** W2-20 (`DAEO-r30l`) is the machine-wide resource gate in the product. It is one of the nine held tickets to be merged back (DEC-941 item 2), and in priority 4 (DEC-946).\n- **Its branch:** head `1a54976c7a71`, worktree clean, 10 commits ahead and 789 behind. STANDARD, with no probe. It has been held since 2026-10-17 for the close order (DEC-737).\n- **The rules changed since it was built:**\n  - DEC-942: the load below `nproc`, no fixed number of leads;\n  - DEC-947: memory reserves the floor, one verification run's peak once, and a working size per lead; the floor is 3 GiB;\n  - DEC-941 item 6: the capacity minimum in W2-20's KPIs;\n  - DEC-898: the disk and inode floors.\n\n",
      "chunk_id": "720ac2cc2763c6b062957cb9",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "5079e429695507253a3d1c86",
      "sha256": "2bc0b4d1107e198841422c16c9807b9e7d1c14ad2298b9873512e3852cca14f4",
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "start_line": 24,
      "end_line": 28,
      "text": "## 3. Why it matters\n- **Merged as built,** the product would ship a gate that refuses what the owner's own rules allow, and allows what they refuse (no disk floor).\n- **The orchestrator meanwhile** runs DEC-942/947 by hand (`tools/gate_check.py`) until W2-20 carries it.\n- **Block D (K6)** waits on W2-20: W2-21 needs it.\n\n",
      "chunk_id": "5079e429695507253a3d1c86",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "f5d5944209e8821ca961d3dc",
      "sha256": "58043059af81c12294c956f5f91563b3d9abc5b4044e010bc936a55d6c1d39cf",
      "path": "governance/project/orchestration/packages/P-W2-20-THREAD-BUDGET.md",
      "start_line": 35,
      "end_line": 37,
      "text": "## Options\n(a) Add the three lines to W2-20 now (recommended; W2-20 is in progress, STANDARD; the lines are small and the CTO's\nscript is the reference). (b) A ticket of its own after W2-20. (c) Defer to Wave 3.\n",
      "chunk_id": "f5d5944209e8821ca961d3dc",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "f970f33e961dfebd0867d5a2",
      "sha256": "dafc81a9a95291b4adb64bdc8f4c25447695e87db96d9bb13373faa528bd6e28",
      "path": "governance/project/orchestration/packages/P-W2-20-THREAD-BUDGET.md",
      "start_line": 1,
      "end_line": 6,
      "text": "# P-W2-20-THREAD-BUDGET: a heavy run's child programs stay within its slot's share (KPI proposal, DEC-1003)\n\nFor the owner. One decision: add the KPI lines below to W2-20 (`DAEO-r30l`, the machine-wide resource gate, the\nproduct), so every adopted repository's heavy runs keep their child programs within their share. Proposed by the CTO\n2026-11-02 ~17:10 under DEC-1038 (4) and the owner's order to map the CTO's gate fix into the product the same day.\n\n",
      "chunk_id": "f970f33e961dfebd0867d5a2",
      "routes": [
        "lexical"
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
    "duplicates": 56,
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
      "chunk_id": "fd552be86eb57e1e3c600c5d",
      "parent_id": "645954b916ae1bd9de52936a",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 682,
      "end_line": 693
    },
    {
      "chunk_id": "f1267d9087f4f3e7a64697ce",
      "parent_id": "fea89233776ce035ad5e8ff1",
      "path": ".tickets/DAEO-xm6l.md",
      "start_line": 98,
      "end_line": 115
    },
    {
      "chunk_id": "bcfbc0f8d0bc99df76b20952",
      "parent_id": "11f37ef14ce7cdf1ec438faf",
      "path": "docs/emergency-2/briefs/LEAD-COMMON.md",
      "start_line": 5,
      "end_line": 17
    },
    {
      "chunk_id": "480cd7c247896c096c5c2505",
      "parent_id": "8ad86159eed8f4a23428be67",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 1,
      "end_line": 15
    },
    {
      "chunk_id": "8f581c572c4ebae606efdf0f",
      "parent_id": "c3073f102a8bb5f25d174b52",
      "path": "docs/changes/W2-156-evidence.md",
      "start_line": 90,
      "end_line": 106
    },
    {
      "chunk_id": "f2ff83b9c1de2b1952e36003",
      "parent_id": "6cfa31519ccc80e495d290ec",
      "path": ".tickets/DAEO-h4rh.md",
      "start_line": 62,
      "end_line": 125
    },
    {
      "chunk_id": "eff945ad78eb9b07334fa418",
      "parent_id": "81eb119dd41fdf48e7c24fa7",
      "path": "governance/project/orchestration/closes/W2-20-DAEO-r30l.md",
      "start_line": 1,
      "end_line": 9
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-03ub",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-057v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0mtg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0pyc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0rfi",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0uhh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0z8c",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2azm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2ds6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2gc7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2keg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2tfd",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-3r1j",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-49o5",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-4k3l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-57hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-5j8b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-5rgj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-60rw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6n5k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6ox0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6w5n",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6y0x",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7r5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7rr2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7y6v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-8lmb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-8s85",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-9nys",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3m2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3u2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-arrl",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b6hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b926",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-blwa",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-btt7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-c1uz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-clon",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-csj8",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cuao",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cv58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cy5o",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-drhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e82f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e8f0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ebmh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ecac",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-egsy",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-emq1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-f58b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-fau3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g23i",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g87r",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-gdzh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h2k3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ha8z",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ifgf",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-iw1f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-j8gn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jip3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jpr0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jsg1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-juee",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jzvg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k4wm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k7hz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kh9l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kia7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kiar",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kl5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kmcr",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-l78m",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-lrre",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-m1u3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-mb2t",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-n0wb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-neam",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-nqa2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ouet",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pg6i",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pl6k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qty6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qzrq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r8vq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r9ss",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rd0g",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rmbe",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s694",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s9qc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-sdhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-siiz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-swdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-t8mp",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-tgk2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ts4y",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u4oz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u5g6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-uzme",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-w19l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wahn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wbdh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wi46",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wnnz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wq2b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wudw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xm6l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xxgp",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-yadm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ye2a",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ym8a",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zflj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zndm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zoex",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zpdj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zqvn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "6ba8bec34704909eeecdec79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "871eeed88e8d0c2e5b17e2e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "f3375615ccb897db259534ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "b541dfb677e3f79fc088e7fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "chunk_id": "0c0d4f8fc11d8b140f15257c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "a8f919851aaa2de1f9f284a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "1733c1cecd322ae0cfb840d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "8c6269359aee82b6db14deaf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "f626cb5f1cd5f8dd954b06fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "664d72fc0dfec71366780597",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "f561dad9222054f51cbaa770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "122f93dcf757d14a572bee93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "2c1565c433bdb56ea6822f38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "3ccc002de3277b359df7c507",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "6c979c84e77819179eaf0158",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "295a946fabde8a795d6f6c30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1ahb.md",
      "chunk_id": "5a3e82392b078e63619948ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "9496ca58565b55cb3ecd40c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "5eb29ecae405641d1e1191dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "fec4bac5358fb780e1e3ce26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "8a9c2a797b18358d0215f392",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ifgf.md",
      "chunk_id": "48a9ae1e77c034e1b815279b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "chunk_id": "96c1217184d6345045be49cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "0485a75ba6ba5e39f1d47cf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "c1d49caaf2295ddc88322d81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "578f6c47a476204b4c6d440d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "59acb5069a5a5cbf59c6432b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "chunk_id": "e87f8864cc6ddee0eb8727f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-177-evidence.md",
      "chunk_id": "6079a9fcfff70da79386c7a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "a72bb4a67ef24af33f612be1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "b701bb831475b97e0fba805e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "15b201c4d5b4448bed2f64e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-156-evidence.md",
      "chunk_id": "aea5ff124716b62c66ba4a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "d61f1979ed8047df06e90e82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rt-slice3.md",
      "chunk_id": "198fb5aab6d3a2b06e3c7df3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "f37b05db098151d75bc06f6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e0af7683ed24975bcf924155",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "0854a1d8060cadbf4ff6c7f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-6.md",
      "chunk_id": "96de379106117e47e3e5e5a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-phase0-reds.md",
      "chunk_id": "c4f5c757b11a03a4af88c65f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "9b7c35db66eebdd3d3e88a08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "484bb8e3606df5af71d5efce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "0fb77d30531b0150b3878cb9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d6-doctor-drift.md",
      "chunk_id": "037a655bfe3cd3f853c6491e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "9358faefdac0817c9b7d83d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-156-evidence.md",
      "chunk_id": "05ff49a7275beefc63c14151",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "40f1628ed64ebfa9f2759bcd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "ca85f078ad5da7aecaa6dde9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "374bf07a75cfa079ce8997e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "d0982a4cb23117342c414db7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "e8eaa267003d6384b28b2b08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-57-CIT-E.md",
      "chunk_id": "f98d0d1146cb8bfa9cec0f0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "50cb43f8183a7707f4c5e564",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "d76ce7093778cb73ecad45e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "9722d226c977612a900869b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "cace67680752a3143833a86d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "829e18dbed19559dd991e947",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "df933bf4259f325175e28bb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cb2b.md",
      "chunk_id": "1ca2c3b73d5dcc4ec296186d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a9a3cdd6423d625d2a03ad2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "37b0b788b7071778264b2d4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-THREAD-BUDGET.md",
      "chunk_id": "7425f31a3b963d87db0f0abb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "bd52d9ebcfc16691483975e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "4f1f018c6002953eb0834b57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "4371ccbb27f24f988f4249f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "144c635b6c3d448ddbe4d268",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-THREAD-BUDGET.md",
      "chunk_id": "8f4a134608a2e77a1e8d34cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-w2-207-gate.md",
      "chunk_id": "7b3243b033340f46d9dc3376",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "968f97f5934de02194dc567c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-20-SCOPE.md",
      "chunk_id": "c9e6fea2c24bc3590489c83d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt4s.md",
      "chunk_id": "61f543ba02e258921b923884",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2ad53b6c537a997032cdee50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-146-CIT-P.md",
      "chunk_id": "528ed6a399748d619d7ecf27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "161e6457f1af8dcea089911b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "e4d4ceab7d1f825ac73f1648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ee2efb3e8fab831035253eda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b33e384436b5a97cba937c12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-1k7y.md",
      "chunk_id": "23e9bd7ee8ae8ca5b9345e4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "676a6f04c3c882eefafb6cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "97066c2c28c3ba7adbeefdac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "fb39695049fa9c61f5084138",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "36eb55155ea3cd0646d10226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1f867044e58ff2b56d8b9336",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "d1463a126b0510f09a529afb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "52e6bece0a3935872e5e266f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "87b1a9e1512e21f5d0175483",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "bc7da2eb8622930c39513289",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "06f6d6ab4260c95fb10a5aef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "3cd34942ac20aa8c750d763c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ba6ec487494f7e5749ebef00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "f59cf177e3f27866b03038fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "97525430e18c93bc4dda9e17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "b0b8e5db97e1be992ed8f301",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "6a0db77ff478efaf83c5f1e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b7da75d422fa0cd258206c8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "cc2c3b433b257cdf642c9141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "505cab33eacd407e76c6d5c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "4d3f30eb4feaa8ac2b1b16e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "c445c0ebbfa2de57c9905fa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "5ec3789985943aabed1b65b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "e0a1a03ed4820bf89a1cf4d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "0d2d584b9a88336af4cb0f8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "20657858255b8034ec0c035a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "9e46b4d04687666719e3bc1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "148ed5d13f7e5929447b2773",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "c2ff6d5cdd191664c3509a53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "f3555a6c00002e2b1c09b7dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a7786cfd2570f2545901340d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-xm6l.md",
      "chunk_id": "5ed0205354b45f96162ea83d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "65d96d4f86cf1d002f78437c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "99c627d17e16db30ee3e31f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c5dc7696e6e31f9298358e3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1626b0f0a6da56fd11f1ce7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e88f9402821671f145d027bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "5d8e6b700d825ec0a44625c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "a63bb965aeb4c88001668178",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "fe6f19c398d02245788c8c89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zkr9.md",
      "chunk_id": "fb22dfc405a55f1bbc55585b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5af782998e68b3fc26ba805f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f274e7bde7aaf36cb930bea7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-pinned-gov-review.md",
      "chunk_id": "3e8ffae11ae58e9a4061460f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-c1uz.md",
      "chunk_id": "99360a79090b0ef080775984",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "c11feda957501de1f672da40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "de3f3309c3c2e9d843ef5c3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "fe800f3a872609f2c8efed12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "050e97c130499320975e3c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f2b988b9082dfe99d92818de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "7aecd24c710eda7828982847",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "5828c9d78a2e5d086739ca50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "359e095bf5ec883a4d7beb61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3efa3b49868ec1c107f1ff25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b2c2d82f2ef922c5387def6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "8f0f63405abcc93fd217d8be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "352a11d2760cd82216ecd896",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "9f6213b4e2ac842d0513e552",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "7a7db801570b4e1a1563c739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3fe227e4122462afa604704f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "2dfc51487490ff038eeee301",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "3b3414ad3a9ee32628bb44ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "71bcd14c0bf0c10bb464e844",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-pinned-gov-review.md",
      "chunk_id": "5a300c5c60bc2974dd8db6cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A1-inventory.md",
      "chunk_id": "f5833823e9622ee774ba4880",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb15072ac692f119b49a0adf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c187aaf47690a6e0cdc3dad3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cb8e73493beeffbc6c27e3ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e3277006fe60229b798f614d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "4b5658bf8f39396db7a01d23",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7dc6ad4635f030ad6895387d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ec4fc97ea1c762200e3fa10c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb88d84ad3e86acb0052f491",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f1d4a7479972ab678e0f9ba4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "2662235bd4b4c6c6773e6329",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "dad4f8f5cba7557f30a85e8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3d4ea9c611fc767a2aadf535",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "0fcca519f3b4d2bee670bb3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "d23af48ff811e6cceb118f41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-11-01.md",
      "chunk_id": "e8c7e47ab71b08d65b0d4d60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ed9a22ecab26ac4f70f75b0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1188e2995060bfd298f1aa67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9f924b82f70788421d0c6099",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "870baeb9f8cc50f54e27a728",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "3c03f1fc4d583675d3a4eab2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "914182188f3cdc66859e4e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "183b1d186fb05909dbd0f730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "70f28e18c48f128e499a6f0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "9288a2318ddba4df7375b26d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "0dfef8df6411a39fcdf86629",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-av72.md",
      "chunk_id": "c9a776e0b1342fb25d1a2348",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "8271d4ae5a36e8233c0750b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "4968e7c58702c2d83268b5dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "b4d15fac657d6c58be6b50dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "5e848af1eb86be868b43c5c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "422f61961cacc8ffe7a45af0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "64736d65f8a266cda5466db1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "1ba8d4b9fb925b539f29393f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1cc8051ca3dc0ae4ee2a5a71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "a006663b524f339ec78280ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "eeb667c5b61b8ccc685a694a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "647fecb1ec4110b99eb98900",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "8548365b3bebefa6029f233f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "3a38041f429aff9b858da3fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "85670b732feb02c2b6372972",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "dc70d069f76f85a133aae886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "b793f5fc48e3cf41e3f52e51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-177-evidence.md",
      "chunk_id": "c01a2ad44033fcb11d0af3f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "228fef247583a516d63c64d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "9ee38c209b6829e4e342a3fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "b7b92b3287a1d81b25455aee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "3490e5e2ab5e3d61fe63e3bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "9ad6f0749af9601c6470d8be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "2cd7f700bf1a6234637b4cda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "df1bfb3a11affd6f038d538d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015b.md",
      "chunk_id": "28724c813e27514d15f1ce6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b49e1ee3f4a6655e93048d8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "662e110f6acc0ee86d3ca7c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "f92f0f56a30f96683d6ec6b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "921468ce0a8b8336b56b54ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "ca80330a515f3e60330c8c5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "13156b74e5dd7d5700f7b5a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "df58f2846d776bf033231599",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "b0b4fda5c997e6797b8fd9e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "66a4b7e68669d1285b7c8a65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "71ccde76a15fe19a15dbeae4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "2dbf5f610d2290e7c557d91d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "4970bb1231bc2cc1309d5c21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p8tv.md",
      "chunk_id": "5fee1be9cbc83308b1a80e92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "cd6446d16fd1b2333d450b05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-xm6l.md",
      "chunk_id": "40ebb31fdeb2dff9483ebf1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "1d4d4cdd15d39d7f2a191d24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "907a4424a56cdbd533071591",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wi46.md",
      "chunk_id": "c4842d539d2947bbb5b606d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "cbc87d442ca33a14eda2ac2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "fd5612c600c18a984c44444a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bf36d16aac0282c497694ed3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-m7u4.md",
      "chunk_id": "87c8d0dac9a2851482422ee6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "671c3e47e48e58c7bc7e32ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "6ce1cda789b771e120d7f803",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "5f0a36dda83ffbe9e5fd2129",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ec8f8c8bf3598f2815c5caa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-btcs.md",
      "chunk_id": "86ab17b3ec21a104c03f502c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "4ba5dc24992c3d5042431f0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "adb8e9c81b8f897e9ae3b455",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "668605857dd6300cd27f56f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ozyt.md",
      "chunk_id": "b10bc74ffa72320844f55549",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "95a8945b6ac7af7755815798",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "631b5a097957dfb682e0c1f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "8167ce22a4a25aceaf369e12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ab7209b865d3c39058f862f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "45ee7a3d8c68ac7ae4996c48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "dccff463b456677fd8bda90b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "4e74dd6bc4288585e7436889",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "299f42e0298327e5d4e39222",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zkr9.md",
      "chunk_id": "11a6af3e08a51b82e7b25dc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0e24401fa07469139b0c644a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "526c9566cf4844ba62fb57bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ff44ebfd2a5230ae1b356cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "d71ebcba53e764b43a15f2f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "1829ddfce73ead216e350916",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "067166abcf086c8659af32cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-m1u3.md",
      "chunk_id": "787d23c37f9c00562fe34f7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "79e1c8d61af65cefbe738950",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b53ac41676c2e0ea0cbc910b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "cc3bc6874911d0fdc48a302c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "f8a83cb6323f0d3727931989",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "67ed2545fe9057550830df9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "a99b8100d6b4dd370ad0159d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "51638cf1edb271ef32bc5618",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "a4e1dcea7e8a7e088a98a1f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "f4cf20fe17b7294f0c4d37a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "8e73c105edb126dd50e14dc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "52e33117b1393ce24e104f8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "5a7c9c7a5b7bd7cb48ea293a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zkr9.md",
      "chunk_id": "aa0d92f318e31dacb34d1115",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "c0b660884544ad9f7ab77063",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "030a5bcfdf29313cfbc95c09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/ci-a-dev-run7-job.json",
      "chunk_id": "dd37c0de7fc2c327bdb18b2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "51f0f506fadb12433cab9f14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c312d4e614de3fc9cd4982b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "f49b7a9d05eeb65c75a94b86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "719d28220f91dd296ba9bbcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "d60916f7fc02d059a8f4524b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "3567a5465ad3c444b85b6e41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "9fa8c016f588b8e63f62269f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "1dcce41ecd8621524bf80de2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "ddd799ce1d3756d259696e34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "0ef32c080b34b09e8022455e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-91-evidence.md",
      "chunk_id": "aef3fb4e865c35a5d1b9e92d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "663cf6353a512f39cbd45b3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-LB-PRODUCT-1.md",
      "chunk_id": "ba10c3da42a9f480263f4723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-REPIN-R1.md",
      "chunk_id": "f699accc0d47d216830232f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "3b5cc040be973cafaf057f88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "c9ab5d51e616613ebdb0d5f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "a41f1d95afa4f7ced510c28d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "042a798942b3986aa378d999",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "31b1dcbf4cf4ab9c0668cdce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "4c6de5b4de20455f808dac56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "59dc826185f1a3314bc86797",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-13-evidence.md",
      "chunk_id": "e1a13de52b6b34f90b57adb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "f0e98c6d188bf7f5e7d27945",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1b3e225e98fe2033a2cbc1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "8b3f599f576dbd9dbe98f3da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "7ef6007b1365c5c76c643db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "0fa603862a9728cb0ae813c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-c1uz.md",
      "chunk_id": "5ed0d4859b0e66ef4384583d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "98ea85a151026da98e21ae71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/ci-a-dev-job.json",
      "chunk_id": "7bcfe67e02304c4f852f7d32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "58bc864e973e4c68121d0028",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "5ebf48e300547a3cdc8ad7f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "de07f8c2e68307f75ed6e358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0a879ef2f0889bf390619d61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "f45e230450b8d85f418f75b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "92a6f0000fbf5d629fea784d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "3802347e296f63835f208a26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "fdd1072c7bfbde9b1de1a55a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "90cebd812ea278ebb0727d68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "5123898331d7b65c99855bc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "80ac4d72688e4c0150377eba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "68ee8d497bd1f28eae53b85d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "96ae0ec42fb8d1523928f826",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "b26080a06a80c858efd51702",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "b63c5eaea2f0433cda51857d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "24386013743bb9c5630c23db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "df5a1a8b40a5bb6a475aa24b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "dc6b9cd110d806ccea26cae7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "78ff3fbcaafdfae72dd614dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "62a192389e4c54f839a1fd74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "444e14aac8c9e77d68f67d11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "6c32cc590cf870d46235d17d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "06d7941ca68a796977790f4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "34aeea3a76804d4f05330718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "5104a45bc215058cae5d8dc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "a196e6246e570d43975060d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "1410eb2ea097c31a1ec12770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "79b9a2d0e024f01adfacebee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "182344872a9d653f96996bf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "4d51eae1864cd1de3d56a4e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5b4bb7aa6b522187a3b4bc0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "0506fd6015268c22e55ad79f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "9cd5a99efeb5c1c87f001dab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "bec2cfe3fe43bcbfff7eac30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "a934d91976394e4e289358fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "8dfcbf3b38e137781ce72eb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-LB-PRODUCT-1.md",
      "chunk_id": "b037cc4e17347321c46bf1ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "11d508ead76b9ca37c64f183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "65f798fe2f70571c0bdb77f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "2c944aeb29e2bc37feb2914a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ylsh.md",
      "chunk_id": "3eb32217d77c602d7210e201",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "4cc77c9ce3ec787b8e18df22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "8081fed211df13faa93e3465",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "acba2bec7cac6cbe8a8f4532",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zkr9.md",
      "chunk_id": "e55c4d7f70d0f2178be3b18b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "779c85ff6d94aa5dcccc5581",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zkr9.md",
      "chunk_id": "c5a219cec6c7d5e0afbfd2ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "1e2b8770de8ad4fdd9785a9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "031ed8e793d1d11c228d190b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "4f0ee711fa9362e16d130010",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c5d5be3aa45ae322c1448713",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5b88567b391f7dcf2785667d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f00b7dacf0f2586714a3b28f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "2bcda0ecfc63b282924f8ad1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c331f3d0202267ad827f53bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f54829ddaa9f2453f1b28165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "c583704a2427a44095534f08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "09ad821a54bd6b14b7471534",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "116a9bd92e2127aa8789eecf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-LB-PRODUCT-1.md",
      "chunk_id": "ca4ba938cf10a9cd07b1de66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "67461ac2db571d2708e9ac4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "e6dabeb733cee020e0b5070d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c2-ticket-lines.md",
      "chunk_id": "b419c851e8011821d44c294e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "d576c988c3e10c3b9bf68285",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-pinned-gov-review.md",
      "chunk_id": "e9cb53b9dec0f694e02ee653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "0ebae3f3b440bbd4c724d2b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "e279957fe59478c27a4ac1f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "6148edd54f427207645e1097",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "74e2e2ce43bc62aedbab786c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "ea8f2bb301b304840e6f78d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "e3041d9aa07ce40f496415cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "07a198d0cfab2a6b7b9cbbc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "5b878be84d4e836dd098ef7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "36a86ac0b53a41bcdff13796",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "717d35471d57c15e6e60242c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "2e3fcb948f0bc95797d8de7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "fde0b97b2b6c45df23b513e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/__init__.py",
      "chunk_id": "83a0de7a3d44e5c207b86b18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "08ac0f519699d539965b9fd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-157-evidence.md",
      "chunk_id": "e858b740dc31767c9c0661e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "4512cf1352b45b0d0d7360bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "ebfa652825450cbc39df982e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0668c5aadeeab0fd0baad35a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "b1014c65a3a0d993d651ce8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "fca7c92989eb3528399a4fce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "ff1f559ab60fd2b85bbaea13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-pinned-gov-review.md",
      "chunk_id": "8e489f91f45d21c4bbf443d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "22dca2536c4cff4888b3ec96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "6800f09cc13e9a1da1870798",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/EMG-gitleaks/PR-EMG-gitleaks.md",
      "chunk_id": "b49bf17c10a3d8356dfea040",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "112ccb10a118b4fcc380fe31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "7b5299ff5a8008f14c796465",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/ollama.py",
      "chunk_id": "fa6292f76a338350481ceba2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "42254225f9e398b0acf262e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/EMG-gitleaks/PR-EMG-gitleaks.md",
      "chunk_id": "ed152d1122ecdc5408637940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "82e3965245f9e38944a7bc36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "8e20f47f8396855d35e5a9f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "04d9a4de12b3697b7e44ad74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "8694b2ba986f1f9594b478ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-157-evidence.md",
      "chunk_id": "6be91ff89543ea344b363134",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "d702b1fe029e5bd1f68ed74b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-136-evidence.md",
      "chunk_id": "cfdfa3b76565ea3b66037a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c3ed2f075e63c31d29b55d72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d9fff3e35fdaa4673e82d71b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-validator-review.md",
      "chunk_id": "9214bec559fd80dee0d4a974",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ba844e139ae3b0899aaa7766",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "80348d1aba91d873e318c9f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-pinned-gov-review.md",
      "chunk_id": "f4348a7ed81d115c5a38538b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "ded9f875c570080871550dd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "92bb6a84c698bc61f2bca122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "04b46fdfeac4470512d9d702",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "12648407f5640a9717e26c29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-136.md",
      "chunk_id": "af8f54caab688742bdb0b64b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "05ceb14034527a257f527b64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "69e01534f2820bc701109ebb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-11-02.md",
      "chunk_id": "1e857a7ec2f8667cffddee70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "00e7f6b620492514f89f7eae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "a85112dc86560065e72d6b33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "c398a4946428979954e76cf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "fd5c4d2588bced3c75104e00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0020.md",
      "chunk_id": "ef892a3c6c1a57a897d70718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "fcb47518ede66875b0aa00ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "27b4f348da6fb087496df454",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "1a19be4a38fee2c00eb1bd11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "794ed95f9018cd9b6ae89959",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "68653b12a98a1aedfd8402e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d2f7e25f02a779ae2ecf5fb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "608d1424d82f563e0b365a93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d44690742fd24dfb39e5870c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c09e438935b088a3250cb3cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "66e882040ca5f7b2fe80aa2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "2468e7b1901af99c5c345c5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "45485f969662ed32b4363667",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "f295db74491cfb29565d7609",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "3fc5a80e20283687f07aa5aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d31243234d1ce38230e850f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "44353283aa9df06039349b9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "9f54fdcb47685c1f7a122dc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "64d33df321956655dbbe3dd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "4789c60670f815e847ffe236",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f72583b4da4f3249d6d93cc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "9f9c90f3e32f9d5d44798b60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "b7ce8d7b12f8b9649325933e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "dd91a0dda8bfa202762b0b01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/gates.py",
      "chunk_id": "e4ac09509b960d72980d5289",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "bd2d2909a71a00e0b911c468",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-2.md",
      "chunk_id": "fce1fa54ca489682a37b12c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-157-evidence.md",
      "chunk_id": "62a79174ce8e8c371ef3d5ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "03ad569aad0a2ce8dbc2fbcf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/rebuild/watch.py",
      "chunk_id": "378aa370d4b2e53e66dd5681",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "be14ed36b68117c528dad933",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "25be2b656f9b9b6cfb6ffd92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "2aa1dea8f97b890b22ab7608",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a60734bd4ee0b9da5f52b4e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "7decb6d47bf6f74efc6a4fc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "5c1604e1a1e786985c839d83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "4b0aa6d25da30f0a8cdea543",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "74ed762007e026236ad8d6cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "a2f9b439b6524be6257be487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "9807e34458dd6adad6a7970c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "cffdcb8ad0aecde55ffac9da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-2.md",
      "chunk_id": "1b1ede4c1716a5971ca63b68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "bae2fec274654ad81775a47a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "9ed83205ce5275ecadfbbd17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "928feb1e9924a4cb4c1646d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "a3df49dba3de2276abb0ab02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "d421c003e9295ac317159fde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-fd0p.md",
      "chunk_id": "d50b800eb6116e3c0c94e88e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "a30b0c799d3e957f0aff54bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/ollama.py",
      "chunk_id": "5ba21e4ba9c94c0fbff8c418",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "958cad15bf167a9346963b0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "98a51a774d4fa94ac8a95129",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-3.md",
      "chunk_id": "fcdb12d07a0785ef1b71b95c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "2d52c1ddc6022942442c9c0b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "cdab34041e630577c7616648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9cef25c1df273f34627c885d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "372427ccdae6720cc1d751df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0020.md",
      "chunk_id": "2de2bd29057e461b8c244c6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "ecd034456b2594f4487bdb85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "c8e7fd4808d288f0296bd027",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "48e5e85bfe97b1600d520f5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "8c6c9a799bc70be262c3bb9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "805dfd469a363d125e94324a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "4f1e0739e073003131c8f9ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "21d6781d54d3a07a5ceb731f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "72134732a6b722ef07c9045f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/plan_check.py",
      "chunk_id": "129299ae1a37a42a164c0c66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "8013ad87fc4fe094d43ff70f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md",
      "chunk_id": "59a6880f214a555e80271247",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "a115f975a4d1d6157664bd67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "4872b4d162689ab6618eaf30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "60a35c5dff985d3cb1ff34fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "bb4205ddeeed407e41a898b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "348bd53a429ab93423659b3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "59b1f6e56c88534005b6c0ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "52596f32d8c4af948561d4af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/ollama.py",
      "chunk_id": "ab698bcd606e8a8341c0cfea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/conftest.py",
      "chunk_id": "b2cbb0c001e01b3b7ec317b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "e5f473cf198c449ae657348c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "b24987ad7b6f12093a51b024",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "772c2aa6926d35fa55462847",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1af2083b037014b21113108a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "69954c2cd226d8172cb59796",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "53af18ae97fc724dc8089ee5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "1e01cf1d4e795d01ba5c37d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "fe22966cf6b7e6579271caa5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-123-evidence.md",
      "chunk_id": "ebffefed22459812d43cbed2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "d6fc6becd1cd5bbe452e9c6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4ed757d8c34cd7600fa93a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "7fec1e7ddb14d8c1ccf336f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "b63ed848a277184cb756b9ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-6.md",
      "chunk_id": "72dc3e78827669d0a515ff16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "d7fd255d2da32c5c3b6ea27b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a51be09291456a3bef25fa2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "92e8c1f3b78f6afb94d7ef5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "652d5ce0e7dbb8f6c49555cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "8177929a574d7a58bc4c3565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c5ed6355da527d619c92358c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "61ad3ed031d18642e12cf2e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "2676fc8c96824d255dadc7dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "91ff34d31c7ddc893356f04f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "120965e2e3871cf02d462c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B1.md",
      "chunk_id": "320db27819cc8a2866ddabc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "7ba89be48122c39a9116f6eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "536ec010d76415d5536eb8b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "3176e1e3eeec99aaeed9c272",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "946d2bec7f8b64d80d1fa9c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "3f595c1b284c36096a6d7467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md",
      "chunk_id": "0e62a7867a03f23756ee2ffe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "08a3ebb612b4d09b647ab4dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "90f1a774e4b21560048b9474",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "01b467523442b9593ad53e1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "de37261ba9037c8edf91f2db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "a3e6784037224661ec913450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "43bca8fe963a0d611d8cafe5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "6e5468e9bc4cacbec8b853e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/README.md",
      "chunk_id": "a8c5c1a7fcc10f8dc965dcee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c3aaa61f7776e4ce714a2119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-136-DAEO-p3ln.md",
      "chunk_id": "8958cbe36b7465aab186c4f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "be5833fac81e127b7b1bc155",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "ed525d0f8a008559470e8b91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "0c39ee51f8f1f4db9f51f48a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "ee81e6c9d5bbacfae0ce55e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e608524b27ddc494baa85928",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-56-CIT-E.md",
      "chunk_id": "16471fd77bb80b9ce5e50eaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "3e95b4c7a10305ea46765f4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "73a95f1dce08ef7fb1a1d67b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "9969d3a9975c4f91181c0781",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "17d717d420c0947e5d9f7ce4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "021e73ac037bd924531b50d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "0e964cb3072dc06454c5bb5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "cf9a164b32060ab8c247e49e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "43001e10821c3f2db4be6de3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "2076a09c07a5472c0d698707",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "836cd36f536ed00ab97490e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "10402015239ea38d94df25fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/REVIEW.md",
      "chunk_id": "39ade266012d53c2e8cc8da6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "b476655dfc7fbc948d17b03b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "5ce68b1bb6c0aed589951653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "736ad76343ccf62d7ba137e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "0c107f639537d6b30418f28c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "f6f3dc0d26910ccdb0421dcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md",
      "chunk_id": "d8f9238640bfa804b377c1b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "da7b8c5f0e135fa3fd3484d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "575bcb12c36720380212dbe0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "268b27edbc2097e467ef63e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "ef17b9d6ca22980578bb0927",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "45ddd0f6c1ddd72766392658",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "d43c66d529d2fe217e3c48c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "chunk_id": "a913767ccb74f44a3b0b79d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "46b9cca803a8c216cec209f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c2-ticket-lines.md",
      "chunk_id": "66a0809d09fba05851f6d94b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "c7ab02b8c7a4f9cd38703130",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "3a324e486f03a7f12d90ceae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "48d69699b6e029d3a776c314",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "54e84cbec31e590c2918f171",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "4d0eae4ec2e42ff509d1d009",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cv58.md",
      "chunk_id": "e0492c8d720246f2fff7642b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_3_PARKING.md",
      "chunk_id": "f3fb09b628a6e907d88e913b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "65b78649eda839ebeba8f2d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "79d585e6a7634c3c2c0dcafa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "chunk_id": "81d4ff11d06e6eb2508a5423",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-30.md",
      "chunk_id": "4dd626a713fccaa1944acba1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "96ac377f925ab9c9e9417fba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "868e890ee2e86be828d4d6b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/ARCHIVE-SUPERSEDED.md",
      "chunk_id": "d4c0fbdbadc4650f95f00ccd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "4697c73b9ce34784287dd426",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "098819999ea12f134ed8c455",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/nightly/disk_gate.sh",
      "chunk_id": "18fbcc933d300c4782ca1c6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "3f835381a513334cb2729f6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-2.md",
      "chunk_id": "831d8db914be0474d6129fe3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/ollama.py",
      "chunk_id": "d4cde04288a2831d10a23cea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "17952bcbb725d595a98d5096",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-136.md",
      "chunk_id": "3f6419493bea4f5dfa1f8771",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_config.py",
      "chunk_id": "96683a54ed7d294af8ef6f0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "2434bb0bb40c69f749828eb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "c14ae83a59beeaa850f734f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "8384cbc6d321156c979f3bb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "ffab226d2a306a588606403c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "13f93de08f8e1df9e757756a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-136.md",
      "chunk_id": "c156c0915b1851cb19a82520",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ifgf.md",
      "chunk_id": "cfaa60c7ee77ac87d720fa15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1b4ed3cccb3514bbb4d5c283",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt2s.md",
      "chunk_id": "cc4a3b70fde95b5a42e4fa1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-123-DAEO-qzrq.md",
      "chunk_id": "97326ccdd35b55c11a833099",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8459f2cf0ffc1de2831fc4a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "2184a32ce5ce31e2f796c94c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "8fe1d5b87fea6015941fa6e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "47c1c68d20d36286232182a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "34027a3534e14779d44aaa5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "73a646690a75c62399223655",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bf2abb005636a5afc686e93c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e3666c791f35caeafb47490c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "970f254deb040eb4056d95eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "4e598dff34f6f08af4fbef42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "65ad7e8ce36e8809c36b819b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ifgf.md",
      "chunk_id": "554f3f9a912404a4865c2d2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "cb3c9544d48c7070cabf9ccf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/ollama.py",
      "chunk_id": "5ea65c3e8ace479e780eb70e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "197c213909e7a67669a2730c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "0e7fb4dfb8b4f43dbf47ca0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "eaa0adfabb62448d963b67b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "f17b9653404570944e7b986e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "df3993c3e2841ad1e6f1d352",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "320db0ca38365e2e330681a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5f9b5ae1e583342b1f86e0ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6eaa31daf9764b265b5df581",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-30.md",
      "chunk_id": "75b3353f981b78df687ac719",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-3.md",
      "chunk_id": "cc23e97e6bb1cd0d7d2fbb7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-136.md",
      "chunk_id": "8da5750d0094385d83b9532c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ed1e43871fc8a86ec5ba0108",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f33a247c78f0f90cdb8057e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "6d43f3a0f2fd18550facebd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "25f1e79bb50d77b44c944d33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_3_PARKING.md",
      "chunk_id": "5e7a61be7d35c579fe80c075",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "fa68f2ff9059451d2e4ae774",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/w1_07_support.py",
      "chunk_id": "ba0394c2af18bb3eae4312ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6553389b6397a6fb089377fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "d85ca0b9bbd87494651f42cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "4e03847e24e54f282b44a395",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "c5a42636dbc3e91038b1538f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "5e95fb34671694533ecacd32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "67bc2bd6acb48777e26e0412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "582cf12d1c90e1e497f77cdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/command.py",
      "chunk_id": "7ddb588616bf3bc91ca74bc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "93a99a937c3c8fa2c4ffb7e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "69d4bd2aa3173afbc2ba9ba7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "chunk_id": "a56cb7524607e4c6a2ebd2b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "8d36b8a5dfa4a48facec3f5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "9a27e738033747caa88b98b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "87451faa62b5836f7cec6dd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "630df801022885cd686c79b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "cb704885dad149f800cee1bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/03-run-time-tool.md",
      "chunk_id": "bde530902ed7b51539770ef5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/registry.py",
      "chunk_id": "ce34ede2880fb16780eaa439",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_plan_source.py",
      "chunk_id": "1e4a7fc600b08242337204b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "41fbe407f13bacf5a62d04bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ba24528da4b2f9d4dd537f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "239d4da0236811fa33345311",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "90cbf44a248eb4629b8f5c5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "76e9f0ed52cd4c56c5e6a1f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "c45c2d4d3fc0c947ac296809",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/rebuild/watch.py",
      "chunk_id": "29800d81381502fc133a7193",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6a1c25e365371b4377ba9b5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "ddfcf50278251c58761e4ea7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "b0015912f27c02681ae7464c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "c1b6db2e93a77d0beaa7e312",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "2fc9b4afcf6411414cf24887",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-116/README.md",
      "chunk_id": "099de20facfeaa4ca8e1c059",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-56-CIT-E.md",
      "chunk_id": "b65cc60f7e19a78feda75dcf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-129-links.md",
      "chunk_id": "4713c1c80f4eac702a036c35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "b93ee407ba7273d3e7ece9f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "54b4dd388142971af7539bb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "521e5b17b4d0028f7203b897",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "ec7d4fd26a1e3478ecfde779",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "13c3480914f494ed504e6de4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "b31c24f95ac779bc334510f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "c015f3617d8a0b113a0aa16e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6lid.md",
      "chunk_id": "13754bd6ac725aac50fafb2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-46/README.md",
      "chunk_id": "9125687dbde03577dd7868e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-fd0p.md",
      "chunk_id": "a4fe2eaf16eea2fefe9aafbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4da454f224cc3e854fd15cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "5cc3e6acc13fdc14539340ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "b6283853b4ab7d7011fc4e09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "e3124b68fd42c768b2f60b3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f695793c5fe690683238af68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60b-CIT-E.md",
      "chunk_id": "926d914c89aed647943e8ead",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e11dc1aea84c7137a6c9078d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "ffe92c6a2d9bf557ecb61a38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-129-DAEO-q7lk.md",
      "chunk_id": "3a57aa8cfb10b2af02ae8aa5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "db78d71e9ab3331dd8ed8472",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_query_start.py",
      "chunk_id": "afcb2cccced74957b8e5e735",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "06a46e45ab71a95f27faced4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "69cb7c67a328ca18749d0df9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "6f399091a2ae524a972ee95d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1/resources_sample_day_v2.sh",
      "chunk_id": "429eeef775ca3343b733caa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "9907b12e982cb4840cf3143c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "31bfc11ae4c9127a7adc5331",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "8b51e971a543f9cd223496a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "698921bde1f53a0a8aa246a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ouet.md",
      "chunk_id": "d204a9a56548402f3f018588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "0b607b448a7429e62a70868b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "324e7ddf39ab771046bc874a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "27808e5f8cca7606583e025e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "9eb9df3cb7d53f8ece9c96ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "4ded4222a0fb6849728dee5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "92441992cf0ff58436c35ffc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "chunk_id": "2808533d411a951d767d749b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "c615eefaec7a3b5e110a69b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "chunk_id": "4df22e38c50062142068aa95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "4b3ae1cf12d3cab0eb67f565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "5e5825491552a3dd0e7df849",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "95cf81eeec34e0b336d5b9ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-50/README.md",
      "chunk_id": "a6ad98a555ad1fe55a927890",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "d9f944b061645940549b61de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "4d227cf9128db20d39c1bdda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "chunk_id": "c0eb2180a1232844e7589dc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "bc7c372aa3afaf30dbebb014",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "036642e6178ab6f047837d6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "c9dffe008fd39069b873ad15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "bb44a5b0a5bb338b68e0d461",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "596705c629a86624a58fafd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "e561c056f4a243166449ef17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "b5a012108e6da0fd183105cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "937684807ec6666e1615bec3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-2.md",
      "chunk_id": "0b49e8e1a52b0e302a16e240",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "ee0fa7abc9a24be4a3593c07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "2ace7ec468940311791213a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "56a2d4bb15fb1c7c38a0786f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "0ff300b4cbad96fae1c78a0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "305939e29c60dcddb9b1cc45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md",
      "chunk_id": "a42deaceda362e9fd06f8898",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "059b77f91718ef09315a4856",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "1d4401a49b7e98a1643dc907",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r9ss.md",
      "chunk_id": "29327f7c850988166f4855e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-38/README.md",
      "chunk_id": "dc742d6388936862c4c32af0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "db50a50671b6f0f6e6d26d8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "97f32a0a83479b38e7c910bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "chunk_id": "b0cbd4dc882425a30fb252e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "196df008c32c7a3c5caa3a07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "4a408f02c6b3aae220406697",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "91726b89d726d741c54773ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "ee59253c3c0e18374ce560e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e4997d2367d766cf3bf8f439",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "19b85b1e7db4dbbe9ca26289",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "d3c8bfedaa57b28696a7ee52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "082a343dcdf9f5e1287d3abf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "62afa357bc35376387ecf428",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "0e824d6b66da5e009fb7bbf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "ff456a9438815af0a4660182",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "850866904ebff5ecded37dbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "ff8b366cdbe1d455663c68cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "d8f0979ed4b5295ad5f714b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "8595319e5507595c48040dee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-tickets-and-rubric.md",
      "chunk_id": "801e15488bfb9458cf154cae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "761a04c98833861d59dbafcb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "8a4d7ebae5d3b361f0a30a17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "654a7870b27fc1b0d8d64a3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "c39a85a09994f1e8931b6665",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "76c79d49dbe408a25b3fe93d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-56-CIT-E.md",
      "chunk_id": "3867bd37db243361c224dcdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1f08e026b29cd33c0a80ef76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "d7640ca8f66b2398b82abd49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "8f1781346bbd381856c85325",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "8d1c995ae94ff9078ce8fd77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "83dbb8329a6cc49d9e9bbac5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/USAGE-1.md",
      "chunk_id": "62ed762a1db6b51de1d771bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "8af7f24629f1ae5c38e623e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "fb8b825bb205ed5eb2877b36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "95093da5e3566d05538dc1fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "c6fb7154f141f70684737571",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "987cdc32e0b0437d5136e227",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-46/README.md",
      "chunk_id": "0c54eb6163c4034d5e80921a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/K7-W2-REMAINDER.md",
      "chunk_id": "bd2d36dea2804cdbd99462f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "5e71812753a2e27a0c282530",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "e67b163860a2db990d919ad2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/USAGE-1.md",
      "chunk_id": "705d78bda628075498fc3229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "9ccf5aa59a1ebce20fcdfa38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "1b5ab7a68648cfe3d25e0378",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "chunk_id": "669c5b6ab008f3dea49a57ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "765d6aa41d20e3d5aa152cdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "69b336874416f19aa617cb8c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "035e1ad5cae4fa75cb702c64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "de28f0cc65d0298af4680f46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "87cf181f22ae2e40b8f86548",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0c14054ea0f5db3a9b740ff8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "dcb4d59eda8781386c264887",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "b38b09d1a91d3e1ba668bc2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "94762fb4ab17cc7d9d8966ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "d6f7bff6572f8e54ddfd68b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "20ed33978f873c059d1c4b6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "09a47c5c9538744d8347e1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md",
      "chunk_id": "da0a0ccc64ce34b2710b9d83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "5d2ff612d7e4731cf67bcafc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-GROWTH-1.md",
      "chunk_id": "73c9964e4da48b329b378d07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "6303915a81e6ff1c9a879458",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RUNTIME.md",
      "chunk_id": "fd195001d2eb0cb3bff13669",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "92d61ca1b78f8685c70290c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "dcf884aac40eabd85aa71eea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/CHANGES.md",
      "chunk_id": "54e5362a47ca2e70c16a80b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "d6b9fe8e3a22333b5b6e5654",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-184-CIT-E.md",
      "chunk_id": "36cf0b56c0bf6f5fef8f55c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md",
      "chunk_id": "f12a11addf5304a90c39b8da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-3.md",
      "chunk_id": "d95f1ccbd6891b36bece2e44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "a840b32cda3bd7811d65a1a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-GROWTH-1.md",
      "chunk_id": "0d0876228eb1bf60dd8703a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "6abb0bf7c302ee4cd9c5545f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cy5o.md",
      "chunk_id": "83a7dd63dda89884f774053e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/HOLDS-REVIEW-1.md",
      "chunk_id": "3bb9f17537099d343c5ced67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "b2f3d073279a826cc1945182",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "4e378ced7f8a9eccffe92273",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/README.md",
      "chunk_id": "00e40679042323f7aa402c81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "73a5381ef5b5791018a12a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "ff4992e60f517495e42e7db0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "2d697d1689bfa28b7d04e878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "c003cf76e1178e2d54021beb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "582d615fdd8885da0c1de7ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "1c647bdb9b860f90cce187c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "c93419269caeaf4fc400f512",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "dd86a4b134a8edad43c48715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "5d33a2ef5d839567014ecd87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "21c970c51d469c3ff07b661a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "496cc7b3813e571c3d30d509",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "009ec972f1fcc93a6adb0841",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-W2-60a-P5.md",
      "chunk_id": "99114e1c0f8564e69b517ee0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "79fcea01f024316a38d199cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "c01ff90283703918140f0393",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "4784da605749592dcd087ff3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/README.md",
      "chunk_id": "cfd51506f12322d4585269d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "1b4ccc161225f7ebf71f66f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "2f851f52ccea9cc566282aed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "a5cc0d7274628dd8acd6e932",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "cc012ddf342c1708856dba42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "72dcc0c0c6c7036a896f36f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "a4b820ccc0cf6ee10d044730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-157-evidence.md",
      "chunk_id": "d6f917c3caa89f476bd66d7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "61e6e3da09866c0119641562",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e73d5397997feed8123789a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/doctor/command.py",
      "chunk_id": "7e9be136dda795cd8eff1032",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "fc0e7e7119c0238767bed804",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/tool-registry.yaml",
      "chunk_id": "9f2d340281674d60c6564fec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "22e2980d61d9b8c3f056a6c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "22e82412993cbaf789fd8780",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-50/README.md",
      "chunk_id": "e1cdfbe1646d3e024db7c928",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/tool-registry.yaml",
      "chunk_id": "30b4baa3f6fed947cca33926",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "4995d6572a5d988325f7e375",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "47606a89291e2fc59e91b619",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-9-impact-landing.md",
      "chunk_id": "b1a0e2e492adb8b9043585ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "a311b6de85d30b81a51490ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "94e8a01b22c8a5dd84d03aee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "641e2b68370dd2f85479b288",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "3d812da58cfbd6e037f68b7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "595d32d4de372e57f8466daa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-blwa.md",
      "chunk_id": "7f4b6c6c58033512d7a586e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "4c6deac548db9b3fa46f2624",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "27206e5b98f4372ef6afe3c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "62b823599d3030d43b5e812e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "61f0bac8c8d057568ef06831",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "17360fda4736cfd11a6d3482",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "57b1f8f7d3dde64b5effcdf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "4d5c43169dc00144726d4623",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "047823bd3bfb50d5abf69595",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "78e18dccf372bb741d2ae893",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "8285d794cadd7aa7bc130d2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "1d09fa99e0aec08125cc1e35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "c77db8dd8ca9c365fec49bad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "1c87d3aebda9019d3446194a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "ca24e20a1e2751f989a2736d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "42e80ceb79a3cd97e7e8ea17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-33-review.md",
      "chunk_id": "c134075321816d866bef0d57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "6be1815e4ac98f39d7990214",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-54/README.md",
      "chunk_id": "2051a24a3bdb5e5f46c10eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "525aa4af81e3fd82182dd884",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-116/README.md",
      "chunk_id": "eb59be1f7e327ce787aed849",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/README.md",
      "chunk_id": "e64ff506e74ee16b7ec82bd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "7a5c4eed8b706843274e7601",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_plan_source.py",
      "chunk_id": "6f397244b73dc021e50d0559",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_command_set.py",
      "chunk_id": "748dd550830e512eb399677f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_plan_source.py",
      "chunk_id": "ab218c904d603f26e3a90eaf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/README.md",
      "chunk_id": "ed4dc6fcf873256aeb4f632b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/README.md",
      "chunk_id": "a288fa37a0e5e91165996044",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-50/README.md",
      "chunk_id": "461950ee7d5d3082bd31fc8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_plan_source.py",
      "chunk_id": "772531892b67d16fe3c00984",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/w2_20_support.py",
      "chunk_id": "f06facf94d820117a71bc775",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "c944d52c088755c0a72a6ee7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/README.md",
      "chunk_id": "47cb8784170c4d0876e4320e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-28/README.md",
      "chunk_id": "6b8c42e4ac0f67e178125e98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_plan_source.py",
      "chunk_id": "17aaf07613aab4dcf443d6d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_pools.py",
      "chunk_id": "bf7a130e13a0be325a63c299",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-60a/README.md",
      "chunk_id": "d4d3506968f0c48f68b8e7f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/w2_56_support.py",
      "chunk_id": "7968c80807ea475033678e22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_measured.py",
      "chunk_id": "3092246ce09b66ab2784d836",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/test_w1_26_recorded_commands.py",
      "chunk_id": "da8dfbe7a1e8f2e9b223742b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-60a/w2_60a_support.py",
      "chunk_id": "5d2dde862cf58b316e2216bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "2549f4f3e70c64fc202e5853",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "c7972993dab5f2b5293d6a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-157/README.md",
      "chunk_id": "f402be62f0f0c85a7163e862",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-33/w1_33_support.py",
      "chunk_id": "b6c235dae18efed36590189a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-33/README.md",
      "chunk_id": "d3e365b2412f164ea553ff9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "1f172b5a5f3c1cc24a62f19c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/test_w2_136_launch_check.py",
      "chunk_id": "f99d6a64358b2f72adf0159d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/README.md",
      "chunk_id": "60b5e3ffbc5335f387e22a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-50/w2_50_support.py",
      "chunk_id": "e2f5780e38f5e1b8b1299b16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-116/w2_116_support.py",
      "chunk_id": "9a97f2c1fcaf070bef920662",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "0fa4cbb15f4ba73bfb4fd935",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-33/w1_33_support.py",
      "chunk_id": "395f97fb9df3964e3fdca3fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-46/w1_46_support.py",
      "chunk_id": "5fb0634cafd31e5fe5f1b1d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "3f200ca244a981d70cabb892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "chunk_id": "c281548800a1d695680ec772",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_157_backstop.py",
      "chunk_id": "8f6a03da82e9f4ec3662e92c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "8cefd711bf885fc51a28d088",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_157_backstop.py",
      "chunk_id": "6332ca06ab3f26ccfb312ebd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-33/conftest.py",
      "chunk_id": "1e3df5d0b0c12781b3d5c1b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/rebuild/test_w2_20_tree_lock.py",
      "chunk_id": "3d63bc75dae2c76382fc5413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/test_w2_136_launch_check.py",
      "chunk_id": "b3061f4c1b745fc1271b44bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/rebuild/test_w2_76_lock_override.py",
      "chunk_id": "7ced4302b54f3a1da13076d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/secrets_check/test_w2_20_pools.py",
      "chunk_id": "42cc02a6f72e52aa59d41004",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "9907041dbd5bb7c5f2a07084",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-50/w2_50_support.py",
      "chunk_id": "bee3638f23b2efeb9e639f12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-clon/PR-DAEO-clon.md",
      "chunk_id": "7d06bdef8a83557c602d6deb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-123/w2_123_support.py",
      "chunk_id": "df146618d8f8342e7133e192",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/rebuild/test_w2_76_watch.py",
      "chunk_id": "07b3498749768fcacd527313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/README.md",
      "chunk_id": "abc28fc8ddfbc1ade0aadadb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_launch.py",
      "chunk_id": "413d76d07ceb13bc739502a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/w1_07_support.py",
      "chunk_id": "9278afc330891f9f0a8611dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r7.md",
      "chunk_id": "6cc3043b617cca29cf487945",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121/README.md",
      "chunk_id": "8a8d2ff3d890df1759eb9d56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-46/README.md",
      "chunk_id": "97e6a0593b53d58bc576f122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-2bdu/PR-DAEO-2bdu-s27w.md",
      "chunk_id": "982819d2987781e23d4c69cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_gate.py",
      "chunk_id": "7f7e9b7acfde2c3f0ed74e49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121/w2_121_support.py",
      "chunk_id": "ee1571443a25e4ce7b2813f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "584cc5fe1f7b8bb5e380a658",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-26/test_w1_26_recorded_commands.py",
      "chunk_id": "e59edfac9900ead11244f8f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-156/test_w2_156_s3_launch.py",
      "chunk_id": "95bf37db4b64aa0f8a84938e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-123/README.md",
      "chunk_id": "9a16442a3734928dcd96afaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_round3.py",
      "chunk_id": "bcfb5dff4c5c5696ce7e2394",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-05/README.md",
      "chunk_id": "800ea19cd54a1840f479384d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_launch.py",
      "chunk_id": "eeaddedcfc6544259368219d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121/test_s2_start_rules.py",
      "chunk_id": "b3e422c888e7703065e2f977",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/plan/test_validate_w2.py",
      "chunk_id": "6e0eadeb1a4a449c32dea9cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121c/w2_121c_support.py",
      "chunk_id": "aa5a1cdc6236e57d4db78d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-16/README.md",
      "chunk_id": "9f8909d2fce3652798ceaa61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-123/README.md",
      "chunk_id": "d088d32b33da3c83827ef292",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_runs.py",
      "chunk_id": "bdba1b81854ff0c63dcf57eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_136_plan_check.py",
      "chunk_id": "2862ad951f47a5346a74f32f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_184_r_fixes.py",
      "chunk_id": "516d4d345c1cbeb8f4011c3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w1_28.py",
      "chunk_id": "d7d68bd04a68773863176df5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w1_32.py",
      "chunk_id": "ee6c9733986617df23151ee9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_added_cases.py",
      "chunk_id": "d550b3542aab0b68bb952d91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/README.md",
      "chunk_id": "a32320ffcd928d4219ccd079",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_round3.py",
      "chunk_id": "6790ef8b84992533d46e54f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-123/w2_123_support.py",
      "chunk_id": "7554a3ea5372602a1facb84d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-116/w2_116_support.py",
      "chunk_id": "f77f32627a8059399ca0bbf2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-157/w2_157_support.py",
      "chunk_id": "67ddaa47514e3140075d8a2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121b/test_b_s4_heavy_steps.py",
      "chunk_id": "627b84d589c413a60ecb6d04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-38/test_w1_38_test_folder_rule.py",
      "chunk_id": "fc89905d81714512c1b3289e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-2bdu/PR-DAEO-2bdu-s27w.md",
      "chunk_id": "3c879db989082787c3efbbc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/test_w2_56_r5_lead_store.py",
      "chunk_id": "1c5ea3eeac38ac1c7eedfb9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/w1_32_launch_support.py",
      "chunk_id": "353b327c738c5d72513f71be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-28/w1_28_launch_support.py",
      "chunk_id": "16dad6908889582c4e3628de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/conftest.py",
      "chunk_id": "71fedec5f9838085f67fe118",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-16/README.md",
      "chunk_id": "b421f835a165f2017d4f422c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_query_start.py",
      "chunk_id": "758a6b670499eccd0eda3bb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_command_set.py",
      "chunk_id": "fd85b8b85242c84ef69b2ae3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_slots.py",
      "chunk_id": "88277e588c205ff54308a0e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/secrets_check/test_w2_20_pool.py",
      "chunk_id": "9eb3a04cf5b673529522e7de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6f0s/PR-DAEO-6f0s.md",
      "chunk_id": "69f50c3cd25a91e11cb81cd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121/w2_121_support.py",
      "chunk_id": "a02e4e69f85640f54d674362",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "5c2b8a59bf58cfa2a2c6fdbe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ozyt/PR-DAEO-ozyt.md",
      "chunk_id": "bfa38f25be668d1dbf034167",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-60a/w2_60a_support.py",
      "chunk_id": "01123898ea9ad9b9352c896f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-157/README.md",
      "chunk_id": "54ee0193b0d7b9670ea3216d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_command_set.py",
      "chunk_id": "1402c4d26c99d78292b4cfb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "c9fc8c0771bacea0a51022a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "27cfbf121fbc69848bb589fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/test_w2_56_r5_lead_store.py",
      "chunk_id": "f3b7de0392e01916617a024d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "5be66584dfc10561cbe2a2ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "b947d7a8b4291086dc0ac520",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-60a/README.md",
      "chunk_id": "f8b1d13a135833542374b6be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-07/test_w2_07_pre_close_gate.py",
      "chunk_id": "b74a99cb2b2d3db75893926a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ozyt/PR-DAEO-ozyt.md",
      "chunk_id": "807bd386729b130c8af1110b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ozyt/PR-DAEO-ozyt.md",
      "chunk_id": "e3d98483c1211137da844ad8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-2bdu/PR-DAEO-2bdu-s27.md",
      "chunk_id": "5f820b0ad4075a3affd8ad38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "74c6494d2281044c51b0e1d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ozyt/PR-DAEO-ozyt.md",
      "chunk_id": "dbfb3e04da4fd19ea575ea55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "63349c107f71b8a69e18e444",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "d63aaa2c028ad22a6d65762e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ifgf/PR-DAEO-ifgf-round-2.md",
      "chunk_id": "a133660b09b6409cd032f225",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/README.md",
      "chunk_id": "0a0c114dd7e249852eb528a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121c/README.md",
      "chunk_id": "b70055e8475970bf56986553",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "e792619d94223687ea1cf4fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ozyt/PR-DAEO-ozyt.md",
      "chunk_id": "9beb80607a3209a3bdcfcf9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "2aad9135dfaeae5626bf290e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-56/README.md",
      "chunk_id": "5a6270e7e739d0f65eb95acf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "88b05d1beead83a5369e53b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "89164f3e9e83a227dc05d647",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "f30601e913f1228f4914399b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "5ecb05755e5a529c160c4c0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "754ed5dde478ebbd8e1c69b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_unit_gate.py",
      "chunk_id": "c811c2c34375263326350108",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "7fc6cf51a6b4674131544675",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "5e223364fcdb33a71e9b82fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "093f7133f23d2458cafcb793",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "bb73ef0c0355e06de7cc2503",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "05cbded24705d4abb77fe529",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "5c25e5f48f6fa630400c1917",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "86ebe8e12e8d49d9a605c209",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py",
      "chunk_id": "04dcff1eb83c862e4aa29da5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py",
      "chunk_id": "d9329ad389a096bb5a1e419b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/README.md",
      "chunk_id": "7dfac06643ec526efd6a3e04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "87c7a0c6c7dad23aa7e86a90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/w2_22_tools_support.py",
      "chunk_id": "c43cba07c99aac5f1315c720",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/w2_22_tools_support.py",
      "chunk_id": "24ad542e85289323843ceaa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/README.md",
      "chunk_id": "6ee744c2c5ad307e97c78cd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py",
      "chunk_id": "8956a2dce200bc97d9cc21ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py",
      "chunk_id": "9038cd7dd3c12b08021d5fdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/w1_48_support.py",
      "chunk_id": "30d5d0605f1bcf02d5b3054c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "411231a3c97f08aea0af7a0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/w2_22_tools_support.py",
      "chunk_id": "1702fa6e42f858bdf477bb2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "e808d44af47412585235987c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r6.py",
      "chunk_id": "38e95d6090ad6afd67bcb249",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/w2_22_support.py",
      "chunk_id": "bf73b954d5a75c95299d9b69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r6.py",
      "chunk_id": "2fe3fab6abcac3fd18722866",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r6.py",
      "chunk_id": "350e494d6ecaf07c1a792552",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "336c1d1e4024089968003e45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/README.md",
      "chunk_id": "d231a9746c97dc599506a894",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r5.py",
      "chunk_id": "98ea1fb9d0151b434d0c6295",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/w1_48_support.py",
      "chunk_id": "12057040380ba65210726b1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/README.md",
      "chunk_id": "f08361b1559e1829049bab61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/README.md",
      "chunk_id": "e019d08ec66b6328bb1aee55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_tool_in_own_folder.py",
      "chunk_id": "7beee2ca1a259c46696a25fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "caff1ff2d260ed804991862a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/doctor/test_w2_22_own_folder.py",
      "chunk_id": "ee0918fa7c47f64ab7b8b9ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r5.py",
      "chunk_id": "c82ed6aee0b1804254c7f573",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/resources/test_w2_20_gate_null.py",
      "chunk_id": "f3a81e809c25d99f94dd7101",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/README.md",
      "chunk_id": "7d1449ec4016d0801573979b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-48/test_w1_48_node22_prefix.py",
      "chunk_id": "f972333e3035aa6b6449ffb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor.py",
      "chunk_id": "12babd10fe998f0f21b70390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/test_w1_27_doctor_r6.py",
      "chunk_id": "e79ec9a63aeb42b722710a62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/w2_22_tools_support.py",
      "chunk_id": "bb5c0e8f68f941f7f12994e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-27/README.md",
      "chunk_id": "3161b002a2e33e0358dc2bd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "b24a0bc1b457cad7be209bbd",
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
    },
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "DEC-803",
          "DEC-866",
          "DEC-898",
          "DEC-961",
          "DEC-979",
          "DEC-1030",
          "DEC-1031",
          "DEC-1088",
          "DEC-1097",
          "DEC-902",
          "DEC-984",
          "DEC-1157"
        ],
        "left": 15
      },
      "changed_by": {
        "DEC-898": [
          "DEC-902"
        ],
        "DEC-961": [
          "DEC-984"
        ],
        "DEC-979": [
          "DEC-1157"
        ],
        "DEC-1088": [
          "DEC-1157"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5867
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLXIzMGwubWQiLDEsMzIsImQ4NTdhZjViNmQ5YThlMDI2NWIxNjVkMiJdLFsiLnRpY2tldHMvREFFTy1yMzBsLm1kIiw2NywxMTUsImEzMDZiM2RiMWQyMDcyNWM2YWFiMjk3MyJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsNjg4LDY5MywiOTE3ZTVlZDliMjg1ZTkzN2FhNDc1N2UxIl0sWyJkb2NzL2NoYW5nZXMvVzItMjAtZXZpZGVuY2UubWQiLDI0LDM1LCI0OGNhMDUzYmI3Nzk0YWIwODM4YTE0YWMiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtZml4LXJlcGluLXJlZ2lzdHJ5Lm1kIiwxNSwxNywiMTE4MGJhZjI3ZDhmMzZlMmQ0YzIxZWM3Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0lOVEVHUkFUSU9OLVBMQU4ubWQiLDc0LDc1LCIyYmRmYWIwMWZhOWNhNTI0NGY1OTYyMTkiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vSU5URUdSQVRJT04tUExBTi5tZCIsNzUsNzcsIjJkNDZhMTllMjczYzU4YzY5MGZjYmFlYSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vY2xvc2VzL1cyLTIwLURBRU8tcjMwbC5tZCIsNSw5LCIzZWQ3NWEwM2U4MzE0MjhmYmRmYjYzYTEiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtVzItMjAtU0NPUEUubWQiLDEsNCwiY2Y4OWU4NDI3YTc2ZjBjNDJmNjJhNDUxIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVcyLTIwLVNDT1BFLm1kIiw1LDEzLCI3MjBhYzJjYzI3NjNjNmIwNjI5NTdjYjkiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtVzItMjAtU0NPUEUubWQiLDI0LDI4LCI1MDc5ZTQyOTY5NTUwNzI1M2EzZDFjODYiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtVzItMjAtVEhSRUFELUJVREdFVC5tZCIsMSw2LCJmOTcwZjMzZTk2MWRmZWJkMDg2N2Q1YTIiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL1AtVzItMjAtVEhSRUFELUJVREdFVC5tZCIsMzUsMzcsImY1ZDU5NDQyMDllODgyMWNhOTYxZDNkYyJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYSIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiMTlhYTYwYTI2ODU1YjYxNCIsIm8iOlsyLDAsMSw5LDM4LDMwLDI1LDMyLDUsMjYsNywyMSw0LDIyLDE4LDEyLDMxLDM2LDM1LDE2LDMsMjAsMjMsMjcsMjgsMzcsMTksMTQsMTMsMTcsOCw2LDM0LDEwLDE1LDMzLDI5LDExLDI0LDM5XX0sInEiOiJ0aGUgcHJvZHVjdCBzbG90J3MgdGVzdCBydW4gUEFUSCwgbm9kZSAyMiBwcmVmaXggZnJvbSB0aGUgdG9vbCByZWdpc3RyeSwgb3BlbnNwZWMgYWJzZW50IHJlZHMgSS02LCBXMi0yMCBzbG90IGNvZGUsIGRvY3RvciB0b29sIHJlcG9ydGluZyIsInIiOjAsInMiOiJlNDU5ODc3MDI4OTJkNWQ2Njk5MjQ5OWVlYzhmOTBiZWIxY2Q0ODQ1IiwidCI6bnVsbCwieCI6WyIxMWYzN2VmMTRjZTdjZGYxZWM0MzhmYWYiLCI2NDU5NTRiOTE2YWUxYmQ5ZGU1MjkzNmEiLCI2Y2ZhMzE1MTljY2M4MGU0OTVkMjkwZWMiLCI4MWViMTE5ZGQ0MWZkZjQ4ZTdjMjRmYTciLCI4YWQ4NjE1OWVlZDhmNGEyMzQyOGJlNjciLCJjMzA3M2YxMDJhOGJiNWYyNWQxNzRiNTIiLCJmZWE4OTIzMzc3NmNlMDM1YWQ1ZThmZjEiXX0=",
  "routing": {
    "code": [],
    "named": [
      "a306b3db1d20725c6aab2973",
      "d857af5b6d9a8e0265b165d2"
    ],
    "phrasings": [
      "the product slot's test run PATH, node 22 prefix from the tool registry, openspec absent reds I-6, W2-20 slot code, doctor tool reporting",
      "product slot s test run PATH node 22 prefix tool registry openspec absent reds I-6 W2-20 slot code doctor tool reporting",
      "the product slot's test run PATH, node 22 prefix from the tool registry, openspec absent reds I-6, W2-20 slot code, doctor tool reporting DAEO-r30l"
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
    "nested": [
      {
        "chunk_id": "917e5ed9b285e937aa4757e1",
        "path": "docs/DECISION_REGISTER.md",
        "start_line": 688,
        "end_line": 693
      },
      {
        "chunk_id": "3ed75a03e831428fbdfb63a1",
        "path": "governance/project/orchestration/closes/W2-20-DAEO-r30l.md",
        "start_line": 5,
        "end_line": 9
      }
    ]
  }
}
