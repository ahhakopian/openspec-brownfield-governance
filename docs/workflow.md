# Workflow

The package preserves the ordinary OpenSpec lifecycle:

```text
OpenSpec propose
-> human review
-> planning complete
-> brownfield-complexity-gate
   -> PASS -> OpenSpec apply
   -> REVISE -> reconcile design/tasks -> brownfield-complexity-gate
-> implementation verification
-> incrementally maintain brownfield map for every verified Change
   -> add implemented AS-IS; remove/replace superseded AS-IS
-> check map internal architectural consistency
   -> consistent -> continue
   -> conflict -> inspect only relevant repository evidence, resolve, recheck
-> OpenSpec archive
-> refresh cross-change roadmap
-> commit
```

`brownfield-map` maintains descriptive AS-IS evidence. Its full-discovery
workflow remains available for bootstrap or a missing/stale baseline; the
post-Change step is incremental maintenance, not a full repository rescan.
`product-boundaries` reconstructs or explicitly governs the product model and
does not create a parallel change lifecycle. `cross-change-roadmap` sequences
candidate changes without creating or authorizing them.

Deferred artifacts remain prior evidence rather than current requirements or
implementation authorization.
