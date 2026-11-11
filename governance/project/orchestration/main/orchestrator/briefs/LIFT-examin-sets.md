# W2-94 and W2-93's sets by the walled writer route: the `evaluation_sets` ACT and the two writer briefs (DEC-1130 (3))

Read `LIFT-common.md` first (scratch only). Role: ACT-preparation and product-spec helper, Sonnet high, class C2
(DEC-1120). Scratch folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/examin-sets/`.
**Never open, list or read anything under `~/gov-os-eval/` (the sets root) or `~/gov-os-runs/`, or any folder named
hidden, memory-verdict or memory-verdict-2.** You write about where sets go; you never look at a set.

## Read first
DEC-1130 (3), DEC-1101 (2)-(3) (the walled writer route and the launch script), DEC-1082 (3) and DEC-1097 (the hidden
half and the walls), DEC-1113 (set-up A's fixed briefs), DEC-1129 (2) (the memory audit's briefs, the latest approved
writer brief: `packages/MEMORY-AUDIT-1/briefs/writer.md`, a model). The tickets: W2-94 (`.tickets/DAEO-g87r.md`,
EXAMIN's question set: memory questions with gold sources about the owner's copy, a visible and a hidden half) and W2-93
(`.tickets/DAEO-6y0x.md`, W2-81's held-out half: hidden questions and planted-problem variants per synthetic
repository); W2-81 (`DAEO-l78m`, the proving ground) for the repositories. The path map's `evaluation_sets` section
(`governance/project/path-map.yaml`: the existing entries, e.g. the memory sets, their keys and what the guard and the
store do with them: `src/gov/guard/`, `src/gov/rebuild/` "kept_out", `src/gov/close/` if read). The launch script
`governance/project/orchestration/tools/indep_launch.py` and `governance/project/indep-walls/kinds.yaml` (what a writer job
needs: inputs, delivery folder, the brief's front matter). The class table `governance/project/operator/class-rules.yaml`
(which row the path map's `evaluation_sets` edit falls in: if adding entries only tightens, it may be class (a)).
Model ACTs: ACT-SETS-GLOBS-1 and ACT-GUARD-SETS-1 (search `packages/`).

## Build
1. **The ACT** (`ACT-EXAMIN-SETS-1.md` with a bundle in the operator's form, like `acts/ACT-PERMISSIONS-3/`: manifest,
   apply.sh, before/after of `governance/project/path-map.yaml`, list, rehearsal log ending `failures: <n>`): two
   `evaluation_sets` entries, `examin` and `adoption-proving-ground`, in the existing entries' form: where each set lives
   under the sets root, its hidden and visible halves, its globs; and whatever else the existing entries carry so the
   guard refuses the hidden half to every session but its writer and checker, the store keeps it out, and the
   independent launch script can deliver into it. Rehearse in a clone in your folder: the guard's deny on a planted
   hidden path for an engineer, CTO and test designer; the store's `kept_out`; `gov.check.pathmap` exit 0. Give the class.
2. **Two writer briefs** in the form of the memory audit's writer brief, with front matter the launch script resolves for
   kind `writer`: `EXAMIN-writer.md` (W2-94's set: what the writer reads of the owner's copy — say which copy and how
   the wall gives it; how many questions, visible and hidden; gold sources; the rubric; the delivery) and
   `PROVING-GROUND-writer.md` (W2-93's: per synthetic repository, hidden questions and planted-problem variants). Each
   names its KPI lines from the ticket it serves, word for word, and stays inside them (DEC-1128 (5)). Note any question
   only the owner can answer (e.g. which copy of EXAMIN; set sizes) as a choice with your recommendation.
3. A short `FOR-THE-OWNER.md`: what the owner approves (the ACT's yes line; the two briefs' sha256 for the approved list
   by a later install ACT), and the order.

## Return
The twelve fields, short; the files; the rehearsal count. Estimate 1.5 to 2 h.
