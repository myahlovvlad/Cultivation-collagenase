# ResearchOS Core + BioTech Domain Pack + BioCult SUPER — Design Specification

**Date:** 2026-09-14  
**Repository:** `myahlovvlad/Cultivation-collagenase`  
**Status:** approved architecture specification; implementation not started  
**Reference use case:** *Aspergillus sydowii* collagenase technology development and scale-up

---

## 1. Product vision

The repository evolves from a domain-specific cultivation simulator into a universal research platform composed of three layers:

1. **ResearchOS Core** — domain-independent research operating system.
2. **BioTech Domain Pack** — biotechnology-specific entities, process models, scientific tools, quality and scale-up policies.
3. **BioCult SUPER** — the first reference application/workspace built on ResearchOS Core + BioTech Domain Pack.

Canonical dependency direction:

```text
ResearchOS Core
      ↑
BioTech Domain Pack
      ↑
BioCult SUPER
```

`ResearchOS Core` must not import or depend on biotechnology concepts such as strain, genome, medium, bioreactor, SBML, chromatography, kLa, FBA or OMICS.

The current `Cultivation-collagenase` implementation remains the first migration source and reference case, not the architecture of the universal core.

---

## 2. Core principles

### 2.1 Scientific integrity

The platform must distinguish explicitly between:

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

AI inference must never be represented as measured or experimentally observed fact.

### 2.2 Human-in-the-loop governance

Canonical principle:

> **AI proposes. Human approves. System records.**

A policy-controlled autonomous mode may be enabled by the user, but hard boundaries remain for signed records, provenance, approvals and regulated decisions.

### 2.3 Provenance first

Every scientifically significant entity, transformation, computation and relation must carry traceable provenance.

Minimum provenance fields:

```text
id
entity_type
version
status
created_at
created_by
source_type
source_reference
confidence
hash
supersedes
policy_id
```

### 2.4 Local-first + team-capable hybrid architecture

ResearchOS must support:

- autonomous local work;
- server-backed team work;
- users, roles and permissions;
- synchronization and conflict handling;
- future centralized storage without forcing it for single-user work.

### 2.5 Extensibility through Domain Packs

The core exposes a stable SDK. Domain Packs register domain entities, relations, validators, tools, importers, exporters, templates, UI schemas and policies.

---

## 3. Repository target structure

The target structure is conceptually:

```text
researchos/
  core/
    domain/
    research/
    eln/
    knowledge/
    governance/
    policies/
    import_export/
    reproducibility/
    agents/
    tools/
    services/
    repositories/
    api/
    sdk/

  domain_packs/
    biotech/
      entities/
      process/
      quality/
      scaleup/
      equipment/
      material_balance/
      omics/
      models/
      chromatography/
      separation/
      tools/
      importers/
      exporters/
      prompts/

  apps/
    biocult_super/
      backend/
      frontend/
      adapters/

legacy/
  current_biocult_kb/
```

The first migration may keep existing files physically in their current location while exposing them through adapters. The architecture must not require an immediate rewrite of legacy computational modules.

---

# Part I — ResearchOS Core

## 4. Research Workspace

The top-level working context is `ResearchWorkspace`.

A workspace groups:

```text
Research Program
Research Cycle
ELN
Knowledge Base
Knowledge Graph
Datasets
Models
Scientific Tools
Reports
Policies
Domain Packs
Users / Roles
Audit / Provenance
```

A workspace may activate one or multiple Domain Packs.

---

## 5. Canonical Research Cycle

The universal research workflow is:

```text
ResearchProgram
  ↓
ResearchObjective
  ↓
ResearchQuestion
  ↓
Hypothesis
  ↓
ExperimentDesign
  ↓
Protocol
  ↓
ExperimentRun
  ↓
Observation / Measurement / Dataset
  ↓
Evidence
  ↓
Analysis / ModelRun / ComputationRun
  ↓
Result
  ↓
Interpretation / Critique
  ↓
Proposal
  ↓
Approval
  ↓
Decision
  ↓
Next Hypothesis / Next Experiment
```

Core domain entities:

- `ResearchWorkspace`
- `ResearchProgram`
- `ResearchObjective`
- `ResearchQuestion`
- `Hypothesis`
- `ExperimentDesign`
- `Protocol`
- `ExperimentRun`
- `Observation`
- `Measurement`
- `Dataset`
- `Evidence`
- `ComputationalModel`
- `ComputationRun`
- `ModelRun`
- `Result`
- `Interpretation`
- `Critique`
- `Proposal`
- `ApprovalDecision`
- `Decision`
- `Artifact`
- `Source`
- `Citation`

These entities must remain domain-independent.

---

## 6. Electronic Laboratory Notebook (ELN)

ELN is the human narrative layer of ResearchOS and is separate from the Knowledge Graph and numeric Data Store.

Entities:

```text
Notebook
NotebookSection
NotebookEntry
EntryVersion
Attachment
Comment
Signature
Approval
ImmutableSnapshot
Amendment
```

### 6.1 Versioning

Entries are append-versioned:

```text
Entry v1
  ↓ superseded_by
Entry v2
  ↓ superseded_by
Entry v3
```

Historical versions are never overwritten.

### 6.2 Lifecycle

```text
DRAFT
→ IN_REVIEW
→ APPROVED
→ SIGNED
→ LOCKED
```

A `LOCKED` record is immutable. Corrections create an `Amendment` or new version with explicit linkage.

### 6.3 Electronic signatures

`SignatureRecord` includes:

```text
actor_id
entity_type
entity_id
entity_version
meaning
signed_at
content_hash
reason
```

Supported meanings include:

- performed
- reviewed
- approved
- witnessed

AI must never create or impersonate a human signature.

### 6.4 ELN templates

Core templates include:

- Daily Research Note
- Experiment Record
- Protocol Deviation
- Observation
- Investigation
- Model Run
- Literature Review
- Decision Record
- Meeting Note

Domain Packs may register additional templates.

### 6.5 Embedded entities

ELN entries may embed links to datasets, experiments, hypotheses, models, results and Domain Pack entities.

Example conceptual references:

```text
@dataset("DS-042")
@experiment("EXP-042")
@hypothesis("H-17")
@modelrun("DFBA-122")
```

---

## 7. Knowledge Base + Knowledge Graph + Semantic Retrieval

ResearchOS uses a hybrid knowledge architecture:

```text
Documents / ELN
        +
Structured Entities
        +
Knowledge Graph
        +
Semantic Search / RAG
```

### 7.1 Knowledge entities

Core entities:

- `KnowledgeEntity`
- `KnowledgeRelation`
- `Document`
- `Source`
- `Citation`
- `Chunk`
- `EmbeddingReference`

### 7.2 Core relations

Stable core relations include:

```text
PART_OF
DERIVED_FROM
GENERATED_BY
SUPPORTS
CONTRADICTS
REFERENCES
USES
PRODUCES
TESTS
SUPERSEDES
BASED_ON
RESOLVES
```

Domain Packs register additional relation types.

Each relation carries provenance, confidence, version and status.

### 7.3 AI retrieval context

AI context is assembled from four sources:

1. Document retrieval.
2. Knowledge Graph neighborhood traversal.
3. Structured Research Core entities.
4. ELN history.

The Context Builder must never silently merge inferred and observed facts.

---

## 8. Governance and policy engine

Core governance entities:

```text
Actor
Role
Permission
Policy
PolicyDecision
ProvenanceRecord
AuditRecord
VersionRecord
ApprovalRecord
```

Policy evaluation returns one of:

```text
ALLOW
REQUIRE_APPROVAL
DENY
```

Risk levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
FORBIDDEN
```

Hard boundaries include:

- no deletion or mutation of signed immutable records;
- no modification of audit history;
- no removal of provenance;
- no conversion of AI inference into observed fact;
- no AI-generated human signature;
- no autonomous final technology-transfer approval.

---

# Part II — ResearchOS Agent Framework

## 9. System roles

The default system roles are:

1. `Research Orchestrator`
2. `Research Planner`
3. `Evidence Analyst`
4. `Hypothesis & Falsification Agent`
5. `Scientific Tool Agent`
6. `Data Analyst`
7. `Knowledge Curator`
8. `Scale-up & Technology Transfer Engineer`
9. `Validation & Compliance Specialist`
10. `Report & Documentation Agent`

Roles are formal capability profiles, not personalities.

---

## 10. Prompt hierarchy

Prompt composition is versioned and layered:

```text
1. Platform System Prompt
2. Governance / Boundary Prompt
3. Role Prompt
4. Domain Pack Prompt
5. Workflow / Task Prompt
```

Prompt artifacts are stored in the repository and versioned.

Example structure:

```text
agents/prompts/
  platform/
  boundaries/
  roles/
  domains/
  workflows/
```

Each prompt manifest contains:

```text
prompt_id
version
inherits
compatible_models
allowed_tools
forbidden_actions
required_context
required_outputs
approval_policy
content_hash
```

Prompt instructions do not replace code-level policy enforcement.

---

## 11. AI operating modes

User-selectable modes:

```text
SUPERVISED
LIMITED_AUTONOMY
FULL_POLICY_AUTONOMY
```

### SUPERVISED

AI may analyze, retrieve, calculate, run safe tools and create drafts/proposals. Canonical mutations require explicit human approval.

### LIMITED_AUTONOMY / FULL_POLICY_AUTONOMY

AI may execute only actions explicitly permitted by active policy.

Even in autonomous mode, the following remain human-only or forbidden:

- signing records;
- final regulated approvals;
- final technology-transfer approval;
- erasing provenance;
- rewriting audit history;
- deleting immutable evidence;
- reclassifying AI inference as measured evidence.

---

## 12. AgentRun provenance

Every AI execution creates `AgentRun`:

```text
agent_role
prompt_versions
model_provider
model_name
model_version
context_hash
retrieved_sources
tools_used
policy_profile
input
output
created_artifacts
approval_status
run_hash
```

This enables traceability of AI-mediated scientific decisions.

---

# Part III — Scientific Tool Gateway

## 13. Tool abstraction

ResearchOS integrates external scientific engines through a stable gateway.

```text
ResearchOS
  ↓
Scientific Tool Gateway
  ↓
Tool Provider
  ↓
Execution Backend
  ↓
Result Artifact + Provenance
```

ResearchOS depends on tool capabilities and contracts, not vendor implementation details.

### 13.1 Tool capability contract

Each tool registers:

```text
id
name
provider
version
domain
capability_type
input_schema
output_schema
execution_modes
risk
permissions
```

### 13.2 Execution backends

Foundation support:

- Local Python
- CLI
- REST API
- MCP

Future backends:

- Docker / Podman
- HPC
- cloud execution
- desktop application adapters

### 13.3 Job lifecycle

```text
CREATED
→ VALIDATING
→ WAITING_APPROVAL
→ QUEUED
→ RUNNING
→ COMPLETED
```

Alternative terminal states:

```text
FAILED
CANCELLED
REJECTED
TIMEOUT
```

Computation provenance must include software/tool versions, parameters, input hashes and output hashes.

---

# Part IV — Import, Export and Reproducibility

## 14. Import pipeline

Import is staged and traceable:

```text
External Source
  ↓
Importer / Connector
  ↓
Staging Area
  ↓
Validation
  ↓
Schema Mapping
  ↓
Entity Resolution
  ↓
Human Review / Policy
  ↓
Canonical State
```

Import entities:

```text
ImportSession
ImportSource
ImportArtifact
ImportMapping
ImportValidation
ImportConflict
TransformationRecord
ImportProfile
```

Raw source data is immutable.

### 14.1 Data layers

```text
RAW
 ↓
CLEANED / NORMALIZED
 ↓
CANONICAL
```

### 14.2 Universal import formats

Core:

- CSV / TSV
- XLSX
- JSON / JSONL
- XML
- YAML
- Parquet
- PDF
- DOCX
- Markdown
- HTML
- TXT
- common images and ZIP packages

Scientific formats are added by Domain Packs.

### 14.3 Schema mapping and units

ResearchOS preserves both original and normalized representations:

```text
original_value
original_unit
normalized_value
normalized_unit
```

AI may suggest mappings but transformations must be recorded explicitly.

### 14.4 Validation levels

1. Structural.
2. Type.
3. Unit.
4. Range.
5. Semantic.
6. Cross-record.
7. Domain-specific.

Every import generates a `DataQualityReport`.

---

## 15. Export and interchange

Human-readable exports:

- PDF
- DOCX
- XLSX
- CSV
- HTML
- Markdown
- JSON

Knowledge export:

- JSON-LD
- RDF/Turtle
- GraphML

Provenance export follows an entity/activity/agent model compatible in concept with W3C PROV.

Domain Packs add scientific formats.

---

## 16. Research Package

ResearchOS defines a portable archive format:

```text
*.researchpkg
```

Conceptual contents:

```text
manifest.json
workspace.json
research/
eln/
knowledge/
datasets/
models/
tools/
provenance/
audit/
domain/
exports/
```

Importing a package reconstructs a workspace while preserving provenance and version history.

---

## 17. Reproducibility engine

Every computation stores a reproducibility manifest:

```text
tool
tool_version
environment
dependencies
input_hashes
parameters
random_seed
model_version
dataset_versions
execution_timestamp
outputs
output_hashes
```

`Reproduce Run` may return:

```text
REPRODUCED_EXACTLY
REPRODUCED_WITH_TOLERANCE
DIFFERENT_RESULT
NOT_REPRODUCIBLE
```

Dataset lineage must be queryable and visualizable from raw import to final decision.

---

# Part V — Domain Pack SDK

## 18. Domain Pack contract

A Domain Pack may register:

```text
entity schemas
relation schemas
validators
ELN templates
scientific tools
importers
exporters
UI schemas
prompt fragments
policies
calculators
```

Conceptual manifest:

```yaml
id: biotech
name: BioTech
version: 1.0.0
entities: []
relations: []
tools: []
imports: []
exports: []
policies: []
```

The Domain Pack SDK must preserve strict one-way dependency on ResearchOS Core.

---

# Part VI — BioTech Domain Pack

## 19. BioTech domain model

Primary domain entities:

```text
Producer
BioObject
Medium
ProcessDefinition
ProcessTrain
UnitOperation
MaterialStream
Equipment
EquipmentConfiguration
OmicsAsset
Product
ProductQualityProfile
ScaleUpStudy
TechnologyTransferPackage
```

### 19.1 Producer and OMICS

`Producer` is the biological root entity. OMICS datasets are separate linked assets, not fields inside one producer record.

```text
Producer
 ├─ HAS_GENOME → GenomeAsset
 ├─ HAS_TRANSCRIPTOME → TranscriptomeAsset
 ├─ HAS_PROTEOME → ProteomeAsset
 ├─ HAS_METABOLOME → MetabolomeAsset
 ├─ HAS_FLUXOME → FluxomeAsset
 └─ HAS_MODEL → ComputationalModel
```

OMICS assets preserve source, accession, experimental condition, pipeline, software versions, quality metrics and provenance.

### 19.2 BioObject

`BioObject` is a typed biological entity supporting, for example:

- Protein
- Enzyme
- Metabolite
- Product
- Biomass
- CellPopulation
- BiologicalMaterial

### 19.3 Medium

Medium composition is versioned. Changes to formulation create new versions rather than overwriting historical recipes.

---

## 20. Model layer and cross-scale relations

BioTech registers support for:

- SBML
- SED-ML
- COMBINE/OMEX
- GEM
- FBA
- dFBA
- transcriptome-constrained models
- future FMU/COPASI/external models

`CrossScaleLink` connects scales through an explicit transformation:

```text
source_entity
target_entity
transformation
model
units
uncertainty
confidence
provenance
```

Example chain:

```text
QM parameter
  ↓
enzyme parameter
  ↓
reaction constraint
  ↓
cellular flux
  ↓
OUR / qS / qP
  ↓
bioreactor state
```

---

# Part VII — End-to-End Biotechnology Process Train

## 21. Process hierarchy

The process is not represented as only `batch/fed-batch/continuous`. BioTech uses:

```text
ProcessDefinition
  ↓
ProcessTrain
  ↓
UnitOperation[]
  ↓
OperationStep[]
```

Unit operation groups:

### 21.1 Upstream processing

- MediaPreparation
- InoculumPreparation
- Cultivation
  - Batch
  - FedBatch
  - Continuous
  - Perfusion
- HarvestPreparation

### 21.2 Primary recovery

- Centrifugation
- DepthFiltration
- Microfiltration
- CellDisruption
- Clarification

### 21.3 Purification

- Precipitation
- Extraction
- Chromatography
- Ultrafiltration
- Diafiltration
- Crystallization
- Adsorption

### 21.4 Final processing

- Concentration
- Formulation
- SterileFiltration
- Drying
- Lyophilization
- Filling
- Storage

Domain extensions may register additional operations.

---

## 22. Material streams

Unit operations exchange typed `MaterialStream` objects.

```text
MaterialStream
├── total_mass_flow
├── volumetric_flow
├── temperature
├── pressure
├── pH
├── density
├── phase
└── components[]
    ├── substance
    ├── concentration
    ├── mass_flow
    ├── molar_flow
    └── uncertainty
```

Process Train therefore becomes a directed material-flow graph rather than a flat list of steps.

---

# Part VIII — Product Quality and Control Strategy

## 23. Product Quality Profile

Quality is modeled as a first-class domain layer.

```text
Product
  ↓
ProductQualityProfile
  ├── TargetAttribute[]
  ├── QualityAttribute[]
  ├── Specification[]
  ├── AcceptanceCriterion[]
  ├── AnalyticalMethod[]
  ├── SamplingPlan[]
  └── ControlStrategy
```

Value semantics distinguish:

```text
TARGET
SPECIFICATION
ACTION_LIMIT
WARNING_LIMIT
OBSERVED
PREDICTED
```

### 23.1 CQA / CPP / CMA model

ResearchOS stores explicit quality-impact relations between:

- Critical Quality Attributes (CQA)
- Critical Process Parameters (CPP)
- Critical Material Attributes (CMA)

`QualityImpactRelation` contains mechanism, effect direction, effect strength, evidence, confidence, scale dependency and risk.

### 23.2 ProductQualityPolicy

Defines:

```text
target product profile
CQA definitions
specifications
warning/action limits
sampling policy
analytical methods
release criteria
quality gates
deviation handling
required evidence
required approvals
```

### 23.3 Quality gates

Each process boundary may define a `QualityGate`.

States:

```text
PASS
PASS_WITH_DEVIATION
HOLD
FAIL
UNKNOWN
```

`UNKNOWN` is mandatory when evidence is insufficient.

---

# Part IX — Parametric Equipment Geometry

## 24. Canonical parametric equipment model

Equipment geometry is a computational model, not a decorative 3D asset.

```text
Equipment
  ↓
ParametricGeometry
  ├── dimensions
  ├── topology
  ├── internals
  ├── connections
  ├── materials
  ├── operating_limits
  └── coordinate_system
```

### 24.1 Bioreactor geometry

Includes at minimum:

- vessel diameter/height;
- head/bottom geometry;
- total and working volume;
- impellers and axial positions;
- baffles;
- sparger;
- jacket/coils;
- probes;
- ports/nozzles.

### 24.2 Chromatography equipment geometry

Includes at minimum:

- column diameter;
- bed height and volume;
- distributor geometry;
- frit geometry;
- tubing;
- valve network;
- pump limits;
- detector positions;
- dead volume.

Additional unit operations register their own parametric schemas.

### 24.3 Bidirectional geometry converter

Canonical layers:

```text
ResearchOS ParametricGeometry
        ↕
Engineering representation
        ↕
Visualization representation
```

Target interchange representations include STEP/BREP-oriented engineering formats and glTF/STL-style visualization formats.

Reverse conversion must report fidelity explicitly:

```text
EXACT_IMPORT
PARAMETER_RECOVERY
APPROXIMATED_RECONSTRUCTION
MANUAL_CONFIRMATION_REQUIRED
```

The system must never present approximate mesh-to-parameter reconstruction as exact geometry.

Geometry changes trigger dependent recalculation through a dependency graph.

---

# Part X — Chromatography and Other Purification Operations

## 25. Chromatography module

Chromatography is a dedicated domain subsystem.

```text
ChromatographyOperation
├── Column
├── Resin
├── MobilePhase
├── Sample
├── LoadingStep
├── WashStep
├── ElutionStep
├── RegenerationStep
├── CIPStep
├── Chromatogram
├── Fraction[]
└── Pool[]
```

Key parameters include:

- column geometry;
- resin and particle size;
- linear velocity;
- flow rate;
- residence time;
- pressure drop;
- sample concentration and load;
- DBC;
- recovery;
- purity;
- resolution;
- peak asymmetry.

Other separation/purification operations follow the same plugin-style UnitOperation interface with their own scale rules.

---

# Part XI — Material Balance Engine

## 26. Online material balances

ResearchOS provides a material-balance engine over the Process Train.

For each unit operation:

```text
Input Stream(s)
      ↓
UnitOperation
      ↓
Output Stream(s)
```

The engine supports:

- total mass balances;
- component balances;
- batch accumulation;
- continuous generation/consumption;
- cumulative recovery;
- stage recovery;
- losses and waste;
- uncertainty propagation.

### 26.1 Interactive online recalculation

Changing an upstream parameter triggers downstream recalculation.

Example:

```text
feed concentration
  ↓
cultivation balance
  ↓
harvest volume
  ↓
chromatography load
  ↓
buffer consumption
  ↓
final yield
```

### 26.2 Live process balance

Future live mode may ingest instrument/PLC/API measurements and perform continuous balance reconciliation.

### 26.3 Data reconciliation

Balance closure states:

```text
BALANCE_OK
WARNING
BALANCE_NOT_CLOSED
```

Measured inconsistencies are reported; raw measurements are never silently overwritten.

### 26.4 Balance scenarios

`BalanceScenario` compares laboratory, pilot and industrial scales for raw materials, buffers, solvents, water, waste, yield, cycle time and equipment load.

---

# Part XII — Technology Scale-up Policy

## 27. Scale-up as policy-controlled engineering workflow

Scale-up is not a single formula. ResearchOS uses a `ScalePolicyRegistry`.

```text
CultivationScalePolicy
ChromatographyScalePolicy
FiltrationScalePolicy
CentrifugationScalePolicy
UFDFScalePolicy
ExtractionScalePolicy
CustomScalePolicy
```

### 27.1 Operation-specific criteria

Cultivation examples:

- kLa
- P/V
- tip speed
- mixing time
- OTR/OUR
- gas velocity
- shear
- heat removal

Chromatography examples:

- bed height
- residence time
- linear velocity
- DBC
- load density
- pressure drop
- column geometry

Filtration examples:

- flux
- TMP
- membrane area
- loading
- fouling behavior

Centrifugation examples:

- Sigma factor
- centrifugal acceleration
- flow rate
- residence time
- solids loading

---

## 28. Target-driven scale-up

Users define `ScaleUpTargetProfile` rather than only source/target volume.

Target profile may contain:

```text
target scale
product targets
process targets
hard constraints
soft constraints
optimization objectives
equipment constraints
quality constraints
risk tolerance
acceptable uncertainty
```

Constraint types:

```text
HardConstraint
SoftConstraint
OptimizationTarget
```

If constraints cannot be satisfied, the engine returns `NO_FEASIBLE_SOLUTION` and reports conflicting requirements.

---

## 29. Scale-up study

`ScaleUpStudy` contains:

```text
SourceScale
TargetScale
ScaleStage[]
ProcessDefinition
EquipmentConfiguration
CPP
CQA
ScaleCriterion[]
ScaleConstraint[]
ModelRun[]
Evidence[]
Risk[]
PilotExperiment[]
Prediction[]
ResidualUncertainty[]
TransferDecision
```

Scale-up paths may contain intermediate stages such as:

```text
2 L → 20 L → 200 L → 2 000 L → 10 000 L
```

The system stores evidence and uncertainty for every transition.

### 29.1 Scale risk

`ScaleRisk` contains hazard, cause, consequence, probability, severity, detectability, evidence, mitigation and residual risk.

### 29.2 Knowledge gaps and uncertainty

The system may create explicit `KnowledgeGap` objects when uncertainty blocks a scale decision and propose a pilot experiment to reduce that uncertainty.

---

# Part XIII — Technology Transfer

## 30. Technology Transfer Workspace

The technology-transfer workflow is:

```text
Lab process
 ↓
Process characterization
 ↓
CPP/CQA identification
 ↓
Scale-up hypothesis
 ↓
Digital prediction
 ↓
Risk assessment
 ↓
Pilot experiment
 ↓
Model recalibration
 ↓
Industrial prediction
 ↓
TechnologyTransferPackage
 ↓
Human approval
```

`TechnologyTransferPackage` includes:

- ProcessDescription
- ApprovedProtocolVersions
- RawMaterialDefinitions
- EquipmentRequirements
- CPP/CQA Matrix
- OperatingRanges
- Scale-up Basis
- Models
- Pilot Evidence
- Deviations
- Risk Assessment
- Control Strategy
- Sampling Strategy
- Knowledge Gaps
- Residual Risks
- Training Materials
- References
- Audit Trail
- Approvals

AI may produce `TRANSFER_RECOMMENDED`, but only an accountable human actor may produce `TRANSFER_APPROVED`.

---

# Part XIV — BioCult SUPER reference application

## 31. Reference use case

BioCult SUPER is the first reference workspace:

```text
ResearchOS Core
      +
BioTech Domain Pack
      +
Aspergillus sydowii collagenase workspace
      =
BioCult SUPER
```

Existing repository assets become migration sources or providers:

- GEM/FBA/SBML;
- dFBA;
- process simulation;
- transcriptome weighting;
- OMICS pipeline;
- reactor physics;
- DoE;
- scaling;
- recommendations;
- audit;
- current frontend and 3D assets.

They must be integrated through adapters rather than copied into ResearchOS Core.

---

# Part XV — Implementation boundaries

## 32. Phase decomposition

The full architecture is intentionally larger than a single implementation milestone.

### Phase 1 — ResearchOS Core Foundation

Implement first:

- package boundary for ResearchOS Core;
- Research Workspace;
- Research Cycle entities;
- provenance/audit/version foundation;
- ELN with immutable version model;
- basic Knowledge Graph;
- basic policy engine;
- domain-pack registry shell;
- REST contracts;
- tests proving ResearchOS Core has no BioTech imports.

### Phase 2 — Knowledge + Agent Foundation

- semantic retrieval/RAG interfaces;
- Prompt Registry;
- Role Registry;
- AgentRun;
- Supervised/autonomous policy profiles;
- Scientific Tool Gateway foundation.

### Phase 3 — BioTech Domain Pack Foundation

- Producer/BioObject/Medium;
- ProcessTrain/UnitOperation/MaterialStream;
- ProductQualityProfile;
- equipment and parametric geometry schemas;
- migration adapters for current BioCult models.

### Phase 4 — Scale-up + Quality + Material Balance

- material-balance engine;
- ProductQualityPolicy;
- ScalePolicyRegistry;
- cultivation and chromatography scale policies;
- ScaleUpStudy;
- online recalculation and uncertainty handling.

### Phase 5 — Import/Export/Reproducibility

- Import Gateway;
- schema mapping;
- DataQualityReport;
- scientific import/export;
- `.researchpkg`;
- reproducibility manifests and re-run.

### Phase 6 — Technology Transfer + Team Collaboration

- TechnologyTransferPackage;
- advanced approvals;
- role-based collaboration;
- synchronization;
- team server mode.

The next implementation plan must target **Phase 1 only**. Later phases receive separate plans after the preceding foundation is verified.

---

## 33. Architectural acceptance criteria

The architecture is considered correctly implemented when all of the following remain true:

1. `ResearchOS Core` can run without BioTech Domain Pack installed.
2. BioTech entities are registered only through the Domain Pack interface.
3. AI inference cannot silently become observed evidence.
4. Signed/locked ELN records are immutable.
5. Every computation has input/output provenance.
6. Every import preserves its raw source and transformation history.
7. Domain-specific scale-up logic is not embedded in ResearchOS Core.
8. Unit operations exchange typed material streams.
9. Product quality targets and hard constraints can block an otherwise numerically valid scale-up.
10. Geometry conversions report reconstruction fidelity instead of claiming false exactness.
11. Material balances preserve component lineage and expose closure errors.
12. BioCult SUPER uses ResearchOS through public contracts/adapters rather than private coupling.
13. Autonomous AI remains subject to Policy Engine hard boundaries.
14. Final technology-transfer approval remains human-only.
15. Existing BioCult functionality remains usable during incremental migration.

---

## 34. Non-goals of Phase 1

Phase 1 does **not** implement:

- full OMICS processing;
- industrial CFD/QM engines;
- complete SBML visual editor;
- production-grade chromatography simulation;
- full material-balance solver;
- technology-transfer workflow;
- PostgreSQL/Neo4j migration;
- distributed job queues;
- real-time PLC integration;
- final GxP validation package.

These are explicit later phases, not hidden requirements of the foundation milestone.

---

## 35. Final architecture statement

ResearchOS is a domain-independent, provenance-first research operating system that manages hypotheses, experiments, evidence, knowledge, ELN records, computational tools, AI proposals, policies, imports, exports and reproducibility.

BioTech Domain Pack extends ResearchOS with end-to-end biotechnology development: producer and OMICS context, upstream processing, recovery and purification, parametric equipment models, product-quality control, online material balances, operation-specific scale-up policies, pilot studies and technology transfer.

BioCult SUPER is the first concrete application of this architecture and uses the existing *Aspergillus sydowii* collagenase project as a reference scientific workspace.
