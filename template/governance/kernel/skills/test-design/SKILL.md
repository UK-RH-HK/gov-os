---
name: test-design
version: "1.0.0"
description: Method for independent test design from specification and KPIs, without reading implementation.
---
# Test design

This skill describes how the independent test designer writes acceptance tests. It follows the Contract and the decision register; it does not grant permissions or set rules on its own authority.

## Read restriction

The test designer reads only the ticket's specification and its KPIs (CAP-38.b, DEC-136). The test designer does not read implementation files, source code, or any path under src/ or other production directories (CAP-38.b). This constraint keeps acceptance tests independent of the implementation so they verify behaviour, not structure.

## Inputs

1. The ticket, including its specification, KPIs (success and failure lines) and acceptance test path (CAP-38.b).
2. Probe findings from the orchestrator's review, when present (DEC-136, CAP-38.e).

## Writing acceptance tests

For each KPI success and failure line, the test designer:

1. Derives one or more test cases from the specification and the KPI wording (CAP-38.b).
2. Writes the test so that it asserts observable behaviour described in the specification (CAP-38.b, DEC-136).
3. Keeps each assertion traceable to a specific KPI line (CAP-38.b).

## Handling probe findings

Per DEC-136 (CAP-38.e), when the orchestrator's review produces probe findings:

1. Each finding is taken as a described behaviour, not as code (DEC-136, CAP-38.e).
2. The test designer decides from the specification whether each finding becomes an acceptance test (DEC-136).
3. A finding that reveals a specification gap is reported to the orchestrator so the specification can be amended before testing proceeds (DEC-136, CAP-38.e).

## What the test designer produces

- A test module under the ticket's acceptance test path (CAP-38.b).
- A conftest if shared fixtures are needed (CAP-38.b).
- A report of any specification gaps found during test design (DEC-136, CAP-38.e).
