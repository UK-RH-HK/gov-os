#!/usr/bin/env bash
# The first re-pin (DEC-884, DEC-889 item 15, DEC-899 item 4, DEC-918, DEC-921): the owner's act.
# Run in a plain terminal (not inside a Claude session), with no Claude session running a gov command
# (the orchestrator confirms the leads are idle before the ACT). Part A re-pins; Part B regenerates the settings.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
P="$HOME/.local/share/gov-os"
C=6a4696eb
W="$P/wheels/$C/gov-0.1.0-py3-none-any.whl"

# ---- Part A: the re-pin -------------------------------------------------------------------------------------------
# A1. A clean export of 6a4696eb, the merge that holds W2-58, W2-59, W2-65, W2-66, W2-07, W2-69 and W2-72
git -C "$R" cat-file -e "$C^{commit}"
rm -rf /tmp/gov-pin-src-$C && mkdir /tmp/gov-pin-src-$C
git -C "$R" archive "$C" | tar -x -C /tmp/gov-pin-src-$C

# A2. The wheel, reproducible (the commit's own time); offline, no build download. The orchestrator's dry run built
#     it twice from clean exports with this sha256.
mkdir -p "$P/wheels/$C"
SOURCE_DATE_EPOCH=1792954352 python3 -m pip wheel --no-deps --no-build-isolation --no-index -w "$P/wheels/$C" /tmp/gov-pin-src-$C
echo "73a281fff667c16eef5cc9157798e727d0a91cdd7c0d7846d474be57e6c6b6c9  $W" | sha256sum -c -

# A3. Its own environment, non-editable (system + user site packages give PyYAML, pytest, xdist, pytest-timeout,
#     sqlite-vec). The bootstrap pin pin-fecb870c is left in place for the rollback.
python3 -m venv --system-site-packages "$P/pin-$C"
"$P/pin-$C/bin/python" -m pip install --no-deps --no-index "$W"

# A4. Point gov at the new pin
ln -sfn "$P/pin-$C/bin/gov" "$HOME/.local/bin/gov"
hash -r

# A5. Verify
readlink -f "$(command -v gov)"                                                  # .../pin-6a4696eb/bin/gov
"$P/pin-$C/bin/python" -E -c 'import gov; print(gov.__file__)'                   # .../pin-6a4696eb/lib/python3.12/site-packages/gov/__init__.py
"$P/pin-$C/bin/python" -E -c 'import yaml, pytest, xdist, pytest_timeout, sqlite_vec; print("deps ok")'
gov --help | head -1                                                             # usage: gov [-h] <command> ...

# A6. The registry entry (refuses unless A2-A4 hold); then commit it
python3 "$R/.gov-runtime/scratch/orchestrator/pin/repin_registry.py"
git -C "$R" commit -m "DEC-921: the first re-pin, gov from the wheel of 6a4696eb" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-921" --trailer "Role: owner" -- governance/project/tool-registry.yaml

# ---- Part B: the settings regeneration (after Part A, DEC-884; W2-59's CIT-P act A2) ------------------------------
# B1. By hand, in .rulesync/permissions.jsonc: delete the two "./docs/source/**": "deny" entries (P-I1-2; the folder
#     left the tree on 2026-10-01), keeping the file valid JSONC; and add the lead clean-up rule you choose in
#     ACT-REPIN-1 item 4, if any. Change nothing else there.
# B2. Generate, then the held-out rules (DEC-641's apply procedure), with the pinned judge:
#       cd "$R" && rulesync generate --targets claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills
#       cd "$R" && "$P/pin-$C/bin/python" -E -m gov.guard.heldout
# B3. Look at what changed (expect: the hook lines take W2-59's and W2-65's form; the two docs/source deny lines go):
#       git -C "$R" status --short; git -C "$R" diff --stat
# B4. Commit the source and the generated files together (Role: owner), with the decision trailer DEC-921.

# ---- Rollback (one command; the old judge comes back) ------------------------------------------------------------
#   ln -sfn "$P/pin-fecb870c/bin/gov" "$HOME/.local/bin/gov"; hash -r
#   then revert the registry commit (and, if Part B was done, the settings commit).
