# ResearchOS Core Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Phase 1 of ResearchOS Core as a standalone, domain-independent Python package with a canonical research cycle, provenance/audit/versioning, immutable ELN, basic knowledge graph, policy engine, Domain Pack registry, REST contracts, and architecture tests proving that the core has no BioTech dependency.

**Architecture:** Create a new top-level `researchos` Python package beside the existing BioCult code. ResearchOS Core owns generic research, ELN, knowledge, governance, policy and SDK contracts; it does not import the current `BioCult-KB_Aspergillus_sydowii` package or any BioTech concept. Existing BioCult code remains untouched in Phase 1 and will be connected through adapters in a later phase.

**Tech Stack:** Python 3.10+, FastAPI, Pydantic 2, SQLAlchemy 2, SQLite for the foundation persistence backend, pytest, HTTPX/TestClient.

**Spec:** `docs/superpowers/specs/2026-09-14-researchos-core-biotech-biocult-super-design.md`

## Global Constraints

- `ResearchOS Core` must run with no BioTech Domain Pack installed.
- `ResearchOS Core` must not import `BioCult-KB_Aspergillus_sydowii`, `web_app`, BioTech entities, SBML, COBRA, OMICS, chromatography, bioreactor, scale-up or material-balance code.
- Preserve the canonical rule: **AI proposes. Human approves. System records.**
- `OBSERVED`, `MEASURED`, `CALCULATED`, `MODEL_PREDICTED`, `AI_INFERRED` and other scientific source classes remain explicit and non-interchangeable.
- Signed or locked ELN versions are immutable; corrections create a new version/amendment.
- Audit records are append-only and hash chained.
- Every scientifically significant record has provenance/version metadata sufficient to trace actor, source, version and supersession.
- Phase 1 uses SQLite/SQLAlchemy only. Do not add PostgreSQL, Neo4j, Celery, Kafka, vector databases, OMICS engines, SBML processing, scale-up solvers, material-balance solvers or technology-transfer workflows.
- Do not migrate or rewrite the existing BioCult modules in this phase.
- Use TDD for every task: failing test, minimal implementation, passing test, commit.

---

## File Structure Locked for Phase 1

Create the following structure:

```text
pyproject.toml
researchos/
  __init__.py
  core/
    __init__.py
    enums.py
    errors.py
    hashing.py
    db.py
    models/
      __init__.py
      base.py
      governance.py
      research.py
      eln.py
      knowledge.py
      policy.py
    schemas/
      __init__.py
      research.py
      eln.py
      knowledge.py
      policy.py
    services/
      __init__.py
      governance.py
      research.py
      eln.py
      knowledge.py
      policy.py
    api/
      __init__.py
      deps.py
      app.py
      routers/
        __init__.py
        research.py
        eln.py
        knowledge.py
        policy.py
        domain_packs.py
    sdk/
      __init__.py
      domain_pack.py
      registry.py
researchos/README.md

tests/
  researchos_core/
    conftest.py
    architecture/
      test_core_boundary.py
    test_database_and_governance.py
    test_research_cycle.py
    test_eln.py
    test_knowledge_graph.py
    test_policy_engine.py
    test_domain_pack_registry.py
    test_api_contracts.py
    test_phase1_acceptance.py

.github/workflows/researchos-core.yml
```

Do not create `researchos/domain_packs/biotech` in Phase 1. The registry contract is tested with an in-test fake pack so that the core remains demonstrably independent.

---

### Task 1: Bootstrap the Standalone ResearchOS Core Package and Dependency Guard

**Files:**
- Create: `pyproject.toml`
- Create: `researchos/__init__.py`
- Create: `researchos/core/__init__.py`
- Create: `researchos/core/errors.py`
- Create: `tests/researchos_core/conftest.py`
- Create: `tests/researchos_core/architecture/test_core_boundary.py`

**Interfaces:**
- Produces importable package `researchos.core`.
- Produces base exception `ResearchOSError` and `DomainBoundaryError`.
- Produces test fixture location used by every later task.
- Establishes the architecture rule that core modules cannot import legacy/BioTech modules.

- [ ] **Step 1: Write the failing package and boundary tests**

Create `tests/researchos_core/architecture/test_core_boundary.py`:

```python
from __future__ import annotations

import ast
import importlib
from pathlib import Path


FORBIDDEN_IMPORT_PREFIXES = (
    "BioCult-KB_Aspergillus_sydowii",
    "web_app",
    "researchos.domain_packs",
    "cobra",
    "libsbml",
    "Bio",
)


def test_researchos_core_is_importable():
    module = importlib.import_module("researchos.core")
    assert module.__name__ == "researchos.core"


def test_core_has_no_domain_or_legacy_imports():
    root = Path("researchos/core")
    violations: list[tuple[str, str]] = []

    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)

            for name in imported:
                if name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    violations.append((str(path), name))

    assert violations == []
```

Create `tests/researchos_core/conftest.py` with only the project root path fixture for now:

```python
from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: FAIL because `researchos.core` does not exist.

- [ ] **Step 3: Add package metadata and minimal package files**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "researchos-core"
version = "0.1.0"
description = "Domain-independent provenance-first research operating system core"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.100",
  "pydantic>=2.0",
  "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "httpx>=0.27",
]

[tool.setuptools.packages.find]
include = ["researchos", "researchos.core*"]
exclude = ["researchos.domain_packs*"]

[tool.pytest.ini_options]
testpaths = ["tests/researchos_core"]
```

Create `researchos/__init__.py`:

```python
__all__ = ["core"]
__version__ = "0.1.0"
```

Create `researchos/core/__init__.py`:

```python
"""Domain-independent ResearchOS Core."""

from .errors import DomainBoundaryError, ResearchOSError

__all__ = ["ResearchOSError", "DomainBoundaryError"]
```

Create `researchos/core/errors.py`:

```python
class ResearchOSError(Exception):
    """Base exception for ResearchOS Core."""


class DomainBoundaryError(ResearchOSError):
    """Raised when code attempts to cross a forbidden core/domain boundary."""
```

- [ ] **Step 4: Install the core package in editable mode and run the tests**

Run:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml researchos tests/researchos_core/conftest.py tests/researchos_core/architecture/test_core_boundary.py
git commit -m "feat: bootstrap standalone ResearchOS Core"
```

---

### Task 2: Add Persistence, Scientific Source Enums, Provenance, Version and Append-Only Audit Foundations

**Files:**
- Create: `researchos/core/enums.py`
- Create: `researchos/core/hashing.py`
- Create: `researchos/core/db.py`
- Create: `researchos/core/models/__init__.py`
- Create: `researchos/core/models/base.py`
- Create: `researchos/core/models/governance.py`
- Create: `researchos/core/services/__init__.py`
- Create: `researchos/core/services/governance.py`
- Modify: `tests/researchos_core/conftest.py`
- Create: `tests/researchos_core/test_database_and_governance.py`

**Interfaces:**
- Produces `SourceType`, `RecordStatus`, `ActorKind` enums.
- Produces `Base`, `ScientificRecordMixin`, `utcnow()`.
- Produces `Database` and `make_database(url: str) -> Database`.
- Produces ORM entities `ProvenanceRecord`, `VersionRecord`, `AuditRecord`, `ApprovalRecord`.
- Produces `GovernanceService.append_audit(...)`, `record_version(...)`, `record_provenance(...)`, `verify_audit_chain() -> bool`.
- Later services depend on these exact names.

- [ ] **Step 1: Write failing governance tests**

Create `tests/researchos_core/test_database_and_governance.py`:

```python
import pytest
from sqlalchemy import inspect, select

from researchos.core.enums import SourceType
from researchos.core.models.governance import AuditRecord
from researchos.core.services.governance import GovernanceService


def test_governance_tables_exist(database):
    database.create_schema()
    names = set(inspect(database.engine).get_table_names())
    assert {"provenance_records", "version_records", "audit_records", "approval_records"} <= names


def test_audit_chain_is_append_only_and_verifiable(session):
    service = GovernanceService(session)
    first = service.append_audit(
        actor_id="researcher-1",
        action="workspace.created",
        entity_type="ResearchWorkspace",
        entity_id="1",
        payload={"title": "Demo"},
    )
    second = service.append_audit(
        actor_id="researcher-1",
        action="hypothesis.created",
        entity_type="Hypothesis",
        entity_id="7",
        payload={"statement": "A affects B"},
    )
    session.commit()

    assert first.previous_hash is None
    assert second.previous_hash == first.record_hash
    assert service.verify_audit_chain() is True

    second.action = "tampered"
    with pytest.raises(Exception):
        session.commit()


def test_provenance_keeps_scientific_source_class(session):
    service = GovernanceService(session)
    record = service.record_provenance(
        entity_type="Evidence",
        entity_id="12",
        source_type=SourceType.MEASURED,
        source_reference="EXP-001/raw.csv",
        activity_type="IMPORT",
        actor_id="researcher-1",
        confidence=0.98,
        input_refs=["artifact:raw.csv"],
    )
    session.commit()
    assert record.source_type == SourceType.MEASURED.value
```

Update `tests/researchos_core/conftest.py`:

```python
from pathlib import Path

import pytest

from researchos.core.db import make_database


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def database():
    db = make_database("sqlite+pysqlite:///:memory:")
    db.create_schema()
    return db


@pytest.fixture
def session(database):
    with database.session() as session:
        yield session
        session.rollback()
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_database_and_governance.py -q
```

Expected: import failures for `researchos.core.db`, enums and governance modules.

- [ ] **Step 3: Implement scientific source/status enums and canonical hashing**

Create `researchos/core/enums.py`:

```python
from enum import Enum


class SourceType(str, Enum):
    OBSERVED = "OBSERVED"
    MEASURED = "MEASURED"
    MANUAL = "MANUAL"
    IMPORTED = "IMPORTED"
    CALCULATED = "CALCULATED"
    MODEL_PREDICTED = "MODEL_PREDICTED"
    RULE_INFERRED = "RULE_INFERRED"
    AI_INFERRED = "AI_INFERRED"
    EXPERT_APPROVED = "EXPERT_APPROVED"
    REJECTED = "REJECTED"


class RecordStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    SIGNED = "SIGNED"
    LOCKED = "LOCKED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ActorKind(str, Enum):
    HUMAN = "HUMAN"
    AI = "AI"
    SYSTEM = "SYSTEM"
    PLUGIN = "PLUGIN"
```

Create `researchos/core/hashing.py`:

```python
import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def canonical_json_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Implement SQLAlchemy base and database factory**

Create `researchos/core/models/base.py` with SQLAlchemy 2 typed declarative models:

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from researchos.core.enums import RecordStatus, SourceType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ScientificRecordMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=RecordStatus.DRAFT.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), default=SourceType.MANUAL.value, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    record_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supersedes_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

Create `researchos/core/db.py` with a `Database` dataclass exposing `engine`, `SessionLocal`, `create_schema()` and a context-managed `session()` method. For `sqlite+pysqlite:///:memory:` use `StaticPool` plus `check_same_thread=False` so API tests share one in-memory database. Import all Phase 1 model modules inside `create_schema()` before calling `Base.metadata.create_all()`.

Core implementation shape:

```python
from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models.base import Base


@dataclass
class Database:
    engine: object
    SessionLocal: sessionmaker

    def create_schema(self) -> None:
        from .models import governance
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session: Session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


def make_database(url: str) -> Database:
    kwargs = {"future": True}
    if url == "sqlite+pysqlite:///:memory:":
        kwargs.update(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    engine = create_engine(url, **kwargs)
    return Database(engine=engine, SessionLocal=sessionmaker(bind=engine, expire_on_commit=False))
```

When later model files are added, extend the local imports in `create_schema()`; do not import legacy modules.

- [ ] **Step 5: Implement governance ORM models and append-only guards**

Create `researchos/core/models/governance.py` with:

```text
ProvenanceRecord:
  id, entity_type, entity_id, source_type, source_reference, activity_type,
  actor_id, confidence, input_refs_json, created_at

VersionRecord:
  id, entity_type, entity_id, version, payload_json, payload_hash,
  created_at, created_by

AuditRecord:
  id, created_at, actor_id, action, entity_type, entity_id,
  payload_json, previous_hash, record_hash

ApprovalRecord:
  id, entity_type, entity_id, entity_version, actor_id, decision,
  meaning, reason, content_hash, created_at
```

Use JSON serialized as `Text` in Phase 1. Register SQLAlchemy `before_update` and `before_delete` listeners for `AuditRecord` that raise `ImmutableRecordError`.

Add to `researchos/core/errors.py`:

```python
class ImmutableRecordError(ResearchOSError):
    """Raised when an immutable record is updated or deleted."""
```

- [ ] **Step 6: Implement governance service**

Create `researchos/core/services/governance.py`. Exact public methods:

```python
class GovernanceService:
    def __init__(self, session): ...

    def append_audit(
        self,
        *,
        actor_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict,
    ) -> AuditRecord: ...

    def record_version(
        self,
        *,
        entity_type: str,
        entity_id: str,
        version: int,
        payload: dict,
        created_by: str,
    ) -> VersionRecord: ...

    def record_provenance(
        self,
        *,
        entity_type: str,
        entity_id: str,
        source_type: SourceType,
        source_reference: str | None,
        activity_type: str,
        actor_id: str,
        confidence: float | None,
        input_refs: list[str],
    ) -> ProvenanceRecord: ...

    def verify_audit_chain(self) -> bool: ...
```

`append_audit()` must select the most recent audit record, include its `record_hash` as `previous_hash`, hash the canonical payload `{created_at, actor_id, action, entity_type, entity_id, payload, previous_hash}`, add the row and `flush()` it. `verify_audit_chain()` must recompute every hash in ascending ID order and verify both the hash and previous-hash pointer.

- [ ] **Step 7: Run governance and architecture tests**

Run:

```bash
python -m pytest tests/researchos_core/test_database_and_governance.py tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add researchos/core tests/researchos_core
git commit -m "feat: add ResearchOS provenance and audit foundation"
```

---

### Task 3: Implement Research Workspace and Canonical Research Cycle Entities

**Files:**
- Create: `researchos/core/models/research.py`
- Create: `researchos/core/schemas/__init__.py`
- Create: `researchos/core/schemas/research.py`
- Create: `researchos/core/services/research.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_research_cycle.py`

**Interfaces:**
- Produces ORM entities `ResearchWorkspace`, `ResearchProgram`, `ResearchObjective`, `ResearchQuestion`, `Hypothesis`, `ExperimentDesign`, `Protocol`, `ExperimentRun`, `Observation`, `Measurement`, `Dataset`, `Evidence`, `Result`, `Proposal`, `Decision`, `Artifact`.
- Produces create/read Pydantic contracts in `schemas.research`.
- Produces `ResearchService` methods listed below.
- Every create operation records a `VersionRecord`, `ProvenanceRecord` and `AuditRecord` through `GovernanceService`.

- [ ] **Step 1: Write failing Research Cycle tests**

Create `tests/researchos_core/test_research_cycle.py`:

```python
from researchos.core.enums import SourceType
from researchos.core.services.research import ResearchService


def test_research_cycle_builds_from_workspace_to_result(session):
    service = ResearchService(session)

    workspace = service.create_workspace("Collagenase research", actor_id="researcher-1")
    program = service.create_program(workspace.id, "Process development", actor_id="researcher-1")
    objective = service.create_objective(program.id, "Improve product recovery", actor_id="researcher-1")
    question = service.create_question(objective.id, "Which process variable limits recovery?", actor_id="researcher-1")
    hypothesis = service.create_hypothesis(
        objective_id=objective.id,
        question_id=question.id,
        statement="A controllable process variable limits recovery",
        rationale="The current data show reproducible variation",
        actor_id="researcher-1",
    )
    design = service.create_experiment_design(
        objective_id=objective.id,
        hypothesis_id=hypothesis.id,
        title="Factor screening",
        design={"factors": ["A", "B"]},
        actor_id="researcher-1",
    )
    protocol = service.create_protocol(
        experiment_design_id=design.id,
        title="Screening protocol",
        body_markdown="Run the predefined factor matrix.",
        actor_id="researcher-1",
    )
    run = service.create_experiment_run(
        workspace_id=workspace.id,
        experiment_design_id=design.id,
        protocol_id=protocol.id,
        title="EXP-001",
        actor_id="researcher-1",
    )
    measurement = service.add_measurement(
        run_id=run.id,
        name="response",
        value=42.0,
        unit="a.u.",
        actor_id="researcher-1",
        source_type=SourceType.MEASURED,
    )
    evidence = service.create_evidence(
        run_id=run.id,
        title="EXP-001 response",
        payload={"measurement_id": measurement.id},
        actor_id="researcher-1",
        source_type=SourceType.MEASURED,
        confidence=0.95,
    )
    result = service.create_result(
        run_id=run.id,
        title="Screening result",
        result_type="STATISTICAL_SUMMARY",
        payload={"best_factor": "A"},
        actor_id="researcher-1",
        source_type=SourceType.CALCULATED,
    )
    session.commit()

    assert result.run_id == run.id
    assert evidence.source_type == SourceType.MEASURED.value
    assert hypothesis.version == 1


def test_ai_inferred_evidence_stays_ai_inferred(session):
    service = ResearchService(session)
    workspace = service.create_workspace("Generic study", actor_id="human-1")
    run = service.create_experiment_run(
        workspace_id=workspace.id,
        experiment_design_id=None,
        protocol_id=None,
        title="EXP-AI",
        actor_id="human-1",
    )
    evidence = service.create_evidence(
        run_id=run.id,
        title="AI interpretation",
        payload={"claim": "possible explanation"},
        actor_id="agent-1",
        source_type=SourceType.AI_INFERRED,
        confidence=0.6,
    )
    assert evidence.source_type == "AI_INFERRED"
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_research_cycle.py -q
```

Expected: import failure because research models/service do not exist.

- [ ] **Step 3: Implement Research Cycle models**

Create `researchos/core/models/research.py`. All scientifically significant entities inherit `ScientificRecordMixin`. Use integer foreign keys where the relation is within one table family and nullable references where the workflow permits partial research records.

Required fields:

```text
ResearchWorkspace: title, description
ResearchProgram: workspace_id, title, description
ResearchObjective: program_id, title, description
ResearchQuestion: objective_id, question_text
Hypothesis: objective_id, question_id?, statement, rationale
ExperimentDesign: objective_id, hypothesis_id?, title, design_json
Protocol: experiment_design_id?, title, body_markdown
ExperimentRun: workspace_id, experiment_design_id?, protocol_id?, title, started_at?, completed_at?
Observation: run_id, text
Measurement: run_id, name, value, unit
Dataset: run_id?, title, uri?, media_type?, checksum?
Evidence: run_id?, title, payload_json
Result: run_id?, title, result_type, payload_json
Proposal: workspace_id, title, payload_json
Decision: proposal_id?, title, outcome, rationale
Artifact: workspace_id, title, artifact_type, uri?, checksum?
```

Store structured Phase 1 payloads as canonical JSON strings in `Text` columns. Do not add domain-specific columns.

- [ ] **Step 4: Implement Pydantic contracts**

Create `researchos/core/schemas/research.py` using Pydantic 2 `BaseModel` and `ConfigDict(from_attributes=True)`. Define explicit create schemas for workspace, program, objective, question, hypothesis, experiment design, protocol, run, measurement, evidence and result. Define matching read schemas with `id`, `version`, `status`, `created_at`, `created_by` plus entity-specific fields.

Example exact contracts:

```python
from pydantic import BaseModel, ConfigDict, Field

from researchos.core.enums import SourceType


class WorkspaceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class HypothesisCreate(BaseModel):
    objective_id: int
    question_id: int | None = None
    statement: str = Field(min_length=1)
    rationale: str | None = None


class EvidenceCreate(BaseModel):
    run_id: int | None = None
    title: str
    payload: dict
    source_type: SourceType
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
```

- [ ] **Step 5: Implement `ResearchService` with governance recording**

Create `researchos/core/services/research.py`. Public methods must have these names:

```text
create_workspace(title, description=None, actor_id=...)
create_program(workspace_id, title, description=None, actor_id=...)
create_objective(program_id, title, description=None, actor_id=...)
create_question(objective_id, question_text, actor_id=...)
create_hypothesis(objective_id, question_id, statement, rationale, actor_id=...)
create_experiment_design(objective_id, hypothesis_id, title, design, actor_id=...)
create_protocol(experiment_design_id, title, body_markdown, actor_id=...)
create_experiment_run(workspace_id, experiment_design_id, protocol_id, title, actor_id=...)
add_observation(run_id, text, actor_id, source_type=SourceType.OBSERVED)
add_measurement(run_id, name, value, unit, actor_id, source_type=SourceType.MEASURED)
create_dataset(run_id, title, actor_id, source_type, uri=None, media_type=None, checksum=None)
create_evidence(run_id, title, payload, actor_id, source_type, confidence=None)
create_result(run_id, title, result_type, payload, actor_id, source_type)
create_proposal(workspace_id, title, payload, actor_id, source_type)
create_decision(proposal_id, title, outcome, rationale, actor_id)
```

Use one private helper `_finalize_create(entity, actor_id, action, provenance_source, payload)` that:

1. Computes `record_hash` from the serialized scientific content.
2. Adds and flushes the entity.
3. Calls `GovernanceService.record_version()`.
4. Calls `GovernanceService.record_provenance()`.
5. Calls `GovernanceService.append_audit()`.
6. Returns the entity without committing; transaction ownership stays with the caller/API request.

Do not auto-upgrade `AI_INFERRED` to another source type.

- [ ] **Step 6: Register research models in schema creation and run tests**

Modify `Database.create_schema()` in `researchos/core/db.py` to import `governance` and `research` before `Base.metadata.create_all()`.

Run:

```bash
python -m pytest tests/researchos_core/test_research_cycle.py tests/researchos_core/test_database_and_governance.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add researchos/core tests/researchos_core/test_research_cycle.py
git commit -m "feat: add canonical ResearchOS research cycle"
```

---

### Task 4: Implement Versioned ELN with Signatures, Snapshots and Hard Immutability

**Files:**
- Create: `researchos/core/models/eln.py`
- Create: `researchos/core/schemas/eln.py`
- Create: `researchos/core/services/eln.py`
- Modify: `researchos/core/db.py`
- Modify: `researchos/core/errors.py`
- Create: `tests/researchos_core/test_eln.py`

**Interfaces:**
- Produces `Notebook`, `NotebookEntry`, `EntryVersion`, `Signature`, `ImmutableSnapshot`.
- Produces `ELNService.create_notebook`, `create_entry`, `create_revision`, `sign_version`, `lock_version`, `get_history`.
- A persisted locked version cannot be updated or deleted even through direct ORM manipulation.

- [ ] **Step 1: Write failing ELN immutability tests**

Create `tests/researchos_core/test_eln.py`:

```python
import pytest

from researchos.core.errors import ImmutableRecordError
from researchos.core.services.eln import ELNService
from researchos.core.services.research import ResearchService


def test_eln_revision_preserves_history_and_signature_locks_version(session):
    workspace = ResearchService(session).create_workspace("ELN study", actor_id="researcher-1")
    eln = ELNService(session)
    notebook = eln.create_notebook(workspace.id, "Main notebook", actor_id="researcher-1")
    entry, v1 = eln.create_entry(
        notebook_id=notebook.id,
        title="Day 1",
        content_markdown="Initial observation",
        actor_id="researcher-1",
    )
    v2 = eln.create_revision(
        entry_id=entry.id,
        content_markdown="Corrected observation",
        actor_id="researcher-1",
        reason="Clarified wording",
    )
    signature = eln.sign_version(
        version_id=v2.id,
        signer_id="researcher-1",
        meaning="performed",
        reason="Entry complete",
    )
    session.commit()

    history = eln.get_history(entry.id)
    assert [item.version_number for item in history] == [1, 2]
    assert signature.content_hash == v2.content_hash
    assert v2.locked_at is not None

    v2.content_markdown = "tampered"
    with pytest.raises(ImmutableRecordError):
        session.commit()


def test_locked_version_cannot_be_deleted(session):
    workspace = ResearchService(session).create_workspace("ELN delete guard", actor_id="researcher-1")
    eln = ELNService(session)
    notebook = eln.create_notebook(workspace.id, "Main", actor_id="researcher-1")
    entry, version = eln.create_entry(notebook.id, "Record", "Evidence", actor_id="researcher-1")
    eln.lock_version(version.id, actor_id="researcher-1", reason="Approved record")
    session.commit()

    session.delete(version)
    with pytest.raises(ImmutableRecordError):
        session.commit()
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_eln.py -q
```

Expected: import failure for ELN models/service.

- [ ] **Step 3: Implement ELN models**

Create `researchos/core/models/eln.py` with:

```text
Notebook:
  id, workspace_id, title, description, created_at, created_by

NotebookEntry:
  id, notebook_id, title, current_version_number, created_at, created_by

EntryVersion:
  id, entry_id, version_number, content_markdown, reason,
  source_type, content_hash, created_at, created_by, locked_at

Signature:
  id, entry_version_id, signer_id, meaning, reason,
  signed_at, content_hash

ImmutableSnapshot:
  id, entry_version_id (unique), payload_json, payload_hash, created_at
```

Add `ELNStateError` to `errors.py` for invalid transitions and reuse `ImmutableRecordError` for mutation guards.

- [ ] **Step 4: Implement SQLAlchemy hard immutability guards**

Register `before_update` and `before_delete` listeners for `EntryVersion`.

For `before_update`, use `sqlalchemy.inspect(target).attrs.locked_at.history` so the transition from `locked_at=None` to a timestamp is allowed, but any update to a version that was already locked in the database raises `ImmutableRecordError`.

Implementation pattern:

```python
from sqlalchemy import event, inspect


@event.listens_for(EntryVersion, "before_update")
def prevent_update_of_locked_version(mapper, connection, target):
    state = inspect(target)
    history = state.attrs.locked_at.history
    was_locked = bool(history.deleted and history.deleted[0] is not None)
    unchanged_locked = target.locked_at is not None and not history.added
    if was_locked or unchanged_locked:
        raise ImmutableRecordError("Locked ELN versions are immutable")


@event.listens_for(EntryVersion, "before_delete")
def prevent_delete_of_locked_version(mapper, connection, target):
    if target.locked_at is not None:
        raise ImmutableRecordError("Locked ELN versions cannot be deleted")
```

- [ ] **Step 5: Implement ELN service and snapshot semantics**

Create `researchos/core/services/eln.py`.

Rules:

- `create_entry()` creates `NotebookEntry` plus version 1; it never stores editable content on `NotebookEntry` itself.
- `create_revision()` always inserts a new `EntryVersion`; it never edits an existing version.
- `lock_version()` creates one `ImmutableSnapshot` using `{entry_id, version_number, content_markdown, content_hash}`, then sets `locked_at`.
- `sign_version()` verifies the current content hash, inserts `Signature`, creates the snapshot if absent, and locks the version in the same transaction.
- `get_history()` returns versions sorted by `version_number ASC`.
- Every create/revise/sign/lock action writes an audit event. Version creation also writes a `VersionRecord`.

Exact public signatures:

```python
class ELNService:
    def create_notebook(self, workspace_id: int, title: str, *, actor_id: str, description: str | None = None): ...
    def create_entry(self, notebook_id: int, title: str, content_markdown: str, *, actor_id: str): ...
    def create_revision(self, entry_id: int, content_markdown: str, *, actor_id: str, reason: str): ...
    def lock_version(self, version_id: int, *, actor_id: str, reason: str): ...
    def sign_version(self, version_id: int, *, signer_id: str, meaning: str, reason: str): ...
    def get_history(self, entry_id: int) -> list[EntryVersion]: ...
```

- [ ] **Step 6: Add Pydantic ELN schemas and register models**

Create request/response schemas for notebook creation, entry creation, revision, lock and signature. Modify `Database.create_schema()` to import `eln`.

Run:

```bash
python -m pytest tests/researchos_core/test_eln.py tests/researchos_core/test_database_and_governance.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add researchos/core tests/researchos_core/test_eln.py
git commit -m "feat: add immutable versioned ResearchOS ELN"
```

---

### Task 5: Implement the Basic Provenance-Aware Knowledge Graph

**Files:**
- Create: `researchos/core/models/knowledge.py`
- Create: `researchos/core/schemas/knowledge.py`
- Create: `researchos/core/services/knowledge.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_knowledge_graph.py`

**Interfaces:**
- Produces `KnowledgeEntity`, `KnowledgeRelation`, `Document`, `Source`, `Citation`.
- Produces core relation enum `CoreRelationType`.
- Produces `KnowledgeService.create_entity`, `create_relation`, `neighbors`, `relations_for`.
- Relations may point to any typed ResearchOS entity through `(source_type, source_id)` and `(target_type, target_id)`; they are not restricted to `KnowledgeEntity` rows.

- [ ] **Step 1: Write failing graph tests**

Create `tests/researchos_core/test_knowledge_graph.py`:

```python
from researchos.core.enums import SourceType
from researchos.core.services.knowledge import KnowledgeService
from researchos.core.services.research import ResearchService


def test_evidence_can_support_hypothesis_with_provenance(session):
    research = ResearchService(session)
    workspace = research.create_workspace("Graph study", actor_id="human-1")
    program = research.create_program(workspace.id, "Program", actor_id="human-1")
    objective = research.create_objective(program.id, "Objective", actor_id="human-1")
    question = research.create_question(objective.id, "Question?", actor_id="human-1")
    hypothesis = research.create_hypothesis(objective.id, question.id, "H1", "Reason", actor_id="human-1")
    evidence = research.create_evidence(
        run_id=None,
        title="Observed evidence",
        payload={"value": 1},
        actor_id="human-1",
        source_type=SourceType.OBSERVED,
        confidence=0.9,
    )

    graph = KnowledgeService(session)
    relation = graph.create_relation(
        workspace_id=workspace.id,
        source_type="Evidence",
        source_id=str(evidence.id),
        relation_type="SUPPORTS",
        target_type="Hypothesis",
        target_id=str(hypothesis.id),
        actor_id="human-1",
        source_class=SourceType.MANUAL,
        confidence=0.9,
        provenance={"reason": "reviewed experimental evidence"},
    )
    session.commit()

    assert relation.relation_type == "SUPPORTS"
    assert graph.neighbors("Hypothesis", str(hypothesis.id))[0].source_type == "Evidence"


def test_ai_relation_remains_ai_inferred(session):
    graph = KnowledgeService(session)
    entity = graph.create_entity(
        workspace_id=1,
        entity_type="Concept",
        label="Candidate mechanism",
        actor_id="agent-1",
        source_class=SourceType.AI_INFERRED,
        confidence=0.55,
    )
    assert entity.source_type == "AI_INFERRED"
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_knowledge_graph.py -q
```

Expected: missing knowledge modules.

- [ ] **Step 3: Add `CoreRelationType`**

Extend `researchos/core/enums.py`:

```python
class CoreRelationType(str, Enum):
    PART_OF = "PART_OF"
    DERIVED_FROM = "DERIVED_FROM"
    GENERATED_BY = "GENERATED_BY"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    REFERENCES = "REFERENCES"
    USES = "USES"
    PRODUCES = "PRODUCES"
    TESTS = "TESTS"
    SUPERSEDES = "SUPERSEDES"
    BASED_ON = "BASED_ON"
    RESOLVES = "RESOLVES"
```

- [ ] **Step 4: Implement knowledge models**

Create `researchos/core/models/knowledge.py` with:

```text
KnowledgeEntity:
  ScientificRecordMixin + workspace_id, entity_type, external_ref?, label, summary?

KnowledgeRelation:
  ScientificRecordMixin + workspace_id, source_type_name, source_id,
  relation_type, target_type_name, target_id, provenance_json

Document:
  ScientificRecordMixin + workspace_id, title, media_type?, uri?, checksum?

Source:
  ScientificRecordMixin + workspace_id, title, source_kind, locator?

Citation:
  ScientificRecordMixin + workspace_id, source_id, entity_type_name,
  entity_id, locator?, quote_hash?
```

Use column names `source_type_name` and `target_type_name` in ORM to avoid collision with `ScientificRecordMixin.source_type`.

- [ ] **Step 5: Implement knowledge service**

Exact methods:

```python
class KnowledgeService:
    def create_entity(self, *, workspace_id: int, entity_type: str, label: str, actor_id: str, source_class: SourceType, confidence: float | None = None, summary: str | None = None, external_ref: str | None = None): ...
    def create_relation(self, *, workspace_id: int, source_type: str, source_id: str, relation_type: str, target_type: str, target_id: str, actor_id: str, source_class: SourceType, confidence: float | None, provenance: dict): ...
    def neighbors(self, entity_type: str, entity_id: str) -> list[KnowledgeRelation]: ...
    def relations_for(self, workspace_id: int) -> list[KnowledgeRelation]: ...
```

`create_relation()` must validate core relation strings against `CoreRelationType` in Phase 1. Future Domain Packs will extend relation registration in a later phase; do not add BioTech relations now.

Every relation stores provenance JSON, explicit confidence, source class and an audit record.

- [ ] **Step 6: Register knowledge models and run tests**

Modify `Database.create_schema()` to import `knowledge`.

Run:

```bash
python -m pytest tests/researchos_core/test_knowledge_graph.py tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add researchos/core tests/researchos_core/test_knowledge_graph.py
git commit -m "feat: add provenance-aware ResearchOS knowledge graph"
```

---

### Task 6: Implement the Phase 1 Policy Engine and Hard AI Boundaries

**Files:**
- Create: `researchos/core/models/policy.py`
- Create: `researchos/core/schemas/policy.py`
- Create: `researchos/core/services/policy.py`
- Modify: `researchos/core/enums.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_policy_engine.py`

**Interfaces:**
- Produces `ExecutionMode`, `RiskLevel`, `PolicyEffect` enums.
- Produces `PolicyProfile` ORM entity.
- Produces `PolicyDecision` value model and `PolicyEngine.evaluate(...)`.
- Enforces hard boundaries independent of prompt text.

- [ ] **Step 1: Write failing policy tests**

Create `tests/researchos_core/test_policy_engine.py`:

```python
from researchos.core.enums import ActorKind, ExecutionMode, PolicyEffect, RiskLevel
from researchos.core.services.policy import PolicyEngine


def test_supervised_ai_requires_approval_for_canonical_mutation():
    decision = PolicyEngine().evaluate(
        action="modify_protocol",
        actor_kind=ActorKind.AI,
        mode=ExecutionMode.SUPERVISED,
        risk=RiskLevel.HIGH,
    )
    assert decision.effect == PolicyEffect.REQUIRE_APPROVAL


def test_autonomous_ai_can_run_low_risk_calculation():
    decision = PolicyEngine().evaluate(
        action="run_calculation",
        actor_kind=ActorKind.AI,
        mode=ExecutionMode.FULL_POLICY_AUTONOMY,
        risk=RiskLevel.LOW,
    )
    assert decision.effect == PolicyEffect.ALLOW


def test_ai_can_never_sign_or_rewrite_audit():
    engine = PolicyEngine()
    for action in ("sign_record", "rewrite_audit_log", "mutate_locked_record", "approve_technology_transfer"):
        decision = engine.evaluate(
            action=action,
            actor_kind=ActorKind.AI,
            mode=ExecutionMode.FULL_POLICY_AUTONOMY,
            risk=RiskLevel.CRITICAL,
        )
        assert decision.effect == PolicyEffect.DENY
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_policy_engine.py -q
```

Expected: missing policy enums/service.

- [ ] **Step 3: Implement policy enums and persisted profile**

Extend `enums.py`:

```python
class ExecutionMode(str, Enum):
    OFF = "OFF"
    SUPERVISED = "SUPERVISED"
    LIMITED_AUTONOMY = "LIMITED_AUTONOMY"
    FULL_POLICY_AUTONOMY = "FULL_POLICY_AUTONOMY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyEffect(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"
```

Create `PolicyProfile` in `models/policy.py`:

```text
id
workspace_id
name
execution_mode
created_at
created_by
```

No per-tool policy persistence is required in Phase 1; that belongs to the agent/tool phase.

- [ ] **Step 4: Implement deterministic policy engine**

Create `researchos/core/services/policy.py`:

```python
from dataclasses import dataclass

from researchos.core.enums import ActorKind, ExecutionMode, PolicyEffect, RiskLevel


@dataclass(frozen=True)
class PolicyDecision:
    effect: PolicyEffect
    reason: str


class PolicyEngine:
    HARD_DENY_FOR_AI = {
        "sign_record",
        "rewrite_audit_log",
        "mutate_locked_record",
        "approve_technology_transfer",
    }

    CANONICAL_MUTATIONS = {
        "modify_protocol",
        "approve_evidence",
        "delete_dataset",
        "commit_proposal",
    }

    def evaluate(self, *, action: str, actor_kind: ActorKind, mode: ExecutionMode, risk: RiskLevel) -> PolicyDecision:
        if actor_kind == ActorKind.AI and action in self.HARD_DENY_FOR_AI:
            return PolicyDecision(PolicyEffect.DENY, "Hard human-only boundary")
        if actor_kind == ActorKind.AI and mode in {ExecutionMode.OFF, ExecutionMode.SUPERVISED} and action in self.CANONICAL_MUTATIONS:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Supervised canonical mutation")
        if risk == RiskLevel.CRITICAL and actor_kind != ActorKind.HUMAN:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Critical action requires accountable human review")
        if actor_kind == ActorKind.AI and mode == ExecutionMode.LIMITED_AUTONOMY and risk in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Limited autonomy risk threshold")
        return PolicyDecision(PolicyEffect.ALLOW, "Action permitted by foundation policy")
```

- [ ] **Step 5: Add policy schemas, register model and run tests**

Define `PolicyEvaluateRequest` and `PolicyEvaluateResponse` in `schemas/policy.py`. Modify `Database.create_schema()` to import `policy`.

Run:

```bash
python -m pytest tests/researchos_core/test_policy_engine.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add researchos/core tests/researchos_core/test_policy_engine.py
git commit -m "feat: add ResearchOS policy engine boundaries"
```

---

### Task 7: Implement the Domain Pack SDK and Registry Shell Without Shipping BioTech

**Files:**
- Create: `researchos/core/sdk/__init__.py`
- Create: `researchos/core/sdk/domain_pack.py`
- Create: `researchos/core/sdk/registry.py`
- Modify: `researchos/core/errors.py`
- Create: `tests/researchos_core/test_domain_pack_registry.py`

**Interfaces:**
- Produces `DomainPackManifest`, `DomainPack` protocol, `DomainPackRegistry`.
- Domain Packs can register metadata and future extension names, but Phase 1 does not load or execute BioTech code.

- [ ] **Step 1: Write failing registry tests**

Create `tests/researchos_core/test_domain_pack_registry.py`:

```python
import pytest

from researchos.core.errors import DomainPackRegistrationError
from researchos.core.sdk.domain_pack import DomainPackManifest
from researchos.core.sdk.registry import DomainPackRegistry


class FakePack:
    manifest = DomainPackManifest(
        id="example-domain",
        name="Example Domain",
        version="1.0.0",
        entities=["ExampleEntity"],
        relations=["RELATES_TO"],
        tools=[],
        imports=[],
        exports=[],
        policies=[],
    )


def test_registry_accepts_domain_pack_without_core_importing_it():
    registry = DomainPackRegistry()
    registry.register(FakePack())
    assert registry.get("example-domain").manifest.name == "Example Domain"
    assert [p.manifest.id for p in registry.list()] == ["example-domain"]


def test_duplicate_pack_id_is_rejected():
    registry = DomainPackRegistry()
    registry.register(FakePack())
    with pytest.raises(DomainPackRegistrationError):
        registry.register(FakePack())
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_domain_pack_registry.py -q
```

Expected: missing SDK modules.

- [ ] **Step 3: Implement manifest and protocol**

Create `researchos/core/sdk/domain_pack.py`:

```python
from typing import Protocol

from pydantic import BaseModel, Field


class DomainPackManifest(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    version: str
    entities: list[str] = []
    relations: list[str] = []
    tools: list[str] = []
    imports: list[str] = []
    exports: list[str] = []
    policies: list[str] = []


class DomainPack(Protocol):
    manifest: DomainPackManifest
```

Use `Field(default_factory=list)` instead of mutable literal list defaults in the final implementation for every list field.

- [ ] **Step 4: Implement registry and duplicate guard**

Add to `errors.py`:

```python
class DomainPackRegistrationError(ResearchOSError):
    """Raised when a Domain Pack cannot be registered safely."""
```

Create `registry.py`:

```python
from researchos.core.errors import DomainPackRegistrationError
from researchos.core.sdk.domain_pack import DomainPack


class DomainPackRegistry:
    def __init__(self):
        self._packs: dict[str, DomainPack] = {}

    def register(self, pack: DomainPack) -> None:
        pack_id = pack.manifest.id
        if pack_id in self._packs:
            raise DomainPackRegistrationError(f"Domain Pack already registered: {pack_id}")
        self._packs[pack_id] = pack

    def get(self, pack_id: str) -> DomainPack:
        try:
            return self._packs[pack_id]
        except KeyError as exc:
            raise DomainPackRegistrationError(f"Unknown Domain Pack: {pack_id}") from exc

    def list(self) -> list[DomainPack]:
        return [self._packs[key] for key in sorted(self._packs)]
```

- [ ] **Step 5: Run registry and architecture tests**

Run:

```bash
python -m pytest tests/researchos_core/test_domain_pack_registry.py tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: all tests pass and the boundary scanner still reports zero forbidden imports.

- [ ] **Step 6: Commit**

```bash
git add researchos/core/sdk researchos/core/errors.py tests/researchos_core/test_domain_pack_registry.py
git commit -m "feat: add ResearchOS Domain Pack registry SDK"
```

---

### Task 8: Expose Phase 1 Through Stable FastAPI REST Contracts

**Files:**
- Create: `researchos/core/api/__init__.py`
- Create: `researchos/core/api/deps.py`
- Create: `researchos/core/api/app.py`
- Create: `researchos/core/api/routers/__init__.py`
- Create: `researchos/core/api/routers/research.py`
- Create: `researchos/core/api/routers/eln.py`
- Create: `researchos/core/api/routers/knowledge.py`
- Create: `researchos/core/api/routers/policy.py`
- Create: `researchos/core/api/routers/domain_packs.py`
- Create: `tests/researchos_core/test_api_contracts.py`

**Interfaces:**
- Produces `create_app(database_url: str = "sqlite+pysqlite:///./researchos.db", registry: DomainPackRegistry | None = None) -> FastAPI`.
- REST endpoints are thin adapters over services; routers contain no scientific business logic.

- [ ] **Step 1: Write failing API contract tests**

Create `tests/researchos_core/test_api_contracts.py`:

```python
from fastapi.testclient import TestClient

from researchos.core.api.app import create_app


def test_researchos_api_exposes_foundation_contracts():
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["service"] == "researchos-core"

    workspace = client.post(
        "/api/workspaces",
        json={"title": "API study", "description": "generic"},
        headers={"X-Actor-Id": "human-1"},
    )
    assert workspace.status_code == 201
    workspace_id = workspace.json()["id"]

    notebook = client.post(
        f"/api/workspaces/{workspace_id}/notebooks",
        json={"title": "ELN", "description": None},
        headers={"X-Actor-Id": "human-1"},
    )
    assert notebook.status_code == 201

    policy = client.post(
        "/api/policy/evaluate",
        json={
            "action": "sign_record",
            "actor_kind": "AI",
            "mode": "FULL_POLICY_AUTONOMY",
            "risk": "CRITICAL",
        },
    )
    assert policy.status_code == 200
    assert policy.json()["effect"] == "DENY"

    packs = client.get("/api/domain-packs")
    assert packs.status_code == 200
    assert packs.json() == []
```

- [ ] **Step 2: Run and verify failure**

Run:

```bash
python -m pytest tests/researchos_core/test_api_contracts.py -q
```

Expected: missing API modules.

- [ ] **Step 3: Implement dependency container**

Create `api/deps.py` with a small `AppServices` dataclass containing `Database` and `DomainPackRegistry`. Provide request dependencies:

```python
def get_services(request: Request) -> AppServices:
    return request.app.state.services


def get_session(services: AppServices = Depends(get_services)):
    with services.database.session() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

Actor identity for Phase 1 is supplied by `X-Actor-Id`; no authentication system is introduced yet. Router helper `actor_id: str = Header(default="local-user", alias="X-Actor-Id")` is sufficient for foundation contracts.

- [ ] **Step 4: Implement thin routers**

Implement these minimum routes:

```text
GET  /api/health
POST /api/workspaces
POST /api/workspaces/{workspace_id}/programs
POST /api/programs/{program_id}/objectives
POST /api/objectives/{objective_id}/questions
POST /api/questions/{question_id}/hypotheses
POST /api/workspaces/{workspace_id}/notebooks
POST /api/notebooks/{notebook_id}/entries
POST /api/eln/entries/{entry_id}/revisions
POST /api/eln/versions/{version_id}/sign
POST /api/knowledge/entities
POST /api/knowledge/relations
POST /api/policy/evaluate
GET  /api/domain-packs
```

Each route validates input with Pydantic schemas, instantiates the corresponding service with the request session, delegates exactly once, and returns an ORM-backed response schema. Convert missing IDs/state errors to 404/409; do not duplicate service rules in routers.

- [ ] **Step 5: Implement app factory**

Create `api/app.py`:

```python
from fastapi import FastAPI

from researchos.core.db import make_database
from researchos.core.sdk.registry import DomainPackRegistry


def create_app(
    database_url: str = "sqlite+pysqlite:///./researchos.db",
    registry: DomainPackRegistry | None = None,
) -> FastAPI:
    database = make_database(database_url)
    database.create_schema()
    app = FastAPI(title="ResearchOS Core", version="0.1.0")
    app.state.services = AppServices(database=database, registry=registry or DomainPackRegistry())
    app.include_router(research_router, prefix="/api")
    app.include_router(eln_router, prefix="/api")
    app.include_router(knowledge_router, prefix="/api")
    app.include_router(policy_router, prefix="/api")
    app.include_router(domain_pack_router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "researchos-core", "version": "0.1.0"}

    return app
```

Import `AppServices` and router objects from their actual modules in the final file.

- [ ] **Step 6: Run API and full Phase 1 tests to this point**

Run:

```bash
python -m pytest tests/researchos_core/test_api_contracts.py -q
python -m pytest tests/researchos_core -q
```

Expected: all current tests pass.

- [ ] **Step 7: Commit**

```bash
git add researchos/core/api tests/researchos_core/test_api_contracts.py
git commit -m "feat: expose ResearchOS Core REST contracts"
```

---

### Task 9: Add a Generic End-to-End Phase 1 Acceptance Scenario

**Files:**
- Create: `tests/researchos_core/test_phase1_acceptance.py`

**Interfaces:**
- Consumes all Phase 1 services.
- Proves a generic, non-BioTech research workflow works end to end.
- Proves AI provenance separation, ELN immutability, graph traceability, policy boundaries, audit integrity and empty Domain Pack operation in one scenario.

- [ ] **Step 1: Write the acceptance scenario**

Create `tests/researchos_core/test_phase1_acceptance.py`:

```python
import pytest

from researchos.core.enums import ActorKind, ExecutionMode, PolicyEffect, RiskLevel, SourceType
from researchos.core.errors import ImmutableRecordError
from researchos.core.sdk.registry import DomainPackRegistry
from researchos.core.services.eln import ELNService
from researchos.core.services.governance import GovernanceService
from researchos.core.services.knowledge import KnowledgeService
from researchos.core.services.policy import PolicyEngine
from researchos.core.services.research import ResearchService


def test_phase1_generic_research_workflow(session):
    research = ResearchService(session)
    workspace = research.create_workspace("Domain-neutral study", actor_id="human-1")
    program = research.create_program(workspace.id, "General research", actor_id="human-1")
    objective = research.create_objective(program.id, "Understand a measured response", actor_id="human-1")
    question = research.create_question(objective.id, "What explains the response?", actor_id="human-1")
    hypothesis = research.create_hypothesis(objective.id, question.id, "Factor A explains the response", "Initial rationale", actor_id="human-1")
    run = research.create_experiment_run(workspace.id, None, None, "EXP-001", actor_id="human-1")
    measurement = research.add_measurement(run.id, "response", 10.2, "a.u.", actor_id="human-1", source_type=SourceType.MEASURED)
    evidence = research.create_evidence(
        run.id,
        "Measured response",
        {"measurement_id": measurement.id},
        actor_id="human-1",
        source_type=SourceType.MEASURED,
        confidence=0.95,
    )
    ai_evidence = research.create_evidence(
        run.id,
        "AI candidate explanation",
        {"claim": "Factor A may explain the response"},
        actor_id="agent-1",
        source_type=SourceType.AI_INFERRED,
        confidence=0.62,
    )

    graph = KnowledgeService(session)
    graph.create_relation(
        workspace_id=workspace.id,
        source_type="Evidence",
        source_id=str(evidence.id),
        relation_type="SUPPORTS",
        target_type="Hypothesis",
        target_id=str(hypothesis.id),
        actor_id="human-1",
        source_class=SourceType.MANUAL,
        confidence=0.95,
        provenance={"review": "human"},
    )

    eln = ELNService(session)
    notebook = eln.create_notebook(workspace.id, "Notebook", actor_id="human-1")
    entry, version = eln.create_entry(notebook.id, "Experiment review", "Measured response recorded.", actor_id="human-1")
    eln.sign_version(version.id, signer_id="human-1", meaning="reviewed", reason="Checked against source data")

    policy = PolicyEngine().evaluate(
        action="sign_record",
        actor_kind=ActorKind.AI,
        mode=ExecutionMode.FULL_POLICY_AUTONOMY,
        risk=RiskLevel.CRITICAL,
    )

    session.commit()

    assert ai_evidence.source_type == "AI_INFERRED"
    assert policy.effect == PolicyEffect.DENY
    assert DomainPackRegistry().list() == []
    assert GovernanceService(session).verify_audit_chain() is True

    version.content_markdown = "attempted overwrite"
    with pytest.raises(ImmutableRecordError):
        session.commit()
```

- [ ] **Step 2: Run the acceptance scenario**

Run:

```bash
python -m pytest tests/researchos_core/test_phase1_acceptance.py -q
```

Expected: PASS.

- [ ] **Step 3: Run the full core suite including architecture guard**

Run:

```bash
python -m pytest tests/researchos_core -q
```

Expected: PASS with zero forbidden-import violations.

- [ ] **Step 4: Commit**

```bash
git add tests/researchos_core/test_phase1_acceptance.py
git commit -m "test: add ResearchOS Core phase 1 acceptance workflow"
```

---

### Task 10: Document Standalone Operation and Add CI Verification

**Files:**
- Create: `researchos/README.md`
- Create: `.github/workflows/researchos-core.yml`
- Modify: `README.md`

**Interfaces:**
- Documents how to install/test/run ResearchOS Core independently of BioCult.
- CI installs only the root ResearchOS package and runs `tests/researchos_core`, demonstrating core independence from the legacy BioTech environment.

- [ ] **Step 1: Add standalone ResearchOS Core documentation**

Create `researchos/README.md` with these exact sections:

```markdown
# ResearchOS Core

ResearchOS Core is the domain-independent foundation of the ResearchOS architecture.
It manages research workspaces, hypotheses, experiments, evidence, ELN records,
knowledge relations, provenance, audit records, policies and Domain Pack registration.

## Boundary

ResearchOS Core does not depend on BioTech, BioCult, SBML, COBRA, OMICS,
bioreactors, chromatography or scale-up logic. Those capabilities are supplied by
Domain Packs and application adapters in later phases.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Test

```bash
python -m pytest tests/researchos_core -q
```

## Run API

```bash
python -m uvicorn "researchos.core.api.app:create_app" --factory --host 127.0.0.1 --port 8010
```

## Phase 1 Scope

Phase 1 includes Research Cycle, provenance/audit/versioning, immutable ELN,
basic Knowledge Graph, Policy Engine, Domain Pack Registry and REST contracts.
BioTech functionality remains outside the core.
```

- [ ] **Step 2: Add a concise root README pointer**

Add a section near the existing project overview in root `README.md`:

```markdown
## ResearchOS architecture

The repository is being evolved toward a layered architecture:

1. `ResearchOS Core` — domain-independent research foundation.
2. `BioTech Domain Pack` — biotechnology process, quality and scale-up capabilities.
3. `BioCult SUPER` — the Aspergillus/collagenase reference application.

The approved architecture and implementation plans are stored under
`docs/superpowers/specs/` and `docs/superpowers/plans/`.
```

Do not rewrite the current BioCult README sections in Phase 1.

- [ ] **Step 3: Add CI workflow**

Create `.github/workflows/researchos-core.yml`:

```yaml
name: ResearchOS Core

on:
  push:
    branches: [main, "design/**", "feature/**"]
  pull_request:

jobs:
  core-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e ".[dev]"
      - run: python -m pytest tests/researchos_core -q
```

This workflow intentionally does not install `BioCult-KB_Aspergillus_sydowii/web_app/requirements.txt`.

- [ ] **Step 4: Run final local verification**

Run:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/researchos_core -q
python -c "import researchos.core; print('ResearchOS Core import OK')"
```

Expected:

```text
all tests passed
ResearchOS Core import OK
```

- [ ] **Step 5: Inspect the dependency boundary one final time**

Run:

```bash
python -m pytest tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: PASS, with no import of BioCult, BioTech, COBRA, SBML or OMICS from `researchos/core`.

- [ ] **Step 6: Commit**

```bash
git add researchos/README.md README.md .github/workflows/researchos-core.yml
git commit -m "docs: document and verify standalone ResearchOS Core"
```

---

## Phase 1 Completion Gate

Do not begin Phase 2 until all of the following are true in one clean checkout:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/researchos_core -q
```

Required evidence:

1. The complete suite passes.
2. `researchos.core` imports without legacy BioCult requirements installed.
3. Architecture guard reports zero forbidden imports.
4. Audit-chain verification passes after a multi-step research workflow.
5. `AI_INFERRED` remains distinct from measured/observed evidence.
6. A signed ELN version rejects direct update and deletion.
7. Policy Engine denies AI signing, audit rewriting, locked-record mutation and technology-transfer approval even in full policy autonomy.
8. A generic research workflow works with zero Domain Packs registered.
9. REST contracts create a workspace and ELN records against an isolated SQLite database.
10. No existing BioCult computational or frontend module has been moved or rewritten.

## Deferred Explicitly to Later Plans

Phase 1 does not implement the following approved architecture. Each receives a later plan after Phase 1 verification:

- Prompt Registry, system roles, boundary prompts and AgentRun runtime.
- RAG/embeddings and semantic retrieval.
- Scientific Tool Gateway and MCP execution.
- BioTech Domain Pack entities and migration adapters.
- Producer/OMICS/SBML/FBA/dFBA integrations.
- Process Train, UnitOperation and MaterialStream domain behavior.
- ProductQualityPolicy, CQA/CPP/CMA and Quality Gates.
- Parametric equipment geometry and bidirectional geometry conversion.
- Chromatography/separation models.
- Online material-balance solver and live reconciliation.
- Target-driven scale-up, operation-specific scale policies and uncertainty optimization.
- Import Gateway, schema mapping, `.researchpkg` and reproducibility re-run.
- Technology Transfer workspace and team synchronization.
