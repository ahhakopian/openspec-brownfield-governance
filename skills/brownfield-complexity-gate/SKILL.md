---
name: brownfield-complexity-gate
description: Review a completed OpenSpec brownfield change for material unjustified architectural complexity before application-code modification. Use after planning is complete and before apply; do not use to design a replacement architecture.
---

# Brownfield Complexity Gate

Perform a read-only semantic pre-apply review of one completed OpenSpec change.

The purpose is to prevent accidental brownfield complexity while preserving
required behavior and real architectural constraints. This is a reviewer for
simplification, not an alternative architecture-design workflow.

## Trigger

Run after the planning artifacts required for the active change are complete
and before the first application-code modification.

Run it again after a `REVISE` result and after the relevant `design.md` or
`tasks.md` has been reconciled.

## Inputs

Read only the bounded material needed to assess this change:

- the active change's proposal, specs, design, and tasks;
- relevant current OpenSpec main specs;
- relevant portions of `openspec/system/brownfield-map.md`;
- relevant Approved product, access, and boundary documents; and
- repository code/tests only when needed to verify a specific claim about an
  existing mechanism, ownership, state, variability, or failure path.

Use the brownfield map as starting context. Do not perform a full brownfield
rediscovery or refresh the map.

## Decision policy

Existing architecture is the default integration target, but it is not
automatically correct. For structural decisions, prefer:

```text
Reuse
→ Extend
→ Local Refactor
→ Introduce New
```

Material new complexity is allowed when a current requirement, an existing
architectural constraint, or real current variability requires it.
Hypothetical future extensibility alone is not justification.

Do not use simplicity to weaken correctness, security, data integrity,
required reliability, required compatibility, Approved Product Boundaries, or
other real architectural invariants.

## Checks

### BC-1 — Existing mechanism vs new mechanism

Identify a new mechanism that lacks a reason beyond local implementation
convenience when an existing mechanism can reasonably satisfy the change by
reuse, extension, or bounded local refactoring.

### BC-2 — Parallel responsibility

Identify a new parallel path for a responsibility that already has an owner or
established path, such as validation, notification, authorization, or
configuration.

### BC-3 — Ownership / source of truth

Identify unnecessary duplicate ownership, authoritative state, persisted or
local copies of authoritative state, sources of truth, or synchronization work
that the change creates.

### BC-4 — Speculative abstraction

Identify abstractions or generalizations justified mainly by hypothetical
future needs. Examine interfaces with one current implementation, factories
without current construction variability, registries without runtime
registration/discovery, strategy hierarchies without current strategies, and
generic frameworks replacing bounded concrete code.

These patterns are allowed when current requirements genuinely justify them.

### BC-5 — State/config/infrastructure expansion

Identify unnecessary runtime state, configuration dimensions, persistence,
dependencies, caching, queues, synchronization, background processing, or
concurrency.

### BC-6 — Edge-case machinery

When edge-case handling materially increases structural complexity, first
check whether required behavior can be preserved through:

```text
invariant prevention
→ boundary validation or rejection
→ existing failure path
→ explicit failure
→ special recovery machinery
```

Do not treat recovery as inherently wrong. It must be necessary for the
current required behavior or invariant.

### BC-7 — Scope-to-complexity proportionality

Semantically assess whether the added structural complexity is proportionate to
the behavioral scope of the change. Do not use numeric scores, file/class
counts, or hard thresholds.

## Verdict

Return exactly one verdict token as the first line:

```text
PASS
```

or:

```text
REVISE
```

`PASS` means no material unjustified brownfield complexity was found and normal
apply may continue.

`REVISE` means application-code implementation must not start. State concise,
evidence-backed findings, identify the planning decision that must be
reconciled, and direct simplification using only the relevant options below:

```text
REUSE
EXTEND
REMOVE
INLINE
MERGE
NARROW
LOCALIZE
MAKE CONCRETE
USE EXISTING FAILURE PATH
```

Do not replace one complex design with another. If safe simplification is
insufficient and a genuinely new architectural choice is needed, state:

```text
requires design decision
```

Do not invent the replacement architecture.

## Boundaries

This skill is read-only. Do not:

- modify application code, tests, OpenSpec artifacts, or persistent project
  documents;
- create `review.md`, `complexity.md`, or any other persistent artifact;
- create complexity scores or a deterministic complexity engine;
- refresh `brownfield-map`; or
- replace correctness, security, reliability, compatibility, or product-boundary
  review.
