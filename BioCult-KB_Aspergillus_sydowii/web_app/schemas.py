from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrainBase(BaseModel):
    species: str
    collection_number: Optional[str] = None
    origin: Optional[str] = None
    biosafety_level: Optional[str] = None
    reactivation_rule: Optional[str] = None


class StrainCreate(StrainBase):
    pass


class MediumBase(BaseModel):
    name: str
    purpose: Optional[str] = None
    pH: Optional[float] = None
    state: Optional[str] = None
    status: Optional[str] = None


class MediumCreate(MediumBase):
    pass


class MediumComponentBase(BaseModel):
    medium_id: int
    component: str
    concentration_g_l: Optional[float] = None
    hydrate_form: Optional[str] = None
    role: Optional[str] = None


class MediumComponentCreate(MediumComponentBase):
    pass


class BioreactorBase(BaseModel):
    name: str
    working_volume_l: Optional[float] = None
    model: Optional[str] = None
    description: Optional[str] = None


class BioreactorCreate(BioreactorBase):
    pass


class CultivationSetpoints(BaseModel):
    temperature_C: float
    pH_min: float
    pH_max: float
    rpm: float
    medium_code: str
    strain: str


class CultivationProfilePoint(BaseModel):
    time_h: float
    biomass_g_l: float
    rpm: float
    pH: float
    pO2_percent: float
    pCO2_percent: float
    kla_h: float
    sugars_g_l: float
    level_percent: float
    density_g_ml: float
    viscosity_mpa_s: float
    temperature_C: float
    pressure_bar: float
    humidity_percent: float
    conductivity_ms_cm: float


class BioreactorScene(BaseModel):
    vessel_internal_diameter_mm: float
    vessel_internal_height_mm: float
    glass_thickness_mm: float
    full_volume_l: float
    working_volume_l: float
    medium_before_inoculation_l: float
    inoculum_volume_ml: float
    impeller_diameter_mm: float
    impeller_blade_height_mm: float
    baffle_count: int
    baffle_height_mm: float
    sparger_height_mm: float
    service_tube_count: int
    process_duration_h: float
    setpoints: CultivationSetpoints
    profile: List[CultivationProfilePoint]


class MediaOptimizationInput(BaseModel):
    molasses_g_l: float = Field(default=20.0, ge=0, le=60)
    peptone_g_l: float = Field(default=85.0, ge=0, le=140)
    collagen_g_l: float = Field(default=5.0, ge=0, le=20)
    mineral_factor: float = Field(default=1.0, ge=0, le=1.5)
    pH: float = Field(default=7.2, ge=4.5, le=9)
    aeration_vvm: float = Field(default=0.8, ge=0, le=2)
    rpm: float = Field(default=220.0, ge=0, le=600)
    cultivation_time_h: float = Field(default=144.0, ge=24, le=240)
    temperature_C: float = Field(default=25.0, ge=15, le=35)
    working_volume_l: float = Field(default=1.7, ge=0.05, le=3000)


class CellProgramScore(BaseModel):
    name: str
    score: int
    status: str
    rationale: str


class ProcessProjection(BaseModel):
    biomass_index: int
    collagenase_activity_index: int
    oxygen_demand_index: int
    viscosity_risk_index: int
    predicted_biomass_g_l: float
    predicted_collagenase_u_ml: float
    predicted_pO2_percent: float
    predicted_pCO2_percent: float
    predicted_viscosity_mpa_s: float
    recommended_harvest_time_h: float
    predicted_yield_score: Optional[float] = None


class MediaOptimizationResult(BaseModel):
    cell_programs: List[CellProgramScore]
    projection: ProcessProjection
    recommendations: List[str]
    genome_process_links: Dict[str, str]


class OptimizationScenario(BaseModel):
    rank: int
    objective_score: float
    input: MediaOptimizationInput
    projection: ProcessProjection
    rationale: List[str]


class CultivationOptimizationResult(BaseModel):
    best: OptimizationScenario
    scenarios: List[OptimizationScenario]
    search_space: Dict[str, List[float]]
    constraints: Dict[str, float]


class BiosynthesisPotentialPoint(BaseModel):
    name: str
    potential_score: int
    evidence_level: str
    process_levers: List[str]
    risks: List[str]


class SystemBiologyModelResult(BaseModel):
    model_version: str
    primary_accession: str
    genome_report: Dict[str, Any]
    condition_evaluation: Dict[str, Any]


class SystemBiologyConditionResult(BaseModel):
    input: Dict[str, Any]
    programs: List[Dict[str, Any]]
    projection: Dict[str, Any]
    interpretation: List[str]


class GemFbaInput(BaseModel):
    medium: MediaOptimizationInput = Field(default_factory=MediaOptimizationInput)
    objective: str = Field(default="biomass", pattern=r"^(biomass|collagenolytic_product|balanced)$")
    growth_floor: float = Field(default=0.05, ge=0, le=10)


class GemFbaResult(BaseModel):
    available: bool
    status: str
    objective: str
    objective_value: Optional[float] = None
    sbml_path: Optional[str] = None
    exchange_bounds: Optional[Dict[str, float]] = None
    limiting_exchange_reactions: Optional[List[str]] = None
    fluxes: Optional[Dict[str, float]] = None
    warnings: Optional[List[str]] = None
    error: Optional[str] = None


class ProcessSimulationInput(BaseModel):
    process_mode: str = Field(default="batch", pattern=r"^(batch|fed_batch|continuous)$")
    medium: MediaOptimizationInput = Field(default_factory=MediaOptimizationInput)
    duration_h: float = Field(default=144.0, ge=24, le=240)
    step_h: float = Field(default=12.0, ge=1, le=24)
    initial_biomass_g_l: float = Field(default=0.12, ge=0.001, le=20)
    initial_volume_l: float = Field(default=1.7, ge=0.05, le=3000)
    feed_rate_l_h: float = Field(default=0.005, ge=0, le=10)
    bleed_rate_l_h: float = Field(default=0.005, ge=0, le=10)


class ProcessSimulationPoint(BaseModel):
    time_h: float
    volume_l: float
    biomass_g_l: float
    molasses_g_l: float
    peptone_n_g_l: float
    collagen_g_l: float
    amino_nitrogen_mg_percent: float
    protein_mg_ml: float
    product_u_ml: float
    pO2_percent: float
    density_g_ml: float
    viscosity_mpa_s: float
    conductivity_ms_cm: float
    fba_mu_capacity_h: float
    fba_product_capacity: float
    dfba_mu_h: Optional[float] = None
    kLa_h: Optional[float] = None
    OTR_mmol_l_h: Optional[float] = None


class ProcessSimulationResult(BaseModel):
    process_mode: str
    degraded_mode: bool
    fba_status: str
    profile: List[ProcessSimulationPoint]
    mass_balance_equations: List[str]
    notes: List[str]


def default_media_optimization_input() -> MediaOptimizationInput:
    return MediaOptimizationInput(
        molasses_g_l=20.0,
        peptone_g_l=85.0,
        collagen_g_l=5.0,
        mineral_factor=1.0,
        pH=7.2,
        aeration_vvm=0.8,
        rpm=220.0,
        cultivation_time_h=144.0,
        temperature_C=25.0,
        working_volume_l=1.7,
    )


class OmicsProjectRequest(BaseModel):
    genome_accession: str = Field(default="GCA_001890705.1", pattern=r"^GC[AF]_\d{9}\.\d+$")
    transcriptome_bioproject: str = Field(default="PRJNA542911", pattern=r"^PRJNA\d+$")
    metabolome_label: Optional[str] = "A. sydowii co-culture metabolomics paper"


class OmicsRegistryResult(BaseModel):
    registry: Dict
    tool_status: Dict[str, bool]


class OmicsScaffoldResult(BaseModel):
    project_dir: str
    artifacts: Dict[str, str]
    commands: Dict[str, str]
    tool_status: Dict[str, bool]
    validation: Dict
    manifest: Dict


class ObservationBase(BaseModel):
    batch_id: Optional[int] = None
    time_h: float
    pH: Optional[float] = None
    pO2_percent: Optional[float] = None
    temperature_C: Optional[float] = None
    rpm: Optional[float] = None
    biomass: Optional[float] = None
    kla: Optional[float] = None
    protein: Optional[float] = None
    sugars: Optional[float] = None
    amino_nitrogen: Optional[float] = None


class ObservationCreate(ObservationBase):
    pass


class BatchRunBase(BaseModel):
    strain_id: int
    medium_id: int
    bioreactor_id: Optional[int] = None
    working_volume_l: Optional[float] = None
    inoculum_volume_ml: Optional[float] = None
    start_datetime: Optional[datetime] = None


class BatchRunCreate(BatchRunBase):
    pass


class CalculationInput(BaseModel):
    observations: List[ObservationBase]


class RecommendationInput(BaseModel):
    medium_id: Optional[int] = None
    controls_present: Optional[bool] = True
    collection_time_h: Optional[float] = None
    last_pO2_percent: Optional[float] = None
    observations: Optional[List[ObservationBase]] = None


class CalculationResult(BaseModel):
    max_kla: Optional[float] = None
    max_biomass: Optional[float] = None
    specific_growth_rate_h: Optional[float] = None
    uca_estimate: Optional[float] = None
    average_pH: Optional[float] = None
    average_pO2: Optional[float] = None
    note: Optional[str] = None


class RecommendationResult(BaseModel):
    recommendations: List[str]


class ImportResult(BaseModel):
    imported: dict
    warnings: Optional[List[str]] = None


class AuditLogInput(BaseModel):
    user: str = "system"
    session_id: str = "default"
    batch_id: Optional[int] = None
    action_type: str
    module: str = "unknown"
    recommendation: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    outcome: Optional[Dict[str, Any]] = None


class AuditRecordSchema(BaseModel):
    id: int
    timestamp: datetime
    user: str
    session_id: str
    batch_id: Optional[int] = None
    action_type: str
    module: str
    recommendation: str
    evidence_json: str
    confidence: Optional[float] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    outcome_json: Optional[str] = None
    record_hash: str

    class Config:
        from_attributes = True


class AuditVerifyResult(BaseModel):
    record_id: int
    valid: bool
    expected_hash: str
    record_hash: str


class DfbaStepInput(BaseModel):
    time_h: float = 0.0
    dt_h: float = Field(default=12.0, gt=0, le=24)
    medium: MediaOptimizationInput = Field(default_factory=MediaOptimizationInput)
    biomass_g_l: float = Field(default=0.12, ge=0)
    molasses_g_l: float = Field(default=20.0, ge=0)
    peptone_n_g_l: Optional[float] = Field(default=None, ge=0)
    collagen_g_l: Optional[float] = Field(default=None, ge=0)
    product_u_ml: float = Field(default=0.0, ge=0)
    do_percent: float = Field(default=92.0, ge=0, le=100)
    volume_l: float = Field(default=1.7, gt=0)


class DfbaStepResult(BaseModel):
    status: str
    degraded_mode: bool
    time_h: float
    volume_l: float
    biomass_g_l: float
    molasses_g_l: float
    peptone_n_g_l: float
    collagen_g_l: float
    product_u_ml: float
    pO2_percent: float
    dfba_mu_h: float
    qP_u_g_h: float
    qS_g_g_h: float
    OUR_mmol_l_h: float
    kLa_h: float
    OTR_mmol_l_h: float
    fluxes: Dict[str, float]
    warnings: List[str] = Field(default_factory=list)


class TranscriptomeUploadInput(BaseModel):
    dataset_id: str = Field(default="PRJNA542911_tpm", pattern=r"^[A-Za-z0-9_.-]+$")
    csv_text: str
    source_label: Optional[str] = "uploaded_tpm"


class TranscriptomeFbaInput(BaseModel):
    dataset_id: str = "PRJNA542911_tpm"
    medium: MediaOptimizationInput = Field(default_factory=MediaOptimizationInput)
    objective: str = Field(default="balanced", pattern=r"^(biomass|collagenolytic_product|balanced)$")
    growth_floor: float = Field(default=0.05, ge=0, le=10)
    threshold: float = Field(default=0.05, ge=0, le=1)
    tpm: Optional[Dict[str, float]] = None


class ScalingInput(BaseModel):
    source_volume_l: float = Field(default=1.7, gt=0)
    target_volume_l: float = Field(default=30.0, gt=0)
    source_rpm: float = Field(default=220.0, ge=0)
    source_vvm: float = Field(default=0.8, ge=0)
    target_vvm: Optional[float] = Field(default=None, ge=0)
    viscosity_mpa_s: float = Field(default=1.8, gt=0)


class DoeInput(BaseModel):
    n_runs: int = Field(default=12, ge=4, le=96)
    factors: Optional[Dict[str, List[float]]] = None
    seed: int = 42


class ProcessEventInput(BaseModel):
    event_type: str
    module: str = "process"
    user: str = "system"
    session_id: str = "default"
    batch_id: Optional[int] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
