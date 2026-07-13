# BioCult-KB: Collagenase Cultivation Knowledge Base

[Русская версия](README.md)

BioCult-KB is a scientific knowledge repository and web prototype for modelling the cultivation of *Aspergillus sydowii* as a producer of collagenolytic activity. The project connects biological knowledge, process engineering, experimental data, simulation, and software into one structured system.

## Why this project exists

Bioprocess development usually distributes critical knowledge across protocols, spreadsheets, literature notes, analytical methods, model files, and operator experience. BioCult-KB explores a more traceable approach in which strain data, cultivation conditions, process models, analytics, and recommendations are represented in a single navigable environment.

## Core capabilities

- Structured knowledge base for the strain, media, cultivation process, bioreactor, analytics, and experiments.
- FastAPI web application with monitoring, calculation, recommendation, and data-management endpoints.
- GEM-lite COBRA/SBML model for exploratory biomass, metabolism, and production estimates.
- Batch, fed-batch, and continuous-process simulation.
- OMICS-oriented pipeline for organising genomic, transcriptomic, and analytical resources.
- Automated tests for process calculations and biological plausibility checks.
- Operational documentation and traceable project structure.

## Repository structure

- `00_project_passport/` — goals, scope, terminology, assumptions, and known limitations.
- `01_strain/` — strain passport, genomic context, and safety-related information.
- `02_media/` — media recipes and component dictionaries.
- `03_cultivation_process/` — cultivation protocols and sampling plans.
- `04_bioreactor/` — bioreactor specifications, sensors, and 3D assets.
- `05_analytics/` — analytical methods and calculation formulas.
- `06_experimental_data/` — experimental datasets and source materials.
- `07_models/` — growth, oxygen-transfer, consumption, and production models.
- `08_expert_system/` — rules, ontology elements, and recommendations.
- `09_reports_and_outputs/` — reports, operating documents, and generated outputs.
- `web_app/` — FastAPI backend, ORM, API, ETL utilities, and web prototype.
- `frontend/` — Vite/React interface and visual assets.

## Quick start

```powershell
cd "BioCult-KB_Aspergillus_sydowii"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r web_app\requirements.txt
$env:PYTHONPATH = (Resolve-Path .).Path
python -m uvicorn web_app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` in a browser.

Run the test suite:

```powershell
cd "BioCult-KB_Aspergillus_sydowii"
$env:PYTHONPATH = (Resolve-Path .).Path
python -m pytest tests -q
```

## Scientific status and limitations

BioCult-KB is a research and knowledge-engineering prototype. Models, rules, and recommendations require validation against controlled experimental data before they can support process-development decisions. The repository intentionally excludes large raw NCBI datasets, complete OMICS packages, and temporary local files.

## Project leadership and authorship

BioCult-KB is designed and directed by **Vlad Myahlov**, Scientific Systems Engineer. The domain structure, modelling objectives, requirements, knowledge architecture, process logic, acceptance criteria, and validation approach are human-defined. Software implementation is developed through an AI-assisted engineering workflow and reviewed for scientific and architectural consistency.

## Intended portfolio value

This project demonstrates the ability to convert a multidisciplinary biotechnology problem into a structured knowledge system that combines domain documentation, process modelling, laboratory analytics, software architecture, and validation-oriented reasoning.
