# Upstream lesson inbox

Destination of `gov upstream submit … --destination <clone>/lessons/inbox`. Each submission is a directory
`PKT-xxxx-<project-alias>/` containing exactly `packet.yaml` (schema `upstream-packet`) and, optionally, declared
synthetic fixture files under `fixture/`. Nothing else is accepted by the export gate (INV-012).

Intake (protocol §15): deduplicate/cluster → severity/frequency/confidence → Framework Change Proposal under
`change-proposals/` → implementation + synthetic regression fixture → independent verification → release.
