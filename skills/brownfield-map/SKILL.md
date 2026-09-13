---
name: brownfield-map
description: Build or refresh an evidence-backed persistent AS-IS system baseline for an existing brownfield codebase. Use during initial OpenSpec bootstrap, after major structural changes, when the system map is missing or stale, or before a redesign whose impact cannot be understood safely from local openspec-explore alone. Do not use for ordinary local changes.
---

# Brownfield Map

Build or refresh a verified persistent model of the system that actually exists in the repository now.

This is a systematic brownfield discovery and persistence workflow.

Its output is descriptive AS-IS system knowledge for future OpenSpec planning.

Do not:

- design the target architecture;
- propose a migration;
- create an OpenSpec change;
- modify application source code;
- modify tests;
- modify legacy specifications;
- modify OpenSpec main specs;
- create or modify product boundaries;
- fix discovered defects.

## Output

Write or refresh only:

`openspec/system/brownfield-map.md`

Create `openspec/system/` if necessary.

Do not create additional persistent files.

## Relationship to openspec-explore

`openspec-explore` is a flexible investigation mode.

`brownfield-map` is a systematic persistence protocol.

Previous Explore findings MAY be used as leads, but they are not authoritative merely because an agent produced them.

Verify architecturally significant claims against repository evidence before persisting them.

## Core rules

### AS-IS is descriptive

Record what the repository actually implements, including poor architecture, incomplete integrations, unusual ownership, coupling, and technical debt.

Never replace observed architecture with preferred architecture.

### Evidence over inference

Support architecturally significant claims with repository evidence when available.

Prefer:

- source code;
- runtime entry points;
- configuration;
- manifests;
- schemas;
- contracts;
- tests;
- persisted-state implementations;
- build/deployment configuration;
- current OpenSpec artifacts;
- legacy specification artifacts.

If evidence is incomplete or conflicting, say so explicitly.

### Current behavior and intended behavior are different

Do not assume documented behavior is implemented.

Do not assume implemented behavior is intended.

When specification, configuration, implementation, tests, or runtime composition disagree, preserve and classify the disagreement instead of silently choosing one side.

### Facts and policies are different

This map records observed system facts and boundaries.

It does not turn an observed boundary into a permanent normative rule.

Normative cross-cutting constraints belong in `openspec/system/product-boundaries.md`.

### Absence is information

Explicitly record important components that do not exist.

Do not invent conventional frontend/backend/auth/database/service boundaries merely because similar systems usually have them.

### Prefer semantic capability identity

Legacy identifiers such as `001`, `002`, etc. may be preserved as mappings, but use stable semantic capability identifiers for the system model where practical.

Example:

`CAP-ADAPTATION — legacy SpecKit Feature 005`

Do not rename source code or legacy artifacts.

# Workflow

## 1. Establish the snapshot

Determine when available:

- repository root;
- branch;
- commit;
- working-tree status;
- map generation date;
- OpenSpec version;
- active OpenSpec schema;
- active OpenSpec changes.

The map describes this repository snapshot.

If Git metadata is unavailable, record that limitation.

Never discard or modify existing uncommitted work.

## 2. Establish source authority and freshness

Inspect relevant knowledge sources, including when present:

- canonical product requirements;
- `openspec/config.yaml`;
- OpenSpec main specs;
- active or relevant archived OpenSpec changes;
- legacy feature specifications;
- contracts;
- schemas;
- data models;
- architecture documents;
- plans;
- research documents;
- task ledgers;
- quickstarts;
- README/status documents;
- tests;
- runtime/build configuration;
- execution evidence.

Classify important sources where useful as:

- normative;
- current;
- executable;
- historical;
- stale;
- conflicting;
- missing;
- recorded-only.

If the repository defines a source-of-truth hierarchy, preserve it.

Do not invent one merely to resolve conflicts.

## 3. Build the capability baseline

Identify the major system/product capabilities that actually exist.

A capability is a meaningful system responsibility or externally observable behavior, not merely a directory.

For each capability determine where possible:

- semantic capability ID;
- name;
- legacy feature/spec ID;
- purpose;
- owning modules;
- important entry points;
- implementation status;
- shipped status;
- default state;
- actual runtime reachability;
- required consent;
- required user configuration;
- required administrative configuration;
- required build-time configuration;
- dependencies;
- persisted state;
- external dependencies;
- known limitations;
- evidence.

Distinguish carefully between:

`implemented`

and:

`reachable/active in production`.

Code presence alone is not proof of product availability.

## 4. Discover runtime and execution topology

Find actual runtime entry points, execution contexts, processes, workers, deployable units, storage surfaces, and external systems.

Identify where applicable:

- UI applications;
- browser/client contexts;
- backend/API processes;
- service workers;
- background jobs;
- content scripts;
- privileged execution worlds;
- admin/internal applications;
- databases;
- caches;
- queues;
- local storage;
- synchronized storage;
- external APIs;
- browser/platform APIs;
- network transports;
- AI/model providers;
- build-time configuration;
- deployment-time configuration.

Do not infer a separate runtime from a directory name.

Prefer actual execution boundaries over conventional frontend/backend terminology.

If there is no server backend, state that explicitly.

## 5. Map responsibilities and ownership

Identify where important responsibilities actually live.

Inspect responsibilities such as:

- UI;
- navigation;
- user state;
- identity;
- authentication;
- authorization;
- consent;
- personalization/configuration;
- runtime execution;
- orchestration;
- administrative operations;
- persistence;
- synchronization;
- migration;
- compatibility;
- integration;
- telemetry;
- validation;
- lifecycle;
- reset/deletion;
- trust checks.

Distinguish where relevant:

- implements;
- reads;
- owns;
- authoritatively mutates;
- coordinates;
- persists;
- replicates;
- validates.

Do not confuse a reader or wrapper with the authoritative owner.

Flag unclear, competing, or duplicated ownership.

## 6. Build the capability dependency and ownership graph

Map meaningful cross-capability dependencies.

Consider:

- semantic dependency;
- contract dependency;
- runtime invocation;
- state ownership;
- lifecycle dependency;
- composition dependency;
- event/outcome dependency;
- persistence dependency;
- external integration dependency.

Distinguish:

`A uses B`

from:

`A owns state consumed by B`

from:

`A controls B's lifecycle`

from:

`A emits information observed by B`.

Do not reduce the architectural graph to import relationships alone.

## 7. Map communication and trust boundaries

Identify significant communication surfaces such as:

- runtime messages;
- HTTP;
- RPC;
- events;
- storage;
- DOM interaction;
- cross-world execution;
- external-site interaction;
- queues or files.

For each important boundary determine:

- sender;
- receiver;
- data crossing;
- validation;
- authorization;
- trust assumptions;
- failure behavior;
- persistence implications.

Identify where untrusted information becomes validated, authorized, normalized, trusted, or persisted.

Do not treat hidden UI as authorization.

Do not treat process locality as trust.

## 8. Separate identity, authentication, authorization, authority, and consent

Treat these as distinct concepts.

Determine where applicable:

### Identity
How users, installations, sessions, devices, or actors are identified.

### Authentication
Where identity is verified.

If authentication does not exist, say so.

### Authorization
Where permission to perform an operation is enforced.

### Authority
Which component or persisted state is authoritative for an important decision or data category.

### Consent
Which optional behaviors require explicit user consent and where consent is stored/enforced.

Do not merge these concepts unless the implementation actually does.

## 9. Build the persistent-data and lifecycle catalog

Identify important persisted state.

For each important state category determine where possible:

- name;
- owner;
- storage technology;
- key/namespace;
- schema/version;
- personal or non-personal;
- authoritative, derived, or cache;
- readers;
- writers;
- retention;
- reset behavior;
- full-deletion behavior;
- synchronization;
- recovery;
- anti-resurrection behavior;
- migration;
- compatibility requirements.

Flag:

- multiple writers;
- unclear ownership;
- duplicated authority;
- inconsistent reset/deletion;
- replication without clear reconciliation;
- persistence outside deletion lifecycle.

## 10. Build the configuration and deployment matrix

Identify conditions that alter actual product behavior or capability reachability.

Distinguish:

- source constants;
- build-time configuration;
- manifest/permission configuration;
- deployment configuration;
- installation state;
- administrative configuration;
- user configuration;
- consent;
- runtime-derived state;
- external availability.

For important capabilities record what must be true for them to become active.

Pay special attention when configuration controls:

- feature enablement;
- supported routes;
- network access;
- host permissions;
- privacy behavior;
- telemetry;
- compatibility;
- external integrations.

## 11. Map compatibility and versioning

Identify relevant:

- persisted schema versions;
- config versions;
- migration registries;
- compatibility tuples;
- synchronization protocols;
- import/export formats;
- external integration assumptions.

Determine:

- what compatibility is checked;
- available migration paths;
- declared but missing migration paths;
- behavior on incompatibility;
- whether compatibility is exact, ranged, migratable, or unknown.

Do not infer functioning migration support merely from the existence of migration abstractions.

## 12. Map external integrations

For each significant external integration record:

- purpose;
- owning capability;
- protocol/surface;
- trust level;
- authentication if any;
- data sent;
- data received;
- reliability assumptions;
- volatility;
- failure behavior;
- available verification evidence.

Distinguish deterministic fixtures from evidence of current compatibility with a live external system.

## 13. Map critical runtime flows

Document only the flows needed to understand system architecture.

Prefer flows exposing:

- cross-capability coordination;
- authority;
- trust transitions;
- persistence;
- external integration;
- lifecycle;
- important failure behavior.

Use the conceptual form:

Actor  
→ entry point  
→ capabilities/components  
→ communication boundary  
→ state read/written  
→ external system if any  
→ result

Do not document every code path.

## 14. Map test topology

Identify relevant verification categories such as:

- contract;
- unit;
- integration;
- property;
- end-to-end;
- benchmark;
- smoke;
- external compatibility;
- manual/runtime evidence.

Distinguish:

- test exists;
- historical record says it passed;
- test was freshly executed during this run.

Do not interpret test existence as proof that it currently passes.

Do not run tests or builds merely to populate the map unless the user explicitly requested fresh verification or existing evidence is insufficient for a material architectural conclusion.

If tests/build were not run, record that explicitly.

## 15. Map evidence topology and freshness

Classify important evidence where useful as:

- `CODE`
- `TEST`
- `CONTRACT`
- `SPEC`
- `PRD`
- `CONFIG`
- `RUNTIME`
- `EXTERNAL`
- `HISTORICAL`

Also classify status where relevant:

- current;
- physically present;
- historical;
- recorded-only;
- missing;
- fixture-only;
- externally verified;
- stale;
- conflicting.

Do not treat a historical checkbox or execution record as fresh verification.

Do not treat a referenced artifact as physically available when the file is absent.

## 16. Record structural observations

Record evidence-backed architectural characteristics such as:

- layer crossing;
- cross-feature coupling;
- central composition;
- responsibility mixing;
- process coupling;
- shared infrastructure;
- public/internal leakage;
- deployment coupling;
- trust-boundary placement;
- ownership concentration.

Use:

Observation  
→ Evidence  
→ Architectural meaning

Do not prescribe redesign.

## 17. Identify behavior/spec/architecture gaps

Compare when relevant:

- product requirements;
- OpenSpec specs;
- legacy specs;
- contracts;
- configuration;
- implementation;
- runtime composition;
- tests;
- runtime/external evidence;
- documentation.

Classify significant discrepancies as:

### VERIFIED CURRENT GAP
Repository evidence demonstrates a real discrepancy in current behavior or composition.

### INTENDED BUT NOT IMPLEMENTED
A sufficiently authoritative requirement exists, but current production behavior does not realize it.

### IMPLEMENTED BUT UNDER-DOCUMENTED
Current implementation exists, but current authoritative documentation does not reflect it.

### STALE OR HISTORICAL DOCUMENTATION
Documentation describes an older state and should not be treated as current system truth.

### EVIDENCE GAP
A claim exists but its required evidence is missing or stale.

### UNCERTAIN
Available evidence is insufficient or conflicting.

Never silently resolve disagreement in favor of code or documentation.

Do not fix gaps in this skill.

## 18. Record unknowns and confidence

For unresolved important questions record:

- the question;
- why it matters;
- evidence inspected;
- missing evidence;
- confidence.

Use:

- High;
- Medium;
- Low.

Confidence reflects evidence quality, not model certainty.

Do not guess to make the map look complete.

## 19. Write or refresh the persistent map

Write:

`openspec/system/brownfield-map.md`

If it already exists:

1. read it completely;
2. preserve still-valid verified information;
3. re-check sections affected by repository changes;
4. update stale claims;
5. update snapshot metadata;
6. preserve unresolved uncertainty unless evidence resolves it;
7. remove claims only when evidence establishes that they are obsolete or incorrect;
8. preserve stable semantic capability IDs when possible.

A refresh is not a blind rewrite.

# Required output structure

Use exactly these top-level sections:

# Brownfield System Map

## Snapshot

## System Identity and Scope

## Source Authority and Freshness

## Capability Baseline

## Runtime and Execution Topology

## Capability Dependencies and Ownership

## Major Responsibilities

## Process and Message Boundaries

## Trust Boundaries

## Identity, Authentication, Authorization, Authority, and Consent

## Persistent Data and Lifecycle

## Configuration and Deployment Matrix

## Compatibility and Versioning

## External Integrations

## Critical Runtime Flows

## Test Topology

## Evidence Topology and Freshness

## Documentation Authority and Freshness

## Structural Observations

## Known Behavior / Spec / Architecture Gaps

## Unknowns

## Confidence

## Evidence Map

Use plain ASCII diagrams where diagrams materially improve understanding.

# Evidence Map format

For architecturally significant claims prefer:

### EVID-XXX — <short claim name>

**Claim:**  
<claim>

**Evidence:**

- `CODE` — `<path>` — `<symbol or relevant area>`
- `TEST` — `<path>`
- `CONFIG` — `<path>`
- `SPEC` — `<path>`

Include only applicable evidence types.

**Evidence status:**  
<current / historical / recorded-only / missing / fixture-only / externally verified / conflicting>

**Meaning:**  
<what the evidence establishes>

**Confidence:**  
<High / Medium / Low>

Do not create evidence entries for trivial facts.

# Boundary handling

The map may record observed:

- ownership boundaries;
- authority boundaries;
- data boundaries;
- process boundaries;
- trust boundaries;
- lifecycle boundaries;
- storage boundaries;
- integration boundaries.

Do not decide here that these must remain invariant.

If an observed boundary appears intentionally normative, identify the supporting evidence and mark it as a candidate for later `product-boundaries` work.

Do not create or modify `product-boundaries.md`.

# OpenSpec awareness

Inspect relevant OpenSpec state when present.

Treat OpenSpec main specs as an important source, not proof of runtime parity.

If OpenSpec artifacts disagree with current implementation, record the disagreement.

Do not create an OpenSpec change merely to represent a discovered discrepancy.

# Legacy specification awareness

Legacy SpecKit, ADR, RFC, design, research, task, and similar artifacts may contain valuable requirements and rationale.

Use them according to their authority and freshness.

Do not bulk-convert legacy specs into OpenSpec main specs.

Do not rewrite legacy documentation.

Brownfield mapping and capability-spec reconciliation are separate operations.

# Write boundary

This skill may write only:

`openspec/system/brownfield-map.md`

and may create its parent directory.

Do not modify any other repository file.

If inspection reveals defects, stale documentation, missing requirements, or architecture problems, record them in the map and stop.

# Completion criteria

Before finishing verify that:

- repository snapshot is identified;
- important sources and their freshness are understood;
- major capabilities are identified;
- runtime reachability is distinguished from code presence;
- execution/runtime topology is mapped;
- responsibilities and ownership are mapped;
- important capability dependencies are mapped;
- communication and trust boundaries are understood;
- identity/authentication/authorization/authority/consent are distinguished;
- important persisted state and lifecycle semantics are mapped;
- capability-enabling configuration is identified;
- compatibility/versioning behavior is mapped;
- significant external integrations are identified;
- critical runtime flows are mapped;
- test topology is described;
- recorded evidence is distinguished from fresh verification;
- missing/stale evidence is identified;
- documentation drift is recorded;
- significant code/spec/runtime disagreements are preserved rather than silently resolved;
- important claims have repository evidence;
- uncertainty is explicit;
- target architecture has not been introduced;
- no OpenSpec change was created;
- no implementation file was modified.

If any criterion cannot be satisfied, state exactly what remains unknown instead of guessing.

# Final response

After writing or refreshing the map, report only:

1. path of the map;
2. repository snapshot;
3. capabilities identified;
4. major runtime/architectural boundaries identified;
5. significant verified gaps;
6. important evidence limitations;
7. whether the map is sufficiently complete to serve as the persistent brownfield baseline for future OpenSpec planning.

Do not proceed automatically to:

- product-boundaries;
- OpenSpec main-spec reconciliation;
- proposal creation;
- implementation.

Stop after completing `openspec/system/brownfield-map.md`.
