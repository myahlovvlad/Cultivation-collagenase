# ResearchOS Core Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Phase 1 of ResearchOS Core as a standalone, domain-independent Python package with a canonical research cycle, provenance/audit/versioning, immutable ELN, a basic knowledge graph, a deterministic policy engine, a Domain Pack registry shell, stable REST contracts, and architecture tests proving that the core has no BioTech dependency.

**Architecture:** Add a new top-level `researchos` Python package beside the current BioCult implementation. ResearchOS Core owns generic research, ELN, knowledge, governance, policy and SDK contracts. Existing `BioCult-KB_Aspergillus_sydowii` code remains untouched in Phase 1 and is not imported by ResearchOS Core; later phases will integrate it through adapters and Domain Packs.

**Tech Stack:** Python 3.10+, FastAPI, Pydantic 2, SQLAlchemy 2, SQLite for the foundation persistence backend, pytest, HTTPX/TestClient.

**Spec:** `docs/superpowers/specs/2026-09-14-researchos-core-biotech-biocult-super-design.md`

## Global Constraints

- `ResearchOS Core` must run with no BioTech Domain Pack installed.
- `researchos/core` must not import `BioCult-KB_Aspergillus_sydowii`, `web_app`, `researchos.domain_packs`, COBRA, libSBML, Biopython or any biotechnology-specific implementation.
- Preserve the rule **AI proposes. Human approves. System records.**
- `OBSERVED`, `MEASURED`, `MANUAL`, `IMPORTED`, `CALCULATED`, `MODEL_PREDICTED`, `RULE_INFERRED`, `AI_INFERRED`, `EXPERT_APPROVED` and `REJECTED` remain explicit source classes.
- Signed or locked ELN versions are immutable; corrections create a new version.
- Audit and approval records are append-only.
- Every scientifically significant record has actor/source/version/provenance metadata and a content hash.
- Phase 1 uses SQLite/SQLAlchemy only. Do not add PostgreSQL, Neo4j, queues, vector databases, OMICS engines, SBML processing, scale-up solvers, material-balance solvers or technology-transfer workflows.
- Do not migrate or rewrite existing BioCult computational or frontend modules in this phase.
- Every task follows TDD: failing test, minimal implementation, passing test, commit.

---

## File Structure Locked for Phase 1

```text
pyproject.toml
researchos/
  __init__.py
  README.md
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
    sdk/
      __init__.py
      domain_pack.py
      registry.py
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

Do not create a BioTech package in Phase 1. Registry behavior is tested using a fake in-test Domain Pack.

---

### Task 1: Bootstrap the Standalone ResearchOS Core Package and Architecture Guard

**Files:**
- Create: `pyproject.toml`
- Create: `researchos/__init__.py`
- Create: `researchos/core/__init__.py`
- Create: `researchos/core/errors.py`
- Create: `tests/researchos_core/conftest.py`
- Create: `tests/researchos_core/architecture/test_core_boundary.py`

**Interfaces:**
- Produces importable package `researchos.core`.
- Produces base exceptions `ResearchOSError` and `DomainBoundaryError`.
- Establishes a static import guard for the core/domain boundary.

- [ ] **Step 1: Write the failing architecture tests**

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
    violations: list[tuple[str, str]] = []
    for path in Path("researchos/core").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                if name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    violations.append((str(path), name))
    assert violations == []
```

Create `tests/researchos_core/conftest.py` initially as:

```python
from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
```

- [ ] **Step 2: Verify the tests fail before implementation**

Run:

```bash
python -m pytest tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: failure because `researchos.core` does not exist.

- [ ] **Step 3: Create package metadata and minimal package**

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
__version__ = "0.1.0"
__all__ = ["core"]
```

Create `researchos/core/errors.py`:

```python
class ResearchOSError(Exception):
    """Base exception for ResearchOS Core."""


class DomainBoundaryError(ResearchOSError):
    """Raised when a forbidden core/domain dependency is detected."""


class ImmutableRecordError(ResearchOSError):
    """Raised when immutable data is changed or deleted."""


class ELNStateError(ResearchOSError):
    """Raised for invalid ELN state transitions."""


class DomainPackRegistrationError(ResearchOSError):
    """Raised when a Domain Pack cannot be registered safely."""
```

Create `researchos/core/__init__.py`:

```python
"""Domain-independent ResearchOS Core."""

from .errors import ResearchOSError

__all__ = ["ResearchOSError"]
```

- [ ] **Step 4: Install and verify the architecture guard passes**

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

### Task 2: Add Persistence, Scientific Source Types, Provenance, Versioning and Append-Only Audit

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
- Produces enums `SourceType`, `RecordStatus`, `ActorKind`.
- Produces `Base`, `ScientificRecordMixin`, `utcnow()`.
- Produces `Database` and `make_database(url: str) -> Database`.
- Produces `ProvenanceRecord`, `VersionRecord`, `AuditRecord`, `ApprovalRecord`.
- Produces `GovernanceService.append_audit`, `record_version`, `record_provenance`, `record_approval`, `verify_audit_chain`.

- [ ] **Step 1: Write failing governance tests**

Create `tests/researchos_core/test_database_and_governance.py`:

```python
import pytest
from sqlalchemy import inspect

from researchos.core.enums import SourceType
from researchos.core.errors import ImmutableRecordError
from researchos.core.services.governance import GovernanceService


def test_governance_tables_exist(database):
    names = set(inspect(database.engine).get_table_names())
    assert {"provenance_records", "version_records", "audit_records", "approval_records"} <= names


def test_audit_chain_is_hash_chained_and_append_only(session):
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
    with pytest.raises(ImmutableRecordError):
        session.commit()


def test_provenance_preserves_source_class(session):
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
    assert record.source_type == "MEASURED"
```

Replace `tests/researchos_core/conftest.py` with:

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

- [ ] **Step 2: Run and verify import failures**

```bash
python -m pytest tests/researchos_core/test_database_and_governance.py -q
```

Expected: failure because database/governance modules are not implemented.

- [ ] **Step 3: Implement source/status enums and canonical hashing**

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

Create `researchos/core/models/base.py`:

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

Create `researchos/core/db.py` with these behaviors:

- `make_database(url)` creates a SQLAlchemy 2 engine and `sessionmaker(expire_on_commit=False)`.
- For SQLite, register a connect listener that executes `PRAGMA foreign_keys=ON`.
- For `sqlite+pysqlite:///:memory:`, also use `StaticPool` and `check_same_thread=False`.
- `Database.create_schema()` imports only `researchos.core.models.*` modules, then calls `Base.metadata.create_all(engine)`.
- `Database.session()` is a context manager that closes the session but does not commit automatically.

Core shape:

```python
from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from researchos.core.models.base import Base


@dataclass
class Database:
    engine: Engine
    SessionLocal: sessionmaker

    def create_schema(self) -> None:
        from researchos.core.models import governance
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session: Session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
```

- [ ] **Step 5: Implement governance tables and immutable guards**

Create explicit `__tablename__` values and fields:

```text
ProvenanceRecord / provenance_records:
  id, entity_type, entity_id, source_type, source_reference,
  activity_type, actor_id, confidence, input_refs_json, created_at

VersionRecord / version_records:
  id, entity_type, entity_id, version, payload_json, payload_hash,
  created_at, created_by

AuditRecord / audit_records:
  id, created_at, actor_id, action, entity_type, entity_id,
  payload_json, previous_hash, record_hash

ApprovalRecord / approval_records:
  id, entity_type, entity_id, entity_version, actor_id, decision,
  meaning, reason, content_hash, created_at
```

Use `Text` for JSON strings in Phase 1. Add SQLAlchemy `before_update` and `before_delete` listeners for both `AuditRecord` and `ApprovalRecord`; each listener raises `ImmutableRecordError`.

- [ ] **Step 6: Implement GovernanceService**

Required public methods and semantics:

```text
append_audit(actor_id, action, entity_type, entity_id, payload) -> AuditRecord
record_version(entity_type, entity_id, version, payload, created_by) -> VersionRecord
record_provenance(entity_type, entity_id, source_type, source_reference,
                  activity_type, actor_id, confidence, input_refs) -> ProvenanceRecord
record_approval(entity_type, entity_id, entity_version, actor_id,
                decision, meaning, reason, content_hash) -> ApprovalRecord
verify_audit_chain() -> bool
```

`append_audit()` must:

1. Read the newest audit row by ID.
2. Capture one timestamp before hashing.
3. Build a canonical payload containing timestamp, actor, action, entity reference, payload and previous hash.
4. Compute SHA-256 with `canonical_json_hash`.
5. Insert and flush the record without committing.

`verify_audit_chain()` recomputes every hash in ascending ID order and verifies every `previous_hash` pointer.

- [ ] **Step 7: Run governance and boundary tests**

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

### Task 3: Implement Research Workspace and the Canonical Research Cycle

**Files:**
- Create: `researchos/core/models/research.py`
- Create: `researchos/core/schemas/__init__.py`
- Create: `researchos/core/schemas/research.py`
- Create: `researchos/core/services/research.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_research_cycle.py`

**Interfaces:**
- Produces generic research entities only.
- Every create operation writes a content hash, version record, provenance record and audit record.
- AI-origin evidence keeps `source_type=AI_INFERRED`; no service silently changes source class.

- [ ] **Step 1: Write the failing Research Cycle tests**

Create `tests/researchos_core/test_research_cycle.py`:

```python
from researchos.core.enums import SourceType
from researchos.core.services.research import ResearchService


def test_research_cycle_builds_from_workspace_to_result(session):
    service = ResearchService(session)
    workspace = service.create_workspace("Generic research", actor_id="researcher-1")
    program = service.create_program(workspace.id, "Program", actor_id="researcher-1")
    objective = service.create_objective(program.id, "Improve response", actor_id="researcher-1")
    question = service.create_question(objective.id, "What controls the response?", actor_id="researcher-1")
    hypothesis = service.create_hypothesis(
        objective.id,
        question.id,
        "Factor A controls the response",
        "Repeated variation suggests a controllable factor",
        actor_id="researcher-1",
    )
    design = service.create_experiment_design(
        objective.id,
        hypothesis.id,
        "Factor screening",
        {"factors": ["A", "B"]},
        actor_id="researcher-1",
    )
    protocol = service.create_protocol(
        design.id,
        "Screening protocol",
        "Run the predefined factor matrix.",
        actor_id="researcher-1",
    )
    run = service.create_experiment_run(
        workspace.id,
        design.id,
        protocol.id,
        "EXP-001",
        actor_id="researcher-1",
    )
    measurement = service.add_measurement(
        run.id,
        "response",
        42.0,
        "a.u.",
        actor_id="researcher-1",
        source_type=SourceType.MEASURED,
    )
    evidence = service.create_evidence(
        run.id,
        "Measured response",
        {"measurement_id": measurement.id},
        actor_id="researcher-1",
        source_type=SourceType.MEASURED,
        confidence=0.95,
    )
    result = service.create_result(
        run.id,
        "Screening result",
        "STATISTICAL_SUMMARY",
        {"best_factor": "A"},
        actor_id="researcher-1",
        source_type=SourceType.CALCULATED,
    )
    session.commit()

    assert result.run_id == run.id
    assert evidence.source_type == "MEASURED"
    assert hypothesis.version == 1


def test_ai_inference_is_not_reclassified(session):
    service = ResearchService(session)
    workspace = service.create_workspace("AI provenance study", actor_id="human-1")
    evidence = service.create_evidence(
        None,
        "Candidate explanation",
        {"claim": "possible mechanism"},
        actor_id="agent-1",
        source_type=SourceType.AI_INFERRED,
        confidence=0.61,
    )
    session.commit()
    assert workspace.id > 0
    assert evidence.source_type == "AI_INFERRED"
```

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_research_cycle.py -q
```

Expected: missing research model/service modules.

- [ ] **Step 3: Implement ORM entities with generic fields only**

All scientifically significant entities inherit `ScientificRecordMixin` and use explicit `__tablename__` values.

```text
ResearchWorkspace / research_workspaces:
  title, description
ResearchProgram / research_programs:
  workspace_id FK, title, description
ResearchObjective / research_objectives:
  program_id FK, title, description
ResearchQuestion / research_questions:
  objective_id FK, question_text
Hypothesis / hypotheses:
  objective_id FK, question_id nullable FK, statement, rationale
ExperimentDesign / experiment_designs:
  objective_id FK, hypothesis_id nullable FK, title, design_json
Protocol / protocols:
  experiment_design_id nullable FK, title, body_markdown
ExperimentRun / experiment_runs:
  workspace_id FK, experiment_design_id nullable FK, protocol_id nullable FK,
  title, started_at nullable, completed_at nullable
Observation / observations:
  run_id FK, text
Measurement / measurements:
  run_id FK, name, value, unit
Dataset / datasets:
  run_id nullable FK, title, uri nullable, media_type nullable, checksum nullable
Evidence / evidence:
  run_id nullable FK, title, payload_json
Result / results:
  run_id nullable FK, title, result_type, payload_json
Proposal / proposals:
  workspace_id FK, title, payload_json
Decision / decisions:
  proposal_id nullable FK, title, outcome, rationale
Artifact / artifacts:
  workspace_id FK, title, artifact_type, uri nullable, checksum nullable
```

Use `Text` for structured JSON payloads and canonical serialization with `canonical_json()`.

- [ ] **Step 4: Implement Pydantic 2 request/response schemas**

Use `ConfigDict(from_attributes=True)` for response models and explicit constraints for IDs, titles and confidence.

Representative exact request schemas:

```python
from pydantic import BaseModel, Field

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
    title: str = Field(min_length=1, max_length=255)
    payload: dict
    source_type: SourceType
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
```

Create analogous explicit schemas for program, objective, question, experiment design, protocol, run, measurement and result.

- [ ] **Step 5: Implement ResearchService**

Required methods:

```text
create_workspace(title, actor_id, description=None)
create_program(workspace_id, title, actor_id, description=None)
create_objective(program_id, title, actor_id, description=None)
create_question(objective_id, question_text, actor_id)
create_hypothesis(objective_id, question_id, statement, rationale, actor_id)
create_experiment_design(objective_id, hypothesis_id, title, design, actor_id)
create_protocol(experiment_design_id, title, body_markdown, actor_id)
create_experiment_run(workspace_id, experiment_design_id, protocol_id, title, actor_id)
add_observation(run_id, text, actor_id, source_type=OBSERVED)
add_measurement(run_id, name, value, unit, actor_id, source_type=MEASURED)
create_dataset(run_id, title, actor_id, source_type, uri=None, media_type=None, checksum=None)
create_evidence(run_id, title, payload, actor_id, source_type, confidence=None)
create_result(run_id, title, result_type, payload, actor_id, source_type)
create_proposal(workspace_id, title, payload, actor_id, source_type)
create_decision(proposal_id, title, outcome, rationale, actor_id)
```

Implement one private create finalizer with this sequence:

```text
serialize scientific payload
→ compute record_hash
→ session.add + flush
→ GovernanceService.record_version
→ GovernanceService.record_provenance
→ GovernanceService.append_audit
→ return entity without commit
```

`source_type` passed by the caller is preserved exactly. Validation may reject invalid enum values but must never promote inference to evidence class.

- [ ] **Step 6: Register research models and run tests**

Add a local import of `research` in `Database.create_schema()` and run:

```bash
python -m pytest tests/researchos_core/test_research_cycle.py tests/researchos_core/test_database_and_governance.py -q
```

Expected: pass.

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
- Create: `tests/researchos_core/test_eln.py`

**Interfaces:**
- Produces `Notebook`, `NotebookEntry`, `EntryVersion`, `Signature`, `ImmutableSnapshot`.
- Produces `ELNService.create_notebook`, `create_entry`, `create_revision`, `lock_version`, `sign_version`, `get_history`.
- Direct ORM mutation/deletion of a persisted locked version raises `ImmutableRecordError`.

- [ ] **Step 1: Write failing ELN tests**

```python
import pytest

from researchos.core.errors import ImmutableRecordError
from researchos.core.services.eln import ELNService
from researchos.core.services.research import ResearchService


def test_signature_locks_version_without_destroying_history(session):
    workspace = ResearchService(session).create_workspace("ELN study", actor_id="human-1")
    eln = ELNService(session)
    notebook = eln.create_notebook(workspace.id, "Main notebook", actor_id="human-1")
    entry, v1 = eln.create_entry(notebook.id, "Day 1", "Initial observation", actor_id="human-1")
    v2 = eln.create_revision(entry.id, "Corrected observation", actor_id="human-1", reason="Clarified wording")
    signature = eln.sign_version(v2.id, signer_id="human-1", meaning="performed", reason="Entry complete")
    session.commit()

    assert [item.version_number for item in eln.get_history(entry.id)] == [1, 2]
    assert signature.content_hash == v2.content_hash
    assert v2.locked_at is not None

    v2.content_markdown = "tampered"
    with pytest.raises(ImmutableRecordError):
        session.commit()


def test_locked_version_cannot_be_deleted(session):
    workspace = ResearchService(session).create_workspace("Delete guard", actor_id="human-1")
    eln = ELNService(session)
    notebook = eln.create_notebook(workspace.id, "Main", actor_id="human-1")
    entry, version = eln.create_entry(notebook.id, "Record", "Evidence", actor_id="human-1")
    eln.lock_version(version.id, actor_id="human-1", reason="Approved record")
    session.commit()

    session.delete(version)
    with pytest.raises(ImmutableRecordError):
        session.commit()
```

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_eln.py -q
```

Expected: missing ELN modules.

- [ ] **Step 3: Implement ELN tables**

```text
Notebook / notebooks:
  id, workspace_id FK, title, description nullable, created_at, created_by
NotebookEntry / notebook_entries:
  id, notebook_id FK, title, current_version_number, created_at, created_by
EntryVersion / entry_versions:
  id, entry_id FK, version_number, content_markdown, reason nullable,
  source_type, content_hash, created_at, created_by, locked_at nullable
Signature / signatures:
  id, entry_version_id FK, signer_id, meaning, reason, signed_at, content_hash
ImmutableSnapshot / immutable_snapshots:
  id, entry_version_id unique FK, payload_json, payload_hash, created_at
```

`NotebookEntry` stores identity/title only; editable content exists only in `EntryVersion` rows.

- [ ] **Step 4: Enforce hard immutability at the ORM layer**

Use SQLAlchemy inspection so the first transition `locked_at: None -> timestamp` is allowed while later updates are blocked:

```python
from sqlalchemy import event, inspect

from researchos.core.errors import ImmutableRecordError


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

- [ ] **Step 5: Implement ELNService**

Rules:

- `create_entry()` inserts `NotebookEntry` and version 1.
- `create_revision()` inserts a new row with `version_number=current+1`; it never edits prior content.
- `lock_version()` creates one `ImmutableSnapshot` from entry/version/content/hash, then sets `locked_at`.
- `sign_version()` verifies the content hash, creates `Signature`, creates/reuses the snapshot, sets `locked_at`, and records an immutable `ApprovalRecord` with the signature meaning.
- `get_history()` returns ascending version order.
- Create/revise/lock/sign actions write audit events; each new EntryVersion also writes a VersionRecord.

Required method signatures:

```text
create_notebook(workspace_id, title, actor_id, description=None)
create_entry(notebook_id, title, content_markdown, actor_id) -> (NotebookEntry, EntryVersion)
create_revision(entry_id, content_markdown, actor_id, reason) -> EntryVersion
lock_version(version_id, actor_id, reason) -> ImmutableSnapshot
sign_version(version_id, signer_id, meaning, reason) -> Signature
get_history(entry_id) -> list[EntryVersion]
```

- [ ] **Step 6: Add ELN Pydantic schemas, register models and run tests**

Create explicit request/response schemas for notebook, entry, revision, lock and signature. Add `eln` import to `Database.create_schema()`.

```bash
python -m pytest tests/researchos_core/test_eln.py tests/researchos_core/test_database_and_governance.py -q
```

Expected: pass.

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
- Modify: `researchos/core/enums.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_knowledge_graph.py`

**Interfaces:**
- Produces `KnowledgeEntity`, `KnowledgeRelation`, `Document`, `Source`, `Citation`.
- Produces `CoreRelationType`.
- `KnowledgeRelation` uses typed references so it can connect ResearchOS entities without forcing every node into one table.

- [ ] **Step 1: Write failing graph tests**

```python
from researchos.core.enums import SourceType
from researchos.core.services.knowledge import KnowledgeService
from researchos.core.services.research import ResearchService


def test_evidence_supports_hypothesis_with_provenance(session):
    research = ResearchService(session)
    workspace = research.create_workspace("Graph study", actor_id="human-1")
    program = research.create_program(workspace.id, "Program", actor_id="human-1")
    objective = research.create_objective(program.id, "Objective", actor_id="human-1")
    question = research.create_question(objective.id, "Question?", actor_id="human-1")
    hypothesis = research.create_hypothesis(objective.id, question.id, "H1", "Reason", actor_id="human-1")
    evidence = research.create_evidence(
        None,
        "Observed evidence",
        {"value": 1},
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

    assert relation.source_type_name == "Evidence"
    assert relation.relation_type == "SUPPORTS"
    neighbors = graph.neighbors("Hypothesis", str(hypothesis.id))
    assert neighbors[0].source_type_name == "Evidence"


def test_ai_knowledge_entity_keeps_ai_source_class(session):
    research = ResearchService(session)
    workspace = research.create_workspace("Knowledge study", actor_id="human-1")
    graph = KnowledgeService(session)
    entity = graph.create_entity(
        workspace_id=workspace.id,
        entity_type="Concept",
        label="Candidate mechanism",
        actor_id="agent-1",
        source_class=SourceType.AI_INFERRED,
        confidence=0.55,
    )
    session.commit()
    assert entity.source_type == "AI_INFERRED"
```

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_knowledge_graph.py -q
```

Expected: missing knowledge modules.

- [ ] **Step 3: Add core relation enum**

Add to `enums.py`:

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

- [ ] **Step 4: Implement knowledge tables**

```text
KnowledgeEntity / knowledge_entities:
  ScientificRecordMixin + workspace_id FK, entity_type, external_ref nullable,
  label, summary nullable
KnowledgeRelation / knowledge_relations:
  ScientificRecordMixin + workspace_id FK, source_type_name, source_id,
  relation_type, target_type_name, target_id, provenance_json
Document / documents:
  ScientificRecordMixin + workspace_id FK, title, media_type nullable,
  uri nullable, checksum nullable
Source / knowledge_sources:
  ScientificRecordMixin + workspace_id FK, title, source_kind, locator nullable
Citation / citations:
  ScientificRecordMixin + workspace_id FK, knowledge_source_id FK,
  entity_type_name, entity_id, locator nullable, quote_hash nullable
```

`source_type_name` and `target_type_name` are intentionally different from `ScientificRecordMixin.source_type`, which stores the scientific provenance class.

- [ ] **Step 5: Implement KnowledgeService**

Required methods:

```text
create_entity(workspace_id, entity_type, label, actor_id, source_class,
              confidence=None, summary=None, external_ref=None)
create_relation(workspace_id, source_type, source_id, relation_type,
                target_type, target_id, actor_id, source_class,
                confidence, provenance)
neighbors(entity_type, entity_id) -> list[KnowledgeRelation]
relations_for(workspace_id) -> list[KnowledgeRelation]
```

`create_relation()` validates `relation_type` against `CoreRelationType` in Phase 1, stores `provenance_json`, preserves `source_class`, computes a record hash and appends an audit event. Domain-specific relation registration is deferred.

- [ ] **Step 6: Register knowledge models and run tests**

```bash
python -m pytest tests/researchos_core/test_knowledge_graph.py tests/researchos_core/architecture/test_core_boundary.py -q
```

Expected: pass with zero forbidden imports.

- [ ] **Step 7: Commit**

```bash
git add researchos/core tests/researchos_core/test_knowledge_graph.py
git commit -m "feat: add provenance-aware ResearchOS knowledge graph"
```

---

### Task 6: Implement the Foundation Policy Engine and Hard AI Boundaries

**Files:**
- Create: `researchos/core/models/policy.py`
- Create: `researchos/core/schemas/policy.py`
- Create: `researchos/core/services/policy.py`
- Modify: `researchos/core/enums.py`
- Modify: `researchos/core/db.py`
- Create: `tests/researchos_core/test_policy_engine.py`

**Interfaces:**
- Produces `ExecutionMode`, `RiskLevel`, `PolicyEffect`.
- Produces persisted `PolicyProfile`.
- Produces deterministic `PolicyDecision` and `PolicyEngine.evaluate`.
- Hard boundaries do not depend on prompts or LLM behavior.

- [ ] **Step 1: Write failing policy tests**

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


def test_human_only_boundaries_remain_denied_to_ai():
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

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_policy_engine.py -q
```

- [ ] **Step 3: Add policy enums and table**

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

Create `PolicyProfile / policy_profiles` with fields `id`, `workspace_id`, `name`, `execution_mode`, `created_at`, `created_by`.

- [ ] **Step 4: Implement deterministic PolicyEngine**

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
        if actor_kind == ActorKind.AI and action in self.CANONICAL_MUTATIONS and mode in {ExecutionMode.OFF, ExecutionMode.SUPERVISED}:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Supervised canonical mutation")
        if actor_kind == ActorKind.AI and mode == ExecutionMode.LIMITED_AUTONOMY and risk in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Limited-autonomy risk threshold")
        if actor_kind != ActorKind.HUMAN and risk == RiskLevel.CRITICAL:
            return PolicyDecision(PolicyEffect.REQUIRE_APPROVAL, "Critical action requires accountable human review")
        return PolicyDecision(PolicyEffect.ALLOW, "Allowed by foundation policy")
```

- [ ] **Step 5: Add Pydantic policy contracts and register the model**

`PolicyEvaluateRequest` contains `action`, `actor_kind`, `mode`, `risk`; `PolicyEvaluateResponse` contains `effect`, `reason`. Add `policy` to `Database.create_schema()` imports.

- [ ] **Step 6: Run tests and commit**

```bash
python -m pytest tests/researchos_core/test_policy_engine.py -q
git add researchos/core tests/researchos_core/test_policy_engine.py
git commit -m "feat: add ResearchOS policy engine boundaries"
```

---

### Task 7: Implement the Domain Pack SDK and Registry Shell

**Files:**
- Create: `researchos/core/sdk/__init__.py`
- Create: `researchos/core/sdk/domain_pack.py`
- Create: `researchos/core/sdk/registry.py`
- Create: `tests/researchos_core/test_domain_pack_registry.py`

**Interfaces:**
- Produces `DomainPackManifest`, `DomainPack` protocol and `DomainPackRegistry`.
- Does not ship or import BioTech code.

- [ ] **Step 1: Write failing registry tests**

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


def test_registry_accepts_external_domain_pack():
    registry = DomainPackRegistry()
    registry.register(FakePack())
    assert registry.get("example-domain").manifest.name == "Example Domain"
    assert [pack.manifest.id for pack in registry.list()] == ["example-domain"]


def test_duplicate_pack_id_is_rejected():
    registry = DomainPackRegistry()
    registry.register(FakePack())
    with pytest.raises(DomainPackRegistrationError):
        registry.register(FakePack())
```

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_domain_pack_registry.py -q
```

- [ ] **Step 3: Implement exact manifest contract with safe defaults**

Create `researchos/core/sdk/domain_pack.py`:

```python
from typing import Protocol

from pydantic import BaseModel, Field


class DomainPackManifest(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    version: str
    entities: list[str] = Field(default_factory=list)
    relations: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)
    exports: list[str] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list)


class DomainPack(Protocol):
    manifest: DomainPackManifest
```

- [ ] **Step 4: Implement registry**

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

- [ ] **Step 5: Run registry plus architecture tests and commit**

```bash
python -m pytest tests/researchos_core/test_domain_pack_registry.py tests/researchos_core/architecture/test_core_boundary.py -q
git add researchos/core/sdk tests/researchos_core/test_domain_pack_registry.py
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
- Produces `create_app(database_url="sqlite+pysqlite:///./researchos.db", registry=None) -> FastAPI`.
- Routers are adapters only; all business rules remain in services.

- [ ] **Step 1: Write failing API tests**

```python
from fastapi.testclient import TestClient

from researchos.core.api.app import create_app


def test_api_exposes_foundation_contracts():
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
        json={"action": "sign_record", "actor_kind": "AI", "mode": "FULL_POLICY_AUTONOMY", "risk": "CRITICAL"},
    )
    assert policy.status_code == 200
    assert policy.json()["effect"] == "DENY"

    assert client.get("/api/domain-packs").json() == []


def test_openapi_contains_research_and_knowledge_routes():
    client = TestClient(create_app("sqlite+pysqlite:///:memory:"))
    paths = client.get("/openapi.json").json()["paths"]
    required = {
        "/api/workspaces",
        "/api/workspaces/{workspace_id}/programs",
        "/api/programs/{program_id}/objectives",
        "/api/objectives/{objective_id}/questions",
        "/api/questions/{question_id}/hypotheses",
        "/api/knowledge/entities",
        "/api/knowledge/relations",
    }
    assert required <= set(paths)
```

- [ ] **Step 2: Verify failure**

```bash
python -m pytest tests/researchos_core/test_api_contracts.py -q
```

- [ ] **Step 3: Implement dependency container and transaction boundary**

Create `api/deps.py` with `AppServices(database, registry)`, `get_services(request)` and `get_session()`. `get_session()` must commit on successful request, roll back on exception, then close. Phase 1 actor identity is `X-Actor-Id` with default `local-user`; authentication is explicitly deferred.

- [ ] **Step 4: Implement minimum REST surface**

Required routes:

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

Each route validates input with a Pydantic schema and delegates to one service method. Convert missing records to 404 and invalid state/immutability conflicts to 409. Do not duplicate service rules in router code.

- [ ] **Step 5: Implement app factory**

Create `create_app()` so it creates the database, creates schema, stores `AppServices` on `app.state`, registers all routers and exposes:

```python
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "researchos-core", "version": "0.1.0"}
```

- [ ] **Step 6: Run API and full core tests, then commit**

```bash
python -m pytest tests/researchos_core/test_api_contracts.py -q
python -m pytest tests/researchos_core -q
git add researchos/core/api tests/researchos_core/test_api_contracts.py
git commit -m "feat: expose ResearchOS Core REST contracts"
```

---

### Task 9: Add End-to-End Acceptance, Standalone Documentation and CI

**Files:**
- Create: `tests/researchos_core/test_phase1_acceptance.py`
- Create: `researchos/README.md`
- Create: `.github/workflows/researchos-core.yml`
- Modify: `README.md`

**Interfaces:**
- Proves the foundation works with zero Domain Packs.
- Proves core can be installed/tested without legacy BioCult requirements.

- [ ] **Step 1: Write the generic end-to-end acceptance test**

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

    KnowledgeService(session).create_relation(
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

    decision = PolicyEngine().evaluate(
        action="sign_record",
        actor_kind=ActorKind.AI,
        mode=ExecutionMode.FULL_POLICY_AUTONOMY,
        risk=RiskLevel.CRITICAL,
    )
    session.commit()

    assert ai_evidence.source_type == "AI_INFERRED"
    assert decision.effect == PolicyEffect.DENY
    assert DomainPackRegistry().list() == []
    assert GovernanceService(session).verify_audit_chain() is True

    version.content_markdown = "attempted overwrite"
    with pytest.raises(ImmutableRecordError):
        session.commit()
```

- [ ] **Step 2: Run acceptance and full suite**

```bash
python -m pytest tests/researchos_core/test_phase1_acceptance.py -q
python -m pytest tests/researchos_core -q
```

Expected: all tests pass and the architecture guard reports zero forbidden imports.

- [ ] **Step 3: Create standalone `researchos/README.md`**

Document:

```text
# ResearchOS Core
Purpose
Core/domain boundary
Install: python -m pip install -e ".[dev]"
Test: python -m pytest tests/researchos_core -q
Run API: python -m uvicorn "researchos.core.api.app:create_app" --factory --host 127.0.0.1 --port 8010
Phase 1 scope
Deferred BioTech functionality
```

The README must explicitly state that Core does not depend on BioCult, SBML, COBRA, OMICS, bioreactors, chromatography or scale-up.

- [ ] **Step 4: Add root README architecture pointer**

Add a short section without rewriting current BioCult documentation:

```markdown
## ResearchOS architecture

The repository is evolving toward three layers:

1. `ResearchOS Core` — domain-independent research foundation.
2. `BioTech Domain Pack` — biotechnology process, quality and scale-up capabilities.
3. `BioCult SUPER` — the Aspergillus/collagenase reference application.

Approved architecture and implementation plans are stored under
`docs/superpowers/specs/` and `docs/superpowers/plans/`.
```

- [ ] **Step 5: Add isolated GitHub Actions verification**

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

Do not install `BioCult-KB_Aspergillus_sydowii/web_app/requirements.txt` in this workflow.

- [ ] **Step 6: Final verification**

Run in a clean checkout:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/researchos_core -q
python -c "import researchos.core; print('ResearchOS Core import OK')"
```

Expected terminal evidence:

```text
all ResearchOS Core tests passed
ResearchOS Core import OK
```

- [ ] **Step 7: Commit**

```bash
git add tests/researchos_core/test_phase1_acceptance.py researchos/README.md README.md .github/workflows/researchos-core.yml
git commit -m "test: verify ResearchOS Core phase 1 foundation"
```

---

## Phase 1 Completion Gate

Do not begin Phase 2 until one clean checkout demonstrates all of the following:

1. `python -m pytest tests/researchos_core -q` passes.
2. `researchos.core` imports without legacy BioCult requirements installed.
3. The architecture test reports zero forbidden imports.
4. A multi-step research workflow produces a valid audit chain.
5. `AI_INFERRED` remains distinct from measured/observed evidence.
6. Audit and approval records reject updates/deletes.
7. A signed/locked ELN version rejects direct update and deletion.
8. Policy Engine denies AI signing, audit rewriting, locked-record mutation and technology-transfer approval even in full policy autonomy.
9. A generic research workflow succeeds with `DomainPackRegistry().list() == []`.
10. REST contracts create a workspace and ELN notebook against isolated SQLite.
11. No existing BioCult module has been moved, rewritten or imported by ResearchOS Core.

## Explicitly Deferred to Later Plans

The approved architecture below remains out of Phase 1 and must not leak into the foundation implementation:

- Prompt Registry, system roles, boundary prompts and `AgentRun` runtime.
- RAG, embeddings and semantic retrieval.
- Scientific Tool Gateway and MCP execution.
- BioTech Domain Pack entities and current BioCult migration adapters.
- Producer/OMICS/SBML/FBA/dFBA integration.
- Process Train, UnitOperation and MaterialStream behavior.
- ProductQualityPolicy, CQA/CPP/CMA and Quality Gates.
- Parametric equipment geometry and bidirectional geometry conversion.
- Chromatography and other purification simulation.
- Online material-balance solver and live reconciliation.
- Target-driven scale-up, operation-specific scale policies and uncertainty optimization.
- Import Gateway, schema mapping, `.researchpkg` and reproducibility re-run.
- Technology Transfer workspace, authorization, team collaboration and synchronization.
