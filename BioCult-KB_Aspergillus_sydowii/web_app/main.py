from pathlib import Path
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import (
    calculations,
    cell_process,
    data_import,
    gem_cobra,
    models,
    omics_pipeline,
    omics_registry,
    omics_validation,
    process_simulation,
    recommendations,
    schemas,
    system_biology,
)
from .db import SessionLocal, init_db

app = FastAPI(
    title="BioCult-KB: база знаний культивирования",
    description="Прототип веб-приложения для работы с базой знаний по культивированию Aspergillus sydowii.",
    version="0.1",
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _as_str(value: Any) -> str:
    return "" if value is None else str(value)


def _as_optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _as_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@app.on_event("startup")
def startup_event():
    init_db()
    with SessionLocal() as session:
        if session.query(models.Strain).count() == 0:
            sample_strain = models.Strain(
                species="Aspergillus sydowii",
                collection_number="ВКПМ F-347",
                origin="Lab register",
                biosafety_level="2",
                reactivation_rule="Стандартный протокол реактивации на среде с глюкозой и пептоном.",
            )
            session.add(sample_strain)
            sample_medium = models.Medium(
                name="Оптимизированная меласса-пептон",
                purpose="культивирование",
                pH=6.0,
                state="liquid",
                status="reference",
            )
            session.add(sample_medium)
            session.commit()


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/api/strains", response_model=List[schemas.StrainBase])
def read_strains(db: Session = Depends(get_db)):
    strains = db.query(models.Strain).all()
    return [
        schemas.StrainBase(
            species=_as_str(getattr(strain, "species", "")),
            collection_number=_as_optional_str(getattr(strain, "collection_number", None)),
            origin=_as_optional_str(getattr(strain, "origin", None)),
            biosafety_level=_as_optional_str(getattr(strain, "biosafety_level", None)),
            reactivation_rule=_as_optional_str(getattr(strain, "reactivation_rule", None)),
        )
        for strain in strains
    ]


@app.get("/api/media", response_model=List[schemas.MediumBase])
def read_media(db: Session = Depends(get_db)):
    media = db.query(models.Medium).all()
    return [
        schemas.MediumBase(
            name=_as_str(getattr(medium, "name", "")),
            purpose=_as_optional_str(getattr(medium, "purpose", None)),
            pH=_as_optional_float(getattr(medium, "pH", None)),
            state=_as_optional_str(getattr(medium, "state", None)),
            status=_as_optional_str(getattr(medium, "status", None)),
        )
        for medium in media
    ]


@app.get("/api/bioreactor-scene", response_model=schemas.BioreactorScene)
def read_bioreactor_scene():
    return schemas.BioreactorScene(
        vessel_internal_diameter_mm=130,
        vessel_internal_height_mm=180,
        glass_thickness_mm=5,
        full_volume_l=2.39,
        working_volume_l=1.7,
        medium_before_inoculation_l=1.6,
        inoculum_volume_ml=100,
        impeller_diameter_mm=40,
        impeller_blade_height_mm=10,
        baffle_count=3,
        baffle_height_mm=230,
        sparger_height_mm=230,
        service_tube_count=6,
        process_duration_h=144,
        setpoints=schemas.CultivationSetpoints(
            temperature_C=25,
            pH_min=7.1,
            pH_max=7.5,
            rpm=220,
            medium_code="MOLASSES20_PEPTONE85_V1",
            strain="Aspergillus sydowii",
        ),
        profile=[
            schemas.CultivationProfilePoint(
                time_h=0,
                biomass_g_l=0.12,
                rpm=180,
                pH=7.35,
                pO2_percent=92,
                pCO2_percent=0.3,
                kla_h=28,
                sugars_g_l=20,
                level_percent=71.1,
                density_g_ml=1.018,
                viscosity_mpa_s=1.18,
                temperature_C=24.8,
                pressure_bar=1.02,
                humidity_percent=58,
                conductivity_ms_cm=8.4,
            ),
            schemas.CultivationProfilePoint(
                time_h=24,
                biomass_g_l=0.8,
                rpm=220,
                pH=7.28,
                pO2_percent=64,
                pCO2_percent=1.2,
                kla_h=42,
                sugars_g_l=16,
                level_percent=71.0,
                density_g_ml=1.019,
                viscosity_mpa_s=1.32,
                temperature_C=25.0,
                pressure_bar=1.04,
                humidity_percent=60,
                conductivity_ms_cm=8.8,
            ),
            schemas.CultivationProfilePoint(
                time_h=48,
                biomass_g_l=1.9,
                rpm=240,
                pH=7.15,
                pO2_percent=38,
                pCO2_percent=2.8,
                kla_h=65,
                sugars_g_l=11,
                level_percent=70.8,
                density_g_ml=1.021,
                viscosity_mpa_s=1.72,
                temperature_C=25.2,
                pressure_bar=1.06,
                humidity_percent=62,
                conductivity_ms_cm=9.4,
            ),
            schemas.CultivationProfilePoint(
                time_h=72,
                biomass_g_l=3.1,
                rpm=260,
                pH=7.08,
                pO2_percent=30,
                pCO2_percent=4.1,
                kla_h=78,
                sugars_g_l=7,
                level_percent=70.6,
                density_g_ml=1.024,
                viscosity_mpa_s=2.35,
                temperature_C=25.1,
                pressure_bar=1.08,
                humidity_percent=64,
                conductivity_ms_cm=10.1,
            ),
            schemas.CultivationProfilePoint(
                time_h=96,
                biomass_g_l=3.6,
                rpm=260,
                pH=7.03,
                pO2_percent=34,
                pCO2_percent=4.8,
                kla_h=82,
                sugars_g_l=5,
                level_percent=70.3,
                density_g_ml=1.026,
                viscosity_mpa_s=2.72,
                temperature_C=25.0,
                pressure_bar=1.07,
                humidity_percent=65,
                conductivity_ms_cm=10.6,
            ),
            schemas.CultivationProfilePoint(
                time_h=120,
                biomass_g_l=3.8,
                rpm=250,
                pH=7.12,
                pO2_percent=41,
                pCO2_percent=4.4,
                kla_h=80,
                sugars_g_l=3.8,
                level_percent=70.1,
                density_g_ml=1.027,
                viscosity_mpa_s=2.68,
                temperature_C=24.9,
                pressure_bar=1.05,
                humidity_percent=64,
                conductivity_ms_cm=10.7,
            ),
            schemas.CultivationProfilePoint(
                time_h=144,
                biomass_g_l=3.7,
                rpm=240,
                pH=7.22,
                pO2_percent=48,
                pCO2_percent=3.7,
                kla_h=76,
                sugars_g_l=3.2,
                level_percent=69.8,
                density_g_ml=1.027,
                viscosity_mpa_s=2.55,
                temperature_C=24.8,
                pressure_bar=1.04,
                humidity_percent=63,
                conductivity_ms_cm=10.5,
            ),
        ],
    )


@app.get("/api/cell-process-model", response_model=schemas.MediaOptimizationResult)
def read_cell_process_model():
    return cell_process.evaluate_media_strategy(schemas.default_media_optimization_input())


@app.post("/api/media-optimization", response_model=schemas.MediaOptimizationResult)
def optimize_media_strategy(input_data: schemas.MediaOptimizationInput):
    return cell_process.evaluate_media_strategy(input_data)


@app.get("/api/system-biology-model", response_model=schemas.SystemBiologyModelResult)
def read_system_biology_model():
    return system_biology.build_system_biology_model()


@app.post("/api/system-biology-model/evaluate", response_model=schemas.SystemBiologyConditionResult)
def evaluate_system_biology_model(input_data: schemas.MediaOptimizationInput):
    return system_biology.evaluate_conditions(input_data)


@app.get("/api/gem/summary")
def read_gem_summary():
    return gem_cobra.gem_summary()


@app.post("/api/gem/fba", response_model=schemas.GemFbaResult)
def run_gem_fba(input_data: schemas.GemFbaInput):
    return gem_cobra.run_fba(input_data)


@app.get("/api/gem/sbml", include_in_schema=False)
def download_gem_sbml():
    path = gem_cobra.export_sbml_model()
    if not path.exists():
        raise HTTPException(status_code=404, detail="SBML model file was not generated")
    return FileResponse(path, media_type="application/xml", filename=path.name)


@app.get("/api/process-modes")
def read_process_modes():
    return {
        "modes": [
            {"id": "batch", "label": "Batch", "description": "Closed batch with fixed working volume."},
            {"id": "fed_batch", "label": "Fed-batch", "description": "Feed increases volume and refreshes substrates."},
            {"id": "continuous", "label": "Continuous", "description": "Feed and bleed maintain a continuous process."},
        ]
    }


@app.post("/api/process-simulation", response_model=schemas.ProcessSimulationResult)
def simulate_process(input_data: schemas.ProcessSimulationInput):
    return process_simulation.simulate_process(input_data)


@app.get("/api/cultivation-optimizer", response_model=schemas.CultivationOptimizationResult)
def read_cultivation_optimizer():
    return cell_process.optimize_cultivation_strategy()


@app.get("/api/omics/registry", response_model=schemas.OmicsRegistryResult)
def read_omics_registry():
    return schemas.OmicsRegistryResult(
        registry=omics_registry.serialize_registry(),
        tool_status=omics_validation.check_tool_availability(),
    )


@app.post("/api/omics/manifest")
def preview_omics_manifest(input_data: schemas.OmicsProjectRequest):
    manifest = omics_pipeline.build_manifest(input_data)
    return {
        "manifest": manifest,
        "validation": {
            "manifest_valid": not omics_validation.validate_manifest_structure(manifest),
            "manifest_errors": omics_validation.validate_manifest_structure(manifest),
            "genome_accession_valid": omics_validation.validate_genome_accession(input_data.genome_accession),
            "transcriptome_bioproject_valid": omics_validation.validate_bioproject_accession(
                input_data.transcriptome_bioproject
            ),
        },
        "commands": omics_pipeline.build_commands(input_data),
    }


@app.post("/api/omics/scaffold", response_model=schemas.OmicsScaffoldResult)
def scaffold_omics_project(input_data: schemas.OmicsProjectRequest):
    return schemas.OmicsScaffoldResult(**omics_pipeline.scaffold_project(input_data))


@app.post("/api/omics/download-genomes")
def download_verified_genome_packages():
    return omics_pipeline.download_all_verified_genome_packages()


@app.post("/api/omics/discover-transcriptome")
def discover_omics_transcriptome(input_data: schemas.OmicsProjectRequest):
    return omics_pipeline.discover_transcriptome_runinfo_http(input_data.transcriptome_bioproject)


@app.post("/api/omics/biosynthesis-report")
def build_omics_biosynthesis_report():
    return omics_pipeline.build_biosynthesis_asset_report()


@app.post("/api/calculate", response_model=schemas.CalculationResult)
def calculate_metrics(input_data: schemas.CalculationInput):
    observations = [schemas.ObservationBase(**obs.dict()) for obs in input_data.observations]
    return calculations.calculate_metrics(observations)


@app.post("/api/recommend", response_model=schemas.RecommendationResult)
def get_recommendations(input_data: schemas.RecommendationInput, db: Session = Depends(get_db)):
    medium = None
    if input_data.medium_id is not None:
        medium = db.query(models.Medium).filter(models.Medium.id == input_data.medium_id).first()
        if medium is None:
            raise HTTPException(status_code=404, detail="Среда не найдена")

    return schemas.RecommendationResult(
        recommendations=recommendations.recommend(
            input_data.dict(),
            medium=medium,
        )
    )


@app.post("/api/import-excel", response_model=schemas.ImportResult)
def import_excel_data(db: Session = Depends(get_db)):
    project_root = Path(__file__).resolve().parents[1]
    result = data_import.import_all_known_sources(db, project_root)
    return schemas.ImportResult(imported=result)


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "database": str(Path(__file__).resolve().parents[1] / "data" / "app.db")}
