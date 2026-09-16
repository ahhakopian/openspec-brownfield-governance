---
name: brownfield-ui-conformance
description: Perform the post-implementation UI governance gate for a materially UI-affecting OpenSpec Brownfield Change. Reconcile bounded browser-verification evidence and native Impeccable critique against approved planning, product authority, and AS-IS constraints before final OpenSpec verification.
---

# Brownfield UI Conformance

Issue the post-implementation UI governance verdict for one materially
UI-affecting OpenSpec Change.

This gate synthesizes evidence. It does not replace project verification,
browser-verification, native Impeccable critique, or final OpenSpec
verification.

## Lifecycle position

Run in this order:

```text
implementation
→ normal project and task verification
→ browser-verification for applicable UI behavior
→ native Impeccable critique
→ brownfield-ui-conformance
→ final OpenSpec verification
→ incremental brownfield-map maintenance
→ archive and spec synchronization
→ cross-change-roadmap reconciliation
```

## Required evidence

Use only evidence bounded to the materially affected surfaces, states,
interactions, and viewport classes:

- the approved Change proposal, specs, design, and tasks;
- relevant OpenSpec main specs;
- relevant canonical PRD and Approved product, access, boundary, and UX
  decisions;
- relevant `PRODUCT.md` context;
- relevant AS-IS constraints from the brownfield map, repository, and tests;
- results from normal implementation and task verification;
- bounded browser-verification evidence; and
- the result of native Impeccable `critique` run normally against the
  implemented target.

Do not require exhaustive state or viewport testing for every Change. Require
enough evidence to support the materially affected behavior and UI claims.

This gate normally consumes `PRODUCT.md` context already checked by the
applicable preflight. If that context is missing or is known to be materially
stale for the current review, stop, route through `brownfield-ui-context`, and
rerun native critique before this gate. Do not perform an unrelated freshness
scan.

## Responsibility split

Keep responsibilities distinct:

- `browser-verification` gathers bounded rendered and browser-behavioral
  evidence using its existing capability;
- native Impeccable `critique` evaluates the implemented surface using its own
  current workflow and may create Impeccable-owned snapshots or other tooling
  artifacts; and
- this skill reconciles those results with approved Change intent, Approved
  product and UX authority, `PRODUCT.md` context, and relevant AS-IS
  constraints, then issues the governance verdict.

Do not build another browser harness or pass browser-verification through a
custom Impeccable adapter. Do not substitute one evidence source for the other.

Native Impeccable `audit` is optional. Use it only when the Change materially
requires its technical UI-quality checks; it is not a universal prerequisite.

## Governance synthesis

Determine whether the implemented UI:

- conforms to the approved Change behavior and material interaction decisions;
- preserves relevant Approved capabilities, surfaces, UX decisions, access
  rules, and Product Boundaries;
- does not expose an internal capability merely because it exists;
- respects relevant AS-IS constraints that planning intentionally preserved;
- is supported by the bounded browser evidence; and
- has no material unresolved native critique finding that contradicts the
  approved Change or governing authority.

Treat `PRODUCT.md` as auxiliary Impeccable context, never as authority over
Approved product intent, OpenSpec behavior, or verified AS-IS facts.

Insufficient, missing, stale, or materially conflicting evidence cannot produce
`PASS`.

## Verdict

Return exactly one verdict token as the first line:

```text
PASS
```

or:

```text
REVISE
```

`PASS` means the bounded evidence supports conformance. Continue to final
OpenSpec verification.

`REVISE` must identify the evidence-backed mismatch or evidence gap and state
whether it points back to:

- implementation, which must be corrected and pass the relevant verification,
  browser-verification, native critique, and this gate again; or
- planning, which must be reconciled and then pass the applicable earlier
  `brownfield-ui-preflight` and `brownfield-complexity-gate` before
  reimplementation and repeated conformance evidence.

Do not invent additional verdict states. Insufficient evidence is reported as
`REVISE`, with the missing or inconclusive evidence named.

## Boundaries

This skill must not modify:

- application code or tests;
- OpenSpec planning or specifications;
- Approved product documents; or
- Brownfield architecture, map, or roadmap artifacts.

Do not create a persistent Brownfield UI review report, evidence database,
scoring system, custom browser layer, or Impeccable adapter.
