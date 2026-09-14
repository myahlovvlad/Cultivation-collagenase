# Codex Execution Context — ResearchOS Core Phase 1

Date: 2026-09-14  
Repository: `myahlovvlad/Cultivation-collagenase`  
Execution branch: `feat/researchos-core-foundation`

## Mission

Implement **Phase 1 — ResearchOS Core Foundation** using Superpowers Subagent-Driven Development.

The goal is a standalone, domain-independent Python package that provides:

- Research Workspace and canonical Research Cycle entities;
- provenance, versioning, approvals and append-only hash-chained audit;
- immutable/versioned ELN;
- basic relational Knowledge Graph;
- policy engine;
- Domain Pack SDK/registry shell;
- REST contracts;
- architecture tests proving the core has no BioTech dependency.

Do not implement BioTech functionality in this phase.

## Source of truth

Read these files in this order:

1. `docs/superpowers/specs/2026-09-14-researchos-core-biotech-biocult-super-design.md`
2. `docs/superpowers/plans/2026-09-14-researchos-core-foundation.md`
3. this execution context

Authority order:

`approved design spec > Phase 1 implementation plan > this file > existing repository code`

The older `2026-09-12-biocult-super-v3-*` spec/plan described the previous in-place `super_core` design and is superseded for Phase 1 by the 2026-09-14 ResearchOS documents.

## Required workflow

Use these Superpowers skills in this order:

1. `using-git-worktrees`
2. `subagent-driven-development`
3. per-task TDD from the implementation plan
4. `requesting-code-review` for the final whole-branch review
5. `verification-before-completion`
6. `finishing-a-development-branch`

Use a fresh implementer subagent per plan task and a separate task reviewer after every task. Do not skip task review. Follow the five-round fix-loop cap defined by `subagent-driven-development`.

Do not execute multiple implementation subagents in parallel because the tasks are sequentially dependent.

## Isolated workspace

Do not implement directly in an unrelated existing checkout.

First verify whether Codex is already in an isolated worktree. If not, create one for `feat/researchos-core-foundation` following `using-git-worktrees`.

Before Task 1:

- confirm clean git status;
- install existing project dependencies only as necessary for baseline verification;
- run the existing repository test suite that is practical in the environment;
- record any pre-existing failures before making implementation changes;
- initialize the SDD ledger for `docs/superpowers/plans/2026-09-14-researchos-core-foundation.md`.

## Binding architecture boundaries

`ResearchOS Core` must remain independent of the existing BioCult implementation.

Forbidden imports from `researchos/core/**` include at minimum:

- `BioCult-KB_Aspergillus_sydowii`
- `web_app`
- `researchos.domain_packs`
- COBRA / SBML / Biopython domain libraries
- OMICS-specific modules
- chromatography, bioreactor, scale-up and material-balance code

Do not create a BioTech Domain Pack in Phase 1. Use only an in-test fake Domain Pack when testing the SDK/registry.

Do not migrate or rewrite existing BioCult computational modules in Phase 1.

## Scientific integrity invariants

Preserve explicit source classes such as:

- `OBSERVED`
- `MEASURED`
- `MANUAL`
- `IMPORTED`
- `CALCULATED`
- `MODEL_PREDICTED`
- `RULE_INFERRED`
- `AI_INFERRED`
- `EXPERT_APPROVED`
- `REJECTED`

Never coerce `AI_INFERRED` or `MODEL_PREDICTED` into measured/observed evidence.

Canonical principle:

> AI proposes. Human approves. System records.

Phase 1 does not need a full agent runtime, but its provenance, policy and approval models must preserve that boundary for later phases.

## Persistence rules

Foundation persistence is SQLAlchemy 2 + SQLite.

Requirements:

- use SQLite foreign-key enforcement (`PRAGMA foreign_keys=ON`);
- in-memory API tests must use a shared SQLite connection strategy appropriate for TestClient;
- audit records and approval records are append-only/immutable;
- audit records form a verifiable hash chain;
- signed/locked ELN versions are immutable;
- corrections to immutable ELN content create a new version or amendment rather than mutating history.

Do not add PostgreSQL, Neo4j, Redis, Celery, Kafka or a vector database in Phase 1.

## Task execution

The implementation plan contains 9 tasks. Execute them strictly in order:

1. Bootstrap standalone package and dependency guard.
2. Persistence, source enums, provenance, versioning and append-only audit.
3. Canonical Research Cycle.
4. Immutable/versioned ELN.
5. Basic Knowledge Graph.
6. Policy Engine.
7. Domain Pack SDK and registry shell.
8. FastAPI REST contracts.
9. Phase 1 acceptance, CI and documentation.

For every task:

- extract/use the complete task brief from the plan;
- write the failing test first;
- verify the expected failure;
- implement the minimum required code;
- run the focused tests;
- run any relevant previously passing ResearchOS Core tests;
- commit;
- produce the implementer report;
- dispatch an independent task reviewer;
- resolve Important/Critical findings through the SDD fix loop before continuing.

Do not widen scope to Phase 2 even if interfaces make later work obvious.

## Completion gate

Phase 1 is complete only when all of the following are demonstrated by tests:

1. `researchos.core` runs without BioTech installed.
2. Core contains no legacy/BioTech imports.
3. Research Cycle can be persisted and traversed through its service/API contracts.
4. provenance preserves the distinction between measured, calculated, model-predicted and AI-inferred records.
5. audit integrity can be verified and audit/approval records cannot be mutated after persistence.
6. ELN signed/locked versions cannot be edited.
7. ELN correction creates a new version/amendment without destroying history.
8. Knowledge relations store provenance/confidence/version information and support bounded traversal.
9. Policy decisions return explicit `ALLOW`, `REQUIRE_APPROVAL` or `DENY` outcomes.
10. a fake Domain Pack can register through the public SDK while zero Domain Packs remains a valid configuration.
11. generic REST endpoints work against an isolated ResearchOS Core database.
12. the complete Phase 1 ResearchOS test suite passes.

## Final review

After all 9 task reviews are clean, run a broad whole-branch code review against the branch base. The final reviewer must explicitly inspect:

- domain-boundary leakage;
- mutability holes in audit/approval/ELN;
- source-type confusion;
- missing foreign-key constraints;
- service/API bypasses around policy or governance boundaries;
- accidental dependencies on legacy BioCult code;
- test gaps around the Phase 1 acceptance criteria.

Do not merge automatically. Finish with the `finishing-a-development-branch` workflow and present integration options to the human owner.