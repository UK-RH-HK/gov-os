# Revision 7 findings reclassified

## Summary

Revision 7 remains rejected against CP-1. Reclassification changes what happens next: it does not justify Revision 8, and it prevents implementation/qualification findings from silently expanding Phase-1 architecture acceptance.

| Finding | Technical validity | Provenance | Correct lifecycle | Recommended action |
|---|---|---|---|---|
| RV7-H1 | confirmed | necessary-derived from owner OP-4/7/11/14/15 | CP-1 architecture | preserve as CP-1 blocker; smaller target uses signed revocation/version metadata and narrower claims |
| RV7-H2 | confirmed | necessary-derived from OP-7/OT-1 | CP-1 architecture | preserve as CP-1 blocker; owner choose expiry/availability in new target |
| RV7-M1 | confirmed | necessary-derived from OP-13; remedy implementation choice | CP-1 bootstrap architecture | preserve; owner decision if single designation remains |
| RV7-M2 | confirmed | necessary-derived from OP-10/16/OT-2 | platform certification architecture | executable criterion required before high-assurance certification, not R0/R1 |
| RV7-M3 | confirmed against stated bound | necessary-derived from CP-1 claim | qualification/certification | test required combinations or narrow residual claim |
| RV7-M4 | confirmed availability gap | new owner decision required | product/CI profile | select provisioned CI or exclude privileged CI |
| RV7-M5 | confirmed | necessary-derived from OP-14 | implementation acceptance | add monotonic-store recovery test if model retained |
| RV7-M6 | confirmed | implementation choice | implementation | choose stable project identity; do not block abstract R0 |
| RV7-M7 | confirmed | original recovery guarantee, implementation detail | implementation | journal/recovery test |
| RV7-M8 | confirmed edge case | verifier hardening | hardening/operations | document/admin boundary or make overlay durable |
| RV7-M9 | confirmed | implementation correctness | implementation | persist sufficient roll-forward state |
| RV7-M10 | confirmed | verifier hardening, Contract V later | qualification | expand vectors before G6 |
| RV7-L1 | confirmed | necessary-derived OP-1 | implementation/schema | constrain schema and compiled check |
| RV7-L2 | confirmed | necessary-derived CP-1 source model | operational qualification | define first-hand publication history/genesis |
| RV7-L3 | confirmed | necessary-derived 24h guarantee | CP-1 operations | state cadence/failure semantics |
| RV7-L4 | confirmed | Contract evidence freshness / verifier hardening | evidence quality | refresh and make runner self-contained |
| RV7-L5 | confirmed | necessary-derived CP-1 bootstrap | operational qualification | define verifier genesis |
| RV7-L6 | confirmed | recovery implementation | implementation | resolve undo/uninstall semantics |
| RV7-L7 | confirmed | clock hardening | later hardening | define trusted-time/skew recovery limits |
| RV7-L8 | confirmed | implementation choice | implementation | atomic durable store transaction |
| RV7-L9 | confirmed | implementation hardening | implementation/qualification | replay-safe one-time reset semantics |
| RV7-L10 | confirmed | necessary-derived OP-13/OT-1 | operational qualification | write two-channel procedure |
| RV7-L11 | confirmed | necessary-derived Contract A1 | implementation/schema | default-deny new authority-bearing keys |
| RV7-L12 | confirmed | necessary-derived OP-11 | implementation/certification | computed security-change classification |
| RV7-I1 | accurate limitation | later qualification | operational audit | prove organizational independence outside key-ID checks |
| RV7-I2 | accurate but non-material | implementation-choice metadata | record hygiene | keep `in_effect:false`; schema improvement optional |
| RV7-I3 | accurate | owner clarification | owner package | record explicit C1/C2/C3 consequence if CP-1 reused |
| RV7-I4 | accurate | verifier hardening | documentation | move excluded paths to history |
| RV7-I5 | accurate | deployment boundary/ODR | integration | authenticated adapter for high-risk deployments |
| RV7-I6 | informational | implementation choice | none | no Phase-1 effect |

## Reclassified verdicts by gate

- Against CP-1 Revision 7: `REJECTED` (H1, H2, M1 and internal claim defects remain).
- Against the original Governance OS baseline: Revision 7 is not the appropriate acceptance object; most findings are not original requirements.
- Against Contract v3 A2: Revision 7 demonstrates serious research but is not needed to satisfy A2; a smaller standard architecture can.
- Against later high-assurance platform certification: `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE`.
- Next architecture revision: prohibited by owner freeze; meta-review recommends a new owner decision and rebase, not Revision 8.
