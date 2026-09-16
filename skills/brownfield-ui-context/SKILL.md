---
name: brownfield-ui-context
description: Create or reconcile Impeccable PRODUCT.md context for an applicable Brownfield UI review when it is missing or materially stale. Use native Impeccable init with the correct product, OpenSpec, and AS-IS authority; this is setup, not a lifecycle gate.
---

# Brownfield UI Context

Prepare trustworthy Impeccable product context only when an applicable UI
review needs it.

This skill is a setup and reconciliation workflow. It does not issue a gate
verdict and is not required for non-UI work.

## Trigger

Run when an applicable Brownfield UI preflight or conformance review needs
`PRODUCT.md` and either:

- the file does not exist; or
- a bounded semantic comparison for the current Change found material product-
  truth drift.

Do not create `PRODUCT.md` during Brownfield installation. Do not require it for
backend-only work, internal refactors, or other non-UI workflows.

## Authority context

Supply native Impeccable `init` with the bounded evidence relevant to the
current Change. Use each source only for the questions it authoritatively
answers:

- the canonical PRD and Approved product, access, boundary, and UX decisions
  for durable product intent and approved capabilities and surfaces;
- OpenSpec main specs and the completed Change artifacts for specified behavior
  and current Change intent;
- the repository, relevant tests, and `openspec/system/brownfield-map.md` for
  relevant AS-IS facts; and
- human clarification only for unresolved durable product intent.

`PRODUCT.md` is project-owned auxiliary context for Impeccable. It does not
override any of these authoritative sources.

Do not create a single global precedence chain. Surface material conflicts
between sources according to the kind of question they answer.

## Workflow

1. Read only the portions of the authority sources needed to establish the
   durable product context affected by the current Change.
2. Use the installed Impeccable skill's native context and `init` workflow.
   Follow its current schema, interview, confirmation, and write semantics
   instead of reproducing them here.
3. Give native `init` the authoritative facts as settled context. Ask the human
   only about unresolved durable product intent; do not ask them to re-decide
   intent already marked Approved.
4. Preserve Impeccable's normal human confirmation before creating or updating
   `PRODUCT.md`, including when authoritative evidence already settles every
   relevant fact.
5. After native `init` completes, return control to the UI review that routed
   here. The caller reruns its bounded semantic check or gate.

Native Impeccable context or doctor may report and handle Impeccable-owned
tooling or schema drift. Semantic drift between `PRODUCT.md` and authoritative
product truth is a Brownfield concern, but reconciliation still occurs through
native Impeccable `init`.

## Boundaries

Never:

- auto-generate or auto-rewrite `PRODUCT.md` from Brownfield sources;
- treat repository evidence as approval of durable product intent;
- invent a Brownfield PRODUCT.md schema, writer, or Impeccable adapter;
- create hashes, timestamps, watchers, freshness databases, or another drift
  subsystem; or
- modify application code, OpenSpec artifacts, Approved product documents, the
  brownfield map, or the roadmap.
