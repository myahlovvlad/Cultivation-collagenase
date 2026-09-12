# Codex Execution Context — BioCult SUPER v3

Date: 2026-09-12  
Repository: `myahlovvlad/Cultivation-collagenase`  
Execution branch: `design/biocult-super-v3`  
Current PR: #1 `docs: define BioCult SUPER v3 architecture`

## 1. Mission

Implement the approved BioCult SUPER v3 foundation as an incremental extension of the existing Cultivation-collagenase project.

BioCult SUPER is an AI-native multiscale research orchestration platform for biotechnology. It connects scientific objectives, hypotheses, experiments, evidence, computational models, expert reasoning, external scientific tools, and human approval into one traceable research cycle.

Canonical product principle:

> AI proposes. Human approves. System records.

AI may read context, interpret evidence, propose hypotheses, propose experiments, run allowed computations, and prepare scientific interpretations. AI must not directly mutate canonical hypotheses, protocols, experimental results, or evidence without explicit human approval.

## 2. Source of truth

Before implementation, read these files in this order:

1. `docs/superpowers/specs/2026-09-12-biocult-super-v3-design.md`
2. `docs/superpowers/plans/2026-09-12-biocult-super-v3-foundation.md`
3. this file
4. `README.md`
5. `BioCult-KB_Aspergillus_sydowii/README.md`
6. `BioCult-KB_Aspergillus_sydowii/web_app/README.md`

Authority order when requirements conflict:

`approved design spec > implementation plan > this execution context > existing documentation > implementation assumptions`

Do not silently reinterpret the design. If the plan and code disagree, preserve backward compatibility unless the spec explicitly requires otherwise.

## 3. Product vision to preserve

Do not reduce the project to a digital twin, ELN, LIMS, chatbot, or dashboard.

The product is an integrated scientific research environment built around this loop:

```text
Research Program
  -> Research Objective
  -> Research Question
  -> Hypothesis
  -> Experiment Design / DoE
  -> Protocol
  -> Experiment Run
  -> Observations / Measurements / Files
  -> Evidence
  -> Computational Analysis
  -> Expert / AI Interpretation
  -> Critique / Falsification
  -> Proposal
  -> Human Approval
  -> Decision
  -> Next Hypothesis / Next Experiment
```

The current Aspergillus sydowii collagenase project is the first reference vertical, not the architectural limit of the platform.

## 4. Scientific architecture

The long-term platform links four scientific scales:

1. quantum / chemical;
2. molecular-genetic;
3. cellular;
4. bioprocess / bioreactor.

The foundation does not implement all scientific solvers internally. Specialized engines are external providers accessed through the Scientific Tool Gateway.

Examples of future providers:

- bioinformatics: Galaxy and workflow engines;
- quantum chemistry / molecular modelling: ORCA, Psi4, docking / MD providers;
- cellular modelling: COBRApy, FBA, dFBA;
- multiphysics / reactor: OpenFOAM-like or COMSOL-like providers;
- CAD / geometry: FreeCAD-like or external CAD APIs;
- analytics: Python, R, statistics, DoE, optimization.

Cross-scale data exchange must be explicit and provenance-aware. Do not introduce implicit coupling between scientific domains.

## 5. Existing code that must remain working

The repository already has working or partially working modules for:

- `Strain`, `Medium`, `Bioreactor`, `BatchRun`, `Observation`;
- audit records;
- culture-fluid state;
- transcriptome datasets;
- dFBA runs;
- DoE designs;
- scaling predictions;
- GEM / COBRA modelling;
- process simulation;
- system biology;
- expert-system concepts;
- FastAPI backend;
- SQLite persistence;
- automated tests.

Foundation work must be additive. Do not rewrite legacy `web_app/models.py`, `web_app/schemas.py`, `gem_cobra.py`, `process_simulation.py`, or `system_biology.py` unless the approved plan explicitly says so.

## 6. Locked foundation package

Create the v3 foundation under:

```text
BioCult-KB_Aspergillus_sydowii/web_app/super_core/
```

Expected structure:

```text
super_core/
  __init__.py
  enums.py
  models.py
  schemas.py
  repository.py
  research_service.py
  graph_service.py
  proposal_service.py
  tool_gateway.py
  connector_registry.py
  context_service.py
  routers/
    __init__.py
    research.py
    knowledge.py
    proposals.py
    tools.py
    context.py
```

Tests belong under `BioCult-KB_Aspergillus_sydowii/tests/` and are specified in the implementation plan.

## 7. System-of-record boundary

For the foundation phase:

- SQLAlchemy + SQLite remain the persistence backend;
- a relational edge table implements the first knowledge-graph projection;
- datasets/artifacts remain logically separate from graph relations and ELN narrative;
- no PostgreSQL, Neo4j, Celery, Kafka, or frontend-framework migration in this phase;
- MCP is initially a stable service/API facade, not a requirement to introduce a full transport stack immediately.

The later target architecture may use PostgreSQL, a graph database/projection layer, object storage, Git projections, and native MCP transport, but these are outside the foundation scope.

## 8. Canonical provenance classes

Every scientifically significant assertion must have explicit origin. Preserve these evidence classes exactly:

```text
OBSERVED
MANUAL
IMPORTED
CALCULATED
MODEL_PREDICTED
RULE_INFERRED
AI_INFERRED
EXPERT_APPROVED
REJECTED
```

Never display `AI_INFERRED` or `MODEL_PREDICTED` as if it were an observed fact.

Every scientific relation must be able to retain source/provenance, confidence, version, and timestamp information.

## 9. Human-in-the-loop proposal boundary

This is a load-bearing requirement.

Allowed AI flow:

```text
AI analysis
 -> Proposal
 -> PENDING_HUMAN_REVIEW
 -> APPROVED / REJECTED / REVISION_REQUESTED
 -> COMMITTED only after approval
```

Required proposal states:

```text
DRAFT
PENDING_HUMAN_REVIEW
APPROVED
REJECTED
REVISION_REQUESTED
COMMITTED
```

There must be no AI-facing function equivalent to:

```text
update_hypothesis_directly()
overwrite_protocol()
change_experiment_result()
delete_evidence()
```

Canonical mutation from an AI-originated action must pass through the proposal service and approval record.

## 10. Knowledge graph role

The graph is a semantic projection and context-retrieval layer, not a replacement for experimental storage.

Representative relations:

```text
Producer --PRODUCES--> Product
Gene --ENCODES--> Protein
Protein --CATALYZES--> Reaction
Reaction --PART_OF--> Pathway
Experiment --TESTS--> Hypothesis
Measurement --GENERATED_BY--> Experiment
Evidence --SUPPORTS--> Hypothesis
Evidence --CONTRADICTS--> Hypothesis
Prediction --GENERATED_BY--> ModelRun
Proposal --BASED_ON--> Evidence
Decision --RESOLVES--> Proposal
```

The first implementation uses `ScientificRelation` rows and bounded traversal. Do not add a graph database during the foundation phase.

## 11. Scientific Tool Gateway

The gateway separates research-domain logic from vendor-specific computation.

Target provider contract:

```text
capabilities()
describe_tool()
input_schema()
validate_input()
submit_job()
job_status()
cancel_job()
get_result()
get_logs()
get_provenance()
```

Existing GEM/process modules should become initial providers or adapters where the plan requires this, not be rewritten into the gateway.

The research domain must not import Galaxy, ORCA, FreeCAD, OpenFOAM, COMSOL, LIMS, or other vendor-specific clients directly.

## 12. Connector framework

Use a generic plugin registry. Concrete integrations come later.

Connector categories include:

```text
REST / OpenAPI
MCP
Filesystem
CSV / XLSX
Database
Git
LIMS
ELN
ERP
Instrument
Scientific API
```

A connector should expose at least:

```text
capabilities
configuration schema
authentication requirements
read/write permissions
data mapping
health check
provenance behavior
```

Foundation reference connectors should stay minimal. Do not attempt to implement all future systems in this plan.

## 13. Codex / MCP-facing context

Codex must operate against a stable scientific context facade, not by directly mutating SQLAlchemy tables.

Expected read capabilities include concepts equivalent to:

```text
get_research_program()
get_active_objectives()
get_active_hypotheses()
get_experiment(id)
get_experimental_data(query)
query_knowledge_graph(query)
trace_cross_scale_dependency(source, target)
list_available_tools(domain)
describe_tool(tool)
get_computation_status(run_id)
get_result(run_id)
```

Expected proposal capabilities include:

```text
create_proposal(...)
propose_hypothesis(...)
propose_experiment(...)
propose_interpretation(...)
propose_model_change(...)
get_pending_proposals()
```

Execution tools may trigger computations, but computation output is not automatically canonical scientific truth.

## 14. Development protocol

Use subagent-driven development for the foundation implementation.

Execution rules:

1. Work in an isolated git worktree created from `design/biocult-super-v3` or from a dedicated implementation branch based on it. Never implement directly on `main`.
2. Read the full design spec and implementation plan before Task 1.
3. Create the SDD progress ledger for this plan and use it as the recovery source of truth.
4. Execute tasks in plan order.
5. For each task:
   - dispatch a fresh implementer context;
   - implement tests first where specified;
   - run the focused tests;
   - self-review;
   - commit;
   - run a separate task review for spec compliance and code quality;
   - fix findings before moving to the next task.
6. After all tasks, run a whole-branch review and full regression suite.
7. Do not merge PR #1 or implementation PRs automatically. Leave final merge to the human.

If the local environment provides the `superpowers` skills, use:

```text
superpowers:using-git-worktrees
superpowers:subagent-driven-development
superpowers:verification-before-completion
superpowers:requesting-code-review
superpowers:finishing-a-development-branch
```

## 15. Scope discipline

During this foundation phase, do NOT expand into:

- full native MCP transport if the stable facade is sufficient;
- production Galaxy integration;
- production LIMS integration;
- production CAD / CFD / QM integrations;
- PostgreSQL migration;
- Neo4j or another graph DB;
- complete GxP validation package;
- complete ELN product;
- autonomous AI control of experiments;
- autonomous modification of canonical scientific records;
- new frontend framework;
- broad redesign of existing biological models.

Those are follow-on plans after the foundation proves the contracts.

## 16. First vertical acceptance scenario

The foundation is successful when the project can demonstrate one traceable `Aspergillus sydowii` collagenase research cycle:

```text
ResearchProgram
 -> ResearchObjective
 -> Hypothesis
 -> Experiment linked to legacy cultivation/batch context
 -> Evidence
 -> Knowledge relations
 -> Computational result through Tool Gateway
 -> AI interpretation/proposal
 -> PENDING_HUMAN_REVIEW
 -> explicit human approval
 -> canonical commit
 -> context projection available to Codex/API
```

The demonstration must prove that observed data, model prediction, AI inference, and human-approved knowledge remain distinguishable.

## 17. Required verification

At minimum, before claiming the foundation complete:

```bash
cd BioCult-KB_Aspergillus_sydowii
python -m pytest tests/test_super_research_core.py -q
python -m pytest tests/test_super_knowledge_graph.py -q
python -m pytest tests/test_super_proposals.py -q
python -m pytest tests/test_super_tool_gateway.py -q
python -m pytest tests/test_super_connector_registry.py -q
python -m pytest tests/test_super_context_api.py -q
python -m pytest tests/test_super_reference_use_case.py -q
python -m pytest tests -q
```

Also start the FastAPI app and verify that existing endpoints still work and the new SUPER routes do not break application startup.

Do not state `complete`, `production-ready`, `validated`, or `GxP-compliant` unless the evidence actually supports that claim.

## 18. Definition of done for Codex

A task is done only when:

- its specified tests pass;
- legacy behavior affected by the task still passes;
- implementation matches the approved spec;
- no direct AI-to-canonical-write bypass has been introduced;
- provenance is retained;
- code is committed with a focused commit;
- task review findings have been resolved or explicitly adjudicated.

The entire foundation is done only after the full suite and final branch review pass.

## 19. First action

Do not start by adding integrations or UI features.

Start with Task 1 from:

`docs/superpowers/plans/2026-09-12-biocult-super-v3-foundation.md`

Task 1 establishes the canonical research/provenance model that every later layer depends on.

Before editing, inspect the existing SQLAlchemy conventions in `web_app/models.py`, existing Pydantic conventions in `web_app/schemas.py`, database setup in `web_app/db.py`, and current tests. Preserve those conventions unless the approved design explicitly overrides them.
