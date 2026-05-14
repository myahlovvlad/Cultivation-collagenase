# Cultivation-collagenase

BioCult-KB is a knowledge-base and web prototype for modeling cultivation of *Aspergillus sydowii* as a producer of extracellular collagenolytic enzyme activity.

The project combines cultivation documentation, strain/media knowledge, analytical methods, expert rules, a FastAPI web dashboard, and a practical GEM-lite COBRA/SBML layer for process decision support.

## What Is Included

- Structured project knowledge base for strain, media, bioreactor, analytics, experimental data, models, and expert rules.
- FastAPI web application with a Russian dashboard for cultivation monitoring and decision support.
- Interactive 3D bioreactor scene, sensor stand, time-series visualization, and expert-system recommendations.
- Medium optimization sliders connected to process forecasts and system-biology interpretation.
- GEM-lite COBRApy/SBML model for *A. sydowii* with FBA endpoints.
- Process simulation core for batch, fed-batch, and continuous cultivation modes.
- OMICS pipeline scaffolding for genome, transcriptome, and metabolome source tracking.
- Unit tests for system-biology evidence parsing and GEM/process simulation.

## Repository Layout

```text
BioCult-KB_Aspergillus_sydowii/
  00_project_passport/        Project scope, terminology, unresolved issues
  01_strain/                  Strain passport, genome references, biosafety
  02_media/                   Medium recipes and component dictionaries
  03_cultivation_process/     Cultivation protocols and sampling plans
  04_bioreactor/              Bioreactor geometry, sensors, calibration
  05_analytics/               Analytical methods and calculation formulas
  06_experimental_data/       Small curated data tables and templates
  07_models/                  Growth, oxygen transfer, substrate and product models
  08_expert_system/           Rules, ontology, recommendation templates
  09_reports_and_outputs/     Reports and generated operating documents
  tests/                      Pytest tests
  web_app/                    FastAPI application and static dashboard
```

Large NCBI datasets, raw OMICS downloads, local SQLite databases, and cache folders are intentionally excluded from git. Recreate or unpack those files locally when needed.

## Quick Start

From the repository root:

```powershell
cd BioCult-KB_Aspergillus_sydowii
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r web_app\requirements.txt
$env:PYTHONPATH = (Resolve-Path .).Path
python -m uvicorn web_app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

## Key API Endpoints

- `GET /api/gem/summary` - GEM-lite/SBML status.
- `POST /api/gem/fba` - FBA calculation for selected medium constraints.
- `GET /api/gem/sbml` - SBML model download.
- `POST /api/process-simulation` - process simulation for batch, fed-batch, or continuous mode.
- `GET /api/system-biology-model` - genome evidence and process-potential report.
- `POST /api/system-biology-model/evaluate` - condition-specific system-biology interpretation.

## Validation

Run tests from `BioCult-KB_Aspergillus_sydowii`:

```powershell
$env:PYTHONPATH = (Resolve-Path .).Path
python -m pytest tests -q
```

Current expected result: all tests pass.

## Current Model Boundary

The v1 model is a practical engineering prototype. It is not a publication-grade curated genome-scale metabolic model.

- GEM-lite uses proxy metabolites and proxy stoichiometry.
- Collagenolytic activity is inferred from protease/peptidase and secretion evidence unless direct annotation is present.
- Cell-cycle evidence is represented as an annotation layer, not as a full ODE/event simulation.
- Process dynamics combine FBA capacity estimates with empirical kinetic assumptions.

## Operating Manual

The operating manual is available at:

```text
BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/operation_manual.pdf
```

