---
name: brownfield-ui-preflight
description: Perform the read-only pre-implementation UI governance gate for a completed OpenSpec Brownfield Change. Use when planning materially affects a human-facing surface, interaction, state, terminology, or accessibility behavior; run before the complexity gate and apply.
---

# Brownfield UI Preflight

Perform a read-only semantic UI governance review of one completed OpenSpec
Change before application-code modification.

Brownfield owns applicability, lifecycle orchestration, authority
reconciliation, and the final verdict. Native Impeccable workflows own UX
reasoning.

## Lifecycle position

Run in this order:

```text
completed OpenSpec planning
→ brownfield-ui-preflight when applicable
→ brownfield-complexity-gate
→ apply
```

Run this gate again after a `REVISE` result and planning reconciliation.

If the complexity gate or a later implementation discovery causes a planning
revision that materially changes the user-visible interaction, rerun this gate
before rerunning `brownfield-complexity-gate`.

## Applicability

Run when completed planning materially creates, removes, changes, or exposes a
human-facing:

- surface or information architecture;
- capability, control, or action exposure;
- interaction or workflow;
- relevant user-facing state, recovery, reset, or destructive behavior;
- user-facing terminology; or
- materially relevant accessibility behavior.

Skip backend-only work, internal refactors, and nonmaterial visual maintenance.
Decide applicability semantically; do not use file paths, labels, or numeric
thresholds as proxies.

## Inputs and authority

Read only the bounded material needed for the current Change:

- the completed Change proposal, specs, design, and tasks;
- relevant OpenSpec main specs;
- relevant canonical PRD and Approved product, access, boundary, and UX
  decisions;
- materially relevant `PRODUCT.md` context;
- relevant portions of `openspec/system/brownfield-map.md`; and
- repository code and tests only as needed to verify a specific AS-IS
  constraint.

Use Approved product sources for durable product intent, OpenSpec for specified
behavior and current Change intent, and the repository, tests, and brownfield
map for AS-IS facts. `PRODUCT.md` is auxiliary Impeccable context and cannot
override those sources.

## PRODUCT.md semantic check

Immediately before using `PRODUCT.md`, compare only its claims material to the
current Change against:

- the relevant canonical PRD;
- relevant Approved product, access, boundary, and UX decisions;
- relevant OpenSpec main specs and completed Change artifacts; and
- bounded Brownfield, repository, and test evidence for relevant AS-IS facts.

Material drift exists only when a conflict or omission could change the current
UI shape decision or cause it to violate a relevant Approved capability,
surface, UX decision, boundary, behavioral contract, or AS-IS constraint.

Unrelated omissions, file changes, timestamps, and non-consequential wording
differences are not material drift.

If `PRODUCT.md` is missing or materially stale:

1. stop preflight;
2. route through `brownfield-ui-context`;
3. reconcile through native Impeccable `init` with its normal human
   confirmation; and
4. rerun this gate from the semantic check.

Do not implement a general freshness scan or drift subsystem.

## Native Impeccable workflow

Use the installed Impeccable skill and its native workflow normally. Do not
copy its UX rules into this skill or wrap it in an adapter.

The default pre-implementation workflow is native Impeccable `shape`.

Choose another native workflow only when the actual problem requires it, for
example:

- `critique` when understanding an existing problematic surface is materially
  necessary;
- `distill` when the Change introduces meaningful control, option, or
  complexity proliferation; or
- `clarify` when terminology or copy is materially part of the Change.

Do not impose a mandatory `critique → shape → distill → clarify` pipeline.
Follow the selected native workflow's current confirmation and artifact
semantics. Native Impeccable-owned artifacts remain Impeccable artifacts; this
gate creates no persistent Brownfield UI review report.

## Governance synthesis

After the native Impeccable result, reconcile its UX reasoning against the
relevant Approved product authority, OpenSpec behavior, and AS-IS constraints.

Enforce both sides of this rule:

- an existing internal capability does not automatically justify visible UI
  exposure; and
- an Approved user-facing capability must not be removed merely for UX
  simplification.

Identify material conflicts without replacing product authority, inventing new
behavior, or treating current implementation as the target UI.

## Verdict

Return exactly one verdict token as the first line:

```text
PASS
```

or:

```text
REVISE
```

`PASS` means the completed planning is materially coherent with the native
Impeccable result, Approved product authority, specified behavior, and relevant
AS-IS constraints. The Change may proceed to `brownfield-complexity-gate`.

`REVISE` means application-code implementation must not start. Identify only:

- the evidence-backed UI or interaction problem;
- the affected planning artifact or decision;
- the relevant Approved constraint or stable ID when applicable; and
- the direction that must be reconsidered.

Do not rewrite the planning artifacts. After they are reconciled, rerun this
gate.

## Boundaries

This skill is read-only. Do not:

- modify application code, tests, OpenSpec artifacts, Approved product
  documents, or Brownfield map or roadmap artifacts;
- create a custom OpenSpec schema, UI review artifact, scoring system, evidence
  store, or persistent Brownfield review report;
- reproduce Impeccable heuristics or build an Impeccable adapter; or
- perform implementation verification or replace the complexity gate.
