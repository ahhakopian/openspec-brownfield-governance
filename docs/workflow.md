# Workflow

The package preserves the ordinary OpenSpec lifecycle. For materially
UI-affecting Changes, it adds the governed path:

```text
OpenSpec propose
-> human review
-> planning complete
-> brownfield-ui-preflight
   -> REVISE -> reconcile planning -> brownfield-ui-preflight
   -> PASS -> continue
-> brownfield-complexity-gate
   -> PASS -> OpenSpec apply
   -> REVISE -> reconcile design/tasks -> brownfield-complexity-gate
-> implementation verification
-> browser-verification
-> native Impeccable critique
-> brownfield-ui-conformance
   -> REVISE (implementation) -> verify, browser-verification, critique, conformance
   -> REVISE (planning) -> reconcile -> UI preflight -> complexity gate
   -> PASS -> final OpenSpec verification
-> incrementally maintain brownfield map for every verified Change
   -> add implemented AS-IS; remove/replace superseded AS-IS
-> check map internal architectural consistency
   -> consistent -> continue
   -> conflict -> inspect only relevant repository evidence, resolve, recheck
-> OpenSpec archive/spec synchronization
-> refresh cross-change roadmap
-> commit
```

`brownfield-ui-context` is setup/reconciliation rather than a gate. It runs
only when an applicable UI review needs missing or materially stale `PRODUCT.md`.
Impeccable remains the external native UX workflow provider, and
`browser-verification` remains the external browser-evidence provider. Non-UI
Changes continue from planning complete directly to `brownfield-complexity-gate`
and do not require `PRODUCT.md` or Impeccable readiness.

`brownfield-map` maintains descriptive AS-IS evidence. Its full-discovery
workflow remains available for bootstrap or a missing/stale baseline; the
post-Change step is incremental maintenance, not a full repository rescan.
`product-boundaries` reconstructs or explicitly governs the product model and
does not create a parallel change lifecycle. `cross-change-roadmap` sequences
candidate changes without creating or authorizing them.

Deferred artifacts remain prior evidence rather than current requirements or
implementation authorization.
