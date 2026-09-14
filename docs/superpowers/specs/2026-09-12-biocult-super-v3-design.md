# BioCult SUPER v3 — архитектура AI-native multiscale research platform

Дата: 2026-09-12  
Репозиторий: `myahlovvlad/Cultivation-collagenase`  
Статус: design specification, до реализации

## 1. Product vision

BioCult SUPER — предиктивная биоаналитическая платформа поддержки наукоёмких исследований в биотехнологии.

Платформа не заменяет специализированные научные пакеты. Она оркестрирует исследовательский цикл, связывает знания, гипотезы, эксперименты, экспериментальные данные, вычислительные модели, экспертные правила и внешние scientific engines в единый трассируемый human-in-the-loop workflow.

Канонический принцип:

> AI proposes. Human approves. System records.

AI может анализировать, интерпретировать, критиковать, формировать гипотезы, проектировать варианты экспериментов и вызывать вычислительные инструменты. AI не может напрямую изменять canonical scientific state без явного подтверждения человека.

## 2. Scientific idea

Исходная научная идея проекта — моделировать эмерджентность биотехнологических процессов на четырёх доменных уровнях и связывать микро- и макропроцессы:

1. Quantum / chemical level
2. Molecular-genetic level
3. Cellular level
4. Bioprocess / bioreactor level

BioCult SUPER не реализует все физические и биологические модели самостоятельно. Для каждого уровня платформа подключает специализированные внешние engines и связывает их результаты через единые contracts, provenance и cross-scale relations.

Пример cross-scale chain:

```text
QM / molecular parameter
    ↓
enzyme activity / binding parameter
    ↓
gene / protein / pathway constraint
    ↓
cellular flux / OUR / qS / qP / μ
    ↓
reactor oxygen demand / mass transfer / mixing
    ↓
DO / temperature / shear / pH environment
    ↑
cellular constraint feedback
```

## 3. Что является продуктом, а что — компонентом

BioCult SUPER не является отдельной LIMS, ELN, CAD, CFD, QM или bioinformatics системой.

Платформа использует их как подключаемые компоненты:

- ELN — научный журнал и история исследования;
- Knowledge Base / Knowledge Graph — структурированная память;
- Experimental Data Store — измерения и datasets;
- Expert System — детерминированные и экспертные правила;
- Computational Engines — модели, статистика, DoE, digital twin;
- Scientific Tool Gateway — запуск внешних инструментов;
- MCP/API facade — управляемый AI-интерфейс;
- Connector Framework — интеграции с внешними системами;
- Proposal Workspace — human-in-the-loop approval boundary.

`Cultivation-collagenase` становится первым reference use case платформы: культивирование `Aspergillus sydowii` как продуцента коллагенолитической активности.

## 4. Центральный research workflow

Главный объект системы — Research Cycle.

```text
Research Program
    ↓
Research Objective
    ↓
Research Question
    ↓
Hypothesis
    ↓
Experiment Design / DoE
    ↓
Protocol
    ↓
Experiment Run
    ↓
Observations + Measurements + Files
    ↓
Evidence
    ↓
Computational Analysis
    ↓
Expert / AI Interpretation
    ↓
Critique / Falsification
    ↓
Proposal
    ↓
Human Approval
    ↓
Decision
    ↓
Next Hypothesis / Next Experiment
```

Платформа должна сохранять не только данные экспериментов, но и историю изменения знания.

## 5. Основные доменные сущности

### 5.1 Research domain

- `ResearchProgram`
- `ResearchObjective`
- `ResearchQuestion`
- `Hypothesis`
- `ExperimentDesign`
- `Protocol`
- `ExperimentRun`
- `Decision`

### 5.2 Biological domain

- `Producer`
- `Strain`
- `Product`
- `Gene`
- `Protein`
- `Pathway`
- `CellState`
- `Medium`

### 5.3 Bioprocess domain

- `Bioreactor`
- `BioreactorGeometry`
- `Sensor`
- `ProcessConfiguration`
- `SamplingPoint`
- `ProcessState`

### 5.4 Evidence domain

- `Observation`
- `Measurement`
- `Dataset`
- `Artifact`
- `Evidence`
- `Source`

### 5.5 Computational domain

- `ToolProvider`
- `ToolCapability`
- `ComputationRun`
- `ComputationalModel`
- `ModelRun`
- `Prediction`
- `CrossScaleLink`

### 5.6 Reasoning domain

- `ExpertRule`
- `ExpertInference`
- `AIInterpretation`
- `Critique`
- `Proposal`
- `ApprovalDecision`

### 5.7 Governance domain

- `AuditRecord`
- `VersionRecord`
- `ApprovalRecord`
- `DataProvenance`

## 6. Canonical data provenance model

Каждый научно значимый объект должен хранить происхождение и статус.

Минимальные поля:

```text
id
entity_type
created_at
created_by
source_type
source_reference
version
status
confidence
hash
supersedes
```

Для значимых научных утверждений используется классификация:

- `OBSERVED`
- `MANUAL`
- `IMPORTED`
- `CALCULATED`
- `MODEL_PREDICTED`
- `RULE_INFERRED`
- `AI_INFERRED`
- `EXPERT_APPROVED`
- `REJECTED`

AI-интерпретация не должна отображаться как измеренный факт.

## 7. Knowledge Base + Knowledge Graph

Knowledge Graph является связующим слоем платформы.

Примеры связей:

```text
Producer --PRODUCES--> Product
Gene --ENCODES--> Protein
Protein --CATALYZES--> Reaction
Reaction --PART_OF--> Pathway
ExperimentRun --TESTS--> Hypothesis
ExperimentRun --USES--> Producer
ExperimentRun --USES--> Bioreactor
Measurement --GENERATED_BY--> ExperimentRun
Evidence --SUPPORTS--> Hypothesis
Evidence --CONTRADICTS--> Hypothesis
Prediction --GENERATED_BY--> ModelRun
Proposal --BASED_ON--> Evidence
Decision --RESOLVES--> Proposal
```

Каждая edge/link должна иметь provenance, confidence и version.

Knowledge Graph используется для:

- поиска evidence по гипотезе;
- трассировки причинных цепочек между масштабами;
- сравнения конкурирующих гипотез;
- поиска противоречий;
- контекстного retrieval для AI.

## 8. Electronic Laboratory Notebook

ELN хранит человеческий контекст исследования:

- research notes;
- hypothesis rationale;
- experiment plans;
- protocol versions;
- observations;
- deviations;
- comments;
- attachments;
- decisions;
- approvals.

ELN, graph и experimental database не смешиваются логически:

- ELN = narrative/research history;
- graph = relations/semantics;
- data store = measurements/datasets.

## 9. Scientific Tool Gateway

### 9.1 Назначение

Scientific Tool Gateway — единый слой запуска внешних научных движков.

Платформа не должна содержать vendor-specific calls внутри бизнес-логики.

### 9.2 Standard ToolProvider contract

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

### 9.3 Типы подключаемых engines

Bioinformatics:
- Galaxy
- sequence analysis tools
- RNA-seq / omics workflows

Quantum / molecular chemistry:
- ORCA
- Psi4
- external QM/MD/docking engines

Cellular:
- COBRApy
- FBA / dFBA
- metabolic models

Multiphysics / reactor:
- COMSOL-like providers
- OpenFOAM-like providers
- external CFD / mass-transfer engines

CAD / geometry:
- FreeCAD-like providers
- external CAD APIs

Analytics:
- Python
- R
- statistics
- DoE
- optimization

## 10. Cross-scale contracts

Между уровнями запрещается неявная передача параметров.

Каждая связь оформляется как `CrossScaleLink`.

Пример:

```yaml
id: CSL-018
source:
  entity: CellularModel.OUR
  units: mmol/gDW/h
target:
  entity: ReactorModel.oxygen_consumption
  units: mol/m3/s
transformation:
  expression: "OUR * biomass / volume"
uncertainty:
  relative_percent: 12
validation_status: VALIDATED
evidence:
  - EXP-020
  - EXP-024
```

Cross-scale contracts должны быть versioned и audit-able.

## 11. AI architecture

AI является meta-layer над платформой, а не system of record.

Основные AI roles:

- `ContextAgent` — собирает релевантный scientific context;
- `HypothesisAgent` — формирует новые гипотезы;
- `ExperimentPlannerAgent` — предлагает дизайн эксперимента;
- `AnalysisAgent` — интерпретирует результаты вычислений;
- `CriticAgent` — ищет confounders и falsification criteria;
- `ExpertAgent` — сопоставляет факты с rule base;
- `ReportAgent` — формирует отчёты;
- `ComplianceAgent` — проверяет traceability и completeness.

AI не получает прямых write-операций в canonical domain.

## 12. Proposal Workspace

Все AI-изменения проходят через Proposal Workspace.

Пример:

```yaml
id: P-017
type: NEW_HYPOTHESIS
proposed_change:
  statement: "Oxygen transfer limitation may reduce collagenase secretion after biomass threshold X"
rationale: "Observed DO decline precedes productivity reduction"
evidence:
  supports:
    - EXP-021
    - EXP-024
  contradicts:
    - EXP-018
confidence: 0.64
suggested_next_experiment: DOE-008
status: PENDING_HUMAN_REVIEW
```

Допустимые состояния:

```text
DRAFT
PENDING_HUMAN_REVIEW
APPROVED
REJECTED
REVISION_REQUESTED
COMMITTED
```

Только переход `APPROVED -> COMMITTED` создаёт изменение canonical scientific state.

## 13. MCP facade

Codex и другие AI-агенты взаимодействуют с системой через MCP/API facade.

### 13.1 Read tools

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

### 13.2 Execution tools

```text
run_computation(tool, workflow, inputs)
run_statistics(dataset, method)
run_doe(objective, factors, constraints)
```

### 13.3 Proposal tools

```text
create_proposal(...)
propose_hypothesis(...)
propose_experiment(...)
propose_interpretation(...)
propose_model_change(...)
get_pending_proposals()
```

### 13.4 Explicitly forbidden direct tools

Не предоставлять AI прямые операции вида:

```text
update_hypothesis_directly()
overwrite_protocol()
change_experiment_result()
delete_evidence()
```

## 14. Connector Framework

Connector Framework реализуется как plugin system.

Базовые типы:

```text
REST
OpenAPI
MCP
Filesystem
CSV/XLSX
Database
Git
LIMS
ELN
ERP
Instrument
Scientific API
```

Предполагаемая структура:

```text
connectors/
  rest/
  filesystem/
  github/
  lims/
  eln/
  erp/
  instruments/
  scientific_tools/
```

Каждый connector обязан объявлять:

```text
capabilities
configuration schema
authentication requirements
read/write permissions
data mapping
health check
provenance behavior
```

Первый набор reference connectors:

- MCP
- REST/OpenAPI
- filesystem/CSV/XLSX
- Git
- one open-source LIMS adapter
- Galaxy

## 15. System of record

Рекомендуемая hybrid architecture:

- PostgreSQL — canonical relational entities;
- graph database or graph projection layer — knowledge relations;
- object/file storage — datasets/artifacts;
- Git — versioned AI-readable research workspace;
- MCP/API — единственный путь AI-доступа к production state.

AI-readable workspace:

```text
.ai/
  system-context.md
  project-state.yaml
  research-goals.yaml
  active-hypotheses.yaml
  experiment-plan.yaml
  pending-proposals.yaml
  capabilities.yaml
  mcp-tools.yaml
```

Этот слой является projection/cache, а не самостоятельным источником истины.

## 16. UI workspaces

Пользователь не должен видеть внутреннюю архитектурную сложность.

Основные разделы:

1. `Research`
2. `Experiments`
3. `ELN`
4. `Data`
5. `Knowledge`
6. `Models`
7. `AI`
8. `Integrations`
9. `Audit & Evidence`

Главный Research экран:

```text
Research Objective
        ↓
Active Hypotheses
        ↓
Current Experiments
        ↓
Incoming Evidence
        ↓
Model / Expert / AI Interpretations
        ↓
Pending Proposals
        ↓
Human Decisions
```

## 17. Первый reference use case

`Cultivation-collagenase` используется как первый vertical demonstration.

Минимальный сквозной сценарий:

1. зарегистрировать `Aspergillus sydowii` как Producer/Strain;
2. создать Research Objective;
3. зарегистрировать Hypothesis;
4. спроектировать Experiment;
5. сформировать electronic protocol;
6. внести/импортировать наблюдения и измерения;
7. запустить существующую process simulation или cellular engine;
8. сформировать expert inference;
9. AI интерпретирует результат;
10. CriticAgent формирует альтернативные объяснения;
11. AI создаёт Proposal следующего эксперимента;
12. человек Approve/Reject/Revise;
13. утверждённое решение попадает в canonical research state и audit trail.

## 18. MVP boundary

В MVP НЕ требуется:

- полноценная собственная QM реализация;
- собственный CFD solver;
- собственный CAD;
- собственная bioinformatics platform;
- автоматическое управление биореактором;
- автономное изменение AI научных данных;
- реализация всех LIMS/ERP connectors.

MVP должен доказать платформенный контракт и один полный research cycle.

## 19. Migration from current repository

Существующие элементы сохраняются и переиспользуются:

- `01_strain` → Producer/Strain knowledge;
- `02_media` → Medium domain;
- `03_cultivation_process` → Protocol/Experiment templates;
- `04_bioreactor` → Bioreactor domain;
- `05_analytics` → analytical methods;
- `06_experimental_data` → Dataset/Evidence layer;
- `07_models` → Computational Models;
- `08_expert_system` → Expert System;
- `09_reports_and_outputs` → Reports/Evidence outputs;
- `web_app` → transitional backend/UI implementation.

Добавляются новые logical domains:

```text
10_research_cycle/
11_knowledge_graph/
12_tool_gateway/
13_connectors/
14_ai_orchestration/
15_governance/
```

Физическая структура каталогов может быть изменена на этапе implementation plan после анализа текущего кода.

## 20. Non-functional principles

- human-in-the-loop by default;
- explicit provenance;
- immutable audit semantics for approved records;
- versioned hypotheses, protocols, rules and models;
- reproducible computation runs;
- tool/version/parameter capture;
- explicit units and transformations;
- uncertainty is first-class data;
- no silent AI writes;
- connector isolation;
- engine isolation;
- offline/on-prem deployment must remain possible;
- scientific claims must remain traceable to evidence.

## 21. Success criteria for v3 MVP

V3 MVP считается доказанным, если пользователь может пройти один полный workflow:

```text
Goal
→ Hypothesis
→ Experiment Design
→ Protocol
→ Experiment Run
→ Data/Evidence
→ Computation
→ Expert Interpretation
→ AI Interpretation
→ Critique
→ Proposal
→ Human Approval
→ Next Experiment
```

и при этом:

- все связи доступны через knowledge graph;
- computation run воспроизводим;
- provenance сохранён;
- Codex может получить контекст через MCP;
- Codex может создать Proposal;
- Codex не может напрямую изменить canonical scientific state;
- approved proposal приводит к versioned domain change;
- audit trail позволяет восстановить последовательность решений.

## 22. Deferred topics

Вынести за пределы первого implementation plan:

- полноценная GxP validation package;
- enterprise RBAC;
- electronic signatures;
- 21 CFR Part 11 qualification claims;
- production LIMS marketplace;
- automatic instrument control;
- autonomous closed-loop experimentation;
- multi-tenant SaaS;
- licensing/monetization implementation.

Эти темы должны проектироваться после доказательства core research workflow.