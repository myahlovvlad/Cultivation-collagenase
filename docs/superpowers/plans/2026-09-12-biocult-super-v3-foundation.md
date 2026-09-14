# BioCult SUPER v3 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing Cultivation-collagenase prototype into the first working BioCult SUPER vertical slice: research goals and hypotheses, evidence-linked experiments, knowledge relations, AI proposals with mandatory human approval, a Scientific Tool Gateway, MCP-facing services, and a plugin connector framework.

**Architecture:** Keep the existing FastAPI/SQLAlchemy application and current biological/process modules intact. Add a new `super_core` package beside the legacy modules, expose its capabilities through FastAPI routers, and migrate the current Aspergillus/collagenase workflow into the new domain incrementally. PostgreSQL/graph-database replacement is deferred; the first slice uses SQLAlchemy plus a relational edge table so the behavior is testable before infrastructure expansion.

**Tech Stack:** Python 3, FastAPI, SQLAlchemy, Pydantic, pytest; existing COBRA/process modules remain computational providers. MCP is implemented initially as a stable service facade/API contract, with transport wiring isolated so a native MCP server can be added without changing domain services.

**Spec:** `docs/superpowers/specs/2026-09-12-biocult-super-v3-design.md`

## Global Constraints

- `AI proposes. Human approves. System records.`
- AI-facing code must not expose direct canonical mutations for hypotheses, protocols, experimental results, or evidence.
- Existing `Strain`, `Medium`, `Bioreactor`, `BatchRun`, `Observation`, process simulation, GEM and system-biology behavior must remain backward compatible during this foundation phase.
- Every scientific assertion that can affect a decision must carry provenance and an explicit evidence type.
- Keep ELN narrative, graph relations, and experimental numeric data logically separate even when SQLite is used as the initial persistence backend.
- External scientific engines are providers behind a stable gateway; vendor-specific calls must not enter research-domain services.
- The first reference vertical is `Aspergillus sydowii` collagenase cultivation.
- Do not introduce PostgreSQL, Neo4j, Celery, Kafka, or a new frontend framework in this foundation phase.

---

## File Structure Locked for This Phase

Create the following package under `BioCult-KB_Aspergillus_sydowii/web_app/`:

```text
super_core/
  __init__.py
  enums.py                 # provenance, proposal, relation and entity statuses
  models.py                # SQLAlchemy canonical entities for v3 foundation
  schemas.py               # Pydantic request/response contracts
  repository.py            # persistence-only queries/commands
  research_service.py      # objectives, hypotheses, experiments, evidence
  graph_service.py         # semantic relation operations and traversal
  proposal_service.py      # AI proposal lifecycle and approval boundary
  tool_gateway.py          # ToolProvider protocol, registry, job lifecycle
  connector_registry.py    # generic connector plugin contract/registry
  context_service.py       # AI-readable research context projection
  routers/
    __init__.py
    research.py
    knowledge.py
    proposals.py
    tools.py
    context.py
```

Add tests under:

```text
tests/
  test_super_research_core.py
  test_super_knowledge_graph.py
  test_super_proposals.py
  test_super_tool_gateway.py
  test_super_connector_registry.py
  test_super_context_api.py
  test_super_reference_use_case.py
```

Modify only these existing files in the foundation phase:

```text
web_app/main.py
web_app/db.py                 # only if test/session helpers are required
web_app/README.md
README.md
```

Do not split or rewrite legacy `web_app/models.py`, `schemas.py`, `gem_cobra.py`, `process_simulation.py`, or `system_biology.py` in this plan.

---

### Task 1: Define Canonical Research and Provenance Domain

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/__init__.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/enums.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/models.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/schemas.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_research_core.py`

**Interfaces:**
- Produces SQLAlchemy entities: `ResearchProgram`, `ResearchObjective`, `Hypothesis`, `Experiment`, `Evidence`, `ScientificRelation`, `Proposal`, `ApprovalRecord`, `ComputationRun`.
- Produces enums: `EvidenceKind`, `HypothesisStatus`, `ProposalStatus`, `RelationType`.
- Produces Pydantic contracts consumed by all later services.

- [ ] **Step 1: Write failing enum/schema tests**

```python
from web_app.super_core.enums import EvidenceKind, ProposalStatus
from web_app.super_core.schemas import HypothesisCreate, EvidenceCreate


def test_scientific_types_are_explicit():
    assert EvidenceKind.OBSERVED.value == "OBSERVED"
    assert EvidenceKind.AI_INFERRED.value == "AI_INFERRED"
    assert ProposalStatus.PENDING_HUMAN_REVIEW.value == "PENDING_HUMAN_REVIEW"


def test_hypothesis_and_evidence_contracts():
    hypothesis = HypothesisCreate(
        objective_id=1,
        statement="Oxygen transfer limits collagenase productivity",
        rationale="Observed DO decline precedes productivity loss",
    )
    evidence = EvidenceCreate(
        kind=EvidenceKind.OBSERVED,
        title="EXP-001 DO trajectory",
        source_reference="EXP-001",
        confidence=0.95,
    )
    assert hypothesis.objective_id == 1
    assert evidence.confidence == 0.95
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```bash
cd BioCult-KB_Aspergillus_sydowii
python -m pytest tests/test_super_research_core.py -q
```

Expected: import failure because `web_app.super_core` does not exist.

- [ ] **Step 3: Implement enums**

Create exact enum values:

```python
from enum import Enum


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    MANUAL = "MANUAL"
    IMPORTED = "IMPORTED"
    CALCULATED = "CALCULATED"
    MODEL_PREDICTED = "MODEL_PREDICTED"
    RULE_INFERRED = "RULE_INFERRED"
    AI_INFERRED = "AI_INFERRED"
    EXPERT_APPROVED = "EXPERT_APPROVED"
    REJECTED = "REJECTED"


class HypothesisStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_HUMAN_REVIEW = "PENDING_HUMAN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    COMMITTED = "COMMITTED"


class RelationType(str, Enum):
    TESTS = "TESTS"
    GENERATED_BY = "GENERATED_BY"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    USES = "USES"
    PRODUCES = "PRODUCES"
    ENCODES = "ENCODES"
    CATALYZES = "CATALYZES"
    PART_OF = "PART_OF"
    BASED_ON = "BASED_ON"
    RESOLVES = "RESOLVES"
    CONSTRAINS = "CONSTRAINS"
    DERIVED_FROM = "DERIVED_FROM"
```

- [ ] **Step 4: Implement focused SQLAlchemy models and Pydantic schemas**

`ResearchObjective` must contain `program_id`, `title`, `description`, `status`, `created_at`.

`Hypothesis` must contain `objective_id`, `statement`, `rationale`, `status`, `created_at`, `created_by`, `version`.

`Experiment` must contain `objective_id`, `title`, `protocol_text`, `status`, `started_at`, `completed_at`, `legacy_batch_id`.

`Evidence` must contain `kind`, `title`, `source_reference`, `confidence`, `payload_json`, `created_at`, `created_by`.

`ScientificRelation` must contain `source_type`, `source_id`, `relation_type`, `target_type`, `target_id`, `confidence`, `provenance_json`, `version`, `created_at`.

All JSON payload columns use `Text` in the foundation phase, matching current project conventions.

- [ ] **Step 5: Add database creation test**

```python
from sqlalchemy import create_engine, inspect
from web_app.super_core.models import SuperBase


def test_super_tables_can_be_created_in_sqlite():
    engine = create_engine("sqlite:///:memory:")
    SuperBase.metadata.create_all(engine)
    names = set(inspect(engine).get_table_names())
    assert {"research_programs", "research_objectives", "hypotheses", "experiments", "evidence", "scientific_relations", "proposals", "approval_records", "computation_runs"} <= names
```

- [ ] **Step 6: Run the focused test file**

Run:

```bash
python -m pytest tests/test_super_research_core.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core BioCult-KB_Aspergillus_sydowii/tests/test_super_research_core.py
git commit -m "feat: add BioCult SUPER research domain"
```

---

### Task 2: Implement Research Service and Evidence Linking

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/repository.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/research_service.py`
- Modify: `BioCult-KB_Aspergillus_sydowii/tests/test_super_research_core.py`

**Interfaces:**
- Produces `ResearchService.create_program`, `create_objective`, `create_hypothesis`, `create_experiment`, `create_evidence`, `link_evidence`.
- Later tasks consume persistent IDs and relation rows created here.

- [ ] **Step 1: Add failing service test**

```python
def test_research_cycle_can_link_evidence_to_hypothesis(super_session):
    service = ResearchService(super_session)
    program = service.create_program("Collagenase optimization")
    objective = service.create_objective(program.id, "Increase collagenolytic activity")
    hypothesis = service.create_hypothesis(
        objective.id,
        "Oxygen limitation reduces secretion",
        "DO decline appears before lower activity",
        created_by="researcher",
    )
    experiment = service.create_experiment(objective.id, "EXP-001", "Batch cultivation")
    evidence = service.create_evidence(
        kind=EvidenceKind.OBSERVED,
        title="DO profile",
        source_reference=f"experiment:{experiment.id}",
        confidence=0.9,
        created_by="researcher",
    )
    relation = service.link_evidence(evidence.id, hypothesis.id, RelationType.SUPPORTS, confidence=0.8)
    assert relation.relation_type == RelationType.SUPPORTS.value
```

- [ ] **Step 2: Run and verify failure**

Expected: `ResearchService` is missing.

- [ ] **Step 3: Implement repository methods**

Implement persistence-only methods: `add`, `get`, `list_by`, `commit`, `refresh`. Do not put scientific rules in `repository.py`.

- [ ] **Step 4: Implement `ResearchService`**

Rules enforced by the service:

```python
if not 0.0 <= confidence <= 1.0:
    raise ValueError("confidence must be between 0 and 1")
```

`link_evidence()` must create a `ScientificRelation` from `Evidence` to `Hypothesis`; it must reject relation types other than `SUPPORTS` and `CONTRADICTS` for this method.

- [ ] **Step 5: Run research-core tests**

Run:

```bash
python -m pytest tests/test_super_research_core.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/repository.py BioCult-KB_Aspergillus_sydowii/web_app/super_core/research_service.py BioCult-KB_Aspergillus_sydowii/tests/test_super_research_core.py
git commit -m "feat: add research cycle service"
```

---

### Task 3: Add Knowledge Graph Projection and Traversal

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/graph_service.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_knowledge_graph.py`

**Interfaces:**
- Consumes `ScientificRelation` from Task 1.
- Produces `GraphService.add_relation`, `neighbors`, `trace_path`, `evidence_for_hypothesis`.

- [ ] **Step 1: Write failing graph traversal test**

```python
def test_graph_traces_experiment_to_hypothesis(super_session, seeded_research_cycle):
    graph = GraphService(super_session)
    path = graph.trace_path(
        source_type="Experiment",
        source_id=seeded_research_cycle.experiment_id,
        target_type="Hypothesis",
        target_id=seeded_research_cycle.hypothesis_id,
        max_depth=4,
    )
    assert [edge.relation_type for edge in path] == ["GENERATED_BY", "SUPPORTS"]
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/test_super_knowledge_graph.py -q
```

Expected: `GraphService` missing.

- [ ] **Step 3: Implement graph operations over the relation table**

Use breadth-first search over `ScientificRelation`; enforce `max_depth <= 8` and return an empty list when no path exists. No graph database dependency is introduced.

- [ ] **Step 4: Add provenance-preservation test**

```python
def test_graph_relation_preserves_provenance(super_session):
    graph = GraphService(super_session)
    edge = graph.add_relation(
        "Gene", 10, RelationType.ENCODES, "Protein", 12,
        confidence=0.98,
        provenance={"source": "NCBI", "accession": "ABC123"},
    )
    assert "ABC123" in edge.provenance_json
```

- [ ] **Step 5: Run graph tests and commit**

```bash
python -m pytest tests/test_super_knowledge_graph.py -q
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/graph_service.py BioCult-KB_Aspergillus_sydowii/tests/test_super_knowledge_graph.py
git commit -m "feat: add scientific knowledge graph projection"
```

---

### Task 4: Enforce AI Proposal → Human Approval → Commit Boundary

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/proposal_service.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_proposals.py`

**Interfaces:**
- Produces `ProposalService.create`, `submit_for_review`, `approve`, `reject`, `request_revision`, `commit_approved`.
- `commit_approved` is the only AI-originated route that can materialize a supported canonical change.

- [ ] **Step 1: Write failing approval-boundary tests**

```python
def test_ai_proposal_cannot_commit_before_human_approval(super_session):
    service = ProposalService(super_session)
    proposal = service.create_new_hypothesis_proposal(
        objective_id=1,
        statement="Oxygen limitation reduces collagenase secretion",
        rationale="DO decline observed",
        evidence_ids=[1],
        confidence=0.64,
        created_by="ai:codex",
    )
    service.submit_for_review(proposal.id)
    with pytest.raises(PermissionError, match="human approval required"):
        service.commit_approved(proposal.id)


def test_human_approval_allows_single_commit(super_session):
    service = ProposalService(super_session)
    proposal = make_pending_hypothesis_proposal(service)
    service.approve(proposal.id, reviewer="researcher", reason="Run confirmatory experiment")
    hypothesis = service.commit_approved(proposal.id)
    assert hypothesis.statement == proposal_statement()
    with pytest.raises(ValueError, match="already committed"):
        service.commit_approved(proposal.id)
```

- [ ] **Step 2: Run tests and verify failure**

Expected: service missing.

- [ ] **Step 3: Implement state machine**

Allowed transitions:

```text
DRAFT -> PENDING_HUMAN_REVIEW
PENDING_HUMAN_REVIEW -> APPROVED
PENDING_HUMAN_REVIEW -> REJECTED
PENDING_HUMAN_REVIEW -> REVISION_REQUESTED
REVISION_REQUESTED -> DRAFT
APPROVED -> COMMITTED
```

Any other transition raises `ValueError`.

- [ ] **Step 4: Require a human reviewer for approval**

`approve()` must reject reviewer identifiers beginning with `ai:` or equal to `system`.

- [ ] **Step 5: Run proposal tests and commit**

```bash
python -m pytest tests/test_super_proposals.py -q
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/proposal_service.py BioCult-KB_Aspergillus_sydowii/tests/test_super_proposals.py
git commit -m "feat: enforce human approval for AI proposals"
```

---

### Task 5: Add Scientific Tool Gateway and Legacy Computational Providers

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/tool_gateway.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_tool_gateway.py`

**Interfaces:**
- Produces `ToolProvider` protocol and `ScientificToolGateway`.
- Registers foundation providers for existing local capabilities, without rewriting their internals.

- [ ] **Step 1: Write failing provider-registry test**

```python
def test_gateway_lists_and_executes_registered_provider():
    gateway = ScientificToolGateway()
    gateway.register(EchoProvider())
    assert gateway.capabilities("test.echo") == ["echo"]
    run = gateway.submit_job("test.echo", "echo", {"value": 42})
    assert run.status == "SUCCEEDED"
    assert run.result == {"value": 42}
```

- [ ] **Step 2: Define the provider protocol**

```python
class ToolProvider(Protocol):
    provider_id: str

    def capabilities(self) -> list[str]: ...
    def describe_tool(self, capability: str) -> dict: ...
    def validate_input(self, capability: str, payload: dict) -> None: ...
    def submit_job(self, capability: str, payload: dict) -> "ToolJobResult": ...
    def get_provenance(self) -> dict: ...
```

- [ ] **Step 3: Implement registry and synchronous job execution**

Foundation jobs may execute synchronously, but the return object must include `run_id`, `provider_id`, `capability`, `status`, `result`, `error`, `provenance` so asynchronous providers can be introduced later without changing callers.

- [ ] **Step 4: Add adapters around existing functions**

Register only wrappers that can be implemented without changing legacy modules:

```text
local.gem            -> existing GEM/FBA entry point
local.process        -> existing process simulation entry point
local.system_biology -> existing system biology evaluation entry point
```

If an existing function signature is not stable enough for a direct wrapper, add a provider-local adapter in `tool_gateway.py`; do not modify the legacy computation code in this task.

- [ ] **Step 5: Add provenance test**

Every provider result must contain at minimum:

```python
assert {"provider_id", "software_component", "input_hash"} <= result.provenance.keys()
```

- [ ] **Step 6: Run tests and commit**

```bash
python -m pytest tests/test_super_tool_gateway.py tests/test_gem_cobra_process.py tests/test_system_biology.py -q
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/tool_gateway.py BioCult-KB_Aspergillus_sydowii/tests/test_super_tool_gateway.py
git commit -m "feat: add scientific tool gateway"
```

---

### Task 6: Add Generic Connector Plugin Registry

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/connector_registry.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_connector_registry.py`

**Interfaces:**
- Produces `Connector`, `ConnectorDescriptor`, `ConnectorRegistry`.
- This task implements the framework only; Galaxy/LIMS/native MCP providers are separate follow-up plans.

- [ ] **Step 1: Write failing registry test**

```python
def test_connector_declares_capabilities_and_permissions():
    registry = ConnectorRegistry()
    registry.register(DummyConnector())
    descriptor = registry.describe("dummy")
    assert descriptor.capabilities == ["read_dataset"]
    assert descriptor.permissions == ["read"]
    assert registry.health("dummy")["status"] == "ok"
```

- [ ] **Step 2: Define connector contract**

```python
class Connector(Protocol):
    connector_id: str

    def descriptor(self) -> ConnectorDescriptor: ...
    def health_check(self) -> dict: ...
    def read(self, operation: str, payload: dict) -> dict: ...
    def write(self, operation: str, payload: dict) -> dict: ...
```

`ConnectorDescriptor` fields:

```text
connector_id
connector_type
capabilities
permissions
configuration_schema
authentication_type
provenance_behavior
```

- [ ] **Step 3: Enforce declared write permission**

`ConnectorRegistry.write()` raises `PermissionError` unless `"write"` is declared.

- [ ] **Step 4: Add provenance normalization**

All connector responses are wrapped with `connector_id`, `operation`, `timestamp`, and `source_reference`.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest tests/test_super_connector_registry.py -q
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/connector_registry.py BioCult-KB_Aspergillus_sydowii/tests/test_super_connector_registry.py
git commit -m "feat: add scientific connector registry"
```

---

### Task 7: Build AI-Readable Context Service and MCP-Safe Facade

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/context_service.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers/context.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers/tools.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers/proposals.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_context_api.py`

**Interfaces:**
- Produces stable application operations equivalent to future MCP tools:
  `get_research_program`, `get_active_objectives`, `get_active_hypotheses`, `query_knowledge_graph`, `list_available_tools`, `run_computation`, `create_proposal`, `get_pending_proposals`.
- Does not expose direct canonical mutation methods to AI clients.

- [ ] **Step 1: Write failing context projection test**

```python
def test_context_projection_separates_facts_predictions_and_ai_inference(super_session):
    context = ContextService(super_session).project(program_id=1)
    kinds = {item["kind"] for item in context["evidence"]}
    assert "OBSERVED" in kinds
    assert "AI_INFERRED" in kinds
    assert context["permissions"]["direct_canonical_write"] is False
```

- [ ] **Step 2: Implement `ContextService.project()`**

Return one normalized dictionary:

```text
program
objectives
hypotheses
active_experiments
evidence
pending_proposals
available_tools
permissions
```

Cap embedded evidence payloads at 50 records per projection; return IDs and source references so clients can query detail separately.

- [ ] **Step 3: Write API safety test**

```python
def test_ai_api_has_no_direct_hypothesis_update_route(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/super/hypotheses/{hypothesis_id}" not in paths
    assert "/api/super/proposals" in paths
```

- [ ] **Step 4: Add routers only for approved facade operations**

Use `/api/super/...` prefix. Keep transport thin; routers call services and contain no domain logic.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest tests/test_super_context_api.py tests/test_super_proposals.py -q
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/context_service.py BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers BioCult-KB_Aspergillus_sydowii/tests/test_super_context_api.py
git commit -m "feat: add AI-safe scientific context facade"
```

---

### Task 8: Wire BioCult SUPER Routers into FastAPI Without Breaking v2

**Files:**
- Modify: `BioCult-KB_Aspergillus_sydowii/web_app/main.py`
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers/__init__.py`
- Modify: `BioCult-KB_Aspergillus_sydowii/tests/test_v2_platform.py`
- Modify: `BioCult-KB_Aspergillus_sydowii/tests/test_super_context_api.py`

**Interfaces:**
- Existing API remains available.
- New endpoints live under `/api/super`.

- [ ] **Step 1: Add regression test for legacy endpoint availability**

Use an endpoint already asserted by `test_v2_platform.py`; add one assertion that its status code remains unchanged after router inclusion.

- [ ] **Step 2: Add new health/capability assertion**

```python
def test_super_capabilities_endpoint(client):
    response = client.get("/api/super/context/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["human_approval_required"] is True
    assert body["direct_canonical_write"] is False
```

- [ ] **Step 3: Include routers in `main.py`**

Use FastAPI `include_router()` with a common `/api/super` prefix. Do not move existing route functions in this task.

- [ ] **Step 4: Run old and new API tests**

```bash
python -m pytest tests/test_v2_platform.py tests/test_super_context_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add BioCult-KB_Aspergillus_sydowii/web_app/main.py BioCult-KB_Aspergillus_sydowii/web_app/super_core/routers BioCult-KB_Aspergillus_sydowii/tests/test_v2_platform.py BioCult-KB_Aspergillus_sydowii/tests/test_super_context_api.py
git commit -m "feat: expose BioCult SUPER API facade"
```

---

### Task 9: Migrate the Existing Collagenase Case into the New Research Cycle

**Files:**
- Create: `BioCult-KB_Aspergillus_sydowii/web_app/super_core/reference_case.py`
- Create: `BioCult-KB_Aspergillus_sydowii/tests/test_super_reference_use_case.py`

**Interfaces:**
- Produces `seed_collagenase_reference_case(session)`.
- Reuses existing `Strain`, `Medium`, `Bioreactor`, `BatchRun`, and observations by reference instead of duplicating their records.

- [ ] **Step 1: Write failing end-to-end reference test**

```python
def test_collagenase_reference_case_forms_complete_research_cycle(session):
    seeded = seed_collagenase_reference_case(session)
    assert seeded.program.title == "Aspergillus sydowii collagenase cultivation"
    assert seeded.objective.title
    assert seeded.hypothesis.status == "ACTIVE"
    assert seeded.experiment.legacy_batch_id is not None
    assert seeded.evidence
```

- [ ] **Step 2: Seed one explicit objective and hypothesis**

Use only statements supported by current project material. Initial canonical hypothesis:

```text
Changes in oxygen-transfer conditions can alter the cultivation trajectory and therefore should be evaluated as a process factor in collagenase-production experiments.
```

This wording intentionally avoids claiming an experimentally proven causal mechanism.

- [ ] **Step 3: Link existing batch/observation data as evidence**

Create `EvidenceKind.IMPORTED` evidence entries pointing to legacy record IDs. Do not copy raw observation values into the knowledge relation table.

- [ ] **Step 4: Add a model-run evidence object**

Invoke one existing local computational provider through `ScientificToolGateway` and record its output as `MODEL_PREDICTED`, preserving provider provenance.

- [ ] **Step 5: Run end-to-end and legacy tests**

```bash
python -m pytest tests/test_super_reference_use_case.py tests/test_gem_cobra_process.py tests/test_system_biology.py tests/test_v2_platform.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add BioCult-KB_Aspergillus_sydowii/web_app/super_core/reference_case.py BioCult-KB_Aspergillus_sydowii/tests/test_super_reference_use_case.py
git commit -m "feat: migrate collagenase case to BioCult SUPER research cycle"
```

---

### Task 10: Document the Foundation and Verify the Whole Repository

**Files:**
- Modify: `BioCult-KB_Aspergillus_sydowii/web_app/README.md`
- Modify: `README.md`

**Interfaces:**
- Documents the stable contract Codex and future connectors should target.

- [ ] **Step 1: Update README architecture section**

Document these boundaries verbatim:

```text
BioCult SUPER Core = system of scientific record
Scientific Tool Gateway = computation execution boundary
Connector Registry = external-system integration boundary
Proposal Workspace = AI-to-human approval boundary
Knowledge Graph = semantic relation layer
Legacy cultivation modules = first reference computational/domain providers
```

- [ ] **Step 2: Document the AI safety rule**

Add:

```text
AI clients may read context, execute approved computational tools, and create proposals.
AI clients may not directly overwrite hypotheses, protocols, experimental results, evidence, or approval records.
```

- [ ] **Step 3: Document foundation API operations**

List the `/api/super` read, tool-execution, and proposal operations implemented in Tasks 7–8.

- [ ] **Step 4: Run the complete test suite**

```bash
cd BioCult-KB_Aspergillus_sydowii
python -m pytest tests -q
```

Expected: all existing and new tests PASS.

- [ ] **Step 5: Run the application smoke test**

```bash
python -m uvicorn web_app.main:app --host 127.0.0.1 --port 8000
```

Verify manually:

```text
GET /docs
GET /api/super/context/capabilities
```

Expected: Swagger loads; capabilities reports human approval required and direct canonical writes disabled.

- [ ] **Step 6: Commit**

```bash
git add README.md BioCult-KB_Aspergillus_sydowii/web_app/README.md
git commit -m "docs: document BioCult SUPER foundation"
```

---

## Post-Foundation Plans

Do not fold the following into this plan. Each is an independent subsystem and should receive its own spec/implementation plan after the foundation passes all tests:

1. **Native MCP Server** — expose the stable context/tool/proposal service operations through an actual MCP transport.
2. **Galaxy Connector** — workflow discovery, dataset upload/reference, job submission, provenance capture.
3. **Open-source LIMS Connector** — start with one target selected from real customer requirements.
4. **External Multiphysics/CAD Gateway** — provider contract for geometry, meshing, CFD/mass-transfer jobs and result mapping.
5. **Quantum-Chemistry Provider** — sandboxed job execution for ORCA/Psi4-like tools with resource controls.
6. **Graph Database Projection** — optional Neo4j/ArangoDB projection after relation semantics stabilize.
7. **Production Persistence** — PostgreSQL, migrations, authentication/authorization, backup/restore.
8. **ELN UI and Research Workspace** — human-facing notebook, evidence review and proposal approval UX.
9. **GxP/ALCOA+ Hardening** — identity, electronic signatures, immutable audit mechanisms, validation evidence and controlled configuration.
10. **Cross-scale Model Federation** — explicit `CrossScaleLink` execution, unit conversion, uncertainty propagation, and model-chain validation.

## Acceptance Criteria for This Foundation

The foundation is complete only when all of the following are demonstrated in tests:

```text
1. A ResearchProgram contains an Objective.
2. An Objective has a Hypothesis.
3. An Experiment tests that Hypothesis.
4. Observed/imported/model evidence can support or contradict it.
5. Scientific relations are traversable with provenance preserved.
6. An AI-originated proposal cannot modify canonical state before human approval.
7. A human approval can commit the proposal exactly once.
8. Existing computational modules are callable through Scientific Tool Gateway.
9. Connectors are registered through a generic plugin contract with explicit permissions.
10. AI-readable context exposes facts, model outputs and AI inferences as distinct provenance classes.
11. The new `/api/super` facade exposes no direct AI route for canonical hypothesis/result overwrite.
12. The existing v2 test suite remains green.
13. The Aspergillus/collagenase reference case can be represented end-to-end using the new research-cycle entities.
```

## Self-Review Result

- Spec coverage in this plan: research cycle, provenance, knowledge graph projection, proposal/approval boundary, Scientific Tool Gateway, connector framework, AI-readable context, API/MCP-safe facade, and the first reference use case.
- Intentionally deferred: native MCP transport, vendor connectors, external QM/CFD/CAD execution, PostgreSQL/graph infrastructure, production auth, full ELN UI, and GxP hardening. These are separate subsystems and should not be mixed into the foundation implementation.
- No direct AI mutation path is introduced.
- Existing v2 biological and process code remains isolated and reusable as providers.
