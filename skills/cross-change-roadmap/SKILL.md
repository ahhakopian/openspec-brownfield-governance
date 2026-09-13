---
name: cross-change-roadmap
description: Build or refresh a persistent cross-change implementation roadmap for a brownfield project. Sequence candidate OpenSpec changes from the current AS-IS baseline toward Approved product targets by identifying dependencies, overlaps, blockers, deferred work, and safe implementation order without creating change artifacts or implementation design.
---

# Cross-Change Roadmap

Build or refresh the persistent implementation roadmap at:

`openspec/roadmap.md`

The roadmap coordinates multiple future OpenSpec changes.

It is not:
- an OpenSpec change;
- a behavioral specification;
- a TARGET architecture;
- an implementation authorization;
- a substitute for `proposal.md`, change specs, `design.md`, or `tasks.md`.

## Primary objective

Determine the safest preliminary sequence of future changes needed to move the current brownfield implementation toward the Approved product target while minimizing cross-change conflict, duplicated work, and premature design.

## Required project sources

Use the relevant current portions of:

1. `openspec/system/brownfield-map.md`
   - current AS-IS capabilities;
   - runtime reachability;
   - ownership/dependencies;
   - known gaps;
   - evidence qualifications.

2. `docs/product/product-model.md`
   - Approved actors, roles, product capabilities, surfaces, UX decisions;
   - AS-IS → TARGET gaps;
   - Approved, Planned, Deferred, and Open decisions.

3. `docs/product/product-boundaries.md`
   - durable Product Boundaries;
   - Product Evolution Policy;
   - current boundary violations.

4. `docs/product/access-model.md`, when present
   - approved ownership, permissions, and access constraints.

5. `PRD.canonical.md`
   - canonical declared product requirements and invariants.

6. `openspec/specs/`
   - current canonical OpenSpec specs, when present.

7. `openspec/deferred-changes/README.md`
   - previously investigated work that is intentionally not active.

8. Relevant preserved deferred changes when their scope overlaps the roadmap.

9. Existing `openspec/roadmap.md`, when refreshing.

Inspect current implementation and tests only when the persistent sources above do not provide enough evidence to determine a material dependency, conflict, or current-state fact.

Do not repeat a full brownfield reconstruction.

## Operating mode

If `openspec/roadmap.md` does not exist:

`BUILD`

Create the initial roadmap.

If `openspec/roadmap.md` already exists:

`REFRESH`

Reconcile it against the current repository, brownfield baseline, Approved product documents, canonical OpenSpec specs, completed/active/deferred work, and current milestone.

Do not assume the previous roadmap sequence is still correct.

## Roadmap workflow

### 1. Establish current milestone

Identify the current implementation milestone from Approved product decisions.

Separate:

- current milestone scope;
- explicitly deferred future capabilities;
- open product decisions;
- operational/evidence work that is not an implementation change.

Do not promote Deferred, Planned, or Open work into the current milestone.

### 2. Derive candidate changes

Identify the smallest meaningful candidate OpenSpec changes needed for the current milestone.

A candidate change should represent a coherent product/system outcome, not an arbitrary file/module grouping.

For each candidate identify:

- preliminary change name;
- objective;
- materially affected stable IDs where applicable:
  - ACT
  - ROLE
  - PCAP
  - SURF
  - UX
  - PB
- relevant current gaps;
- explicit non-goals;
- known deferred/prior work;
- likely dependencies on other candidate changes.

Candidate changes are planning hypotheses, not approved implementation designs.

Do not create directories under `openspec/changes/`.

### 3. Analyze cross-change dependencies

For every material pair of candidate changes, determine whether there is:

- no meaningful dependency;
- ordering dependency;
- ownership/authority dependency;
- data/lifecycle dependency;
- runtime/interface dependency;
- UX/surface dependency;
- semantic/configuration dependency;
- verification/evidence dependency.

Prefer ordering change A before change B when A establishes an authority, contract, lifecycle, semantic rule, or surface boundary that B would otherwise have to assume or later rewrite.

Do not invent dependencies merely because two changes touch the same file or module.

### 4. Analyze conflicts and duplicated work

Identify cases where implementing one candidate first could cause:

- work on a surface that a later change removes or relocates;
- temporary parallel authority;
- incompatible contracts;
- duplicated migrations;
- conflicting lifecycle behavior;
- contradictory UX;
- premature backend/service/account/storage decomposition;
- duplicate research already preserved in deferred work.

Where appropriate recommend:

- reorder;
- merge;
- split;
- defer;
- drop;
- block pending product decision.

Do not perform those implementation changes.

### 5. Detect product blockers

If sequencing requires a product decision that is not Approved:

mark the candidate as `BLOCKED`.

State:

- the unresolved decision;
- affected stable IDs;
- why technical design should not proceed;
- which other candidate changes are blocked by it.

Do not select a product decision on behalf of the user.

Do not turn the blocker into implementation design.

### 6. Determine preliminary sequence

Produce the smallest defensible ordering for current-milestone candidate changes.

Use dependency reasoning rather than numeric priority alone.

The sequence may change after each completed change.

Do not create detailed proposal/spec/design/tasks for downstream candidates.

### 7. Reconcile deferred work

For any relevant deferred change:

- reference its preserved location;
- retain its current deferred status unless its recorded reopen trigger is now satisfied;
- do not treat preserved artifacts as current requirements;
- if the trigger is satisfied, recommend fresh reconciliation before reactivation.

Never reactivate a deferred change automatically.

### 8. Refresh after completed work

When running in `REFRESH` mode:

- identify completed/archived changes;
- update the roadmap status for them;
- use the refreshed brownfield baseline and current OpenSpec main specs as the new current state;
- reassess all downstream dependencies and conflicts;
- reorder, split, merge, defer, drop, or add candidate changes only when current evidence justifies it.

Do not preserve obsolete roadmap assumptions merely for historical continuity.

Git history and archived OpenSpec changes provide historical traceability.

## Candidate status vocabulary

Use only when useful:

- `PLANNED` — candidate for the current milestone, not active yet.
- `ACTIVE` — an actual corresponding OpenSpec change is currently active.
- `COMPLETE` — implementation has been completed and archived.
- `BLOCKED` — cannot responsibly proceed until an identified decision/dependency is resolved.
- `DEFERRED` — intentionally outside the current implementation milestone.
- `SUPERSEDED` — replaced by a split, merge, or materially different candidate.

Roadmap status does not override OpenSpec lifecycle state.

## Required roadmap structure

Keep `openspec/roadmap.md` concise and maintainable.

Use this structure:

# Cross-Change Implementation Roadmap

## Status

Include:
- current milestone;
- roadmap status;
- last reconciliation date;
- repository revision when available.

## Purpose

State that this document sequences candidate changes and is not implementation authority.

## Current Milestone Objective

State the Approved implementation outcome for the current milestone.

## Explicitly Deferred / Out of Current Milestone

List relevant deferred or planned future capabilities and their reopen conditions.

## Candidate Changes

Use a compact table containing at least:

| ID | Candidate change | Status | Objective | Affected scope | Depends on | Main overlap / risk |

Use local roadmap IDs such as `C1`, `C2`, ... only for roadmap navigation.

They are not product stable IDs and must not replace ACT/ROLE/PCAP/SURF/UX/PB IDs.

## Dependency and Conflict Analysis

Describe only material ordering or conflict relationships.

## Preliminary Sequence

List the recommended order with a short reason for each position.

## Reconciliation Rules

Include that after every completed/archived change:

1. refresh the brownfield baseline when materially affected;
2. reconcile this roadmap against the new repository state and OpenSpec main specs;
3. mark completed work;
4. reassess remaining dependencies/conflicts;
5. reorder, split, merge, defer, drop, block, or add candidates when justified;
6. do not create future OpenSpec change artifacts during roadmap refresh.

## Next Recommended Change

Identify exactly one next candidate for `$openspec-propose`.

Explain briefly why it is safe and useful to start next.

Do not create the change.

## Hard constraints

- Preserve the distinction between AS-IS evidence and TARGET intent.
- Approved product decisions and Product Boundaries constrain sequencing.
- Current code does not override Approved product decisions.
- The roadmap does not approve new product scope.
- The roadmap does not approve technical architecture.
- The roadmap does not create or modify `openspec/changes/`.
- The roadmap does not run apply, archive, or spec synchronization.
- The roadmap does not edit production code.
- The roadmap must not turn a deferred capability into current MVP scope.
- Prefer a small number of coherent candidate changes over a large task backlog.
- Do not optimize ordering merely to minimize touched files; optimize for stable authority, contracts, lifecycle, semantics, and user-visible boundaries.

## Completion criteria

The skill is complete when:

- `openspec/roadmap.md` reflects the current milestone;
- all material current-milestone candidate changes are represented;
- explicit deferred work remains separated;
- material dependencies/conflicts are visible;
- a defensible preliminary order exists;
- exactly one next candidate is recommended;
- no active OpenSpec change was created;
- no implementation or premature downstream design was performed.
