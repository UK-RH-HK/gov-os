#!/bin/sh
# G1 (RoT-1 revision 3, 26 §3.1) — how Git delivers a tracked occupation file at .governance-runtime/migration to working
# copies that hold legacy adoption residue at that path. Scratch only: pass a fresh scratch directory as $1.
set -u
S="${1:?scratch dir}"; mkdir -p "$S" && cd "$S" || exit 2
G="git -c user.name=g1 -c user.email=g1@x -c init.defaultBranch=main"
mkdir origin && cd origin && $G init -q && printf '.governance-runtime/\n' > .gitignore && mkdir spec && echo a > spec/a.md && $G add -A && $G commit -qm legacy && cd ..
echo "== case 1: working copy with IGNORED residue directory in the way, then pull of the occupation commit"
$G clone -q origin wc1
mkdir -p wc1/.governance-runtime/migration/batch-1/files/spec
echo '{"moves":[],"created":[],"touched":[]}' > wc1/.governance-runtime/migration/batch-1/batch.json
echo residue > wc1/.governance-runtime/migration/batch-1/files/spec/a.md
cd origin && mkdir -p .governance-runtime && echo "ROT-1-TRUST-FORMAT:occupied" > .governance-runtime/migration && $G add -f .governance-runtime/migration && $G commit -qm "rot-1 occupation" && cd ..
cd wc1 && $G pull -q; echo "pull exit=$?"; printf 'type of .governance-runtime/migration: '; if [ -f .governance-runtime/migration ]; then echo regular-file; elif [ -d .governance-runtime/migration ]; then echo directory; else echo absent; fi
printf 'residue batch.json present: '; [ -e .governance-runtime/migration/batch-1/batch.json ] && echo yes || echo no
$G log --oneline | head -1; cd ..
echo "== case 2: working copy with UNIGNORED untracked residue in the way, then checkout of the occupation commit"
$G clone -q origin wc2 && cd wc2 && $G checkout -q HEAD~1 && printf '' > .gitignore && mkdir -p .governance-runtime/migration/batch-1 && echo x > .governance-runtime/migration/batch-1/batch.json
$G checkout -q main; echo "checkout exit=$?"; printf 'HEAD at: '; $G log --oneline -1; printf 'type of .governance-runtime/migration: '; [ -d .governance-runtime/migration ] && echo directory || echo other; cd ..
echo "== case 3: fresh clone"
$G clone -q origin wc3; printf 'type of .governance-runtime/migration: '; [ -f wc3/.governance-runtime/migration ] && echo regular-file || echo other
